# ORBIT-VERIFY-008 — scripted plugin runner / trace / grading regression

<badge>PASS</badge> **Final status: all checks passed**

**Code under test:** `fec93ba59842d866149c7d03383b1833745077d2`  
**Branch:** `orbit/plugin-benchmark-fixture`  
**Verifier:** Deepnote project `6415944e-8d6c-432c-a7cf-3bbaa997799c`, notebook `3639f9a98ce5435fa4cd0168eaaca3a1`  
**Successful run:** `570dd432-474f-4520-8f17-700d480358bb`

## Question

Can a provider-agnostic model-facing plugin loop use the prepared canonical tool schemas, dispatch exclusively through the fail-closed permission boundary, create an append-only ORBIT trace, and receive an independent deterministic grade without contacting a model or provider?

## Source identity

The following files matched byte-for-byte between Deepnote and GitHub at the tested branch revision:
- `DHI_v1/benchmark/plugin_runner.py`
- `DHI_v1/benchmark/tests/test_plugin_runner.py`
- `DHI_v1/benchmark/plugin_execution.py`
- `DHI_v1/benchmark/plugin_task_loader.py`
- `DHI_v1/benchmark/plugin_trace.py`
- `DHI_v1/benchmark/plugin_trace.schema.json`
- `DHI_v1/environment/tinyfish_client.py`
- `DHI_v1/environment/tests/test_tinyfish_client.py`

Task-manifest blob SHA: `f1a73f4cc377f0ea72a37f7d2f9a3e7476ffe033`.

## Focused TDD evidence

- Red: `b167fe4f-ba9b-45ef-8eab-0688a9ef2243` — after installing the declared dev requirements, pytest collection failed because `plugin_runner` did not exist.
- Sync miss: `a439c972-b974-402c-872f-962742d7d3ce` — not a code result; Deepnote did not yet contain the committed runner source. The exact branch file was synced before retry.
- Focused green: `e67a4325-ce87-45c1-8946-7bed750173d1` — **4 passed**.

## Full exact-revision result

- Manifest validator: **PASS** — valid=true, 30 tasks, Stage A=30, Stage B=0, no errors.
- Full benchmark + environment pytest: **182 passed, 0 failed** in 434.443 seconds (pytest summary: 388.18 seconds).
- `compileall`: **PASS** — exit code 0.
- Entrypoint imports: **PASS**.
- Plugin loader smoke: **PASS** — all 30 plans load; **0 model runs enabled**.
- Python: 3.13.18.

Full commands, outputs, exit codes, timings and environment details are archived in [results/verification-report.json](results/verification-report.json).

## Runner contract

The provider-agnostic runner accepts a validated `PluginTaskPlan`, the original task record, a `PreparedPluginExecution`, a bounded chat-completion client, and an optional independent state observer. It:
- checks the model-execution flag on both the original task record and prepared plan;
- presents canonical model-visible schemas with optional pre-action effect forecast metadata;
- strips DHI-only forecast metadata before strict dispatch schema validation;
- sends all calls through `PreparedPluginExecution.dispatch`;
- records append-only `task_started`, `assistant_prediction`, `action_started`, `action_executed`, and `task_closed` events;
- derives state effects from independent before/after hash maps rather than model-authored summaries;
- requires an independent state observer for tasks that permit sandbox writes;
- validates the trace with `plugin_trace.validate_trace` and grades the original task record with `grade_task`;
- withholds arbitrary provider exception details from the trace.

The four focused tests use a scripted local client and fake GitHub handlers. The denied-write test proves a visible-but-disallowed write tool is rejected before the handler is invoked.

## Evidence boundary

This closes the **scripted plugin runner engineering gate**. It proves the local model/tool loop, permission boundary, trace schema and deterministic grader work together for the tested task.

It does **not** prove a real hosted model will choose correctly, call a real provider, or pass a full ORBIT benchmark task. There is still no connected GitHub/Firecrawl project integration in Deepnote; the GitHub fake handlers in these tests are not live provider handlers. All 30 manifest tasks remain `model_runs_allowed=false`.

## Next gate — GitHub runtime tool bundle

The current task matrix has 16 tasks requiring GitHub. Build a credential-gated, canonical GitHub REST bundle test-first for the registered read capabilities, then the task-guarded create/update/branch operations:
1. expose exact registry IDs and strict argument schemas;
2. implement bounded GitHub REST calls with a project-scoped token, redacted errors, no automatic retries, and host/path allowlists;
3. keep reads read-only and require the existing exact-task/path/branch write guard for every sandbox write;
4. test HTTP request construction with fake responses and test that no handler is exposed without the runtime key;
5. integrate the returned handler map with `prepare_plugin_execution` and the new plugin runner without enabling live model execution.

Firecrawl Alexandria's assistant-session contract is known, but no Deepnote project transport is attached. OpenRouter remains at $0 credits, with no project-scoped model configuration. See [WORKSPACE.md](../../WORKSPACE.md) and the launch-readiness audit.
