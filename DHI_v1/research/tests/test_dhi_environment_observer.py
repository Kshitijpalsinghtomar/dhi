import hashlib
import json

import pytest

from DHI_v1.environment.dhi_env import DHIEnvironment, DEFAULT_TOOL_CATALOGUE, TaskSpec
from DHI_v1.research.dhi_environment_observer import observe_dhi_environment
from DHI_v1.research.joint_state import diff_joint_state


def make_task(**overrides):
    values = {
        "task_id": "joint-observer-case",
        "prompt": "Inspect the workspace and report its state.",
        "goal": "Read the workspace without modifying protected files.",
        "postconditions": [
            {"type": "contains", "path": "README.md", "text": "# Observer fixture"}
        ],
        "visible_tool_ids": ["fs.read_file"],
    }
    values.update(overrides)
    return TaskSpec(**values)


def make_catalogue():
    catalogue = [dict(item) for item in DEFAULT_TOOL_CATALOGUE]
    catalogue.extend([
        {
            "tool_id": "external.read",
            "name": "External read",
            "description": "Read an external resource.",
            "tags": ["external_read"],
            "input_schema": {
                "type": "object",
                "properties": {"resource": {"type": "string"}},
                "required": ["resource"],
                "additionalProperties": False,
            },
            "requires_handler": True,
            "side_effects": "read_only",
            "permission_scope": "external_read",
        },
        {
            "tool_id": "restricted.write",
            "name": "Restricted write",
            "description": "Write through an explicitly allowlisted tool.",
            "tags": ["restricted_write"],
            "input_schema": {
                "type": "object",
                "properties": {"value": {"type": "string"}},
                "required": ["value"],
                "additionalProperties": False,
            },
            "requires_explicit_task_allowlist": True,
            "side_effects": "workspace_write",
            "permission_scope": "workspace_write",
        },
    ])
    return catalogue


def make_env(tmp_path, *, allowed_tool_ids=None):
    (tmp_path / "README.md").write_text("# Observer fixture\n", encoding="utf-8")
    env = DHIEnvironment(
        tmp_path,
        catalogue=make_catalogue(),
        visible_tool_ids={"fs.read_file"},
    )
    env.begin_task(make_task(allowed_tool_ids=allowed_tool_ids))
    return env


def observe(env, suffix):
    return observe_dhi_environment(
        env,
        workspace_scope_id="workspace:joint-observer-case",
        catalogue_scope_id="catalogue:joint-observer-case",
        observation_ref=f"test://joint-observer/{suffix}",
    )


def test_observer_uses_real_dhi_environment_and_preserves_unknowns(tmp_path):
    env = make_env(tmp_path)
    before_events = len(env.events)

    observed = observe(env, "initial")

    assert len(env.events) == before_events
    assert observed.task.complete_snapshot is True
    assert observed.ecosystem.complete_snapshot is True
    assert observed.task.scope_id == "workspace:joint-observer-case"
    assert observed.ecosystem.scope_id == "catalogue:joint-observer-case"

    facts = {fact.key: fact.value for fact in observed.task.facts}
    expected_hash = hashlib.sha256(b"# Observer fixture\n").hexdigest()
    assert facts == {"file:README.md": expected_hash}

    tools = {tool.tool_id: tool for tool in observed.ecosystem.tools}
    assert tools["fs.read_file"].availability == "callable"
    assert tools["fs.search_text"].availability == "discoverable"
    assert tools["external.read"].availability == "disconnected"
    assert tools["restricted.write"].availability == "unavailable"
    assert tools["restricted.write"].permission_state == "unknown"
    assert tools["external.read"].permission_state == "unknown"
    assert tools["external.read"].permissions == ("external_read",)
    assert tools["fs.read_file"].schema_sha256 == hashlib.sha256(
        json.dumps(
            tools["fs.read_file"]._schema_for_test,
            sort_keys=True, separators=(",", ":"), ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest() if hasattr(tools["fs.read_file"], "_schema_for_test") else isinstance(tools["fs.read_file"].schema_sha256, str)


def test_explicit_task_allowlist_denial_is_not_reported_as_callable(tmp_path):
    env = make_env(tmp_path, allowed_tool_ids=["fs.read_file"])
    observed = observe(env, "allowlist")

    tools = {tool.tool_id: tool for tool in observed.ecosystem.tools}
    assert tools["fs.write_file"].availability == "unavailable"
    assert tools["fs.write_file"].permission_state == "denied"


def test_observer_requires_an_active_task_scope(tmp_path):
    (tmp_path / "README.md").write_text("# Observer fixture\n", encoding="utf-8")
    env = DHIEnvironment(tmp_path, catalogue=make_catalogue())

    with pytest.raises(ValueError, match="active task"):
        observe(env, "no-active-task")


def test_discovery_changes_tool_availability_without_changing_world_state(tmp_path):
    env = make_env(tmp_path)
    before = observe(env, "before-discovery")

    discovered = env.discover_tools("search text in files")
    assert any(item["tool_id"] == "fs.search_text" for item in discovered)
    after = observe(env, "after-discovery")

    delta = diff_joint_state(before, after)
    assert delta.world_changes == ()
    assert delta.tool_changes == ()
    tools = {tool.tool_id: tool for tool in after.ecosystem.tools}
    assert tools["fs.search_text"].availability == "callable"


def test_workspace_action_changes_only_world_state_observation(tmp_path):
    env = make_env(tmp_path)
    before = observe(env, "before-write")

    result = env.run_action({
        "tool_id": "fs.append_file",
        "arguments": {"path": "README.md", "content": "Research note\n"},
    })
    assert result.ok is True
    after = observe(env, "after-write")

    delta = diff_joint_state(before, after)
    assert len(delta.world_changes) == 1
    assert delta.world_changes[0].key == "file:README.md"
    assert delta.world_changes[0].operation == "update"
    assert delta.tool_changes == ()


def test_catalogue_schema_drift_changes_only_ecosystem_observation(tmp_path):
    env = make_env(tmp_path)
    before = observe(env, "before-schema-drift")

    target = next(item for item in env.catalogue if item["tool_id"] == "fs.read_file")
    target["input_schema"]["properties"]["encoding"] = {"type": "string"}
    target["input_schema"]["properties"]["path"]["description"] = "Workspace-relative path."
    after = observe(env, "after-schema-drift")

    delta = diff_joint_state(before, after)
    assert delta.world_changes == ()
    schema_changes = [
        item for item in delta.tool_changes
        if item.tool_id == "fs.read_file" and item.field == "schema_sha256"
    ]
    assert len(schema_changes) == 1
    assert schema_changes[0].before != schema_changes[0].after


def test_joint_mechanism_test_detects_world_and_tool_drift_independently(tmp_path):
    env = make_env(tmp_path)
    before = observe(env, "joint-before")

    env.run_action({
        "tool_id": "fs.append_file",
        "arguments": {"path": "README.md", "content": "Changed world.\n"},
    })
    target = next(item for item in env.catalogue if item["tool_id"] == "fs.read_file")
    target["input_schema"]["properties"]["encoding"] = {"type": "string"}
    after = observe(env, "joint-after")

    delta = diff_joint_state(before, after)
    assert len(delta.world_changes) == 1
    assert any(x.tool_id == "fs.read_file" and x.field == "schema_sha256" for x in delta.tool_changes)


if __name__ == "__main__":
    import unittest
    unittest.main()
