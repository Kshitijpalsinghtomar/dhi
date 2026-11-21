# ORBIT-S09-002-BASELINE-CONTAMINATION-001

**Task:** ORBIT-A-S09-002  
**Date:** 2026-11-05  
**Status:** Environment reset prerequisite is stale; no task write was executed.

## Finding

The pinned `branch_state_before.json` snapshot was captured on 2026-11-03 and lists only three branch heads:
- `main`
- `orbit/plugin-benchmark-fixture`
- `orbit/plugin-resume-sandbox`

The current DHI repository contains 11 branches. The target branch named in the task, `orbit/effect-forecast-check`, already exists at the expected base commit. Therefore the task's original precondition ("target branch must be absent") is false, and its current before-state snapshot is no longer representative.

## Current branch set

The complete observed branch/head set is retained in `manifest.json`. Key observation:
- `orbit/effect-forecast-check` exists at `af6c0d31fcf2e3232cb427c421850536139e3b3a`.
- The other benchmark sandbox branches were created for independent task work.
- No branch was deleted, reset, or overwritten in this check.

## Consequence

Do not run ORBIT-A-S09-002 against the stale snapshot. A clean future trial requires a new pinned before-state that includes all current heads and a target branch name not already present (or a genuinely isolated repository fixture). Recompute and pin the environment state hash and task-instance fingerprint before the task is re-enabled.

This is an environment contamination finding, not a task failure and not evidence of model capability. Model execution remains disabled.


## Live recheck — 2026-11-21

A new read-only GitHub `/branches?per_page=100` inventory confirms **13 branches**. The original 2026-11-03 three-branch snapshot is not a valid current before-state. The task target still exists at exactly the commit the task would attempt to create it from.

| Branch | Current head |
|---|---|
| `main` | `c640e7152885e8c4e0171afd69b9a50ec711636a` |
| `orbit/effect-forecast-check` | `af6c0d31fcf2e3232cb427c421850536139e3b3a` |
| `orbit/effect-forecast-update` | `a24a2c3999d18dc2f2d1c876d5785a77b1539652` |
| `orbit/plugin-benchmark-fixture` | `276b5278e43f421abb15209d67a1c2c5536c7fcc` |
| `orbit/plugin-resume-sandbox` | `d3f7ca37a8623ef6e5f5b3ed4e60f88a2a8efb1c` |
| `orbit/s06-runtime-report` | `ef28038a295403e4928c7a74ee5dae0cec5996a9` |
| `orbit/s09-effect-prediction` | `9853da932b925426ee445af7b4c2fc9bf85f8824` |
| `orbit/sandbox/orbit-a-s06-001` | `60d02d29220d4f85a007f9677f1d26e4c31a8e0a` |
| `orbit/sandbox/orbit-a-s07-001` | `ee4215bf6f71e3d901987465fc1cf7eee10a2456` |
| `orbit/sandbox/orbit-a-s07-002` | `a9c95537f42c992ba0ec5f9321c6b37304ca5910` |
| `orbit/sandbox/orbit-a-s09-001` | `a2df221f0eeaf1ec5fb8f5f116d8144de6d315f5` |
| `orbit/sandbox/orbit-a-s09-003` | `c168564457562ed01a621349b82ae41fe6a2f668` |
| `orbit/tool-ecosystem-audit` | `466d2bfef06dbf87729ff625f9f27688ce500321` |

No branch was created, deleted, reset or updated during this recheck. In particular, `orbit/effect-forecast-check` remains a retained task fixture at the expected base SHA. The original pinned `branch_state_before.json` and original 2026-11-05 experiment manifest are preserved as historical evidence.

**Decision:** keep ORBIT-A-S09-002 blocked. Do not force the original operation through against a contaminated baseline. Before any future execution, either prepare a genuinely isolated repository fixture or update the task to a unique target branch and a complete fresh before-state; then recompute `environment.state_sha256`, `task_instance_sha256` and validate the exact manifest. Do not delete or overwrite the retained branch to manufacture a passing precondition.
