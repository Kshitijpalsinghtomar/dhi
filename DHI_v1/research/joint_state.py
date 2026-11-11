"""Observed joint-state diffs and scoring for the DHI-v1 research hypothesis.

This is a measurement contract, not a learned model, planner, runtime adapter, or
capability result. Observations and model forecasts remain separate.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Literal

Availability = Literal["callable", "discoverable", "disconnected", "unavailable", "unknown"]
PermissionState = Literal["granted", "denied", "requires_consent", "unknown"]


class JointStateError(ValueError):
    """An observation or forecast is ambiguous or invalid."""


def _text(value: str, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise JointStateError(f"{field} must be a non-empty string")
    return value.strip()


def _string_set(values: tuple[str, ...] | None, field: str) -> tuple[str, ...] | None:
    if values is None:
        return None
    if not isinstance(values, tuple):
        raise JointStateError(f"{field} must be a tuple or None (unknown)")
    cleaned = tuple(_text(item, field) for item in values)
    if len(cleaned) != len(set(cleaned)):
        raise JointStateError(f"{field} contains duplicates")
    return tuple(sorted(cleaned))


def _set_json(values: tuple[str, ...] | None) -> str | None:
    return None if values is None else json.dumps(list(values), separators=(",", ":"))


@dataclass(frozen=True, order=True)
class WorldFact:
    key: str
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "key", _text(self.key, "fact.key"))
        object.__setattr__(self, "value", _text(self.value, "fact.value"))


@dataclass(frozen=True)
class TaskWorldState:
    revision: str
    scope_id: str
    complete_snapshot: bool
    facts: tuple[WorldFact, ...]
    observation_ref: str

    def __post_init__(self) -> None:
        for field in ("revision", "scope_id", "observation_ref"):
            object.__setattr__(self, field, _text(getattr(self, field), f"task.{field}"))
        if not isinstance(self.complete_snapshot, bool):
            raise JointStateError("task.complete_snapshot must be boolean")
        if not isinstance(self.facts, tuple) or any(not isinstance(x, WorldFact) for x in self.facts):
            raise JointStateError("task.facts must be a tuple of WorldFact")
        keys = [fact.key for fact in self.facts]
        if len(keys) != len(set(keys)):
            raise JointStateError("task.facts contains duplicate keys")


@dataclass(frozen=True)
class ToolState:
    tool_id: str
    schema_sha256: str | None
    capabilities: tuple[str, ...] | None
    availability: Availability
    permission_state: PermissionState
    permissions: tuple[str, ...] | None = None
    side_effects: tuple[str, ...] | None = None
    required_permission_scopes: tuple[str, ...] | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "tool_id", _text(self.tool_id, "tool.tool_id"))
        if self.schema_sha256 is not None and (
            not isinstance(self.schema_sha256, str)
            or not re.fullmatch(r"[0-9a-f]{64}", self.schema_sha256)
        ):
            raise JointStateError("tool.schema_sha256 must be a lowercase SHA-256 digest or None")
        if not isinstance(self.availability, str) or self.availability not in {
            "callable", "discoverable", "disconnected", "unavailable", "unknown"
        }:
            raise JointStateError("tool.availability is unsupported")
        if not isinstance(self.permission_state, str) or self.permission_state not in {
            "granted", "denied", "requires_consent", "unknown"
        }:
            raise JointStateError("tool.permission_state is unsupported")
        for field in ("capabilities", "permissions", "side_effects", "required_permission_scopes"):
            object.__setattr__(self, field, _string_set(getattr(self, field), f"tool.{field}"))


@dataclass(frozen=True)
class ToolEcosystemState:
    revision: str
    scope_id: str
    complete_snapshot: bool
    tools: tuple[ToolState, ...]
    observation_ref: str

    def __post_init__(self) -> None:
        for field in ("revision", "scope_id", "observation_ref"):
            object.__setattr__(self, field, _text(getattr(self, field), f"ecosystem.{field}"))
        if not isinstance(self.complete_snapshot, bool):
            raise JointStateError("ecosystem.complete_snapshot must be boolean")
        if not isinstance(self.tools, tuple) or any(not isinstance(x, ToolState) for x in self.tools):
            raise JointStateError("ecosystem.tools must be a tuple of ToolState")
        ids = [tool.tool_id for tool in self.tools]
        if len(ids) != len(set(ids)):
            raise JointStateError("ecosystem.tools contains duplicate tool IDs")


@dataclass(frozen=True)
class ObservedJointState:
    task: TaskWorldState
    ecosystem: ToolEcosystemState

    def __post_init__(self) -> None:
        if not isinstance(self.task, TaskWorldState) or not isinstance(self.ecosystem, ToolEcosystemState):
            raise JointStateError("joint state requires task and ecosystem observations")


@dataclass(frozen=True, order=True)
class WorldChange:
    operation: Literal["add", "remove", "update"]
    key: str
    before: str | None
    after: str | None

    def __post_init__(self) -> None:
        if not isinstance(self.operation, str) or self.operation not in {"add", "remove", "update"}:
            raise JointStateError("world change operation must be add, remove, or update")
        object.__setattr__(self, "key", _text(self.key, "world_change.key"))
        for field in ("before", "after"):
            value = getattr(self, field)
            if value is not None:
                object.__setattr__(self, field, _text(value, f"world_change.{field}"))
        valid = (
            self.operation == "add" and self.before is None and self.after is not None
            or self.operation == "remove" and self.before is not None and self.after is None
            or self.operation == "update" and self.before is not None and self.after is not None
            and self.before != self.after
        )
        if not valid:
            raise JointStateError("world change before/after values do not match its operation")


@dataclass(frozen=True, order=True)
class ToolChange:
    tool_id: str
    field: str
    before: str | None
    after: str | None

    def __post_init__(self) -> None:
        object.__setattr__(self, "tool_id", _text(self.tool_id, "tool_change.tool_id"))
        object.__setattr__(self, "field", _text(self.field, "tool_change.field"))
        for field in ("before", "after"):
            value = getattr(self, field)
            if value is not None:
                object.__setattr__(self, field, _text(value, f"tool_change.{field}"))
        if self.before == self.after:
            raise JointStateError("tool change must describe an actual difference")


@dataclass(frozen=True)
class JointStateDelta:
    world_changes: tuple[WorldChange, ...]
    tool_changes: tuple[ToolChange, ...]


@dataclass(frozen=True)
class PredictedJointEffects:
    # None = no forecast supplied; () = explicit prediction of no change.
    world_changes: tuple[WorldChange, ...] | None = None
    tool_changes: tuple[ToolChange, ...] | None = None

    def __post_init__(self) -> None:
        for field, changes, kind in (
            ("world_changes", self.world_changes, WorldChange),
            ("tool_changes", self.tool_changes, ToolChange),
        ):
            if changes is not None:
                if not isinstance(changes, tuple) or any(not isinstance(x, kind) for x in changes):
                    raise JointStateError(f"prediction.{field} contains an invalid record")
                if len(changes) != len(set(changes)):
                    raise JointStateError(f"prediction.{field} contains duplicates")


@dataclass(frozen=True)
class DimensionScore:
    status: Literal["scored", "not_predicted"]
    true_positive: int | None
    false_positive: int | None
    false_negative: int | None
    precision: float | None
    recall: float | None
    f1: float | None
    exact_match: bool | None
    missed: tuple[WorldChange | ToolChange, ...] = ()
    unexpected: tuple[WorldChange | ToolChange, ...] = ()


@dataclass(frozen=True)
class JointEffectsScore:
    world: DimensionScore
    ecosystem: DimensionScore
    actual: JointStateDelta


def _require_comparable(before: ObservedJointState, after: ObservedJointState) -> None:
    for left, right, label in (
        (before.task, after.task, "task/world"),
        (before.ecosystem, after.ecosystem, "tool-ecosystem"),
    ):
        if left.scope_id != right.scope_id:
            raise JointStateError(f"{label} snapshots have different scope IDs")
        if not left.complete_snapshot or not right.complete_snapshot:
            raise JointStateError(f"cannot infer additions/removals from incomplete {label} snapshots")


def diff_joint_state(before: ObservedJointState, after: ObservedJointState) -> JointStateDelta:
    """Compute observed changes separately; partial or mismatched scopes fail closed."""
    if not isinstance(before, ObservedJointState) or not isinstance(after, ObservedJointState):
        raise JointStateError("before and after must be ObservedJointState records")
    _require_comparable(before, after)
    old_facts = {fact.key: fact.value for fact in before.task.facts}
    new_facts = {fact.key: fact.value for fact in after.task.facts}
    world: list[WorldChange] = []
    for key in sorted(old_facts.keys() | new_facts.keys()):
        old, new = old_facts.get(key), new_facts.get(key)
        if old is None:
            world.append(WorldChange("add", key, None, new))
        elif new is None:
            world.append(WorldChange("remove", key, old, None))
        elif old != new:
            world.append(WorldChange("update", key, old, new))

    old_tools = {tool.tool_id: tool for tool in before.ecosystem.tools}
    new_tools = {tool.tool_id: tool for tool in after.ecosystem.tools}
    tool_changes: list[ToolChange] = []
    for tool_id in sorted(old_tools.keys() | new_tools.keys()):
        old, new = old_tools.get(tool_id), new_tools.get(tool_id)
        if old is None:
            tool_changes.append(ToolChange(tool_id, "presence", None, "present"))
        elif new is None:
            tool_changes.append(ToolChange(tool_id, "presence", "present", None))
        else:
            fields = {
                "schema_sha256": (old.schema_sha256, new.schema_sha256),
                "capabilities": (_set_json(old.capabilities), _set_json(new.capabilities)),
                "availability": (old.availability, new.availability),
                "permission_state": (old.permission_state, new.permission_state),
                "permissions": (_set_json(old.permissions), _set_json(new.permissions)),
                "side_effects": (_set_json(old.side_effects), _set_json(new.side_effects)),
                "required_permission_scopes": (
                    _set_json(old.required_permission_scopes),
                    _set_json(new.required_permission_scopes),
                ),
            }
            for field, (before_value, after_value) in sorted(fields.items()):
                if before_value != after_value:
                    tool_changes.append(ToolChange(tool_id, field, before_value, after_value))
    return JointStateDelta(tuple(world), tuple(tool_changes))


def _score(
    predicted: tuple[WorldChange, ...] | tuple[ToolChange, ...] | None,
    actual: tuple[WorldChange, ...] | tuple[ToolChange, ...],
) -> DimensionScore:
    if predicted is None:
        return DimensionScore("not_predicted", None, None, None, None, None, None, None)
    p, a = set(predicted), set(actual)
    tp, fp, fn = len(p & a), len(p - a), len(a - p)
    precision = tp / (tp + fp) if tp + fp else (1.0 if fn == 0 else None)
    recall = tp / (tp + fn) if tp + fn else (1.0 if fp == 0 else None)
    f1 = 0.0 if precision is None or recall is None or precision + recall == 0 else 2 * precision * recall / (precision + recall)
    return DimensionScore(
        "scored", tp, fp, fn, precision, recall, f1, p == a,
        tuple(sorted(a - p)), tuple(sorted(p - a)),
    )


def score_joint_effects(
    prediction: PredictedJointEffects,
    before: ObservedJointState,
    after: ObservedJointState,
) -> JointEffectsScore:
    """Score forecasts against independently observed state differences.

    An omitted forecast is unscored; an empty tuple is scored as a no-change
    prediction. The world and ecosystem dimensions are never collapsed.
    """
    if not isinstance(prediction, PredictedJointEffects):
        raise JointStateError("prediction must be PredictedJointEffects")
    actual = diff_joint_state(before, after)
    return JointEffectsScore(
        _score(prediction.world_changes, actual.world_changes),
        _score(prediction.tool_changes, actual.tool_changes),
        actual,
    )
