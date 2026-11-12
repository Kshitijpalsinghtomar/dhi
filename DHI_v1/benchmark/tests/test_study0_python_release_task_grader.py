from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from DHI_v1.benchmark.plugin_trace import grade_task


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"
SNAPSHOT_PATH = ROOT / "DHI_v1" / "benchmark" / "fixtures" / "plugin_ecology" / "external_snapshots" / "python_releases_2026-11-03.md"

TASK_ID = "ORBIT-A-S02-002"
URL = "https://www.python.org/downloads/"
FETCH_TOOL = "mcp__TinyFish__fetch_content"
SEARCH_TOOL = "mcp__TinyFish__search"

SNAPSHOT = """# Python official release snapshot

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

The page lists Python 3.16 as a pre-release planned for 2027-10-06, not as the current stable release. Python 3.10 is end-of-life as of this observation date. A future currentness benchmark must fetch a fresh page rather than reuse this historical snapshot.
"""


def load_task() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    task = copy.deepcopy(next(item for item in manifest["tasks"] if item["task_id"] == TASK_ID))
    task["task_instance_sha256"] = task["split_metadata"]["task_instance_sha256"]
    return task


def make_trace(
    *,
    fetch_tool: str = FETCH_TOOL,
    fetch_url: str = URL,
    fetch_ok: bool = True,
    fetch_content: str = SNAPSHOT,
    search_content: str = "Official Python downloads page: https://www.python.org/downloads/",
    fetch_urls: list[str] | None = None,
    answer: str | None = None,
) -> dict:
    task = load_task()
    search_args = {"query": "official Python downloads latest stable pre-release branch status " + URL}
    fetch_args = {
        "urls": list(fetch_urls) if fetch_urls is not None else [fetch_url],
        "format": "markdown",
        "links": False,
        "image_links": False,
        "iframe_links": False,
        "page_metadata": True,
    }
    events = [{
        "event_id": "s02-task-start", "event_index": 1, "event_type": "task_started",
        "timestamp_utc": "2026-11-03T00:00:00Z", "task_id": TASK_ID,
        "source_ref": "fixture://s02-python-release",
    }, {
        "event_id": "s02-search-start", "event_index": 2, "event_type": "action_started",
        "timestamp_utc": "2026-11-03T00:00:01Z", "task_id": TASK_ID,
        "action_id": "s02-search", "tool_id": SEARCH_TOOL, "arguments": search_args,
    }, {
        "event_id": "s02-search-done", "event_index": 3, "event_type": "action_executed",
        "timestamp_utc": "2026-11-03T00:00:02Z", "task_id": TASK_ID,
        "action_id": "s02-search", "tool_id": SEARCH_TOOL, "arguments": search_args,
        "actual_tool_result": {"ok": True, "result": {"content": search_content, "url": URL},
                               "error": None, "provider_cost": 0},
    }, {
        "event_id": "s02-fetch-start", "event_index": 4, "event_type": "action_started",
        "timestamp_utc": "2026-11-03T00:00:03Z", "task_id": TASK_ID,
        "action_id": "s02-fetch", "tool_id": fetch_tool, "arguments": fetch_args,
    }, {
        "event_id": "s02-fetch-done", "event_index": 5, "event_type": "action_executed",
        "timestamp_utc": "2026-11-03T00:00:04Z", "task_id": TASK_ID,
        "action_id": "s02-fetch", "tool_id": fetch_tool, "arguments": fetch_args,
        "actual_tool_result": {
            "ok": fetch_ok, "result": {"content": fetch_content, "url": fetch_url},
            "error": None if fetch_ok else "synthetic fetch failure", "provider_cost": 0,
        },
    }, {
        "event_id": "s02-close", "event_index": 6, "event_type": "task_closed",
        "timestamp_utc": "2026-11-03T00:00:05Z", "task_id": TASK_ID,
        "closure_status": "success",
    }]
    return {
        "trace_schema_version": "orbit.plugin-trace.v1",
        "trajectory_id": "s02-python-release-test",
        "task_id": TASK_ID,
        "task_instance_sha256": task["task_instance_sha256"],
        "environment": {
            "environment_id": task["environment"]["environment_id"],
            "version": task["environment"]["version"],
            "state_sha256": task["environment"]["state_sha256"],
        },
        "tool_schema_sha256": task["tool_inventory"]["tool_schema_sha256"],
        "provenance": {"evidence_class": "scripted-reference", "executor": "s02-python-release-tests",
                       "recorded_at_utc": "2026-11-03T00:00:00Z"},
        "events": events,
        "final_answer": answer if answer is not None else (
            "Observation date: 2026-11-03. Official source: https://www.python.org/downloads/. "
            "Latest stable release: Python 3.15.2. Python 3.16 is a planned pre-release for 2027-10-06, not a stable release. "
            "Maintenance: Python 3.15 and 3.14 are bugfix; 3.13, 3.12 and 3.11 are security; "
            "Python 3.10 is end-of-life since 2026-10-01."
        ),
        "final_artifacts": [],
        "usage": {"tool_calls": 2, "provider_credits_spent": 0},
        "closure": {"status": "success", "verified_postconditions": [], "failed_postconditions": [],
                    "final_state_sha256": "d" * 64, "closed_at_utc": "2026-11-03T00:00:05Z"},
    }


