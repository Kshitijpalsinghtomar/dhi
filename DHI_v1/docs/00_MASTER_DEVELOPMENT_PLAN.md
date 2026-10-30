# DHI-v1 Master Development Plan

**Version:** 1.0  
**Date:** 2026-10-31  
**Status:** Active controlling plan; first deterministic environment prototype implemented. No v1 training run authorized yet.  
**Programme:** DHI-v1 — Predictive Agentic Intelligence

## 1. The actual ambition

DHI-v1 is not a chatbot with a better prompt, a RAG collection, a fixed list of tool calls, or a wrapper around other agents.

The intended model is a **general-purpose, tool-aware, long-horizon predictive agentic model**. Its learned capabilities should include:

- General reasoning and conceptual understanding.
- Awareness that useful external capabilities may exist beyond the tools already placed in the immediate prompt.
- Discovery of tools/apps/connectors when the available inventory is insufficient.
- Reasoning about tool affordances, schemas, preconditions, permissions, costs, freshness, and side effects.
- Planning over multiple dependent steps, multiple apps, and long time horizons.
- Choosing when to answer from model knowledge, when to verify, when to search for a tool, when to invoke one, and when not to use a tool.
- Predicting the relevant effects of candidate actions before execution.
- Updating plans when execution differs from expectation.
- Maintaining task state across long workflows and context boundaries.
- Verifying actual final state against the original goal and refusing to claim success without evidence.

The model's intelligence must be in its learned parameters and internal computation. A runtime is still required to expose tool descriptions, permissions, actual execution, environment observations, and durable state. The runtime is an interface and evidence source; it must not be mistaken for the intelligence itself.

## 2. The user-originated failure that DHI must address

The project's motivating observation is that current assistants can possess many apps, plugins, APIs, browser tools, coding tools, and connectors yet fail to use the wider ecosystem effectively. Common failure modes include:

1. Using only familiar knowledge or the currently visible tools, without checking whether a better capability exists.
2. Not recognizing that a task requires an app, service, or connector not already in the current tool list.
3. Failing to search a tool/app catalogue or capability registry.
4. Choosing a tool by familiar name rather than matching its actual affordances to the task.
5. Calling a tool when no tool is needed, or failing to call one when current evidence or an external action is necessary.
6. Making one plan and following it after new evidence invalidates it.
7. Performing shallow one-step loops instead of nested planning, execution, monitoring, recovery, and verification.
8. Losing the goal, constraints, intermediate state, or reasons for previous actions over a long task.
9. Reporting a task as complete because an action returned successfully, without checking the requested postconditions.

DHI must be tested directly against these failures. These are hypotheses about a broad model weakness, not universal claims about every existing agent.

## 3. Model identity and scope

### 3.1 Product/research category

A general-purpose model with native agentic competence. Tool use is not the only capability: it must retain useful language, conceptual, analytical, coding, and multimodal reasoning.

### 3.2 Learned intelligence targets

| Capability | What must be learned by the model |
|---|---|
| Broad reasoning | Solve new problems, reason about constraints, causality, abstraction, and uncertainty. |
| Tool ecology awareness | Recognize task capabilities and discover available tools from dynamic descriptions/registries. |
| Tool affordance reasoning | Understand which tools can do what, prerequisites, limits, side effects, and failure modes. |
| Tool selection | Choose the best available tool or combination, and identify when no suitable tool exists. |
| Hierarchical planning | Decompose goals into milestones, dependencies, and executable steps. |
| Multi-loop control | Alternate planning, acting, observing, evaluating, and replanning at appropriate levels. |
| Predictive state reasoning | Predict task-relevant consequences of actions and state transitions. |
| Goal closure | Determine whether all required final-state conditions are actually satisfied. |
| Context continuity | Preserve relevant task state, constraints, pending work, and prior outcomes through long workflows. |
| Calibration | Match confidence, computation, and verification effort to uncertainty and stakes. |
| Safe agency | Respect authorization, permissions, irreversible actions, privacy, and tool-output trust boundaries. |
| Transfer | Generalize to tools, schemas, workflows, and environments not seen in training. |

### 3.3 Explicit exclusions

The following do not by themselves count as DHI intelligence:

- A system prompt that tells the model to use tools.
- A hard-coded router that maps a few keywords to a fixed tool.
- RAG that retrieves a tool name or answer but does not teach the model tool affordance reasoning.
- A multi-agent orchestrator whose intelligence is entirely supplied by an external model.
- Synthetic tool outputs that were never executed.
- Long chain-of-thought text without measurable improvement in reasoning or execution.
- A high AutoScientist win rate on its own training/evaluation set.
- A larger parameter count without a capability delta.

