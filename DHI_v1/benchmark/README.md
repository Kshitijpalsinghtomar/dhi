# DHI-v1 Agentic Pilot Cases — 0.1

**Status:** development pilot, not a frozen benchmark. **Not training data.**

The hand-authored 12-case suite contains eight executable file-workspace cases and four cases held out until the necessary external runtime integrations exist.

## Eight supported cases

1. Stable knowledge / no-tool restraint: answer a trivial fact without discovering or invoking tools.
2. Read-only source inspection and exact file identification.
3. Hidden text-search capability discovery.
4. Multi-step documentation update with source/config invariants.
5. Already-satisfied task and no-write restraint.
6. Recovery after one controlled transient search-tool failure.
7. Honest reporting when deployment configuration is absent.
8. README update while preserving protected source/config files.

## Four currently unsupported cases

Current-source/web verification, live app/plugin discovery, decoy-tool selection across external permissioned providers, and cross-session long-horizon resume. They are not scored by the file-workspace environment and must not be reported as passes or failures.

## Run against a served model

The model can be called through Adaption's Responses API or any OpenAI-compatible chat-completions endpoint with function/tool calling. For Adaption, first list your account's exact hosted model IDs:

```bash
export ADAPTION_API_KEY="..."
python -m DHI_v1.environment.examples.list_adaption_models

export DHI_MODEL_PROVIDER="adaption"
export DHI_MODEL_NAME="EXACT_HOSTED_MODEL_ID_FROM_THE_LIST"
python -m DHI_v1.benchmark.run_pilot_benchmark
```

The Adaption adapter uses `POST /api/v1/responses`, disables response storage and agentic memory for controlled evaluation, and translates DHI tool calls through Responses function-call items. Use a direct hosted-model ID for base screening. `stack:<slug>` is supported for later system experiments, but a stack adds its configured tools/datasets/memory and therefore is not a clean base-model comparison.

For another provider, set `DHI_MODEL_PROVIDER=openai_compatible` and provide `DHI_MODEL_BASE_URL`, `DHI_MODEL_API_KEY`, and `DHI_MODEL_NAME`.

The command writes a JSON report and one JSONL trajectory per case under `outputs/pilot_benchmarks/<run-id>/`. It uses a fresh pinned fixture workspace per task. Existing outputs are never overwritten.

Adaption's connected MCP tool set does not expose inference, but the platform REST API does: DHI now includes a Responses API adapter. A live call still requires an Adaption API key and a hosted model ID available to that key; no model has been evaluated by this runner yet.

## Scoring

The evaluator uses observable rules only: verified environment closure, final-answer checks, required tool usage, discovery events, changed-path limits, no-tool restraint, controlled error recovery, and protected-path preservation. It does not use another LLM as the sole judge.

The report's `pass_rate` is the percentage of these eight pilot cases passed. It is **not** the DHI 100-point capability rubric and cannot support a general model-quality or universal-intelligence claim.

## Data integrity

- Task descriptions are hand-authored specifications.
- Tool outputs and state changes originate from real local environment execution.
- One task uses a declared deterministic transient failure; it is recorded in the trace.
- Every supported case has executable postconditions.
- Scripted smoke traces and pilot benchmark reports are diagnostic artifacts, not approved training data.
- Freeze a larger, hidden, independently reviewed suite before confirmatory base-model comparisons.
