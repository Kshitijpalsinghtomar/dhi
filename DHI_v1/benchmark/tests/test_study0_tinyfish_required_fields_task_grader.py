from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from DHI_v1.benchmark.plugin_trace import grade_task
from test_plugin_trace_grader import make_task, make_trace


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"
SNAPSHOT_PATH = (
    ROOT
    / "DHI_v1"
    / "benchmark"
    / "fixtures"
    / "plugin_ecology"
    / "external_snapshots"
    / "go_releases_2026-11-03.md"
)
TASK_ID = "ORBIT-A-S05-004"
TOOL_ID = "mcp__TinyFish__fetch_content"
URL = "https://go.dev/doc/devel/release"
REQUIRED_FIELDS = [
    "urls",
    "format",
    "links",
    "image_links",
    "iframe_links",
    "page_metadata",
]


def load_task() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return copy.deepcopy(next(item for item in manifest["tasks"] if item["task_id"] == TASK_ID))


def make_s05_004_trace(*, tool_id: str = TOOL_ID, ok: bool = True) -> dict:
    snapshot = SNAPSHOT_PATH.read_text(encoding="utf-8")
    task = load_task()
    trace = make_trace()
    trace["task_id"] = TASK_ID
    trace["task_instance_sha256"] = task["split_metadata"]["task_instance_sha256"]
    trace["environment"] = {
        "environment_id": task["environment"]["environment_id"],
        "version": task["environment"]["version"],
        "state_sha256": task["environment"]["state_sha256"],
    }
    trace["tool_schema_sha256"] = task["tool_inventory"]["tool_schema_sha256"]
    trace["provenance"]["evidence_class"] = "scripted-reference"
    trace["provenance"]["executor"] = "study0-s05-go-release-schema-unit-test"
    for event in trace["events"]:
        event["task_id"] = TASK_ID
    arguments = {
        "urls": [URL],
        "format": "markdown",
        "links": False,
        "image_links": False,
        "iframe_links": False,
        "page_metadata": True,
    }
    for event in trace["events"][2:4]:
        event["tool_id"] = tool_id
        event["arguments"] = copy.deepcopy(arguments)
    trace["events"][3]["actual_tool_result"] = {
        "ok": ok,
        "result": {"url": URL, "content": snapshot},
        "error": None if ok else "synthetic fetch failure",
        "provider_cost": 0,
    }
    trace["usage"] = {"tool_calls": 1, "provider_credits_spent": 0}
    trace["final_answer"] = "Go 1.27.3 was released on 2026-10-19."
    return trace


def grade(trace: dict):
    return grade_task(load_task(), trace)


class Study0TinyFishRequiredFieldsTaskGraderTests(unittest.TestCase):
    def test_s05_004_accepts_successful_typed_request_and_source_bound_release_fact(self):
        result = grade(make_s05_004_trace())
        self.assertEqual(result["status"], "pass", result)

    def test_s05_004_rejects_each_missing_required_runtime_argument(self):
        for field in REQUIRED_FIELDS:
            with self.subTest(field=field):
                trace = make_s05_004_trace()
                for event in trace["events"][2:4]:
                    event["arguments"].pop(field)
                result = grade(trace)
                self.assertEqual(result["status"], "fail", result)

    def test_s05_004_rejects_page_metadata_as_string_not_boolean(self):
        trace = make_s05_004_trace()
        for event in trace["events"][2:4]:
            event["arguments"]["page_metadata"] = "true"
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_004_rejects_wrong_type_for_other_required_boolean_flags(self):
        for field in ("links", "image_links", "iframe_links"):
            with self.subTest(field=field):
                trace = make_s05_004_trace()
                for event in trace["events"][2:4]:
                    event["arguments"][field] = "false"
                result = grade(trace)
                self.assertEqual(result["status"], "fail", result)

    def test_s05_004_rejects_urls_argument_as_string(self):
        trace = make_s05_004_trace()
        for event in trace["events"][2:4]:
            event["arguments"]["urls"] = URL
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_004_rejects_extra_url_in_exact_single_source_request(self):
        trace = make_s05_004_trace()
        for event in trace["events"][2:4]:
            event["arguments"]["urls"] = [URL, "https://example.org/"]
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_004_rejects_failed_fetch_even_with_matching_arguments(self):
        result = grade(make_s05_004_trace(ok=False))
        self.assertEqual(result["status"], "fail", result)

    def test_s05_004_rejects_wrong_provider_tool(self):
        result = grade(make_s05_004_trace(tool_id="mcp__GitHub__fetch_file"))
        self.assertEqual(result["status"], "fail", result)

    def test_s05_004_rejects_response_not_attributed_to_official_go_url(self):
        trace = make_s05_004_trace()
        for event in trace["events"][2:4]:
            event["arguments"]["urls"] = ["https://example.org/"]
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_004_rejects_incorrect_go_release_revision(self):
        trace = make_s05_004_trace()
        trace["events"][3]["actual_tool_result"]["result"]["content"] = (
            trace["events"][3]["actual_tool_result"]["result"]["content"]
            .replace("Go 1.27.3", "Go 1.27.2")
        )
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)

    def test_s05_004_rejects_incorrect_go_release_date(self):
        trace = make_s05_004_trace()
        trace["events"][3]["actual_tool_result"]["result"]["content"] = (
            trace["events"][3]["actual_tool_result"]["result"]["content"]
            .replace("2026-10-19", "2026-10-18")
        )
        result = grade(trace)
        self.assertEqual(result["status"], "fail", result)


if __name__ == "__main__":
    unittest.main()
