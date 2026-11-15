from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from DHI_v1.benchmark.plugin_trace import grade_task
from test_plugin_trace_grader import make_trace


ROOT = Path(__file__).resolve().parents[3]
MANIFEST_PATH = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"

SCENARIOS = {
    "ORBIT-A-S03-001": {
        "snapshot": "DHI_v1/benchmark/fixtures/plugin_ecology/discovery_snapshots/firecrawl_package_metadata_2026-11-03.md",
        "query": "software release latest version package registry metadata",
        "response": {
            "provider": "package-registry-metadata-download-stats",
            "capability": "packages/package",
            "required_inputs": ["registry", "name"],
            "execution_credits": 1,
            "discovery_credits": 0,
        },
        "snapshot_assertions": [
            "package-registry-metadata-download-stats",
            "packages/package",
            "registry",
            "name",
            "Execution credit cost: 1",
            "Discovery call credit cost: 0",
        ],
    },
    "ORBIT-A-S03-002": {
        "snapshot": "DHI_v1/benchmark/fixtures/plugin_ecology/discovery_snapshots/firecrawl_security_provider_discovery_2026-11-03.md",
        "query": "software security advisories CVE affected package version severity patched version",
        "response": {
            "provider": "osv-dev",
            "capability": "vulnerabilities/query",
            "acceptable_inputs": ["purl", "ecosystem+name"],
            "execution_credits": 5,
        },
        "snapshot_assertions": [
            "osv-dev",
            "vulnerabilities/query",
            "purl",
            "ecosystem",
            "version",
            "5 credits",
        ],
    },
    "ORBIT-A-S03-003": {
        "snapshot": "DHI_v1/benchmark/fixtures/plugin_ecology/discovery_snapshots/firecrawl_research_provider_discovery_2026-11-03.md",
        "query": "academic research paper metadata abstract citation context full text",
        "response": {
            "required": [
                ["semanticscholar-org", "papers/search_papers", 5],
                ["semanticscholar-org", "papers/get_paper", 5],
                ["semanticscholar-org", "papers/get_citations", 5],
                ["firecrawl-research-index", "inspect", 0],
            ],
        },
        "snapshot_assertions": [
            "semanticscholar-org",
            "papers/search_papers",
            "papers/get_paper",
            "papers/get_citations",
            "firecrawl-research-index",
            "inspect",
            "5 credits",
            "0 credits",
        ],
    },
    "ORBIT-A-S03-004": {
        "snapshot": "DHI_v1/benchmark/fixtures/plugin_ecology/discovery_snapshots/firecrawl_dependents_contract_2026-11-03.md",
        "query": "package reverse dependencies provider capability",
        "response": {
            "provider": "package-registry-metadata-download-stats",
            "capability": "packages/dependents",
            "required_inputs": ["registry", "name"],
            "optional_inputs": ["version", "sample"],
            "execution_credits": 1,
            "discovery_credits": 0,
            "output_fields": ["total", "direct", "indirect"],
        },
        "snapshot_assertions": [
            "package-registry-metadata-download-stats",
            "packages/dependents",
            "registry",
            "name",
            "version",
            "sample",
            "total",
            "direct",
            "indirect",
            "Execution cost: **1 credit**",
            "Discovery call cost: 0 credits",
        ],
    },
}


def load_manifest_tasks() -> dict[str, dict]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {
        task["task_id"]: task
        for task in manifest["tasks"]
        if task["task_id"] in SCENARIOS
    }


