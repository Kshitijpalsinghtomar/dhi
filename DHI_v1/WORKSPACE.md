# DHI-v1 Live Workspace

**Last updated:** 2026-11-02  
**Repository:** https://github.com/Kshitijpalsinghtomar/dhi  
**Branch:** `main`  
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
phase: benchmark_contract_and_coverage_mapped_task_authoring_pending
status: blocked
status_reason: >
  The 120/240 allocation is defined. A schema-backed task register and a
  source-audited environment coverage matrix now exist. No task instances have
  been materialized: S02 has a missing current-source environment, and several
  other strata are only partially supported. Comparable base-model inference
  access and verified trajectories remain incomplete.
training_status: not_authorized
benchmark_status: scope_defined_task_manifest_unfrozen
last_verified_repository_head_before_this_workspace_checkpoint: 3640e4a86495299688b5e20e098097730743ab53
```
</details>

**No DHI-v1 model capability result is currently established. No DHI-v1 SFT, DPO, RL, or custom latent-predictive training run is authorized.**

## 4. What is implemented

- Deterministic file-workspace environment and pinned SHA-256 fixture.
- Bounded model-to-tool runner with per-turn tool-schema refresh.
- Adaption Responses API adapter and hosted-model catalogue reader.
- Read-only Adaption connector-catalogue discovery.
- Twelve hand-authored diagnostic seeds: eight common executable cases, one Adaption-specific discovery case, and three unsupported future-runtime cases.
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
| INFER-001 hosted inference preflight | Hosted catalogue succeeded; Responses inference not run | Only Gemma 4 31B matches a selected candidate in the hosted catalogue; Qwen/GPT-OSS base comparison unavailable through that route |
| ADAPTION-001 live platform audit | Completed; read-only | Qwen/Gemma require 10,000 effective training rows; GPT-OSS recipe returned for 300 rows; dataset not eligible; zero credits spent |
| Untouched candidate model screening | Not run | No model winner |
| DHI-v1 executed model trajectories | None recorded | No trajectory SFT source yet |
| DHI-v1 training | Not authorized / not run | Data and benchmark gates remain closed |

## 6. Data status and hard stops

- Both 120-row Invent task-spec candidates are quarantined because task-contract JSON was generated as a completion rather than a natural answer/valid execution trajectory.
- The 300-row ORBIT collaboration-behaviour candidate (`169af31f-06e0-4a48-84ab-b84c9f9ce924`) is Invent-sourced and not training-ready: only 98 visible complete pairs were reviewed (25 candidate, 53 revise, 20 reject); 202 rows remain unreviewed. This was model-assisted partial triage, not full independent adjudication.
- Adaption's evaluation of that dataset returned grade A / 9.4 on a 100-row evaluation sample. This is text-quality metadata, not an agent-capability score and not evidence of executed tool traces.
- Live Adaption recommendations confirmed a 10,000-effective-row minimum for Qwen3.6-35B-A3B and Gemma 4 31B. GPT-OSS-20B returned a LoRA recipe for the 300-row set, but this does not override its provenance/review failure.
- Do not train on any of those datasets, do not promote their Adaption grades to capability evidence, and do not fabricate tool traces or outcomes.
- The primary future SFT evidence must be actual model execution in the DHI environment, with raw tool responses, actual state deltas, predictions, and independently verified postconditions.
- Do not spend Adaption credits until the documented data, benchmark, model, and estimate gates pass.

## 7. Current blockers and platform boundary

The previous hosted-model catalogue preflight is complete. The connected Adaption MCP integration is useful for training-registry inspection, dataset inventory/evaluation, data transformation estimates, hyperparameter recommendations, and AutoScientist runs. It does **not** expose the hosted Responses inference operation.

Current facts:
- Live training registry lists Qwen/Qwen3.6-35B-A3B, openai/gpt-oss-20b, and google/gemma-4-31B-it for supported SFT/DPO methods.
- The separate hosted Responses catalogue returned six IDs, but only Gemma 4 31B matched a committed candidate. Qwen3.6 and GPT-OSS were absent from that hosted catalogue. Do not treat registry support as inference access.
- A single Gemma call would test only one integration path; it cannot select the primary model against the mandatory GPT-OSS challenger. It is therefore not the next research action.
- The live Adaption recommender rejected Qwen3.6 and Gemma on the 300-row dataset because they require at least 10,000 effective rows. GPT-OSS returned a recipe, but the dataset remains ineligible.
- The recommender did not return a price quote. Dataset generation/adaptation/augmentation actions expose `estimate: true`; the connected training-launch action spends credits and has no estimate field in its exposed schema. Obtain platform cost information before any chargeable launch.
- No DHI-v1 inference, training run, or new dataset-generation job was launched in ADAPTION-001. Credits spent: zero.

Experiment records:
- `DHI_v1/experiments/INFER-001/` — secure runtime and hosted catalogue preflight.
- `DHI_v1/experiments/ADAPTION-001/` — live Adaption model/data eligibility audit.

## 8. Active verification

VERIFY-001 is blocked on Deepnote's parallel-project quota. Initial run `93645a78-7cd2-4c64-9c84-353fbd31e15c` verified the exact checkout and passed compileall; pytest did not collect tests because pytest was missing. The retry cell (`f0d38652cb8c490595ca474cc5ae2317`) is ready but both detached and live run creation were rejected before execution by the same quota. Machine inspection found one project currently running in the workspace; no project was stopped. Experiment record: `DHI_v1/experiments/VERIFY-001/`.

## 9. Next authorized action

**Author the first executable task families and close harness gaps before materializing the full panel.**

Completed in MANIFEST-001:
- [Task-record JSON Schema](benchmark/task_manifest.schema.json) defines the per-task contract and panel metadata.
- [Task register](benchmark/task_manifest.json) records the 120+120 allocation, all ten strata, Stage B sealing policy, and integrity rules. It intentionally contains zero task instances; no placeholder prompts or fake tasks were created.
- [Environment coverage audit](benchmark/ENVIRONMENT_COVERAGE_MATRIX.md) maps the current runner and graders to each stratum and names unsupported behavior.

Current coverage: S01, S05 (registered schema subset), and S06 (file-workspace only) have bounded execution/grading paths; S03, S04, S07, S08, S09, and S10 are partial; S02 is a harness gap. The existing 12-case integration pilot remains excluded from Stage A and Stage B.

Next:
1. Build and test distinct executable task families for bounded S01/S05/S06, then add partial-stratum probes only with each limitation represented in the task record and scorecard.
2. Implement the missing source adapter for S02, permission-distinct decoy fixtures for S04, and persistent checkpoint/resume for S07 before those full strata are scored.
3. Add explicit deterministic provider-failure injection/retry controls for S08; structured state predicates and effect graders for S09; and adversarial/permission fixtures for S10.
4. Add a panel-integrity validator that checks exactly 12 tasks per stage per stratum, unique task IDs, disjoint A/B family and independence-group hashes, fixture/tool hashes, and Stage B access restrictions.
5. Keep model execution disabled until all 240 tasks are executable and independently reviewed, the A/B family split is hashed, and matched inference access for Qwen3.6 and GPT-OSS is available.

No Stage A/B tasks have been authored or run. No model was run and no Adaption credits were spent in this checkpoint.

## 10. Latest committed work

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
| `VERIFY-001 run 93645a78` | Exact checkout verified; compileall passed; pytest blocked by missing package before collection |
| `VERIFY-001` retry | Blocked before execution by Deepnote quota in detached and live modes; retry cell is ready |
| `VERIFY-001` | Initial compileall passed; pytest blocked by missing dependency; retry blocked by Deepnote quota |

The current version of this file is the active checkpoint. Its own commit SHA is the newest `main` commit when this file is fetched; always inspect the branch head rather than hardcoding a self-referential SHA here.

## 11. Session continuation checklist

A new agent must:
1. Read this file.
2. Fetch the latest `main` head and inspect changes since the last checkpoint.
3. Read [the Git-first workflow](docs/12_GIT_FIRST_WORKFLOW.md).
4. Read the controlling plan and the exact protocol for the next task.
5. Verify the latest run/experiment from its raw artifact reference—not from a chat message.
6. Continue only the single next authorized action above.
7. Commit every meaningful checkpoint, including failures and blockers, then update this workspace before switching tasks.

Do not use this chat as a handover. The repository must remain sufficient to resume the work.
