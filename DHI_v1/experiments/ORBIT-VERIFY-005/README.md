# ORBIT-VERIFY-005 — canonical plugin task-loader regression

<badge>PASS</badge> **Final status: all checks passed**

**Code under test:** `ea3269aec35527386804ac357a953933de31fbf0`  
**Branch:** `orbit/plugin-benchmark-fixture`  
**Verifier:** Deepnote project `6415944e-8d6c-432c-a7cf-3bbaa997799c`, notebook `3639f9a98ce5435fa4cd0168eaaca3a1`  
**Successful run:** `384fec58-6f67-407a-b599-301b3b9de74a`

## Question

Do the full benchmark/environment suites and package checks pass with the new fail-closed plugin task loader, canonical task IDs and policy-derived allowlists?

## Source identity

Exact Deepnote/GitHub match was confirmed for:
- `DHI_v1/benchmark/plugin_task_loader.py`
- `DHI_v1/benchmark/tests/test_plugin_task_loader.py`
- `DHI_v1/benchmark/fixtures/plugin_ecology/plugin_tool_registry.json`
- `DHI_v1/environment/agent_runner.py`
- `DHI_v1/environment/dhi_env.py`
- `DHI_v1/environment/tinyfish_client.py`

The full task manifest (4,704 lines, Git blob SHA `f1a73f4cc377f0ea72a37f7d2f9a3e7476ffe033`) matched exactly in 19 bounded chunks.

## TDD evidence

- Red: `a06e4d42-2093-42c2-90f4-83af4f85b52f` — new tests failed because the loader did not exist.
- Fixture path correction and validation-order fixes were made only after focused failures.
- Permission red: `39c767ed-d15f-45f7-9a81-869422c9461a` — seven passed, one failed as expected: an unrelated `external_purchase` permission incorrectly granted read-only access.
- Focused green: `0578c28c-9144-421e-87c0-ff7ca639ba31` — **8 passed** after explicit read-only permission mapping.

## Full regression result

- Manifest validator: **PASS** — valid=true, 30 tasks, Stage A=30, Stage B=0, no errors.
- Combined benchmark + environment pytest: **166 passed, 0 failed** in 384.195 seconds (pytest summary: 337.40 seconds).
- `compileall`: **PASS** — exit code 0.
- Entrypoint imports: **PASS**.
- Plugin task-loader smoke: **PASS** — all 30 task plans resolved; required tool IDs were subsets of allowed IDs; model runs enabled: **0**.
- Python: 3.13.18.
- No model inference, training, paid provider operation or external provider write was performed.

Full command output, exit codes, timings and environment details are archived in [results/verification-report.json](results/verification-report.json).

## Evidence boundary

This closes the **loader engineering regression** for the pinned code. It proves manifest and registry records can be resolved into safe task plans and that the broader suites still pass. It does not connect the manifest to the model-facing agent runner, implement GitHub or Firecrawl handlers, validate tasks end-to-end, demonstrate learned ORBIT capability, select a base model, or authorize training.

All 30 tasks remain authored/contract-checked and model execution stays disabled. The next work unit is the manifest-driven plugin execution bridge with canonical tool IDs, exact callable schemas, task-level handler checks, action traces and independent graders. Do not expand the Stage A manifest before that bridge is proven.

See [ORBIT launch-readiness audit](../../ORBIT_LAUNCH_READINESS_AUDIT_2026-11-03.md) and [live workspace](../../WORKSPACE.md).
