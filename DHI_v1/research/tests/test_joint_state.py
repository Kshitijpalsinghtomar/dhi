import unittest

from DHI_v1.research.joint_state import (
    ObservedJointState, PredictedJointEffects, TaskWorldState,
    ToolEcosystemState, ToolState, WorldFact, WorldChange, ToolChange,
    diff_joint_state, score_joint_effects,
)

HASH_A = "a" * 64
HASH_B = "b" * 64


def joint_state(*, world=(), tools=(), revision="r1"):
    return ObservedJointState(
        task=TaskWorldState(revision, "workspace:test", True, tuple(world), f"world:{revision}"),
        ecosystem=ToolEcosystemState(revision, "catalogue:test", True, tuple(tools), f"tools:{revision}"),
    )


class JointStateDiffTests(unittest.TestCase):
    def test_diff_tracks_world_and_ecosystem_changes_separately(self):
        before = joint_state(
            world=[WorldFact("file:report.md", "absent")],
            tools=[ToolState("repo.read", HASH_A, ("read_file",), "callable", "granted")],
            revision="before",
        )
        after = joint_state(
            world=[WorldFact("file:report.md", "present")],
            tools=[ToolState("repo.read", HASH_B, ("read_file", "read_directory"), "callable", "granted")],
            revision="after",
        )
        delta = diff_joint_state(before, after)
        self.assertEqual(delta.world_changes, (
            WorldChange("update", "file:report.md", "absent", "present"),
        ))
        self.assertEqual(delta.tool_changes, (
            ToolChange("repo.read", "capabilities", '[ "read_file" ]'.replace(" ", ""), '[ "read_directory", "read_file" ]'.replace(" ", "")),
            ToolChange("repo.read", "schema_sha256", HASH_A, HASH_B),
        ))

    def test_renamed_tool_is_add_and_remove_not_assumed_identity(self):
        before = joint_state(tools=[ToolState("repo.read", HASH_A, ("read_file",), "callable", "granted")])
        after = joint_state(tools=[ToolState("github.fetch_file", HASH_A, ("read_file",), "callable", "granted")])
        self.assertEqual(diff_joint_state(before, after).tool_changes, (
            ToolChange("github.fetch_file", "presence", None, "present"),
            ToolChange("repo.read", "presence", "present", None),
        ))

    def test_partial_catalogue_cannot_infer_tool_removal(self):
        before = joint_state(tools=[ToolState("repo.read", HASH_A, ("read_file",), "callable", "granted")])
        after = ObservedJointState(
            TaskWorldState("r2", "workspace:test", True, (), "world:r2"),
            ToolEcosystemState("r2", "catalogue:test", False, (), "tools:r2"),
        )
        with self.assertRaisesRegex(ValueError, "incomplete"):
            diff_joint_state(before, after)

    def test_incomplete_world_snapshot_cannot_infer_fact_removal(self):
        before = joint_state(world=[WorldFact("file:x", "present")])
        after = ObservedJointState(
            TaskWorldState("r2", "workspace:test", False, (), "world:r2"),
            ToolEcosystemState("r2", "catalogue:test", True, (), "tools:r2"),
        )
        with self.assertRaisesRegex(ValueError, "incomplete"):
            diff_joint_state(before, after)

    def test_incompatible_scopes_are_rejected(self):
        before = joint_state(world=[WorldFact("file:x", "present")])
        after = ObservedJointState(
            TaskWorldState("r2", "other-workspace", True, (), "world:r2"),
            ToolEcosystemState("r2", "catalogue:test", True, (), "tools:r2"),
        )
        with self.assertRaisesRegex(ValueError, "scope"):
            diff_joint_state(before, after)

    def test_unknown_schema_and_capabilities_stay_unknown_until_observed(self):
        before = joint_state(tools=[ToolState("repo.read", None, None, "unknown", "unknown")])
        after = joint_state(tools=[ToolState("repo.read", HASH_A, ("read_file",), "callable", "granted")])
        changes = diff_joint_state(before, after).tool_changes
        by_field = {change.field: change for change in changes}
        self.assertIsNone(by_field["schema_sha256"].before)
        self.assertEqual(by_field["schema_sha256"].after, HASH_A)
        self.assertEqual(by_field["capabilities"].before, None)

    def test_duplicate_tool_ids_are_rejected(self):
        with self.assertRaises(ValueError):
            joint_state(tools=[
                ToolState("repo.read", HASH_A, ("read_file",), "callable", "granted"),
                ToolState("repo.read", HASH_A, ("read_file",), "callable", "granted"),
            ])

    def test_bad_schema_digest_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            ToolState("repo.read", "not-a-hash", ("read_file",), "callable", "granted")

    def test_required_permission_scope_is_distinct_from_granted_permissions(self):
        before = joint_state(tools=[ToolState(
            "repo.write", HASH_A, None, "callable", "unknown",
            permissions=None, required_permission_scopes=("workspace_write",),
        )])
        after = joint_state(tools=[ToolState(
            "repo.write", HASH_A, None, "callable", "unknown",
            permissions=("workspace_write",), required_permission_scopes=("workspace_write",),
        )])
        changes = diff_joint_state(before, after).tool_changes
        self.assertEqual(changes, (
            ToolChange("repo.write", "permissions", None, '["workspace_write"]'),
        ))

    def test_world_add_and_remove_are_explicit(self):
        before = joint_state(world=[WorldFact("file:old", "present")])
        after = joint_state(world=[WorldFact("file:new", "present")])
        self.assertEqual(diff_joint_state(before, after).world_changes, (
            WorldChange("add", "file:new", None, "present"),
            WorldChange("remove", "file:old", "present", None),
        ))