These may be useful infrastructure or training aids, but they are not the claimed model contribution.

## 4. Candidate integrated architecture

The long-term model should use a shared trainable backbone with internal computational components that can be developed and ablated separately.

### Candidate functional decomposition

1. **General representation core:** encodes user request, relevant conversation history, observations, and multimodal inputs.
2. **Goal/constraint representation:** encodes desired outcome, hard constraints, preferences, dependencies, and postconditions.
3. **Tool-affordance representation:** reasons over a live tool capability manifest and learned tool-function abstractions, rather than memorizing only tool names.
4. **Hierarchical policy:** chooses direct answer, evidence lookup, tool discovery, single call, multi-tool sequence, parallel work, delegation, clarification, safe stop, or replan.
5. **Predictive transition mechanism:** estimates task-relevant next state/delta for a candidate action, conditioned on the current state and goal.
6. **Uncertainty/risk estimator:** identifies uncertain facts, unreliable tools, costly or irreversible actions, and when more evidence is needed.
7. **Closure verifier:** evaluates whether actual final state satisfies the original goal and protected invariants.

This is a target decomposition, not an assertion that seven separate modules must be implemented. The first Adaption prototype may express these capabilities through shared model weights and structured trajectory supervision. GBA can later test whether explicit latent heads or a new computational graph improve the model.

### Model-level versus runtime-level boundary

| Model learns | Runtime supplies |
|---|---|
| When tool discovery is needed. | Current catalogue of tools actually available to this user/session. |
| Which affordances match a task. | Tool descriptions, input schema, output schema, and callable endpoint. |
| How to plan and sequence calls. | Credentials, permissions, consent, and actual invocation. |
| How to interpret observations and revise plans. | Raw tool results and environment state. |
| What effects are expected and whether task is closed. | Execution, tests, state diffs, logs, and authoritative outcome signals. |
| When to save/recall task state. | Durable state storage and context restoration interface. |

The model must learn to request discovery and use returned catalogues. The catalogue itself is dynamic and cannot be frozen into model weights.

## 5. The three nested control loops

DHI should not behave as a single prompt → one response loop.

### Outer strategic loop

- Interpret the requested outcome.
- Establish success conditions and constraints.
- Estimate task horizon, dependencies, risk, and resource budget.
- Decide whether to plan the whole task, start with a bounded milestone, or ask one essential clarification.
- Revisit strategy when the objective, resources, or available tools materially change.

### Middle plan/execution loop

- Maintain a dependency-aware task graph.
- Identify the next unblocked action.
- Discover/select the capability needed for that action.
- Predict important consequences.
- Execute one action or a safe group of independent actions.
- Record actual result and update task state.

### Inner verification/recovery loop

- Validate tool output and state changes.
- Compare predicted with actual effects.
- Detect errors, missing outputs, stale evidence, partial success, or side effects.
- Retry only when safe and justified.
- Change strategy when repeated attempts provide no new information.
- Confirm postconditions before marking a task complete.

The model should learn when to enter, continue, shorten, parallelize, or stop each loop. Fixed-depth repeated reflection is not the objective.

## 6. Model and training strategy

### Selected first Adaption candidate

**Qwen/Qwen3.6-35B-A3B** is the primary candidate for DHI-v1's first trained agentic prototype.

**Mandatory challenger:** openai/gpt-oss-20b.  
**Multimodal alternative:** google/gemma-4-31B-it.

This selection is based on current Adaption registry compatibility, Qwen's sparse 35B / approximately 3B-active model design, reasoning support, long context, multimodal input, and agentic-coding positioning. GPT-OSS is a mandatory comparator because its published model capabilities explicitly include function calling, web/Python tool use, structured output, and adjustable reasoning effort. The untouched bases must be screened on the same diagnostic suite before any training.

The full selection rationale and limitations are in 03_MODEL_SELECTION_AND_ADAPTION.md.

### Training stages

