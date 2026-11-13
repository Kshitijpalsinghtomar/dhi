from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from DHI_v1.benchmark.plugin_trace import grade_task


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"

TASK_ID = "ORBIT-A-S06-002"
REPOSITORY = "Kshitijpalsinghtomar/dhi"
BASE = "d0df1950a0f1d23c8bd6347619ae9a3a36d771fa"
BRANCH = "orbit/s06-runtime-report"
NODE_PATH = "DHI_v1/benchmark/fixtures/plugin_ecology/external_snapshots/nodejs_releases_2026-11-03.md"
PYTHON_PATH = "DHI_v1/benchmark/fixtures/plugin_ecology/external_snapshots/python_releases_2026-11-03.md"
REPORT_PATH = "DHI_v1/benchmark/fixtures/plugin_ecology/reports/runtime-release-state.md"

NODE_BLOB = "2316a22af4cb0f9dd582bd52d33d942491f1dba1"
PYTHON_BLOB = "39a4a2d2bc222f06327e9630a0613c09ae5e4faf"
WRITE_COMMIT = "d" * 40

NODE_CONTENT = """# Node.js official release table snapshot

- Source: https://nodejs.org/en/about/previous-releases
- Retrieved through: TinyFish search + fetch_content
- Page title: Node.js — Node.js Releases
- Page published/updated metadata: 2026-10-29
- Observation date: 2026-11-03
- Use: historical, reproducible currentness check for benchmark task ORBIT-A-S02-001.

## Release rows captured

| Major | First released | Status |
|---|---|---|
| v27 | Oct 29, 2026 | Alpha |
| v26 | May 05, 2026 | LTS |
| v25 | Oct 15, 2025 | EOL |
| v24 | May 06, 2025 | LTS |
| v23 | Oct 16, 2024 | EOL |
| v22 | Apr 24, 2024 | LTS |

The official page states: production applications should use Active LTS or Maintenance LTS releases. It distinguishes Node.js v27 (Alpha) from the current LTS lines v26, v24 and v22 at this observation date.

This is a date-pinned reference snapshot.
"""

PYTHON_CONTENT = """# Python official release snapshot

- Source: https://www.python.org/downloads/
- Retrieved through: TinyFish search + fetch_content
- Observation date: 2026-11-03
- Use: historical, reproducible currentness check for ORBIT-A-S02-002.

## Active Python branches at observation time

| Version | Maintenance status | First released | End of support |
|---|---|---|---|
| 3.16 | pre-release | 2027-10-06 (planned) | 2032-10 |
| 3.15 | bugfix | 2026-10-09 | 2031-10 |
| 3.14 | bugfix | 2025-10-07 | 2030-10 |
| 3.13 | security | 2024-10-07 | 2029-10 |
| 3.12 | security | 2023-10-02 | 2028-10 |
| 3.11 | security | 2022-10-24 | 2027-10 |
| 3.10 | end-of-life | 2021-10-04 | 2026-10-01 |

## Latest listed stable releases

- Python 3.15.2 — Oct. 25, 2026
- Python 3.14.10 — Oct. 25, 2026
- Python 3.13.18 — Oct. 25, 2026
- Python 3.12.16 — Oct. 25, 2026
- Python 3.11.18 — Oct. 25, 2026

The page lists Python 3.16 as a pre-release planned for 2027-10-06, not as the current stable release. Python 3.10 is end-of-life as of this observation date.
"""

REPORT_CONTENT = """# Cross-runtime release-state comparison

Observation date: 2026-11-03

## Sources
- Node.js: https://nodejs.org/en/about/previous-releases
- Python: https://www.python.org/downloads/

## Node.js
Highest major version: Node.js v27 — Alpha (first released Oct 29, 2026).
Current Node.js LTS lines: v26, v24, and v22.
Production guidance: Active LTS or Maintenance LTS. The higher-numbered v27 Alpha release is not the production recommendation.

## Python
Latest stable release: Python 3.15.2 (Oct. 25, 2026).
Python 3.16 is a planned pre-release for 2027-10-06, not a stable release.
Python branch maintenance: 3.15 and 3.14 — bugfix; 3.13, 3.12 and 3.11 — security; 3.10 — end-of-life as of 2026-10-01.

## Interpretation
The highest-numbered or planned pre-release is not necessarily stable or production-ready. For Node.js, use Active LTS or Maintenance LTS rather than Alpha; for Python, 3.15.2 is the latest stable release and the planned 3.16 pre-release must not be presented as stable.
"""

