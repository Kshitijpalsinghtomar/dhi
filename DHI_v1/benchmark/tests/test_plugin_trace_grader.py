from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from DHI_v1.benchmark.plugin_trace import grade_task, validate_trace


ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "DHI_v1" / "benchmark" / "plugin_trace.schema.json"


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def make_trace(events: list[dict] | None = None, *, artifacts: list[dict] | None = None) -> dict:
    return {
        "trace_schema_version": "orbit.plugin-trace.v1",
        "trajectory_id": "traj-test-001",
        "task_id": "ORBIT-A-S09-001",
        "task_instance_sha256": "a" * 64,
        "environment": {
            "environment_id": "github-sandbox",
            "version": "test-v1",
            "state_sha256": "b" * 64,
        },
        "tool_schema_sha256": "c" * 64,
        "provenance": {
            "evidence_class": "scripted-reference",
            "executor": "test-fixture",
            "recorded_at_utc": "2026-11-03T00:00:00Z",
        },
        "events": events if events is not None else [
            {
                "event_id": "e1",
                "event_index": 1,
                "event_type": "task_started",
                "timestamp_utc": "2026-11-03T00:00:00Z",
                "task_id": "ORBIT-A-S09-001",
                "source_ref": "fixture://task-start",
            },
            {
                "event_id": "e2",
                "event_index": 2,
                "event_type": "assistant_prediction",
                "timestamp_utc": "2026-11-03T00:00:01Z",
                "task_id": "ORBIT-A-S09-001",
                "expected_effects": {
                    "added_paths": ["reports/result.md"],
                    "modified_paths": [],
                    "deleted_paths": [],
                },
            },
            {
                "event_id": "e3",
                "event_index": 3,
                "event_type": "action_started",
                "timestamp_utc": "2026-11-03T00:00:02Z",
                "task_id": "ORBIT-A-S09-001",
                "action_id": "act-1",
                "tool_id": "mcp__GitHub__create_file",
                "arguments": {"path": "reports/result.md"},
                "observed_state_before": {"README.md": "b" * 64},
            },
            {
                "event_id": "e4",
                "event_index": 4,
                "event_type": "action_executed",
                "timestamp_utc": "2026-11-03T00:00:03Z",
                "task_id": "ORBIT-A-S09-001",
                "action_id": "act-1",
                "tool_id": "mcp__GitHub__create_file",
                "arguments": {"path": "reports/result.md"},
                "observed_state_before": {"README.md": "b" * 64},
                "observed_state_after": {"README.md": "b" * 64, "reports/result.md": "e" * 64},
                "actual_tool_result": {"ok": True, "result": {"blob_sha": "d" * 40}, "error": None},
                "actual_effects": {
                    "added_paths": ["reports/result.md"],
                    "modified_paths": [],
                    "deleted_paths": [],
                    "changed_paths": ["reports/result.md"],
                    "unchanged_paths": ["README.md"],
                },
            },
            {
                "event_id": "e5",
                "event_index": 5,
                "event_type": "task_closed",
                "timestamp_utc": "2026-11-03T00:00:04Z",
                "task_id": "ORBIT-A-S09-001",
                "closure_status": "success",
            },
        ],
        "final_answer": "Created and verified reports/result.md",
        "final_artifacts": artifacts if artifacts is not None else [],
        "usage": {"tool_calls": 1, "provider_credits_spent": 0},
    }


def make_task(condition: dict) -> dict:
    return {
        "task_id": "ORBIT-A-S09-001",
        "task_instance_sha256": "a" * 64,
        "postconditions": [{
            "verifier_id": "test-condition",
            "condition": condition,
            "expected_evidence": "test evidence",
            "failure_if_unmet": True,
        }],
    }


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


class PluginTraceValidationTests(unittest.TestCase):
    def test_valid_trace_with_prediction_action_pair_and_closure_passes(self) -> None:
        self.assertEqual(validate_trace(make_trace(), load_schema()), [])

    def test_action_execution_without_prior_start_is_rejected(self) -> None:
        trace = make_trace()
        trace["events"] = [trace["events"][0], trace["events"][1], trace["events"][3], trace["events"][4]]
        trace["events"][-2]["event_index"] = 3
        trace["events"][-1]["event_index"] = 4
        errors = validate_trace(trace, load_schema())
        self.assertTrue(any("action_executed has no preceding action_started" in error for error in errors))

    def test_action_arguments_must_match_between_start_and_execution(self) -> None:
        trace = make_trace()
        trace["events"][3]["arguments"]["path"] = "reports/other.md"
        errors = validate_trace(trace, load_schema())
        self.assertTrue(any("action arguments differ" in error for error in errors))

    def test_duplicate_event_ids_are_rejected(self) -> None:
        trace = make_trace()
        trace["events"][1]["event_id"] = trace["events"][0]["event_id"]
        errors = validate_trace(trace, load_schema())
        self.assertTrue(any("duplicate event_id" in error for error in errors))

    def test_non_contiguous_event_indices_are_rejected(self) -> None:
        trace = make_trace()
        trace["events"][2]["event_index"] = 9
        errors = validate_trace(trace, load_schema())
        self.assertTrue(any("event_index sequence" in error for error in errors))


