from __future__ import annotations

import copy
import unittest

from DHI_v1.benchmark.plugin_trace import grade_task
from test_plugin_trace_grader import make_task, make_trace


TASK_ID = "ORBIT-A-S05-003"
REPOSITORY = "Kshitijpalsinghtomar/dhi"
PATH = "DHI_v1/benchmark/fixtures/plugin_ecology/reports/update-file-contract.md"
BRANCH = "orbit/plugin-benchmark-fixture"
SEED_REF = "fa0c47781539f9c5bbe68ef6457c2b4dae258cc4"
SEED_BLOB = "ae7694c15fc2949184a7267dc9fa8e430fd6e037"
UPDATED_BLOB = "68ec2aab89854ca674f64b1c3f087e1f233c54af"
UPDATE_COMMIT = "0e2e0b08a48d8348dc80eb83d52804df61cfb9f5"
UPDATED_CONTENT = """# Plugin update contract — verified result

Status: complete

The TinyFish release snapshots and Firecrawl provider discovery records are pinned under `fixtures/plugin_ecology/`.

The ORBIT GitHub update_file action must use the exact current blob SHA returned by fetch_file, the complete replacement content, a non-empty commit message, and the explicit benchmark branch `orbit/plugin-benchmark-fixture`.

The update is verified only after fetching this file again and confirming that the branch diff from the seed commit contains this path as modified, with no other paths changed.

No source, task policy, issue state, deployment or external provider has been changed.
"""


def condition() -> dict:
    return {
        "type": "github_update_file_transaction",
        "repository_full_name": REPOSITORY,
        "path": PATH,
        "branch": BRANCH,
        "seed_ref": SEED_REF,
        "expected_seed_blob_sha": SEED_BLOB,
        "expected_updated_blob_sha": UPDATED_BLOB,
        "expected_content": UPDATED_CONTENT,
        "expected_tool_sequence": [
            "mcp__GitHub__fetch_file",
            "mcp__GitHub__update_file",
            "mcp__GitHub__fetch_file",
            "mcp__GitHub__compare_commits",
        ],
        "expected_diff": {
            "status": "modified",
            "additions": 8,
            "deletions": 4,
            "changes": 12,
        },
    }


def make_transaction_trace() -> dict:
    trace = make_trace()
    trace["task_id"] = TASK_ID
    for event in trace["events"]:
        event["task_id"] = TASK_ID

    actions = [
        {
            "tool": "mcp__GitHub__fetch_file",
            "args": {
                "repository_full_name": REPOSITORY,
                "path": PATH,
                "ref": BRANCH,
            },
            "result": {
                "ok": True,
                "result": {"sha": SEED_BLOB, "content": "# Plugin update contract — seed\n\nStatus: draft\n\nThis file is an existing report target for the ORBIT GitHub update_file argument-contract task.\n\nThe task is not complete until the file is updated with the final evidence statement, fetched back, and compared to the seed commit. Only this file may change.\n"},
                "error": None,
            },
            "side_effect": None,
        },
        {
            "tool": "mcp__GitHub__update_file",
            "args": {
                "repository_full_name": REPOSITORY,
                "path": PATH,
                "content": UPDATED_CONTENT,
                "message": "test(orbit): update existing report using current blob SHA",
                "sha": SEED_BLOB,
                "branch": BRANCH,
            },
            "result": {
                "ok": True,
                "result": {
                    "commit_sha": UPDATE_COMMIT,
                    "content_sha": UPDATED_BLOB,
                },
                "error": None,
            },
            "side_effect": "external_write",
        },
        {
            "tool": "mcp__GitHub__fetch_file",
            "args": {
                "repository_full_name": REPOSITORY,
                "path": PATH,
                "ref": BRANCH,
            },
            "result": {
                "ok": True,
                "result": {"sha": UPDATED_BLOB, "content": UPDATED_CONTENT},
                "error": None,
            },
            "side_effect": None,
        },
        {
            "tool": "mcp__GitHub__compare_commits",
            "args": {
                "repo_full_name": REPOSITORY,
                "base": SEED_REF,
                "head": UPDATE_COMMIT,
            },
            "result": {
                "ok": True,
                "result": {
                    "base": SEED_REF,
                    "head": UPDATE_COMMIT,
                    "status": "ahead",
                    "ahead_by": 1,
                    "behind_by": 0,
                    "files": [{
                        "filename": PATH,
                        "status": "modified",
                        "additions": 8,
                        "deletions": 4,
                        "changes": 12,
                    }],
                },
                "error": None,
            },
            "side_effect": None,
        },
    ]

    events = trace["events"][:2]
    event_index = 3
    for action_no, action in enumerate(actions, 1):
        action_id = f"s05-003-action-{action_no}"
        start = {
            "event_id": f"s05-003-start-{action_no}",
            "event_index": event_index,
            "event_type": "action_started",
            "timestamp_utc": f"2026-11-03T00:00:{event_index:02d}Z",
            "task_id": TASK_ID,
            "action_id": action_id,
            "tool_id": action["tool"],
            "arguments": copy.deepcopy(action["args"]),
        }
        if action["side_effect"]:
            start["side_effect_class"] = action["side_effect"]
        event_index += 1
        executed = {
            "event_id": f"s05-003-executed-{action_no}",
            "event_index": event_index,
            "event_type": "action_executed",
            "timestamp_utc": f"2026-11-03T00:00:{event_index:02d}Z",
            "task_id": TASK_ID,
            "action_id": action_id,
            "tool_id": action["tool"],
            "arguments": copy.deepcopy(action["args"]),
            "actual_tool_result": copy.deepcopy(action["result"]),
        }
        events.extend([start, executed])
        event_index += 1

    events.append({
        "event_id": "s05-003-close",
        "event_index": event_index,
        "event_type": "task_closed",
        "timestamp_utc": f"2026-11-03T00:00:{event_index:02d}Z",
        "task_id": TASK_ID,
        "closure_status": "success",
    })
    trace["events"] = events
    trace["usage"] = {"tool_calls": 4, "provider_credits_spent": 0}
    return trace


