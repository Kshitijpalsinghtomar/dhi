"""Deterministic, file-backed tool environment for the DHI-v1 pilot.

This is a development harness, not an OS security sandbox. It exposes a small
allowlisted set of filesystem tools and never executes arbitrary shell/Python
commands supplied by an agent.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Iterable

TRACE_SCHEMA_VERSION = "dhi.trajectory.v1"
DEFAULT_MAX_FILE_BYTES = 10_000_000
DEFAULT_IGNORED_DIRS = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}


class DHIEnvironmentError(Exception):
    """An expected, task-visible environment/tool error."""


@dataclass
class TaskSpec:
    task_id: str
    prompt: str
    goal: str
    hard_constraints: list[str] = field(default_factory=list)
    preferences: list[str] = field(default_factory=list)
    postconditions: list[dict[str, Any]] = field(default_factory=list)
    protected_paths: list[str] = field(default_factory=list)
    allowed_tool_ids: list[str] | None = None
    visible_tool_ids: list[str] | None = None
    fault_injections: list[dict[str, Any]] = field(default_factory=list)
    environment_version: str = "dhi-file-workspace.v1"
    split: str = "development"
    metadata: dict[str, Any] = field(default_factory=dict)
    trajectory_id: str | None = None

    def __post_init__(self) -> None:
        if not self.task_id.strip():
            raise ValueError("task_id is required")
        if not self.prompt.strip():
            raise ValueError("prompt is required")
        if not self.goal.strip():
            raise ValueError("goal is required")
        if not self.postconditions:
            raise ValueError("at least one explicit postcondition is required")
        if self.trajectory_id is None:
            self.trajectory_id = self.task_id
        elif not self.trajectory_id.strip():
            raise ValueError("trajectory_id must not be empty")


@dataclass
class ActionResult:
    ok: bool
    tool_id: str
    result: dict[str, Any] | list[Any] | None
    error: str | None
    actual_effects: dict[str, Any]
    prediction_comparison: dict[str, Any]
    event: dict[str, Any]


DEFAULT_TOOL_CATALOGUE: list[dict[str, Any]] = [
    {
        "tool_id": "catalog.search",
        "name": "Discover tools by capability",
        "description": "Search the full tool catalogue for tools matching a natural-language capability description.",
        "tags": ["catalogue", "discover", "discovery", "find", "search", "tools", "capabilities", "apps", "connectors"],
        "input_schema": {"type": "object", "required": ["query"], "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 10}}, "additionalProperties": False},
        "side_effects": "read_only",
        "permission_scope": "catalogue_read",
        "preconditions": ["tool catalogue is available"],
        "cost_class": "local_low",
        "reversible": True,
    },
    {
        "tool_id": "catalog.adaption_search",
        "name": "Search connected Adaption app and connector catalogue",
        "description": (
            "Search the live Adaption connector catalogue for external capabilities "
            "and inspect their availability, auth requirements, permissions and approval defaults. "
            "Read-only discovery; this tool does not execute any external connector action."
        ),
        "tags": ["adaption", "external", "catalogue", "connector", "integration", "app", "plugin", "mcp", "discover", "availability", "permission"],
        "input_schema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string"},
                "available_only": {"type": "boolean", "default": true},
                "limit": {"type": "integer", "default": 10},
            },
            "additionalProperties": false,
        },
        "side_effects": "read_only",
        "permission_scope": "connector_catalogue_read",
        "preconditions": ["Adaption Responses client is configured"],
        "cost_class": "external_api_request_cost_unverified",
        "reversible": true,
        "execution_boundary": "catalogue_discovery_only",
    },
    {
        "tool_id": "fs.list_files",
        "name": "List workspace files",
        "description": "List files under a workspace-relative directory.",
        "tags": ["filesystem", "directory", "inspect", "files", "workspace"],
        "input_schema": {"type": "object", "properties": {"path": {"type": "string", "default": ""}}, "additionalProperties": False},
        "side_effects": "read_only",
        "permission_scope": "workspace_read",
        "preconditions": ["workspace exists"],
        "cost_class": "local_low",
        "reversible": True,
    },
    {
        "tool_id": "fs.read_file",
        "name": "Read a text file",
        "description": "Read UTF-8 text from a workspace-relative file.",
        "tags": ["filesystem", "file", "read", "inspect", "text", "source code"],
        "input_schema": {"type": "object", "required": ["path"], "properties": {"path": {"type": "string"}}, "additionalProperties": False},
        "side_effects": "read_only",
        "permission_scope": "workspace_read",
        "preconditions": ["file exists and is UTF-8"],
        "cost_class": "local_low",
        "reversible": True,
    },
    {
        "tool_id": "fs.write_file",
        "name": "Write a text file",
        "description": "Create or replace UTF-8 text in a workspace-relative file.",
        "tags": ["filesystem", "file", "write", "create", "edit", "text", "source code"],
        "input_schema": {"type": "object", "required": ["path", "content"], "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "additionalProperties": False},
        "side_effects": "workspace_write",
        "permission_scope": "workspace_write",
        "preconditions": ["target path remains inside workspace", "parent directory exists"],
        "cost_class": "local_low",
        "reversible": True,
    },
    {
        "tool_id": "fs.append_file",
        "name": "Append to a text file",
        "description": "Append UTF-8 text to an existing workspace-relative file.",
        "tags": ["filesystem", "file", "append", "write", "edit", "text"],
        "input_schema": {"type": "object", "required": ["path", "content"], "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "additionalProperties": False},
        "side_effects": "workspace_write",
        "permission_scope": "workspace_write",
        "preconditions": ["file exists and remains inside workspace"],
        "cost_class": "local_low",
        "reversible": True,
    },
    {
        "tool_id": "fs.search_text",
        "name": "Search text in files",
        "description": "Search UTF-8 files for a literal text query and return matching line numbers.",
        "tags": ["filesystem", "file", "search", "find", "grep", "query", "text", "source code"],
        "input_schema": {"type": "object", "required": ["query"], "properties": {"query": {"type": "string"}, "path": {"type": "string", "default": ""}, "case_sensitive": {"type": "boolean", "default": False}}, "additionalProperties": False},
        "side_effects": "read_only",
        "permission_scope": "workspace_read",
        "preconditions": ["search root exists"],
        "cost_class": "local_low",
        "reversible": True,
    },
]


class DHIEnvironment:
    """A deterministic workspace tool environment with JSONL trajectory logging."""

    def __init__(
        self,
        workspace: str | Path,
        *,
        trace_path: str | Path | None = None,
        visible_tool_ids: Iterable[str] | None = None,
        max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
        max_snapshot_files: int = 5000,
        max_snapshot_bytes: int = 100_000_000,
        ignored_dirs: Iterable[str] | None = None,
        catalogue: list[dict[str, Any]] | None = None,
        tool_handlers: dict[str, Callable[[dict[str, Any]], dict[str, Any] | list[Any]]] | None = None,
    ) -> None:
        self.workspace = Path(workspace).expanduser().resolve()
        self.workspace.mkdir(parents=True, exist_ok=True)
        if not self.workspace.is_dir():
            raise ValueError("workspace must be a directory")

        self.trace_path = Path(trace_path).expanduser().resolve() if trace_path else None
        if self.trace_path is not None:
            try:
                self.trace_path.relative_to(self.workspace)
            except ValueError:
                pass
            else:
                raise ValueError("trace_path must be outside the workspace snapshot")
            if self.trace_path.exists():
                raise FileExistsError(
                    f"trace file already exists; use a new path to avoid mixing trajectories: {self.trace_path}"
                )
            self.trace_path.parent.mkdir(parents=True, exist_ok=True)

        if max_file_bytes <= 0:
            raise ValueError("max_file_bytes must be positive")
        if max_snapshot_files <= 0 or max_snapshot_bytes <= 0:
            raise ValueError("snapshot limits must be positive")
        self.max_file_bytes = max_file_bytes
        self.max_snapshot_files = max_snapshot_files
        self.max_snapshot_bytes = max_snapshot_bytes
        self.ignored_dirs = set(ignored_dirs) if ignored_dirs is not None else set(DEFAULT_IGNORED_DIRS)
        self.catalogue = [dict(item) for item in (catalogue or DEFAULT_TOOL_CATALOGUE)]
        self.tool_handlers = dict(tool_handlers or {})
        catalogue_ids = [item["tool_id"] for item in self.catalogue]
        if len(catalogue_ids) != len(set(catalogue_ids)):
            raise ValueError("tool catalogue contains duplicate tool_id values")
        unknown_handlers = set(self.tool_handlers) - set(catalogue_ids)
        if unknown_handlers:
            raise ValueError(f"tool handlers reference unknown tools: {sorted(unknown_handlers)}")
        default_visible = {"catalog.search", "fs.list_files", "fs.read_file", "fs.write_file", "fs.append_file"}
        if "catalog.adaption_search" in self.tool_handlers:
            default_visible.add("catalog.adaption_search")
        self._default_visible = set(visible_tool_ids) if visible_tool_ids is not None else default_visible
        self._discovered_tool_ids: set[str] = set()
        self._tool_attempt_counts: dict[str, int] = {}
        self._consumed_faults: set[int] = set()
        self._active_task: TaskSpec | None = None
        self._trajectory_id: str | None = None
        self._sequence = 0
        self.events: list[dict[str, Any]] = []
        self._initial_snapshot: dict[str, str] = {}

    @property
    def active_task_id(self) -> str | None:
        return self._active_task.task_id if self._active_task else None

    def list_tools(self, *, visible_only: bool = True) -> list[dict[str, Any]]:
        """Return a copy of the visible inventory or the full discoverable catalogue."""
        if self._active_task and self._active_task.visible_tool_ids is not None:
            visible = set(self._active_task.visible_tool_ids)
        else:
            visible = set(self._default_visible)
        visible.update(self._discovered_tool_ids)
        visible.add("catalog.search")
        if "catalog.adaption_search" in self.tool_handlers:
            visible.add("catalog.adaption_search")
        available = [
            item for item in self.catalogue
            if item["tool_id"] != "catalog.adaption_search" or "catalog.adaption_search" in self.tool_handlers
        ]
        tools = available if not visible_only else [x for x in available if x["tool_id"] in visible]
        return [dict(item) for item in tools]

    def discover_tools(self, query: str, *, limit: int = 10) -> list[dict[str, Any]]:
        """Search the complete tool catalogue by lexical affordance overlap.

        This is intentionally a simple, deterministic catalogue fixture, not a
        claim that lexical search is sufficient for production tool discovery.
        """
        if not query.strip():
            raise ValueError("discovery query must not be empty")
        if limit < 1:
            raise ValueError("limit must be positive")
        if self._active_task is None:
            raise RuntimeError("begin_task must be called before tool discovery")
        query_terms = self._tokens(query)
        scored: list[tuple[int, str, dict[str, Any]]] = []
        visible_ids = {x["tool_id"] for x in self.list_tools(visible_only=True)}
        for item in self.catalogue:
            if item["tool_id"] == "catalog.adaption_search" and "catalog.adaption_search" not in self.tool_handlers:
                continue
            searchable = " ".join([
                item.get("tool_id", ""), item.get("name", ""),
                item.get("description", ""), " ".join(item.get("tags", [])),
            ])
            terms = self._tokens(searchable)
            score = len(query_terms & terms)
            if score and item["tool_id"] not in visible_ids:
                scored.append((score, item["tool_id"], item))
        scored.sort(key=lambda row: (-row[0], row[1]))
        results = [dict(item) for _, _, item in scored[:limit]]
        if self._active_task.allowed_tool_ids is not None:
            results = [item for item in results if item["tool_id"] in self._active_task.allowed_tool_ids]
        self._discovered_tool_ids.update(item["tool_id"] for item in results)
        self._record({
            "event_type": "tool_discovery",
            "task_id": self.active_task_id,
            "query": query,
            "visible_tool_ids": sorted(visible_ids),
            "discovered_tool_ids": [item["tool_id"] for item in results],
            "results": results,
        })
        return results

    @staticmethod
    def _tokens(value: str) -> set[str]:
        return {token for token in re.findall(r"[a-z0-9_]+", value.casefold()) if len(token) > 1}

    def begin_task(self, task: TaskSpec) -> dict[str, Any]:
        if self._active_task is not None:
            raise RuntimeError(f"task {self._active_task.task_id!r} is already active")
        known = {item["tool_id"] for item in self.catalogue}
        if task.allowed_tool_ids is not None:
            unknown = set(task.allowed_tool_ids) - known
            if unknown:
                raise ValueError(f"task allowlist contains unknown tools: {sorted(unknown)}")
        if task.visible_tool_ids is not None:
            unknown = set(task.visible_tool_ids) - known
            if unknown:
                raise ValueError(f"task visible_tool_ids contains unknown tools: {sorted(unknown)}")
        seen_faults: set[tuple[str, int]] = set()
        for fault in task.fault_injections:
            if not isinstance(fault, dict):
                raise ValueError("each fault injection must be an object")
            tool_id = fault.get("tool_id")
            attempt = fault.get("attempt")
            error = fault.get("error")
            if tool_id not in known:
                raise ValueError(f"fault injection references unknown tool: {tool_id}")
            if not isinstance(attempt, int) or isinstance(attempt, bool) or attempt < 1:
                raise ValueError("fault injection attempt must be a positive integer")
            if not isinstance(error, str) or not error.strip():
                raise ValueError("fault injection error must be a non-empty string")
            fault_key = (tool_id, attempt)
            if fault_key in seen_faults:
                raise ValueError(f"duplicate fault injection for {tool_id} attempt {attempt}")
            seen_faults.add(fault_key)
        for protected_path in task.protected_paths:
            try:
                protected_file = self._safe_path(protected_path, must_exist=True)
            except DHIEnvironmentError as exc:
                raise ValueError(
                    f"protected path must already exist and be a regular file: {protected_path}"
                ) from exc
            if not protected_file.is_file():
                raise ValueError(
                    f"protected path must already exist and be a regular file: {protected_path}"
                )
        self._active_task = task
        self._discovered_tool_ids.clear()
        self._tool_attempt_counts.clear()
        self._consumed_faults.clear()
        self._trajectory_id = task.trajectory_id
        self._sequence = 0
        self._initial_snapshot = self.snapshot()
        event = self._record({
            "event_type": "task_started",
            "task_id": task.task_id,
            "task_prompt": task.prompt,
            "task_goal": task.goal,
            "hard_constraints": task.hard_constraints,
            "preferences": task.preferences,
            "initial_state": self._initial_snapshot,
            "environment_type": "deterministic_file_workspace",
            "environment_version": task.environment_version,
            "tool_manifest": self.list_tools(visible_only=True),
            "postconditions": task.postconditions,
            "protected_paths": task.protected_paths,
            "fault_injections": task.fault_injections,
            "split": task.split,
            "provenance": task.metadata,
        })
        return event

    def run_action(
        self, action: dict[str, Any], *, presented_tool_ids: set[str] | None = None
    ) -> ActionResult:
        if self._active_task is None:
            raise RuntimeError("begin_task must be called before run_action")
        if not isinstance(action, dict):
            raise TypeError("action must be a dictionary")
        tool_id = action.get("tool_id")
        arguments = action.get("arguments", {})
        if not isinstance(tool_id, str) or not tool_id:
            raise ValueError("action.tool_id is required")
        if not isinstance(arguments, dict):
            raise ValueError("action.arguments must be an object")

        before = self.snapshot()
        expected_effects = action.get("expected_effects")
        if expected_effects is not None:
            if not isinstance(expected_effects, dict):
                raise ValueError("expected_effects must be an object")
            for key in ("changed_paths", "unchanged_paths"):
                if key in expected_effects and (
                    not isinstance(expected_effects[key], list)
                    or any(not isinstance(path, str) for path in expected_effects[key])
                ):
                    raise ValueError(f"expected_effects.{key} must be an array of strings")
        started = datetime.now(timezone.utc)
        next_step = self._sequence + 1
        self._record({
            "event_type": "action_started",
            "task_id": self._active_task.task_id,
            "step_id": next_step,
            "timestamp_started": started.isoformat(),
            "observed_state_before": before,
            "selected_tool_id": tool_id,
            "arguments": arguments,
            "presented_tool_ids": sorted(presented_tool_ids) if presented_tool_ids is not None else None,
            "expected_effects": expected_effects,
            "plan_version": action.get("plan_version", 1),
        })
        result: dict[str, Any] | list[Any] | None = None
        error: str | None = None
        allowlist_passed = True
        fault_injection: dict[str, Any] | None = None
        try:
            if (tool_id not in {"catalog.search", "catalog.adaption_search"}
                    and self._active_task.allowed_tool_ids is not None
                    and tool_id not in self._active_task.allowed_tool_ids):
                allowlist_passed = False
                raise DHIEnvironmentError(f"tool {tool_id!r} is not allowed for this task")
            visible_tool_ids = {x["tool_id"] for x in self.list_tools(visible_only=True)}
            if tool_id not in visible_tool_ids:
                raise DHIEnvironmentError(f"tool {tool_id!r} is not currently visible; discover it first")
            if presented_tool_ids is not None and tool_id not in presented_tool_ids:
                raise DHIEnvironmentError(
                    f"tool {tool_id!r} was not in the schema presented for this turn; "
                    "discover it and call it on the next turn"
                )
            self._validate_arguments(tool_id, arguments)
            attempt_number = self._tool_attempt_counts.get(tool_id, 0) + 1
            self._tool_attempt_counts[tool_id] = attempt_number
            for fault_index, fault in enumerate(self._active_task.fault_injections):
                if (fault_index not in self._consumed_faults
                        and fault["tool_id"] == tool_id
                        and fault["attempt"] == attempt_number):
                    self._consumed_faults.add(fault_index)
                    fault_injection = dict(fault)
                    raise DHIEnvironmentError(fault["error"])
            result = self._dispatch(tool_id, arguments)
        except (DHIEnvironmentError, OSError, UnicodeError, ValueError) as exc:
            error = str(exc)
        after = self.snapshot()
        actual_effects = self._diff(before, after)
        prediction = self._compare_prediction(expected_effects, actual_effects)
        self._sequence = next_step
        event = self._record({
            "event_type": "action_executed",
            "task_id": self._active_task.task_id,
            "step_id": self._sequence,
            "timestamp_started": started.isoformat(),
            "timestamp_finished": datetime.now(timezone.utc).isoformat(),
            "observed_state_before": before,
            "subgoal": action.get("subgoal"),
            "selected_tool_id": tool_id,
            "arguments": arguments,
            "expected_effects": expected_effects,
            "fault_injection": fault_injection,
            "actual_tool_result": {"ok": error is None, "result": result, "error": error},
            "observed_state_after": after,
            "actual_effects": actual_effects,
            "prediction_comparison": prediction,
            "plan_version": action.get("plan_version", 1),
            "safety_and_permission_check": {
                "task_allowlist_passed": allowlist_passed,
                "workspace_boundary_enforced": True,
                "tool_side_effect_class": self._tool_meta(tool_id).get("side_effects", "unknown"),
            },
        })
        return ActionResult(
            ok=error is None,
            tool_id=tool_id,
            result=result,
            error=error,
            actual_effects=actual_effects,
            prediction_comparison=prediction,
            event=event,
        )

    def close_task(self) -> dict[str, Any]:
        if self._active_task is None:
            raise RuntimeError("no active task to close")
        final_state = self.snapshot()
        verified = [self._verify_postcondition(condition) for condition in self._active_task.postconditions]
        failed = [item for item in verified if not item["passed"]]
        protected = []
        for relative in self._active_task.protected_paths:
            initial_hash = self._initial_snapshot.get(relative)
            final_hash = final_state.get(relative)
            protected.append({
                "path": relative,
                "passed": initial_hash == final_hash,
                "initial_sha256": initial_hash,
                "final_sha256": final_hash,
            })
        failed_protected = [item for item in protected if not item["passed"]]
        closure = {
            "success": len(failed) == 0 and len(failed_protected) == 0,
            "verified_postconditions": verified,
            "failed_postconditions": failed,
            "verified_protected_paths": protected,
            "failed_protected_paths": failed_protected,
        }
        event = self._record({
            "event_type": "task_closed",
            "task_id": self._active_task.task_id,
            "final_state": final_state,
            "overall_effects": self._diff(self._initial_snapshot, final_state),
            "closure": closure,
            "task_goal": self._active_task.goal,
            "hard_constraints": self._active_task.hard_constraints,
        })
        self._active_task = None
        self._trajectory_id = None
        return {**closure, "event": event}

    def snapshot(self) -> dict[str, str]:
        """Map workspace-relative paths to SHA-256 hashes for regular files."""
        result: dict[str, str] = {}
        total_bytes = 0
        for path in self._iter_files(self.workspace):
            if len(result) >= self.max_snapshot_files:
                raise DHIEnvironmentError(f"workspace exceeds max_snapshot_files ({self.max_snapshot_files})")
            relative = path.relative_to(self.workspace).as_posix()
            try:
                file_size = path.stat().st_size
                total_bytes += file_size
                if total_bytes > self.max_snapshot_bytes:
                    raise DHIEnvironmentError(f"workspace exceeds max_snapshot_bytes ({self.max_snapshot_bytes})")
                if file_size > self.max_file_bytes:
                    raise DHIEnvironmentError(f"workspace file exceeds max_file_bytes: {relative}")
                content = path.read_bytes()
            except OSError as exc:
                raise DHIEnvironmentError(f"cannot snapshot {relative}: {exc}") from exc
            result[relative] = hashlib.sha256(content).hexdigest()
        return result

    def _iter_files(self, folder: Path) -> Iterable[Path]:
        """Yield regular, non-symlink files while pruning common generated/vendor trees."""
        for root, dirs, files in os.walk(folder, topdown=True, followlinks=False):
            root_path = Path(root)
            dirs[:] = sorted(
                name for name in dirs
                if name not in self.ignored_dirs and not (root_path / name).is_symlink()
            )
            for name in sorted(files):
                path = root_path / name
                if path.is_symlink() or not path.is_file():
                    continue
                yield path

    def _safe_path(self, relative: str, *, must_exist: bool = False) -> Path:
        if not isinstance(relative, str) or not relative.strip():
            raise DHIEnvironmentError("workspace-relative path is required")
        if "\\" in relative:
            raise DHIEnvironmentError("path must use POSIX '/' separators")
        pure = PurePosixPath(relative)
        if pure.is_absolute() or any(part in {"", ".", ".."} for part in pure.parts):
            raise DHIEnvironmentError("path must remain inside the workspace")
        candidate = self.workspace.joinpath(*pure.parts)
        current = self.workspace
        for part in pure.parts:
            current = current / part
            if current.is_symlink():
                raise DHIEnvironmentError("symlink paths are not supported")
        resolved = candidate.resolve(strict=False)
        try:
            resolved.relative_to(self.workspace)
        except ValueError as exc:
            raise DHIEnvironmentError("path escapes the workspace") from exc
        if must_exist and not resolved.is_file():
            raise DHIEnvironmentError(f"file does not exist: {relative}")
        return resolved

    def _dispatch(self, tool_id: str, arguments: dict[str, Any]) -> dict[str, Any] | list[Any]:
        if tool_id == "catalog.search":
            return {
                "tools": self.discover_tools(arguments["query"], limit=arguments.get("limit", 10)),
            }

        if tool_id == "catalog.adaption_search":
            handler = self.tool_handlers.get(tool_id)
            if handler is None:
                raise DHIEnvironmentError("live Adaption connector discovery is not configured")
            payload = handler(arguments)
            connectors = payload.get("tools", []) if isinstance(payload, dict) else []
            if self._active_task is not None:
                self._record({
                    "event_type": "tool_discovery",
                    "task_id": self.active_task_id,
                    "query": arguments.get("query", ""),
                    "visible_tool_ids": sorted(item["tool_id"] for item in self.list_tools(visible_only=True)),
                    "discovered_tool_ids": [
                        f"adaption:{item.get('server_label', 'unknown')}" for item in connectors
                        if isinstance(item, dict)
                    ],
                    "results": [item for item in connectors if isinstance(item, dict)],
                    "catalogue_source": "adaption_api",
                    "available_only": arguments.get("available_only", True),
                    "catalogue_snapshot_sha256": payload.get("catalogue_snapshot_sha256") if isinstance(payload, dict) else None,
                    "catalogue_snapshot_scope": payload.get("catalogue_snapshot_scope") if isinstance(payload, dict) else None,
                })
            return payload

        if tool_id in self.tool_handlers:
            return self.tool_handlers[tool_id](arguments)

        if tool_id == "fs.list_files":
            path = arguments.get("path", "")
            if path == "":
                folder = self.workspace
            else:
                folder = self._safe_path(path)
            if not folder.is_dir():
                raise DHIEnvironmentError(f"directory does not exist: {path}")
            files = [p.relative_to(self.workspace).as_posix() for p in self._iter_files(folder)]
            return {"files": files}

        if tool_id == "fs.read_file":
            path = self._safe_path(arguments.get("path"), must_exist=True)
            data = path.read_bytes()
            if len(data) > self.max_file_bytes:
                raise DHIEnvironmentError(f"file exceeds max_file_bytes ({self.max_file_bytes})")
            return {"path": path.relative_to(self.workspace).as_posix(), "content": data.decode("utf-8")}

        if tool_id in {"fs.write_file", "fs.append_file"}:
            relative = arguments.get("path")
            content = arguments.get("content")
            if not isinstance(content, str):
                raise DHIEnvironmentError("content must be a string")
            encoded = content.encode("utf-8")
            if len(encoded) > self.max_file_bytes:
                raise DHIEnvironmentError(f"content exceeds max_file_bytes ({self.max_file_bytes})")
            path = self._safe_path(relative, must_exist=(tool_id == "fs.append_file"))
            if not path.parent.is_dir():
                raise DHIEnvironmentError("parent directory does not exist; create it through an allowed task action first")
            if tool_id == "fs.append_file":
                existing = path.read_bytes()
                if len(existing) + len(encoded) > self.max_file_bytes:
                    raise DHIEnvironmentError(f"result exceeds max_file_bytes ({self.max_file_bytes})")
                encoded = existing + encoded
            self._atomic_write(path, encoded)
            digest = hashlib.sha256(encoded).hexdigest()
            return {"path": path.relative_to(self.workspace).as_posix(), "sha256": digest, "bytes": len(encoded)}

        if tool_id == "fs.search_text":
            query = arguments.get("query")
            if not isinstance(query, str) or not query:
                raise DHIEnvironmentError("query must be a non-empty string")
            prefix = arguments.get("path", "")
            folder = self.workspace if prefix == "" else self._safe_path(prefix)
            if not folder.is_dir():
                raise DHIEnvironmentError(f"directory does not exist: {prefix}")
            case_sensitive = bool(arguments.get("case_sensitive", False))
            needle = query if case_sensitive else query.casefold()
            matches = []
            for file_path in self._iter_files(folder):
                if file_path.stat().st_size > self.max_file_bytes:
                    continue
                try:
                    text = file_path.read_text(encoding="utf-8")
                except (UnicodeError, OSError):
                    continue
                for line_number, line in enumerate(text.splitlines(), start=1):
                    haystack = line if case_sensitive else line.casefold()
                    if needle in haystack:
                        matches.append({
                            "path": file_path.relative_to(self.workspace).as_posix(),
                            "line": line_number,
                            "text": line,
                        })
            return {"matches": matches, "count": len(matches)}

        raise DHIEnvironmentError(f"tool is not implemented: {tool_id}")

    @staticmethod
    def _atomic_write(path: Path, data: bytes) -> None:
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(data)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, path)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink(missing_ok=True)

    def _tool_meta(self, tool_id: str) -> dict[str, Any]:
        return next((item for item in self.catalogue if item["tool_id"] == tool_id), {})

    @staticmethod
    def _diff(before: dict[str, str], after: dict[str, str]) -> dict[str, Any]:
        before_keys, after_keys = set(before), set(after)
        added = sorted(after_keys - before_keys)
        deleted = sorted(before_keys - after_keys)
        modified = sorted(path for path in before_keys & after_keys if before[path] != after[path])
        return {
            "added_paths": added,
            "modified_paths": modified,
            "deleted_paths": deleted,
            "changed_paths": sorted(added + modified + deleted),
            "unchanged_paths": sorted(path for path in before_keys & after_keys if before[path] == after[path]),
        }

    @staticmethod
    def _compare_prediction(expected: dict[str, Any] | None, actual: dict[str, Any]) -> dict[str, Any]:
        if expected is None:
            return {"status": "not_provided", "precision": None, "recall": None, "f1": None,
                    "unchanged_path_violations": []}
        predicted = set(expected.get("changed_paths", []))
        predicted_unchanged = set(expected.get("unchanged_paths", []))
        observed = set(actual["changed_paths"])
        unchanged_violations = sorted(predicted_unchanged & observed)
        if not predicted and not observed:
            precision = recall = f1 = 1.0
        else:
            true_positive = len(predicted & observed)
            precision = true_positive / len(predicted) if predicted else 0.0
            recall = true_positive / len(observed) if observed else 0.0
            f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
        matched = predicted == observed and not unchanged_violations
        return {
            "status": "matched" if matched else "mismatched",
            "predicted_changed_paths": sorted(predicted),
            "predicted_unchanged_paths": sorted(predicted_unchanged),
            "observed_changed_paths": sorted(observed),
            "precision": round(precision, 6),
            "recall": round(recall, 6),
            "f1": round(f1, 6),
            "unexpected_changed_paths": sorted(observed - predicted),
            "missing_predicted_changes": sorted(predicted - observed),
            "unchanged_path_violations": unchanged_violations,
        }

    def _validate_arguments(self, tool_id: str, arguments: dict[str, Any]) -> None:
        metadata = self._tool_meta(tool_id)
        schema = metadata.get("input_schema", {})
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        missing = sorted(set(required) - set(arguments))
        if missing:
            raise DHIEnvironmentError(f"missing required argument(s): {', '.join(missing)}")
        if schema.get("additionalProperties") is False:
            unexpected = sorted(set(arguments) - set(properties))
            if unexpected:
                raise DHIEnvironmentError(f"unexpected argument(s): {', '.join(unexpected)}")
        type_map = {"string": str, "boolean": bool, "integer": int, "number": (int, float), "object": dict, "array": list}
        for key, value in arguments.items():
            expected_type = properties.get(key, {}).get("type")
            python_type = type_map.get(expected_type)
            if python_type is not None:
                if expected_type == "integer" and isinstance(value, bool):
                    raise DHIEnvironmentError(f"argument {key!r} must be {expected_type}")
                if not isinstance(value, python_type):
                    raise DHIEnvironmentError(f"argument {key!r} must be {expected_type}")

    def _verify_postcondition(self, condition: dict[str, Any]) -> dict[str, Any]:
        kind = condition.get("type")
        relative = condition.get("path")
        try:
            path = self._safe_path(relative) if relative else None
            passed = False
            observed: Any = None
            if kind == "exists":
                passed = bool(path and path.exists())
                observed = passed
            elif kind == "not_exists":
                passed = bool(path and not path.exists())
                observed = passed
            elif kind in {"contains", "equals", "sha256"}:
                if path is None or not path.is_file():
                    observed = None
                else:
                    content = path.read_bytes()
                    if len(content) > self.max_file_bytes:
                        raise DHIEnvironmentError("postcondition file exceeds max_file_bytes")
                    if kind == "sha256":
                        observed = hashlib.sha256(content).hexdigest()
                        passed = observed == condition.get("value")
                    else:
                        text = content.decode("utf-8")
                        observed = text
                        if kind == "contains":
                            passed = condition.get("text", "") in text
                        else:
                            passed = text == condition.get("text", "")
            else:
                raise DHIEnvironmentError(f"unsupported postcondition type: {kind}")
            return {"condition": condition, "passed": passed, "observed": observed}
        except (DHIEnvironmentError, OSError, UnicodeError) as exc:
            return {"condition": condition, "passed": False, "error": str(exc)}

    def _record(self, payload: dict[str, Any]) -> dict[str, Any]:
        event = {
            "trace_schema_version": TRACE_SCHEMA_VERSION,
            "trajectory_id": self._trajectory_id,
            "event_index": len(self.events) + 1,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(),
            **payload,
        }
        self.events.append(event)
        if self.trace_path is not None:
            with self.trace_path.open("a", encoding="utf-8") as file:
                file.write(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n")
        return event
