# ORBIT-VERIFY-004 — TinyFish adapter exact-head regression

<badge>PASS</badge> **Final status: all checks passed**

**Code under test:** `5b144c531e8a548787918f0fcdf9e681f05d96e8`  
**Branch:** `orbit/plugin-benchmark-fixture`  
**Verifier:** Deepnote project `6415944e-8d6c-432c-a7cf-3bbaa997799c`, notebook `3639f9a98ce5435fa4cd0168eaaca3a1`  
**Successful run:** `96ac3bf5-9a06-4a9f-9e80-3bc29c541f38`

## Question

Do the complete benchmark and environment test suites, manifest validator, compileall and runner import smoke pass against the exact branch code that includes the TinyFish adapter?

## Frozen protocol

1. Confirm the Deepnote source files match the target GitHub code commit.
2. Execute `python -m DHI_v1.benchmark.validate_task_manifest --json`.
3. Execute `python -m pytest -q DHI_v1/benchmark/tests DHI_v1/environment/tests`.
4. Execute `python -m compileall -q DHI_v1/benchmark DHI_v1/environment`.
5. Execute the explicit import smoke for `agent_runner`, `adaption_responses` and `benchmark.runner`.
6. Record exact stdout/stderr, return codes, elapsed time, Python version and code commit under test.

The selected run executed only the new ORBIT-VERIFY-004 cell. It did **not** execute the pre-existing saved regression cell, either TinyFish provider-probe cell, or the full notebook.

## Source identity check

Before execution, the following were compared between Deepnote and the GitHub branch: `agent_runner.py`, `dhi_env.py`, `fixture_manager.py`, their relevant tests, `tinyfish_client.py`, `test_tinyfish_client.py`, `plugin_trace.py`, `plugin_trace.schema.json`, task-manifest schema, manifest validator, and benchmark trace/manifest tests. All matched exactly.

The 4,704-line `task_manifest.json` was compared in 19 bounded line windows; all windows matched after removing the reader's terminal-newline convention.

## Final result

- Manifest validator: **PASS** — valid=true, 30 tasks, Stage A=30, Stage B=0, no errors.
- Combined benchmark + environment pytest: **158 passed, 0 failed** in 458.367 seconds (pytest's own summary: 336.03 seconds).
- `compileall`: **PASS** — exit code 0.
- Runner / adapter import smoke: **PASS** — exit code 0.
- Development dependency bootstrap: **PASS** — installed only the repository-declared `pytest>=8.0,<10` and found `jsonschema>=4.21,<5` already satisfied.
- Interpreter: Python 3.13.18.

Full output, commands, return codes and timings are archived in [results/verification-report.json](results/verification-report.json).

## First attempt and correction

Run `72a2e697-89b4-4408-beba-c2185b2f95d1` passed manifest validation, compileall and import smoke, but pytest did not start because the live kernel lacked the `pytest` package. It was a runner bootstrap blocker, not a test failure.

The successful retry installed only the pinned repository development requirements before executing the full frozen suite. No source code was changed between attempts.

## Evidence boundary

This closes the **engineering regression gate** for the pinned adapter code. It does not establish plugin-manifest-to-runner integration, model capability, benchmark task validation, a base-model winner, training-data readiness, trained ORBIT weights, or launch readiness.

The 30 plugin-native tasks are still authored/contract-checked but not executable end-to-end through the current model runner. See [ORBIT_LAUNCH_READINESS_AUDIT_2026-11-03.md](../../ORBIT_LAUNCH_READINESS_AUDIT_2026-11-03.md) and [WORKSPACE.md](../../WORKSPACE.md).
