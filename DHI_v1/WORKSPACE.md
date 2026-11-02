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
  isolated Deepnote secret-presence probe was rejected before execution by the
  parallel-project quota, so secure key presence and hosted IDs remain unverified.
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
| INFER-001 hosted inference preflight | Blocked on 2026-11-02 | Training registry refreshed; no connected MCP inference action; isolated secret-presence probe rejected before execution by Deepnote project quota |
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

The connected Adaption MCP actions do not expose the hosted model-listing or Responses inference methods. The existing Deepnote project `DHI — ORBIT Research Lab` has no attached integrations; its workspace has only `[Demo] Snowflake`, and its file inventory includes unrelated DPAK work. Do not run DHI inside that mixed project. A clean isolated Deepnote project was created for a presence-only secret probe, but its detached run was rejected before execution because the parallel-running-project quota was exceeded. Therefore secret presence is unmeasured, not known absent. No credential is recorded in Git. Never ask the user to paste a key into chat.

## 8. Next authorized action

**Unblock INFER-001 through the isolated DHI runtime.**

- Make one Deepnote parallel-run slot available by stopping an idle project only with explicit user approval, or provide another clean secure runtime. Do not stop any running project automatically.
- Configure `ADAPTION_API_KEY` (or `DHI_ADAPTION_API_KEY`) as a secure environment secret in the isolated project `2eb8d02b-b505-4b39-a33a-32aeda2e1cc4`; do not paste it into chat or commit it.
- Run the committed presence-only probe `DHI_v1/experiments/INFER-001/check_runtime_secret_presence.py` first. It must output booleans only.
- If present, run `python -m DHI_v1.environment.examples.list_adaption_models` and record exact hosted IDs or the redacted API error in `DHI_v1/experiments/INFER-001/`.
- Only after an exact hosted model is confirmed and provider/cost are approved, launch the existing development pilot.
- Do not use the mixed DHI/DPAK Deepnote project, silently switch provider, guess model IDs, train, or generate another dataset.

Before a confirmatory base-screen design, reconcile the repository's scope discrepancy: the model-selection document describes a 120-task initial screen (6×20), while the benchmark protocol describes a 240-task diagnostic suite (10×24). The existing 12-case development pilot is neither. Record the intended staged design in the decision log before freezing a larger suite.

## 9. Latest committed work

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
| `9edb4d08` | Appended Deepnote quota rejection and corrected interpretation (secret presence unmeasured) |
| `dff718ac` | Corrected earlier access wording: secret presence remains unverified |

The current version of this file is the active checkpoint. Its own commit SHA is the newest `main` commit when this file is fetched; always inspect the branch head rather than hardcoding a self-referential SHA here.

## 10. Session continuation checklist

A new agent must:
1. Read this file.
2. Fetch the latest `main` head and inspect changes since the last checkpoint.
3. Read [the Git-first workflow](docs/12_GIT_FIRST_WORKFLOW.md).
4. Read the controlling plan and the exact protocol for the next task.
5. Verify the latest run/experiment from its raw artifact reference—not from a chat message.
6. Continue only the single next authorized action above.
7. Commit every meaningful checkpoint, including failures and blockers, then update this workspace before switching tasks.

Do not use this chat as a handover. The repository must remain sufficient to resume the work.