class JointPredictionScoringTests(unittest.TestCase):
    def test_world_and_ecosystem_predictions_score_independently(self):
        before = joint_state(
            world=[WorldFact("file:report.md", "absent")],
            tools=[ToolState("repo.read", HASH_A, ("read_file",), "callable", "granted")],
            revision="before",
        )
        after = joint_state(
            world=[WorldFact("file:report.md", "present")],
            tools=[ToolState("repo.read", HASH_B, ("read_file",), "callable", "granted")],
            revision="after",
        )
        prediction = PredictedJointEffects(
            world_changes=(WorldChange("update", "file:report.md", "absent", "present"),),
            tool_changes=(ToolChange("repo.read", "schema_sha256", HASH_A, HASH_B),),
        )
        score = score_joint_effects(prediction, before, after)
        self.assertTrue(score.world.exact_match)
        self.assertTrue(score.ecosystem.exact_match)
        self.assertEqual(score.world.f1, 1.0)
        self.assertEqual(score.ecosystem.f1, 1.0)

    def test_omitted_forecast_is_unscored_but_empty_forecast_is_scored(self):
        before = joint_state(world=[WorldFact("file:x", "absent")])
        after = joint_state(world=[WorldFact("file:x", "present")])
        omitted = score_joint_effects(PredictedJointEffects(), before, after)
        explicit_no_change = score_joint_effects(PredictedJointEffects(world_changes=()), before, after)
        self.assertEqual(omitted.world.status, "not_predicted")
        self.assertEqual(explicit_no_change.world.status, "scored")
        self.assertFalse(explicit_no_change.world.exact_match)
        self.assertEqual(explicit_no_change.world.recall, 0.0)

    def test_explicit_no_change_is_correct_when_nothing_changed(self):
        before = joint_state(world=[WorldFact("file:x", "absent")])
        after = joint_state(world=[WorldFact("file:x", "absent")])
        score = score_joint_effects(PredictedJointEffects((), ()), before, after)
        self.assertTrue(score.world.exact_match)
        self.assertTrue(score.ecosystem.exact_match)
        self.assertEqual(score.world.f1, 1.0)
        self.assertEqual(score.ecosystem.f1, 1.0)

    def test_unknown_permission_is_not_promoted_to_granted(self):
        before = joint_state(tools=[ToolState("repo.write", HASH_A, ("write_file",), "callable", "unknown")])
        after = joint_state(tools=[ToolState("repo.write", HASH_A, ("write_file",), "callable", "denied")])
        self.assertEqual(diff_joint_state(before, after).tool_changes, (
            ToolChange("repo.write", "permission_state", "unknown", "denied"),
        ))


if __name__ == "__main__":
    unittest.main()
