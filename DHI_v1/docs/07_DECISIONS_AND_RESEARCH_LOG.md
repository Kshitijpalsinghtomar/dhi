# DHI-v1 Decisions and Research Log

**Created:** 2026-10-31  
**Status:** Active decision record. Append new decisions; do not rewrite history without a correction note.

## 2026-10-31 — Start DHI-v1 as a broader model-development programme

### Decision
Preserve DHI-v0 and establish DHI-v1 as a separate active programme targeting a general-purpose, tool-aware, long-horizon predictive agentic model.

### Reason
The user's latest requirement is broader than the previous compact DHI-v0 reasoning/Indic experiment. It includes tool ecosystem awareness, app/plugin discovery, appropriate tool choice, multi-loop planning, long-horizon execution, action-effect prediction, adaptation to failure, continuity, and verified completion.

### Consequence
DHI-v0's historical methodology and constraints remain intact. DHI-v1 has its own master plan, rubric, model selection, methods, benchmark, and data contract. Do not overwrite v0's historical next-step documents.

## 2026-10-31 — Choose first model candidates

### Decision
- Primary Adaption candidate: Qwen/Qwen3.6-35B-A3B.
- Mandatory tool-use challenger: openai/gpt-oss-20b.
- Multimodal challenger: google/gemma-4-31B-it.

### Evidence
Adaption's connected model registry on 2026-10-31 lists reasoning support and SFT/DPO for these models with LoRA. The registry lists Gemma 4 31B with LoRA/full training. Qwen3.6 has 262K context and multimodal metadata; public Qwen materials describe 35B total / approximately 3B active and agentic-coding positioning. OpenAI's official GPT-OSS model description documents function calling, web/Python tools, structured output, and configurable reasoning effort. Google's Gemma 4 model card documents multimodal input, configurable thinking, function calling, 256K context for 31B, and multilingual support.

### Boundary
This is a candidate choice, not a measured ranking. Base screening on the same 120-task diagnostic set must precede training. Re-query the registry and recommender at run time.

## 2026-10-31 — Add a tool-ecology awareness capability

### Decision
DHI must learn to identify missing capabilities and discover relevant tools from a dynamic catalogue. It must evaluate tool affordances, schemas, permissions, freshness, reliability, cost, and side effects. It must also know when no tool is necessary.

### Reason
The user observed that agents often remain within a narrow preloaded set and do not actively discover apps/connectors even when a task would benefit from them.

### Boundary
The catalogue and callable tools are runtime infrastructure. The learned model capability is recognizing the need, searching, evaluating descriptions/schemas, selecting, sequencing, and verifying. A static embedded tool list is not sufficient.

## 2026-10-31 — Add multi-loop and long-horizon capability

### Decision
DHI is evaluated on nested strategic, planning/execution, and verification/recovery loops. The loops are adaptive rather than fixed-depth chain-of-thought generation.

### Reason
One-pass response generation fails to represent long tasks where actions change state, new evidence appears, dependencies break, and work must continue across sessions.

### Boundary
A durable task-state store can preserve state, but the model must learn what to preserve, how to update it, and when to replan.

## 2026-10-31 — Choose Adaption-backed first training route

### Decision
First compare untouched models; then build a deterministic sandbox and verified tool trajectories; then run one SFT experiment on the selected model. Add forecast/closure supervision as a controlled ablation. Consider DPO only after good preference pairs; custom RL/JEPA/latent work requires external code.

### Adaption evidence
The connected AutoScientist API supports registered-model SFT/instruction and DPO/alignment with LoRA. It does not expose custom architecture graphs, arbitrary latent losses, user-defined RL rollouts/rewards, or new foundation-model pretraining.

### Consequence
No generic SFT/DPO rerun on old DHI datasets. No new Adaption credits spent until the benchmark, harness, data contract, base-model screen, and cost estimate are ready.

## 2026-10-31 — Freeze a capability rubric and evaluation gates

### Decision
Use the weighted 100-point rubric in 01_CAPABILITY_RUBRIC_AND_SCORECARD.md plus non-compensable safety, truthfulness, closure, provenance, and evaluation-integrity gates.

### Boundary
A perfect 100 score is a stretch goal on one frozen, audited challenge set. It cannot be claimed as universal real-world perfection.

## 2026-10-31 — Record relevant prior art

