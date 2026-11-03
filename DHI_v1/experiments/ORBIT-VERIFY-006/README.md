# ORBIT-VERIFY-006 — plugin execution boundary exact-head regression

**Status:** prepared  
**Code under test:** `410d1113231cef020dc72292ccf2496e580f803e`  
**Branch:** `orbit/plugin-benchmark-fixture`  
**Verifier:** Deepnote project `6415944e-8d6c-432c-a7cf-3bbaa997799c`, notebook `3639f9a98ce5435fa4cd0168eaaca3a1`

## Question

Do the full benchmark/environment suites and package checks pass with the manifest task loader and the new fail-closed plugin dispatch boundary?

## Frozen checks

1. Confirm the key implementation, test, registry, trace, schema, environment and adapter files match the pinned GitHub branch.
2. Confirm the task manifest is the previously verified immutable blob `f1a73f4cc377f0ea72a37f7d2f9a3e7476ffe033`.
3. Run manifest validation.
4. Run all benchmark and environment pytest tests.
5. Run compileall and entrypoint import smoke.
6. Resolve all 30 task plans and confirm model execution remains disabled in the source manifest.
7. Prepare a synthetic TinyFish-like read-only task using local fake handlers and dispatch one schema-valid call. Do not contact TinyFish or any other provider.
8. Save stdout, return codes, elapsed times, Python/platform and exact commit.

Only the ORBIT-VERIFY-006 selected block is to be executed. The notebook's original saved regression cell and all provider-probe cells remain untouched.

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

Task-manifest blob SHA is `f1a73f4cc377f0ea72a37f7d2f9a3e7476ffe033`, identical to ORBIT-VERIFY-005's 4,704-line manifest, which was compared in 19 bounded windows.

## Focused TDD evidence

- Red: `fbfaa878-9d54-4262-8ca0-a4e8a0e5cbcc` — test collection failed because plugin_execution did not yet exist.
- First implementation: `3320182b-af56-4b49-adb7-0f3bea45da47` — 7 passed, 1 failed because the test fixture omitted the write argument's `path` schema. The dispatch code correctly rejected the invalid arguments before invoking the guard.
- Fixture corrected to require a string `path`.
- Focused green: `71251b83-84ba-4f7e-83a7-f87e8acd1a3c` — **8 passed**.

## Evidence boundary

This verifies the fail-closed preparation/dispatch boundary with local synthetic handlers. It does not connect any real provider, wire the boundary into the full model loop, produce ORBIT trajectories, or establish model capability.
