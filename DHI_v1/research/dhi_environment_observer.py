"""Read-only observations of the real DHIEnvironment for DHI-v1 research.

The adapter intentionally does not execute tools, discover tools, mutate task
state, or infer user consent from a permission-scope label.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any, Protocol

from .joint_state import (
    JointStateError,
    ObservedJointState,
    TaskWorldState,
    ToolEcosystemState,
    ToolState,
    WorldFact,
)


class DHIEnvironmentObservationSource(Protocol):
    """Small read-only interface required from the deterministic DHI environment."""

    @property
    def active_task_id(self) -> str | None: ...

    @property
    def active_task_allowed_tool_ids(self) -> tuple[str, ...] | None: ...

    @property
    def tool_catalogue_snapshot(self) -> tuple[dict[str, Any], ...]: ...

    @property
    def configured_tool_handler_ids(self) -> frozenset[str]: ...

    @property
    def workspace_snapshot_policy(self) -> dict[str, Any]: ...

    def list_tools(self, *, visible_only: bool = True) -> list[dict[str, Any]]: ...

    def snapshot(self) -> dict[str, str]: ...


_VALID_PERMISSION_STATES = frozenset({"granted", "denied", "requires_consent", "unknown"})
_CATALOGUE_POLICY_EXEMPT_TOOLS = frozenset({"catalog.search", "catalog.adaption_search"})


def _digest(payload: Any) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _optional_string_tuple(value: Any, *, field: str) -> tuple[str, ...] | None:
    if value is None:
        return None
    if not isinstance(value, (list, tuple)):
        raise JointStateError(f"{field} must be an array or None")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise JointStateError(f"{field} must contain non-empty strings")
    result = tuple(sorted(value))
    if len(result) != len(set(result)):
        raise JointStateError(f"{field} contains duplicate values")
    return result


def _permission_state(
    metadata: dict[str, Any],
    *,
    task_allowlist: tuple[str, ...] | None,
    tool_id: str,
) -> str:
    # An explicit task allowlist is an execution policy. Its denial is observable,
    # but the mere presence of permission_scope never means consent was granted.
    if (
        task_allowlist is not None
        and tool_id not in task_allowlist
        and tool_id not in _CATALOGUE_POLICY_EXEMPT_TOOLS
    ):
        return "denied"
    explicit = metadata.get("permission_state")
    return explicit if explicit in _VALID_PERMISSION_STATES else "unknown"


def _availability(
    metadata: dict[str, Any],
    *,
    tool_id: str,
    visible_ids: frozenset[str],
    handler_ids: frozenset[str],
    task_allowlist: tuple[str, ...] | None,
) -> str:
    requires_handler = metadata.get("requires_handler") is True or (
        tool_id == "catalog.adaption_search"
    )
    if requires_handler and tool_id not in handler_ids:
        return "disconnected"
    if (
        task_allowlist is not None
        and tool_id not in task_allowlist
        and tool_id not in _CATALOGUE_POLICY_EXEMPT_TOOLS
    ):
        return "unavailable"
    if metadata.get("requires_explicit_task_allowlist") is True and (
        task_allowlist is None or tool_id not in task_allowlist
    ):
        return "unavailable"
    if tool_id in visible_ids:
        return "callable"
    return "discoverable"


def observe_dhi_environment(
    env: DHIEnvironmentObservationSource,
    *,
    workspace_scope_id: str,
    catalogue_scope_id: str,
    observation_ref: str,
) -> ObservedJointState:
    """Capture complete workspace/catalogue snapshots without mutating the environment.

    The active task is mandatory because visible/discoverable/allowlisted status is
    task-dependent. The workspace snapshot inherits DHIEnvironment.snapshot()'s
    configured file-size, file-count, byte-count, and ignored-directory policy.
    The catalogue snapshot is the complete configured catalogue, not just the
    currently visible or handler-backed subset.
    """
    for field, value in (
        ("workspace_scope_id", workspace_scope_id),
        ("catalogue_scope_id", catalogue_scope_id),
        ("observation_ref", observation_ref),
    ):
        if not isinstance(value, str) or not value.strip():
            raise JointStateError(f"{field} must be a non-empty string")
    if env.active_task_id is None:
        raise JointStateError("an active task is required to observe task-scoped tool availability")

    workspace_snapshot = env.snapshot()
    if not isinstance(workspace_snapshot, dict):
        raise JointStateError("DHIEnvironment.snapshot() must return a path-to-SHA256 mapping")
    world_facts: list[WorldFact] = []
    for path, file_hash in sorted(workspace_snapshot.items()):
        if not isinstance(path, str) or not path:
            raise JointStateError("workspace snapshot contains an invalid relative path")
        if not isinstance(file_hash, str) or len(file_hash) != 64:
            raise JointStateError(f"workspace snapshot contains an invalid SHA-256 for {path!r}")
        try:
            int(file_hash, 16)
        except ValueError as exc:
            raise JointStateError(f"workspace snapshot contains an invalid SHA-256 for {path!r}") from exc
        world_facts.append(WorldFact(f"file:{path}", file_hash.lower()))

    catalogue = env.tool_catalogue_snapshot
    if not isinstance(catalogue, tuple):
        raise JointStateError("tool_catalogue_snapshot must be a complete tuple")
    visible = env.list_tools(visible_only=True)
    if not isinstance(visible, list):
        raise JointStateError("list_tools(visible_only=True) must return a list")
    visible_ids = frozenset(
        item.get("tool_id") for item in visible if isinstance(item, dict)
    )
    if any(not isinstance(tool_id, str) or not tool_id for tool_id in visible_ids):
        raise JointStateError("visible tool inventory contains an invalid tool ID")
    handler_ids = env.configured_tool_handler_ids
    if not isinstance(handler_ids, frozenset):
        raise JointStateError("configured_tool_handler_ids must be a frozenset")
    task_allowlist = env.active_task_allowed_tool_ids
    if task_allowlist is not None and not isinstance(task_allowlist, tuple):
        raise JointStateError("active task allowlist must be a tuple or None")

    tools: list[ToolState] = []
    for item in catalogue:
        if not isinstance(item, dict):
            raise JointStateError("tool catalogue contains a non-object entry")
        tool_id = item.get("tool_id")
        if not isinstance(tool_id, str) or not tool_id.strip():
            raise JointStateError("tool catalogue entry is missing tool_id")

        input_schema = item.get("input_schema")
        schema_hash = _digest(input_schema) if isinstance(input_schema, dict) else None
        capabilities = _optional_string_tuple(item.get("tags"), field=f"{tool_id}.tags")
        scope = item.get("permission_scope")
        permissions = (scope,) if isinstance(scope, str) and scope.strip() else None
        raw_effects = item.get("side_effects")
        if isinstance(raw_effects, str) and raw_effects.strip():
            side_effects = (raw_effects,)
        else:
            side_effects = _optional_string_tuple(
                raw_effects, field=f"{tool_id}.side_effects"
            )
        tools.append(ToolState(
            tool_id=tool_id,
            schema_sha256=schema_hash,
            capabilities=capabilities,
            availability=_availability(
                item,
                tool_id=tool_id,
                visible_ids=visible_ids,
                handler_ids=handler_ids,
                task_allowlist=task_allowlist,
            ),
            permission_state=_permission_state(
                item,
                task_allowlist=task_allowlist,
                tool_id=tool_id,
            ),
            permissions=permissions,
            side_effects=side_effects,
        ))

    world_payload = [(fact.key, fact.value) for fact in world_facts]
    tool_payload = [
        (
            tool.tool_id, tool.schema_sha256, tool.capabilities, tool.availability,
            tool.permission_state, tool.permissions, tool.side_effects,
        )
        for tool in sorted(tools, key=lambda item: item.tool_id)
    ]
    snapshot_policy = env.workspace_snapshot_policy
    if not isinstance(snapshot_policy, dict):
        raise JointStateError("workspace_snapshot_policy must return an object")
    effective_workspace_scope = (
        f"{workspace_scope_id}|snapshot-policy:{_digest(snapshot_policy)}"
    )
    task_state = TaskWorldState(
        revision=_digest(world_payload),
        scope_id=effective_workspace_scope,
        complete_snapshot=True,
        facts=tuple(world_facts),
        observation_ref=f"{observation_ref}#workspace",
    )
    ecosystem_state = ToolEcosystemState(
        revision=_digest({
            "task_id": env.active_task_id,
            "allowed_tool_ids": task_allowlist,
            "tools": tool_payload,
        }),
        scope_id=catalogue_scope_id,
        complete_snapshot=True,
        tools=tuple(tools),
        observation_ref=f"{observation_ref}#tool-catalogue",
    )
    return ObservedJointState(task=task_state, ecosystem=ecosystem_state)
