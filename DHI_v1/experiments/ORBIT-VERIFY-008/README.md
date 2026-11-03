# ORBIT-VERIFY-008 — scripted plugin runner / trace / grading regression

**Status:** prepared  
**Code under test:** `fec93ba59842d866149c7d03383b1833745077d2`  
**Branch:** `orbit/plugin-benchmark-fixture`  
**Verifier:** Deepnote project `6415944e-8d6c-432c-a7cf-3bbaa997799c`, notebook `3639f9a98ce5435fa4cd0168eaaca3a1`

## Question

Can a provider-agnostic model-facing plugin loop use the prepared canonical tool schemas, dispatch exclusively through the fail-closed permission boundary, create an append-only ORBIT trace, and receive an independent deterministic grade without contacting a model or provider?

## Frozen checks

1. Confirm the runner, tests, dispatch, loader, trace schema/module, and TinyFish adapter files match the pinned GitHub branch.
2. Confirm the task manifest remains the immutable blob used in ORBIT-VERIFY-006 and ORBIT-VERIFY-007.
3. Run manifest validation.
4. Run every benchmark and environment pytest test.
5. Run compileall and entrypoint imports.
6. Resolve all 30 task plans and verify the live manifest still disables all model runs.
7. Run the scripted runner test suite and validate its traces against the committed JSON Schema and deterministic grader.
8. Do not invoke a live model, TinyFish, GitHub, Firecrawl, or training.

Only the ORBIT-VERIFY-008 selected block is to be executed. Do not run the notebook's saved regression cell or provider-probe cells.

## Source identity

The following files match byte-for-byte between Deepnote and GitHub:
- `DHI_v1/benchmark/plugin_runner.py`
- `DHI_v1/benchmark/tests/test_plugin_runner.py`
- `DHI_v1/benchmark/plugin_execution.py`
- `DHI_v1/benchmark/plugin_task_loader.py`
- `DHI_v1/benchmark/plugin_trace.py`
- `DHI_v1/benchmark/plugin_trace.schema.json`
- `DHI_v1/environment/tinyfish_client.py`
- `DHI_v1/environment/tests/test_tinyfish_client.py`

Manifest blob SHA: `f1a73f4cc377f0ea72a37f7d2f9a3e7476ffe033`.

## Focused TDD evidence

- Red: `b167fe4f-ba9b-45ef-8eab-0688a9ef2243` — after installing the repo's declared dev requirements, pytest collection failed because `plugin_runner` did not exist.
- Initial sync miss: `a439c972-b974-402c-872f-962742d7d3ce` — not a code result; Deepnote lacked the committed runner file. The exact branch file was subsequently synced.
- Focused green: `e67a4325-ce87-45c1-8946-7bed750173d1` — **4 passed**.

## Runner contract under test

The runner accepts a validated `PluginTaskPlan`, the original task record, a `PreparedPluginExecution`, a bounded chat-completion client, and an optional independent state observer. It:
- checks the execution flag on both the original task record and the prepared plan;
- presents the prepared canonical function schemas, including optional DHI effect-forecast metadata;
- strips that metadata before the dispatch layer validates arguments against the pinned schema;
- sends every call through `PreparedPluginExecution.dispatch`;
- logs pre-action prediction, action start, raw handler outcome, independently observed before/after state hashes, and task closure;
- validates the append-only trajectory with `plugin_trace.validate_trace` and grades it with `grade_task`;
- requires independent state observation for tasks permitting sandbox writes;
- redacts arbitrary provider exception details from trace output.

The test uses a scripted local model client and fake GitHub read handlers. It is not a live model or provider experiment.

## Evidence boundary

This verifies the model/tool loop's local scripted integration with the generic permission gate, trace schema and grader. It does not prove a real hosted model will select tools correctly, call a real provider, or complete an ORBIT benchmark task. The manifest remains unchanged with all 30 model runs disabled.
