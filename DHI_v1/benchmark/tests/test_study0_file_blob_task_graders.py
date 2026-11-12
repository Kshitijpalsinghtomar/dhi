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
TASK_ID = "ORBIT-A-S05-001"
CSV_PATH = "DHI_v1/benchmark/fixtures/plugin_ecology/data/work_items.csv"
PINNED_REF = "af6c0d31fcf2e3232cb427c421850536139e3b3a"
EXPECTED_BLOB_SHA = "fe9f3fec31796694ec44711dfaf8a2dc1acbfe2d"


def load_task() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    task = copy.deepcopy(next(item for item in manifest["tasks"] if item["task_id"] == TASK_ID))
    task["task_instance_sha256"] = task["split_metadata"]["task_instance_sha256"]
    return task


def git_blob_sha(content: bytes) -> str:
    return hashlib.sha1(
        b"blob " + str(len(content)).encode("ascii") + bytes([0]) + content
    ).hexdigest()


def make_s05_trace(task: dict, *, ref: str = PINNED_REF, blob_sha: str = EXPECTED_BLOB_SHA,
                   read_ok: bool = True) -> dict:
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
    trace["provenance"]["executor"] = "study0-s05-csv-grader-unit-test"
    args = {
        "repository_full_name": "Kshitijpalsinghtomar/dhi",
        "path": CSV_PATH,
        "ref": ref,
    }
    for event in trace["events"]:
        event["task_id"] = TASK_ID
    for event in trace["events"][2:4]:
        event["tool_id"] = "mcp__GitHub__fetch_file"
        event["action_id"] = "fetch-work-items-csv"
        event["arguments"] = copy.deepcopy(args)
        event["observed_state_before"] = {CSV_PATH: "b" * 64}
        event["observed_state_after"] = {CSV_PATH: "b" * 64}
        event["actual_effects"] = {
            "added_paths": [],
            "modified_paths": [],
            "deleted_paths": [],
            "changed_paths": [],
            "unchanged_paths": [CSV_PATH],
        }
    source_content = (ROOT / CSV_PATH).read_text(encoding="utf-8")
    trace["events"][3]["actual_tool_result"] = {
        "ok": read_ok,
        "result": {"sha": blob_sha, "content": source_content},
        "error": None if read_ok else "provider read failed",
    }
    trace["usage"] = {"tool_calls": 1, "provider_credits_spent": 0}
    trace["final_answer"] = "Fetched the pinned work_items.csv and verified its SHA and row count."
    for index, event in enumerate(trace["events"], 1):
        event["event_id"] = f"{TASK_ID}-event-{index}"
        event["event_index"] = index
        event["task_id"] = TASK_ID
    return trace


class Study0FileBlobTaskGraderTests(unittest.TestCase):
    def test_s05_001_accepts_exact_pinned_csv_blob_and_row_count(self):
        task = load_task()
        source = (ROOT / CSV_PATH).read_bytes()
        self.assertEqual(git_blob_sha(source), EXPECTED_BLOB_SHA)
        result = grade_task(task, make_s05_trace(task))
        self.assertEqual(result["status"], "pass", result)

    def test_s05_001_rejects_wrong_repository_ref(self):
        task = load_task()
        result = grade_task(task, make_s05_trace(task, ref="main"))
        self.assertEqual(result["status"], "fail", result)

    def test_s05_001_rejects_wrong_blob_sha(self):
        task = load_task()
        result = grade_task(task, make_s05_trace(task, blob_sha="0" * 40))
        self.assertEqual(result["status"], "fail", result)

    def test_s05_001_rejects_wrong_csv_row_count(self):
        task = load_task()
        task["postconditions"][0]["condition"]["data_rows"] = 9
        result = grade_task(task, make_s05_trace(task))
        self.assertEqual(result["status"], "fail", result)

    def test_s05_001_rejects_failed_file_read(self):
        task = load_task()
        result = grade_task(task, make_s05_trace(task, read_ok=False))
        self.assertEqual(result["status"], "fail", result)


if __name__ == "__main__":
    unittest.main()
