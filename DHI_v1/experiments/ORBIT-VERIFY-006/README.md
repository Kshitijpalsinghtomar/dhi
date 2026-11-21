# ORBIT-VERIFY-006 — plugin execution boundary exact-head regression

<badge>PASS</badge> **Final status: all checks passed**

**Code under test:** `410d1113231cef020dc72292ccf2496e580f803e`  
**Branch:** `orbit/plugin-benchmark-fixture`  
**Verifier:** Deepnote project `6415944e-8d6c-432c-a7cf-3bbaa997799c`, notebook `3639f9a98ce5435fa4cd0168eaaca3a1`  
**Successful run:** `6591b36d-6233-4443-b9e0-fbf4b0ac1197`

## Question

Do the full benchmark/environment suites and package checks pass with the manifest task loader and the new fail-closed plugin dispatch boundary?

## Source identity

Confirmed byte-for-byte between Deepnote and GitHub:
- `DHI_v1/benchmark/plugin_execution.py`
- `DHI_v1/benchmark/tests/test_plugin_execution.py`
- `DHI_v1/benchmark/plugin_task_loader.py`
- `DHI_v1/benchmark/tests/test_plugin_task_loader.py`
- `DHI_v1/benchmark/fixtures/plugin_ecology/plugin_tool_registry.json`
- `DHI_v1/benchmark/plugin_trace.py`
- `DHI_v1/benchmark/plugin_trace.schema.json`
- `DHI_v1/environment/agent_runner.py`
- `DHI_v1/environment/dhi_env.py`
- `DHI_v1/environment/tinyfish_client.py`

The task-manifest blob SHA is `f1a73f4cc377f0ea72a37f7d2f9a3e7476ffe033`, identical to ORBIT-VERIFY-005's 4,704-line manifest, which was compared in 19 bounded windows.

## Focused TDD evidence

- Red: `fbfaa878-9d54-4262-8ca0-a4e8a0e5cbcc` — test collection failed because `plugin_execution` did not yet exist.
- First implementation: `3320182b-af56-4b49-adb7-0f3bea45da47` — 7 passed, 1 failed because the test fixture omitted the write argument's `path` schema. The dispatch code correctly rejected invalid arguments before invoking the guard.
- Test fixture corrected to declare a string `path`.
- Focused green: `71251b83-84ba-4f7e-83a7-f87e8acd1a3c` — **8 passed**.

## Full exact-head result

- Manifest validator: **PASS** — valid=true, 30 tasks, Stage A=30, Stage B=0, no errors.
- Combined benchmark + environment pytest: **174 passed, 0 failed** in 384.86 seconds (pytest summary: 339.47 seconds).
- `compileall`: **PASS** — exit code 0.
- Entrypoint import smoke: **PASS**.
- Plugin manifest-loader smoke: **PASS** — all 30 task plans resolve, required IDs are permitted, **0 model runs enabled**.
- Synthetic plugin-dispatch smoke: **PASS** — canonical TinyFish function schemas prepared and one fake-handler call dispatched successfully.
- Provider calls / paid requests / training jobs: **0**.
- Python: 3.13.18.

Full commands, outputs, exit codes, timings and environment details are archived in [results/verification-report.json](results/verification-report.json).

## Evidence boundary

This closes the engineering regression for the manifest loader and fail-closed plugin preparation/dispatch boundary. It proves that:
- task IDs and permission allowlists are resolved from the pinned manifest/registry;
- missing handlers and schemas block preparation;
- visible-but-denied tools cannot be dispatched;
- JSON Schema arguments are validated before handler calls;
- sandbox-write tools need a task-specific guard that approves the exact arguments.

It does **not** connect the dispatch boundary to the full model loop, call GitHub/Firecrawl from Deepnote, validate tasks end-to-end, produce model-generated trajectories, or establish ORBIT capability.

All live manifest tasks remain `model_runs_allowed=false`. The next step is canonical TinyFish ID alignment and a real TinyFish handler/schema bundle, followed by a credentialed GitHub runtime adapter. Firecrawl Alexandria's exact connected-tool contract is known, but no Deepnote project transport/integration is attached. See [WORKSPACE.md](../../WORKSPACE.md) and [ORBIT launch-readiness audit](../../ORBIT_LAUNCH_READINESS_AUDIT_2026-11-03.md).
