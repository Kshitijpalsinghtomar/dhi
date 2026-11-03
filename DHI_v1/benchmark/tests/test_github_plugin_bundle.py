from __future__ import annotations

import os
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pytest

from DHI_v1.benchmark.plugin_execution import PluginExecutionNotReady, prepare_plugin_execution
from DHI_v1.benchmark.plugin_task_loader import load_plugin_task
from DHI_v1.environment.github_client import (
    GITHUB_TOOL_CATALOGUE,
    GitHubReadWriteClient,
    github_plugin_bundle_from_env,
)


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"
REGISTRY = ROOT / "DHI_v1" / "benchmark" / "fixtures" / "plugin_ecology" / "plugin_tool_registry.json"

READ_IDS = {
    "mcp__GitHub__fetch_file",
    "mcp__GitHub__fetch",
    "mcp__GitHub__compare_commits",
}
WRITE_IDS = {
    "mcp__GitHub__create_branch",
    "mcp__GitHub__create_file",
    "mcp__GitHub__update_file",
}


def _base_env(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", "github-unit-test-secret")
    monkeypatch.delenv("DHI_GITHUB_WRITES_ENABLED", raising=False)
    monkeypatch.delenv("GITHUB_ALLOWED_REPOSITORIES", raising=False)


def test_bundle_schemas_match_canonical_registry_and_no_token_means_no_handlers(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    schemas, handlers = github_plugin_bundle_from_env()

    assert set(schemas) == {item["tool_id"] for item in GITHUB_TOOL_CATALOGUE}
    assert handlers == {}
    assert all(schema["type"] == "object" for schema in schemas.values())
    assert all(schema["additionalProperties"] is False for schema in schemas.values())


def test_token_alone_exposes_only_read_only_handlers(monkeypatch):
    _base_env(monkeypatch)

    schemas, handlers = github_plugin_bundle_from_env()

    assert set(handlers) == READ_IDS
    assert not set(handlers) & WRITE_IDS


def test_write_handlers_are_exposed_only_with_flag_and_repository_allowlist(monkeypatch):
    _base_env(monkeypatch)
    monkeypatch.setenv("DHI_GITHUB_WRITES_ENABLED", "true")
    monkeypatch.setenv("GITHUB_ALLOWED_REPOSITORIES", "acme/northstar, acme/secondary")

    schemas, handlers = github_plugin_bundle_from_env()

    assert set(handlers) == READ_IDS | WRITE_IDS
    assert set(schemas) == READ_IDS | WRITE_IDS

    monkeypatch.delenv("GITHUB_ALLOWED_REPOSITORIES")
    _, no_allowlist = github_plugin_bundle_from_env()
    assert set(no_allowlist) == READ_IDS


def test_real_manifest_github_read_task_prepares_from_canonical_bundle(monkeypatch):
    _base_env(monkeypatch)
    fake_handlers = {
        tool_id: (lambda arguments: {"synthetic": tool_id, "arguments": arguments})
        for tool_id in READ_IDS
    }
    with patch.object(GitHubReadWriteClient, "tool_handlers", return_value=fake_handlers):
        schemas, handlers = github_plugin_bundle_from_env()

    base_plan = load_plugin_task(MANIFEST, REGISTRY, "ORBIT-A-S04-001")
    plan = replace(base_plan, model_runs_allowed=True)
    prepared = prepare_plugin_execution(plan, schemas=schemas, handlers=handlers)

    assert set(prepared.tool_name_by_id) == set(plan.visible_tool_ids)
    assert prepared.dispatch(
        prepared.tool_name_by_id["mcp__GitHub__fetch_file"],
        {"repository_full_name": "acme/northstar", "path": "TASK_POLICY.md"},
    )["synthetic"] == "mcp__GitHub__fetch_file"


def test_allowlisted_write_handler_still_requires_task_specific_dispatch_guard(monkeypatch):
    _base_env(monkeypatch)
    monkeypatch.setenv("DHI_GITHUB_WRITES_ENABLED", "true")
    monkeypatch.setenv("GITHUB_ALLOWED_REPOSITORIES", "Kshitijpalsinghtomar/dhi")
    fake_handlers = {
        tool_id: (lambda arguments: {"synthetic": tool_id, "arguments": arguments})
        for tool_id in READ_IDS | WRITE_IDS
    }
    with patch.object(GitHubReadWriteClient, "tool_handlers", return_value=fake_handlers):
        schemas, handlers = github_plugin_bundle_from_env()

    base_plan = load_plugin_task(MANIFEST, REGISTRY, "ORBIT-A-S06-001")
    plan = replace(base_plan, model_runs_allowed=True)
    with pytest.raises(PluginExecutionNotReady, match="missing write guard"):
        prepare_plugin_execution(plan, schemas=schemas, handlers=handlers)

    guards = {
        "mcp__GitHub__create_file": lambda task, args: (
            task.task_id == "ORBIT-A-S06-001"
            and args.get("repository_full_name") == "Kshitijpalsinghtomar/dhi"
            and args.get("branch") == "orbit/plugin-benchmark-fixture"
            and args.get("path") == "reports/release-readiness.md"
        )
    }
    prepared = prepare_plugin_execution(
        plan, schemas=schemas, handlers=handlers, write_guards=guards
    )
    create_name = prepared.tool_name_by_id["mcp__GitHub__create_file"]
    assert prepared.dispatch(create_name, {
        "repository_full_name": "Kshitijpalsinghtomar/dhi",
        "path": "reports/release-readiness.md",
        "content": "fixture only",
        "message": "fixture only",
        "branch": "orbit/plugin-benchmark-fixture",
    })["synthetic"] == "mcp__GitHub__create_file"
