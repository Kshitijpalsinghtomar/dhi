# DHI-v1 Research Direction Reset

**Effective date:** 2026-11-11  
**Programme:** DHI-v1 / ORBIT — Predictive Agentic Intelligence  
**Status:** research hypothesis and experimental protocol; not a novelty claim or model result  
**Authority:** This reset supersedes older "next actions" and engineering priorities in earlier handovers and audit documents. `DHI_v1/WORKSPACE.md` remains the session entrypoint.  
**Branch:** `orbit/plugin-benchmark-fixture`; do not merge or modify `main`.

## 1. Hard project boundary

This is DHI-v1 research only. Do not import goals, methods, datasets, metrics, code, or results from GBA/DPAK or any other research project. DHI-v0 remains historical.

The objective is a learned agent, not a product wrapper, fixed router, retrieval-only system, scripted orchestrator, or a larger benchmark harness. Runtime components may expose tools, permissions, schemas, execution, observations, and durable state. The model must learn how to reason and act with that information.

## 2. What the research is about

DHI's target capability is not simply "tool calling" or "predict what a file edit does." The research question is:

> **Can a learned agent maintain and update a joint belief about (a) the task/world state and (b) the available tool ecosystem, then use that belief to decide whether a goal is feasible, discover and compose capabilities, predict the consequences of actions, recover from changes, and verify closure?**

The tool ecosystem is part of the changing environment. Its state can include:
- which tools are visible, discoverable, connected, callable, or unavailable;
- each tool's current name/identity, schema, affordances, preconditions, permissions, freshness, cost, reliability, side effects, statefulness, and reversibility;
- changes to any of the above during a long-running task.

The task/world state includes the user's goal and hard constraints, current resources and artifacts, subgoal dependencies, actual observations, expected effects, and independently verified postconditions.

At decision time, a candidate model should reason over both:
`B_t = (G_t, S_t, E_t, P_t, U_t)`
where `G_t` is goal/constraints, `S_t` task-world state, `E_t` tool-ecosystem state, `P_t` plan/dependency state, and `U_t` uncertainty/provenance.

The hypothesized transition is joint:
`p(S_{t+1}, E_{t+1}, O_{t+1} | B_t, a_t)`
An action can change the task state, the ecosystem state, both, or neither. A model should be able to predict relevant effects, detect when its belief is stale or contradicted, replan, abstain, or ask for authorization.

This is a research formulation. No joint-belief model or learned transition has yet been implemented or measured in DHI.

## 3. Prior-art boundary — do not claim these as DHI novelty

The following work directly overlaps with individual parts of the idea and must be treated as prior art:

| Work | What it already covers | What DHI must not claim |
|---|---|---|
| AutoTool, ICML 2026 / PMLR 306 | SFT/RL for dynamic multi-step tool selection; explicit tool-selection rationales; use of unseen tools from evolving inventories. | Dynamic tool selection or unseen-tool generalization by itself. |
| ToolDriftBench / ToolDriftGuard, IEEE SmartIoT 2026 | Schema, semantic, and capability drift in MCP catalogs; detection and index repair/re-embedding; drift evaluation. | Tool-catalogue drift detection or index refresh by itself. |
| ANTE, arXiv:2610.15368 (2026 preprint) | Pre-action beliefs about action outcomes, verified against execution; per-action learning signals and test-time action optimization in coding agents. | Pre-action outcome prediction or execution-verified belief learning by itself. |
| Qwen-AgentWorld, arXiv:2606.24597 (2026) | Large-scale language world models for agentic environment simulation and next-state prediction across seven domains, trained from large interaction corpora. | General language world modelling, next-state prediction, or agentic simulation by itself. |
| Agent Planning Benchmark, arXiv:2606.04874 (2026) | Long-horizon and step-wise planning diagnostics; extraneous/broken tools and unsolvable tasks; calibrated refusal. | Long-horizon planning or robustness to broken/irrelevant tools by itself. |
| MetaTool, ICLR 2024 | Whether to use tools and which tool(s) to select. | Tool-use awareness or tool restraint by itself. |
| The Tool Illusion, COLM 2026 | Controlled analysis of whether and when tool use benefits web agents across tools, models, frameworks, and benchmarks. | Assuming that adding more tools necessarily improves agents. |

**Working gap (tentative):** the joint, continuously updated belief over task-world state and tool-ecosystem state, where the same plan must reason about capability composition, permissions/schema/precondition changes, action effects, and independently verified goal closure. The gap is not established as novel. Before any novelty claim, perform a systematic primary-literature search for work that jointly models these two state spaces and evaluates their interaction under long-horizon execution.

## 4. Competing hypotheses

These are falsifiable alternatives, not conclusions.

