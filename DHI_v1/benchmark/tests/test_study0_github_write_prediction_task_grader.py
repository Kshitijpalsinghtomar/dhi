from __future__ import annotations

import copy
import hashlib
import unittest
from pathlib import Path

from DHI_v1.benchmark.plugin_trace import grade_task, validate_trace


ROOT = Path(__file__).resolve().parents[3]
SCHEMA_PATH = ROOT / "DHI_v1" / "benchmark" / "plugin_trace.schema.json"

REPOSITORY = "Kshitijpalsinghtomar/dhi"
BRANCH = "orbit/s09-effect-prediction"
BASE_COMMIT = "af6c0d31fcf2e3232cb427c421850536139e3b3a"
WRITE_COMMIT = "d" * 40
REPORT_PATH = "DHI_v1/benchmark/fixtures/plugin_ecology/reports/effect-check.md"
REPORT_CONTENT = """# Northstar Workbench acceptance check

Source: DHI_v1/benchmark/fixtures/plugin_ecology/data/acceptance_tests.csv
Verified acceptance-test counts:
- Passed: 3
- Blocked: 1
- Not Run: 1
- Failed: 1

These are acceptance-matrix statuses, not a claim of release readiness.
"""


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def git_blob_sha(value: str) -> str:
    data = value.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def load_schema() -> dict:
    import json
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def condition() -> dict:
    return {
        "type": "github_write_prediction_closure",
        "repository_full_name": REPOSITORY,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "report_path": REPORT_PATH,
        "predicted_added_paths": [REPORT_PATH],
        "predicted_modified_paths": [],
        "predicted_deleted_paths": [],
        "required_report_phrases": ["Passed: 3", "Blocked: 1", "Not Run: 1", "Failed: 1"],
        "min_tool_calls": 3,
        "max_tool_calls": 5,
    }


def append_action(events: list[dict], tool_id: str, action_id: str, arguments: dict, result: dict,
                  *, before: dict | None = None, after: dict | None = None,
                  effects: dict | None = None, side_effect_class: str = "read_only") -> None:
    index = len(events) + 1
    events.append({
        "event_id": f"e{index}", "event_index": index, "event_type": "action_started",
        "timestamp_utc": f"2026-11-03T00:00:{index:02d}Z", "task_id": "ORBIT-A-S09-001",
        "action_id": action_id, "tool_id": tool_id, "arguments": copy.deepcopy(arguments),
        "observed_state_before": copy.deepcopy(before or {}),
        "side_effect_class": side_effect_class,
    })
    index = len(events) + 1
    before_state = copy.deepcopy(before or {})
    after_state = copy.deepcopy(after if after is not None else before or {})
    if effects is None:
        added = sorted(set(after_state) - set(before_state))
        deleted = sorted(set(before_state) - set(after_state))
        modified = sorted(path for path in set(before_state) & set(after_state) if before_state[path] != after_state[path])
        actual_effects = {
            "added_paths": added, "modified_paths": modified, "deleted_paths": deleted,
            "changed_paths": sorted(set(added + modified + deleted)),
            "unchanged_paths": sorted(path for path in set(before_state) & set(after_state) if before_state[path] == after_state[path]),
        }
    else:
        actual_effects = copy.deepcopy(effects)
    events.append({
        "event_id": f"e{index}", "event_index": index, "event_type": "action_executed",
        "timestamp_utc": f"2026-11-03T00:00:{index:02d}Z", "task_id": "ORBIT-A-S09-001",
        "action_id": action_id, "tool_id": tool_id, "arguments": copy.deepcopy(arguments),
        "observed_state_before": before_state,
        "observed_state_after": after_state,
        "actual_tool_result": {"ok": True, "result": copy.deepcopy(result), "error": None},
        "actual_effects": actual_effects,
    })


