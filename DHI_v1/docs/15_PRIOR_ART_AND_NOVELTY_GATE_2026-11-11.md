# DHI-v1 Prior-Art and Novelty Gate — 2026-11-11

**Programme:** DHI-v1 / ORBIT only  
**Status:** prior-art boundary; no distinct new DHI method is accepted. Active programme is empirical DHI-v1 model development, not continued novelty hunting.  
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
| **SafeMCP**, Wang et al., ACL 2026, 2026.acl-long.522 / arXiv:2606.01991 | A learned, agent-agnostic server-side defence predicts next states, predicts future unsafe actions/states, and proactively prunes the state-specific effective tool set before the agent acts; it combines safety and utility in a Stackelberg formulation, then adds immediate intervention. Its own method trains next-state prediction + unsafe-step prediction, SFT, then RL with dual verifiable rewards. | Predictive look-ahead over tool acquisition, action-set power, state transitions, and safety/utility trade-offs is already direct prior art. DHI cannot claim predictive acquisition or future action-set reasoning alone. A possible distinction is that SafeMCP is an external safety leader/filter while the underlying task agent remains the utility-maximizing follower—but the paper must be compared in full before treating that distinction as a gap. |
| **MCP-Zero**, Fei et al., arXiv:2506.01056 (2025) | Active tool request: the model identifies capability gaps, asks for tools on demand, routes requests to servers/tools, and iteratively extends cross-domain toolchains. | Active tool discovery, capability-gap requests, and iterative toolchain assembly are not new. |
| **AutoTool**, Zou et al., ICML 2026, PMLR 306 | SFT/RL-based dynamic multi-step tool selection and generalization to previously unseen tools in evolving tool inventories. | Dynamic selection, multi-step retrieval/selection, and unseen-tool generalization are not new. |
| **AutoTool: Dynamic Tool Selection and Integration for Agentic Reasoning**, Zou et al., arXiv:2512.13278v2 / ICML 2026 | Dual-phase SFT/RL trajectory stabilization plus Plackett–Luce ranking refinement of per-step tool selection; 200k-scale training data across 1,000+ tools and 100+ tasks; claims transfer to evolving/unseen toolsets. | Learned per-step dynamic tool selection, multi-step tool composition, embedding-grounded unseen-tool selection, and trajectory-level tool-choice refinement are already direct prior art. |
| **Scores Are Not Decisions: Cost-Aware Stopping for Tool Acquisition in LLM Agents (CAM-DF)**, Feng et al., arXiv:2607.27083 (2026) | Learns regret-weighted stop/continue decisions over ranked tool prefixes under task sufficiency and heterogeneous acquisition costs. Evaluates 1,343 tasks across five tool-use domains; live Retail exposure fell 37% with comparable observed success. The paper explicitly scopes this to one-turn pre-execution prefix acquisition and does not update decisions after tool outputs. | Cost-aware tool acquisition, learned acquisition stopping, and reducing exposed tools while preserving task success are already covered. The remaining scope distinction is online output-adaptive multi-round control, which must be compared with iterative retrieval/discovery work—not claimed novel by itself. |
| **Utility-Guided Agent Orchestration for Efficient LLM Tool Use**, Liu et al., arXiv:2603.19896 (2026) | Explicit action policy chooses among respond, retrieve, tool call, verify, and stop using estimated gain, step cost, uncertainty and redundancy. The paper states it is a heuristic/control framework, not a learned RL policy. | Utility-guided orchestration actions and gain/cost/uncertainty/redundancy control are not new at the systems level. A learned-policy extension requires matched evidence, not just a new utility formula. |
| **Beyond Single-Shot: Multi-step Tool Retrieval via Query Planning (ToolQP)**, Fang & Glass, Findings of ACL 2026 | Iteratively decomposes tasks into subqueries and retrieves tools for each subtask; trained with synthetic query trajectories and RL with verifiable rewards; evaluates zero-shot transfer and downstream execution. | Multi-round query-planned tool retrieval, decomposition-driven discovery, and RL-trained retrieval queries are already prior art. |
| **Plan or Retrieve First? A Scale Study of Tool Discovery Architectures**, Zhang et al., EMNLP 2026 Industry Track | Compares Retrieve-then-Plan with Plan-then-Retrieve on 46,984 ToolBench endpoints; finds a task-complexity-dependent crossover, and measures extra discovery-call cost and stub hallucination. | Planning before retrieval, abstract tool stubs, and complexity-adaptive retrieval are already studied. |
| **Completeness and Cost of Retrieval Structures for Multi-Tool Requests in LLM Agents**, Zhang, arXiv:2610.41905 (2026 preprint) | Compares six retrieval structures on 345 AppWorld queries and 103 MCP-Bench tasks over 257 tools; measures complete required-tool-set retrieval and retrieval-time cost. Reports major multi-tool completeness gaps and distinct prerequisite-vs-target failure modes. | Multi-tool tool-set completeness, dependency-aware retrieval, and quality/cost trade-offs are already being measured directly. DHI cannot claim those metrics or the basic problem as new. |
| **When Should Agents Build Reusable Tools?**, Xu, Wilder & Singh, SSRN working paper (2026) | Models online capability creation versus patching/reuse under uncertain task recurrence and stochastic tool quality; proposes a cost-sensitive acquisition controller and reports an API-migration benchmark. | Economic decision-making about whether to create/acquire reusable capabilities under uncertain future demand is already being explored; this is a working paper and must be verified at full-paper level before drawing detailed conclusions. |
| **ANTE**, Ge et al., arXiv:2610.15368 (2026) | Coding-agent pre-action beliefs are checked against actual execution; feedback provides per-action learning signals and supports test-time action optimization. | Pre-action outcome prediction and execution-verified belief learning are not new. |
| **Reinforcement World Model Learning (RWML)**, Yu et al., arXiv:2602.05842 (2026) | Self-supervised action-conditioned next-state world-model learning from the target policy's own real environment rollouts, using sim-to-real embedding-gap rewards and GRPO before downstream task-success RL. Evaluated on ALFWorld and `\\tau^2` Bench. | Action-conditioned world-model training from real rollout transitions without expert or stronger-model labels is already prior art. A DHI-specific transition loss/representation must show why it is needed beyond RWML and structured state-diff scoring. |
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