def grade(trace: dict):
    task = make_task(condition(), task_id=TASK_ID)
    return grade_task(task, trace)


def action_event(trace: dict, action_no: int, event_type: str) -> dict:
    return next(
        event for event in trace["events"]
        if event.get("event_id") == f"s05-003-{event_type}-{action_no}"
    )


class Study0GitHubUpdateFileTaskGraderTests(unittest.TestCase):
    def test_s05_003_accepts_exact_sha_branch_readback_and_single_path_diff(self):
        result = grade(make_transaction_trace())
        self.assertEqual(result["status"], "pass", result)

    def test_s05_003_rejects_pre_read_content_not_matching_provider_blob_sha(self):
        trace = make_transaction_trace()
        pre_read = action_event(trace, 1, "executed")
        pre_read["actual_tool_result"]["result"]["content"] = (
            pre_read["actual_tool_result"]["result"]["content"].replace("Status: draft", "Status: final")
        )
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_003_rejects_update_sha_not_obtained_from_pre_read(self):
        trace = make_transaction_trace()
        for event in trace["events"]:
            if event.get("action_id") == "s05-003-action-2":
                event["arguments"]["sha"] = "f" * 40
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_003_rejects_update_to_main(self):
        trace = make_transaction_trace()
        for event in trace["events"]:
            if event.get("action_id") == "s05-003-action-2":
                event["arguments"]["branch"] = "main"
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_003_rejects_create_file_substitution(self):
        trace = make_transaction_trace()
        for event in trace["events"]:
            if event.get("action_id") == "s05-003-action-2":
                event["tool_id"] = "mcp__GitHub__create_file"
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_003_rejects_partial_replacement_content(self):
        trace = make_transaction_trace()
        for event in trace["events"]:
            if event.get("action_id") == "s05-003-action-2":
                event["arguments"]["content"] = "Status: complete\n"
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_003_rejects_failed_update(self):
        trace = make_transaction_trace()
        executed = action_event(trace, 2, "executed")
        executed["actual_tool_result"]["ok"] = False
        executed["actual_tool_result"]["error"] = "stale blob SHA"
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_003_rejects_readback_with_wrong_blob(self):
        trace = make_transaction_trace()
        executed = action_event(trace, 3, "executed")
        executed["actual_tool_result"]["result"]["sha"] = "0" * 40
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_003_rejects_readback_before_update(self):
        trace = make_transaction_trace()
        starts = {e["action_id"]: i for i, e in enumerate(trace["events"]) if e["event_type"] == "action_started"}
        first_read = starts["s05-003-action-1"]
        write = starts["s05-003-action-2"]
        readback = starts["s05-003-action-3"]
        compare = starts["s05-003-action-4"]
        events = trace["events"]
        # Move the readback pair before the update pair, then restore contiguous indices.
        pair = events[readback:readback + 2]
        del events[readback:readback + 2]
        events[first_read + 2:first_read + 2] = pair
        for index, event in enumerate(events, 1):
            event["event_index"] = index
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_003_rejects_compare_with_an_extra_changed_path(self):
        trace = make_transaction_trace()
        executed = action_event(trace, 4, "executed")
        executed["actual_tool_result"]["result"]["files"].append({
            "filename": "README.md",
            "status": "modified",
            "additions": 1,
            "deletions": 0,
            "changes": 1,
        })
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_003_rejects_compare_head_not_returned_by_update_file(self):
        trace = make_transaction_trace()
        started = action_event(trace, 4, "start")
        compare = action_event(trace, 4, "executed")
        started["arguments"]["head"] = "1" * 40
        compare["arguments"]["head"] = "1" * 40
        compare["actual_tool_result"]["result"]["head"] = "1" * 40
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)


if __name__ == "__main__":
    unittest.main()
