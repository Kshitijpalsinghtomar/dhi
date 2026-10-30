# DHI-v1 Deterministic Tool Environment — v0.1

**Date:** 2026-10-31  
**Status:** First runnable development harness. Not a production sandbox or model capability result.

## Purpose

This is the first executable dependency for DHI-v1: a deterministic software-workspace environment that records real file-tool actions, observed state changes, action-effect predictions, and executable goal postconditions.

It exists so DHI can eventually be evaluated and trained on actual action → observation → state delta → verification trajectories, rather than examples where a model merely invents what a tool supposedly returned.

## Implemented tools

| Tool ID | Function | Side-effect class |
|---|---|---|
| **catalog.search** | Search the local deterministic tool catalogue for a capability absent from the initially visible list. | Read-only |
| **catalog.adaption_search** | When an Adaption Responses client is configured, search the live account connector catalogue and expose availability, auth, required scope, connection and approval metadata. | Read-only; discovery only |
| **fs.list_files** | List workspace-relative files. | Read-only |
| **fs.read_file** | Read UTF-8 text. | Read-only |
| **fs.write_file** | Create/replace UTF-8 text. | Workspace write |
| **fs.append_file** | Append UTF-8 text to an existing file. | Workspace write |
| **fs.search_text** | Search UTF-8 files and return matching line numbers. | Read-only |

The catalogue-search tool is always visible even when a task's initial file-tool subset omits the search capability. This lets the agent request discovery rather than requiring the runner to guess what tool it needs.

**Scope distinction:** catalog.search is still deterministic lexical matching over the tiny local fixture catalogue. In Adaption mode, catalog.adaption_search uses the live Adaption `GET /api/v1/tools` registry and returns actual connector availability, auth source, connection flow, required scope, connection mode, approval default, and reason when unavailable. Both are read-only discovery surfaces. A catalogue record does not create a callable connector tool and does not authorize an external action.

## Trace and verification

The runner emits append-only JSONL events using the dhi.trajectory.v1 schema:

- task_started: task goal, constraints, initial file hashes, visible tool manifest, postconditions, and provenance;
- action_started: action intent, selected tool, arguments, predicted effects, and pre-action state;
- tool_discovery: discovery query and tools returned;
- action_executed: actual result/error, after-state hashes, actual changed paths, prediction comparison, and permission metadata;
- task_closed: final state, overall delta, executable postcondition results, and protected-path checks.

Each trace path must be new; the runner refuses to append to an existing file so separate trajectories cannot be silently mixed. A pre-action action_started event is written before the tool executes. This makes an interrupted trace distinguishable from an action that was never attempted.

The first prediction metric compares predicted changed/unchanged file paths with actual SHA-256 snapshot deltas. It is not yet a learned latent-state prediction metric. Later versions should add structured state predicates, test outcomes, dependency effects, risk, and uncertainty.

Task closure fails when any required postcondition fails or any protected path changes. A task must supply at least one explicit postcondition; success is not vacuously true.

## Safety boundary

This harness deliberately exposes no arbitrary shell, Python, package-install, browser, or external connector execution. It only mutates files inside a designated workspace. When configured, the optional Adaption discovery meta-tool makes a read-only HTTPS request to the connector catalogue; it never invokes a connector.

It rejects path traversal and symlinks, validates tool argument schemas, enforces task tool allowlists (while keeping read-only catalogue discovery available), and bounds snapshot/file sizes.

**This is not an OS/container security sandbox.** Do not run untrusted agent-generated code in the same process or machine as sensitive data. Before adding arbitrary command or code execution, place the environment inside a disposable container/VM with network, filesystem, CPU, memory, and process restrictions. The current file-only harness is suitable for deterministic development tests, not adversarial code execution.

Tool results can contain file contents. Use synthetic fixtures or approved sanitized repositories only; never place secrets, credentials, production user data, or private tokens in a trace.

## Run tests

From the DHI repository root on Python 3.11+:

**python -m pip install -r DHI_v1/environment/requirements-dev.txt**

**python -m pytest -q DHI_v1/environment/tests DHI_v1/benchmark/tests**

## Model-to-environment runner

`agent_runner.py` supplies an OpenAI-compatible chat-completions adapter and a bounded tool loop. It builds function schemas from the current visible inventory on every turn, exposes only those schemas to the model, and refreshes them after catalogue discovery. Hidden tools cannot be called before discovery; if discovery and a hidden call arrive in the same response, the environment rejects the call until the next turn's schema refresh.

