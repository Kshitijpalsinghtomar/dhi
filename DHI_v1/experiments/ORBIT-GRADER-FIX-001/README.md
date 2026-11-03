# ORBIT-GRADER-FIX-001 — deterministic discovery recovery and branch-state scoring

**Status:** protocol committed; RED test execution pending  
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
