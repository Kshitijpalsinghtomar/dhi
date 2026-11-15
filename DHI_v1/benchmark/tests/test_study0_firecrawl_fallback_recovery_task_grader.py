from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from DHI_v1.benchmark.plugin_trace import grade_task
from test_plugin_trace_grader import make_trace


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"
TASK_ID = "ORBIT-A-S08-002"
TOOL_ID = "mcp__Firecrawl__firecrawl_find_tools"
PROVIDER = "package-registry-metadata-download-stats"
CAPABILITY = "packages/package"
BROAD_QUERY = "software release latest version package registry metadata"
SCOPED_QUERY = "package-registry-metadata-download-stats packages/package"
BROAD_ARGS = {"query": BROAD_QUERY}
SCOPED_ARGS = {
    "providers": [PROVIDER],
    "capabilities": [CAPABILITY],
    "level": "tools",
    "expand": ["options", "response"],
}
REQUIRED_INPUTS = ["registry", "name"]
OUTPUT_FIELDS = [
    "latest_version", "latest_published_at", "license", "repository",
    "downloads", "dependents", "source_urls", "warnings",
]
ANSWER = (
    "The broad discovery did not return no matches: it timed out during reranking but "
    "returned a matching candidate and nextTool continuation. I followed that continuation "
    "with provider-filtered discovery for package-registry-metadata-download-stats / "
    "packages/package. Required inputs: registry and name. Output fields: latest_version, "
    "latest_published_at, license, repository, downloads, dependents, source_urls and warnings. "
    "Discovery cost: 0 credits. Provider execution cost: 1 credit. No provider execution occurred."
)


def load_task() -> dict:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    task = copy.deepcopy(next(item for item in manifest["tasks"] if item["task_id"] == TASK_ID))
    task["task_instance_sha256"] = task["split_metadata"]["task_instance_sha256"]
    return task


def condition() -> dict:
    return copy.deepcopy(load_task()["postconditions"][0]["condition"])


def fallback_record() -> dict:
    return {
        "phase": "broad_fallback",
        "status": "reranking_fallback",
        "candidate_items": [{
            "provider": PROVIDER,
            "capability": CAPABILITY,
            "name": "Package registry metadata and download stats",
        }],
        "nextTool": {
            "provider": PROVIDER,
            "capability": CAPABILITY,
            "level": "tools",
            "expand": ["options", "response"],
        },
    }


def scoped_record() -> dict:
    return {
        "phase": "provider_filtered",
        "status": "success",
        "provider": PROVIDER,
        "capability": CAPABILITY,
        "required_inputs": copy.deepcopy(REQUIRED_INPUTS),
        "output_fields": copy.deepcopy(OUTPUT_FIELDS),
        "execution_credits": 1,
        "discovery_credits": 0,
    }


