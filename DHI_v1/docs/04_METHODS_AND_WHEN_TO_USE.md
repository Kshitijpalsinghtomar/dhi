# DHI-v1 Methods, Dates, and When to Use Them

**Version:** 1.0  
**Date:** 2026-10-31  
**Purpose:** Choose methods because a specific observed limitation calls for them, not because a method is fashionable.

## 1. Method-selection principle

DHI-v1 is a programme, not a pile of techniques. Every method must answer a specific capability gap and have a measurement that can prove whether it helped.

Use the simplest method that can test the hypothesis. Add methods only when the prior stage has a valid baseline and a clearly identified failure mode.

## 2. Methods available or relevant to DHI

| Method | Role in DHI | When to involve it | Current platform fit |
|---|---|---|---|
| Base-model screening | Establish native model capability before changing weights. | First, before creating new training data or spending on fine-tuning. | Adaption registry and inference/app tools; run the same diagnostic harness. |
| Supervised fine-tuning (SFT) | Teach the model from real tool-use and task trajectories. | First training stage after the environment runner and trajectory data pass quality gates. | Supported by Adaption AutoScientist for registered models. |
| Continued pretraining (CPT) | Adapt broad representations to a domain/token distribution using raw or structured corpora. | Only if evidence shows a language/domain representation gap that SFT cannot address. Not the first tool-use intervention. | Not exposed as a custom CPT workflow by the connected AutoScientist API. |
| Preference optimization (DPO) | Teach preferences between better and worse plans, tool choices, recoveries, and outcomes. | After SFT or base behavior is measurable and independently checked preference pairs exist. | Supported by Adaption alignment/DPO on registered models. |
| Reinforcement learning (RL / GRPO or related) | Optimize decisions from actual environment rewards and verified task outcomes. | After a reliable sandbox, reward design, trajectory logging, and anti-reward-hacking tests exist. | User-defined environment rollouts/reward functions are not exposed in the connected Adaption API; implement outside Adaption. |
| Tool-trajectory distillation | Transfer high-quality workflow execution from stronger models/agents into DHI. | When competent teachers can produce useful candidate trajectories but every outcome can be executed and verified. | Data preparation can use Invent/Adaptive Data; execution and validation occur outside. |
| Counterfactual / contrastive training | Teach sensitivity to real changes in task constraints and invariance to irrelevant wording changes. | Alongside SFT data construction and benchmark design. | Can be represented in SFT/DPO rows; more specialized objectives require custom code. |
| Action-effect prediction | Teach the model to forecast state changes and side effects before an action. | After ordinary agentic SFT is working; compare prediction-supervised against matched baseline. | Text/structured prediction can be represented in SFT. A custom latent objective is outside current Adaption API. |
| JEPA-style latent prediction | Train internal representations to predict relevant future latent states rather than reconstruct all raw observations. | Only after a useful effect-prediction signal and a precise representation/anti-collapse design are established. | Requires custom GBA model code and a trainer with custom losses. |
| Model-based planning | Use a learned predictive model to compare action sequences before execution. | When transition predictions are sufficiently calibrated and useful over multiple steps. | Requires custom inference/training components; not a named Adaption AutoScientist recipe. |
| Inference-time adaptation / routing | Optimize how a model is used at inference, including context/runtime composition. | As a separate systems track; useful for latency, context, routing, and execution setup. | Adaption exposes an Inference Stacks application surface. Verify exactly what changes; do not claim the base weights improved unless they did. |
| Multi-agent delegation | Split independent research, coding, or data subtasks among agents. | Only when subtasks are independent, outputs are checkable, and coordination cost is justified. | Execution/runtime feature; the DHI model must learn when delegation helps, not delegate every task. |
| Memory/state persistence | Preserve project state and long-running task information. | When tasks cross context windows, sessions, or tools. | Runtime supplies durable state; model learns what to preserve, update, retrieve, and verify. It is not a substitute for reasoning. |

## 3. Exact DHI method sequence

### Stage 0 — base model and benchmark (31 Oct–12 Nov target window)

Use untouched Qwen3.6-35B-A3B and GPT-OSS-20B on the same 120-case screening set. Include Gemma 4 31B when screenshot/document interaction is required in the first build.

**Do not train yet.** Determine which model actually performs best on tool necessity, tool discovery, tool choice, multi-step execution, and closure. Validate native tool formatting and permissions first.

### Stage 1 — environment-grounded SFT (target window after base screen)

Build training examples from actual execution. Each trajectory includes the task, live tool inventory or discovery result, action plan, chosen tool, invocation, real observation, state delta, and verified postconditions.

The first SFT question:

> Does supervised learning from verified multi-tool execution trajectories improve DHI's held-out tool awareness, planning, and task completion over the untouched base model?

Avoid adding JEPA losses, RL, DPO, memory systems, and multi-agent teams at the same time.

### Stage 2 — forecast and closure ablation

Create matched training variants:
- **A:** agentic SFT, with action and observation.
- **B:** same SFT plus pre-action action-effect forecasts and actual post-action state deltas.
- **C:** B plus explicit goal-closure/postcondition labels.

Compare B and C against A on identical held-out tasks and matched data/compute. This tests whether prediction and closure supervision add value beyond ordinary tool trajectories.

Important: textual forecasts are not latent JEPA. Only call it a latent predictive model after a trainable latent state objective exists and has been evaluated.

### Stage 3 — DPO preference learning

