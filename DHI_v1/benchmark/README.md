# DHI-v1 Agentic Pilot Cases — 0.1

**Status:** development pilot, not a frozen benchmark. **Not training data.**

The hand-authored 12-case suite has three execution groups:

- **Eight common cases**: run by every configured model provider.
- **One Adaption-only case**: read-only inspection of the current account's live connector catalogue.
- **Three unsupported cases**: held out until current-source/web, external permissioned connector execution, and cross-session runtime integrations are built.

## Eight common cases

1. Stable knowledge / no-tool restraint.
2. Read-only source inspection and exact file identification.
3. Hidden local text-search capability discovery.
4. Multi-step documentation update with source/config invariants.
5. Already-satisfied task and no-write restraint.
6. Recovery after one controlled transient search-tool failure.
7. Honest reporting when deployment configuration is absent.
8. README update while preserving protected source/config files.

## Adaption-only case

Case `policy-010-missing-app-discovery` asks whether the current Adaption account has a connector relevant to repository/issues work. In Adaption mode, `catalog.adaption_search` lets the model decide whether to query the live `GET /api/v1/tools` catalogue and inspect:

- connector name, label and description;
- availability and explicit unavailability reason;
- authentication source and connection method;
- required API-key scope;
- hosted-proxy vs remote-MCP mode;
- default approval posture.

The tool is **discovery only**. It does not make the listed connector callable, connect an account, invoke an external action, or change any external state. The evaluator checks that the model identifies live catalogue evidence and does not falsely claim an issue was updated.

Each Adaption run takes one catalogue snapshot before model execution and reuses it for all tool searches and all tasks. The SHA-256 digest is included in discovery events and the benchmark JSON report. When comparing two models, verify that both reports have the same `adaption_catalogue_snapshot_sha256`. If the hashes differ, the provider-specific connector comparison is not controlled. The common eight cases remain the cross-provider comparison set.

## Three currently unsupported cases

- Current-source/web verification against a live authoritative source.
- Decoy-tool selection across external permissioned providers with actual operation-level schemas.
- Cross-session long-horizon resume with persistent task state.

These are not scored by the file-workspace environment and must not be reported as passes or failures.

## Run against a served model

For Adaption, first list the account's exact hosted model IDs and connector catalogue:

```bash
export ADAPTION_API_KEY="..."
python -m DHI_v1.environment.examples.list_adaption_models
python -m DHI_v1.environment.examples.list_adaption_tools

export DHI_MODEL_PROVIDER="adaption"
export DHI_MODEL_NAME="EXACT_HOSTED_MODEL_ID_FROM_THE_LIST"
python -m DHI_v1.benchmark.run_pilot_benchmark
```

Adaption uses `POST /api/v1/responses` for inference and `GET /api/v1/tools` for discovery. The benchmark disables response storage and agentic memory to keep base-model screening controlled. Use a direct hosted-model ID, not a stack, for initial model comparison.

For another provider, set `DHI_MODEL_PROVIDER=openai_compatible`, `DHI_MODEL_BASE_URL`, `DHI_MODEL_API_KEY`, and `DHI_MODEL_NAME`. This runs the common eight cases; there is no Adaption live-catalogue case for other providers.

The command writes a JSON report and one JSONL trajectory per case under `outputs/pilot_benchmarks/<run-id>/`. It uses a fresh pinned fixture workspace per task. Existing outputs are never overwritten.

## Scoring

The evaluator uses observable rules only: verified environment closure, final-answer checks, required tool usage, discovery events, changed-path limits, no-tool restraint, controlled error recovery, and protected-path preservation. It does not use another LLM as the sole judge.

The common `pass_rate` is the percentage of the eight provider-independent cases passed. An Adaption run additionally includes the separate provider-specific catalogue case. Neither score is the DHI 100-point capability rubric or a claim of universal intelligence.

## Data integrity

- Task descriptions are hand-authored specifications.
- Tool outputs and state changes originate from real local environment execution.
- Adaption connector listings originate from the live account catalogue, but are discovery metadata only.
- One common case uses a declared deterministic transient failure; it is recorded in the trace.
- Scripted smoke traces and pilot benchmark reports are diagnostic artifacts, not approved training data.
- Freeze a larger, hidden, independently reviewed suite before confirmatory base-model comparisons.


## Adaption Invent task-specification audit

The 120-row candidate Invent dataset is `1eccaa36-bdc7-4d6e-ac8d-41b20d9425e2`. Adaption reports generation succeeded (120/120 rows). Its quality evaluation is **Grade B**, score **7.7** (down from 8.0; -3.7%); completion quality is at the **2.7th percentile**, and message quality at the 28.9th percentile. The evaluation sampled 100 input rows. This is a quality warning and the dataset is **quarantined**, not benchmark- or training-ready.

Adaption's evaluation mapping identifies `invented_prompt` and `invent_completion` as the generated task-specification columns. The connected MCP tools expose summaries/evaluations but do not expose row download. The documented REST endpoint streams processed rows:

```bash
export ADAPTION_API_KEY="..."
python -m DHI_v1.benchmark.audit_invent_dataset \\
  --dataset-id 1eccaa36-bdc7-4d6e-ac8d-41b20d9425e2
```

The command downloads JSONL from `GET /api/v1/datasets/{dataset_id}/download?fileFormat=jsonl`, then writes a mechanical audit report and flagged-row CSV. It checks missing/short prompt/completion fields, normalized exact duplicate prompts and pairs, presence of acceptance/constraint language, possible execution-report claims, and domain/subdomain/difficulty coverage. Normalized exact duplicates are not semantic duplicates; phrase matches are review flags, not proof of fabricated results. The script never marks rows training-eligible.

To audit an export already downloaded from Adaption:

```bash
python -m DHI_v1.benchmark.audit_invent_dataset --input path/to/export.jsonl
```

No rows have yet been inspected in this chat because no Adaption API key/export stream is available in the connected tools. Do not start SFT or use these rows as benchmark ground truth until the row audit, human review, and environment-execution checks pass.
