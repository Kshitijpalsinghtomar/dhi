"""Fail-closed preparation and dispatch for manifest-driven plugin tasks.

This module is deliberately an execution boundary, not a provider integration.
Callers must supply exact schemas and separately approved callable handlers.
No provider is invoked during preparation; every dispatch is task-allowlisted.
"""
from __future__ import annotations

import copy
import re
from dataclasses import dataclass
from typing import Any, Callable, Mapping

from jsonschema import Draft202012Validator, FormatChecker, SchemaError

from .plugin_task_loader import PluginTaskPlan


ToolHandler = Callable[[dict[str, Any]], Any]
WriteGuard = Callable[[PluginTaskPlan, dict[str, Any]], bool]


class PluginExecutionNotReady(RuntimeError):
    """The task cannot safely be exposed to a model with the current handlers."""


class PluginToolPermissionError(PermissionError):
    """A model tool call violates the task's tool or argument permissions."""


def _function_name(tool_id: str) -> str:
    """Use the same deterministic provider-safe name mapping as the DHI runner."""
    name = re.sub(r"[^a-zA-Z0-9_-]", "_", tool_id)
    if not name or not re.match(r"^[a-zA-Z_]", name):
        name = f"tool_{name}"
    return name[:64]


def _schema_errors(schema: Any) -> list[str]:
    if not isinstance(schema, dict):
        return ["schema must be a JSON object"]
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        return [str(exc.message)]
    if schema.get("type") != "object":
        return ["tool argument schema must declare type=object"]
    if schema.get("additionalProperties") is not False:
        return ["tool argument schema must set additionalProperties=false"]
    return []


@dataclass(frozen=True)
class PreparedPluginExecution:
    """A validated set of model-visible tools and guarded dispatch capabilities."""

    task: PluginTaskPlan
    tool_schemas: tuple[dict[str, Any], ...]
    tool_name_by_id: dict[str, str]
    _tool_id_by_name: dict[str, str]
    _schemas_by_id: dict[str, dict[str, Any]]
    _handlers_by_id: dict[str, ToolHandler]
    _write_guards_by_id: dict[str, WriteGuard]

    def dispatch(self, function_name: str, arguments: dict[str, Any]) -> Any:
        """Validate and execute one model-selected function under task policy."""
        if not isinstance(function_name, str) or not function_name:
            raise PluginToolPermissionError("function name must be a non-empty string")
        tool_id = self._tool_id_by_name.get(function_name)
        if tool_id is None:
            raise PluginToolPermissionError(f"unknown or non-visible model function: {function_name!r}")
        if tool_id not in self.task.allowed_tool_ids:
            raise PluginToolPermissionError(f"tool {tool_id!r} is not allowed by task {self.task.task_id}")
        if not isinstance(arguments, dict):
            raise PluginToolPermissionError("tool arguments must be an object")

        schema = self._schemas_by_id.get(tool_id)
        if schema is None:
            raise PluginExecutionNotReady(f"missing schema for permitted tool {tool_id!r}")
        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        issues = sorted(
            validator.iter_errors(arguments),
            key=lambda issue: (tuple(str(x) for x in issue.absolute_path), issue.message),
        )
        if issues:
            details = "; ".join(
                f"{'/'.join(str(x) for x in issue.absolute_path) or '$'}: {issue.message}"
                for issue in issues[:5]
            )
            raise PluginToolPermissionError(
                f"schema validation failed for {tool_id!r}: {details}"
            )

        contract = self.task.tool_contracts.get(tool_id, {})
        if contract.get("side_effect_class") == "sandbox_write":
            guard = self._write_guards_by_id.get(tool_id)
            if not callable(guard):
                raise PluginExecutionNotReady(f"missing write guard for sandbox-write tool {tool_id!r}")
            try:
                permitted = guard(self.task, copy.deepcopy(arguments))
            except Exception as exc:
                raise PluginToolPermissionError(
                    f"write guard denied {tool_id!r}: {type(exc).__name__}: {exc}"
                ) from exc
            if permitted is not True:
                raise PluginToolPermissionError(
                    f"write guard denied {tool_id!r} for task {self.task.task_id}"
                )

        handler = self._handlers_by_id.get(tool_id)
        if not callable(handler):
            raise PluginExecutionNotReady(f"missing callable handler for permitted tool {tool_id!r}")
        return handler(copy.deepcopy(arguments))


