from __future__ import annotations

import copy
import json
from dataclasses import replace
from pathlib import Path

import pytest

from DHI_v1.benchmark.plugin_execution import prepare_plugin_execution
from DHI_v1.benchmark.plugin_runner import PluginRunnerError, run_plugin_task
from DHI_v1.benchmark.plugin_task_loader import load_plugin_task
from DHI_v1.benchmark.plugin_trace import validate_trace


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"
REGISTRY = ROOT / "DHI_v1" / "benchmark" / "fixtures" / "plugin_ecology" / "plugin_tool_registry.json"
TRACE_SCHEMA = json.loads((ROOT / "DHI_v1" / "benchmark" / "plugin_trace.schema.json").read_text(encoding="utf-8"))

FETCH_FILE = "mcp__GitHub__fetch_file"
FETCH = "mcp__GitHub__fetch"
CREATE_FILE = "mcp__GitHub__create_file"


def _task_and_plan(task_id: str = "ORBIT-A-S04-001"):
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    task_record = copy.deepcopy(next(task for task in manifest["tasks"] if task["task_id"] == task_id))
    # Unit tests operate on an in-memory authorization copy only.
    task_record["execution"]["model_runs_allowed"] = True
    plan = replace(load_plugin_task(MANIFEST, REGISTRY, task_id), model_runs_allowed=True)
    return task_record, plan


def _prepared(plan):
    schemas = {
        FETCH_FILE: {
            "type": "object",
            "properties": {
                "repository_full_name": {"type": "string"},
                "path": {"type": "string"},
                "ref": {"type": "string"},
                "start_line": {"type": "integer"},
                "end_line": {"type": "integer"},
            },
            "required": ["repository_full_name", "path"],
            "additionalProperties": False,
        },
        FETCH: {
            "type": "object",
            "properties": {"url": {"type": "string"}},
            "required": ["url"],
            "additionalProperties": False,
        },
        CREATE_FILE: {
            "type": "object",
            "properties": {
                "repository_full_name": {"type": "string"},
                "path": {"type": "string"},
                "content": {"type": "string"},
                "message": {"type": "string"},
                "branch": {"type": "string"},
            },
            "required": ["repository_full_name", "path", "content", "message"],
            "additionalProperties": False,
        },
    }
    calls = []
    handlers = {
        FETCH_FILE: lambda args: calls.append(("read", args)) or {
            "sha": "0e5d3c519749651ad5f5ec728622895cfc44a649",
            "content": "fixture policy content",
        },
        FETCH: lambda args: calls.append(("fetch", args)) or {"content": "generic fetch"},
    }
    return prepare_plugin_execution(plan, schemas=schemas, handlers=handlers), calls


class ScriptedClient:
    def __init__(self, function_name: str, arguments: dict, final_answer: str = "Read completed.") -> None:
        self.function_name = function_name
        self.arguments = arguments
        self.final_answer = final_answer
        self.calls = 0
        self.seen_schemas = []

    def complete(self, *, messages, tools, temperature=0.0):
        self.calls += 1
        self.seen_schemas.append(copy.deepcopy(tools))
        if self.calls == 1:
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "tool_calls": [{
                            "id": "call-scripted-1",
                            "type": "function",
                            "function": {
                                "name": self.function_name,
                                "arguments": json.dumps(self.arguments),
                            },
                        }],
                    },
                }],
            }
        return {"choices": [{"message": {"role": "assistant", "content": self.final_answer}}]}


