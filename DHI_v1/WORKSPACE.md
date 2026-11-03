# DHI-v1 Live Workspace

**Last updated:** 2026-11-03  
**Repository:** https://github.com/Kshitijpalsinghtomar/dhi  
**Active research branch:** `orbit/plugin-benchmark-fixture` (default `main` remains unchanged; branch is intentionally unmerged)  
**Live-state rule:** This file is the first read at every session. It supersedes older chat summaries and dated handover snapshots when describing current status.

## 1. Identity

- Active programme: **DHI-v1 — Predictive Agentic Intelligence**.
- Model codename used in this programme: **ORBIT**.
- DHI-v0 is historical and separate.
- GBA/DPAK and all other research are separate. Do not mix evidence or directions across projects without a committed DHI decision.
- GitHub is the durable project memory. Follow [the Git-first workflow](docs/12_GIT_FIRST_WORKFLOW.md).

## 2. Current objective

Develop a model whose learned capabilities support goal/constraint reasoning, dynamic tool discovery and affordance-aware selection, hierarchical long-horizon planning, action-effect prediction, feedback-conditioned replanning, safe execution, context continuity, and independently verified goal closure.

This is a research target, not a result or novelty claim. A prompt, RAG store, fixed router, scripted client, or external orchestrator is not by itself the learned model contribution.

## 3. Current phase and status

<details>
<summary>Machine-readable status</summary>

```yaml
programme: DHI-v1
codename: ORBIT
phase: plugin_native_stage_a_seed_authored
status: in_progress
status_reason: >
  The plugin-native task route now has 30 Stage A task records across all ten strata.
  The manifest validator passes and 44 focused manifest/grader tests plus compileall
  passed at code commit 421955df46975d8b20fba63f8922949a49b4551c. S07 and S09 remain
  partial pending model-run checkpoint and pre-action prediction traces. No DHI model
  inference, trained capability result, or verified model trajectory exists. OpenRouter
  exposes both base candidates, but its account balance is zero, so no inference was run.
training_status: not_authorized
benchmark_status: stage_a_authoring_30_of_120; stage_b_sealed_unmaterialized
last_verified_code_commit: 421955df46975d8b20fba63f8922949a49b4551c
```
</details>

**No DHI-v1 model capability result is currently established. No DHI-v1 SFT, DPO, RL, or custom latent-predictive training run is authorized.**

## 4. What is implemented

- Deterministic file-workspace environment and pinned SHA-256 fixture.
- Bounded model-to-tool runner with per-turn tool-schema refresh.
- Adaption Responses API adapter and hosted-model catalogue reader.
- Read-only Adaption connector-catalogue discovery.
- Twelve hand-authored diagnostic seeds: eight common executable cases, one Adaption-specific discovery case, and three unsupported future-runtime cases.
- Plugin-native task profile with 16 exact connected tool contracts pinned in `benchmark/fixtures/plugin_ecology/plugin_tool_registry.json`.
- Synthetic Northstar plugin ecology fixture with source data, untrusted issue content, external snapshots, checkpoint and report artifacts.
- Thirty Stage A task instances across all ten strata recorded in `benchmark/task_manifest.json`.
- Observable grader for tool use, no-tool restraint, recovery, state changes, protected paths, and verified closure.
- Model-facing entrypoints:
  - `python -m DHI_v1.benchmark.run_model_pilot`
  - `python -m DHI_v1.benchmark.run_pilot_benchmark`

## 5. Evidence ledger

