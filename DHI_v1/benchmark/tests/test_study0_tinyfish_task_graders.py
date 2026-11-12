from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from DHI_v1.benchmark.plugin_trace import grade_task
from test_plugin_trace_grader import make_trace


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"
TASK_ID = "ORBIT-A-S05-002"
MAIN_URL = "https://www.python.org/downloads/"
SOURCE_URL = "https://www.python.org/downloads/source/"
TOOL_ID = "mcp__TinyFish__fetch_content"
SNAPSHOT_PATH = (
    ROOT
    / "DHI_v1"
    / "benchmark"
    / "fixtures"
    / "plugin_ecology"
    / "external_snapshots"
    / "python_releases_2026-11-03.md"
)


def load_task() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    task = copy.deepcopy(next(item for item in manifest["tasks"] if item["task_id"] == TASK_ID))
    task["task_instance_sha256"] = task["split_metadata"]["task_instance_sha256"]
    return task


def make_s05_002_trace(
    task: dict,
    *,
    tool_id: str = TOOL_ID,
    ok: bool = True,
    urls: list[str] | None = None,
    result_override: dict | None = None,
) -> dict:
    main_url = MAIN_URL
    source_url = SOURCE_URL
    requested_urls = list(urls) if urls is not None else [main_url, source_url]
    snapshot = SNAPSHOT_PATH.read_text(encoding="utf-8")
    result = result_override if result_override is not None else {
        "results": [
            {"url": main_url, "content": snapshot},
            {"url": source_url, "content": "Python source distribution download information."},
        ]
    }
    arguments = {
        "urls": requested_urls,
        "format": "markdown",
        "links": False,
        "image_links": False,
        "iframe_links": False,
        "page_metadata": False,
    }

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
    trace["provenance"]["executor"] = "study0-s05-tinyfish-multi-url-unit-test"

    for event in trace["events"]:
        event["task_id"] = TASK_ID
    for event in trace["events"][2:4]:
        event["tool_id"] = tool_id
        event["action_id"] = "fetch-python-release-pages"
        event["arguments"] = copy.deepcopy(arguments)

    trace["events"][3]["actual_tool_result"] = {
        "ok": ok,
        "result": result,
        "error": None if ok else "synthetic fetch failure",
        "provider_cost": 0,
    }
    trace["usage"] = {"tool_calls": 1, "provider_credits_spent": 0}
    trace["final_answer"] = (
        "Historical 2026-11-03 snapshot: Python 3.15.2 was the latest listed stable "
        "release; Python 3.16 was a planned pre-release."
    )
    return trace


class Study0TinyFishTaskGraderTests(unittest.TestCase):
    def test_s05_002_accepts_successful_exact_two_url_fetch_and_pinned_facts(self):
        task = load_task()
        trace = make_s05_002_trace(task)
        result = grade_task(task, trace)
        self.assertEqual(result["status"], "pass", result)
        self.assertTrue(all(item["status"] == "pass" for item in result["results"]))

    def test_s05_002_rejects_failed_fetch_even_when_arguments_match(self):
        task = load_task()
        result = grade_task(task, make_s05_002_trace(task, ok=False))
        self.assertEqual(result["status"], "fail", result)

    def test_s05_002_rejects_extra_url_in_batch(self):
        task = load_task()
        trace = make_s05_002_trace(task, urls=[MAIN_URL, SOURCE_URL, "https://example.org/"])
        result = grade_task(task, trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_002_rejects_omitted_required_boolean_argument(self):
        task = load_task()
        trace = make_s05_002_trace(task)
        for event in trace["events"][2:4]:
            event["arguments"].pop("page_metadata")
        result = grade_task(task, trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_002_rejects_provider_credit_spend(self):
        task = load_task()
        trace = make_s05_002_trace(task)
        trace["usage"]["provider_credits_spent"] = 1
        trace["events"][3]["actual_tool_result"]["provider_cost"] = 1
        result = grade_task(task, trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_002_rejects_wrong_tool_even_when_request_and_response_look_valid(self):
        task = load_task()
        result = grade_task(task, make_s05_002_trace(task, tool_id="mcp__GitHub__fetch"))
        self.assertEqual(result["status"], "fail", result)

    def test_s05_002_rejects_response_missing_second_page_source(self):
        task = load_task()
        trace = make_s05_002_trace(
            task,
            result_override={
                "results": [
                    {
                        "url": MAIN_URL,
                        "content": SNAPSHOT_PATH.read_text(encoding="utf-8"),
                    }
                ]
            },
        )
        result = grade_task(task, trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_002_rejects_response_missing_pinned_stable_release_fact(self):
        task = load_task()
        trace = make_s05_002_trace(task)
        trace["events"][3]["actual_tool_result"]["result"]["results"][0]["content"] = (
            trace["events"][3]["actual_tool_result"]["result"]["results"][0]["content"]
            .replace("Python 3.15.2", "Python 3.15.1")
        )
        result = grade_task(task, trace)
        self.assertEqual(result["status"], "fail", result)


if __name__ == "__main__":
    unittest.main()
