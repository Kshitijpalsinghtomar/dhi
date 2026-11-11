# DHI-v1 Prior-Art and Novelty Gate — 2026-11-11

**Programme:** DHI-v1 / ORBIT only  
**Status:** preliminary research synthesis; the proposed gap is unverified  
**Authority:** this document narrows the 2026-11-11 reset in `14_RESEARCH_DIRECTION_RESET_2026-11-11.md`. For the current code and next action, read `DHI_v1/WORKSPACE.md` first.  
**Do not merge:** all work remains on `orbit/plugin-benchmark-fixture`.

## 1. Why the joint-belief framing is not enough

The earlier formulation—jointly modelling task/world state and tool-ecosystem state—was useful for defining an observation contract. It is **not sufficient to establish novelty**. The literature now contains direct examples of:
- language world models simulating MCP schemas, server configuration, hidden environment state, permissions, service availability, and injected errors;
- proactive tool requests and iterative capability acquisition;
- predictive safety look-ahead that constrains tool acquisition and action-space expansion;
- dynamic multi-step selection and generalization to unseen tools;
- explicit task-state preservation and pre-action outcome prediction.

The implementation in `DHI_v1/research/joint_state.py` and `dhi_environment_observer.py` should therefore be described as measurement infrastructure for a candidate research question, not as DHI's novel model, architecture, or contribution.

## 2. Prior-art matrix

| Work | Primary contribution demonstrated or claimed | Boundary for DHI |
|---|---|---|
| **Qwen-AgentWorld**, Zuo et al., arXiv:2606.24597 (2026) | General language world models and agentic environment simulators across seven domains. The MCP simulation setup includes tool schemas/server configuration and hidden environment details such as database contents, permission settings and service availability; its simulator can inject errors, withhold results, control returned formats and set final environment state. | MCP environment simulation, tool-schema-conditioned state, permissions, availability, and injected-error simulation are not new DHI claims. The paper is especially close to the previous broad joint-state formulation. |
| **SafeMCP**, Wang et al., ACL 2026, 2026.acl-long.522 | A server-side defence uses environment-grounded look-ahead/world-model reasoning to constrain tool acquisition and hazardous action-space expansion, with proactive filtering plus immediate intervention. It reports a dynamic-grounding, safe-initialization and RL pipeline with verifiable rewards. | Predictive reasoning over tool acquisition and its effect on action-space power/safety is already explicit prior art. DHI cannot claim predictive tool acquisition or safe action-space expansion alone. The paper's stated objective is safety regulation; whether it optimizes the task-solving policy's goal reachability and acquisition trade-offs in the way hypothesized below requires full-paper comparison. |
| **MCP-Zero**, Fei et al., arXiv:2506.01056 (2025) | Active tool request: the model identifies capability gaps, asks for tools on demand, routes requests to servers/tools, and iteratively extends cross-domain toolchains. | Active tool discovery, capability-gap requests, and iterative toolchain assembly are not new. |
| **AutoTool**, Zou et al., ICML 2026, PMLR 306 | SFT/RL-based dynamic multi-step tool selection and generalization to previously unseen tools in evolving tool inventories. | Dynamic selection, multi-step retrieval/selection, and unseen-tool generalization are not new. |
| **ANTE**, Ge et al., arXiv:2610.15368 (2026) | Coding-agent pre-action beliefs are checked against actual execution; feedback provides per-action learning signals and supports test-time action optimization. | Pre-action outcome prediction and execution-verified belief learning are not new. |
| **ToolDriftBench / ToolDriftGuard**, IEEE SmartIoT 2026 | Schema, semantic, and capability drift in MCP tool indexes, with detection and index repair/re-embedding evaluated under controlled drift. | Drift detection and stale-index repair are not new. |
| **OODA-Tool**, Guo et al., arXiv:2608.24368 (2026) | A typed Observe/Orient/Decide/Act interface for preserving task state across multi-turn tool use, separating state preservation from action realization. | Explicit typed state preservation and a closed-loop tool-use decomposition are not new. |
| **Action-Space Shaping for LLM Agents**, Liu et al., arXiv:2609.34971 (2026) | Studies how semantically equivalent tool-schema transformations change success, with large model- and schema-dependent sensitivity. | Schema variation/generalization and schema bias as an evaluation factor are not new. |
| **Agent Planning Benchmark**, Sun et al., arXiv:2606.04874 (2026) | Long-horizon and step-wise planning diagnostics, with extraneous/broken tools and unsolvable tasks/refusal. | Planning under irrelevant/broken tools and infeasibility/refusal evaluation are not new. |
| **Agent-World**, Dong et al., arXiv:2604.18292 (2026) | Real-world environment synthesis and environment-policy co-evolution for general agents. | Evolving task environments and co-evolving agent/environment training arenas are not new. |
| **The Menu Is an Execution Prior: State-Path Tool Menus for Online Agents**, EMNLP 2026 | Constructs state-path-aware tool menus that encode prerequisite/dependency order for multi-tool tasks. | Ordering tools around state paths and prerequisites is not new. |
| **Tool Primitives / HEART**, Jin et al., arXiv:2609.01736 (2026) | Tool interface primitives and a large heterogeneous catalogue used with retrieval/planning/routing/verification for multi-step execution and recovery. | General heterogeneous tool-interface abstraction and orchestration are not new. |
| **Fact-Augmented Lookahead Planning (LWM-Planner)**, AISTATS 2026, PMLR 300 | In-context world-model look-ahead over atomic facts with consistency filtering and depth-limited planning. | Look-ahead planning with an in-context world model is not new. |
| **ToolGen**, Wang et al., ICLR 2025 | Integrates tool representations into model token vocabulary and reports retrieval/task results over a large tool set. | Parameterized tool knowledge and generative tool retrieval are not new. |
| **MetaTool**, ICLR 2024 | Evaluates whether and which tools should be used. | Tool-use awareness or deciding not to call a tool is not new. |
| **The Tool Illusion**, Lou et al., COLM 2026 | Controlled study of when tools improve web agents and what side effects tool use introduces. | More tools do not automatically mean better task performance; claims need controlled comparison. |
| **API-Bank**, Li et al., arXiv:2304.08244 (2023) | Early executable benchmark for API/tool planning, retrieval, and calling. | Plan/retrieve/call benchmark structure is not a contribution by itself. |