The following work must be reviewed before claiming novelty:
- Agent Planning Benchmark, arXiv:2606.04874 (2026-06-05; Findings of EMNLP 2026 listing): planning diagnostics with 4,209 cases, 22 domains, extra/broken tools, and unsolvable tasks.
- Qwen-AgentWorld, arXiv:2606.24597 (2026-06-23): language world models for general agents.
- ANTE, arXiv:2610.15368 (2026-10-11): pre-action outcome prediction and execution verification for coding agents.
- V-JEPA 2, arXiv:2506.09985: latent predictive world modelling with action-conditioned planning.
- τ-bench, ICLR 2025: stateful tool-agent-user interaction and pass^k.
- OSWorld, NeurIPS 2024: multimodal computer-use benchmark.
- BFCL v4: function calling and agentic tool evaluation; use cautiously because a 2026-09-10 Epoch AI audit reported potential defects in 24 of 50 sampled tasks.
- SWE-bench Verified: do not use as sole coding benchmark due the 2026-02-23 contamination warning. SWE-bench Pro also requires item-quality checks; OpenAI's 2026-07-08 audit reported broken tasks in its sample.

## Historical Adaption/DHI context retained

- Earlier Qwen3.5-4B SFT and DPO runs on older/invented datasets produced weak or mixed results; the latest 12,116-preference DPO run recorded a 0.4609 AutoScientist win rate. These are run-specific metrics, not a DHI-v1 benchmark.
- The 1,200-row invented Core v2 AutoScientist run recorded 0.1229. The UI screenshot showed base SFT win rate 58 versus adapted 42 on the displayed measure.
- The 10K recursive augmentation's Grade A evaluation was inherited from the source dataset. Adaption support explained recursive augmentation similarity, missing original prompt fields for invented rows, and that grading was being fixed to re-evaluate augmentations.
- Do not recycle these datasets as ground-truth tool-execution traces.

## Current next actions

1. Implement the deterministic repository/terminal environment and real action/state trace contract.
2. Freeze the 120-task base-screen diagnostic suite and hidden split.
3. Run Qwen3.6-35B-A3B and GPT-OSS-20B under identical conditions; add Gemma 4 if visual UI is in scope.
4. Inspect failure cases using the 100-point rubric.
5. Produce a small verified execution-trajectory pilot.
6. Estimate the actual Adaption SFT job for Qwen3.6 using the real dataset columns, then launch only if the estimate and data-quality gate pass.
7. Compare ordinary SFT with predictive/closure supervision.
8. Advance to DPO, RL, or latent architecture only when the method's entry conditions are met.

## Sources and dated references

- Agent Planning Benchmark: https://arxiv.org/abs/2606.04874
- Qwen-AgentWorld: https://arxiv.org/abs/2606.24597
- ANTE: https://arxiv.org/abs/2610.15368
- V-JEPA 2: https://arxiv.org/abs/2506.09985
- τ-bench: https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b126cc38b8638e07bef37e7b2bb72bf-Abstract-Conference.html
- OSWorld: https://proceedings.neurips.cc/paper_files/paper/2024/hash/5d413e48f84dc61244b6be550f1cd8f5-Abstract-Datasets_and_Benchmarks_Track.html
- BFCL: https://gorilla.cs.berkeley.edu/leaderboard
- BFCL audit: https://epoch.ai/benchmarks/berkeley-function-calling-leaderboard/review
- SWE-bench Verified contamination notice: https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/
- SWE-bench Pro task-quality audit: https://openai.com/index/separating-signal-from-noise-coding-evaluations/
- Qwen3.6 model card: https://huggingface.co/Qwen/Qwen3.6-35B-A3B
- GPT-OSS-20B official model details: https://developers.openai.com/api/docs/models/gpt-oss-20b
- Gemma 4 model card: https://ai.google.dev/gemma/docs/core/model_card_4


## 2026-10-31 — First deterministic DHI-v1 environment prototype

### Delivered
Added `DHI_v1/environment/` with a deterministic file-workspace environment, six tool IDs (including catalogue discovery), append-only JSONL trace events, SHA-256 snapshots/deltas, predicted-vs-actual file-change comparison, explicit postconditions, protected-path checks, tool schema validation, task allowlists, path/symlink protections, and a JSON Schema.

### Verification
- 15 unit/integration tests passed locally.
- Python compileall passed.
- A real scripted smoke execution generated 13 events and passed the JSON Schema validator.
- The smoke task's README postcondition passed and both protected files remained unchanged.
- GitHub Actions CI was added for Python 3.11.