| Item | Status | Evidence boundary |
|---|---|---|
| Scripted reference pilot | 8/8 passed | Harness/reference validation only; not an LLM result or training data |
| Historical environment/benchmark tests | 75 passed on 2026-10-31 | Historical run; do not claim latest HEAD is tested |
| ORBIT adjudication gate | Focused tests passed on 2026-10-31 | Gate code verification only |
| INFER-001 hosted inference preflight | Adaption-hosted catalogue read only | Gemma 4 31B was the only selected candidate in that Adaption catalogue; no Adaption Responses inference was run |
| INFER-002 OpenRouter inference preflight | Qwen3.6-35B-A3B and GPT-OSS-20B both listed with tool-capable PrimeIntellect endpoints | OpenRouter balance $0; no free endpoint for either model; no inference was run |
| ADAPTION-001 live platform audit | Completed; read-only | Qwen/Gemma require 10,000 effective training rows; GPT-OSS recipe returned for 300 rows; dataset not eligible; zero credits spent |
| Untouched candidate model screening | Not run | No model winner |
| DHI-v1 executed model trajectories | None recorded | No trajectory SFT source yet |
| DHI-v1 training | Not authorized / not run | Data and benchmark gates remain closed |
| Plugin-native Stage A authoring | 30 tasks materialized; 30 ready for validation | Actual GitHub/TinyFish/Firecrawl tool contracts and pinned evidence; no model runs |
| Plugin reference workflows | Release report and checkpoint-resume report completed | Scripted reference evidence only; not DHI model capability results |
| Plugin-native task grading | Not run | Grader contracts are authored; independent and model-facing validation still pending |
| Manifest and trace-grader verification | Passed at code commit 421955df46975d8b20fba63f8922949a49b4551c | Validator: 30/30 valid, Stage A=30, Stage B=0; 44 focused tests passed; compileall passed. Harness integrity only, not a model result |

## 6. Data status and hard stops

- Both 120-row Invent task-spec candidates are quarantined because task-contract JSON was generated as a completion rather than a natural answer/valid execution trajectory.
- The 300-row ORBIT collaboration-behaviour candidate (`169af31f-06e0-4a48-84ab-b84c9f9ce924`) is Invent-sourced and not training-ready: only 98 visible complete pairs were reviewed (25 candidate, 53 revise, 20 reject); 202 rows remain unreviewed. This was model-assisted partial triage, not full independent adjudication.
- The 10,000-row augmented intent dataset (`843888da-28e2-420e-909e-88b203d16404`) has `rephrased_prompt`/`enhanced_completion` columns, but its evaluation input path and config source point to the separate 300-row `c1f4df14-b12c-430c-91ad-e10b559d1cee` dataset and a 100-row sample. Its A grade is not accepted as a certificate for the 10K export. See `experiments/TRAINING-ACCESS-002/`.
- Adaption's evaluation of that dataset returned grade A / 9.4 on a 100-row evaluation sample. This is text-quality metadata, not an agent-capability score and not evidence of executed tool traces.
- Live Adaption recommendations confirmed a 10,000-effective-row minimum for Qwen3.6-35B-A3B and Gemma 4 31B. GPT-OSS-20B returned a LoRA recipe for the 300-row set, but this does not override its provenance/review failure.
- Do not train on any of those datasets, do not promote their Adaption grades to capability evidence, and do not fabricate tool traces or outcomes.
- The primary future SFT evidence must be actual model execution in the DHI environment, with raw tool responses, actual state deltas, predictions, and independently verified postconditions.
- Do not spend Adaption credits until the documented data, benchmark, model, and estimate gates pass.

## 7. Current blockers and platform boundary

Adaption's connected MCP integration is useful for training-registry inspection, dataset inventory/evaluation, data transformation estimates, hyperparameter recommendations and AutoScientist runs, but it does not expose hosted Responses inference. OpenRouter now provides a separate inference route for Qwen3.6-35B-A3B and the mandatory GPT-OSS-20B challenger; both have tool-capable endpoints at PrimeIntellect. The OpenRouter account has **$0 remaining credit**, and no free endpoint was found for either model, so no model call or benchmark run was made.

