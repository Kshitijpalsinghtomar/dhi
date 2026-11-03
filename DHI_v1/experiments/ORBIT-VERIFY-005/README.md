# ORBIT-VERIFY-005 — canonical plugin task-loader regression

**Status:** protocol frozen; awaiting execution  
**Code under test:** `ea3269aec35527386804ac357a953933de31fbf0`  
**Branch:** `orbit/plugin-benchmark-fixture`  
**Verifier:** Deepnote project `6415944e-8d6c-432c-a7cf-3bbaa997799c`, notebook `3639f9a98ce5435fa4cd0168eaaca3a1`

## Question

Do the full benchmark/environment suites and package checks pass with the new fail-closed plugin task loader, canonical task IDs and policy-derived allowlists?

## Frozen checks

1. Confirm source identity for the loader, loader tests, plugin registry, runner/environment, TinyFish adapter and all relevant schemas.
2. Confirm the 4,704-line task manifest matches GitHub in bounded line windows.
3. Run manifest validation.
4. Run all benchmark and environment pytest tests.
5. Run compileall and the runner/adapter import smoke.
6. Save stdout, stderr, exit codes, elapsed times, Python/platform and exact code commit.

Only the new ORBIT-VERIFY-005 selected block is to be executed. The original saved regression cell and all provider-probe cells remain untouched.

## Source identity

Exact Deepnote/GitHub match was confirmed for:
- `DHI_v1/benchmark/plugin_task_loader.py`
- `DHI_v1/benchmark/tests/test_plugin_task_loader.py`
- `DHI_v1/benchmark/fixtures/plugin_ecology/plugin_tool_registry.json`
- `DHI_v1/environment/agent_runner.py`
- `DHI_v1/environment/dhi_env.py`
- `DHI_v1/environment/tinyfish_client.py`

The full task manifest (4,704 lines, Git blob SHA `f1a73f4cc377f0ea72a37f7d2f9a3e7476ffe033`) matched exactly in 19 bounded chunks. The trace schema, manifest schema, validator and existing grader tests were checked in ORBIT-VERIFY-004 and have not changed in the intervening loader-only work.

## TDD evidence

- Red: `a06e4d42-2093-42c2-90f4-83af4f85b52f` — new tests failed at module import because the loader did not exist yet.
- Initial implementation path correction: `de8dfff9-4fc6-4ff1-839d-a4def647fa44` — seven fixture path failures; incorrect test root was corrected.
- Policy diagnostic ordering: `9abb2f74-819c-4c46-a6af-7f92a232a698` — six passed, one assertion failed because unknown tool IDs were reported as inventory mismatch before registry absence; validation order was corrected.
- Explicit permission red test: `39c767ed-d15f-45f7-9a81-869422c9461a` — seven passed, one failed as expected: unrelated `external_purchase` permission incorrectly granted a read-only tool.
- Focused green: `0578c28c-9144-421e-87c0-ff7ca639ba31` — **8 passed** after the explicit read-only permission mapping.

## Evidence boundary

The task loader is a validated policy/manifest boundary, not a provider dispatcher and not a model capability result. The full regression only establishes that the loader and related tests do not regress the rest of the codebase. It does not enable model inference: all current task manifest records have `model_runs_allowed=false`.