Use DPO when there are genuine alternative trajectories for the same task:
- preferred tool versus irrelevant/unsafe tool;
- correct discovery versus unnecessary clarification;
- efficient dependency-aware plan versus redundant sequence;
- valid recovery versus repeated failed action;
- verified closure versus false completion.

The chosen/rejected labels need executable outcomes or expert review. Do not let the same generator produce both options and decide the winner without an independent verifier.

Adaption previously rejected an alignment dataset below 12,000 effective preference pairs. Re-check the current gate. Do not pad by duplicating or recursively paraphrasing examples.

### Stage 4 — environment-grounded RL

Use RL only after:
- the environment can be reset and replayed;
- tool outputs and state changes are logged;
- reward is tied to true task outcomes and constraints;
- the evaluator resists shortcuts;
- safety and side-effect constraints are hard gates;
- the policy has a stable SFT starting point.

Reward components may include task success, valid intermediate states, constraint preservation, verified closure, recoverability, and resource cost. Penalize false completion, unauthorized side effects, unsafe tool selection, and needless calls. Prevent the reward from being maximized by verbose plans or excessive tool use.

A custom environment rollout/reward loop is not exposed by the connected Adaption AutoScientist API.

### Stage 5 — latent predictive architecture

Implement in GBA after the predictive-SFT ablation provides evidence:
- state encoder;
- action-conditioned transition predictor;
- target/state representation path;
- anti-collapse and consistency objective;
- uncertainty prediction;
- goal/invariant/closure head;
- shared or decoupled policy integration.

Compare a text forecast, latent forecast, and no-forecast baseline. Do not add every head before the minimal transition objective is understood.

## 4. When to use a tool, app, or external source

The model should learn the following decisions:

| Situation | Required behavior |
|---|---|
| Stable fact within reliable model knowledge | No tool call; direct answer. |
| Fact can change after training cutoff or depends on current date/time | Use a current source/API and record its date. |
| User asks to inspect/edit a connected file/repository/account | Use the corresponding app/connector rather than guessing from general knowledge. |
| Required app capability is not present in current tools | Search the available app/plugin/connector directory if supported. |
| More than one provider may serve the same goal | Compare scope, access, reliability, freshness, cost, and side effects. |
| Data/action is high stakes | Prefer authoritative source, independent verification, and stronger confirmation. |
| User asks to perform an external write/send/delete/deploy/purchase | Check permissions/authorization and verify resulting state. |
| Tool output conflicts with trusted source or task constraints | Treat it as untrusted evidence; resolve conflict before proceeding. |
| No suitable tool or permission exists | State the limitation; do not invent successful access. |

## 5. When to use long-horizon and multi-loop planning

Use full hierarchical planning when:
- the goal requires multiple dependent changes;
- task state will evolve over time;
- multiple apps or external systems are involved;
- an intermediate failure changes later steps;
- the user expects a completed deliverable rather than advice;
- there are important postconditions or irreversible actions.

Use a shorter loop for:
- simple factual questions;
- single reversible actions;
- tasks where one direct call fully verifies completion.

Do not invoke a multi-agent plan merely because a task is long. First check whether work can be split independently and recombined reliably.

## 6. When to use multimodal input

Use image/screen/document/audio/video capability when the actual task requires that evidence. For the first software-agent experiment, text, repository state, terminal output, and test results are sufficient. Add screenshot/UI control after the tool-use core has a reliable text/API baseline. Gemma 4 and Qwen3.6 are multimodal alternatives; multimodal input support is not evidence of robust computer use.

## 7. Dated research/method references

All dates below identify the published method/work being considered, not the date it was invented or a guarantee of performance.

- **SFT and DPO:** established training methods; selected because Adaption currently exposes them. Use SFT first for verified trajectories; use DPO for real preference comparisons after quality checks.
- **τ-bench (ICLR 2025):** state-based tool-agent-user interaction and pass^k reliability. Use for domain workflows and repeated-trial reliability.
- **OSWorld (NeurIPS 2024):** real-computer environments and multimodal computer tasks. Use after DHI begins screen/UI interaction.
- **Agent Planning Benchmark / APB (arXiv:2606.04874, posted 2026-06-05; Findings of EMNLP 2026 listing):** holistic and feedback-conditioned planning, extra/broken tools, unsolvable tasks. Use for the planning diagnostic.
- **Qwen-AgentWorld (arXiv:2606.24597, 2026-06-23):** language world models for general agents. Use as close prior art before claiming a unified world-model/agent.
- **ANTE (arXiv:2610.15368, 2026-10-11):** anticipate-before-execute with verified action outcomes for coding agents. Use as very close prior art for action-effect forecasting and execution-grounded learning.
- **BFCL v4 (leaderboard updated 2026-04-12):** function calling and agentic tool evaluation. Use as an auxiliary diagnostic, not as a sole success target; a September 2026 audit reported substantial item-quality defects in a sample.
- **SWE-bench Verified:** do not use as the sole coding capability claim; OpenAI reported contamination concerns on 2026-02-23. SWE-bench Pro also needs item-quality scrutiny; OpenAI's 2026-07-08 audit reported issues in a portion of tasks.

## 8. Non-negotiable method rules

- Never generate fake environment outputs and call them execution traces.
- Do not recursively augment an already augmented seed to hit a row target.
- Separate task invention, action execution, quality checking, and packaging.
- Keep provenance and timestamps for every record.
- Do not accept inherited quality grades as fresh validation.
- Do not launch DPO or RL just because SFT is disappointing.
- Do not claim an architecture result from an inference stack.
- Do not change model, data, trainer, decoding, and benchmark simultaneously.