def build_trace(report: str = REPORT_CONTENT) -> dict:
    events = [{
        "event_id": "e1", "event_index": 1, "event_type": "task_started",
        "timestamp_utc": "2026-11-03T00:00:00Z", "task_id": "ORBIT-A-S09-001",
        "source_ref": "fixture://northstar-s09",
    }, {
        "event_id": "e2", "event_index": 2, "event_type": "assistant_prediction",
        "timestamp_utc": "2026-11-03T00:00:01Z", "task_id": "ORBIT-A-S09-001",
        "expected_effects": {"added_paths": [REPORT_PATH], "modified_paths": [], "deleted_paths": []},
    }]
    before = {"README.md": sha("unchanged pinned fixture readme")}
    after = {**before, REPORT_PATH: sha(report)}
    append_action(
        events, "mcp__GitHub__create_file", "write-1",
        {"repository_full_name": REPOSITORY, "path": REPORT_PATH, "content": report,
         "message": "test: create predicted S09 report", "branch": BRANCH},
        {"commit_sha": WRITE_COMMIT}, before=before, after=after,
        effects={"added_paths": [REPORT_PATH], "modified_paths": [], "deleted_paths": [],
                 "changed_paths": [REPORT_PATH], "unchanged_paths": ["README.md"]},
        side_effect_class="sandbox_write",
    )
    report_url = f"https://github.com/{REPOSITORY}/blob/{BRANCH}/{REPORT_PATH}"
    append_action(
        events, "mcp__GitHub__fetch_file", "read-1",
        {"repository_full_name": REPOSITORY, "path": REPORT_PATH, "ref": BRANCH},
        {"content": report, "sha": git_blob_sha(report), "display_url": report_url},
        before=after, after=after,
    )
    readback_index = len(events) + 1
    events.append({
        "event_id": f"e{readback_index}", "event_index": readback_index,
        "event_type": "artifact_readback", "timestamp_utc": "2026-11-03T00:00:08Z",
        "task_id": "ORBIT-A-S09-001",
        "artifact_readback": {
            "path": REPORT_PATH, "repository_full_name": REPOSITORY, "ref": BRANCH,
            "status": "verified", "source_action_id": "write-1",
            "sha256": sha(report), "blob_sha": git_blob_sha(report), "source_ref": report_url,
        },
    })
    append_action(
        events, "mcp__GitHub__compare_commits", "compare-1",
        {"repo_full_name": REPOSITORY, "base": BASE_COMMIT, "head": WRITE_COMMIT},
        {"base": BASE_COMMIT, "head": WRITE_COMMIT, "status": "ahead",
         "ahead_by": 1, "behind_by": 0, "total_commits": 1,
         "files": [{"filename": REPORT_PATH, "status": "added", "additions": 9, "deletions": 0, "changes": 9}]},
        before=after, after=after,
    )
    closed_index = len(events) + 1
    events.append({
        "event_id": f"e{closed_index}", "event_index": closed_index,
        "event_type": "task_closed", "timestamp_utc": "2026-11-03T00:00:12Z",
        "task_id": "ORBIT-A-S09-001", "closure_status": "success",
        "prediction_comparison": {"status": "correct", "matched_fields": ["added_paths", "modified_paths", "deleted_paths"], "missed_fields": [], "details": "The observed one-file add matched the pre-write prediction."},
    })
    return {
        "trace_schema_version": "orbit.plugin-trace.v1",
        "trajectory_id": "s09-prediction-test",
        "task_id": "ORBIT-A-S09-001",
        "task_instance_sha256": "a" * 64,
        "environment": {"environment_id": "github-plugin-side-effect-sandbox",
                        "version": "github-tool-registry@4a5a390a5e7246366f17f504cf14b62c56ba6f86",
                        "state_sha256": "b" * 64},
        "tool_schema_sha256": "c" * 64,
        "provenance": {"evidence_class": "scripted-reference", "executor": "unit-test",
                       "recorded_at_utc": "2026-11-03T00:00:00Z"},
        "events": events,
        "final_answer": "Created the report and verified the observed branch effect.",
        "final_artifacts": [{
            "path": REPORT_PATH, "content": report, "sha256": sha(report),
            "blob_sha": git_blob_sha(report), "status": "read",
            "source_event_index": readback_index, "source_ref": report_url,
        }],
        "usage": {"tool_calls": 3, "provider_credits_spent": 0},
        "closure": {"status": "success", "verified_postconditions": [],
                    "failed_postconditions": [], "final_state_sha256": "e" * 64,
                    "closed_at_utc": "2026-11-03T00:00:12Z"},
    }


