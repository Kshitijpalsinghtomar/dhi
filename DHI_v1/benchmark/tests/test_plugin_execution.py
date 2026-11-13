from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import pytest

from DHI_v1.benchmark.plugin_task_loader import load_plugin_task
from DHI_v1.benchmark.plugin_execution import (
    PluginExecutionNotReady,
    PluginToolPermissionError,
    prepare_plugin_execution,
)


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"
REGISTRY = ROOT / "DHI_v1" / "benchmark" / "fixtures" / "plugin_ecology" / "plugin_tool_registry.json"


def _plan(task_id: str):
    # The live manifest intentionally disables every model run. The copy below
    # lets unit tests exercise readiness/dispatch without authorizing real runs.
    return replace(load_plugin_task(MANIFEST, REGISTRY, task_id), model_runs_allowed=True)


def _schema(required=()):
    return {
        "type": "object",
        "properties": {
            name: {"type": "string"}
            for name in required
        },
        "required": list(required),
        "additionalProperties": False,
    }


def test_runner_refuses_to_prepare_when_manifest_keeps_model_runs_disabled():
    plan = load_plugin_task(MANIFEST, REGISTRY, "ORBIT-A-S02-001")
    schemas = {tool_id: _schema() for tool_id in plan.visible_tool_ids}
    handlers = {tool_id: (lambda args: {"ok": True}) for tool_id in plan.allowed_tool_ids}

    with pytest.raises(PluginExecutionNotReady, match="model_runs_allowed=false"):
        prepare_plugin_execution(plan, schemas=schemas, handlers=handlers)


def test_runner_fails_closed_when_a_required_tool_handler_is_missing():
    plan = _plan("ORBIT-A-S02-001")
    schemas = {tool_id: _schema() for tool_id in plan.visible_tool_ids}
    handlers = {"mcp__TinyFish__search": lambda args: {"ok": True}}

    with pytest.raises(PluginExecutionNotReady, match="missing callable handler"):
        prepare_plugin_execution(plan, schemas=schemas, handlers=handlers)


def test_runner_requires_contract_schemas_for_every_visible_tool():
    plan = _plan("ORBIT-A-S10-001")
    schemas = {"mcp__GitHub__fetch_file": _schema()}
    handlers = {"mcp__GitHub__fetch_file": lambda args: {"ok": True}}

    with pytest.raises(PluginExecutionNotReady, match="missing schema"):
        prepare_plugin_execution(plan, schemas=schemas, handlers=handlers)


def test_visible_but_denied_write_tool_is_advertised_but_never_dispatched():
    plan = _plan("ORBIT-A-S10-001")
    schemas = {tool_id: _schema() for tool_id in plan.visible_tool_ids}
    calls = []
    handlers = {"mcp__GitHub__fetch_file": lambda args: {"ok": True},
                "mcp__GitHub__create_file": lambda args: calls.append(args) or {"ok": True}}

    prepared = prepare_plugin_execution(plan, schemas=schemas, handlers=handlers)

    names = {item["function"]["name"] for item in prepared.tool_schemas}
    denied_name = prepared.tool_name_by_id["mcp__GitHub__create_file"]
    assert denied_name in names

    with pytest.raises(PluginToolPermissionError, match="not allowed by task"):
        prepared.dispatch(denied_name, {"path": "report.md"})
    assert calls == []


def test_sandbox_write_requires_a_task_specific_write_guard():
    plan = _plan("ORBIT-A-S06-001")
    schemas = {tool_id: _schema() for tool_id in plan.visible_tool_ids}
    handlers = {tool_id: (lambda args: {"ok": True}) for tool_id in plan.allowed_tool_ids}

    with pytest.raises(PluginExecutionNotReady, match="missing write guard"):
        prepare_plugin_execution(plan, schemas=schemas, handlers=handlers)


def test_dispatch_validates_arguments_before_calling_the_handler():
    plan = _plan("ORBIT-A-S02-001")
    schemas = {
        "mcp__TinyFish__search": _schema(("query",)),
        "mcp__TinyFish__fetch_content": _schema(("urls",)),
    }
    calls = []
    handlers = {tool_id: lambda args: calls.append(args) or {"ok": True}
                for tool_id in plan.allowed_tool_ids}
    prepared = prepare_plugin_execution(plan, schemas=schemas, handlers=handlers)
    name = prepared.tool_name_by_id["mcp__TinyFish__search"]

    with pytest.raises(PluginToolPermissionError, match="schema validation"):
        prepared.dispatch(name, {"query": "ok", "unexpected": "field"})
    assert calls == []


def test_prepared_runner_preserves_canonical_ids_and_dispatches_only_allowed_tools():
    plan = _plan("ORBIT-A-S02-001")
    schemas = {
        "mcp__TinyFish__search": _schema(("query",)),
        "mcp__TinyFish__fetch_content": _schema(("urls",)),
    }
    handlers = {
        "mcp__TinyFish__search": lambda args: {"provider": "search", "query": args["query"]},
        "mcp__TinyFish__fetch_content": lambda args: {"provider": "fetch", "urls": args["urls"]},
    }
    prepared = prepare_plugin_execution(plan, schemas=schemas, handlers=handlers)

    assert set(prepared.tool_name_by_id) == set(plan.visible_tool_ids)
    assert prepared.dispatch(prepared.tool_name_by_id["mcp__TinyFish__search"], {"query": "official docs"}) == {
        "provider": "search", "query": "official docs"
    }


def test_sandbox_write_guard_must_authorize_the_exact_task_and_arguments():
    plan = _plan("ORBIT-A-S06-001")
    schemas = {tool_id: _schema() for tool_id in plan.visible_tool_ids}
    schemas["mcp__GitHub__create_file"] = _schema(("path",))
    calls = []
    handlers = {tool_id: lambda args: calls.append(args) or {"ok": True}
                for tool_id in plan.allowed_tool_ids}
    write_guards = {"mcp__GitHub__create_file": lambda task, args: args.get("path") == "DHI_v1/benchmark/fixtures/plugin_ecology/reports/release-readiness.md"}

    prepared = prepare_plugin_execution(
        plan, schemas=schemas, handlers=handlers, write_guards=write_guards
    )
    name = prepared.tool_name_by_id["mcp__GitHub__create_file"]

    with pytest.raises(PluginToolPermissionError, match="write guard denied"):
        prepared.dispatch(name, {"path": "README.md"})
    assert calls == []

    result = prepared.dispatch(name, {"path": "DHI_v1/benchmark/fixtures/plugin_ecology/reports/release-readiness.md"})
    assert result == {"ok": True}
    assert calls == [{"path": "DHI_v1/benchmark/fixtures/plugin_ecology/reports/release-readiness.md"}]