### H0 — A strong modular baseline is sufficient
A conventional agent with dynamic tool retrieval, a planner, and a separate action-effect predictor performs as well as a jointly maintained ecosystem/world belief. If so, DHI should prefer the simpler modular design.

### H1 — Joint ecosystem/world belief improves robustness
A model trained to update one structured belief over task state and tool-ecosystem state will recover more reliably from mid-task tool removal, schema changes, permission changes, and replacement tools than the same base model using independent retrieval and action prediction modules.

### H2 — Explicit feasibility reasoning improves safe completion
A model trained to identify capability coverage, dependency gaps, permission blockers, and unavailable actions before execution will reduce invalid/unauthorized calls and false completion while preserving success on feasible tasks. It should also become better calibrated at stopping or asking for authorization on infeasible tasks.

### H3 — Joint prediction is only useful at longer horizons
The joint method may show little or no advantage on single-tool tasks, but outperform modular baselines when multiple tools form a dependency chain and ecosystem changes occur after partial progress. This predicts a horizon-by-drift interaction, not a universal uplift.

Reject the central hypothesis if the joint method does not beat the strongest modular baseline on held-out tool ecosystems, or if its gains come with worse safety, false-closure, calibration, latency, or cost.

## 5. Required experimental comparisons

All candidate methods must use the same base-model revision, task, tool snapshot, permission state, prompts/instructions, decoding settings, execution environment, and action/token budget.

- **B0 — Native policy:** visible tool schemas and normal model tool use; no added catalogue index, explicit joint belief, or external effect predictor.
- **B1 — Retrieval then plan:** retrieve tools from the current catalogue, then plan and execute; update the index when the catalogue is refreshed.
- **B2 — Plan/retrieve + separate effect prediction:** B1 plus a separate pre-action effect predictor, with independent task and catalogue state.
- **DHI — Joint belief candidate:** one learned policy maintains task/world and tool-ecosystem belief, predicts effects on both, tracks uncertainty/provenance, and replans after observed discrepancies.

Do not compare different models and call the result an architectural ablation. First compare approaches on the same model; model-family comparisons are a separate experiment.

## 6. Experimental environment and task factors

The experiment should vary these factors independently:
1. **Tool availability:** tool present, hidden-but-discoverable, disconnected, removed, or replaced.
2. **Contract drift:** renamed tool, changed parameter schema, changed output semantics, or incompatible version.
3. **Capability drift:** capability added, removed, narrowed, or provided by a replacement tool.
4. **Permission drift:** read-only becomes write-capable, permission is revoked, or explicit consent is missing.
5. **World-state change:** observations contradict an earlier action forecast or an action has a partial/unexpected effect.
6. **Planning horizon:** one action, a short dependent chain, and a long chain with interruption/resumption.
7. **Feasibility:** fully solvable, solvable only after discovery/recovery, blocked by permissions, or genuinely infeasible.

Use counterbalanced variants and hold out tool names, schemas, combinations, and task families. Do not expose hidden grader state or future tool snapshots to the model.

## 7. Primary outcomes and hard guards

Primary:
- independently verified end-to-end goal closure on feasible tasks;
- correct feasibility classification and calibrated abstention on infeasible/permission-blocked tasks;
- recovery success after tool/ecosystem drift;
- transfer to held-out tool names, schemas, and capability combinations.

Diagnostic:
- capability discovery precision/recall;
- valid tool invocation rate and argument-schema compliance;
- dependency-order correctness;
- calibration/accuracy of pre-action predictions for both task state and ecosystem state;
- detection latency after drift;
- replanning quality and extra/redundant calls;
- action count, latency, token use, and monetary cost.

Non-compensable guards:
- zero unauthorized or forbidden side effects;
- no fabricated tool availability, permission, result, or completion;
- no hidden-state leakage;
- final closure only when independent postconditions pass;
- no false success on blocked or infeasible tasks.

Report per-factor and per-stratum results, not only an aggregate. Use paired tasks, multiple seeds where stochastic, uncertainty intervals, and an independent evaluator.

## 8. First research execution — gated plan

