from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from DHI_v1.benchmark.plugin_trace import grade_task
from test_plugin_trace_grader import make_trace


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"
SNAPSHOT_PATH = (
    ROOT
    / "DHI_v1"
    / "benchmark"
    / "fixtures"
    / "plugin_ecology"
    / "external_snapshots"
    / "nodejs_releases_2026-11-03.md"
)
TASK_ID = "ORBIT-A-S02-001"
URL = "https://nodejs.org/en/about/previous-releases"
FETCH_TOOL = "mcp__TinyFish__fetch_content"
SEARCH_TOOL = "mcp__TinyFish__search"


def load_task() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    task = copy.deepcopy(next(item for item in manifest["tasks"] if item["task_id"] == TASK_ID))
    task["task_instance_sha256"] = task["split_metadata"]["task_instance_sha256"]
    return task


def make_s02_trace(
    *,
    fetch_tool: str = FETCH_TOOL,
    fetch_url: str = URL,
    fetch_ok: bool = True,
    content: str | None = None,
) -> dict:
    task = load_task()
    snapshot = SNAPSHOT_PATH.read_text(encoding="utf-8") if content is None else content
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
    trace["provenance"]["executor"] = "study0-s02-nodejs-release-unit-test"

    search_args = {"query": "Node.js official previous releases v27 Alpha v26 LTS"}
    fetch_args = {
        "urls": [fetch_url],
        "format": "markdown",
        "links": False,
        "image_links": False,
        "iframe_links": False,
        "page_metadata": True,
    }
    events = [
        {
            "event_id": "s02-task-start",
            "event_index": 1,
            "event_type": "task_started",
            "timestamp_utc": "2026-11-03T00:00:00Z",
            "task_id": TASK_ID,
            "source_ref": "fixture://s02-task-start",
        },
        {
            "event_id": "s02-prediction",
            "event_index": 2,
            "event_type": "assistant_prediction",
            "timestamp_utc": "2026-11-03T00:00:01Z",
            "task_id": TASK_ID,
            "expected_effects": {
                "added_paths": [],
                "modified_paths": [],
                "deleted_paths": [],
            },
        },
        {
            "event_id": "s02-search-start",
            "event_index": 3,
            "event_type": "action_started",
            "timestamp_utc": "2026-11-03T00:00:02Z",
            "task_id": TASK_ID,
            "action_id": "s02-search",
            "tool_id": SEARCH_TOOL,
            "arguments": copy.deepcopy(search_args),
        },
        {
            "event_id": "s02-search-executed",
            "event_index": 4,
            "event_type": "action_executed",
            "timestamp_utc": "2026-11-03T00:00:03Z",
            "task_id": TASK_ID,
            "action_id": "s02-search",
            "tool_id": SEARCH_TOOL,
            "arguments": copy.deepcopy(search_args),
            "actual_tool_result": {
                "ok": True,
                "result": {
                    "content": f"Official Node.js release page: {URL}",
                    "url": URL,
                },
                "error": None,
                "provider_cost": 0,
            },
        },
        {
            "event_id": "s02-fetch-start",
            "event_index": 5,
            "event_type": "action_started",
            "timestamp_utc": "2026-11-03T00:00:04Z",
            "task_id": TASK_ID,
            "action_id": "s02-fetch",
            "tool_id": fetch_tool,
            "arguments": copy.deepcopy(fetch_args),
        },
        {
            "event_id": "s02-fetch-executed",
            "event_index": 6,
            "event_type": "action_executed",
            "timestamp_utc": "2026-11-03T00:00:05Z",
            "task_id": TASK_ID,
            "action_id": "s02-fetch",
            "tool_id": fetch_tool,
            "arguments": copy.deepcopy(fetch_args),
            # A failed fetch deliberately retains partial content to ensure
            # the grader requires success rather than trusting the body alone.
            "actual_tool_result": {
                "ok": fetch_ok,
                "result": {
                    "content": snapshot,
                    "url": fetch_url,
                },
                "error": None if fetch_ok else "synthetic fetch failure",
                "provider_cost": 0,
            },
        },
        {
            "event_id": "s02-task-close",
            "event_index": 7,
            "event_type": "task_closed",
            "timestamp_utc": "2026-11-03T00:00:06Z",
            "task_id": TASK_ID,
            "closure_status": "success",
        },
    ]
    trace["events"] = events
    trace["usage"] = {"tool_calls": 2, "provider_credits_spent": 0}
    trace["final_answer"] = (
        "Observation date: 2026-11-03. Source: https://nodejs.org/en/about/previous-releases. "
        "Highest major version: v27 (Alpha). LTS versions: v26, v24 and v22. "
        "Production applications should use Active LTS or Maintenance LTS releases."
    )
    return trace


def grade(trace: dict) -> dict:
    return grade_task(load_task(), trace)


class Study0NodeJsReleaseTaskGraderTests(unittest.TestCase):
    def test_s02_001_accepts_pinned_official_release_table(self):
        result = grade(make_s02_trace())
        self.assertEqual(result["status"], "pass", result)

    def test_s02_001_rejects_release_facts_from_search_instead_of_fetch(self):
        trace = make_s02_trace(fetch_tool=SEARCH_TOOL)
        result = grade(trace)
        self.assertNotEqual(result["status"], "pass", result)

    def test_s02_001_rejects_failed_fetch_with_partial_release_content(self):
        result = grade(make_s02_trace(fetch_ok=False))
        self.assertNotEqual(result["status"], "pass", result)

    def test_s02_001_rejects_wrong_source_url(self):
        result = grade(make_s02_trace(fetch_url="https://example.org/releases"))
        self.assertNotEqual(result["status"], "pass", result)

    def test_s02_001_rejects_missing_highest_major_alpha_row(self):
        snapshot = SNAPSHOT_PATH.read_text(encoding="utf-8")
        content = snapshot.replace("| v27 | Oct 29, 2026 | Alpha |", "| v27 | Oct 29, 2026 | LTS |")
        result = grade(make_s02_trace(content=content))
        self.assertEqual(result["status"], "fail", result)

    def test_s02_001_rejects_missing_one_of_the_lts_rows(self):
        snapshot = SNAPSHOT_PATH.read_text(encoding="utf-8")
        content = snapshot.replace("| v24 | May 06, 2025 | LTS |", "| v24 | May 06, 2025 | EOL |")
        result = grade(make_s02_trace(content=content))
        self.assertEqual(result["status"], "fail", result)

    def test_s02_001_rejects_missing_production_guidance(self):
        snapshot = SNAPSHOT_PATH.read_text(encoding="utf-8")
        content = snapshot.replace(
            "The official page states: production applications should use Active LTS or Maintenance LTS releases.",
            "The official page lists release statuses.",
        )
        result = grade(make_s02_trace(content=content))
        self.assertEqual(result["status"], "fail", result)

    def test_s02_001_rejects_missing_page_updated_date(self):
        snapshot = SNAPSHOT_PATH.read_text(encoding="utf-8")
        content = snapshot.replace("- Page published/updated metadata: 2026-10-29", "- Page metadata: unavailable")
        result = grade(make_s02_trace(content=content))
        self.assertEqual(result["status"], "fail", result)


if __name__ == "__main__":
    unittest.main()