def test_scripted_model_dispatches_allowed_tool_and_emits_gradeable_append_only_trace():
    task_record, plan = _task_and_plan()
    prepared, handler_calls = _prepared(plan)
    tool_name = prepared.tool_name_by_id[FETCH_FILE]
    client = ScriptedClient(tool_name, {
        "repository_full_name": "Kshitijpalsinghtomar/dhi",
        "path": "TASK_POLICY.md",
        "ref": "af6c0d31fcf2e3232cb427c421850536139e3b3a",
        "__dhi_expected_effects": {
            "changed_paths": [],
            "unchanged_paths": ["northstar/TASK_POLICY.md"],
        },
    })
    state = {"northstar/TASK_POLICY.md": "b" * 64}

    result = run_plugin_task(
        task_record,
        prepared,
        client,
        observe_state=lambda: dict(state),
        trajectory_id="traj-plugin-runner-test-001",
    )

    assert result.final_answer == "Read completed."
    assert result.stopped_reason == "final_answer"
    assert result.model_turn_count == 2
    assert result.tool_call_count == 1
    assert handler_calls == [("read", {
        "repository_full_name": "Kshitijpalsinghtomar/dhi",
        "path": "TASK_POLICY.md",
        "ref": "af6c0d31fcf2e3232cb427c421850536139e3b3a",
    })]
    assert [event["event_type"] for event in result.trace["events"]] == [
        "task_started", "assistant_prediction", "action_started",
        "action_executed", "task_closed",
    ]
    assert result.trace["events"][1]["expected_effects"]["unchanged_paths"] == [
        "northstar/TASK_POLICY.md"
    ]
    assert result.trace["events"][3]["actual_tool_result"]["ok"] is True
    assert result.trace["events"][3]["actual_effects"]["unchanged_paths"] == [
        "northstar/TASK_POLICY.md"
    ]
    assert result.trace["closure"]["status"] == "success"
    assert result.grade["status"] == "pass"
    assert result.trace_validation_errors == []
    assert validate_trace(result.trace, TRACE_SCHEMA) == []
    assert client.calls == 2


def test_scripted_model_cannot_dispatch_visible_but_denied_write_tool():
    task_record, plan = _task_and_plan()
    prepared, handler_calls = _prepared(plan)
    denied_name = prepared.tool_name_by_id[CREATE_FILE]
    client = ScriptedClient(denied_name, {
        "repository_full_name": "Kshitijpalsinghtomar/dhi",
        "path": "TASK_POLICY.md",
        "content": "attempted write",
        "message": "must be denied",
    })
    state = {"northstar/TASK_POLICY.md": "b" * 64}

    result = run_plugin_task(
        task_record,
        prepared,
        client,
        observe_state=lambda: dict(state),
        trajectory_id="traj-plugin-runner-denied-write",
    )

    assert all(kind != "write" for kind, _ in handler_calls)
    executed = [event for event in result.trace["events"] if event["event_type"] == "action_executed"]
    assert len(executed) == 1
    assert executed[0]["tool_id"] == CREATE_FILE
    assert executed[0]["actual_tool_result"]["ok"] is False
    assert "not allowed by task" in executed[0]["actual_tool_result"]["error"]
    assert result.grade["status"] == "fail"
    assert result.trace["closure"]["status"] == "failure"
    assert result.trace_validation_errors == []


def test_runner_rejects_task_record_that_still_disables_model_execution():
    task_record, plan = _task_and_plan()
    task_record["execution"]["model_runs_allowed"] = False
    prepared, _ = _prepared(plan)

    class NeverCalled:
        def complete(self, **kwargs):
            raise AssertionError("model must not be called for a disabled manifest task")

    with pytest.raises(PluginRunnerError, match="model_runs_allowed=false"):
        run_plugin_task(
            task_record,
            prepared,
            NeverCalled(),
            observe_state=lambda: {},
        )


def test_runner_requires_independent_state_observer_for_sandbox_write_tasks():
    task_record, plan = _task_and_plan("ORBIT-A-S06-001")
    # A separate test only needs to prove that write tasks cannot run without
    # an independently observed before/after state source.
    schemas = {
        tool_id: {"type": "object", "properties": {}, "additionalProperties": False}
        for tool_id in plan.visible_tool_ids
    }
    handlers = {
        tool_id: (lambda args: {"ok": True})
        for tool_id in plan.allowed_tool_ids
    }
    guards = {
        tool_id: (lambda task, args: True)
        for tool_id in plan.allowed_tool_ids
        if plan.tool_contracts[tool_id].get("side_effect_class") == "sandbox_write"
    }
    prepared = prepare_plugin_execution(
        plan, schemas=schemas, handlers=handlers, write_guards=guards
    )

    with pytest.raises(PluginRunnerError, match="state observer"):
        run_plugin_task(task_record, prepared, ScriptedClient("unused", {}))
