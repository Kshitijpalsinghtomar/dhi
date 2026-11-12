from __future__ import annotations

import copy
import json
import unittest

from DHI_v1.benchmark.plugin_trace import grade_task
from test_plugin_trace_grader import make_trace


REPOSITORY = "Kshitijpalsinghtomar/dhi"
REF = "af6c0d31fcf2e3232cb427c421850536139e3b3a"
DIRECTORY = "DHI_v1/benchmark/fixtures/plugin_ecology/data"
BAD_PATH = f"{DIRECTORY}/work-items.csv"
GOOD_PATH = f"{DIRECTORY}/work_items.csv"
DIRECTORY_URL = (
    f"https://api.github.com/repos/{REPOSITORY}/contents/{DIRECTORY}?ref={REF}"
)
BLOB_SHA = "fe9f3fec31796694ec44711dfaf8a2dc1acbfe2d"
CSV_CONTENT = (
    "work_item_id,team,priority,estimate_hours,status,blocked_by\n"
    "NS-101,Platform,High,5,Open,\n"
    "NS-102,Data,Medium,3,In Progress,NS-101\n"
    "NS-103,Platform,Low,2,Done,\n"
    "NS-104,Research,High,8,Open,NS-102\n"
    "NS-105,Data,High,4,Open,\n"
    "NS-106,Research,Medium,6,In Progress,NS-105\n"
    "NS-107,Platform,Medium,1,Done,\n"
    "NS-108,Data,Low,2,Open,\n"
    "NS-109,Research,High,3,Blocked,NS-105\n"
    "NS-110,Platform,Medium,4,In Review,\n"
)


def load_task() -> dict:
    manifest = json.loads(
        (__import__("pathlib").Path(__file__).resolve().parents[1] / "task_manifest.json")
        .read_text(encoding="utf-8")
    )
    return copy.deepcopy(next(t for t in manifest["tasks"] if t["task_id"] == "ORBIT-A-S08-001"))


def _directory_listing(*, include_target: bool = True, target_sha: str = BLOB_SHA) -> str:
    entries = [
        {
            "name": "acceptance_tests.csv",
            "path": f"{DIRECTORY}/acceptance_tests.csv",
            "sha": "8e496af712058bb4ca120fd8003b0495e35f0e85",
            "type": "file",
        }
    ]
    if include_target:
        entries.append({
            "name": "work_items.csv",
            "path": GOOD_PATH,
            "sha": target_sha,
            "type": "file",
        })
    return json.dumps(entries, separators=(",", ":"))


def _action_pair(index: int, tool_id: str, arguments: dict, actual_tool_result: dict) -> list[dict]:
    action_id = f"s08-action-{index}"
    return [
        {
            "event_id": f"s08-start-{index}",
            "event_index": 0,
            "event_type": "action_started",
            "timestamp_utc": f"2026-11-03T00:00:0{index * 2}Z",
            "task_id": "ORBIT-A-S08-001",
            "action_id": action_id,
            "tool_id": tool_id,
            "arguments": copy.deepcopy(arguments),
        },
        {
            "event_id": f"s08-executed-{index}",
            "event_index": 0,
            "event_type": "action_executed",
            "timestamp_utc": f"2026-11-03T00:00:0{index * 2 + 1}Z",
            "task_id": "ORBIT-A-S08-001",
            "action_id": action_id,
            "tool_id": tool_id,
            "arguments": copy.deepcopy(arguments),
            "actual_tool_result": copy.deepcopy(actual_tool_result),
        },
    ]


def make_s08_trace() -> dict:
    task = load_task()
    trace = make_trace()
    trace["task_id"] = "ORBIT-A-S08-001"
    trace["task_instance_sha256"] = task["split_metadata"]["task_instance_sha256"]
    trace["environment"] = {
        "environment_id": task["environment"]["environment_id"],
        "version": task["environment"]["version"],
        "state_sha256": task["environment"]["state_sha256"],
    }
    trace["tool_schema_sha256"] = task["tool_inventory"]["tool_schema_sha256"]
    trace["provenance"]["evidence_class"] = "scripted-reference"
    trace["provenance"]["executor"] = "study0-s08-github-404-recovery-unit-test"
    failed_read = {
        "ok": False,
        "status_code": 404,
        "result": None,
        "error": "GitHub Contents API returned 404 Not Found (HTTP 404)",
        "provider_cost": 0,
    }
    directory_read = {
        "ok": True,
        "status_code": 200,
        "result": {
            "content": _directory_listing(),
            "title": "data",
            "url": DIRECTORY_URL,
        },
        "error": None,
        "provider_cost": 0,
    }
    successful_read = {
        "ok": True,
        "status_code": 200,
        "result": {
            "sha": BLOB_SHA,
            "content": CSV_CONTENT,
            "display_url": f"https://github.com/{REPOSITORY}/blob/{REF}/{GOOD_PATH}",
        },
        "error": None,
        "provider_cost": 0,
    }
    pairs = [
        _action_pair(1, "mcp__GitHub__fetch_file", {
            "repository_full_name": REPOSITORY,
            "path": BAD_PATH,
            "ref": REF,
        }, failed_read),
        _action_pair(2, "mcp__GitHub__fetch", {"url": DIRECTORY_URL}, directory_read),
        _action_pair(3, "mcp__GitHub__fetch_file", {
            "repository_full_name": REPOSITORY,
            "path": GOOD_PATH,
            "ref": REF,
        }, successful_read),
    ]
    events = [
        {
            "event_id": "s08-task-start",
            "event_index": 1,
            "event_type": "task_started",
            "timestamp_utc": "2026-11-03T00:00:00Z",
            "task_id": "ORBIT-A-S08-001",
            "source_ref": "fixture://s08-task-start",
        },
        {
            "event_id": "s08-prediction",
            "event_index": 2,
            "event_type": "assistant_prediction",
            "timestamp_utc": "2026-11-03T00:00:01Z",
            "task_id": "ORBIT-A-S08-001",
            "expected_effects": {
                "added_paths": [],
                "modified_paths": [],
                "deleted_paths": [],
            },
        },
    ]
    for pair in pairs:
        events.extend(pair)
    events.append({
        "event_id": "s08-task-close",
        "event_index": 0,
        "event_type": "task_closed",
        "timestamp_utc": "2026-11-03T00:00:09Z",
        "task_id": "ORBIT-A-S08-001",
        "closure_status": "success",
    })
    for i, event in enumerate(events, 1):
        event["event_index"] = i
    trace["events"] = events
    trace["usage"] = {"tool_calls": 3, "provider_credits_spent": 0}
    trace["final_answer"] = (
        f"Recovered {GOOD_PATH}; blob {BLOB_SHA}; 10 data rows."
    )
    return trace