1. **Base screening:** compare untouched candidate models with identical tool manifests, harness, task sets, decoding policy, and budgets.
2. **Trajectory SFT:** teach actual tool/task workflows from verified environment-executed trajectories. Start with standard action-observation trajectories; do not immediately add every proposed auxiliary objective.
3. **Predictive/closure SFT ablation:** add structured pre-action forecasts, observed state deltas, and verified postconditions to a matched subset. Compare against ordinary agentic SFT.
4. **DPO:** only after high-quality preference pairs represent actual better/worse tool choices, plans, recoveries, and completion decisions.
5. **Environment-grounded RL:** only after the sandbox, reward signals, and independent evaluator are valid. This requires a custom training loop outside the currently exposed Adaption API.
6. **Latent predictive objective:** only after forecast supervision shows useful signal. Implement the actual trainable state-prediction mechanism in GBA; text forecasts alone do not establish a JEPA-like latent model.

No later stage is automatically required. Each is gated by evidence.

## 7. Adaption capability boundary

Connected Adaption API verified on 2026-10-31 exposes:
- Model registry and model/hyperparameter recommendations.
- Dataset invention, augmentation, and adaptation.
- Dataset status, columns, export links, and quality evaluations.
- AutoScientist instruction/SFT and alignment/DPO runs.
- LoRA training on registered models.
- Dataset inspection/visualization through the application.
- An Inference Stacks / self-improving-model application surface, which is a separate inference-time research track.

The connected AutoScientist API does not expose:
- Custom model graphs or arbitrary architecture definitions.
- Custom JEPA/latent-state auxiliary losses.
- User-defined environment-grounded RL reward functions/rollouts.
- Full pretraining of an arbitrary new architecture.

Therefore, Adaption is the right platform for data work, supported backbone screening/fine-tuning, SFT/DPO baselines, and inference-stack experiments. It is not sufficient by itself for the long-term custom architecture. GBA/PyTorch and an environment runner are needed for that.

## 8. Dated execution programme

Dates are planning windows set on 2026-10-31, not promises of completion. Advancement is by evidence gate, not by calendar.

| Window | Phase | Deliverable | Advance only when |
|---|---|---|---|
| 31 Oct–2 Nov 2026 | Specification freeze | DHI-v1 rubric, tool manifest schema, task-state schema, model candidates frozen. | Scoring and task contracts are executable or independently checkable. |
| 2–6 Nov | Environment harness | Deterministic repository/terminal tool environment, real action logs, state diffs, postcondition tests. | Every logged transition can be replayed/verified. |
| 6–9 Nov | Diagnostic benchmark | Pilot task set covering no-tool, discover-tool, tool-noise, multi-tool, long-horizon and recovery cases. | Held-out split and contamination controls frozen. |
| 9–12 Nov | Base model screening | Qwen3.6-35B-A3B vs GPT-OSS-20B; Gemma 4 31B if multimodal UI is in scope. | Same harness, tasks, budget, and scorecard. |
| 12–16 Nov | Trajectory pilot | Small batch of genuinely executed trajectories, reviewed for provenance, semantic alignment, and outcome fidelity. | No fabricated tool outcomes; coverage and quality gates pass. |
| 16–21 Nov | Adaption SFT estimate/run | One selected backbone, one controlled agentic SFT run. | Adaption accepts the actual schema; estimate is approved; baseline frozen. |
| 21–26 Nov | Predictive/closure ablation | Compare ordinary agentic SFT against forecast- and closure-supervised variant. | Matched data/compute and independent task outcomes. |
| After 26 Nov | DPO/RL/custom latent core | Add only the method justified by the diagnostic failure and previous positive evidence. | DPO pair quality/minimum verified; RL harness validated; latent loss implemented and tested separately. |

If a phase takes longer, the date moves; evidence requirements do not.

## 9. Current decision

- DHI-v0 remains archived and intact.
- DHI-v1 becomes the active broader model-development track.
- Qwen3.6-35B-A3B is the first Adaption candidate.
- GPT-OSS-20B is the required tool-use challenger.
- No further generic SFT/DPO variation on old datasets is authorized by this plan.
- No new Adaption credits should be spent until the deterministic harness, data contract, frozen rubric, base screening, and estimate are ready.
- GBA will own custom predictive-state and architecture experiments; DHI owns model/data/evaluation programme records.

## 10. Success definition

The immediate success is not a perfect universal model. It is a reproducible model-level capability gain that survives:
- held-out tasks and environments;
- unseen tool names and schemas;
- decoy, unavailable, broken, and irrelevant tools;
- no-tool-needed cases;
- multi-step and long-horizon workflows;
- state-based final verification;
- cost/latency matching;
- independent re-scoring.

A 100/100 score on a frozen, independently audited DHI challenge suite is the stretch objective. It cannot be represented as perfect real-world intelligence. Safety, authorization, and truthful completion are hard gates that cannot be traded for average score.


## 11. Implementation update — 2026-10-31

