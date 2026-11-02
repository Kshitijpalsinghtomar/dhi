# DHI-v1 / ORBIT — Agent Handover

**Snapshot date:** 2026-11-02  
**Repository:** https://github.com/Kshitijpalsinghtomar/dhi  
**Branch:** `main`  
**Repository head at handover review:** `74d6d044b7c43d48cf923e7359e3b60c821d9412` — `Add explicit entrypoint for model-facing DHI pilot`  
**Status:** Active research programme; no DHI-v1 model result and no DHI-v1 training run recorded.

This is a dated background snapshot, not the live state file. **Always read `DHI_v1/WORKSPACE.md` first**; it is the authoritative current continuation pointer and supersedes this snapshot when the two differ. Follow `DHI_v1/docs/12_GIT_FIRST_WORKFLOW.md` and commit progress incrementally. This file preserves the 2026-11-02 recovery context; it is not meant to be copied into chat or regenerated at the end of every session.

## 1. Identity and project boundaries

- **Active programme:** DHI-v1 — Predictive Agentic Intelligence.
- **User-designated model codename:** ORBIT. Existing repository records also use ORBIT as the codename for generated task/data artefacts and task IDs. Treat this as naming within the DHI programme, not a separate research project.
- **Historical programme:** DHI-v0 is preserved separately. Root-level `NEXT_STEP.md`, `docs/DHI_CURRENT_STATE_AND_NEXT_STEPS.md`, `docs/DHI_DECISION_LOG.md`, and `docs/DHI_DESIGN_METHODOLOGY.md` describe DHI-v0; they are not the active DHI-v1 next-step authority.
- **Separate research:** GBA/DPAK quantization and other projects are not DHI evidence. DHI's master plan assigns custom predictive-state/architecture experiments to GBA when that stage is justified, while DHI owns its model, data, benchmark, and programme records. Do not import GBA/DPAK results or hypotheses into DHI unless a DHI decision explicitly links them.

## 2. Programme objective

DHI-v1 aims for learned, general-purpose agentic capability—not a prompt wrapper, RAG collection, fixed keyword router, or externally orchestrated agent. Target behaviours include:

- Representing user goals, hard constraints, preferences, dependencies, and postconditions.
- Recognizing when a capability is missing from the currently visible tools.
- Discovering relevant tools/apps/connectors from a changing inventory.
- Comparing tool affordances, schemas, preconditions, permissions, costs, freshness, side effects, and reversibility.
- Choosing between direct answer, verification, discovery, execution, clarification, delegation, and safe stop.
- Hierarchical planning across dependent actions and long horizons.
- Alternating planning, action, observation, verification, recovery, and replanning at appropriate levels.
- Predicting task-relevant action effects and comparing predictions with actual environment state.
- Verifying final postconditions and reporting completion honestly.
- Preserving relevant task state across long tasks and context boundaries.
- Maintaining safety, permission discipline, and transfer to unseen tools/workflows.

The model must learn these decisions. The runtime supplies current tool manifests, credentials/permissions, execution, observations, and durable state interfaces; these are not substitutes for learned intelligence.

## 3. Model candidates — selection is not a result

The current shortlist in `DHI_v1/docs/03_MODEL_SELECTION_AND_ADAPTION.md` is:

1. Primary candidate: `Qwen/Qwen3.6-35B-A3B`.
2. Mandatory tool-use challenger: `openai/gpt-oss-20b`.
3. Multimodal challenger: `google/gemma-4-31B-it`.

This is a candidate selection based on registry/model fit, not a measured ranking. Untouched-base screening must precede training. Recheck the live Adaption training registry and hosted inference catalogue at run time. The hosted inference ID must come from the account's authenticated `GET /api/v1/models?type=hosted` response; do not assume a training-registry ID is callable.

Adaption's documented route is `POST /api/v1/responses`. The repository contains `DHI_v1/environment/adaption_responses.py` and a model adapter. Connected Adaption MCP actions in this session do not expose the hosted Responses endpoint; a valid API key is required at runtime. Do not put keys in GitHub or dataset rows.

## 4. Implemented environment and benchmark

The repository contains:

- Deterministic file-workspace environment: `DHI_v1/environment/dhi_env.py`.
- Model/tool loop with per-turn visible-schema refresh: `DHI_v1/environment/agent_runner.py`.
- Adaption Responses adapter and read-only connector catalogue discovery.
- Pinned SHA-256-verified fixture and safe workspace materialization.
- Event trace schema, state snapshots/deltas, prediction comparison, postcondition closure, and protected-path checks.
- Hand-authored 12-case development seed suite: `DHI_v1/benchmark/pilot_cases.json`.
- Eight common executable file-workspace cases.
- One Adaption-only read-only connector-catalogue discovery case.
- Three cases not yet supported by the current environment: live current-source/web verification, decoy selection across external permissioned providers, and cross-session resume.
- Model-facing entrypoints, including the latest `DHI_v1/benchmark/run_model_pilot.py` added at repository head `74d6d044`.