def discovery_trace(task: dict, *, response_override: dict | None = None) -> dict:
    task_id = task["task_id"]
    scenario = SCENARIOS[task_id]
    trace = make_trace()
    trace["task_id"] = task_id
    trace["task_instance_sha256"] = task["split_metadata"]["task_instance_sha256"]
    trace["environment"] = {
        "environment_id": task["environment"]["environment_id"],
        "version": task["environment"]["version"],
        "state_sha256": task["environment"]["state_sha256"],
    }
    trace["tool_schema_sha256"] = task["tool_inventory"]["tool_schema_sha256"]
    trace["provenance"]["evidence_class"] = "scripted-reference"
    trace["provenance"]["executor"] = "study0-discovery-contract-unit-test"
    trace["events"] = [
        copy.deepcopy(trace["events"][0]),
        {
            "event_id": f"{task_id}-discovery",
            "event_index": 2,
            "event_type": "tool_discovery",
            "timestamp_utc": "2026-11-03T00:00:01Z",
            "task_id": task_id,
            "query": scenario["query"],
            "visible_tool_ids": ["mcp__Firecrawl__firecrawl_find_tools"],
            "discovered_tool_ids": [
                scenario["response"].get("capability", "provider-contract-bundle")
            ],
            "discovery_results": [
                copy.deepcopy(response_override or scenario["response"])
            ],
        },
        copy.deepcopy(trace["events"][-1]),
    ]
    for index, event in enumerate(trace["events"], 1):
        event["event_index"] = index
        event["task_id"] = task_id
        event["event_id"] = f"{task_id}-event-{index}"
    trace["usage"] = {"tool_calls": 0, "provider_credits_spent": 0}
    trace["final_answer"] = "Discovered the registered provider contract; no paid provider was executed."
    trace["closure"]["status"] = "success"
    return trace


class Study0ProviderDiscoveryTaskGraderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tasks = load_manifest_tasks()
        if set(cls.tasks) != set(SCENARIOS):
            raise AssertionError("All four exact Stage A S03 tasks must exist in the manifest.")

    def task_copy(self, task_id: str) -> dict:
        task = copy.deepcopy(self.tasks[task_id])
        task["task_instance_sha256"] = task["split_metadata"]["task_instance_sha256"]
        return task

    def test_all_four_snapshot_backed_discovery_contracts_pass(self):
        for task_id, scenario in SCENARIOS.items():
            with self.subTest(task_id=task_id):
                snapshot_path = ROOT / scenario["snapshot"]
                snapshot = snapshot_path.read_text(encoding="utf-8")
                for required_text in scenario["snapshot_assertions"]:
                    self.assertIn(required_text, snapshot, required_text)

                task = self.task_copy(task_id)
                trace = discovery_trace(task)
                result = grade_task(task, trace)
                self.assertEqual(result["status"], "pass", result)
                self.assertTrue(all(item["status"] == "pass" for item in result["results"]))
                self.assertEqual(trace["provenance"]["evidence_class"], "scripted-reference")
                self.assertEqual(trace["usage"], {"tool_calls": 0, "provider_credits_spent": 0})

    def test_package_metadata_rejects_wrong_execution_cost(self):
        task = self.task_copy("ORBIT-A-S03-001")
        response = copy.deepcopy(SCENARIOS[task["task_id"]]["response"])
        response["execution_credits"] = 0
        result = grade_task(task, discovery_trace(task, response_override=response))
        self.assertEqual(result["status"], "fail")

    def test_security_discovery_rejects_single_record_provider_as_osv_query(self):
        task = self.task_copy("ORBIT-A-S03-002")
        response = copy.deepcopy(SCENARIOS[task["task_id"]]["response"])
        response["provider"] = "github-com"
        result = grade_task(task, discovery_trace(task, response_override=response))
        self.assertEqual(result["status"], "fail")

    def test_research_discovery_rejects_nonzero_metadata_inspection_cost(self):
        task = self.task_copy("ORBIT-A-S03-003")
        response = copy.deepcopy(SCENARIOS[task["task_id"]]["response"])
        response["required"][-1][2] = 5
        result = grade_task(task, discovery_trace(task, response_override=response))
        self.assertEqual(result["status"], "fail")

    def test_dependents_discovery_rejects_missing_direct_indirect_output_fields(self):
        task = self.task_copy("ORBIT-A-S03-004")
        response = copy.deepcopy(SCENARIOS[task["task_id"]]["response"])
        response["output_fields"] = ["total", "indirect"]
        result = grade_task(task, discovery_trace(task, response_override=response))
        self.assertEqual(result["status"], "fail")


if __name__ == "__main__":
    unittest.main()
