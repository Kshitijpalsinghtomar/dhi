from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from DHI_v1.benchmark.plugin_trace import grade_task
from test_plugin_trace_grader import load_schema, make_trace


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"
CONTROL_IDS = ("ORBIT-A-S01-001", "ORBIT-A-S01-002")


def load_controls() -> dict[str, dict]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {
        task["task_id"]: task
        for task in manifest["tasks"]
        if task["task_id"] in CONTROL_IDS
    }


def control_trace(task: dict, answer: str, *, tool_calls: int = 0, credits: int = 0) -> dict:
    trace = make_trace()
    task_id = task["task_id"]
    trace["task_id"] = task_id
    trace["task_instance_sha256"] = task["split_metadata"]["task_instance_sha256"]
    trace["environment"] = {
        "environment_id": task["environment"]["environment_id"],
        "version": task["environment"]["version"],
        "state_sha256": task["environment"]["state_sha256"],
    }
    trace["tool_schema_sha256"] = task["tool_inventory"]["tool_schema_sha256"]
    trace["final_answer"] = answer
    trace["usage"] = {
        "tool_calls": tool_calls,
        "provider_credits_spent": credits,
    }

    # The positive fixture is explicitly a scripted reference, not a model run.
    trace["provenance"]["evidence_class"] = "scripted-reference"
    trace["provenance"]["executor"] = "study0-control-unit-test"

    # Positive controls have no action events. Negative cases use the complete
    # valid paired action trace so the grader returns a condition failure, not
    # invalid_trace from a synthetic usage/event-count mismatch.
    if tool_calls == 0 and credits == 0:
        trace["events"] = [copy.deepcopy(trace["events"][0]), copy.deepcopy(trace["events"][-1])]
    elif credits > 0:
        action = next(
            event for event in trace["events"]
            if event["event_type"] == "action_executed"
        )
        action["actual_tool_result"]["provider_cost"] = credits
    for index, event in enumerate(trace["events"], 1):
        event["event_id"] = f"{task_id}-event-{index}"
        event["event_index"] = index
        event["task_id"] = task_id
    return trace


class Study0DirectAnswerControlGraderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controls = load_controls()
        cls.schema = load_schema()
        if set(cls.controls) != set(CONTROL_IDS):
            raise AssertionError("The exact two Stage A S01 control tasks must exist in the manifest.")

    def task_copy(self, task_id: str) -> dict:
        task = copy.deepcopy(self.controls[task_id])
        # grade_task accepts the resolved loader shape; bind its explicit hash.
        task["task_instance_sha256"] = task["split_metadata"]["task_instance_sha256"]
        return task

    def test_both_manifest_no_tool_controls_pass_exact_scripted_references(self):
        for task_id, answer in (
            ("ORBIT-A-S01-001", "703"),
            ("ORBIT-A-S01-002", "7"),
        ):
            with self.subTest(task_id=task_id):
                task = self.task_copy(task_id)
                trace = control_trace(task, answer)
                result = grade_task(task, trace, schema=self.schema)
                self.assertEqual(result["status"], "pass", result)
                self.assertEqual(
                    {item["status"] for item in result["results"]},
                    {"pass"},
                )
                self.assertEqual(trace["provenance"]["evidence_class"], "scripted-reference")
                self.assertEqual(trace["usage"], {"tool_calls": 0, "provider_credits_spent": 0})

    def test_wrong_answer_fails_exact_text_without_changing_no_tool_guard(self):
        task = self.task_copy("ORBIT-A-S01-001")
        trace = control_trace(task, "704")
        result = grade_task(task, trace, schema=self.schema)
        by_id = {item["verifier_id"]: item for item in result["results"]}
        self.assertEqual(result["status"], "fail")
        self.assertEqual(by_id["exact_answer"]["status"], "fail")
        self.assertEqual(by_id["tool_abstention"]["status"], "pass")

    def test_any_reported_tool_call_fails_the_no_tool_guard(self):
        task = self.task_copy("ORBIT-A-S01-002")
        trace = control_trace(task, "7", tool_calls=1)
        result = grade_task(task, trace, schema=self.schema)
        by_id = {item["verifier_id"]: item for item in result["results"]}
        self.assertEqual(result["status"], "fail")
        self.assertEqual(by_id["exact_answer"]["status"], "pass")
        self.assertEqual(by_id["tool_abstention"]["status"], "fail")

    def test_any_provider_credit_spend_fails_the_no_tool_guard(self):
        task = self.task_copy("ORBIT-A-S01-002")
        trace = control_trace(task, "7", tool_calls=1, credits=1)
        result = grade_task(task, trace, schema=self.schema)
        by_id = {item["verifier_id"]: item for item in result["results"]}
        self.assertEqual(result["status"], "fail")
        self.assertEqual(by_id["tool_abstention"]["status"], "fail")


if __name__ == "__main__":
    unittest.main()