**Environment limits:** this is a deterministic file-workspace harness, not a production OS/container sandbox. It does not expose arbitrary shell, Python, browser, or external connector execution. Local catalogue search is lexical. Adaption discovery is read-only; it does not invoke discovered connectors or perform external mutations.

### Evidence that exists

- Scripted reference pilot: **8/8** supported common cases passed, with 12 tool calls, 20 turns, and 8 successful closures. This verifies the harness, fixture, scripted reference policy, and deterministic graders.
- The scripted reference client is **not an LLM**. The result is not a model capability score and its traces are not model-generated training trajectories.
- Historical local test reports: 75 tests passed across environment and benchmark modules on 2026-10-31; focused ORBIT adjudication/fixture/catalogue tests also passed in Deepnote. Do not claim the latest repository HEAD has been retested unless a new run is recorded.
- **No untouched-base DHI-v1 model screening result is recorded.**
- **No DHI-v1 SFT, DPO, RL, or custom latent-predictive training run is recorded or authorized.**

## 5. ORBIT data and training gates

Keep the data products separate:

1. **Benchmark task specifications:** evaluation contracts, fixtures, tool manifests, graders, and splits. These are not SFT completions.
2. **Optional one-step decision supervision:** prompt includes the task, state, tool manifest, and constraints; completion is only the proposed next decision/action. It is not an executed call or trajectory.
3. **Executed agent trajectories:** primary future SFT source. They must come from actual model execution in the environment, with real tool calls/results, state deltas, prediction comparisons, and independently verified postconditions.
4. **Preference pairs:** later DPO source, only from same-task/equivalent-initial-state alternatives with independently verified outcomes.

### Invent/task datasets currently quarantined or blocked

- Task-spec candidate A: dataset `1eccaa36-bdc7-4d6e-ac8d-41b20d9425e2`, 120/120 rows, Grade B, score 8.0 → 7.7; completion quality at the 2.7th percentile. Quarantined because the generated completion was task-contract JSON rather than a natural response/valid trajectory.
- Task-spec candidate B: dataset `be05757d-2f24-45d4-8768-659268d9d18e`, 120/120 rows, Grade C, score 7.0 → 6.6; same target-format mismatch. Quarantined.
- Collaboration-behaviour instruction candidate: dataset `169af31f-06e0-4a48-84ab-b84c9f9ce924`, 300 rows, Adaption Grade A / 9.4. Only 98 complete visible prompt/completion pairs were audited; provisional triage was 25 candidate, 53 revise, 20 reject. The other 202 rows were not reviewed. This is partial, model-assisted triage—not full human/expert adjudication. SFT/DPO remains blocked.

For the 300-row dataset, required sequence is: obtain full authenticated export; reconcile the 98 prompt fingerprints; establish explicit prompt/completion columns; adjudicate the remaining rows; independently verify semantic correctness, factual support, execution claims, and safety; correct/discard revise/reject rows; assign grouped train/validation/test splits; run `DHI_v1/benchmark/orbit_adjudication.py`; inspect its report. The gate fails closed on partial exports and incomplete verification.

Adaption Invent may create task prompts/contracts or carefully specified atomic decisions. It must not fabricate tool execution, tool outputs, state changes, tests, or verified completion. Do not spend further Invent credits on the rejected task-spec-as-completion format. Do not train merely because a dataset says Grade A or a platform marks it ready.

## 6. Current continuation point

The latest commit adds an explicit model-facing benchmark entrypoint. The next evidence-producing step in the current programme is an **untouched-model run against the existing development pilot**, once the exact hosted inference model ID and required credentials/provider configuration are available.

For Adaption, repository instructions use:

- `ADAPTION_API_KEY` supplied only through a secure local/runtime secret.
- `DHI_MODEL_PROVIDER=adaption`.
- `DHI_MODEL_NAME` set to the exact hosted model ID returned by the authenticated hosted-model catalogue.
- `python -m DHI_v1.benchmark.run_model_pilot` (or the documented benchmark CLI).

For other OpenAI-compatible serving, use the provider's base URL, key, and exact model slug through runtime environment variables. Never commit credentials. A run may incur provider charges; do not launch without the user's approved provider/model/cost context.

