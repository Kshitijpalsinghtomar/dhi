# DHI-v1 research code

This package contains research mechanisms for **DHI-v1 / Predictive Agentic Intelligence**. It is separate from the ORBIT task runner and does not itself constitute a learned model or measured capability.

## Joint task/world + tool-ecosystem state

- `joint_state.py` defines typed, independently sourced snapshots and diffs for task/world facts and tool-ecosystem state.
- `dhi_environment_observer.py` adapts the real deterministic `DHIEnvironment` into those observations without executing tools, performing discovery, writing events, or mutating task state.
- `DHIEnvironment` exposes detached read-only copies of the full configured catalogue, configured handler IDs, current task allowlist, and workspace snapshot policy.
- The observer requires an active task because visibility, discovery, and allowlist status are task-scoped.
- The observer reads the complete configured catalogue, not just visible or callable tools. It distinguishes visible/callable, hidden-but-discoverable, handler-disconnected, and task-policy-unavailable tools.
- The workspace scope incorporates a digest of the exact ignored-directory and snapshot-size policy. Snapshots with different coverage policies cannot be diffed as though they were the same scope.
- File state is represented by path and content SHA-256, not copied file contents.
- Catalogue `tags` are retrieval keywords, not verified capabilities. The observer reads capabilities only from an explicit `capabilities` field; otherwise they remain unknown.
- Required permission scopes are stored separately from granted permissions. A `permission_scope` label is not evidence of user consent. Permission state and grants remain unknown unless explicitly provided; an explicit task allowlist denial is represented as denied.
- Missing schema/capability metadata stays unknown (`None`); a known empty set is `()`.
- Renamed tool IDs are removal plus addition. No alias or semantic identity is inferred.
- An omitted forecast (`None`) is unscored; an empty forecast (`()`) is an explicit no-change prediction. World and ecosystem forecasts are scored separately.

## What the observer mechanism test proves

The deterministic observer tests use real `DHIEnvironment` instances and exercise:
- initial workspace and catalogue snapshots;
- tool visibility, catalogue discovery, disconnected handlers, and allowlist denial;
- exact input-schema fingerprints and unknown permission state;
- workspace snapshot-policy mismatch rejection;
- an actual authorized workspace action changing only world state;
- catalogue schema drift changing only ecosystem state;
- a combined world + ecosystem transition.

These tests establish that the DHI environment can expose the two state dimensions separately and that the diff contract can identify the changes. On 2026-11-11, the exact committed files passed 22/22 focused tests and compileall in Deepnote run `ca0c1e0e-bace-4927-ae65-5d83528eb59a`. They do **not** show that a model can predict those changes, discover tools well, plan, recover, or complete goals.

## Focused verification

From the repository root:

```bash
python -m unittest discover -s DHI_v1/research/tests -v
python -m compileall -q DHI_v1/research
```

Record the exact Git commit, command, exit code, and output for every verification claim. Do not substitute an old ORBIT regression report for verification of these files.

## Next research integration

Only after the observer tests pass:
1. Add a small deterministic, paired mechanism experiment with isolated availability/schema/permission/world-state changes and immutable before/after observations.
2. Freeze factors, scoring, and expected results before observing any model output.
3. Integrate with model predictions only after explicit model-run authorization and a funded/approved inference route. Predictions must be written before actions and never inserted into the observation records.

Do not modify `agent_runner.py` or enable model runs as part of this observer integration.