class TestStudy0GithubWritePrediction(unittest.TestCase):
    def grade(self, trace: dict) -> dict:
        task = {
            "task_id": "ORBIT-A-S09-001", "task_instance_sha256": "a" * 64,
            "postconditions": [{"verifier_id": "write_prediction_closure",
                                "condition": condition(), "expected_evidence": "prediction/readback/diff",
                                "failure_if_unmet": True}],
        }
        return grade_task(task, trace, schema=load_schema())

    def test_success_requires_prediction_write_readback_and_compare_chain(self):
        report = self.grade(build_trace())
        self.assertEqual(report["status"], "pass", report)

    def test_missing_prediction_is_rejected(self):
        trace = build_trace()
        trace["events"] = [e for e in trace["events"] if e["event_type"] != "assistant_prediction"]
        self.reindex(trace)
        self.assertEqual(self.grade(trace)["status"], "fail")

    def test_prediction_after_write_invocation_is_rejected(self):
        trace = build_trace()
        prediction = next(e for e in trace["events"] if e["event_type"] == "assistant_prediction")
        trace["events"].remove(prediction)
        write_start = next(i for i, e in enumerate(trace["events"]) if e.get("action_id") == "write-1" and e["event_type"] == "action_started")
        trace["events"].insert(write_start + 1, prediction)
        self.reindex(trace)
        self.assertEqual(self.grade(trace)["status"], "fail")

    def test_prediction_must_match_exactly_one_added_path_and_no_other_deltas(self):
        for key, value in [
            ("added_paths", [REPORT_PATH, "src/changed.py"]),
            ("modified_paths", ["README.md"]),
            ("deleted_paths", ["old.txt"]),
        ]:
            trace = build_trace()
            prediction = next(e for e in trace["events"] if e["event_type"] == "assistant_prediction")
            prediction["expected_effects"][key] = value
            self.assertEqual(self.grade(trace)["status"], "fail")

    def test_wrong_prediction_path_is_rejected(self):
        trace = build_trace()
        prediction = next(e for e in trace["events"] if e["event_type"] == "assistant_prediction")
        prediction["expected_effects"]["added_paths"] = ["reports/other.md"]
        self.assertEqual(self.grade(trace)["status"], "fail")

    def test_multiple_write_actions_are_rejected(self):
        trace = build_trace()
        write_pair = copy.deepcopy(trace["events"][2:4])
        for event in write_pair:
            event["action_id"] = "write-2"
            event["arguments"]["path"] = "other.md"
            event["event_id"] = "duplicate-" + event["event_type"]
        trace["events"][4:4] = write_pair
        self.reindex(trace)
        self.assertEqual(self.grade(trace)["status"], "fail")

    def test_write_requires_exact_registered_create_file_tool_and_arguments(self):
        for field, value in [("tool_id", "other__create_file")]:
            trace = build_trace()
            for event in trace["events"]:
                if event.get("action_id") == "write-1":
                    event[field] = value
            self.assertEqual(self.grade(trace)["status"], "fail")
        trace = build_trace()
        for event in trace["events"]:
            if event.get("action_id") == "write-1":
                event["arguments"]["branch"] = "main"
        self.assertEqual(self.grade(trace)["status"], "fail")

    def test_failed_write_with_partial_commit_is_rejected(self):
        trace = build_trace()
        event = next(e for e in trace["events"] if e.get("action_id") == "write-1" and e["event_type"] == "action_executed")
        event["actual_tool_result"]["ok"] = False
        self.assertEqual(self.grade(trace)["status"], "fail")

    def test_readback_must_be_successful_exact_report_and_blob(self):
        for mutate in [
            lambda event: event["actual_tool_result"].update(ok=False),
            lambda event: event["actual_tool_result"]["result"].update(sha="f" * 40),
            lambda event: event["actual_tool_result"]["result"].update(content="different text"),
            lambda event: event["arguments"].update(ref="main"),
        ]:
            trace = build_trace()
            readback = next(e for e in trace["events"] if e.get("action_id") == "read-1" and e["event_type"] == "action_executed")
            mutate(readback)
            self.assertEqual(self.grade(trace)["status"], "fail")

    def test_forged_final_artifact_without_readback_is_rejected(self):
        trace = build_trace()
        trace["events"] = [e for e in trace["events"] if e.get("action_id") != "read-1"]
        trace["events"] = [e for e in trace["events"] if e["event_type"] != "artifact_readback"]
        self.reindex(trace)
        self.assertEqual(self.grade(trace)["status"], "fail")

    def test_readback_must_follow_write_completion(self):
        trace = build_trace()
        read_start = next(e for e in trace["events"] if e.get("action_id") == "read-1" and e["event_type"] == "action_started")
        trace["events"].remove(read_start)
        write_done_index = next(i for i, e in enumerate(trace["events"]) if e.get("action_id") == "write-1" and e["event_type"] == "action_executed")
        trace["events"].insert(write_done_index, read_start)
        self.reindex(trace)
        self.assertEqual(self.grade(trace)["status"], "fail")

    def test_missing_compare_or_wrong_base_or_head_is_rejected(self):
        trace = build_trace()
        trace["events"] = [e for e in trace["events"] if e.get("action_id") != "compare-1"]
        self.reindex(trace)
        self.assertEqual(self.grade(trace)["status"], "fail")
        for key, value in [("base", "0" * 40), ("head", "f" * 40)]:
            trace = build_trace()
            event = next(e for e in trace["events"] if e.get("action_id") == "compare-1" and e["event_type"] == "action_executed")
            event["arguments"][key] = value
            event["actual_tool_result"]["result"][key] = value
            start = next(e for e in trace["events"] if e.get("action_id") == "compare-1" and e["event_type"] == "action_started")
            start["arguments"][key] = value
            self.assertEqual(self.grade(trace)["status"], "fail")

    def test_fabricated_actual_effects_without_compare_response_is_rejected(self):
        trace = build_trace()
        trace["events"] = [e for e in trace["events"] if e.get("action_id") != "compare-1"]
        self.reindex(trace)
        self.assertEqual(self.grade(trace)["status"], "fail")

    def test_compare_must_show_exactly_one_added_file_and_one_commit(self):
        trace = build_trace()
        result = next(e for e in trace["events"] if e.get("action_id") == "compare-1" and e["event_type"] == "action_executed")["actual_tool_result"]["result"]
        result["files"].append({"filename": "src/api.py", "status": "modified", "additions": 1, "deletions": 0, "changes": 1})
        self.assertEqual(self.grade(trace)["status"], "fail")
        trace = build_trace()
        result = next(e for e in trace["events"] if e.get("action_id") == "compare-1" and e["event_type"] == "action_executed")["actual_tool_result"]["result"]
        result["ahead_by"] = 2
        result["total_commits"] = 2
        self.assertEqual(self.grade(trace)["status"], "fail")

    def test_compare_observation_must_follow_report_readback(self):
        trace = build_trace()
        compare_start = next(e for e in trace["events"] if e.get("action_id") == "compare-1" and e["event_type"] == "action_started")
        trace["events"].remove(compare_start)
        artifact_index = next(i for i, e in enumerate(trace["events"]) if e["event_type"] == "artifact_readback")
        trace["events"].insert(artifact_index, compare_start)
        self.reindex(trace)
        self.assertEqual(self.grade(trace)["status"], "fail")

    def test_extra_report_path_and_wrong_content_are_rejected(self):
        trace = build_trace()
        result = next(e for e in trace["events"] if e.get("action_id") == "compare-1" and e["event_type"] == "action_executed")["actual_tool_result"]["result"]
        result["files"][0]["filename"] = "reports/other.md"
        self.assertEqual(self.grade(trace)["status"], "fail")
        trace = build_trace(REPORT_CONTENT.replace("Blocked: 1", "Blocked: 0"))
        self.assertEqual(self.grade(trace)["status"], "fail")

    def test_declared_tool_calls_must_match_actual_action_starts(self):
        trace = build_trace()
        trace["usage"]["tool_calls"] = 2
        self.assertEqual(self.grade(trace)["status"], "fail")

    @staticmethod
    def reindex(trace: dict) -> None:
        for index, event in enumerate(trace["events"], 1):
            event["event_index"] = index
            event["event_id"] = f"e{index}"
        trace["usage"]["tool_calls"] = sum(e.get("event_type") == "action_started" for e in trace["events"])
        for event in trace["events"]:
            if event.get("event_type") == "artifact_readback":
                trace["final_artifacts"][0]["source_event_index"] = event["event_index"]


if __name__ == "__main__":
    unittest.main()