Keep the first model run a development-pilot result, not a frozen benchmark claim. Use fresh fixture workspaces, record model revision/decoding/tool manifests/traces, and verify the raw report. Compare candidate models with the same tasks, fixtures, visible tools, permissions, and budgets. Do not let the scripted reference client's plan leak into model execution.

After the integration pilot, return to the broader base-screen design only after resolving the benchmark-size inconsistency below. Do not start training or dataset generation before the documented gates pass.

## 7. Repository inconsistencies to resolve before a confirmatory screen

- `DHI_v1/docs/03_MODEL_SELECTION_AND_ADAPTION.md` specifies an initial 120-task base screen (six groups of 20).
- `DHI_v1/docs/05_BENCHMARK_PROTOCOL.md` specifies an initial 240-task diagnostic suite (ten strata of 24).
- The implemented development pilot is a 12-case seed suite: eight common executable cases, one Adaption-only case, and three unsupported cases.
- These are different stages/scope descriptions. Do not silently choose one as the frozen confirmatory benchmark. Reconcile the intended base-screen version in the decision log before treating a larger suite as frozen.
- `DHI_v1/README.md` previously linked to the non-existent `04_METHODS_AND_INTERVENTION_GATES.md`; the actual file is `04_METHODS_AND_WHEN_TO_USE.md`. This handover update corrects the navigation link and adds the latest benchmark entrypoint.

## 8. State-management rules for every continuation

1. Start by reading this file and the current `main` head; never rely on chat memory as the project state.
2. Read the relevant controlling protocol, decision log, handover, workspace records, and experiment outputs before acting.
3. The repository is the authoritative source for DHI programme state. Deepnote may hold raw/private execution artefacts; cite their exact notebook/run/file in the repository record, and do not treat an unrecorded chat summary as evidence.
4. Append decisions and dated findings to `DHI_v1/docs/07_DECISIONS_AND_RESEARCH_LOG.md`; do not rewrite history except with an explicit correction note.
5. Update `DHI_v1/WORKSPACE.md` whenever the current state, blocker, or next authorized action changes. This dated handover remains background only.
6. Record every experiment's question, exact method/configuration, environment, data/model revision, raw artifact locations, metrics, limitations, decision, and next step.
7. Label every result as exploratory, scripted-reference, model-generated, independently verified, rejected, inconclusive, or frozen as appropriate.
8. Never present scripted traces as model-generated data; never present Adaption quality scores as capability scores.
9. Do not introduce a new architecture, training method, dataset direction, or research hypothesis unless it is supported by the existing DHI evidence and explicitly recorded as a proposal/decision.
10. Do not mix DHI-v1 with DHI-v0, GBA/DPAK, or other projects. Cross-project links must be explicit and evidence-based.

## 9. Controlling files

- Programme navigation: `README.md`, `DHI_v1/README.md`.
- Live state and next action: `DHI_v1/WORKSPACE.md` (read first every session).
- Incremental checkpoint/commit rules: `DHI_v1/docs/12_GIT_FIRST_WORKFLOW.md`.
- Dated background handover snapshot: this file.
- Programme plan and gates: `DHI_v1/docs/00_MASTER_DEVELOPMENT_PLAN.md`.
- Capability scorecard: `DHI_v1/docs/01_CAPABILITY_RUBRIC_AND_SCORECARD.md`.
- Capability specification: `DHI_v1/docs/02_TOOL_AWARENESS_AND_LONG_HORIZON.md`.
- Candidate selection/platform limits: `DHI_v1/docs/03_MODEL_SELECTION_AND_ADAPTION.md`.
- Methods and intervention gates: `DHI_v1/docs/04_METHODS_AND_WHEN_TO_USE.md`.
- Benchmark protocol: `DHI_v1/docs/05_BENCHMARK_PROTOCOL.md`.
- Trajectory/data contract: `DHI_v1/docs/06_DATA_AND_TRAJECTORY_CONTRACT.md`.
- Append-only decisions: `DHI_v1/docs/07_DECISIONS_AND_RESEARCH_LOG.md`.
- ORBIT data-generation method review: `DHI_v1/docs/08_ORBIT_DATA_GENERATION_METHOD_REVIEW.md`.
- ORBIT adjudication gate: `DHI_v1/docs/09_ORBIT_ADJUDICATION_GATE.md`.
- Scripted reference results: `DHI_v1/docs/10_DHI_SCRIPTED_REFERENCE_PILOT_RESULTS.md`.
- Development task suite: `DHI_v1/benchmark/README.md`.
- Environment/runtime instructions: `DHI_v1/environment/README.md`.