## 3. What is already covered, and what DHI must now prove

### Strong prior-art coverage

| Capability | Relevant prior work | Research boundary |
|---|---|---|
| Multi-turn planning under changing tool costs/availability/preferences | **CostBench**, ACL 2026 | Cost-optimal trajectories and replanning under tool bans, removals, cost changes and preference changes are already evaluated. It is travel-domain, but directly relevant to the mechanism. |
| Dynamic selection and unseen-tool generalization | **AutoTool**, ICML 2026 | Learned per-step selection and transfer to evolving/unseen tool inventories are already proposed and evaluated. |
| Multi-round active tool discovery | **MCP-Zero**, 2025; **ToolQP**, Findings ACL 2026 | Explicit tool requests and retrieval-feedback-conditioned iterative query planning are already covered. |
| Complete multi-tool set retrieval | **Completeness and Cost of Retrieval Structures**, 2026; **Tool Recommendation**, 2026 | Multi-tool completeness, dependency-sensitive retrieval, large catalogs, and context/cost trade-offs are already studied. |
| Cost-aware acquisition/stopping | **CAM-DF**, 2026 | One-shot pre-execution ranked-prefix stopping under heterogeneous acquisition cost is covered. |
| Tool-use budget allocation | **BATS/CATS**, COLM 2026 | Token/tool-call budget tracking and adaptive allocation between sequential and parallel search are covered. |
| MCP environment simulation / learned world models | **Qwen-AgentWorld**, 2026 | A trained world model simulates multiple domains and MCP state; same-model next-state prediction is evaluated as an agent warm-up. |
| Predictive action effects and feedback | **ANTE**, 2026; **RWML**, 2026 | Pre-action outcome beliefs checked against execution and action-conditioned world-model learning from real rollouts are already being studied. |
| Predictive safety and tool-set filtering | **SafeMCP**, ACL 2026 | World-model look-ahead to constrain tool acquisition/action-set expansion is already covered. |
| Tool catalogue/schema drift | **ToolDriftBench/ToolDriftGuard**, 2026 | Drift detection and stale catalogue/index repair are already covered. |
| Affordance-based tool repurposing | **CreativityBench**, 2026; **MM-CreativityBench**, 2026 | Grounded physical-object affordance discovery and unconventional tool repurposing are already evaluated. These are not software-API benchmarks, but DHI cannot claim affordance reasoning or repurposing generically as new. |
| Goal completion in long horizons | **Agent Planning Benchmark**, **Tool Decathlon**, **CostBench**, and other interactive-agent evaluations | Long-horizon execution, broken tools, infeasibility, replanning and closure are active benchmark areas. |

### Important distinctions and caveats

- CostBench directly evaluates multi-turn adaptation to four disruption types: tool bans and preference changes (explicit), plus cost changes and composite-tool removal (implicit). It reports cost gap, path deviation, exact trajectory match, task completion and invalid tool use. This invalidates the previous claim that output-adaptive cost/lifecycle decisions were an unexplored DHI gap.
- CAM-DF's paper explicitly limits its formulation to one-turn pre-execution ranked-prefix acquisition and does not update acquisition after tool outputs. That distinction is real, but MCP-Zero, ToolQP and CostBench cover iterative retrieval or replanning in adjacent ways. It is not enough to claim a DHI contribution by itself.
- Tool Recommendation is a production gateway/system with three meta-tools over a large catalogue; its results do not establish that the underlying model learned a new policy. Distinguish gateway capability from learned-model capability.
- CreativityBench focuses on physical object parts/attributes and household affordances; it is adjacent, not equivalent to software/API affordance reasoning.
- The CostBench GitHub repository exposed no SPDX license metadata and no license file in its repository tree during this review. Do not vendor, fork, or adapt its code unless the authors add a clear license or grant permission. Its paper may still be cited and used to guide an independent protocol.
- The reviewed literature is broad but not exhaustive. These boundaries are sufficient to reject the current lifecycle/acquisition novelty candidate; they are not a claim that every possible DHI research question has been solved.