Optional `__dhi_expected_effects` and `__dhi_subgoal` fields let the model forecast file-level effects before a consequential action. The runner strips those metadata fields before validating the actual tool arguments. The environment compares the forecast with SHA-256 state deltas and independently checks the task postconditions.

The runner does not request or store hidden chain-of-thought. It stores structured tool calls, observed tool results, state deltas, predictions, and verified closure.

The connected Adaption MCP integration exposes dataset/training operations but not the Responses REST method. DHI now includes a direct adapter for Adaption's documented `POST /api/v1/responses` API, with hosted-model catalogue support at `GET /api/v1/models`. For fair base-model screening, use a hosted model ID, not a saved stack, so extra stack tools/datasets/memory do not confound the model comparison.

```bash
# List exact hosted model IDs available to this Adaption API key
export ADAPTION_API_KEY="..."
python -m DHI_v1.environment.examples.list_adaption_models

# Read-only: inspect the actual connector/tool catalogue and availability
python -m DHI_v1.environment.examples.list_adaption_tools

# Run the DHI one-task integration pilot or common eight-case benchmark
# In Adaption mode, a ninth live connector-discovery case is added automatically
export DHI_MODEL_PROVIDER="adaption"
export DHI_MODEL_NAME="EXACT_HOSTED_MODEL_ID_FROM_THE_LIST"
python -m DHI_v1.benchmark.run_pilot_benchmark
```

Use `DHI_ADAPTION_API_BASE_URL` only if your organization has a different API base, and `DHI_ADAPTION_ORGANIZATION_ID` when the key requires an organization header. The adapter defaults to `https://api.prod.adaptionlabs.ai`, keeps response storage and agentic memory disabled during evaluation, and maps DHI function calls to Responses `function_call` / `function_call_output` items. The read-only `GET /api/v1/tools` catalogue distinguishes available connectors from unavailable entries and explains why they cannot currently be used. DHI exposes this as the model-callable `catalog.adaption_search` meta-tool only when an Adaption client is configured. The model chooses whether to query it; the local runner records a discovery event and never gives the model a connector execution schema.

A saved Inference Stack can also be called with `DHI_MODEL_NAME="stack:your-stack-slug"`; create/manage it in Adaption's Inference stacks app because the API only calls stacks. Do not use a stack for the first base-model comparison unless its tools, datasets, and memory are deliberately part of the experiment.

For other serving providers, set `DHI_MODEL_PROVIDER="openai_compatible"` plus `DHI_MODEL_BASE_URL`, `DHI_MODEL_API_KEY`, and `DHI_MODEL_NAME`. Those runs use the common eight cases; the Adaption-specific connector-catalogue case is not run.

Credentials are read only at runtime and must never be committed. The model pilot writes a new JSONL trace under `outputs/model_pilots/`; the benchmark writes its JSON report and per-case traces under `outputs/pilot_benchmarks/`. These are diagnostic artifacts, not training data or frozen benchmark results. The adapter has passed local request/response unit tests; a live account-key/model call is still required to verify the actual hosted model IDs and any account-specific access.

## Run the deterministic smoke pilot

**python -m DHI_v1.environment.examples.run_pilot --output outputs/dhi_v1_pilot_trace.jsonl**

The pilot creates a temporary sample repository, lists its files, discovers the hidden text-search capability through catalog.search, searches source, reads the actual file, updates the README, compares predicted and actual changed paths, verifies the README postcondition, and confirms protected files are unchanged.

The pilot is hand-scripted to test the runner. It is not generated by a language model, not an agent success result, and not approved training data. A model must later produce the decisions/actions itself under the same harness.

## Files

