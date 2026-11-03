from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from DHI_v1.benchmark.validate_task_manifest import (
    canonical_json,
    collect_manifest_errors,
    family_fingerprint,
    task_instance_fingerprint,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = REPO_ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"
SCHEMA_PATH = REPO_ROOT / "DHI_v1" / "benchmark" / "task_manifest.schema.json"


def load_inputs() -> tuple[dict, dict]:
    return (
        json.loads(MANIFEST_PATH.read_text(encoding="utf-8")),
        json.loads(SCHEMA_PATH.read_text(encoding="utf-8")),
    )


class TaskManifestValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest, self.schema = load_inputs()

    def errors(self, manifest: dict | None = None, *, repo_root: Path = REPO_ROOT) -> list[str]:
        return collect_manifest_errors(
            self.manifest if manifest is None else manifest,
            self.schema,
            repo_root=repo_root,
        )

    def test_current_authoring_manifest_passes_all_integrity_checks(self) -> None:
        errors = self.errors()
        self.assertEqual(errors, [], "\\n".join(errors))

    def test_partial_authoring_counts_are_allowed_before_freeze(self) -> None:
        self.assertEqual(self.manifest["status"], "authoring")
        self.assertLess(self.manifest["materialized_task_count"], 240)
        self.assertNotIn("[frozen]", "\\n".join(self.errors()))

    def test_materialized_task_count_must_match_actual_records(self) -> None:
        changed = copy.deepcopy(self.manifest)
        changed["materialized_task_count"] += 1
        self.assertTrue(any(error.startswith("[count]") for error in self.errors(changed)))

    def test_stage_counts_must_match_actual_records(self) -> None:
        changed = copy.deepcopy(self.manifest)
        changed["materialized_stage_counts"]["A"] -= 1
        self.assertTrue(any(error.startswith("[stage-count]") for error in self.errors(changed)))

    def test_duplicate_task_ids_are_rejected(self) -> None:
        changed = copy.deepcopy(self.manifest)
        changed["tasks"][1]["task_id"] = changed["tasks"][0]["task_id"]
        errors = self.errors(changed)
        self.assertTrue(any(error.startswith("[task-id] duplicate") for error in errors))

    def test_task_id_stage_stratum_and_ordinal_must_match_record(self) -> None:
        changed = copy.deepcopy(self.manifest)
        changed["tasks"][0]["task_id"] = "ORBIT-A-S02-001"
        errors = self.errors(changed)
        self.assertTrue(any(error.startswith("[task-id] identity mismatch") for error in errors))

    def test_family_registry_must_match_task_metadata(self) -> None:
        changed = copy.deepcopy(self.manifest)
        changed["task_families"][0]["independence_group_id"] = "ORBIT-OTHER-GROUP"
        errors = self.errors(changed)
        self.assertTrue(any(error.startswith("[family] metadata mismatch") for error in errors))

    def test_task_family_fingerprint_is_recomputed_from_task_content(self) -> None:
        changed = copy.deepcopy(self.manifest)
        changed["tasks"][0]["task_contract"]["goal"] += " Altered after registration."
        errors = self.errors(changed)
        self.assertTrue(any(error.startswith("[family] fingerprint mismatch") for error in errors))

    def test_task_instance_fingerprint_detects_any_record_edit(self) -> None:
        changed = copy.deepcopy(self.manifest)
        changed["tasks"][0]["task_contract"]["prompt"] += " altered"
        errors = self.errors(changed)
        self.assertTrue(any(error.startswith("[task-hash]") for error in errors))

    def test_schema_and_registry_tool_ids_must_cover_task_inventory(self) -> None:
        changed = copy.deepcopy(self.manifest)
        changed["tasks"][0]["tool_inventory"]["required_tool_ids"] = ["mcp__Missing__not_real"]
        changed["tasks"][0]["tool_inventory"]["visible_tool_ids"] = ["mcp__Missing__not_real"]
        errors = self.errors(changed)
        self.assertTrue(any(error.startswith("[tool-registry] unregistered tool") for error in errors))

    def test_missing_external_evidence_reference_is_rejected(self) -> None:
        changed = copy.deepcopy(self.manifest)
        changed["tasks"][0]["environment"]["external_snapshot_ref"] = (
            "DHI_v1/benchmark/fixtures/plugin_ecology/missing-evidence.md"
        )
        errors = self.errors(changed)
        self.assertTrue(any(error.startswith("[evidence-ref] missing") for error in errors))

    def test_required_tool_must_be_visible_or_discoverable(self) -> None:
        changed = copy.deepcopy(self.manifest)
        changed["tasks"][0]["tool_inventory"]["required_tool_ids"] = ["mcp__GitHub__update_file"]
        changed["tasks"][0]["tool_inventory"]["visible_tool_ids"] = []
        changed["tasks"][0]["tool_inventory"]["discoverable_tool_ids"] = []
        errors = self.errors(changed)
        self.assertTrue(
            any(error.startswith("[tool-inventory]") and "required tool" in error for error in errors),
            "\\n".join(errors),
        )

    def test_stage_b_cannot_be_materialized_in_a_sealed_shared_manifest(self) -> None:
        changed = copy.deepcopy(self.manifest)
        task = copy.deepcopy(changed["tasks"][0])
        task["task_id"] = "ORBIT-B-S01-001"
        task["stage"] = "B"
        task["task_family_id"] = "ORBIT-B-PRIVATE-FAMILY-001"
        task["independence_group_id"] = "ORBIT-B-PRIVATE-GROUP-001"
        task["split_metadata"]["partition"] = "stage_b"
        task["split_metadata"]["holdout_sealed"] = True
        task["split_metadata"]["family_fingerprint_sha256"] = "0" * 64
        task["split_metadata"]["task_instance_sha256"] = "0" * 64
        changed["tasks"].append(task)
        changed["task_families"].append({
            "family_id": task["task_family_id"],
            "stage": "B",
            "independence_group_id": task["independence_group_id"],
            "family_fingerprint_sha256": "0" * 64,
            "review_status": "draft",
        })
        changed["materialized_task_count"] += 1
        changed["materialized_stage_counts"]["B"] += 1
        errors = self.errors(changed)
        self.assertTrue(any(error.startswith("[stage-b]") for error in errors))

    def test_frozen_panel_requires_exact_stage_quota_and_accepted_validation(self) -> None:
        changed = copy.deepcopy(self.manifest)
        changed["status"] = "frozen"
        changed["frozen"] = True
        errors = self.errors(changed)
        self.assertTrue(any(error.startswith("[frozen]") for error in errors))

    def test_every_task_condition_must_have_a_deterministic_grader(self) -> None:
        changed = copy.deepcopy(self.manifest)
        changed["tasks"][0]["postconditions"][0]["condition"]["type"] = "unimplemented_condition"
        errors = self.errors(changed)
        self.assertTrue(
            any(error.startswith("[grader]") and "unimplemented_condition" in error for error in errors),
            "\\n".join(errors),
        )

    def test_fingerprint_helpers_are_deterministic(self) -> None:
        task = copy.deepcopy(self.manifest["tasks"][0])
        self.assertEqual(family_fingerprint(task), family_fingerprint(task))
        self.assertEqual(task_instance_fingerprint(task), task_instance_fingerprint(task))
        self.assertEqual(canonical_json({"b": 1, "a": 2}), '{"a":2,"b":1}')


    def test_tool_registry_digest_rejects_contract_mutation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="orbit-tool-registry-test-") as temporary:
            root = Path(temporary)
            registry_path = root / "DHI_v1" / "benchmark" / "fixtures" / "plugin_ecology" / "plugin_tool_registry.json"
            registry_path.parent.mkdir(parents=True)
            registry = json.loads(
                (REPO_ROOT / "DHI_v1" / "benchmark" / "fixtures" / "plugin_ecology" / "plugin_tool_registry.json").read_text(encoding="utf-8")
            )
            registry["tools"][0]["exact_contract_description"] += "\nmutated contract"
            registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            errors = self.errors(repo_root=root)
        self.assertTrue(
            any("tool_schema_sha256 mismatch" in error for error in errors),
            "\n".join(errors),
        )

    def test_malformed_nested_inventory_returns_errors_instead_of_crashing(self) -> None:
        changed = copy.deepcopy(self.manifest)
        changed["tasks"][0]["tool_inventory"] = None
        errors = self.errors(changed)
        self.assertTrue(any(error.startswith("[schema]") for error in errors))


    def test_plugin_trace_schema_and_grader_are_pinned_and_hashed(self) -> None:
        integrity = self.manifest["integrity"]
        self.assertEqual(integrity["trace_schema_path"], "DHI_v1/benchmark/plugin_trace.schema.json")
        self.assertEqual(integrity["trace_grader_path"], "DHI_v1/benchmark/plugin_trace.py")
        self.assertRegex(integrity["trace_schema_sha256"], r"^[a-f0-9]{64}$")
        self.assertRegex(integrity["trace_grader_sha256"], r"^[a-f0-9]{64}$")

    def test_plugin_trace_schema_hash_drift_is_rejected(self) -> None:
        changed = copy.deepcopy(self.manifest)
        changed["integrity"]["trace_schema_sha256"] = "0" * 64
        errors = self.errors(changed)
        self.assertTrue(any(error.startswith("[trace-contract]") for error in errors))

    def test_missing_plugin_trace_grader_path_is_rejected(self) -> None:
        changed = copy.deepcopy(self.manifest)
        changed["integrity"]["trace_grader_path"] = "DHI_v1/benchmark/not-a-grader.py"
        errors = self.errors(changed)
        self.assertTrue(any(error.startswith("[trace-contract]") for error in errors))


if __name__ == "__main__":
    unittest.main()
