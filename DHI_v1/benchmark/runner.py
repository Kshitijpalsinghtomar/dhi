"""Execute supported DHI-v1 pilot cases and score observable outcomes."""
from __future__ import annotations

import json
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from DHI_v1.environment.agent_runner import ChatCompletionClient, run_agent_task
from DHI_v1.environment.dhi_env import DHIEnvironment, TaskSpec
from DHI_v1.environment.fixture_manager import materialize_fixture

SUPPORTED_SCOPE = "file_workspace"
SUPPORTED_STATUS = {"pilot_case"}


def load_supported_cases(suite_path: str | Path) -> list[dict[str, Any]]:
    suite = json.loads(Path(suite_path).read_text(encoding="utf-8"))
    cases = suite.get("cases")
    if not isinstance(cases, list):
        raise ValueError("benchmark suite must contain a cases array")
    selected = [
        case for case in cases
        if case.get("scope") == SUPPORTED_SCOPE and case.get("status") in SUPPORTED_STATUS
    ]
    ids = [case.get("case_id") for case in selected]
    if not selected or any(not isinstance(case_id, str) or not case_id for case_id in ids):
        raise ValueError("no valid supported pilot cases found")
    if len(ids) != len(set(ids)):
        raise ValueError("supported pilot case IDs must be unique")
    for case in selected:
        if not case.get("postconditions"):
            raise ValueError(f"case {case['case_id']} needs executable postconditions")
        if not isinstance(case.get("evaluation", {}), dict):
            raise ValueError(f"case {case['case_id']} evaluation must be an object")
    return selected


def evaluate_case(case: dict[str, Any], result: Any, events: list[dict[str, Any]]) -> dict[str, Any]:
    """Score explicit, observable criteria; no LLM judge is used."""
    evaluation = case.get("evaluation", {})
    answer = (result.final_answer or "").casefold()
    closure = result.closure or {}
    checks: dict[str, bool] = {"closure": bool(closure.get("success"))}

    if evaluation.get("answer_contains"):
        checks["answer_contains"] = all(str(value).casefold() in answer for value in evaluation["answer_contains"])
    if evaluation.get("answer_any_contains"):
        checks["answer_any_contains"] = any(str(value).casefold() in answer for value in evaluation["answer_any_contains"])

    action_events = [event for event in events if event.get("event_type") == "action_executed"]
    used_tools = {event.get("selected_tool_id") for event in action_events}
    if evaluation.get("must_use_tools"):
        checks["required_tools_used"] = set(evaluation["must_use_tools"]).issubset(used_tools)

    discovered_tools = {
        tool_id for event in events if event.get("event_type") == "tool_discovery"
        for tool_id in event.get("discovered_tool_ids", [])
    }
    if evaluation.get("must_discover"):
        checks["required_discoveries"] = set(evaluation["must_discover"]).issubset(discovered_tools)

    closure_event = closure.get("event", {})
    changed_paths = set(closure_event.get("overall_effects", {}).get("changed_paths", []))
    if "max_changed_paths" in evaluation:
        checks["max_changed_paths"] = len(changed_paths) <= int(evaluation["max_changed_paths"])
    if evaluation.get("must_change_paths"):
        checks["required_paths_changed"] = set(evaluation["must_change_paths"]).issubset(changed_paths)
    if "max_tool_calls" in evaluation:
        checks["max_tool_calls"] = int(getattr(result, "tool_call_count", 0)) <= int(evaluation["max_tool_calls"])

    if "min_tool_errors" in evaluation:
        errors = sum(1 for event in action_events if not event.get("actual_tool_result", {}).get("ok", False))
        checks["min_tool_errors"] = errors >= int(evaluation["min_tool_errors"])
    if evaluation.get("must_succeed_tool_any"):
        successful_tools = {
            event.get("selected_tool_id") for event in action_events
            if event.get("actual_tool_result", {}).get("ok", False)
        }
        checks["must_succeed_tool_any"] = bool(successful_tools & set(evaluation["must_succeed_tool_any"]))

    protected = closure.get("verified_protected_paths", [])
    checks["protected_paths_preserved"] = all(item.get("passed", False) for item in protected)
    return {
        "case_id": case["case_id"],
        "passed": all(checks.values()),
        "checks": checks,
        "failed_checks": [name for name, passed in checks.items() if not passed],
        "tool_call_count": getattr(result, "tool_call_count", 0),
        "model_turn_count": getattr(result, "model_turn_count", 0),
        "stopped_reason": getattr(result, "stopped_reason", None),
        "closure_success": bool(closure.get("success")),
        "final_answer": result.final_answer,
    }


