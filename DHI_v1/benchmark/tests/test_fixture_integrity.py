import json
import tempfile
import unittest
from pathlib import Path

from DHI_v1.benchmark.runner import apply_fixture_variant
from DHI_v1.environment.dhi_env import DHIEnvironment, TaskSpec
from DHI_v1.environment.fixture_manager import materialize_fixture, validate_fixture


FIXTURE_ROOT = Path(__file__).resolve().parents[2] / "environment" / "fixtures" / "basic_repo"
SUITE_PATH = Path(__file__).resolve().parents[1] / "pilot_cases.json"


class TestPinnedBasicRepositoryFixture(unittest.TestCase):
    def test_checked_in_fixture_manifest_matches_all_payloads(self):
        manifest = validate_fixture(FIXTURE_ROOT)
        self.assertEqual(manifest["fixture_id"], "dhi-v1-basic-repository")
        self.assertEqual(manifest["file_count"], 3)

    def test_already_complete_variant_satisfies_noop_task_without_changes(self):
        suite = json.loads(SUITE_PATH.read_text(encoding="utf-8"))
        case = next(item for item in suite["cases"] if item["case_id"] == "file-005-already-satisfied-no-op")
        with tempfile.TemporaryDirectory(prefix="dhi-noop-fixture-test-") as temporary:
            workspace = Path(temporary) / "workspace"
            materialize_fixture(FIXTURE_ROOT, workspace)
            apply_fixture_variant(case, workspace)
            task = TaskSpec(
                task_id=case["case_id"],
                prompt=case["prompt"],
                goal=case["goal"],
                hard_constraints=case.get("hard_constraints", []),
                preferences=case.get("preferences", []),
                postconditions=case["postconditions"],
                protected_paths=case.get("protected_paths", []),
                visible_tool_ids=case.get("visible_tool_ids"),
                fault_injections=case.get("fault_injections", []),
                metadata={"fixture_validation": True},
            )
            environment = DHIEnvironment(workspace)
            environment.begin_task(task)
            closure = environment.close_task()
            self.assertTrue(closure["success"], closure["failed_postconditions"])
            self.assertEqual(closure["event"]["overall_effects"]["changed_paths"], [])