def grade(trace: dict) -> dict:
    return grade_task(load_task(), trace)


class Study0PythonReleaseTaskGraderTests(unittest.TestCase):
    def test_s02_002_accepts_pinned_official_release_snapshot(self):
        result = grade(make_trace())
        self.assertEqual(result["status"], "pass", result)

    def test_release_facts_from_search_without_fetch_are_rejected(self):
        trace = make_trace(search_content=SNAPSHOT)
        trace["events"] = [e for e in trace["events"] if not (
            e.get("action_id") == "s02-fetch"
        )]
        trace["usage"]["tool_calls"] = 1
        result = grade(trace)
        self.assertNotEqual(result["status"], "pass", result)

    def test_search_observation_cannot_substitute_for_exact_registered_fetch(self):
        trace = make_trace(fetch_tool=SEARCH_TOOL, search_content=SNAPSHOT)
        result = grade(trace)
        self.assertNotEqual(result["status"], "pass", result)

    def test_failed_fetch_with_partial_python_content_is_rejected(self):
        result = grade(make_trace(fetch_ok=False))
        self.assertNotEqual(result["status"], "pass", result)

    def test_fetch_must_use_only_the_exact_official_url(self):
        trace = make_trace(fetch_urls=[URL, "https://example.org/python"])
        result = grade(trace)
        self.assertNotEqual(result["status"], "pass", result)

    def test_fetch_must_not_accept_untrusted_mirror(self):
        result = grade(make_trace(fetch_url="https://example.org/python"))
        self.assertNotEqual(result["status"], "pass", result)

    def test_missing_observation_date_in_source_is_rejected(self):
        content = SNAPSHOT.replace("- Observation date: 2026-11-03", "- Observation date: unavailable")
        result = grade(make_trace(fetch_content=content))
        self.assertEqual(result["status"], "fail", result)

    def test_missing_exact_branch_row_is_rejected(self):
        content = SNAPSHOT.replace("| 3.15 | bugfix | 2026-10-09 | 2031-10 |",
                                   "| 3.15 | security | 2026-10-09 | 2031-10 |")
        result = grade(make_trace(fetch_content=content))
        self.assertEqual(result["status"], "fail", result)

    def test_latest_stable_release_must_be_exactly_3152(self):
        content = SNAPSHOT.replace("Python 3.15.2 — Oct. 25, 2026", "Python 3.15.1 — Oct. 25, 2026")
        result = grade(make_trace(fetch_content=content))
        self.assertEqual(result["status"], "fail", result)

    def test_final_answer_must_include_observation_date_and_official_url(self):
        answer = make_trace().get("final_answer")
        answer = answer.replace("Observation date: 2026-11-03. ", "")
        answer = answer.replace("https://www.python.org/downloads/", "https://example.org/python")
        self.assertNotEqual(grade(make_trace(answer=answer))["status"], "pass")

    def test_final_answer_must_not_promote_316_prerelease_to_stable(self):
        answer = make_trace().get("final_answer") + " Python 3.16 is the latest stable release."
        self.assertNotEqual(grade(make_trace(answer=answer))["status"], "pass")

    def test_final_answer_must_state_python310_eol_explicitly(self):
        answer = make_trace().get("final_answer").replace(
            "Python 3.10 is end-of-life since 2026-10-01.",
            "Python 3.10 remains supported."
        )
        self.assertNotEqual(grade(make_trace(answer=answer))["status"], "pass")


if __name__ == "__main__":
    unittest.main()
