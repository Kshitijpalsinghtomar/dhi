# DHI-v1 Agentic Pilot Cases — 0.1

**Status:** development pilot, not frozen benchmark. **Not training data.**

`pilot_cases.json` contains 12 hand-authored diagnostic specifications. Seven currently run in the deterministic file-workspace harness. Five remain explicitly unsupported until a real current-source adapter, app/plugin registry, permission-aware document tool, or cross-session runtime exists.

## Supported cases

1. Read-only source inspection and exact file identification.
2. Hidden text-search capability discovery.
3. Multi-step documentation update with source/config invariants.
4. Already-satisfied task and no-write restraint.
5. Recovery after one controlled transient search-tool failure.
6. Honest reporting when deployment configuration is absent.
7. README update while preserving protected source/config files.

## Run against a served model

The model must be exposed through an OpenAI-compatible chat-completions endpoint with function/tool calling:

```bash
export DHI_MODEL_BASE_URL="https://your-serving-endpoint/v1"
export DHI_MODEL_API_KEY="..."
export DHI_MODEL_NAME="your-served-model-id"
python -m DHI_v1.benchmark.run_pilot_benchmark
```

The command writes a JSON report and one JSONL trajectory per case under `outputs/pilot_benchmarks/<run-id>/`. It uses a fresh pinned fixture workspace per task. Existing outputs are never overwritten.

The current connected Adaption API exposes dataset and training operations but no inference call. This benchmark can run once a real model-serving endpoint is configured; no model has been evaluated by this runner yet.

## Scoring

The evaluator uses observable rules only: verified environment closure, answer substrings or alternative phrases, required tool usage, discovery events, required file changes, no-op limits, controlled error recovery, and protected-path preservation. It does not use another LLM as the only judge.

The report's `pass_rate` is the percentage of these seven pilot cases passed. It is **not** the DHI 100-point capability rubric and cannot support a general model-quality or universal-intelligence claim.

## Unsupported cases

The five cases requiring live current-source verification, external app/plugin discovery, decoy-tool permission reasoning, and cross-session long-horizon execution remain excluded from the file-workspace score. Do not count them as passed or failed until their required runtime integrations and graders exist.

## Data integrity

- Tasks are hand-authored specifications.
- All tool outputs and state changes originate from real execution in the local environment.
- One task uses a controlled, declared transient failure to test recovery; the injection is recorded in the trace.
- Every case has executable postconditions.
- Scripted smoke traces and pilot benchmark reports are diagnostic artifacts, not approved training data.
- Freeze a larger, hidden, independently reviewed suite before confirmatory base-model comparisons.