REQUIRED_REPORT_PHRASES = [
    "Observation date: 2026-11-03",
    "Node.js v27 — Alpha",
    "Current Node.js LTS lines: v26, v24, and v22",
    "Production guidance: Active LTS or Maintenance LTS",
    "Latest stable release: Python 3.15.2",
    "Python 3.16 is a planned pre-release for 2027-10-06, not a stable release",
    "3.15 and 3.14 — bugfix",
    "3.13, 3.12 and 3.11 — security",
    "3.10 — end-of-life as of 2026-10-01",
]
REQUIRED_ANSWER_PHRASES = [
    REPORT_PATH,
    "created",
    "fetched back",
    "one added path",
]


def git_blob_sha(value: str) -> str:
    data = value.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def sha(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def load_task() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    task = copy.deepcopy(next(item for item in manifest["tasks"] if item["task_id"] == TASK_ID))
    task["task_instance_sha256"] = task["split_metadata"]["task_instance_sha256"]
    return task


def condition() -> dict:
    return {
        "type": "github_cross_source_report_closure",
        "repository_full_name": REPOSITORY,
        "branch": BRANCH,
        "base_commit": BASE,
        "source_files": [
            {"path": NODE_PATH, "blob_sha": NODE_BLOB, "required_values": ["v27", "Alpha", "v26", "v24", "v22", "Active LTS", "Maintenance LTS"]},
            {"path": PYTHON_PATH, "blob_sha": PYTHON_BLOB, "required_values": ["3.15.2", "3.16", "pre-release", "bugfix", "security", "3.10", "end-of-life"]},
        ],
        "report_path": REPORT_PATH,
        "required_report_phrases": REQUIRED_REPORT_PHRASES,
        "forbidden_report_phrases": [
            "recommend v27 alpha for production",
            "python 3.16 is the latest stable release",
            "python 3.10 remains supported",
        ],
        "required_answer_phrases": REQUIRED_ANSWER_PHRASES,
        "min_tool_calls": 5,
        "max_tool_calls": 9,
    }


def append_action(
    events: list[dict],
    tool_id: str,
    action_id: str,
    arguments: dict,
    result: dict,
    *,
    before: dict,
    after: dict | None = None,
    ok: bool = True,
    side_effect_class: str = "read_only",
    effects: dict | None = None,
) -> None:
    index = len(events) + 1
    events.append({
        "event_id": f"e{index}", "event_index": index, "event_type": "action_started",
        "timestamp_utc": f"2026-11-03T00:00:{index:02d}Z", "task_id": TASK_ID,
        "action_id": action_id, "tool_id": tool_id, "arguments": copy.deepcopy(arguments),
        "observed_state_before": copy.deepcopy(before),
        "side_effect_class": side_effect_class,
    })
    index = len(events) + 1
    after_state = copy.deepcopy(after if after is not None else before)
    events.append({
        "event_id": f"e{index}", "event_index": index, "event_type": "action_executed",
        "timestamp_utc": f"2026-11-03T00:00:{index:02d}Z", "task_id": TASK_ID,
        "action_id": action_id, "tool_id": tool_id, "arguments": copy.deepcopy(arguments),
        "observed_state_before": copy.deepcopy(before), "observed_state_after": after_state,
        "actual_tool_result": {"ok": ok, "result": copy.deepcopy(result), "error": None if ok else "synthetic failure"},
        "actual_effects": copy.deepcopy(effects or {
            "added_paths": [], "modified_paths": [], "deleted_paths": [],
            "changed_paths": [], "unchanged_paths": sorted(before),
        }),
    })


def build_trace(
    *,
    report: str = REPORT_CONTENT,
    node: str = NODE_CONTENT,
    python: str = PYTHON_CONTENT,
    node_blob: str = NODE_BLOB,
    python_blob: str = PYTHON_BLOB,
    write_ok: bool = True,
    readback: str | None = None,
    readback_ok: bool = True,
    compare_result: dict | None = None,
    compare_ok: bool = True,
) -> dict:
    task = load_task()
    before = {"README.md": "a" * 64}
    after = {**before, REPORT_PATH: sha(report)}
    events = [{
        "event_id": "e1", "event_index": 1, "event_type": "task_started",
        "timestamp_utc": "2026-11-03T00:00:00Z", "task_id": TASK_ID,
        "source_ref": "fixture://s06-cross-runtime",
    }]
    node_args = {"repository_full_name": REPOSITORY, "path": NODE_PATH, "ref": BASE}
    python_args = {"repository_full_name": REPOSITORY, "path": PYTHON_PATH, "ref": BASE}
    append_action(
        events, "mcp__GitHub__fetch_file", "read-node", node_args,
        {"content": node, "sha": node_blob, "display_url": f"https://github.com/{REPOSITORY}/blob/{BASE}/{NODE_PATH}"},
        before=before,
    )
    append_action(
        events, "mcp__GitHub__fetch_file", "read-python", python_args,
        {"content": python, "sha": python_blob, "display_url": f"https://github.com/{REPOSITORY}/blob/{BASE}/{PYTHON_PATH}"},
        before=before,
    )
    write_args = {
        "repository_full_name": REPOSITORY,
        "path": REPORT_PATH,
        "content": report,
        "message": "test: add cross-runtime release-state report",
        "branch": BRANCH,
    }
    append_action(
        events, "mcp__GitHub__create_file", "write-report", write_args,
        {"commit_sha": WRITE_COMMIT}, before=before, after=after,
        ok=write_ok, side_effect_class="sandbox_write",
        effects={
            "added_paths": [REPORT_PATH], "modified_paths": [], "deleted_paths": [],
            "changed_paths": [REPORT_PATH], "unchanged_paths": ["README.md"],
        },
    )
    read_args = {"repository_full_name": REPOSITORY, "path": REPORT_PATH, "ref": BRANCH}
    returned_report = report if readback is None else readback
    append_action(
        events, "mcp__GitHub__fetch_file", "read-report", read_args,
        {"content": returned_report, "sha": git_blob_sha(returned_report),
         "display_url": f"https://github.com/{REPOSITORY}/blob/{BRANCH}/{REPORT_PATH}"},
        before=after, ok=readback_ok,
    )
    compare_args = {"repo_full_name": REPOSITORY, "base": BASE, "head": WRITE_COMMIT}
    compare_data = compare_result if compare_result is not None else {
        "repository_full_name": REPOSITORY, "base": BASE, "head": WRITE_COMMIT,
        "status": "ahead", "ahead_by": 1, "behind_by": 0, "total_commits": 1,
        "files": [{
            "filename": REPORT_PATH, "status": "added",
            "additions": len(report.splitlines()), "deletions": 0, "changes": len(report.splitlines()),
        }],
    }
    append_action(
        events, "mcp__GitHub__compare_commits", "compare-report", compare_args,
        compare_data, before=after, ok=compare_ok,
    )
    readback_event_index = len(events) + 1
    events.append({
        "event_id": f"e{readback_event_index}", "event_index": readback_event_index,
        "event_type": "artifact_readback", "timestamp_utc": "2026-11-03T00:00:30Z",
        "task_id": TASK_ID,
        "artifact_readback": {
            "path": REPORT_PATH, "repository_full_name": REPOSITORY, "ref": BRANCH,
            "status": "verified", "source_action_id": "write-report",
            "sha256": sha(returned_report), "blob_sha": git_blob_sha(returned_report),
            "source_ref": f"https://github.com/{REPOSITORY}/blob/{BRANCH}/{REPORT_PATH}",
        },
    })
    closed_index = len(events) + 1
    events.append({
        "event_id": f"e{closed_index}", "event_index": closed_index,
        "event_type": "task_closed", "timestamp_utc": "2026-11-03T00:00:40Z",
        "task_id": TASK_ID, "closure_status": "success",
    })
    return {
        "trace_schema_version": "orbit.plugin-trace.v1",
        "trajectory_id": "s06-cross-runtime-report",
        "task_id": TASK_ID,
        "task_instance_sha256": task["split_metadata"]["task_instance_sha256"],
        "environment": {
            "environment_id": task["environment"]["environment_id"],
            "version": task["environment"]["version"],
            "state_sha256": task["environment"]["state_sha256"],
        },
        "tool_schema_sha256": task["tool_inventory"]["tool_schema_sha256"],
        "provenance": {"evidence_class": "scripted-reference", "executor": "s06-cross-runtime-tests",
                       "recorded_at_utc": "2026-11-03T00:00:00Z"},
        "events": events,
        "final_answer": (
            f"Created {REPORT_PATH}, fetched back the same report, and verified a branch diff with one added path."
        ),
        "final_artifacts": [{
            "path": REPORT_PATH, "content": returned_report, "sha256": sha(returned_report),
            "blob_sha": git_blob_sha(returned_report), "status": "read",
            "source_event_index": readback_event_index,
            "source_ref": f"https://github.com/{REPOSITORY}/blob/{BRANCH}/{REPORT_PATH}",
        }],
        "usage": {"tool_calls": 5, "provider_credits_spent": 0},
        "closure": {"status": "success", "verified_postconditions": [],
                    "failed_postconditions": [], "final_state_sha256": "e" * 64,
                    "closed_at_utc": "2026-11-03T00:00:40Z"},
    }


def grade(trace: dict) -> dict:
    task = load_task()
    task["postconditions"] = [{
        "verifier_id": "cross_source_report",
        "condition": condition(),
        "expected_evidence": "Two pinned sources; one report write/readback; exact branch diff; no other changes.",
        "failure_if_unmet": True,
    }]
    return grade_task(task, trace)


class Study0CrossRuntimeReleaseReportTests(unittest.TestCase):
    def test_positive_report_requires_both_pinned_sources_and_full_write_readback_diff_chain(self):
        result = grade(build_trace())
        self.assertEqual(result["status"], "pass", result)

    def test_missing_node_or_python_source_is_rejected(self):
        for action_id in ("read-node", "read-python"):
            trace = build_trace()
            trace["events"] = [e for e in trace["events"] if e.get("action_id") != action_id]
            self.reindex(trace)
            self.assertNotEqual(grade(trace)["status"], "pass")

    def test_source_reads_must_use_exact_pinned_repository_paths_and_base_ref(self):
        trace = build_trace()
        event = next(e for e in trace["events"] if e.get("action_id") == "read-node" and e["event_type"] == "action_started")
        event["arguments"]["ref"] = "main"
        self.assertNotEqual(grade(trace)["status"], "pass")

    def test_source_blob_sha_and_content_must_match_the_pinned_snapshot(self):
        self.assertNotEqual(grade(build_trace(node_blob="0" * 40))["status"], "pass")
        altered = NODE_CONTENT.replace("v27 | Oct 29, 2026 | Alpha", "v27 | Oct 29, 2026 | LTS")
        self.assertNotEqual(grade(build_trace(node=altered))["status"], "pass")

    def test_failed_or_wrong_tool_source_read_is_rejected(self):
        trace = build_trace()
        event = next(e for e in trace["events"] if e.get("action_id") == "read-node" and e["event_type"] == "action_executed")
        event["actual_tool_result"]["ok"] = False
        self.assertNotEqual(grade(trace)["status"], "pass")
        trace = build_trace()
        for event in trace["events"]:
            if event.get("action_id") == "read-python":
                event["tool_id"] = "mcp__GitHub__create_file"
        self.assertNotEqual(grade(trace)["status"], "pass")

    def test_report_write_must_follow_both_source_reads(self):
        trace = build_trace()
        write_start = next(e for e in trace["events"] if e.get("action_id") == "write-report" and e["event_type"] == "action_started")
        trace["events"].remove(write_start)
        trace["events"].insert(1, write_start)
        self.reindex(trace)
        self.assertNotEqual(grade(trace)["status"], "pass")

    def test_report_write_must_target_exact_path_and_dedicated_branch(self):
        for field, value in [("path", "README.md"), ("branch", "main")]:
            trace = build_trace()
            event = next(e for e in trace["events"] if e.get("action_id") == "write-report" and e["event_type"] == "action_started")
            event["arguments"][field] = value
            self.assertNotEqual(grade(trace)["status"], "pass")

    def test_failed_report_write_is_rejected_even_with_readback_data(self):
        self.assertNotEqual(grade(build_trace(write_ok=False))["status"], "pass")

    def test_report_must_contain_all_cross_runtime_facts_and_not_misstate_channels(self):
        for altered in [
            REPORT_CONTENT.replace("Node.js v27 — Alpha", "Node.js v27 — LTS"),
            REPORT_CONTENT.replace("Latest stable release: Python 3.15.2", "Latest stable release: Python 3.16"),
            REPORT_CONTENT.replace("3.10 — end-of-life as of 2026-10-01", "3.10 — security"),
        ]:
            self.assertNotEqual(grade(build_trace(report=altered))["status"], "pass")

    def test_report_readback_must_follow_write_and_match_content_and_blob(self):
        self.assertNotEqual(grade(build_trace(readback="different report body"))["status"], "pass")
        trace = build_trace()
        event = next(e for e in trace["events"] if e.get("action_id") == "read-report" and e["event_type"] == "action_executed")
        event["actual_tool_result"]["ok"] = False
        self.assertNotEqual(grade(trace)["status"], "pass")

    def test_artifact_must_be_linked_to_successful_report_readback(self):
        trace = build_trace()
        trace["final_artifacts"][0]["blob_sha"] = "0" * 40
        self.assertNotEqual(grade(trace)["status"], "pass")
        trace = build_trace()
        trace["final_artifacts"][0]["source_event_index"] = 5
        self.assertNotEqual(grade(trace)["status"], "pass")

    def test_compare_must_use_exact_pinned_base_and_actual_write_commit(self):
        trace = build_trace()
        event = next(e for e in trace["events"] if e.get("action_id") == "compare-report" and e["event_type"] == "action_started")
        event["arguments"]["base"] = "0" * 40
        self.assertNotEqual(grade(trace)["status"], "pass")

    def test_compare_must_be_successful_and_show_only_one_added_report_path(self):
        self.assertNotEqual(grade(build_trace(compare_ok=False))["status"], "pass")
        result = copy.deepcopy(build_trace()["events"][9]["actual_tool_result"]["result"])
        result["files"].append({"filename": "README.md", "status": "modified", "additions": 1, "deletions": 0, "changes": 1})
        self.assertNotEqual(grade(build_trace(compare_result=result))["status"], "pass")

    def test_wrong_compare_path_or_status_or_count_is_rejected(self):
        for field, value in [("filename", "other.md"), ("status", "modified"), ("changes", 1)]:
            trace = build_trace()
            compare = next(e for e in trace["events"] if e.get("action_id") == "compare-report" and e["event_type"] == "action_executed")
            compare["actual_tool_result"]["result"]["files"][0][field] = value
            self.assertNotEqual(grade(trace)["status"], "pass")

    def test_mutation_tool_or_extra_action_is_rejected(self):
        trace = build_trace()
        event = next(e for e in trace["events"] if e.get("action_id") == "read-node" and e["event_type"] == "action_started")
        event["tool_id"] = "mcp__GitHub__update_file"
        self.assertNotEqual(grade(trace)["status"], "pass")

    def test_usage_must_match_five_actions_with_zero_provider_credits(self):
        trace = build_trace()
        trace["usage"]["tool_calls"] = 4
        self.assertNotEqual(grade(trace)["status"], "pass")
        trace = build_trace()
        trace["usage"]["provider_credits_spent"] = 1
        self.assertNotEqual(grade(trace)["status"], "pass")

    @staticmethod
    def reindex(trace: dict) -> None:
        for index, event in enumerate(trace["events"], 1):
            event["event_index"] = index
            event["event_id"] = f"e{index}"


if __name__ == "__main__":
    unittest.main()