Current facts:
- Live training registry lists Qwen/Qwen3.6-35B-A3B, openai/gpt-oss-20b, and google/gemma-4-31B-it for supported SFT/DPO methods.
- OpenRouter route audit: Qwen3.6 and GPT-OSS are both present; PrimeIntellect offers Qwen fp8 at $0.01/$0.092 per million input/output tokens and GPT-OSS fp4 at $0.009/$0.038. These are live catalogue prices only; account balance is $0, and no model call was attempted.
- Adaption's recommender returned a Qwen3.6 LoRA configuration for the 10K-row dataset, but its evaluation record points to a different 300-row dataset. No training is authorized until raw rows and lineage are verified.
- The separate hosted Responses catalogue returned six IDs, but only Gemma 4 31B matched a committed candidate. Qwen3.6 and GPT-OSS were absent from that hosted catalogue. Do not treat registry support as inference access.
- A single Gemma call would test only one integration path; it cannot select the primary model against the mandatory GPT-OSS challenger. It is therefore not the next research action.
- The live Adaption recommender rejected Qwen3.6 and Gemma on the 300-row dataset because they require at least 10,000 effective rows. GPT-OSS returned a recipe, but the dataset remains ineligible.
- The recommender did not return a price quote. Dataset generation/adaptation/augmentation actions expose `estimate: true`; the connected training-launch action spends credits and has no estimate field in its exposed schema. Obtain platform cost information before any chargeable launch.
- No DHI-v1 inference, training run, or new dataset-generation job was launched in ADAPTION-001. The OpenRouter preflight was read-only; no model call was made.

Experiment records:
- `DHI_v1/experiments/INFER-001/` — secure runtime and hosted catalogue preflight.
- `DHI_v1/experiments/ADAPTION-001/` — live Adaption model/data eligibility audit.
- `DHI_v1/experiments/INFER-002/` — OpenRouter base-model route and zero-credit preflight.
- `DHI_v1/experiments/TRAINING-ACCESS-002/` — current dataset-lineage and Qwen3.6 training-readiness audit.
- `DHI_v1/experiments/ORBIT-VERIFY-002/` — latest exact-head validator, focused pytest and compileall result.

## 8. Active verification

VERIFY-001 remains a historical blocked attempt on the older Deepnote project. It is superseded for the current manifest/grader code by ORBIT-VERIFY-002.

The isolated verifier run `52254373-656f-4d0c-841d-c3a2c621d7cc`, against code commit `421955df46975d8b20fba63f8922949a49b4551c`, passed:
- Cross-record manifest validator: `valid=true`, 30 tasks, Stage A=30, Stage B=0, no errors.
- Focused regression tests: 44 passed, 0 failed (20 manifest-validator + 24 plugin trace grader tests).
- `compileall -q DHI_v1/benchmark`: return code 0.

The machine-readable report is committed in `experiments/ORBIT-VERIFY-002/`. This validates the authored harness integrity only; it does not establish model capability or validate any task through model execution.

## 9. Research methodology now active

- [ORBIT Research Method](docs/13_ORBIT_RESEARCH_METHOD.md) adapts controlled experiments from Karpathy autoresearch and the broader planning/evaluation/regression/adversarial-review workflow from uditgoenka/autoresearch.
- [Experiment record template](experiments/EXPERIMENT_RECORD_TEMPLATE.md) defines the minimum frozen protocol, manifest and run ledger for each research unit.
- This method is now the required operating protocol for benchmark authoring and model research. It does not authorize model inference, training, provider-credit spend, merge or deployment.

## 10. Next authorized action

**Expand and validate the plugin-native Stage A panel. Do not return to a local-harness-only design.**

Completed in the current authoring branch:
- [Task-record JSON Schema](benchmark/task_manifest.schema.json) defines all task-record fields and split requirements.
- [Task register](benchmark/task_manifest.json) now contains **30 Stage A task instances** and 30 task-family records, distributed across all ten strata. Stage A target is 120; Stage B remains unmaterialized and sealed.
- [Plugin-native execution profile](benchmark/PLUGIN_NATIVE_EXECUTION_PROFILE.md) distinguishes connected plugin execution from local file-workspace capabilities and records write/cost boundaries.
- [Plugin tool registry snapshot](benchmark/fixtures/plugin_ecology/plugin_tool_registry.json) pins 15 exact tool contracts for GitHub, TinyFish, Firecrawl, Deepnote, Consensus, Scite, and Wolfram.
- [Execution evidence](benchmark/fixtures/plugin_ecology/plugin_execution_evidence.json) records live plugin access checks, source snapshots, branch mutations/readbacks, the real 404 recovery, and explicit limitations.
- The Northstar synthetic fixture, Node.js current-source snapshot, Firecrawl discovery snapshot, and checkpoint/resume sandbox are committed in the authoring branch.