### Systems and protocol evidence (not learned-model contributions)

The MCP security/lifecycle survey (ACM, 2026, DOI 10.1145/3796519) describes server lifecycle phases and security risks. The Agent Host Protocol exposes enable/disable/start/stop lifecycle actions and state changes. Current VS Code documentation distinguishes server trust, authentication, tool availability, and approval as separate controls. These are useful sources for defining realistic lifecycle state and intervention factors; they are not evidence that a model learns the required policy.

## 3. What is already covered, and what remains unproven

### Covered by prior work
- retrieving/selecting tools from large or changing inventories;
- actively requesting tools to fill identified capability gaps;
- simulating tool/environment state, including MCP schemas and permissions;
- predicting action outcomes before execution and verifying those beliefs afterwards;
- applying look-ahead to filter dangerous tool acquisitions;
- handling schema/catalogue drift and repairing retrieval indexes;
- typed task-state preservation, long-horizon planning, recovery and refusal.

### Potentially under-tested intersection (not a novelty claim)
A *task-solving policy* must sometimes choose a **tool-lifecycle action**—for example request a capability, enable/disable a server, reconnect a provider, request authorization, or choose not to expand access. These actions change the future callable action set. The policy should estimate how each lifecycle choice affects:
1. the task/world state and probability of eventual verified goal closure;
2. which actions/tools will become callable, discoverable, or remain blocked afterwards;
3. permission/consent and side-effect risk;
4. acquisition/activation latency, monetary/resource cost, and later reliability;
5. the value of alternative routes if the requested capability fails to appear.

A narrower candidate question is:

> **Can a task-solving policy learn to choose among capability-acquisition and tool-lifecycle actions by predicting their effects on both future goal reachability and the future callable action set, while respecting consent, safety, and acquisition cost—and can it outperform strong active-discovery and predictive-safety baselines on held-out tool ecosystems?**

