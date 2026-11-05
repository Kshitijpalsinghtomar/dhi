"""Trusted task-scoped GitHub runtime assembly for plugin-native ORBIT tasks.

This module binds the manifest precondition observer, write guards, and final
artifact reader to one repository and one deterministic sandbox branch. It
never enables provider writes itself: the supplied GitHub client must already
have writes enabled and the repository must be in its write allowlist.
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from typing import Any, Callable, Mapping
from urllib.parse import quote

from DHI_v1.environment.github_client import GITHUB_TOOL_CATALOGUE

from .plugin_execution import (
    PreparedPluginExecution,
    PluginExecutionNotReady,
    prepare_plugin_execution,
)
from .plugin_task_loader import PluginTaskPlan


class GitHubTaskRuntimeError(RuntimeError):
    """The task cannot be bound safely to the configured GitHub sandbox."""


@dataclass(frozen=True)
class PreparedGitHubTaskRuntime:
    """Prepared model tools plus trusted provider callbacks for a single task."""

    prepared: PreparedPluginExecution
    repository_full_name: str
    expected_branch: str
    expected_base_commit: str
    allowed_paths: frozenset[str]
    precondition_observer: Callable[[Mapping[str, Any], Mapping[str, Any]], Mapping[str, Any]]
    state_observer: Callable[[], Mapping[str, str]]
    artifact_reader: Callable[[str, str, str], Mapping[str, Any]]


def _sandbox_branch(task_id: str) -> str:
    if not isinstance(task_id, str) or not re.fullmatch(r"ORBIT-A-S\d{2}-\d{3}", task_id):
        raise GitHubTaskRuntimeError("task ID is not a supported ORBIT Stage A task")
    return f"orbit/sandbox/{task_id.lower()}"


def _pinned_base_commit(plan: PluginTaskPlan) -> str:
    found: list[str] = []
    for item in plan.preconditions:
        condition = item.get("condition") if isinstance(item, Mapping) else None
        if isinstance(condition, Mapping) and condition.get("type") == "branch_head_equals":
            commit = condition.get("commit")
            if isinstance(commit, str) and re.fullmatch(r"[a-f0-9]{40}", commit):
                found.append(commit)
            else:
                raise GitHubTaskRuntimeError("branch_head_equals precondition has an invalid commit")
    if len(found) != 1:
        raise GitHubTaskRuntimeError("task must declare exactly one pinned branch_head_equals precondition")
    return found[0]


def _allowed_output_paths(plan: PluginTaskPlan) -> frozenset[str]:
    paths: set[str] = set()
    for item in plan.postconditions:
        condition = item.get("condition") if isinstance(item, Mapping) else None
        if not isinstance(condition, Mapping):
            continue
        kind = condition.get("type")
        if kind in {"github_file_exists", "github_file_contains"}:
            path = condition.get("path")
            if isinstance(path, str) and path:
                paths.add(path)
        elif kind == "branch_diff_only":
            allowed = condition.get("allowed_paths")
            if isinstance(allowed, list):
                paths.update(path for path in allowed if isinstance(path, str) and path)
    if not paths:
        raise GitHubTaskRuntimeError("task has no deterministic file-output allowlist")
    return frozenset(paths)


def _catalogue_schemas(tool_ids: tuple[str, ...]) -> dict[str, dict[str, Any]]:
    catalogue = {item["tool_id"]: item["input_schema"] for item in GITHUB_TOOL_CATALOGUE}
    missing = sorted(set(tool_ids) - set(catalogue))
    if missing:
        raise GitHubTaskRuntimeError(f"task contains GitHub tools outside the pinned adapter catalogue: {missing}")
    return {tool_id: json.loads(json.dumps(catalogue[tool_id])) for tool_id in tool_ids}



def run_github_plugin_task(
    task_record: Mapping[str, Any],
    runtime: PreparedGitHubTaskRuntime,
    model_client: Any,
    *,
    trajectory_id: str | None = None,
    model_id: str | None = None,
    evidence_class: str = "scripted-reference",
    max_model_turns: int | None = None,
    max_tool_calls: int | None = None,
    temperature: float = 0.0,
):
    """Run through the trusted runtime so callers cannot omit its safety callbacks.

    This is deliberately a thin binding layer: the canonical plugin runner still
    performs model-call limits, tool validation, trace generation and grading.
    The wrapper only binds the exact prepared tools and the precondition, state
    snapshot and readback observers constructed for the same task-scoped sandbox.
    """
    if not isinstance(runtime, PreparedGitHubTaskRuntime):
        raise GitHubTaskRuntimeError("runtime must be a PreparedGitHubTaskRuntime")
    if not isinstance(task_record, Mapping) or task_record.get("task_id") != runtime.prepared.task.task_id:
        raise GitHubTaskRuntimeError("task record does not match the prepared GitHub runtime")

    from .plugin_runner import run_plugin_task

    return run_plugin_task(
        task_record,
        runtime.prepared,
        model_client,
        observe_state=runtime.state_observer,
        precondition_observer=runtime.precondition_observer,
        artifact_reader=runtime.artifact_reader,
        trajectory_id=trajectory_id,
        model_id=model_id,
        evidence_class=evidence_class,
        max_model_turns=max_model_turns,
        max_tool_calls=max_tool_calls,
        temperature=temperature,
    )

def build_github_plugin_runtime(
    plan: PluginTaskPlan,
    client: Any,
    *,
    repository_full_name: str,
) -> PreparedGitHubTaskRuntime:
    """Bind one manifest task to a single repo, sandbox branch, and output set.

    The client is a configured GitHubReadWriteClient (or a contract-compatible
    test double). Branch identity is derived deterministically from the trusted
    task ID, never from model arguments. The expected base SHA is read from the
    manifest precondition. Write permission is only used if already granted by
    the client constructor and its repository allowlist.
    """
    if not isinstance(plan, PluginTaskPlan):
        raise GitHubTaskRuntimeError("plan must be a validated PluginTaskPlan")
    if plan.model_runs_allowed is not True:
        raise GitHubTaskRuntimeError("task model_runs_allowed=false; model execution remains disabled")
    if not isinstance(repository_full_name, str) or not re.fullmatch(
        r"[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}", repository_full_name
    ):
        raise GitHubTaskRuntimeError("repository_full_name is invalid")
    if not getattr(client, "enable_writes", False):
        raise GitHubTaskRuntimeError("GitHub write configuration is not enabled for this runtime")
    allowed_repositories = getattr(client, "allowed_repositories", frozenset())
    if repository_full_name not in allowed_repositories:
        raise GitHubTaskRuntimeError("repository is outside the GitHub client write allowlist")
    if (
        not callable(getattr(client, "fetch", None))
        or not callable(getattr(client, "fetch_file", None))
        or not callable(getattr(client, "compare_commits", None))
    ):
        raise GitHubTaskRuntimeError("GitHub client lacks fetch, fetch_file and compare_commits read capabilities")
    if not callable(getattr(client, "tool_handlers", None)):
        raise GitHubTaskRuntimeError("GitHub client lacks the canonical tool handler map")

    expected_branch = _sandbox_branch(plan.task_id)
    expected_base_commit = _pinned_base_commit(plan)
    allowed_paths = _allowed_output_paths(plan)

    visible_ids = tuple(plan.visible_tool_ids)
    schemas = _catalogue_schemas(visible_ids)
    client_handlers = client.tool_handlers()
    if not isinstance(client_handlers, Mapping):
        raise GitHubTaskRuntimeError("GitHub client returned an invalid tool handler map")
    handlers = {
        tool_id: client_handlers[tool_id]
        for tool_id in visible_ids
        if tool_id in client_handlers
    }

    write_guards: dict[str, Callable[[PluginTaskPlan, dict[str, Any]], bool]] = {}
    for tool_id in plan.allowed_tool_ids:
        contract = plan.tool_contracts.get(tool_id, {})
        if contract.get("side_effect_class") != "sandbox_write":
            continue
        if tool_id.endswith("__create_file") or tool_id.endswith("__update_file"):
            def guard(task: PluginTaskPlan, args: dict[str, Any]) -> bool:
                return (
                    task.task_id == plan.task_id
                    and args.get("repository_full_name") == repository_full_name
                    and args.get("branch") == expected_branch
                    and args.get("path") in allowed_paths
                )
            write_guards[tool_id] = guard
        else:
            raise GitHubTaskRuntimeError(
                f"task sandbox-write tool has no task-scoped branch guard: {tool_id}"
            )

    try:
        prepared = prepare_plugin_execution(
            plan,
            schemas=schemas,
            handlers=handlers,
            write_guards=write_guards,
        )
    except PluginExecutionNotReady as exc:
        raise GitHubTaskRuntimeError(f"GitHub tool preparation failed: {exc}") from exc

    expected_ref = f"refs/heads/{expected_branch}"

    def precondition_observer(
        task_record: Mapping[str, Any],
        precondition: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        if not isinstance(task_record, Mapping) or task_record.get("task_id") != plan.task_id:
            raise GitHubTaskRuntimeError("precondition task does not match the prepared task")
        condition = precondition.get("condition") if isinstance(precondition, Mapping) else None
        if not isinstance(condition, Mapping):
            raise GitHubTaskRuntimeError("precondition has no structured condition")
        condition_type = condition.get("type")
        if condition_type == "branch_head_equals":
            if condition.get("commit") != expected_base_commit:
                raise GitHubTaskRuntimeError("branch precondition does not match the task's pinned base commit")
            url = (
                f"https://api.github.com/repos/{repository_full_name}/git/ref/heads/"
                f"{quote(expected_branch, safe='/')}"
            )
            response = client.fetch({"url": url})
            content = response.get("content") if isinstance(response, Mapping) else None
            if not isinstance(content, str):
                raise GitHubTaskRuntimeError("GitHub branch observer returned no response content")
            try:
                payload = json.loads(content)
            except json.JSONDecodeError as exc:
                raise GitHubTaskRuntimeError("GitHub branch observer returned malformed JSON") from exc
            if not isinstance(payload, Mapping) or payload.get("ref") != expected_ref:
                raise GitHubTaskRuntimeError("GitHub branch ref did not match the task-scoped sandbox branch")
            obj = payload.get("object")
            head_sha = obj.get("sha") if isinstance(obj, Mapping) else None
            if not isinstance(head_sha, str) or not re.fullmatch(r"[a-f0-9]{40}", head_sha):
                raise GitHubTaskRuntimeError("GitHub branch ref did not contain a valid head SHA")
            return {"branch_name": expected_branch, "head_sha": head_sha}

        if condition_type == "github_file_blob":
            path = condition.get("path")
            commit = condition.get("commit")
            expected_blob = condition.get("blob_sha")
            if (
                not isinstance(path, str)
                or not path
                or path.startswith("/")
                or "\\" in path
                or any(part in {"", ".", ".."} for part in path.split("/"))
                or not isinstance(commit, str)
                or not re.fullmatch(r"[a-f0-9]{40}", commit)
                or commit != expected_base_commit
                or not isinstance(expected_blob, str)
                or not re.fullmatch(r"[a-f0-9]{40}", expected_blob)
            ):
                raise GitHubTaskRuntimeError("pinned GitHub file-blob precondition is malformed or outside the task base")
            response = client.fetch_file({
                "repository_full_name": repository_full_name,
                "path": path,
                "ref": commit,
            })
            content = response.get("content") if isinstance(response, Mapping) else None
            blob_sha = response.get("sha") if isinstance(response, Mapping) else None
            if (
                not isinstance(content, str)
                or not isinstance(blob_sha, str)
                or not re.fullmatch(r"[a-f0-9]{40}", blob_sha)
                or hashlib.sha1(
                    b"blob " + str(len(content.encode("utf-8"))).encode("ascii")
                    + b"\0" + content.encode("utf-8")
                ).hexdigest() != blob_sha
            ):
                raise GitHubTaskRuntimeError("GitHub checkpoint readback failed its content/blob integrity check")
            if blob_sha != expected_blob:
                raise GitHubTaskRuntimeError("GitHub checkpoint blob SHA does not match the manifest-pinned blob SHA")
            return {"path": path, "commit": commit, "blob_sha": blob_sha}

        raise GitHubTaskRuntimeError(f"unsupported trusted GitHub precondition type: {condition_type!r}")

    def state_observer() -> Mapping[str, str]:
        """Return the independently observed base-to-branch file-diff snapshot."""
        response = client.compare_commits({
            "repo_full_name": repository_full_name,
            "base": expected_base_commit,
            "head": expected_branch,
        })
        if not isinstance(response, Mapping):
            raise GitHubTaskRuntimeError("GitHub compare returned an invalid result")
        if (
            response.get("repository_full_name") != repository_full_name
            or response.get("base") != expected_base_commit
            or response.get("head") != expected_branch
        ):
            raise GitHubTaskRuntimeError("GitHub compare response does not match the pinned task repository/branch")
        files = response.get("files")
        if not isinstance(files, list):
            raise GitHubTaskRuntimeError("GitHub compare response has no file list")

        state: dict[str, str] = {}
        allowed_statuses = {"added", "removed", "modified", "renamed", "copied", "changed"}
        for item in files:
            if not isinstance(item, Mapping):
                raise GitHubTaskRuntimeError("GitHub compare returned a malformed file record")
            path = item.get("filename")
            status = item.get("status")
            blob_sha = item.get("sha")
            if (
                not isinstance(path, str)
                or not path
                or path.startswith("/")
                or "\\" in path
                or any(part in {"", ".", ".."} for part in path.split("/"))
                or not isinstance(status, str)
                or status not in allowed_statuses
            ):
                raise GitHubTaskRuntimeError("GitHub compare returned an invalid path or status")
            if blob_sha is not None and (
                not isinstance(blob_sha, str) or not re.fullmatch(r"[a-f0-9]{40}", blob_sha)
            ):
                raise GitHubTaskRuntimeError(f"GitHub compare returned an invalid blob SHA for {path!r}")

            fingerprint = hashlib.sha256(json.dumps(
                {"status": status, "blob_sha": blob_sha},
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")).hexdigest()
            if path in state:
                raise GitHubTaskRuntimeError(f"GitHub compare returned duplicate path {path!r}")
            state[path] = fingerprint

            previous = item.get("previous_filename")
            if previous is not None:
                if (
                    not isinstance(previous, str)
                    or not previous
                    or previous.startswith("/")
                    or "\\" in previous
                    or any(part in {"", ".", ".."} for part in previous.split("/"))
                    or previous in state
                ):
                    raise GitHubTaskRuntimeError("GitHub compare returned an invalid previous_filename")
                state[previous] = hashlib.sha256(json.dumps(
                    {"status": "renamed_from", "blob_sha": blob_sha},
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")).hexdigest()
        return dict(sorted(state.items()))

    def artifact_reader(repo: str, path: str, ref: str) -> Mapping[str, Any]:
        if repo != repository_full_name or path not in allowed_paths or ref != expected_branch:
            raise GitHubTaskRuntimeError("artifact readback request is outside the task-scoped sandbox")
        response = client.fetch_file({
            "repository_full_name": repository_full_name,
            "path": path,
            "ref": expected_branch,
        })
        if not isinstance(response, Mapping):
            raise GitHubTaskRuntimeError("GitHub artifact readback returned an invalid result")
        content = response.get("content")
        sha = response.get("sha")
        display_url = response.get("display_url")
        if not isinstance(content, str) or not isinstance(sha, str) or not isinstance(display_url, str):
            raise GitHubTaskRuntimeError("GitHub artifact readback is missing content or provenance")
        return {"content": content, "sha": sha, "display_url": display_url}

    return PreparedGitHubTaskRuntime(
        prepared=prepared,
        repository_full_name=repository_full_name,
        expected_branch=expected_branch,
        expected_base_commit=expected_base_commit,
        allowed_paths=allowed_paths,
        precondition_observer=precondition_observer,
        state_observer=state_observer,
        artifact_reader=artifact_reader,
    )
