# ORBIT-VERIFY-012 — trusted task-scoped GitHub runtime exact-head regression

**Status:** PASS — full exact-head offline regression passed.
**Code under test:** `7f244bf76ccbccec5477b0055d23da5a5931e27a`
**Branch:** `orbit/plugin-benchmark-fixture`

## Scope

This verification covers the task-scoped GitHub runtime introduced after ORBIT-VERIFY-011. The runtime binds all provider-sensitive operations to one task, repository, disposable branch and manifest-derived output path set:

1. **Precondition observer:** reads the exact sandbox branch ref and head SHA, then compares the observed head with the manifest-pinned `branch_head_equals` commit. Missing, malformed, mismatched or unavailable observations fail closed before model execution.
2. **State observer:** uses the same GitHub client to compare the pinned base commit with the sandbox branch. Each changed path is fingerprinted from its provider-reported change status and blob SHA. The full changed-path set is preserved for independent before/after grading, so out-of-allowlist modifications cannot be hidden.
3. **Write guard:** binds create/update operations to the configured repository, the task-derived sandbox branch, and paths explicitly allowed by the task's postconditions.
4. **Artifact reader:** independently fetches the final file from the same repository, branch and approved path after a successful write. The plugin runner verifies the returned content against its Git blob SHA before placing it in `trace.final_artifacts`.
5. **Runner wrapper:** `run_github_plugin_task` supplies the precondition, state and artifact callbacks itself. Callers cannot replace or omit the trusted state observer.

The runner sequence is now `task_started → precondition checks → baseline state observation → model`. If a precondition fails or is unavailable, the task closes blocked without querying repository state or calling the model.

## Deepnote execution

- Project: `6415944e-8d6c-432c-a7cf-3bbaa997799c`
- Notebook: `3639f9a98ce5435fa4cd0168eaaca3a1`
- Full verifier block: `d76385ef1ba24707ae3f97b7bef2987e`
- Full verifier run: `3f2f3b31-86db-46f3-a731-f9f4c502435d`
- Focused trusted-runtime/runner regression: `9bd9c829-ff96-49a4-8eee-82b6b0bc4ba8` — 45 passed
- Python: 3.13.18
- Platform: Linux
- Finished: 2026-11-05T07:48:16Z

## Results

| Gate | Result |
|---|---|
| Manifest validator | PASS — 30 tasks; Stage A=30; Stage B=0; no errors |
| Full benchmark + environment pytest | **224 passed, 0 failed** |
| `compileall` | PASS |
| Entrypoint import smoke | PASS |
| Plugin task loader | PASS — 30 plans; 0 model runs enabled |
| Full verifier | PASS — all five commands exited 0 |

The raw verifier report retains exact command arguments, outputs, return codes and timings in [verification-report.json](results/verification-report.json).

## Evidence boundary

This is offline engineering/harness verification only:
- GitHub calls during tests used fake HTTP transport; no live GitHub request or repository write occurred.
- No TinyFish request, hosted-model inference, training job or dataset-generation job was run.
- The fake HTTP path verified the actual `GitHubReadWriteClient` request/handler boundary, but not a live credentialed GitHub runtime.
- All 30 source-manifest `model_runs_allowed` flags remain `false`.
- All 30 Stage A tasks remain `ready_for_validation`, not `validated`; Stage B remains sealed and empty.
- No ORBIT model capability score, learned task trajectory or training result is established.

## Remaining blockers

1. **Live provider configuration:** the Deepnote project has not been provisioned with a project-scoped `GITHUB_TOKEN`, write-enable flag and repository allowlist. No live request was attempted.
2. **Sandbox branch provisioning:** the dedicated task branch must be created/reset to the exact manifest-pinned base SHA before any future S06 run. The runtime will block if this precondition is not true.
3. **Task validation:** independent reviewer/grader validation for the 30 Stage A tasks is still outstanding.
4. **Model access and capability evidence:** no comparable untouched-model inference or execution trajectories exist; training remains unauthorized.

## Next authorized work unit

Provision credentials and a disposable sandbox branch only after the separate access and isolation gate is approved. Then perform a controlled S06 provider smoke test with a live precondition read, one approved report write, independent readback and branch diff. Do not enable general model runs; keep all 30 manifest flags false until task-level validation and model-access gates are separately closed.