### Boundary
The pilot was scripted to test the environment. It was not produced by a language model, is not evidence of agent capability, and must not enter the training set. Catalogue discovery uses a small lexical fixture; it does not yet search a live app/plugin marketplace. The harness has no arbitrary shell execution and is not an OS/container sandbox.

### Next decision
Build a pinned reset/replay fixture and diagnostic tasks, then connect untouched base models for identical benchmark screening. Do not launch Adaption SFT/DPO on this work until model screening, trajectory quality, and a current cost estimate pass.


## 2026-10-31 — Trace and protected-file regression hardening

- Protected paths must now exist as regular files before a task starts; nonexistent paths cannot pass through a None == None hash comparison.
- Existing trace files are rejected at environment construction to prevent separate trajectories from silently mixing in one JSONL file.
- Added two regression tests for these conditions.
- Local suite: 17 passed. The fresh scripted pilot generated 13 events; all events validated against the checked-in JSON Schema, the predicted file delta matched the observed delta, and the final goal postcondition passed.
- The pilot remains scripted and is not training data.


## 2026-10-31 — Pinned fixture and diagnostic pilot added

- Added a three-file repository fixture with a versioned SHA-256 manifest.
- Added fixture validation and safe materialization into a new/empty workspace; it does not delete existing user files.
- Added exact inventory/hash checks, traversal rejection, symlink checks, and generated-cache/vendor directory exclusions.
- Added a 12-case hand-authored pilot suite. Seven cases match the current file-workspace environment; five are explicitly marked unsupported until live tool/app registry and cross-session runtime adapters exist.
- Local suite: 26 tests pass, including compileall-cache regression. No model has executed these tasks; the case specs and scripted smoke pilot are not training trajectories.
- Next: implement a task-case runner and structured action/decision outcomes, then connect a model inference endpoint for identical base screening. The current connected Adaption API does not expose model inference; this remains a deployment/inference-stack integration gate.


## 2026-10-31 — Model runner and per-turn tool-schema control

- Added `agent_runner.py`: bounded OpenAI-compatible chat-completions loop, model function schemas built from the current visible inventory, tool output handoff, and environment-backed closure.
- Function names are mapped to internal tool IDs. Only visible schemas are sent; hidden tools are rejected until catalogue discovery. A tool discovered during one model response becomes available on the next turn, not retroactively within the same response.
- Tool metadata (permission, side effects, preconditions, cost class, reversibility) is placed in each offered schema where available.
- Optional pre-action effect forecasts are passed through `__dhi_expected_effects`; these are removed before actual tool argument validation and compared with observed file deltas.
- Added an endpoint-backed example. It requires user-configured `DHI_MODEL_BASE_URL`, `DHI_MODEL_API_KEY`, and `DHI_MODEL_NAME`; no key is stored in the repository.
- Added five integration tests. Local environment suite: 34 passed; compileall passed; scripted smoke generated 13 schema-valid events.
- No base model has been connected because the current connected Adaption API does not expose inference. No v1 training run has been launched.

## CI status note — 2026-10-31

GitHub Actions runs triggered by the earlier push workflow failed before job execution: jobs reported runner_id=0, empty runner_name, and no steps. This is a runner-allocation/account configuration issue, not a reported test assertion failure. Local tests are passing. The workflow is changed to pull-request and manual dispatch triggers to avoid generating a failed run for every individual file commit; a functioning GitHub runner is still required for hosted CI.


## 2026-10-31 — Executable pilot grading and transient failure injection

- Added `DHI_v1/benchmark/runner.py` to execute only the seven supported file-workspace cases and score observable criteria.
- Added `benchmark/run_pilot_benchmark.py` to run the pilot against an OpenAI-compatible served model and write JSON/per-case traces.
- Added task-level deterministic fault injection: exact tool ID, attempt number, and error message. The schedule is recorded at task start, injected outcome at action execution; the next tool attempt may recover.
- Updated case 006 to test a transient search failure and subsequent recovery. Cases 005 and 007 now have explicit fixture variant/postconditions.
- Added evaluator checks for answer content, required tool calls, required discoveries, no-op/changed-path constraints, and successful recovery after a failed tool.
- Local tests: 42 passed; compileall passed. The model benchmark has not run because there is no configured inference endpoint.