This is not claimed as novel. SafeMCP is a particularly close overlap for predictive tool acquisition; MCP-Zero is close for active capability acquisition; Qwen-AgentWorld is close for modelling tool/environment states. A systematic review of SafeMCP's methods, Qwen-AgentWorld's MCP setup, MCP-Zero's acquisition loop, and any work on tool lifecycle/authorization planning is required before deciding whether any research gap remains.

## 4. Competing hypotheses

### H0 — Active discovery is sufficient
An MCP-Zero/AutoTool-style request-and-retrieve policy, followed by a strong planner, is sufficient. Predictive future-action-set modelling provides no reliable incremental gain.

### H1 — Predictive lifecycle choice improves goal closure
For tasks in which the current action set is insufficient, a policy that predicts the post-acquisition action set and task reachability will improve independently verified goal closure over active retrieval/request alone, under the same base model and tool budget.

### H2 — Predictive lifecycle choice improves safe capability use
The policy will reduce unnecessary acquisitions, unauthorized attempts and false claims of capability availability, while retaining success on feasible tasks. This must be compared directly with SafeMCP-style predictive safety filtering and deterministic permission enforcement; the model never replaces enforcement.

### H3 — Any benefit is conditional, not universal
Improvements occur only when a task includes a consequential lifecycle choice (acquire, enable, reconnect, seek consent, or choose a replacement path) and a multi-step dependency. There should be little or no uplift on tasks where the currently callable set already suffices.

**Falsification:** reject H1/H2 if the candidate fails to beat H0 and the best matched prior-work-inspired baseline on held-out lifecycle choices, or if gains rely on extra context, tool budget, hidden-state leakage, privileged access, or a different base model. Reject any claim of learned improvement if the intervention is only a prompt or hand-coded router change.

## 5. Required matched experiment

Use the same untouched base model, task instances, initial tool catalogue, lifecycle action set, permission/consent state, environment snapshots, decoding, and resource budget across arms.

- **B0 — Static action set:** only initially callable tools are presented.
- **B1 — Active acquisition:** model can discover/request missing tools, MCP-Zero/AutoTool-inspired; no explicit predicted future action set.
- **B2 — Predictive safety filter:** acquisition is checked with a SafeMCP-inspired risk/look-ahead constraint; clearly distinguish filter decisions from model decisions.
- **B3 — DHI candidate:** model predicts the result of each lifecycle option on task/world state and future callable action set; it chooses whether to acquire, enable, reconnect, request consent, use an alternative route, or stop. Its forecasts are captured before the lifecycle action; the environment then supplies independent actual state.

The model must not see hidden future catalogue state, expected grader outcomes, or post-action ground truth before forecasting. The lifecycle transition is enacted by the environment, not inferred from the model's own statement. Permission and consent remain deterministic external gates.

### Factors
- current capability coverage (sufficient / insufficient / ambiguous);
- acquisition path (discover, request, enable, reconnect, consent-required, no valid route);
- lifecycle result (success, delayed, failure, partial/incorrect tool addition);
- schema/capability drift after provisioning;
- alternative provider available vs unavailable;
- acquisition latency/resource cost and side-effect risk;
- task dependency depth and held-out tool/provider identity.

### Outcomes
Primary:
- independently verified task-goal closure;
- correct selection of lifecycle action or alternative/abstention;
- improvement over active-discovery and predictive-safety baselines.

Diagnostics:
- post-lifecycle action-set prediction precision/recall and calibration;
- task-reachability forecast calibration;
- unnecessary acquisition rate;
- unauthorized attempts (hard failure);
- false callable/available claims (hard failure);
- recovery after failed or partial acquisition;
- extra calls, latency, tokens and monetary cost.

Use paired task variants, disjoint train/validation/test tool families, multiple seeds when decoding is stochastic, confidence intervals, and an evaluator that does not consume model rationales. Report strata separately. Do not report an aggregate uplift without the lifecycle/no-lifecycle interaction.

## 6. Implementation/evidence status

