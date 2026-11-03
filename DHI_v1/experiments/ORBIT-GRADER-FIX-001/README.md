# ORBIT-GRADER-FIX-001 — deterministic discovery recovery and branch-state scoring

**Status:** full regression passed — 142 tests, 0 failures; manifest validation, compileall and runner import smoke also passed  
**Branch:** `orbit/plugin-benchmark-fixture`  
**Baseline code:** `49e2ee031b18280206d8d4cc1f33c0e9c272e55b`

## Question

Can the plugin trace grader reliably score the two Stage A predicates currently marked unscorable by the implementation: `discovery_sequence` (S08-002) and `branch_state_delta` (S09-002), while requiring evidence from ordered observations and pre-action model predictions?

## Hypothesis

A normalized, ordered plugin trace can provide deterministic evidence for both mechanisms:
- Firecrawl recovery: a broad degraded discovery response contains candidate items and a continuation, followed by a provider-filtered successful contract with exact required inputs and separate discovery/execution costs.
- GitHub branch effects: the trace contains a pre-action structured prediction, an independently observed branch list before the create action, and an independently fetched branch list after it. The new branch must point to the specified base; every prior branch head must remain unchanged; no file changes or paid actions may occur.

## Null and falsifier

Null: the available trace evidence is insufficient or ambiguous, so the grader must return unscorable/fail rather than pass.

Falsifiers include:
- scoped search without the prior fallback;
- no candidate items or continuation in the fallback;
- provider/capability/input/cost mismatch;
- any provider execution or credit spend;
- prediction after the create action;
- missing before/after branch observations;
- wrong base SHA, extra branch, deleted branch, modified existing branch, or file mutation.

## Frozen scope

- Primary code: `DHI_v1/benchmark/plugin_trace.py`
- Trace contract: `DHI_v1/benchmark/plugin_trace.schema.json`
- Tests: `DHI_v1/benchmark/tests/test_plugin_trace_grader.py`
- Task contracts: `ORBIT-A-S08-002`, `ORBIT-A-S09-002` in `benchmark/task_manifest.json`
- No model inference, training, paid provider execution, or task status promotion.

## Initial RED attempt

Test-only candidate commit: `49e2ee031b18280206d8d4cc1f33c0e9c272e55b`.

The first detached Deepnote attempt (`db19bd2b-a005-42d0-a269-385d8e5de3ae`) did not reach pytest because that run environment did not have pytest installed (`No module named pytest`). This is an environment setup failure, not a test failure and not evidence for or against the hypothesis. The next attempt installs only `DHI_v1/environment/requirements-dev.txt` before running the focused tests.

## Decision rule

Keep only if the new regression tests demonstrate both supported conditions and reject the counterexamples above, the manifest validator accepts the task panel, and the full benchmark/environment suites pass. Otherwise reject or revise the adapter; never weaken the evidence requirements.


## Initial full regression result — 2026-11-03 (superseded by final pass)

Deepnote run `43e0726e-e16d-428c-b2dd-f18332e2f882` executed against code head `92bec2c3485220eec6c80a7fe8ae41865a4ef54e`.

- Cross-record manifest validator: **PASS** — 30 tasks, Stage A=30, Stage B=0, no errors.
- Benchmark + environment pytest suite: **141 passed, 1 failed**.
- The single failure was `test_runner_exposes_structured_repository_branch_forecast_schema`: the test expected a nested `$defs` object, while the emitted schema deliberately contains inline branch item schemas. This is a test-contract mismatch, not evidence of a grader failure.
- The active branch subsequently updated that assertion to inspect the inline schema directly (test file blob `269e5c9c3f7c678d0da56529b4d36798daca404e`).
- A rerun was attempted, but Deepnote refused a new run because the account's parallel-project quota was exceeded. The DHI verifier machine itself was stopped. No other project was stopped or modified.
- Therefore the corrected full suite is **not yet verified**. Compileall/import smoke did not run because the combined script stopped after pytest failed.

Next: rerun the focused schema test, then the full benchmark + environment suite on the current branch head once Deepnote capacity is available. Do not mark the suite green based on the source correction alone.


## Final full regression adjudication — 2026-11-03

The corrected test and full benchmark/environment regression **passed** in Deepnote run `34ca752c-e864-4a3d-9388-957d2c3e1859`, tested against code commit `cba8421d4f4c6c4f929d5f4c3196eb83f98f7351`.

- Manifest validator: **PASS** — 30 task records, Stage A=30, Stage B=0, zero errors.
- Benchmark + environment pytest suites: **142 passed, 0 failed**.
- Compile check: `python -m compileall -q DHI_v1/benchmark DHI_v1/environment` — exit 0.
- Import smoke for `agent_runner`, `adaption_responses`, and `benchmark.runner` — passed.
- All four verification commands returned exit code 0.
- Python: 3.13.18.

Raw evidence is retained in the isolated Deepnote verifier:
- Project: `6415944e-8d6c-432c-a7cf-3bbaa997799c`
- Notebook: `3639f9a98ce5435fa4cd0168eaaca3a1`
- Run: `34ca752c-e864-4a3d-9388-957d2c3e1859` (terminal status `success`)
- Output block: `43e281b25689485a9ff1c31e7cbfcbdc`
- Snapshot block content hash: `sha256:4a6a556b2ed08feb83f3119939e2642756b5701b36f85d1645f176b66aad25b5`
- Machine-readable report: `grader-fix-full-report-final.json`

The active branch head is now `43608791494e445b17556e1ec8fc08b8a9f2f455`. Comparing `cba8421d4f4c6c4f929d5f4c3196eb83f98f7351` to that head shows six commits containing only documentation/record changes (`WORKSPACE.md`, the decision log, this experiment README, and its manifest); no runtime or test source changed after the passing run. The 142-test result therefore covers the current branch's code and test files.

A later focused retry, run `b401c21c-d586-4a69-8e69-80c6cf02ae43`, failed before collection because that notebook cell did not install the declared development requirements and `pytest` was absent. An earlier retry `220cc301-c5de-4c33-b507-784d456935d6` stopped without output. Neither is a code-test failure and neither supersedes the completed full pass. The notebook bootstrap should install `DHI_v1/environment/requirements-dev.txt` before any future isolated run.

**Decision:** close the full regression gate for the current runtime/test code. This establishes harness/code health only. It does not validate any Stage A task through model execution, establish model capability, authorize training, or open the external-plugin execution gate.
