# ORBIT-VERIFY-003 — combined benchmark and environment regression

**Status:** passed  
**Code under test:** `421955df46975d8b20fba63f8922949a49b4551c`  
**Documentation branch at session start:** `ac153edc657167847523fe5257d6b53fff572261`  
**Branch:** `orbit/plugin-benchmark-fixture`

## Question

Do the DHI benchmark suite and the supporting environment / model-runner suite pass together on the exact code revision already used for the benchmark-only verification?

## Frozen scope and commands

The isolated Deepnote verifier project runs these commands in order:

1. `python -m DHI_v1.benchmark.validate_task_manifest --json`
2. `python -m pytest -q DHI_v1/benchmark/tests DHI_v1/environment/tests`
3. `python -m compileall -q DHI_v1/benchmark DHI_v1/environment`
4. Import smoke for `agent_runner`, `adaption_responses`, and `benchmark.runner`.

The two test directories currently contain 136 declared `test_*` functions (82 benchmark and 54 environment). The collected pytest count and outcomes are not yet known.

## Execution record

- Runner: existing isolated Deepnote project `6415944e-8d6c-432c-a7cf-3bbaa997799c`
- Notebook: `3639f9a98ce5435fa4cd0168eaaca3a1`
- Run: `f661f5ad-7c5e-48b9-9af6-afda1e6f021b`
- Python: 3.13 environment (exact interpreter string to be copied from the completed run report)
- Model inference: none
- Training / dataset generation: none
- Provider credits: none requested or spent by this verification.

The detached run was launched before its experiment manifest was committed. This is a process deviation from the commit-before-run rule in the ORBIT method; it is recorded rather than concealed. The tested code revision is explicitly pinned above and the run is for regression only.

## Result

<badge>PASS</badge> All checks passed against code commit `421955df46975d8b20fba63f8922949a49b4551c`.

| Check | Result |
|---|---|
| Manifest validator | PASS — 30 tasks; Stage A=30; Stage B=0; no errors |
| Combined benchmark + environment tests | **136 passed, 0 failed** |
| Compile benchmark + environment | PASS — exit code 0 |
| Runner / adapter import smoke | PASS — exit code 0 |

Pytest reported `136 passed in 377.05s`; the enclosing subprocess wall-time record was 502.268 seconds. The verifier ran under Python 3.13.18. All required repository files were present.

Full command output, stdout/stderr, timings, and return codes are archived in [results/verification-report.json](results/verification-report.json). Deepnote run: `f661f5ad-7c5e-48b9-9af6-afda1e6f021b`.

Do not change task validation status based on this regression run.

## Evidence boundary

Even a full pass only establishes deterministic code / harness health. It does not establish model capability, model-generated trajectories, a validated or frozen Stage A panel, a model winner, training readiness, or launch readiness.