def make_trace(
    *,
    fallback: dict | None = None,
    scoped: dict | None = None,
    broad_tool: str = TOOL_ID,
    scoped_tool: str = TOOL_ID,
    broad_query: str = BROAD_QUERY,
    scoped_query: str = SCOPED_QUERY,
    broad_arguments: dict | None = None,
    scoped_arguments: dict | None = None,
    broad_visible: list[str] | None = None,
    scoped_visible: list[str] | None = None,
    paid_actions: bool = False,
    extra_discovery: bool = False,
    reverse: bool = False,
    answer: str = ANSWER,
    credits: int = 0,
    tool_calls: int = 0,
) -> dict:
    task = load_task()
    base = make_trace()
    events = [copy.deepcopy(base["events"][0])]
    first = {
        "event_id": "s08-broad",
        "event_index": 2,
        "event_type": "tool_discovery",
        "timestamp_utc": "2026-11-03T00:00:01Z",
        "task_id": TASK_ID,
        "tool_id": broad_tool,
        "query": broad_query,
        "arguments": copy.deepcopy(BROAD_ARGS if broad_arguments is None else broad_arguments),
        "visible_tool_ids": copy.deepcopy(broad_visible if broad_visible is not None else [TOOL_ID]),
        "discovered_tool_ids": [CAPABILITY],
        "discovery_results": [copy.deepcopy(fallback if fallback is not None else fallback_record())],
    }
    second = {
        "event_id": "s08-scoped",
        "event_index": 3,
        "event_type": "tool_discovery",
        "timestamp_utc": "2026-11-03T00:00:02Z",
        "task_id": TASK_ID,
        "tool_id": scoped_tool,
        "query": scoped_query,
        "arguments": copy.deepcopy(SCOPED_ARGS if scoped_arguments is None else scoped_arguments),
        "visible_tool_ids": copy.deepcopy(scoped_visible if scoped_visible is not None else [TOOL_ID]),
        "discovered_tool_ids": [CAPABILITY],
        "discovery_results": [copy.deepcopy(scoped if scoped is not None else scoped_record())],
    }
    events.extend([second, first] if reverse else [first, second])
    if extra_discovery:
        duplicate = copy.deepcopy(second)
        duplicate["event_id"] = "s08-extra"
        duplicate["event_index"] = 4
        events.append(duplicate)
    if paid_actions:
        started = {
            "event_id": "s08-paid-start",
            "event_index": len(events) + 1,
            "event_type": "action_started",
            "timestamp_utc": "2026-11-03T00:00:04Z",
            "task_id": TASK_ID,
            "action_id": "paid-provider",
            "tool_id": "mcp__Firecrawl__firecrawl_scrape",
            "arguments": {"url": "https://registry.npmjs.org/example"},
            "observed_state_before": {"state.json": "a" * 64},
            "side_effect_class": "read_only",
        }
        done = {
            "event_id": "s08-paid-done",
            "event_index": len(events) + 2,
            "event_type": "action_executed",
            "timestamp_utc": "2026-11-03T00:00:05Z",
            "task_id": TASK_ID,
            "action_id": "paid-provider",
            "tool_id": "mcp__Firecrawl__firecrawl_scrape",
            "arguments": copy.deepcopy(started["arguments"]),
            "observed_state_before": {"state.json": "a" * 64},
            "observed_state_after": {"state.json": "a" * 64},
            "actual_tool_result": {
                "ok": True,
                "result": {"content": "package metadata"},
                "error": None,
                "provider_cost": 1,
            },
            "actual_effects": {
                "added_paths": [], "modified_paths": [], "deleted_paths": [],
                "changed_paths": [], "unchanged_paths": ["state.json"],
            },
        }
        events.extend([started, done])
    events.append({
        "event_id": f"s08-close-{len(events)}",
        "event_index": len(events) + 1,
        "event_type": "task_closed",
        "timestamp_utc": "2026-11-03T00:00:10Z",
        "task_id": TASK_ID,
        "closure_status": "success",
    })
    for index, event in enumerate(events, 1):
        event["event_index"] = index
        event["task_id"] = TASK_ID
    trace = copy.deepcopy(base)
    trace.update({
        "trajectory_id": "s08-firecrawl-fallback",
        "task_id": TASK_ID,
        "task_instance_sha256": task["split_metadata"]["task_instance_sha256"],
        "environment": {
            "environment_id": task["environment"]["environment_id"],
            "version": task["environment"]["version"],
            "state_sha256": task["environment"]["state_sha256"],
        },
        "tool_schema_sha256": task["tool_inventory"]["tool_schema_sha256"],
        "events": events,
        "final_answer": answer,
        "usage": {"tool_calls": tool_calls + (1 if paid_actions else 0), "provider_credits_spent": credits + (1 if paid_actions else 0)},
        "final_artifacts": [],
    })
    trace["provenance"]["evidence_class"] = "scripted-reference"
    trace["provenance"]["executor"] = "s08-firecrawl-fallback-tests"
    trace["closure"]["status"] = "success"
    return trace


def grade(trace: dict) -> dict:
    return grade_task(load_task(), trace)


