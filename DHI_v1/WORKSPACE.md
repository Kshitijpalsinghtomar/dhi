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
phase: untouched_base_model_inference_preflight
status: blocked
status_reason: >
  The model-facing runner and Adaption Responses adapter are implemented,
  but the connected Adaption actions expose training registry only. The
  isolated DHI runtime now has ADAPTION_API_KEY mounted; authenticated hosted
  model listing is the next unverified gate.
training_status: not_authorized
benchmark_status: development_pilot_not_frozen
last_verified_repository_head_before_this_workspace_checkpoint: dff718acc0640517c61eb739f62f40485fea3a0e
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
| INFER-001 hosted inference preflight | Hosted catalogue query pending | ADAPTION_API_KEY presence confirmed in isolated runtime; hosted endpoint not yet queried |
| Untouched candidate model screening | Not run | No model winner |
| DHI-v1 executed model trajectories | None recorded | No trajectory SFT source yet |
| DHI-v1 training | Not authorized / not run | Data and benchmark gates remain closed |

## 6. Data status and hard stops

- Both 120-row Invent task-spec candidates are quarantined because task-contract JSON was generated as a completion rather than a natural answer/valid execution trajectory.
- The 300-row ORBIT collaboration-behaviour candidate is not training-ready: only 98 visible complete pairs were reviewed (25 candidate, 53 revise, 20 reject); 202 rows remain unreviewed. This was model-assisted partial triage, not full independent adjudication.
- Do not train on any of those datasets, do not promote their Adaption grades to capability evidence, and do not fabricate tool traces or outcomes.
- The primary future SFT evidence must be actual model execution in the DHI environment, with raw tool responses, actual state deltas, predictions, and independently verified postconditions.
- Do not spend Adaption credits until the documented data, benchmark, model, and estimate gates pass.

## 7. Exact current blocker

The code path is available, but no live hosted inference call has been verified from this workspace.

Adaption flow documented in the repository:
1. Use an API key through a secure runtime/local secret (never store it in Git or chat).
2. Run `python -m DHI_v1.environment.examples.list_adaption_models` to obtain the exact account-visible hosted IDs from `GET /api/v1/models?type=hosted`.
3. Select an ID actually returned by that endpoint; do not assume the training-registry ID is callable.
4. Only after model ID/access and user-approved provider/cost are confirmed, run the development pilot with `DHI_MODEL_PROVIDER=adaption` and `DHI_MODEL_NAME=<exact-hosted-id>`.
5. Preserve the report and per-case traces; label this as a development pilot, not a frozen benchmark or training data.

The connected Adaption MCP actions do not expose the hosted model-listing or Responses inference methods. The existing `DHI — ORBIT Research Lab` Deepnote project remains mixed with unrelated files; DHI work is using the separate `DHI — Isolated Runtime Preflight` project only. The user created the `ADAPTION` Environment variables integration and it is attached to the isolated project. The secret-presence probe confirms `ADAPTION_API_KEY` is present without printing the value. Key validity and hosted model access remain unverified. No credential is recorded in Git.

## 8. Active verification

VERIFY-001 is blocked on Deepnote's parallel-project quota. Initial run `93645a78-7cd2-4c64-9c84-353fbd31e15c` verified the exact checkout and passed compileall; pytest did not collect tests because pytest was missing. The retry cell (`f0d38652cb8c490595ca474cc5ae2317`) is ready but both detached and live run creation were rejected before execution by the same quota. Machine inspection found one project currently running in the workspace; no project was stopped. Experiment record: `DHI_v1/experiments/VERIFY-001/`.

## 9. Next authorized action

**Run the authenticated hosted-model catalogue query in the isolated DHI runtime.**

- The `ADAPTION` Environment variables integration (ID `999bb21e-9bfd-4071-a2bc-d26590958de7`) is attached to project `2eb8d02b-b505-4b39-a33a-32aeda2e1cc4`; the presence-only probe confirms `ADAPTION_API_KEY=true`.
- Fetch the latest committed DHI repository revision into ephemeral project storage and run `python -m DHI_v1.environment.examples.list_adaption_models`.
- Record exact hosted IDs returned by `GET /api/v1/models?type=hosted`, or the redacted HTTP/API error, in `DHI_v1/experiments/INFER-001/`.
- Do not call Responses inference until the catalogue request succeeds. Do not guess model IDs or switch providers.
- A separate Deepnote parallel-project quota still blocks VERIFY-001's test retry; one workspace project is currently running. Do not stop it without explicit approval.
- After a hosted model is confirmed, use only the existing DHI model-facing pilot and obtain provider/cost approval before any inference run.

Benchmark scope audit is complete but the discrepancy remains unresolved: `03_MODEL_SELECTION_AND_ADAPTION.md` specifies 120 initial base-screen tasks (6×20), `05_BENCHMARK_PROTOCOL.md` specifies 240 initial diagnostic tasks (10×24), and the decision log names 120. No file establishes nesting or stage order; neither count is frozen. Warnings now appear in both source documents. Do not choose or freeze a suite until an explicit decision resolves purpose, size, strata, relationship, and split.

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
