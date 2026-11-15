from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from DHI_v1.benchmark.plugin_trace import grade_task


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"

TASK_ID = "ORBIT-A-S04-002"
REPOSITORY = "Kshitijpalsinghtomar/dhi"
BASE = "04d0e12f48067b3b3a3de3ffe10944b7ef594984"
HEAD = "d3f7ca37a8623ef6e5f5b3ed4e60f88a2a8efb1c"
REPORT_PATH = "DHI_v1/benchmark/fixtures/plugin_ecology/reports/resume-release-review.md"
COMPARE_TOOL = "mcp__GitHub__compare_commits"
READ_ONLY_ARGS = {"repo_full_name": REPOSITORY, "base": BASE, "head": HEAD}
EXPECTED_FILES = [{"path": REPORT_PATH, "status": "added", "changes": 50}]


def load_task() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    task = copy.deepcopy(next(item for item in manifest["tasks"] if item["task_id"] == TASK_ID))
    task["task_instance_sha256"] = task["split_metadata"]["task_instance_sha256"]
    return task


def build_trace(
    *,
    tool_id: str = COMPARE_TOOL,
    arguments: dict | None = None,
    result: dict | None = None,
    ok: bool = True,
    side_effect_class: str = "read_only",
    include_completion: bool = True,
    answer: str | None = None,
    usage_calls: int = 1,
    credits: int = 0,
    extra_actions: list[tuple[str, dict, dict]] | None = None,
) -> dict:
    args = copy.deepcopy(READ_ONLY_ARGS if arguments is None else arguments)
    comparison = copy.deepcopy(result if result is not None else {
        "repository_full_name": REPOSITORY,
        "base": BASE,
        "head": HEAD,
        "status": "ahead",
        "ahead_by": 1,
        "behind_by": 0,
        "total_commits": 1,
        "files": [{
            "filename": REPORT_PATH,
            "status": "added",
            "additions": 50,
            "deletions": 0,
            "changes": 50,
            "previous_filename": None,
        }],
    })
    task = load_task()
    task_id = task["task_id"]
    before = {"README.md": "a" * 64}
    events = [{
        "event_id": "e1", "event_index": 1, "event_type": "task_started",
        "timestamp_utc": "2026-11-03T00:00:00Z", "task_id": task_id,
        "source_ref": "fixture://s04-commit-diff",
    }, {
        "event_id": "e2", "event_index": 2, "event_type": "action_started",
        "timestamp_utc": "2026-11-03T00:00:01Z", "task_id": task_id,
        "action_id": "compare-1", "tool_id": tool_id, "arguments": args,
        "observed_state_before": copy.deepcopy(before),
        "side_effect_class": side_effect_class,
    }]
    if include_completion:
        events.append({
            "event_id": "e3", "event_index": 3, "event_type": "action_executed",
            "timestamp_utc": "2026-11-03T00:00:02Z", "task_id": task_id,
            "action_id": "compare-1", "tool_id": tool_id, "arguments": copy.deepcopy(args),
            "observed_state_before": copy.deepcopy(before),
            "observed_state_after": copy.deepcopy(before),
            "actual_tool_result": {"ok": ok, "result": comparison, "error": None if ok else "compare failed"},
            "actual_effects": {
                "added_paths": [], "modified_paths": [], "deleted_paths": [],
                "changed_paths": [], "unchanged_paths": ["README.md"],
            },
        })
    for extra_tool, extra_args, extra_result in extra_actions or []:
        index = len(events) + 1
        action_id = f"extra-{index}"
        events.append({
            "event_id": f"e{index}", "event_index": index, "event_type": "action_started",
            "timestamp_utc": f"2026-11-03T00:00:{index:02d}Z", "task_id": task_id,
            "action_id": action_id, "tool_id": extra_tool, "arguments": copy.deepcopy(extra_args),
            "observed_state_before": copy.deepcopy(before), "side_effect_class": "read_only",
        })
        events.append({
            "event_id": f"e{index+1}", "event_index": index+1, "event_type": "action_executed",
            "timestamp_utc": f"2026-11-03T00:00:{index+1:02d}Z", "task_id": task_id,
            "action_id": action_id, "tool_id": extra_tool, "arguments": copy.deepcopy(extra_args),
            "observed_state_before": copy.deepcopy(before), "observed_state_after": copy.deepcopy(before),
            "actual_tool_result": {"ok": True, "result": copy.deepcopy(extra_result), "error": None},
            "actual_effects": {
                "added_paths": [], "modified_paths": [], "deleted_paths": [],
                "changed_paths": [], "unchanged_paths": ["README.md"],
            },
        })
    close_index = len(events) + 1
    events.append({
        "event_id": f"e{close_index}", "event_index": close_index, "event_type": "task_closed",
        "timestamp_utc": f"2026-11-03T00:00:{close_index:02d}Z", "task_id": task_id,
        "closure_status": "success",
    })
    return {
        "trace_schema_version": "orbit.plugin-trace.v1",
        "trajectory_id": "s04-commit-diff-readonly",
        "task_id": task_id,
        "task_instance_sha256": task["split_metadata"]["task_instance_sha256"],
        "environment": {
            "environment_id": task["environment"]["environment_id"],
            "version": task["environment"]["version"],
            "state_sha256": task["environment"]["state_sha256"],
        },
        "tool_schema_sha256": task["tool_inventory"]["tool_schema_sha256"],
        "provenance": {
            "evidence_class": "scripted-reference", "executor": "s04-commit-diff-unit-test",
            "recorded_at_utc": "2026-11-03T00:00:00Z",
        },
        "events": events,
        "final_answer": answer if answer is not None else (
            f"{REPORT_PATH} — status: added; 50 line changes. "
            "Used the read-only compare_commits operation; no repository changes were made."
        ),
        "final_artifacts": [],
        "usage": {"tool_calls": usage_calls, "provider_credits_spent": credits},
        "closure": {
            "status": "success", "verified_postconditions": [], "failed_postconditions": [],
            "final_state_sha256": "b" * 64, "closed_at_utc": "2026-11-03T00:00:10Z",
        },
    }