### Delivered: deterministic tool environment v0.1

The first engineering dependency is now implemented in `DHI_v1/environment/`:

- Dynamic task-level visible tool subset plus an always-available read-only `catalog.search` meta-tool.
- File workspace tools: list, read, write, append, and text search.
- Action-intent event recorded before execution and separate execution event with real result/error.
- SHA-256 file snapshots and actual state deltas.
- Pre-action predicted changed/unchanged path comparison.
- Required postconditions and protected-path verification for task closure.
- Tool argument schema checks, task allowlists, path-traversal and symlink rejection, bounded files/snapshots, and atomic writes.
- JSONL trace contract and JSON Schema.
- Deterministic hand-scripted smoke pilot.

### Verification performed

- 42 tests passed locally on 2026-10-31.
- Python compileall passed.
- Generated trace events passed JSON Schema validation.
- Smoke pilot produced 13 events, verified its README postcondition, and preserved source/configuration protected paths.
- GitHub Actions workflow added to run the tests on future changes.

### Interpretation boundary

This proves only that the deterministic harness and trace contract behave as tested. It does **not** prove that a language model can discover tools, plan tasks, or perform agentic work. The tool catalogue search is a lexical fixture and the smoke pilot is scripted, not model-generated. The environment is not an OS/container security sandbox.

### Next engineering gate

Add isolated workspace reset/materialization from a pinned fixture (materialization is now implemented), structured state predicates, and expand the 12-case pilot into a validated multi-task benchmark with no-tool cases, hidden-tool discovery, decoy/unavailable tools, broken-call recovery, changed constraints, and false-closure traps. The initial test suite now includes regressions for missing protected paths and reused trace files. Then connect untouched candidate models to the same harness for base screening. Do not start training-data generation or spend Adaption credits before that base screen and trajectory-quality review.


### Added: pinned fixture and diagnostic pilot — 2026-10-31

- Added a SHA-256-manifested three-file repository fixture.
- Added safe fixture materialization that refuses to overwrite non-empty destinations and verifies copied hashes.
- Added validation for path traversal, unexpected files, symlink directories, and source/destination nesting; generated Python/cache/vendor directories are ignored.
- Added a hand-authored 12-case diagnostic pilot: seven cases target the current file workspace, while five explicitly require future runtime integrations.
- The pilot is not frozen, not a complete 120-task base-screen suite, and not training data.
- Local suite now passes 26 tests, including a repeat run after compileall.


### Added: model-to-environment runner — 2026-10-31

- Added an OpenAI-compatible chat-completions adapter and bounded model/tool loop.
- The model sees only currently visible function schemas. Catalogue discovery promotes tools into the live inventory for the next turn; same-response calls cannot use a schema that was not offered at the start of that turn.
- Function schemas include tool descriptions, permission scope, side effects, preconditions, cost class, and reversibility where supplied by the environment manifest.
- Optional structured action-effect forecasts and subgoal labels are captured; the environment verifies forecasts against actual file deltas.
- The runner never equates a model's final sentence with task success. Closure is computed from environment postconditions and protected-path hashes.
- Added five fake-client integration tests, including hidden-tool recovery, same-turn schema-snapshot rejection, false-completion rejection, turn-budget stopping, and effect-forecast scoring.
- Local suite: 34 tests passed; compileall passed; scripted smoke produced 13 events with zero JSON Schema errors.

### Inference integration boundary

The runner is an endpoint adapter, not evidence that a model has been connected. The connected Adaption API currently exposes dataset/training calls but no model inference endpoint. A real OpenAI-compatible serving endpoint must be configured before base-model screening. No new training dataset or AutoScientist training run has been started for DHI-v1.


### Added: executable pilot evaluator and controlled failure case — 2026-10-31

- The 12-case seed suite now has seven executable file-workspace cases and five explicitly unsupported runtime cases.
- Added observable case grading: environment closure, final-answer predicates, required tool usage, discovery events, changed-path limits, controlled error recovery, and protected path preservation.
- Added one deterministic transient search-tool failure on attempt 1; a model must recover through a subsequent successful action. Fault schedule and injected failure are part of the trace.
- Added a command to run the seven supported cases against an OpenAI-compatible served model and write a JSON report plus per-case traces. The result is a development pilot pass rate, not the weighted 100-point DHI grade.
- Local suite: 42 tests passed; compileall passed; scripted smoke remains 13 schema-valid events.
- The connected Adaption API still has no model inference operation; no model base-screen result exists, and no training run has been launched.
