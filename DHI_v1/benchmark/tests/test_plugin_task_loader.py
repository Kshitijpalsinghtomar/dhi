from __future__ import annotations

import json
from pathlib import Path

import pytest

from DHI_v1.benchmark.plugin_task_loader import (
    PluginTaskLoadError,
    load_all_plugin_tasks,
    load_plugin_task,
)


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"
REGISTRY = ROOT / "DHI_v1" / "benchmark" / "fixtures" / "plugin_ecology" / "plugin_tool_registry.json"


def test_loader_preserves_canonical_provider_tool_ids():
    plan = load_plugin_task(MANIFEST, REGISTRY, "ORBIT-A-S02-001")

    assert plan.visible_tool_ids == (
        "mcp__TinyFish__search",
        "mcp__TinyFish__fetch_content",
    )
    assert plan.required_tool_ids == plan.visible_tool_ids
    assert plan.allowed_tool_ids == plan.visible_tool_ids


def test_read_only_task_does_not_authorize_visible_write_decoy():
    plan = load_plugin_task(MANIFEST, REGISTRY, "ORBIT-A-S10-001")

    assert "mcp__GitHub__create_file" in plan.visible_tool_ids
    assert "mcp__GitHub__create_file" not in plan.allowed_tool_ids
    assert "mcp__GitHub__fetch_file" in plan.allowed_tool_ids


def test_disposable_report_task_authorizes_only_its_declared_write_tool():
    plan = load_plugin_task(MANIFEST, REGISTRY, "ORBIT-A-S06-001")

    assert "mcp__GitHub__create_file" in plan.allowed_tool_ids
    assert "mcp__GitHub__fetch_file" in plan.allowed_tool_ids
    assert "mcp__GitHub__compare_commits" in plan.allowed_tool_ids
    assert "mcp__GitHub__update_file" not in plan.allowed_tool_ids
    assert "mcp__GitHub__create_branch" not in plan.allowed_tool_ids


def test_loader_keeps_model_execution_disabled_until_manifest_authorizes_it():
    plan = load_plugin_task(MANIFEST, REGISTRY, "ORBIT-A-S02-001")

    assert plan.model_runs_allowed is False
    assert plan.execution_status == "not_run"


def test_all_authored_stage_a_tasks_resolve_required_ids_in_registry():
    plans = load_all_plugin_tasks(MANIFEST, REGISTRY)

    assert len(plans) == 30
    assert {plan.stage for plan in plans} == {"A"}
    assert all(set(plan.required_tool_ids).issubset(plan.allowed_tool_ids) for plan in plans)


def test_loader_fails_closed_when_a_required_tool_is_not_registered(tmp_path):
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    manifest["tasks"][1]["tool_inventory"]["required_tool_ids"].append("mcp__Unknown__execute")

    manifest_path = tmp_path / "manifest.json"
    registry_path = tmp_path / "registry.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    registry_path.write_text(json.dumps(registry), encoding="utf-8")

    with pytest.raises(PluginTaskLoadError, match="not present in the pinned registry"):
        load_plugin_task(manifest_path, registry_path, "ORBIT-A-S02-001")


def test_loader_fails_closed_on_manifest_registry_schema_fingerprint_mismatch(tmp_path):
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    registry["tool_schema_sha256"] = "0" * 64

    manifest_path = tmp_path / "manifest.json"
    registry_path = tmp_path / "registry.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    registry_path.write_text(json.dumps(registry), encoding="utf-8")

    with pytest.raises(PluginTaskLoadError, match="schema fingerprint mismatch"):
        load_plugin_task(manifest_path, registry_path, "ORBIT-A-S02-001")


def test_unrelated_permission_label_does_not_grant_read_only_tool_access(tmp_path):
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    task = next(item for item in manifest["tasks"] if item["task_id"] == "ORBIT-A-S02-001")
    task["policy"]["allowed_side_effects"] = ["external_purchase"]

    manifest_path = tmp_path / "manifest.json"
    registry_path = tmp_path / "registry.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    registry_path.write_text(json.dumps(registry), encoding="utf-8")

    with pytest.raises(PluginTaskLoadError, match="required tools exceed task side-effect permissions"):
        load_plugin_task(manifest_path, registry_path, "ORBIT-A-S02-001")
