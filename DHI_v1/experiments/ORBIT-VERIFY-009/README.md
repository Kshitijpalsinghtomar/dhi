# ORBIT-VERIFY-009 — GitHub adapter security and regression

<badge>PASS</badge> **Final status: all exact-revision checks passed**

- **Code under test:** `cca077e9c5c6b50fffee94ea3c74576c89c34462`
- **Branch snapshot:** `eb0f681d13b333b6b4c03b5b14f9555ca624a6ef`
- **Deepnote run:** `a249a76e-6454-4ca8-b9c4-64ca6a098c2f`
- **Focused GitHub adapter run:** `5855c01e-c3cc-4248-be3a-5ae165d2f70f`

## Results

| Check | Result |
|---|---:|
| Manifest validator | PASS — 30 tasks, Stage A 30, Stage B 0 |
| Full benchmark + environment pytest | **203 passed, 0 failed** |
| GitHub client + task-bundle focused tests | **21 passed, 0 failed** |
| compileall | PASS |
| Entrypoint import smoke | PASS |
| Plugin loader smoke | PASS — 30 plans, 0 model runs enabled |

Python 3.13.18. See [the raw verification report](results/verification-report.json) for commands, exit codes, timings and captured outputs.

## Security and fixture changes covered

1. Added `_RejectRedirects` to the GitHub adapter's authenticated and public fetch openers. Python's default redirect behavior can forward request headers; this adapter now rejects a redirect before following it.
2. Corrected bundle-test handler maps so only tools visible to each manifest task are supplied.
3. Fixed late-bound lambdas in synthetic tool handlers.
4. Changed the S06 fixture guard to use a dedicated synthetic sandbox branch name, not the active research branch.

The focused tests use fake HTTP responses. No live GitHub request was made.

## Evidence boundary

This closes the GitHub adapter's offline engineering regression for the exact code revision. It does **not** prove a live GitHub credential, live provider request, model-generated trajectory or successful end-to-end benchmark task.

- GitHub credential presence in Deepnote: false.
- GitHub write flag and repository allowlist: false.
- Live GitHub requests and writes: zero.
- Model calls and training jobs: zero.
- All 30 source-manifest tasks remain `model_runs_allowed=false` and `ready_for_validation`.

The plugin runner still needs manifest precondition enforcement (including S06's required branch-head SHA) and independently verified artifact/readback capture before S06 can be graded end-to-end. No model-execution gate is opened by this pass.