def grade(trace: dict) -> dict:
    return grade_task(load_task(), trace)


class Study0CommitDiffSelectionTaskGraderTests(unittest.TestCase):
    def test_s04_002_accepts_exact_read_only_compare_result(self):
        report = grade(build_trace())
        self.assertEqual(report["status"], "pass", report)

    def test_search_or_fetch_cannot_substitute_for_compare_commits(self):
        for tool in ("mcp__GitHub__fetch_file", "mcp__GitHub__fetch"):
            with self.subTest(tool=tool):
                self.assertNotEqual(grade(build_trace(tool_id=tool))["status"], "pass")

    def test_compare_must_be_successful_even_when_partial_diff_is_present(self):
        self.assertNotEqual(grade(build_trace(ok=False))["status"], "pass")

    def test_compare_requires_exact_repository_and_commit_arguments(self):
        for field, value in [("repo_full_name", "other/repo"), ("base", "0" * 40), ("head", "f" * 40)]:
            with self.subTest(field=field):
                arguments = copy.deepcopy(READ_ONLY_ARGS)
                arguments[field] = value
                self.assertNotEqual(grade(build_trace(arguments=arguments))["status"], "pass")

    def test_mutation_capable_action_is_rejected(self):
        for tool in ("mcp__GitHub__update_file", "mcp__GitHub__create_file"):
            with self.subTest(tool=tool):
                self.assertNotEqual(grade(build_trace(tool_id=tool))["status"], "pass")

    def test_write_action_after_compare_is_rejected(self):
        trace = build_trace(extra_actions=[(
            "mcp__GitHub__update_file",
            {"repository_full_name": REPOSITORY, "path": REPORT_PATH, "branch": "main", "content": "bad"},
            {"commit_sha": "f" * 40},
        )])
        self.assertNotEqual(grade(trace)["status"], "pass")

    def test_unknown_or_write_side_effect_class_is_rejected(self):
        for value in ("unknown", "sandbox_write", "external_write", "destructive"):
            with self.subTest(side_effect_class=value):
                self.assertNotEqual(grade(build_trace(side_effect_class=value))["status"], "pass")

    def test_missing_compare_completion_is_rejected(self):
        self.assertNotEqual(grade(build_trace(include_completion=False))["status"], "pass")

    def test_compare_response_must_match_exact_single_file_diff(self):
        mutations = []
        wrong_path = copy.deepcopy(build_trace())
        wrong_path["events"][2]["actual_tool_result"]["result"]["files"][0]["filename"] = "other.md"
        mutations.append(wrong_path)
        extra_file = copy.deepcopy(build_trace())
        extra_file["events"][2]["actual_tool_result"]["result"]["files"].append(
            {"filename": "README.md", "status": "modified", "changes": 1}
        )
        mutations.append(extra_file)
        wrong_status = copy.deepcopy(build_trace())
        wrong_status["events"][2]["actual_tool_result"]["result"]["files"][0]["status"] = "modified"
        mutations.append(wrong_status)
        wrong_count = copy.deepcopy(build_trace())
        wrong_count["events"][2]["actual_tool_result"]["result"]["files"][0]["changes"] = 49
        mutations.append(wrong_count)
        for trace in mutations:
            with self.subTest(result=trace["events"][2]["actual_tool_result"]["result"]):
                self.assertNotEqual(grade(trace)["status"], "pass")

    def test_compare_response_must_match_exact_base_and_head(self):
        for key in ("base", "head"):
            result = copy.deepcopy(build_trace()["events"][2]["actual_tool_result"]["result"])
            result[key] = "0" * 40
            self.assertNotEqual(grade(build_trace(result=result))["status"], "pass")

    def test_final_answer_must_report_exact_path_and_added_status(self):
        for answer in (
            "Changed one file.",
            f"{REPORT_PATH} — status: modified; 50 changes.",
            "other.md — added; 50 changes.",
        ):
            with self.subTest(answer=answer):
                self.assertNotEqual(grade(build_trace(answer=answer))["status"], "pass")

    def test_declared_tool_calls_and_provider_credits_must_match_read_only_action(self):
        self.assertNotEqual(grade(build_trace(usage_calls=2))["status"], "pass")
        self.assertNotEqual(grade(build_trace(credits=1))["status"], "pass")

    def test_fabricated_diff_text_without_compare_observation_is_rejected(self):
        trace = build_trace(include_completion=False)
        trace["final_answer"] = f"{REPORT_PATH} — added, 50 changes."
        self.assertNotEqual(grade(trace)["status"], "pass")


if __name__ == "__main__":
    unittest.main()