### No-model research work: current state
1. **Prior art:** an initial focused review has identified direct overlap in dynamic tool selection (AutoTool), catalogue drift (ToolDriftBench/ToolDriftGuard), verified pre-action beliefs (ANTE), environment world models (Qwen-AgentWorld), long-horizon planning diagnostics (APB), and tool-use restraint (MetaTool / The Tool Illusion). This is not yet a saturation review and supports no novelty claim.
2. **Joint observation/forecast contract:** `DHI_v1/research/joint_state.py` is now committed. It models independently observed task/world and tool-ecosystem snapshots, keeps their diffs separate, and scores each forecast against observations. It distinguishes omitted forecasts from explicit no-change predictions; preserves unknown metadata; and rejects partial or cross-scope diffs.
3. **Focused verification:** 13 unit tests and compileall passed against the isolated local copy. The exact committed GitHub copies have been mirrored to the Deepnote verifier for an exact-file focused run; until that run completes with inspectable output, do not mark the committed implementation verified.
4. **Next code action:** integrate a read-only observer from the actual `DHIEnvironment` catalogue/workspace state into `ObservedJointState`. It must preserve complete-snapshot scope, explicit unknown fields, visibility/discoverability, permission state, exact schema fingerprints, and provenance. Add focused tests against real DHI environment fixtures. Do not touch `agent_runner.py` until the observer and provenance boundaries are proven.
5. **Then:** create a small paired deterministic mechanism test that changes one environment/tool-ecosystem property at a time. It tests observability and score identifiability only; it does **not** establish learned agent ability. Freeze the pilot and scoring before any model result is observed.

### Work that requires explicit model-run authorization and a funded/approved route
1. Matched untouched-base inference on the already selected DHI candidates (Qwen3.6-35B-A3B primary and GPT-OSS-20B challenger); include the multimodal challenger only for executable multimodal cases.
2. Preserve model-originated forecasts, actual tool calls/responses, state deltas, catalogue changes, replans, costs, and independent postcondition results.
3. Generate candidate training trajectories only from actual model executions. Independently adjudicate, deduplicate, and split them by tool/schema/task family.
4. Run one controlled SFT baseline only after the dataset, model, evaluation, permission, and cost gates pass. Test joint-belief supervision as a separate ablation; do not combine SFT, DPO, RL, and a custom world-model loss in one experiment.

**No model run or training is authorized by this document.** At the last live check on 2026-11-11, OpenRouter reported zero account credits; the Deepnote verifier had no model-provider integration; all DHI task manifest model-run flags remain false. A free-model catalogue listing is not authorization, is not a matched candidate comparison, and does not establish privacy/retention equivalence.

## 9. Explicit stop list — prevent another infrastructure detour

Unless a specific research hypothesis requires it, do not:
- expand the 30-task plugin-native panel toward 120/240;
- add more provider adapters, credentials, test fixtures, or benchmark strata;
- continue S07/S09 harness hardening as the main workstream;
- produce more scripted reference workflows and present them as model evidence;
- generate or augment synthetic training data;
- launch Adaption training or spend provider credits;
- change candidate models or model-run flags;
- merge the branch or modify `main`.

These items can be reopened only when they are a demonstrated blocker to the declared research experiment or the user explicitly redirects the programme.

## 10. Next-agent execution contract

At the start of every session:
1. Read `DHI_v1/WORKSPACE.md` and this file, then inspect the exact active branch head.
2. Work only in `Kshitijpalsinghtomar/dhi`, branch `orbit/plugin-benchmark-fixture`. Never mix other research repositories.
3. State the single research question and hypothesis before coding. Tie every code change to an experiment or an observed falsifier.
4. Do not infer that a test passed from the presence of a test file, old CI badge, or old verification report. Run against the exact commit and retain the command, exit code, output, and SHA.
5. Keep these evidence labels separate: scripted reference; offline unit/contract test; deterministic mechanism test; actual model inference; model-generated execution trajectory; adjudicated training example; training run/checkpoint.
6. If blocked, record the precise blocker and continue with the highest-value no-cost research action. Do not substitute unrelated infrastructure work.
7. Before finishing, update the evidence ledger and this workspace with what changed, exact commit, tests actually run, and the next single research action.

## 11. Primary sources to review

- AutoTool (ICML 2026), PMLR 306: https://proceedings.mlr.press/v306/zou26p.html
- ToolDriftBench / ToolDriftGuard (IEEE SmartIoT 2026): https://ieeexplore.ieee.org/abstract/document/11677805
- ANTE (2026 preprint): https://arxiv.org/abs/2610.15368
- Qwen-AgentWorld (2026): https://arxiv.org/abs/2606.24597 and https://github.com/QwenLM/Qwen-AgentWorld
- Agent Planning Benchmark (2026): https://arxiv.org/abs/2606.04874
- MetaTool (ICLR 2024): https://proceedings.iclr.cc/paper_files/paper/2024/hash/bc12914d66b41b6bfc2d3a5decdb498-Abstract-Conference.html
- The Tool Illusion (COLM 2026): https://www.microsoft.com/en-us/research/publication/the-tool-illusion-rethinking-tool-use-in-web-agents/
- Plan or Retrieve First? (Findings of EMNLP 2026 Industry Track): https://aclanthology.org/2026.emnlp-industry.19/

All claims of novelty must wait until a broader literature search, full-paper review, and independent critique are complete.
