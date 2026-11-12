from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from DHI_v1.benchmark.plugin_trace import grade_task
from test_plugin_trace_grader import make_trace


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"
TASK_ID = "ORBIT-A-S04-001"
POLICY_PATH = "DHI_v1/benchmark/fixtures/plugin_ecology/TASK_POLICY.md"
PINNED_REF = "af6c0d31fcf2e3232cb427c421850536139e3b3a"
EXPECTED_BLOB_SHA = "0e5d3c519749651ad5f5ec728622895cfc44a649"


def load_task() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    task = next(item for item in manifest["tasks"] if item["task_id"] == TASK_ID)
    task = copy.deepcopy(task)
    task["task_instance_sha256"] = task["split_metadata"]["task_instance_sha256"]
    return task


def make_s04_trace(task: dict, *, blob_sha: str = EXPECTED_BLOB_SHA, ref: str = PINNED_REF,
                   tool_id: str = "mcp__GitHub__fetch_file", read_ok: bool = True) -> dict:
    trace = make_trace()
    trace["task_id"] = TASK_ID
    trace["task_instance_sha256"] = task["task_instance_sha256"]
    trace["environment"] = {
        "environment_id": task["environment"]["environment_id"],
        "version": task["environment"]["version"],
        "state_sha256": task["environment"]["state_sha256"],
    }
    trace["tool_schema_sha256"] = task["tool_inventory"]["tool_schema_sha256"]
    trace["provenance"]["evidence_class"] = "scripted-reference"
    trace["provenance"]["executor"] = "study0-s04-tool-selection-unit-test"

    arguments = {
        "repository_full_name": "Kshitijpalsinghtomar/dhi",
        "path": POLICY_PATH,
        "ref": ref,
    }
    for event in trace["events"]:
        event["task_id"] = TASK_ID

    read_action_id = "read-task-policy"
    for event in trace["events"][2:4]:
        event["tool_id"] = tool_id
        event["action_id"] = read_action_id
        event["arguments"] = copy.deepcopy(arguments)
    trace["events"][2]["side_effect_class"] = "read_only"
    trace["events"][3]["actual_tool_result"] = {
        "ok": read_ok,
        "result": {"sha": blob_sha, "content": "Pinned TASK_POLICY.md"} if read_ok else None,
        "error": None if read_ok else "fixture read failed",
    }

    state_sha = hashlib.sha256(b"pinned policy file state").hexdigest()
    before = {POLICY_PATH: state_sha}
    for event in trace["events"][2:4]:
        event["observed_state_before"] = copy.deepcopy(before)
        event["observed_state_after"] = copy.deepcopy(before)
        event["actual_effects"] = {
            "added_paths": [],
            "modified_paths": [],
            "deleted_paths": [],
            "changed_paths": [],
            "unchanged_paths": [POLICY_PATH],
        }

    trace["usage"] = {"tool_calls": 1, "provider_credits_spent": 0}
    trace["final_answer"] = "Read the pinned task policy using the read-only file tool."
    for index, event in enumerate(trace["events"], 1):
        event["event_index"] = index
        event["event_id"] = f"{TASK_ID}-event-{index}"
        event["task_id"] = TASK_ID
    return trace


class Study0ReadOnlyGitHubTaskGraderTests(unittest.TestCase):
    def test_s04_001_accepts_exact_read_tool_arguments_and_pinned_blob(self):
        task = load_task()
        policy_file = ROOT / POLICY_PATH
        raw = policy_file.read_bytes()
        git_blob_sha = hashlib.sha1(
            b"blob " + str(len(raw)).encode("ascii") + bytes([0]) + raw
        ).hexdigest()
        self.assertEqual(git_blob_sha, EXPECTED_BLOB_SHA)
        result = grade_task(task, make_s04_trace(task))
        self.assertEqual(result["status"], "pass", result)

    def test_s04_001_rejects_wrong_blob_sha(self):
        task = load_task()
        result = grade_task(task, make_s04_trace(task, blob_sha="0" * 40))
        self.assertEqual(result["status"], "fail", result)

    def test_s04_001_rejects_wrong_repository_ref(self):
        task = load_task()
        result = grade_task(task, make_s04_trace(task, ref="main"))
        self.assertEqual(result["status"], "fail", result)

    def test_s04_001_rejects_failed_file_read(self):
        task = load_task()
        result = grade_task(task, make_s04_trace(task, read_ok=False))
        self.assertEqual(result["status"], "fail", result)

    def test_s04_001_rejects_write_tool_substitution(self):
        task = load_task()
        result = grade_task(task, make_s04_trace(task, tool_id="mcp__GitHub__create_file"))
        self.assertEqual(result["status"], "fail", result)


if __name__ == "__main__":
    unittest.main()