def prepare_plugin_execution(
    task: PluginTaskPlan,
    *,
    schemas: Mapping[str, dict[str, Any]],
    handlers: Mapping[str, ToolHandler],
    write_guards: Mapping[str, WriteGuard] | None = None,
) -> PreparedPluginExecution:
    """Prepare one manifest task without invoking tools or a model.

    The schemas mapping is keyed by canonical registry ID and must cover every
    visible tool (including visible decoys) and every permitted tool. The caller
    is responsible for sourcing these schemas from a separately pinned provider
    contract. The handlers mapping may contain denied visible decoys, but only
    permitted tool IDs become callable. Every sandbox-write handler additionally
    requires a task-specific write_guards callback that checks exact arguments.
    """
    if not isinstance(task, PluginTaskPlan):
        raise PluginExecutionNotReady("task must be a validated PluginTaskPlan")
    if task.model_runs_allowed is not True:
        raise PluginExecutionNotReady(
            f"task {task.task_id} has model_runs_allowed=false; model execution is disabled"
        )

    visible_ids = tuple(task.visible_tool_ids)
    allowed_ids = tuple(task.allowed_tool_ids)
    required_ids = tuple(task.required_tool_ids)
    known_contract_ids = set(task.tool_contracts)

    if len(visible_ids) != len(set(visible_ids)):
        raise PluginExecutionNotReady("task visible tool inventory contains duplicate IDs")
    if len(allowed_ids) != len(set(allowed_ids)):
        raise PluginExecutionNotReady("task allowed tool inventory contains duplicate IDs")
    if not set(required_ids).issubset(allowed_ids):
        raise PluginExecutionNotReady("required task tools are not included in the permission allowlist")
    if not set(visible_ids).issubset(known_contract_ids):
        missing = sorted(set(visible_ids) - known_contract_ids)
        raise PluginExecutionNotReady(f"missing pinned registry contracts for visible tools: {missing}")
    if not set(allowed_ids).issubset(known_contract_ids):
        missing = sorted(set(allowed_ids) - known_contract_ids)
        raise PluginExecutionNotReady(f"missing pinned registry contracts for permitted tools: {missing}")

    if not isinstance(schemas, Mapping) or not isinstance(handlers, Mapping):
        raise PluginExecutionNotReady("schemas and handlers must be mappings keyed by canonical tool ID")
    guards = write_guards or {}
    if not isinstance(guards, Mapping):
        raise PluginExecutionNotReady("write_guards must be a mapping")

    schema_ids_required = set(visible_ids) | set(allowed_ids)
    missing_schemas = sorted(tool_id for tool_id in schema_ids_required if tool_id not in schemas)
    if missing_schemas:
        raise PluginExecutionNotReady(f"missing schema for tool(s): {missing_schemas}")

    schema_copy: dict[str, dict[str, Any]] = {}
    for tool_id in sorted(schema_ids_required):
        schema = copy.deepcopy(schemas[tool_id])
        errors = _schema_errors(schema)
        if errors:
            raise PluginExecutionNotReady(
                f"invalid schema for {tool_id!r}: {'; '.join(errors)}"
            )
        schema_copy[tool_id] = schema

    unexpected_handlers = sorted(set(handlers) - set(visible_ids))
    if unexpected_handlers:
        raise PluginExecutionNotReady(
            f"handler map contains tools not visible for this task: {unexpected_handlers}"
        )

    handler_copy: dict[str, ToolHandler] = {}
    for tool_id in allowed_ids:
        handler = handlers.get(tool_id)
        if not callable(handler):
            raise PluginExecutionNotReady(f"missing callable handler for permitted tool {tool_id!r}")
        handler_copy[tool_id] = handler

    unexpected_guards = sorted(set(guards) - set(allowed_ids))
    if unexpected_guards:
        raise PluginExecutionNotReady(
            f"write guard map contains tools not allowed for this task: {unexpected_guards}"
        )
    guard_copy: dict[str, WriteGuard] = {}
    for tool_id in allowed_ids:
        side_effect_class = task.tool_contracts[tool_id].get("side_effect_class")
        if side_effect_class == "sandbox_write":
            guard = guards.get(tool_id)
            if not callable(guard):
                raise PluginExecutionNotReady(f"missing write guard for sandbox-write tool {tool_id!r}")
            guard_copy[tool_id] = guard
        elif side_effect_class != "read_only":
            raise PluginExecutionNotReady(
                f"unsupported side-effect class for permitted tool {tool_id!r}: {side_effect_class!r}"
            )

    id_by_name: dict[str, str] = {}
    name_by_id: dict[str, str] = {}
    for tool_id in visible_ids:
        function_name = _function_name(tool_id)
        previous = id_by_name.get(function_name)
        if previous is not None:
            raise PluginExecutionNotReady(
                f"provider function-name collision: {previous!r} and {tool_id!r} map to {function_name!r}"
            )
        id_by_name[function_name] = tool_id
        name_by_id[tool_id] = function_name

    tool_schemas: list[dict[str, Any]] = []
    for tool_id in visible_ids:
        contract = task.tool_contracts[tool_id]
        description = contract.get("exact_contract_description")
        if not isinstance(description, str) or not description.strip():
            raise PluginExecutionNotReady(f"missing pinned provider contract description for {tool_id!r}")
        tool_schemas.append({
            "type": "function",
            "function": {
                "name": name_by_id[tool_id],
                "description": description,
                "parameters": copy.deepcopy(schema_copy[tool_id]),
            },
        })

    return PreparedPluginExecution(
        task=task,
        tool_schemas=tuple(tool_schemas),
        tool_name_by_id=dict(name_by_id),
        _tool_id_by_name=dict(id_by_name),
        _schemas_by_id=schema_copy,
        _handlers_by_id=handler_copy,
        _write_guards_by_id=guard_copy,
    )
