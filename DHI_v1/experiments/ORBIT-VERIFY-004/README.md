# ORBIT-VERIFY-004 — TinyFish adapter exact-head regression

**Status:** protocol frozen; awaiting execution  
**Code under test:** `5b144c531e8a548787918f0fcdf9e681f05d96e8`  
**Branch:** `orbit/plugin-benchmark-fixture`  
**Verifier:** Deepnote project `6415944e-8d6c-432c-a7cf-3bbaa997799c`, notebook `3639f9a98ce5435fa4cd0168eaaca3a1`

## Question

Do the complete benchmark and environment test suites, manifest validator, compileall and runner import smoke pass against the exact branch code that includes the TinyFish adapter?

## Frozen protocol

1. Confirm the Deepnote source files match the target GitHub commit.
2. Execute `python -m DHI_v1.benchmark.validate_task_manifest --json`.
3. Execute `python -m pytest -q DHI_v1/benchmark/tests DHI_v1/environment/tests`.
4. Execute `python -m compileall -q DHI_v1/benchmark DHI_v1/environment`.
5. Execute the explicit import smoke for `agent_runner`, `adaption_responses` and `benchmark.runner`.
6. Record exact stdout/stderr, return codes, elapsed time, Python version and commit under test.

The selected run must execute only the new ORBIT-VERIFY-004 cell. It must **not** execute the pre-existing saved regression cell, the TinyFish provider-probe cells, or the full notebook.

## Source identity check

Before execution, the following were compared between Deepnote and the GitHub branch: `agent_runner.py`, `dhi_env.py`, `fixture_manager.py`, their relevant tests, `tinyfish_client.py`, `test_tinyfish_client.py`, `plugin_trace.py`, `plugin_trace.schema.json`, task-manifest schema, manifest validator, and benchmark trace/manifest tests. All matched exactly.

The 4,704-line `task_manifest.json` was compared in 19 bounded line windows; all windows matched after removing the reader's terminal-newline convention.

## Evidence boundary

A pass establishes engineering/harness integrity for the frozen code only. It does not establish model capability, benchmark task validation, a base-model winner, training-data readiness, trained ORBIT weights, or launch readiness.

## Result

Pending. Do not infer success from a started or running job. Update this record only after retrieving the terminal run status and full outputs.


## Execution attempt 1 — runner bootstrap blocker

- Run: `72a2e697-89b4-4408-beba-c2185b2f95d1`
- Manifest validator: PASS — 30 tasks, Stage A=30, Stage B=0, no errors.
- Full pytest command: did not collect or execute tests; the live kernel returned `No module named pytest` immediately.
- Compileall: PASS.
- Entrypoint import smoke: PASS.
- Overall: BLOCKED by missing development dependency, not a test failure. This attempt is not counted as a suite pass.

## Execution attempt 2 — declared dependency bootstrap

- Run: `96ac3bf5-9a06-4a9f-9e80-3bc29c541f38`
- The selected verification cell now checks for `pytest` and `jsonschema` and installs only `DHI_v1/environment/requirements-dev.txt` when missing, then repeats the frozen four checks.
- Status at this update: running. Do not mark the experiment passed until its terminal run result and every command output are retrieved.
- The notebook's saved regression cell was not executed or modified.