class Study0FirecrawlFallbackRecoveryTests(unittest.TestCase):
    def test_positive_fallback_then_provider_filtered_recovery_passes(self):
        result = grade(make_trace())
        self.assertEqual(result["status"], "pass", result)

    def test_each_phase_must_be_emitted_by_registered_firecrawl_discovery_tool(self):
        self.assertNotEqual(grade(make_trace(broad_tool="mcp__GitHub__fetch_file"))["status"], "pass")
        self.assertNotEqual(grade(make_trace(scoped_tool="mcp__GitHub__fetch_file"))["status"], "pass")

    def test_visible_tool_inventory_must_include_firecrawl_discovery(self):
        self.assertNotEqual(grade(make_trace(broad_visible=[]))["status"], "pass")
        self.assertNotEqual(grade(make_trace(scoped_visible=[]))["status"], "pass")

    def test_broad_query_and_request_arguments_must_match_registered_request(self):
        self.assertNotEqual(grade(make_trace(broad_query="different query"))["status"], "pass")
        self.assertNotEqual(grade(make_trace(broad_arguments={"query": "different query"}))["status"], "pass")

    def test_scoped_recovery_must_be_provider_filtered_with_exact_capability_and_expansion(self):
        wrong = copy.deepcopy(SCOPED_ARGS)
        wrong["providers"] = ["another-provider"]
        self.assertNotEqual(grade(make_trace(scoped_arguments=wrong))["status"], "pass")
        wrong = copy.deepcopy(SCOPED_ARGS)
        wrong["capabilities"] = ["packages/dependents"]
        self.assertNotEqual(grade(make_trace(scoped_arguments=wrong))["status"], "pass")
        wrong = copy.deepcopy(SCOPED_ARGS)
        wrong["expand"] = ["options"]
        self.assertNotEqual(grade(make_trace(scoped_arguments=wrong))["status"], "pass")

    def test_fallback_must_contain_candidate_and_nexttool_continuation(self):
        fallback = fallback_record()
        fallback["candidate_items"] = []
        self.assertNotEqual(grade(make_trace(fallback=fallback))["status"], "pass")
        fallback = fallback_record()
        fallback.pop("nextTool")
        self.assertNotEqual(grade(make_trace(fallback=fallback))["status"], "pass")
        fallback = fallback_record()
        fallback["nextTool"]["provider"] = "wrong-provider"
        self.assertNotEqual(grade(make_trace(fallback=fallback))["status"], "pass")

    def test_broad_fallback_must_not_be_mislabeled_as_total_no_match(self):
        fallback = fallback_record()
        fallback["status"] = "no_matches"
        self.assertNotEqual(grade(make_trace(fallback=fallback))["status"], "pass")

    def test_scoped_result_must_return_exact_contract_including_output_fields(self):
        scoped = scoped_record()
        scoped["required_inputs"] = ["registry"]
        self.assertNotEqual(grade(make_trace(scoped=scoped))["status"], "pass")
        scoped = scoped_record()
        scoped["output_fields"] = ["latest_version"]
        self.assertNotEqual(grade(make_trace(scoped=scoped))["status"], "pass")

    def test_discovery_and_execution_costs_must_be_reported_separately(self):
        scoped = scoped_record()
        scoped["discovery_credits"] = 1
        self.assertNotEqual(grade(make_trace(scoped=scoped))["status"], "pass")
        scoped = scoped_record()
        scoped["execution_credits"] = 0
        self.assertNotEqual(grade(make_trace(scoped=scoped))["status"], "pass")

    def test_scoped_success_must_follow_fallback_and_only_two_discovery_events_exist(self):
        self.assertNotEqual(grade(make_trace(reverse=True))["status"], "pass")
        self.assertNotEqual(grade(make_trace(extra_discovery=True))["status"], "pass")

    def test_paid_execution_and_credit_spend_are_rejected(self):
        self.assertNotEqual(grade(make_trace(paid_actions=True))["status"], "pass")
        self.assertNotEqual(grade(make_trace(credits=1))["status"], "pass")

    def test_final_answer_must_not_claim_no_tools_found_or_paid_execution(self):
        for answer in (
            "No tools found.",
            "I executed the package provider for one credit.",
            "The discovery operation cost one credit.",
            "The execution cost is free.",
        ):
            with self.subTest(answer=answer):
                self.assertNotEqual(grade(make_trace(answer=answer))["status"], "pass")

    def test_declared_tool_call_count_must_not_claim_an_action_that_did_not_occur(self):
        self.assertNotEqual(grade(make_trace(tool_calls=1))["status"], "pass")


if __name__ == "__main__":
    unittest.main()