def run_pilot_benchmark(
    client: ChatCompletionClient,
    *,
    model_name: str,
    suite_path: str | Path,
    fixture_root: str | Path,
    output_root: str | Path,
    max_model_turns: int = 16,
    max_tool_calls: int = 48,
) -> dict[str, Any]:
    cases = load_supported_cases(suite_path)
    run_id = uuid.uuid4().hex[:12]
    run_dir = Path(output_root).expanduser().resolve() / f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{run_id}"
    trace_dir = run_dir / "traces"
    trace_dir.mkdir(parents=True, exist_ok=False)
    results: list[dict[str, Any]] = []

    for case in cases:
        with tempfile.TemporaryDirectory(prefix=f"dhi-{case['case_id']}-") as temporary:
            workspace = Path(temporary) / "workspace"
            materialize_fixture(fixture_root, workspace)
            variant = case.get("fixture_variant")
            if variant == "readme_already_complete":
                with (workspace / "README.md").open("a", encoding="utf-8") as handle:
                    handle.write("\nHealth-check function: \x60src/api.py#healthcheck\x60\n")
            elif variant:
                raise ValueError(f"unknown fixture variant: {variant}")

            task = TaskSpec(
                task_id=case["case_id"],
                prompt=case["prompt"],
                goal=case["goal"],
                hard_constraints=case.get("hard_constraints", []),
                preferences=case.get("preferences", []),
                postconditions=case["postconditions"],
                protected_paths=case.get("protected_paths", []),
                visible_tool_ids=case.get("visible_tool_ids"),
                fault_injections=case.get("fault_injections", []),
                split="development_pilot_not_frozen",
                metadata={
                    "origin": "hand-authored DHI-v1 pilot case",
                    "case_id": case["case_id"],
                    "fixture_id": "dhi-v1-basic-repository",
                    "fixture_variant": variant,
                    "model_name": model_name,
                    "training_eligible": False,
                },
            )
            trace_path = trace_dir / f"{case['case_id']}.jsonl"
            environment = DHIEnvironment(workspace, trace_path=trace_path)
            model_result = run_agent_task(
                environment, task, client,
                max_model_turns=max_model_turns,
                max_tool_calls=max_tool_calls,
            )
            outcome = evaluate_case(case, model_result, environment.events)
            outcome["trace_path"] = str(trace_path)
            outcome["closure"] = model_result.closure
            results.append(outcome)

    passed = sum(1 for result in results if result["passed"])
    report = {
        "benchmark_id": "dhi-v1-agentic-pilot-0.1",
        "suite_status": "development_pilot_not_frozen",
        "run_id": run_id,
        "model_name": model_name,
        "case_count": len(results),
        "passed_cases": passed,
        "pass_rate": passed / len(results) if results else 0.0,
        "results": results,
        "training_eligible": False,
        "limitations": [
            "Only deterministic file-workspace cases are executed.",
            "This is a small pilot, not the frozen 120-task base-screen benchmark.",
            "The local catalogue is lexical and contains six fixture tools, not a live app/plugin marketplace.",
            "A model pass rate here is not the weighted DHI 100-point rubric or a universal capability claim.",
        ],
    }
    (run_dir / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report["report_path"] = str(run_dir / "report.json")
    return report
