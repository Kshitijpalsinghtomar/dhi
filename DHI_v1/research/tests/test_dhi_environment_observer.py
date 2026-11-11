import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from DHI_v1.environment.dhi_env import DHIEnvironment, DEFAULT_TOOL_CATALOGUE, TaskSpec
from DHI_v1.research.dhi_environment_observer import observe_dhi_environment
from DHI_v1.research.joint_state import ToolChange, diff_joint_state


def make_task(**overrides):
    values = {
        "task_id": "joint-observer-case",
        "prompt": "Inspect the workspace and report its state.",
        "goal": "Read the workspace and verify its observed state.",
        "postconditions": [
            {"type": "contains", "path": "README.md", "text": "# Observer fixture"}
        ],
        "visible_tool_ids": ["fs.read_file", "fs.append_file"],
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


class DHIEnvironmentObserverTests(unittest.TestCase):
    def setUp(self):
        self._temp = tempfile.TemporaryDirectory()
        self.root = Path(self._temp.name)

    def tearDown(self):
        self._temp.cleanup()

    def make_env(self, name, *, allowed_tool_ids=None):
        workspace = self.root / name
        workspace.mkdir()
        (workspace / "README.md").write_text("# Observer fixture\n", encoding="utf-8")
        env = DHIEnvironment(
            workspace,
            catalogue=make_catalogue(),
            visible_tool_ids={"fs.read_file", "fs.append_file"},
        )
        env.begin_task(make_task(allowed_tool_ids=allowed_tool_ids))
        return env

    @staticmethod
    def observe(env, suffix):
        return observe_dhi_environment(
            env,
            workspace_scope_id="workspace:joint-observer-case",
            catalogue_scope_id="catalogue:joint-observer-case",
            observation_ref=f"test://joint-observer/{suffix}",
        )

    def test_observer_uses_real_dhi_environment_and_preserves_unknowns(self):
        env = self.make_env("initial")
        before_events = len(env.events)

        observed = self.observe(env, "initial")

        self.assertEqual(len(env.events), before_events)
        self.assertTrue(observed.task.complete_snapshot)
        self.assertTrue(observed.ecosystem.complete_snapshot)
        self.assertEqual(observed.task.scope_id, "workspace:joint-observer-case")
        self.assertEqual(observed.ecosystem.scope_id, "catalogue:joint-observer-case")

        facts = {fact.key: fact.value for fact in observed.task.facts}
        expected_hash = hashlib.sha256(b"# Observer fixture\n").hexdigest()
        self.assertEqual(facts, {"file:README.md": expected_hash})

        tools = {tool.tool_id: tool for tool in observed.ecosystem.tools}
        self.assertEqual(tools["fs.read_file"].availability, "callable")
        self.assertEqual(tools["fs.search_text"].availability, "discoverable")
        self.assertEqual(tools["external.read"].availability, "disconnected")
        self.assertEqual(tools["restricted.write"].availability, "unavailable")
        self.assertEqual(tools["restricted.write"].permission_state, "unknown")
        self.assertEqual(tools["external.read"].permission_state, "unknown")
        self.assertEqual(tools["external.read"].permissions, ("external_read",))

        read_metadata = next(item for item in env.catalogue if item["tool_id"] == "fs.read_file")
        expected_schema_hash = hashlib.sha256(
            json.dumps(
                read_metadata["input_schema"],
                sort_keys=True, separators=(",", ":"), ensure_ascii=False,
            ).encode("utf-8")
        ).hexdigest()
        self.assertEqual(tools["fs.read_file"].schema_sha256, expected_schema_hash)

    def test_explicit_task_allowlist_denial_is_not_reported_as_callable(self):
        env = self.make_env("allowlist", allowed_tool_ids=["fs.read_file"])
        observed = self.observe(env, "allowlist")

        tools = {tool.tool_id: tool for tool in observed.ecosystem.tools}
        self.assertEqual(tools["fs.write_file"].availability, "unavailable")
        self.assertEqual(tools["fs.write_file"].permission_state, "denied")

    def test_observer_requires_an_active_task_scope(self):
        workspace = self.root / "no-task"
        workspace.mkdir()
        (workspace / "README.md").write_text("# Observer fixture\n", encoding="utf-8")
        env = DHIEnvironment(workspace, catalogue=make_catalogue())

        with self.assertRaisesRegex(ValueError, "active task"):
            self.observe(env, "no-active-task")

    def test_discovery_changes_tool_availability_in_ecosystem_state(self):
        env = self.make_env("discovery")
        before = self.observe(env, "before-discovery")

        discovered = env.discover_tools("search text in files")
        self.assertTrue(any(item["tool_id"] == "fs.search_text" for item in discovered))
        after = self.observe(env, "after-discovery")

        delta = diff_joint_state(before, after)
        self.assertEqual(delta.world_changes, ())
        self.assertEqual(delta.tool_changes, (
            ToolChange("fs.search_text", "availability", "discoverable", "callable"),
        ))

    def test_workspace_action_changes_only_world_state_observation(self):
        env = self.make_env("workspace-change")
        before = self.observe(env, "before-write")

        result = env.run_action({
            "tool_id": "fs.append_file",
            "arguments": {"path": "README.md", "content": "Research note\n"},
        })
        self.assertTrue(result.ok)
        after = self.observe(env, "after-write")

        delta = diff_joint_state(before, after)
        self.assertEqual(len(delta.world_changes), 1)
        self.assertEqual(delta.world_changes[0].key, "file:README.md")
        self.assertEqual(delta.world_changes[0].operation, "update")
        self.assertEqual(delta.tool_changes, ())

    def test_catalogue_schema_drift_changes_only_ecosystem_observation(self):
        env = self.make_env("schema-drift")
        before = self.observe(env, "before-schema-drift")

        target = next(item for item in env.catalogue if item["tool_id"] == "fs.read_file")
        target["input_schema"]["properties"]["encoding"] = {"type": "string"}
        target["input_schema"]["properties"]["path"]["description"] = "Workspace-relative path."
        after = self.observe(env, "after-schema-drift")

        delta = diff_joint_state(before, after)
        self.assertEqual(delta.world_changes, ())
        schema_changes = [
            item for item in delta.tool_changes
            if item.tool_id == "fs.read_file" and item.field == "schema_sha256"
        ]
        self.assertEqual(len(schema_changes), 1)
        self.assertNotEqual(schema_changes[0].before, schema_changes[0].after)

    def test_joint_mechanism_test_detects_world_and_tool_drift_independently(self):
        env = self.make_env("joint-drift")
        before = self.observe(env, "joint-before")

        result = env.run_action({
            "tool_id": "fs.append_file",
            "arguments": {"path": "README.md", "content": "Changed world.\n"},
        })
        self.assertTrue(result.ok)
        target = next(item for item in env.catalogue if item["tool_id"] == "fs.read_file")
        target["input_schema"]["properties"]["encoding"] = {"type": "string"}
        after = self.observe(env, "joint-after")

        delta = diff_joint_state(before, after)
        self.assertEqual(len(delta.world_changes), 1)
        self.assertTrue(any(
            item.tool_id == "fs.read_file" and item.field == "schema_sha256"
            for item in delta.tool_changes
        ))


if __name__ == "__main__":
    unittest.main()