Current status:
- 30/120 Stage A task instances exist: S01=2, S02=3, S03=4, S04=3, S05=4, S06=4, S07=2, S08=3, S09=3, S10=2.
- 0/120 Stage B tasks exist; Stage B remains sealed.
- S01, S02, S03, S04, S05, S06, S08 and S10 have bounded plugin-native task routes.
- S07 is partial: the GitHub checkpoint was re-read and the resumed report was verified, but model-run interruption/recovery traces remain to be validated.
- S09 is partial: GitHub write/readback/diff works, but the runner still needs a structured pre-action prediction trace.
- Every one of the 30 tasks has `validation.status=ready_for_validation`; none is labelled validated.
- No DHI model inference, benchmark score, training data, or training run has been produced.

Next:
1. Run all remaining benchmark test modules as a broad regression check; manifest validation, 44 focused tests, and compileall have passed.
2. Continue materializing the remaining 90 Stage A tasks with genuinely distinct families, environment evidence, executable postconditions and independently reviewable graders. Remaining quotas: S01=10, S02=9, S03=8, S04=9, S05=8, S06=8, S07=10, S08=9, S09=9, S10=10.
3. Independently review all 30 current task prompts and graders; keep `ready_for_validation` until the task is exercised through the frozen task runner or an independent deterministic reference check.
4. Implement the plugin action-trace adapter for pre-action effect predictions and cross-session checkpoint/recovery events. Close the remaining S07/S09 model-run trace gaps.
5. Build Stage B from 120 structurally distinct holdout tasks only after Stage A and the candidate/interface decision are fixed. Do not put sealed Stage B task bodies in this public repository.
6. Keep model execution disabled until Stage A is complete, independently reviewed and frozen; the matched Qwen3.6/GPT-OSS route has been found but is blocked by the zero-credit OpenRouter account. Do not substitute one model or a free model for the matched screen.
7. Audit the private 10K intent-arbitration export row by row and reconcile its evaluation lineage before any training. Do not use the returned Qwen3.6 LoRA recommendation as authorization.
No DHI candidate model was run. Firecrawl capability discovery cost zero; the discovered package-record execution (one credit) and security/research provider executions (five credits each) were not called. TinyFish Go recovery included a schema-validation rejection followed by a 404 and a successful official-source re-fetch. Consensus search was unavailable because the provider's monthly free quota was exhausted. No Adaption generation/training action was called.

## 11. Latest committed work