### Decision: stop novelty hunting; execute the DHI model-development programme

No distinct new method is accepted from the current tool-acquisition/lifecycle thread. Do not continue narrowing that idea in search of novelty.

DHI-v1 remains a model-development research programme. Its central empirical question is whether a learned model trained from **real, independently verified tool-execution trajectories** can improve general tool-aware, long-horizon task execution over untouched base models, and which supervision components actually cause any improvement.

That is not a claim that SFT, action-effect prediction, world modelling, tool discovery, or goal closure are individually novel. They are established methods to reproduce and ablate within DHI's intended model. DHI's claims must be based on measured capability gains, held-out transfer, and safety/closure gates—not on a renamed architecture or a new benchmark wrapper.

## 4. Active DHI-v1 research sequence

Do the work in this order. Each study changes one factor and uses the same task splits, base weights and resource limits where applicable.

### Study 0 — Untouched base-model capability screen

**Question:** what do the selected base models actually fail at in DHI's own environment before any fine-tuning?

- Primary: `Qwen/Qwen3.6-35B-A3B`.
- Mandatory challenger: `openai/gpt-oss-20b`.
- Multimodal challenger: `google/gemma-4-31B-it`, only for tasks that require multimodal input.
- Use the existing DHI pilot/Stage A subset only after its task graders and exact-head harness pass. The currently materialized 30 tasks are a screening slice, not a statistically sufficient confirmatory benchmark.
- Same task instances, system instructions, tool schemas, permissions, retry policy, decoding, seeds and cost/tool-call budgets for each candidate.
- Report per-task and per-capability results: direct-answer/no-tool restraint, capability discovery, tool selection, argument validity, dependency order, effect forecast, recovery/replanning, closure, safety, latency, tokens, calls and cost.
- Do not call an unavailable candidate a model failure. Record model revision and inference route precisely.

**Exit:** frozen failure analysis and a reproducible untouched-base baseline. No training before this exit.

### Study 1 — Verified trajectory SFT

**Question:** does SFT on real, verified DHI executions improve held-out task completion and tool behavior over the untouched base?

- Capture actual model-originated action/observation sequences in the DHI environment.
- Independently compute state changes, tests and postconditions.
- Exclude scripted reference traces, task specifications, imagined tool outputs and unverifiable rows from positive trajectory data.
- Deduplicate and split by task family, tool family and schema so test structures do not leak into training.
- Run one SFT intervention; keep DPO/RL/latent objectives out of this experiment.

**Exit:** same frozen test suite shows a defensible improvement without hard-gate regressions.

### Study 2 — Prediction and closure supervision ablation

Compare matched variants from the same base and same verified trajectories:
- **A:** ordinary agentic SFT with real actions and observations.
- **B:** A plus explicit pre-action effects and independently observed post-action state deltas (ANTE-inspired).
- **C:** B plus explicit goal-closure/postcondition supervision.

The only causal difference should be the additional supervision target. Measure forecast accuracy separately from task success; a good verbal forecast is not evidence of better action choice.

### Study 3 — Generalization and robustness

Only after Studies 0–2:
- hold out tool names, schemas, tool combinations and task families;
- introduce controlled changes in availability, schema, permission and environment state;
- compare against AutoTool/MCP-Zero/ToolQP-style discovery, CAM-DF-style acquisition stopping, CostBench-style replanning and SafeMCP-style safety filtering where those baselines can be fairly reproduced;
- report safety, unauthorized actions, false closure, cost and reliability as hard/independent measures.

Do not combine several interventions and then attribute the result to a single module.

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
- **CostBench**, Liu et al., ACL 2026, 2026.acl-long.584 / arXiv:2511.02734: https://aclanthology.org/2026.acl-long.584/ and https://arxiv.org/abs/2511.02734
- **Tool Recommendation for Multi-Step Agents**, Partee et al., arXiv:2610.23707: https://arxiv.org/abs/2610.23707
- **Budget-Aware Tool-Use Enables Effective Agent Scaling (BATS/CATS)**, Liu et al., COLM 2026 / arXiv:2511.17006: https://arxiv.org/abs/2511.17006 and https://github.com/google-research/budget-aware-agent
- **CreativityBench**, Qian et al., arXiv:2605.02910: https://arxiv.org/abs/2605.02910 and https://github.com/CreativityBench/CreativityBench
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