- `DHI_v1/research/joint_state.py`: typed joint observation/diff and separate forecast scoring.
- `DHI_v1/research/dhi_environment_observer.py`: read-only adapter for real DHI environment snapshots. Catalogue `tags` are retrieval keywords and remain separate from explicit `capabilities`; `permission_scope` is a required scope and is not copied into granted `permissions`. Unknown grants remain unknown.
- The observer mechanism tests cover task/world changes, tool discovery/availability, schema drift, configured-handler disconnection, task allowlist denials, and snapshot-policy scope.
- The committed research package, including the observer semantic refinement, passed **22/22 focused tests** and `compileall` in exact-file Deepnote run `ca0c1e0e-bace-4927-ae65-5d83528eb59a` on 2026-11-11. The run executed the files fetched from the active branch; code blobs included joint-state `7f874ada919bb07c7946a08d8be683d1c3824f7b`, observer `2872b2718ee1d911575d3d0fbc6c30e1b70aaa2e`, and observer tests `65bb44df34a77297fe841468d342420bbca44dd1`. The code is deterministic measurement infrastructure, not model inference.
- These are **deterministic mechanism tests only**. They do not show that a model predicts lifecycle effects, selects the right lifecycle action, generalizes to held-out tools, or closes goals.
- No model inference, model-generated trajectory, adjudicated training dataset, capability score, or DHI training checkpoint exists. All model-run flags remain false. Do not switch providers/candidates or start inference/training without explicit user authorization and an approved resource route.

## 7. Research stop conditions

Stop pursuing this candidate as a distinct contribution if full-paper review shows that an existing work already trains a task-solving policy to optimize future task reachability under predicted tool-lifecycle/action-set transitions with matched controlled baselines. In that case, DHI must either:
1. identify a sharply narrower, testable gap supported by evidence; or
2. adopt the strongest prior method as a baseline and investigate a different DHI objective.

Do not preserve a weak novelty claim because code has already been written.

## 8. Primary references

- Qwen-AgentWorld, arXiv:2606.24597 (2026): https://arxiv.org/abs/2606.24597
- SafeMCP, Wang et al., ACL 2026, 2026.acl-long.522: https://aclanthology.org/2026.acl-long.522/
- MCP-Zero, Fei et al., arXiv:2506.01056 (2025): https://arxiv.org/abs/2506.01056
- AutoTool, Zou et al., ICML 2026 / PMLR 306: https://proceedings.mlr.press/v306/zou26p.html
- ANTE, Ge et al., arXiv:2610.15368 (2026): https://arxiv.org/abs/2610.15368
- ToolDriftBench / ToolDriftGuard, IEEE SmartIoT 2026: https://ieeexplore.ieee.org/abstract/document/11677805
- OODA-Tool, Guo et al., arXiv:2608.24368 (2026): https://arxiv.org/abs/2608.24368
- Action-Space Shaping, Liu et al., arXiv:2609.34971 (2026): https://arxiv.org/abs/2609.34971
- Agent Planning Benchmark, arXiv:2606.04874 (2026): https://arxiv.org/abs/2606.04874
- Agent-World, Dong et al., arXiv:2604.18292 (2026): https://arxiv.org/abs/2604.18292
- The Menu Is an Execution Prior, EMNLP 2026: https://aclanthology.org/2026.emnlp-main.XXX/ (verify final identifier before citing)
- Tool Primitives / HEART, arXiv:2609.01736 (2026): https://arxiv.org/abs/2609.01736
- LWM-Planner, AISTATS 2026 / PMLR 300: https://proceedings.mlr.press/v300/holt26a.html
- ToolGen, Wang et al., ICLR 2025: https://www.microsoft.com/en-us/research/publication/toolgen-unified-tool-retrieval-and-calling-via-generation/
- MetaTool, ICLR 2024: https://proceedings.iclr.cc/paper_files/paper/2024/hash/bc12914d66b41b6bfc2d3a5decdb498-Abstract-Conference.html
- The Tool Illusion, Lou et al., COLM 2026: https://www.microsoft.com/en-us/research/publication/the-tool-illusion-rethinking-tool-use-in-web-agents/
- API-Bank, Li et al., arXiv:2304.08244 (2023): https://arxiv.org/abs/2304.08244
- MCP security/lifecycle survey, ACM 2026, DOI: https://doi.org/10.1145/3796519
