"""Load plugin-native ORBIT tasks against their pinned tool registry.

This module builds a validated, read-only execution plan. It does not invoke
providers, enable model runs, or turn a scripted reference into model evidence.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class PluginTaskLoadError(ValueError):
    """Raised when a manifest task cannot be safely resolved against its registry."""


@dataclass(frozen=True)
class PluginTaskPlan:
    task_id: str
    stage: str
    stratum_id: str
    prompt: str
    goal: str
    visible_tool_ids: tuple[str, ...]
    discoverable_tool_ids: tuple[str, ...]
    required_tool_ids: tuple[str, ...]
    allowed_tool_ids: tuple[str, ...]
    allowed_side_effects: tuple[str, ...]
    forbidden_side_effects: tuple[str, ...]
    tool_contracts: dict[str, dict[str, Any]]
    environment: dict[str, Any]
    horizon: dict[str, Any]
    preconditions: tuple[dict[str, Any], ...]
    postconditions: tuple[dict[str, Any], ...]
    model_runs_allowed: bool
    execution_status: str
    max_model_turns: int
    max_tool_calls: int
    trial_seeds: tuple[int, ...]
    task_instance_sha256: str
    task_manifest_sha256: str
    registry_schema_sha256: str

    @property
    def execution_authorized(self) -> bool:
        """Whether the manifest explicitly permits model execution for this task."""
        return self.model_runs_allowed

    @property
    def visible_but_denied_tool_ids(self) -> tuple[str, ...]:
        """Visible decoys that must not pass the runtime permission gate."""
        allowed = set(self.allowed_tool_ids)
        return tuple(tool_id for tool_id in self.visible_tool_ids if tool_id not in allowed)


def _read_json(path: str | Path, label: str) -> tuple[dict[str, Any], bytes]:
    file_path = Path(path)
    try:
        raw = file_path.read_bytes()
    except OSError as exc:
        raise PluginTaskLoadError(f"cannot read {label} file: {file_path}") from exc
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise PluginTaskLoadError(f"{label} file is not valid UTF-8 JSON: {file_path}") from exc
    if not isinstance(value, dict):
        raise PluginTaskLoadError(f"{label} root must be a JSON object")
    return value, raw


def _string_list(value: Any, field: str, *, allow_empty: bool = True) -> tuple[str, ...]:
    if not isinstance(value, list) or (not allow_empty and not value):
        raise PluginTaskLoadError(f"{field} must be a {'non-empty ' if not allow_empty else ''}array")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise PluginTaskLoadError(f"{field} must contain only non-empty strings")
    if len(value) != len(set(value)):
        raise PluginTaskLoadError(f"{field} contains duplicate values")
    return tuple(value)


READ_ONLY_POLICY_EFFECTS = frozenset({
    "free_tool_catalogue_discovery",
    "public_web_read",
    "read_github_fixture",
    "read_only_plugin_calls",
    "read_only_policy_and_provider_discovery",
})


def _policy_allows(side_effect_class: str, allowed_side_effects: tuple[str, ...]) -> bool:
    """Map explicit task policy labels to the pinned registry side-effect classes.

    A read-only action is visible to the policy gate only when the task declares
    an explicit read/discovery permission, or when it is part of a declared
    create/update workflow that must first read source state. An unrelated
    permission (for example, a purchase) must not accidentally grant reads.

    Sandbox writes require a create_* or update_* policy action. Delete, merge,
    deployment and other side effects are never authorized by this mapping.
    """
    policy = set(allowed_side_effects)
    declares_read = bool(policy & READ_ONLY_POLICY_EFFECTS)
    declares_write_workflow = any(
        action.startswith(("create_", "update_"))
        for action in policy
    )
    if side_effect_class == "read_only":
        return declares_read or declares_write_workflow
    if side_effect_class == "sandbox_write":
        return declares_write_workflow
    raise PluginTaskLoadError(
        f"unknown registry side_effect_class {side_effect_class!r}; refusing to fail open"
    )


def _registry_index(registry: dict[str, Any]) -> tuple[dict[str, dict[str, Any]], str]:
    tools = registry.get("tools")
    if not isinstance(tools, list):
        raise PluginTaskLoadError("registry.tools must be an array")
    index: dict[str, dict[str, Any]] = {}
    for item in tools:
        if not isinstance(item, dict):
            raise PluginTaskLoadError("registry.tools entries must be objects")
        tool_id = item.get("tool_id")
        if not isinstance(tool_id, str) or not tool_id:
            raise PluginTaskLoadError("registry tool is missing a non-empty tool_id")
        if tool_id in index:
            raise PluginTaskLoadError(f"duplicate tool_id in registry: {tool_id}")
        index[tool_id] = item
    fingerprint = registry.get("tool_schema_sha256")
    if not isinstance(fingerprint, str) or len(fingerprint) != 64:
        raise PluginTaskLoadError("registry tool_schema_sha256 must be a SHA-256 hex string")
    try:
        int(fingerprint, 16)
    except ValueError as exc:
        raise PluginTaskLoadError("registry tool_schema_sha256 must be hexadecimal") from exc
    return index, fingerprint


def _build_plan(
    task: dict[str, Any],
    task_index: dict[str, dict[str, Any]],
    registry_fingerprint: str,
    manifest_sha256: str,
) -> PluginTaskPlan:
    task_id = task.get("task_id")
    if not isinstance(task_id, str) or not task_id:
        raise PluginTaskLoadError("task is missing a non-empty task_id")

    contract = task.get("task_contract")
    if not isinstance(contract, dict):
        raise PluginTaskLoadError(f"{task_id}: task_contract must be an object")
    prompt = contract.get("prompt")
    goal = contract.get("goal")
    if not isinstance(prompt, str) or not prompt.strip():
        raise PluginTaskLoadError(f"{task_id}: task prompt is required")
    if not isinstance(goal, str) or not goal.strip():
        raise PluginTaskLoadError(f"{task_id}: task goal is required")

    inventory = task.get("tool_inventory")
    if not isinstance(inventory, dict):
        raise PluginTaskLoadError(f"{task_id}: tool_inventory must be an object")
    visible = _string_list(inventory.get("visible_tool_ids"), f"{task_id}.visible_tool_ids")
    discoverable = _string_list(
        inventory.get("discoverable_tool_ids"), f"{task_id}.discoverable_tool_ids"
    )
    required = _string_list(inventory.get("required_tool_ids"), f"{task_id}.required_tool_ids")
    if set(visible) & set(discoverable):
        raise PluginTaskLoadError(f"{task_id}: visible and discoverable tool IDs overlap")
    registry_references = set(visible) | set(discoverable) | set(required)
    for tool_id in sorted(registry_references):
        registry_item = task_index.get(tool_id)
        if registry_item is None:
            raise PluginTaskLoadError(
                f"{task_id}: tool {tool_id!r} is not present in the pinned registry"
            )
        if registry_item.get("allowed_in_benchmark") is not True:
            raise PluginTaskLoadError(
                f"{task_id}: tool {tool_id!r} is not allowed in the benchmark"
            )

    offered_ids = set(visible) | set(discoverable)
    missing_required = set(required) - offered_ids
    if missing_required:
        raise PluginTaskLoadError(
            f"{task_id}: required tool IDs are not visible or discoverable: {sorted(missing_required)}"
        )

    task_fingerprint = inventory.get("tool_schema_sha256")
    if task_fingerprint != registry_fingerprint:
        raise PluginTaskLoadError(
            f"{task_id}: schema fingerprint mismatch between task and pinned registry"
        )

    policy = task.get("policy")
    if not isinstance(policy, dict):
        raise PluginTaskLoadError(f"{task_id}: policy must be an object")
    allowed_side_effects = _string_list(
        policy.get("allowed_side_effects"), f"{task_id}.allowed_side_effects"
    )
    forbidden_side_effects = _string_list(
        policy.get("forbidden_side_effects"), f"{task_id}.forbidden_side_effects"
    )

    referenced_ids = visible + discoverable
    contracts: dict[str, dict[str, Any]] = {}
    allowed_ids: list[str] = []
    for tool_id in referenced_ids:
        registry_item = task_index.get(tool_id)
        if registry_item is None:
            raise PluginTaskLoadError(
                f"{task_id}: tool {tool_id!r} is not present in the pinned registry"
            )
        if registry_item.get("allowed_in_benchmark") is not True:
            raise PluginTaskLoadError(
                f"{task_id}: tool {tool_id!r} is not allowed in the benchmark"
            )
        side_effect_class = registry_item.get("side_effect_class")
        contracts[tool_id] = dict(registry_item)
        if _policy_allows(side_effect_class, allowed_side_effects):
            allowed_ids.append(tool_id)

    denied_required = set(required) - set(allowed_ids)
    if denied_required:
        raise PluginTaskLoadError(
            f"{task_id}: required tools exceed task side-effect permissions: {sorted(denied_required)}"
        )

    execution = task.get("execution")
    if not isinstance(execution, dict):
        raise PluginTaskLoadError(f"{task_id}: execution must be an object")
    model_runs_allowed = execution.get("model_runs_allowed")
    if not isinstance(model_runs_allowed, bool):
        raise PluginTaskLoadError(f"{task_id}: execution.model_runs_allowed must be boolean")
    execution_status = execution.get("status")
    if not isinstance(execution_status, str) or not execution_status:
        raise PluginTaskLoadError(f"{task_id}: execution.status is required")

    def positive_int(field: str) -> int:
        value = execution.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise PluginTaskLoadError(f"{task_id}: execution.{field} must be a positive integer")
        return value

    trial_seeds = execution.get("trial_seeds")
    if not isinstance(trial_seeds, list) or any(
        not isinstance(seed, int) or isinstance(seed, bool) or seed < 0
        for seed in trial_seeds
    ):
        raise PluginTaskLoadError(f"{task_id}: execution.trial_seeds must be non-negative integers")

    environment = task.get("environment")
    horizon = task.get("horizon")
    preconditions = task.get("preconditions")
    postconditions = task.get("postconditions")
    if not isinstance(environment, dict) or not isinstance(horizon, dict):
        raise PluginTaskLoadError(f"{task_id}: environment and horizon must be objects")
    if not isinstance(preconditions, list) or not isinstance(postconditions, list):
        raise PluginTaskLoadError(f"{task_id}: preconditions and postconditions must be arrays")

    instance_hash = task.get("split_metadata", {}).get("task_instance_sha256")
    if not isinstance(instance_hash, str) or len(instance_hash) != 64:
        raise PluginTaskLoadError(f"{task_id}: task_instance_sha256 must be present")
    try:
        int(instance_hash, 16)
    except ValueError as exc:
        raise PluginTaskLoadError(f"{task_id}: task_instance_sha256 must be hexadecimal") from exc

    for field in ("stage", "stratum_id"):
        if not isinstance(task.get(field), str) or not task[field]:
            raise PluginTaskLoadError(f"{task_id}: {field} is required")

    return PluginTaskPlan(
        task_id=task_id,
        stage=task["stage"],
        stratum_id=task["stratum_id"],
        prompt=prompt,
        goal=goal,
        visible_tool_ids=visible,
        discoverable_tool_ids=discoverable,
        required_tool_ids=required,
        allowed_tool_ids=tuple(allowed_ids),
        allowed_side_effects=allowed_side_effects,
        forbidden_side_effects=forbidden_side_effects,
        tool_contracts=contracts,
        environment=dict(environment),
        horizon=dict(horizon),
        preconditions=tuple(dict(item) for item in preconditions),
        postconditions=tuple(dict(item) for item in postconditions),
        model_runs_allowed=model_runs_allowed,
        execution_status=execution_status,
        max_model_turns=positive_int("max_model_turns"),
        max_tool_calls=positive_int("max_tool_calls"),
        trial_seeds=tuple(trial_seeds),
        task_instance_sha256=instance_hash,
        task_manifest_sha256=manifest_sha256,
        registry_schema_sha256=registry_fingerprint,
    )


def load_plugin_task(
    manifest_path: str | Path,
    registry_path: str | Path,
    task_id: str,
) -> PluginTaskPlan:
    """Load one manifest task and fail closed on registry/policy inconsistencies."""
    if not isinstance(task_id, str) or not task_id.strip():
        raise PluginTaskLoadError("task_id must be a non-empty string")
    manifest, manifest_bytes = _read_json(manifest_path, "task manifest")
    registry, _ = _read_json(registry_path, "tool registry")
    tasks = manifest.get("tasks")
    if not isinstance(tasks, list):
        raise PluginTaskLoadError("task manifest.tasks must be an array")
    matches = [task for task in tasks if isinstance(task, dict) and task.get("task_id") == task_id]
    if len(matches) != 1:
        raise PluginTaskLoadError(
            f"expected exactly one task with task_id {task_id!r}; found {len(matches)}"
        )
    index, fingerprint = _registry_index(registry)
    return _build_plan(
        matches[0],
        index,
        fingerprint,
        hashlib.sha256(manifest_bytes).hexdigest(),
    )


def load_all_plugin_tasks(
    manifest_path: str | Path,
    registry_path: str | Path,
) -> list[PluginTaskPlan]:
    """Load all manifest tasks in order, rejecting duplicate IDs and unsafe contracts."""
    manifest, manifest_bytes = _read_json(manifest_path, "task manifest")
    registry, _ = _read_json(registry_path, "tool registry")
    tasks = manifest.get("tasks")
    if not isinstance(tasks, list) or not tasks:
        raise PluginTaskLoadError("task manifest.tasks must be a non-empty array")
    task_ids = [
        task.get("task_id") if isinstance(task, dict) else None
        for task in tasks
    ]
    if any(not isinstance(task_id, str) or not task_id for task_id in task_ids):
        raise PluginTaskLoadError("every task must have a non-empty task_id")
    if len(task_ids) != len(set(task_ids)):
        raise PluginTaskLoadError("task manifest contains duplicate task_id values")
    index, fingerprint = _registry_index(registry)
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    return [
        _build_plan(task, index, fingerprint, manifest_sha256)
        for task in tasks
    ]