- dhi_env.py — environment, tool catalogue, action execution, state snapshots, prediction comparison, and closure verifier.
- agent_runner.py — OpenAI-compatible tool-calling loop with per-turn schema refresh and independently verified closure.
- examples/run_model_pilot.py — endpoint-backed smoke integration entry point.
- fixture_manager.py — SHA-256-validated pinned fixtures and safe materialization into new/empty workspaces.
- fixtures/basic_repo/ — initial deterministic repository state plus manifest.
- tests/test_dhi_env.py — tests for discovery, permissions, traversal defense, schemas, traces, predictions, postconditions, and closure.
- examples/run_pilot.py — deterministic hand-scripted smoke pilot.
- examples/run_model_pilot.py — one-task, model-endpoint integration pilot.
- examples/list_adaption_models.py — list exact hosted model IDs available to the configured Adaption API key.
- examples/list_adaption_tools.py — inspect Adaption's live connector catalogue, including caller availability and missing-scope/plan/disabled reasons.
- adaption_responses.py — Adaption Responses API client, model catalogue reader, and function-call format adapter.
- benchmark/runner.py — eight-case executable diagnostic pilot and observable evaluator.
- benchmark/run_pilot_benchmark.py — endpoint-backed command for running the eight supported cases.
- benchmark/tests/ — evaluator and pilot-selection tests.
- schemas/trajectory-event.schema.json — JSON Schema for event validation.
- requirements-dev.txt — pytest and JSON Schema validation dependencies.

## Test status

Local verification on 2026-10-31: **75 tests passed**. The tests include validation of generated JSONL events against the checked-in JSON Schema. The smoke pilot separately produced 13 real runner events and verified the README postcondition plus two protected files.

## Benchmark pilot

The hand-authored 12-case seed suite lives in `DHI_v1/benchmark/pilot_cases.json`. Eight common file-workspace cases run with any configured provider. An Adaption-configured run adds one provider-specific live connector-catalogue discovery case, for nine total. Three remaining cases (current-source/web verification, decoy permissions across external providers, and cross-session resume) remain unsupported. The suite is not frozen, not a 120-task base-screen benchmark, and not training data.

Each Adaption run fetches the live connector catalogue once and reuses that snapshot across model turns and all cases. Its SHA-256 fingerprint is stored in the discovery event and top-level benchmark report. Compare this fingerprint between model runs; a changed connector inventory means the provider-specific comparison was not made against the same tool ecosystem.

Run supported cases against a served model with `DHI_MODEL_BASE_URL`, `DHI_MODEL_API_KEY`, and `DHI_MODEL_NAME` set:

```bash
python -m DHI_v1.benchmark.run_pilot_benchmark
```

The run writes a JSON report and per-case traces to `outputs/pilot_benchmarks/`. The common pass rate is an eight-case development metric; Adaption runs also report the separate ninth connector-discovery case. Neither is the DHI 100-point rubric.

## Next engineering gates

1. Add environment reset/replay from a pinned initial workspace fixture and version/hash manifest.
2. Add structured state predicates and protected invariants beyond file-level hashes.
3. Add a trusted test-runner adapter inside a disposable sandbox; never allow arbitrary shell arguments through a tool schema.
4. Add multi-step repository tasks with dependencies, broken tools, changed constraints, and false-closure cases.
5. Connect model inference only after the deterministic environment and hidden evaluation set are frozen.
6. Connect a real inference endpoint and screen the untouched candidate bases under identical tool manifests/budgets. Collect model-generated action trajectories only after the benchmark split is frozen; keep scripted pilots out of training.

## Known limitations

- File-workspace only; no shell, git, browser, code execution, external APIs, multi-agent tools, or true marketplace discovery.
- The local catalogue search is lexical and deterministic; the Adaption catalogue search is also lexical over live metadata, not a semantic tool marketplace.
- Adaption connector discovery is read-only; no external connector action is exposed through this adapter.
- State snapshots contain file hashes, not full semantic program state.
- Prediction scoring uses changed/unchanged path sets only.
- The Adaption Responses API adapter and OpenAI-compatible adapter are implemented. No Adaption API key/model has been exercised from this environment yet; no base-model benchmark has been run.
- No training dataset has been created from this harness.
- No claims of general agentic intelligence or architecture novelty are supported by this prototype.


## Invent task-specification dataset gate

The first 120-row Invent task-specification dataset completed processing, but Adaption graded it B with score 7.7 (down from 8.0, -3.7%). Completion quality was at the 2.7th percentile; message quality at the 28.9th percentile. It is quarantined and is not training data. Use `python -m DHI_v1.benchmark.audit_invent_dataset --dataset-id 1eccaa36-bdc7-4d6e-ac8d-41b20d9425e2` with `ADAPTION_API_KEY` set locally to download the JSONL export and inspect actual rows.