class PluginTraceGraderTests(unittest.TestCase):
    def test_exact_text_condition_passes_only_exact_match(self) -> None:
        task = make_task({"type": "exact_text", "value": "703"})
        trace = make_trace()
        trace["final_answer"] = "703"
        report = grade_task(task, trace)
        self.assertEqual(report["status"], "pass")

    def test_tool_trace_checks_required_and_forbidden_tools(self) -> None:
        condition = {
            "type": "tool_trace",
            "required_tool": "mcp__GitHub__create_file",
            "forbidden_tools": ["mcp__GitHub__delete_file"],
        }
        report = grade_task(make_task(condition), make_trace())
        self.assertEqual(report["status"], "pass")

    def test_no_paid_action_requires_zero_credits_and_no_forbidden_tool(self) -> None:
        condition = {
            "type": "tool_trace_absence",
            "forbidden_tool": "mcp__Firecrawl__firecrawl_scrape",
            "forbidden_capability": "packages/package",
            "credits_spent": 0,
        }
        report = grade_task(make_task(condition), make_trace())
        self.assertEqual(report["status"], "pass")
        trace = make_trace()
        trace["usage"]["provider_credits_spent"] = 1
        self.assertEqual(grade_task(make_task(condition), trace)["status"], "fail")

    def test_branch_diff_only_rejects_unexpected_changed_paths(self) -> None:
        condition = {"type": "branch_diff_only", "allowed_paths": ["reports/result.md"]}
        self.assertEqual(grade_task(make_task(condition), make_trace())["status"], "pass")
        trace = make_trace()
        trace["events"][3]["observed_state_after"]["src/api.py"] = "f" * 64
        trace["events"][3]["actual_effects"]["added_paths"].append("src/api.py")
        trace["events"][3]["actual_effects"]["changed_paths"].append("src/api.py")
        self.assertEqual(grade_task(make_task(condition), trace)["status"], "fail")

    def test_prediction_must_be_recorded_before_write(self) -> None:
        condition = {
            "type": "assistant_trace_before_write",
            "predicted_added_paths": ["reports/result.md"],
            "predicted_modified_paths": [],
            "predicted_deleted_paths": [],
        }
        self.assertEqual(grade_task(make_task(condition), make_trace())["status"], "pass")
        trace = make_trace()
        trace["events"][1], trace["events"][3] = trace["events"][3], trace["events"][1]
        for index, event in enumerate(trace["events"], 1):
            event["event_index"] = index
        self.assertEqual(grade_task(make_task(condition), trace)["status"], "fail")

    def test_report_contains_all_checks_stored_artifact_content(self) -> None:
        report_text = "Passed: 3; Blocked: 1; Not Run: 1; Failed: 1"
        condition = {"type": "report_contains_all", "required": ["Passed: 3", "Blocked: 1", "Failed: 1"]}
        trace = make_trace(artifacts=[{
            "path": "reports/result.md",
            "content": report_text,
            "sha256": sha(report_text),
            "source_event_index": 4,
        }])
        self.assertEqual(grade_task(make_task(condition), trace)["status"], "pass")

    def test_artifact_hash_mismatch_invalidates_trace(self) -> None:
        text_value = "Verified report"
        trace = make_trace(artifacts=[{
            "path": "reports/result.md",
            "content": text_value,
            "sha256": "0" * 64,
            "source_event_index": 4,
        }])
        errors = validate_trace(trace, load_schema())
        self.assertTrue(any("artifact content SHA-256 mismatch" in error for error in errors))

    def test_unsupported_condition_is_unscorable_not_pass(self) -> None:
        report = grade_task(make_task({"type": "external_snapshot_match", "source": "https://example.test"}), make_trace())
        self.assertEqual(report["status"], "unscorable")
        self.assertEqual(report["results"][0]["status"], "unscorable")

    def test_mixed_supported_and_unsupported_conditions_do_not_overstate_success(self) -> None:
        task = {"postconditions": [
            {"verifier_id": "exact", "condition": {"type": "exact_text", "value": "Created and verified reports/result.md"}},
            {"verifier_id": "external", "condition": {"type": "external_snapshot_match", "source": "https://example.test"}},
        ]}
        report = grade_task(task, make_trace())
        self.assertEqual(report["status"], "unscorable")

    def test_invalid_trace_is_not_graded_as_success(self) -> None:
        trace = make_trace()
        trace["events"][3]["actual_tool_result"] = None
        report = grade_task(make_task({"type": "exact_text", "value": "Created and verified reports/result.md"}), trace, schema=load_schema())
        self.assertEqual(report["status"], "invalid_trace")


    def test_observed_state_delta_must_match_before_after_hashes(self) -> None:
        trace = make_trace()
        trace["events"][3]["actual_effects"]["added_paths"] = []
        errors = validate_trace(trace, load_schema())
        self.assertTrue(any("actual_effects differ from observed state hashes" in error for error in errors))

    def test_checkpoint_path_can_be_verified_from_resume_event(self) -> None:
        trace = make_trace()
        trace["events"].insert(4, {
            "event_id": "checkpoint",
            "event_index": 5,
            "event_type": "checkpoint_resumed",
            "timestamp_utc": "2026-11-03T00:00:03Z",
            "task_id": "ORBIT-A-S09-001",
            "checkpoint_ref": "checkpoints/session-A.md",
            "checkpoint_sha256": "f" * 64,
            "source_ref": "github://commit/checkpoint",
        })
        trace["events"][4]["event_index"] = 5
        for index, event in enumerate(trace["events"], 1):
            event["event_index"] = index
        trace["events"][-2]["event_index"] = len(trace["events"]) - 1
        trace["events"][-1]["event_index"] = len(trace["events"])
        condition = {"type": "tool_trace_contains", "path": "checkpoints/session-A.md"}
        self.assertEqual(grade_task(make_task(condition), trace)["status"], "pass")


    def test_source_fact_uses_raw_response_not_final_answer_claim(self) -> None:
        trace = make_trace()
        trace["final_answer"] = "Go 1.27.3 released on 2026-10-19"
        condition = {"type": "source_fact", "source": "https://go.dev/doc/devel/release", "expected": "Go 1.27.3 released on 2026-10-19"}
        self.assertEqual(grade_task(make_task(condition), trace)["status"], "unscorable")

    def test_source_fact_passes_when_source_request_and_response_support_it(self) -> None:
        trace = make_trace()
        trace["events"][3]["arguments"] = {"url": "https://go.dev/doc/devel/release"}
        trace["events"][3]["actual_tool_result"]["result"] = {"content": "Go 1.27.3 released on 2026-10-19"}
        condition = {"type": "source_fact", "source": "https://go.dev/doc/devel/release", "expected": "Go 1.27.3 released on 2026-10-19"}
        self.assertEqual(grade_task(make_task(condition), trace)["status"], "pass")

    def test_provider_contract_requires_structured_discovery_evidence(self) -> None:
        trace = make_trace()
        trace["events"].insert(1, {
            "event_id": "discover",
            "event_index": 2,
            "event_type": "tool_discovery",
            "timestamp_utc": "2026-11-03T00:00:00Z",
            "task_id": "ORBIT-A-S09-001",
            "query": "package metadata",
            "visible_tool_ids": [],
            "discovered_tool_ids": ["packages/package"],
            "discovery_results": [{
                "provider": "package-registry-metadata-download-stats",
                "capability": "packages/package",
                "required_inputs": ["registry", "name"],
                "execution_credits": 1,
                "discovery_credits": 0,
            }],
        })
        for index, event in enumerate(trace["events"], 1):
            event["event_index"] = index
        condition = {
            "type": "provider_capability_contract",
            "provider": "package-registry-metadata-download-stats",
            "capability": "packages/package",
            "required_inputs": ["registry", "name"],
            "execution_credits": 1,
            "discovery_credits": 0,
        }
        self.assertEqual(grade_task(make_task(condition), trace)["status"], "fail")

    def test_file_blob_match_verifies_sha_and_csv_data_rows(self) -> None:
        csv_text = "id,name\\n1,A\\n2,B\\n"
        trace = make_trace()
        trace["events"][2]["tool_id"] = "mcp__GitHub__fetch_file"
        trace["events"][3]["tool_id"] = "mcp__GitHub__fetch_file"
        trace["events"][2]["arguments"] = {"path": "data/items.csv"}
        trace["events"][3]["arguments"] = {"path": "data/items.csv"}
        trace["events"][2]["observed_state_before"] = {"data/items.csv": "b" * 64}
        trace["events"][3]["observed_state_before"] = {"data/items.csv": "b" * 64}
        trace["events"][3]["observed_state_after"] = {"data/items.csv": "b" * 64}
        trace["events"][3]["actual_effects"] = {
            "added_paths": [],
            "modified_paths": [],
            "deleted_paths": [],
            "changed_paths": [],
            "unchanged_paths": ["data/items.csv"],
        }
        trace["events"][3]["actual_tool_result"]["result"] = {
            "sha": "d" * 40,
            "content": csv_text,
        }
        condition = {
            "type": "file_blob_match",
            "path": "data/items.csv",
            "blob_sha": "d" * 40,
            "data_rows": 2,
            "header_rows": 1,
        }
        self.assertEqual(grade_task(make_task(condition), trace)["status"], "pass")

    def test_branch_state_delta_remains_unscorable_without_normalized_state_adapter(self) -> None:
        condition = {"type": "branch_state_delta", "after_expected": {"new_branch": "orbit/test"}}
        self.assertEqual(grade_task(make_task(condition), make_trace())["status"], "unscorable")

    def test_discovery_sequence_remains_unscorable_without_normalized_recovery_events(self) -> None:
        condition = {"type": "discovery_sequence", "sequence": ["fallback", "scoped_success"]}
        self.assertEqual(grade_task(make_task(condition), make_trace())["status"], "unscorable")


if __name__ == "__main__":
    unittest.main()