def _pairs(trace: dict) -> list[list[dict]]:
    actions = {}
    for event in trace["events"]:
        if event.get("event_type") in {"action_started", "action_executed"}:
            actions.setdefault(event["action_id"], []).append(event)
    return [actions[f"s08-action-{i}"] for i in sorted(
        (int(key.rsplit("-", 1)[1]) for key in actions)
    ) for key in [f"s08-action-{i}"]]


def _rebuild(trace: dict, pairs: list[list[dict]]) -> None:
    prefix = [e for e in trace["events"] if e.get("event_type") in {"task_started", "assistant_prediction"}]
    suffix = [e for e in trace["events"] if e.get("event_type") == "task_closed"]
    events = prefix + [event for pair in pairs for event in pair] + suffix
    for i, event in enumerate(events, 1):
        event["event_index"] = i
    trace["events"] = events
    trace["usage"]["tool_calls"] = len(pairs)


def grade(trace: dict) -> dict:
    return grade_task(load_task(), trace)


class Study0GitHub404RecoveryTaskGraderTests(unittest.TestCase):
    def test_s08_001_accepts_exact_404_directory_recovery_and_pinned_file(self):
        result = grade(make_s08_trace())
        self.assertEqual(result["status"], "pass", result)

    def test_s08_001_rejects_404_for_a_different_initial_path(self):
        trace = make_s08_trace()
        for event in _pairs(trace)[0]:
            event["arguments"]["path"] = f"{DIRECTORY}/other.csv"
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s08_001_rejects_non_404_initial_failure(self):
        trace = make_s08_trace()
        _pairs(trace)[0][1]["actual_tool_result"]["status_code"] = 403
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s08_001_rejects_directory_lookup_before_the_404(self):
        trace = make_s08_trace()
        pairs = _pairs(trace)
        _rebuild(trace, [pairs[1], pairs[0], pairs[2]])
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s08_001_rejects_directory_lookup_for_another_folder(self):
        trace = make_s08_trace()
        for event in _pairs(trace)[1]:
            event["arguments"]["url"] = DIRECTORY_URL.replace("/data?", "/reports?")
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s08_001_rejects_directory_listing_that_omits_recovered_file(self):
        trace = make_s08_trace()
        event = _pairs(trace)[1][1]
        event["actual_tool_result"]["result"]["content"] = _directory_listing(include_target=False)
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s08_001_rejects_directory_entry_with_wrong_blob(self):
        trace = make_s08_trace()
        event = _pairs(trace)[1][1]
        event["actual_tool_result"]["result"]["content"] = _directory_listing(target_sha="0" * 40)
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s08_001_rejects_successful_file_fetch_before_directory_evidence(self):
        trace = make_s08_trace()
        pairs = _pairs(trace)
        _rebuild(trace, [pairs[0], pairs[2], pairs[1]])
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s08_001_rejects_fetch_of_a_different_final_path(self):
        trace = make_s08_trace()
        for event in _pairs(trace)[2]:
            event["arguments"]["path"] = f"{DIRECTORY}/acceptance_tests.csv"
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s08_001_rejects_failed_final_file_fetch(self):
        trace = make_s08_trace()
        result_event = _pairs(trace)[2][1]
        result_event["actual_tool_result"]["ok"] = False
        result_event["actual_tool_result"]["status_code"] = 404
        result_event["actual_tool_result"]["error"] = "still not found"
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s08_001_rejects_blind_retry_of_the_same_failing_path(self):
        trace = make_s08_trace()
        pairs = _pairs(trace)
        repeated = copy.deepcopy(pairs[0])
        for event in repeated:
            event["event_id"] = event["event_id"] + "-retry"
            event["action_id"] = "s08-action-4"
        _rebuild(trace, [pairs[0], repeated, pairs[1], pairs[2]])
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s08_001_rejects_spoofed_file_sha_when_content_is_different(self):
        trace = make_s08_trace()
        result_event = _pairs(trace)[2][1]
        result_event["actual_tool_result"]["result"]["content"] = (
            CSV_CONTENT.replace("NS-101", "NS-999")
        )
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)


if __name__ == "__main__":
    unittest.main()