| Commit | Change |
|---|---|
| `74d6d044` | Added model-facing pilot entrypoint |
| `d8b82b6f` | Added ORBIT/DHI-v1 background handover snapshot |
| `efaf0dec` | Linked background snapshot and model-pilot entrypoint |
| `65003263` | Defined Git-first research workflow |
| `f670000b` | Added live workspace state file |
| `8d4a548a` | Made live workspace the repository-root session entrypoint |
| `023f836c` | Made live workspace the DHI-v1 README session entrypoint |
| `218b6dce` | Clarified dated handover is a snapshot, not live state |
| `a5ff6f7c` | Recorded Git-first operating decision in the append-only decision log |
| `e049d7ce` / `0f33f5ce` | Recorded INFER-001 blocked preflight and manifest |
| `4a218d92` | Logged first hosted-inference preflight blocker |
| `5a649db4` | Added secret-presence-only runtime probe; no secret value is emitted |
| `ab9946bd` / `8be08d1c` | Recorded isolated runtime creation and quota rejection in INFER-001 artifacts |
| `9edb4d08` | Appended Deepnote quota rejection; secret presence remained unmeasured at that checkpoint |
| `dff718ac` | Corrected earlier access wording |
| `INFER-001 run b39c478a` | Measured both Adaption key variables absent before integration was attached |
| `INFER-001 run 9e34f54b` | Confirmed `ADAPTION_API_KEY` present after secure integration attachment |
| `INFER-001 run 4bd4a7ba` | Authenticated hosted-model catalogue returned 6 IDs; no inference called |
| `4e8b9bf4` / `34dc832f` | Added ADAPTION-001 read-only model/data eligibility audit and manifest; zero credits spent |
| `64439c9c` | Added controlling nested Stage A/Stage B 120+120 benchmark scope |
| `f734b374` | Aligned model-selection screen protocol to ten-stratum scope |
| `72dac025` | Aligned diagnostic benchmark protocol to Stage A/Stage B scope |
| `bbbc653f` | Recorded dated decision resolving 120-vs-240 scope conflict |
| `0955d719` | Clarified why ten strata replace the six-bucket allocation |
| `8b90f9ac` | Clarified benchmark scope decision rationale in the append-only log |
| `MANIFEST-001` | Added schema-backed 240-task register and source-grounded environment coverage audit; zero task instances created |
| `MANIFEST-001a` | Required task-family split hashes, Stage B sealing metadata, and complete validation evidence before a task can be marked validated |
| `PLUGIN-REGISTRY-001` | Pinned 15 actual connected plugin tool contracts and created the Northstar synthetic plugin fixture |
| `ORBIT-TASKS-001` | Authored ten Stage A plugin-native tasks, one per stratum; manifest passed schema validation |
| `ORBIT-TASKS-002` | Expanded the plugin-native Stage A register to 20 independent task families; schema and cross-record checks passed |
| `ORBIT-TASKS-003` | Added Go release verification and TinyFish schema/404 recovery; Stage A reached 22 task families |
| `ORBIT-TASKS-004` | Expanded Stage A to 30 task instances; S07 checkpoint/resume, additional schema, effect and multi-source cases added |
| `ORBIT-REGISTRY-001` | Corrected missing `mcp__GitHub__update_file` contract and recomputed the 16-tool registry SHA-256 |
| `ORBIT-MANIFEST-VALIDATOR-001` | Added cross-record validator and 17 regression tests; required task-instance/family fingerprints |
| `ORBIT-VERIFY-002` | Manifest validator passed 30/30; 44 focused tests passed; compileall passed at 421955df |
| `INFER-002` | OpenRouter listed Qwen3.6 and GPT-OSS tool-capable endpoints; $0 credits; no inference |
| `TRAINING-ACCESS-002` | Qwen3.6 LoRA recommendation returned for the 10K export; evaluation-lineage mismatch keeps dataset on hold |
| `ORBIT-INTEGRITY-001` | Independent static inspection confirmed 30/30 hashes, registered tools, and complete evidence references; Python tests remain unexecuted |
| `ORBIT-METHOD-001` | Reviewed Karpathy and uditgoenka autoresearch; committed ORBIT's adapted evidence-first method and experiment template |
| `ORBIT-REFERENCE-001` | Verified multi-file GitHub workflow and a persistent checkpoint/resume workflow with readback and single-path diffs |
| `ORBIT-REFERENCE-002` | Verified two-source Node/Python release report, Firecrawl fallback recovery, and branch-effect prediction reference |
| `VERIFY-001 run 93645a78` | Exact checkout verified; compileall passed; pytest blocked by missing package before collection |
| `VERIFY-001` retry | Blocked before execution by Deepnote quota in detached and live modes; retry cell is ready |
| `VERIFY-001` | Initial compileall passed; pytest blocked by missing dependency; retry blocked by Deepnote quota |

This file is the live checkpoint on the active research branch. Always fetch the branch head and this file before continuing; do not infer active branch state from main or chat.

## 12. Session continuation checklist

A new agent must:
1. Read this file from the active research branch.
2. Fetch the latest active-branch head and inspect changes since the last checkpoint; compare with main when needed.
3. Read [the Git-first workflow](docs/12_GIT_FIRST_WORKFLOW.md), [the ORBIT research method](docs/13_ORBIT_RESEARCH_METHOD.md), and the manifest validation report.
4. Read the controlling plan and the exact protocol for the next task, including [the panel integrity checkpoint](benchmark/PANEL_INTEGRITY_VALIDATION_2026-11-03.md).
5. Verify the latest run/experiment from its raw artifact reference—not from a chat message.
6. Continue only the single next authorized action above.
7. Commit every meaningful checkpoint, including failures and blockers, then update this workspace before switching tasks.

Do not use this chat as a handover. The repository must remain sufficient to resume the work.
