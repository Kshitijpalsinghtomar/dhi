# VERIFY-001 — DHI-v1 repository verification

**Date:** 2026-11-02  
**Status:** RUNNING  
**Pinned revision:** `c2e0dddaa6eb22d0c4722fc7fb43f2c2439c7c61`  
**Programme:** DHI-v1 / ORBIT  
**Type:** implementation verification only; not a model experiment.

## Question

Does the current checked-in DHI-v1 environment and benchmark test suite pass at the pinned repository revision in a clean Python 3.11 Deepnote runtime?

## Scope

Run:
1. `python -m pytest -q DHI_v1/environment/tests DHI_v1/benchmark/tests`
2. `python -m compileall -q DHI_v1`

Use a clean detached Deepnote run with read-only project storage. Clone/fetch the exact commit listed above into ephemeral runtime storage; do not mutate the Git repo or use the older mixed DHI/DPAK project.

## Boundaries

- No model inference.
- No Adaption endpoint call.
- No dataset generation or training.
- No Adaption credit spend.
- No claim about agent capability or model quality.
- A passing test suite validates only the checked-in software behavior exercised by these tests.

## Result

Pending. Raw run ID, exact command output, exit codes, elapsed time, and repository revision will be appended after execution.

## Next step

- If successful, record the test count, compileall result, and raw output digest; then return to INFER-001 secure-key setup and hosted-model listing.
- If failed, preserve the full failure, identify the failing test/module, and only change code when the failure is understood. Any repair must include regression tests and a Git commit before rerunning.
