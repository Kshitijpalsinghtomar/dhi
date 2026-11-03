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

1. Finish validating the deterministic environment/runner and its observable state-transition trace.
2. Materialize and independently audit Stage A (120) and Stage B (120) task partitions under the controlling [screen/diagnostic scope](../benchmark/SCREEN_AND_DIAGNOSTIC_SCOPE.md). Do not freeze tasks that the current environment cannot execute and grade.
3. Resolve comparable untouched-base inference access for Qwen3.6-35B-A3B and GPT-OSS-20B, with Gemma 4 31B included when multimodal/UI scope is executable.
4. Run Stage A on all accessible mandatory candidates under matched conditions; use Stage B as a hidden confirmation set after model/interface selection.
5. Produce a small trajectory pilot from actual environment executions, retaining raw tool responses, pre-action forecasts, actual state deltas, and independently verified postconditions.
6. Use Adaption estimates and current model/data eligibility checks before any paid dataset job or SFT launch. Do not use Invent text as a substitute for executed trajectories.
7. Compare ordinary SFT with predictive/closure supervision as a matched ablation.
8. Advance to DPO, RL, or custom latent architecture only when each method's evidence and implementation entry conditions are met.

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


## 2026-10-31 — No-tool restraint promoted into executable pilot

- Promoted case `policy-001-no-tool-needed` into the executable file-workspace suite. It asks a stable arithmetic fact while a repository is available, and requires zero tool calls, zero changed paths, and a correct answer.
- The evaluator rejects a correct answer if the model unnecessarily calls `catalog.search` or any other tool.
- The pilot now has eight supported file-workspace cases and four unsupported external-runtime cases.
- Local suite: 44 passed; compileall passed.

## 2026-10-31 — Adaption task-specification seed launched

- Dataset: `DHI-v1 Repository Agent Task Specifications — Diagnostic Candidate 120`.
- Dataset ID: `1eccaa36-bdc7-4d6e-ac8d-41b20d9425e2`.
- Type: invented instruction task specifications; 120 requested rows; code/technology domains.
- Estimate: 12 credits; 87 credits available at estimate/launch. The 200-row alternative was estimated at 20 credits and was not launched.
- Latest status check: running; row_count, processed_rows, progress, and columns all null. No evaluation/export is available yet.
- The dataset prompt prohibits invented tool outputs/results. Its intended use is candidate task specifications only. Do not convert its text into ground-truth action trajectories or training data until rows are inspected and each task is executable/gradable in the environment.


## 2026-10-31 — Adaption Responses API route and DHI adapter

### Correction
The connected Adaption MCP action list contains dataset/training operations but no response-inference action. That does not mean the Adaption platform lacks inference. Current platform documentation exposes:
- `POST /api/v1/responses` for hosted models or `stack:<slug>`.
- `GET /api/v1/models` for the account's hosted models, harnesses, and stacks; use `type=hosted` to list hosted IDs available to the API key.
- Responses function-call and function-call-output items for agent tool loops.
- Inference Stack create/manage in the app; the API can call stacks but cannot create/edit them.

### Implementation
- Added `environment/adaption_responses.py`: API client, hosted-model catalogue reader, and mappings between DHI ChatCompletionClient messages/tools and Adaption Responses items.
- Added `examples/list_adaption_models.py` so the exact callable model IDs are obtained from the user's own API key rather than guessed from the training registry.
- Updated both one-task and eight-case pilot CLIs to select `DHI_MODEL_PROVIDER=adaption` or another OpenAI-compatible endpoint.
- Disabled server-side response storage and agentic memory during these benchmark requests for isolation.
- Added seven adapter tests. Local total: 51 tests pass; compileall passes; the scripted 13-event smoke task verifies goal closure and protected paths.

### Remaining blocker
No Adaption API key is present in this execution environment, so no live `GET /api/v1/models` or `POST /api/v1/responses` call was made. The user can run `python -m DHI_v1.environment.examples.list_adaption_models` with `ADAPTION_API_KEY` set, choose a visible hosted model ID, then run the benchmark with `DHI_MODEL_PROVIDER=adaption`. A stack can be used later for a system-level experiment, not the first base-model comparison.


## 2026-10-31 — Live Adaption connector catalogue discovery

- Verified Adaption's `GET /api/v1/tools` contract: list entries include connector/server label, type, auth source, connection flow, invocation mode, approval default, required scope, availability, and unavailable reason.
- Added `AdaptionResponsesClient.list_tools_catalogue()` and `examples/list_adaption_tools.py` for read-only inventory discovery.
- Added tests for available/unavailable connector records, including missing-scope reasons; also tested the Responses function schema request and rejected incomplete Responses results.
- Local suite: 54 tests passed; compileall passed.
- This is catalogue discovery only. It does not yet execute external connectors. DHI needs explicit approval integration, actual tool-level schemas, per-action trace records, and externally verifiable closure before connector execution is included in scored tasks.


## 2026-10-31 — DHI model-driven Adaption connector discovery

- Added `catalog.adaption_search` to the DHI environment as a read-only meta-tool exposed only when an Adaption Responses client is configured.
- The model decides whether to search the Adaption host connector catalogue. The search returns real account-specific metadata: connector label/name/description, availability and unavailability reason, auth source, connection method, hosted-proxy/remote-MCP mode, required scope, and default approval posture.
- The connector remains non-callable after discovery. No connector action is executed by this adapter, and task completion cannot be claimed from a catalogue record.
- Added an Adaption-specific pilot task; baseline non-Adaption runs stay at eight common tasks, Adaption runs execute those eight plus the read-only connector-discovery case. Three tasks still await live-source, external permissioned-execution and cross-session integrations.
- Added snapshot reproducibility: one live tool catalogue fetch per agent run, reused for every query/task, canonical JSON SHA-256 written in discovery events and benchmark report.
- Added regression tests for meta-tool availability, allowlist/read-only behavior, ranked connector search, end-to-end discovery, event-schema validity, false external-completion claims, provider-specific case inclusion and per-run snapshot consistency.
- Local test suite: 66 passed; compileall passed. No live Adaption API key was present, so no live inference result or connector inventory is claimed.


## 2026-10-31 — Adaption Invent 120-row task-spec candidate evaluated

### Actual platform result
- Dataset `1eccaa36-bdc7-4d6e-ac8d-41b20d9425e2` completed successfully: 120 of 120 rows processed.
- Dataset is tabular/invented. Evaluation column mapping: `enhanced_prompt -> invented_prompt`, `original_prompt -> prompt`, `enhanced_completion -> invent_completion`, `original_completion -> completion`.
- Adaption quality result: Grade B before and after; score 8.0 → 7.7 (-3.7%). Message-quality percentile 28.9; completion-quality percentile 2.7; average message score 8.62; average completion score 6.8. Evaluation row-count sample: 100.
- Decision: dataset quarantined. Do not promote as benchmark task set, SFT/DPO target, or execution ground truth. The unusually low completion percentile is a stop signal; task-spec quality is not established by successful row generation.

### Access limitation and audit tooling
- `get_dataset` and `get_dataset_evaluation` expose metadata/evaluation but not individual row content. `get_dataset_export_links` returns null because no external export was created.
- Adaption's OpenAPI spec documents `GET /api/v1/datasets/{dataset_id}/download?fileFormat=jsonl` as a processed-row stream. The connected MCP interface does not expose it.
- Added `DHI_v1/benchmark/audit_invent_dataset.py` with direct download using a key held in the user's local shell, JSONL/JSON/CSV support, prompt/completion mapping, normalized exact duplicate checks, missing/short fields, acceptance/constraint-language review, possible execution-report claim flags, coverage distributions and report/flagged-row output.
- Added nine tests; combined local suite: 75 passed; compileall passed.
- The audit is mechanical and will not verify semantic correctness, task solvability, or execution truth. It always emits `training_eligible=false`; promotion still requires human review and execution in DHI's pinned environment.
- No individual Invent rows were available to inspect during this run, and no DHI-v1 model training has been launched.


## 2026-10-31 — ORBIT Invent methodology reset

### Decision
Use **ORBIT** as the external codename for future generated task rows, IDs, and dataset names. Do not include the internal project name in generated data. Quarantine both 120-row Invent task-spec candidates. Do not train from them, promote them as benchmark cases, or launch another dataset run using the same task-spec-as-completion format.

### Evidence
- First dataset `1eccaa36-bdc7-4d6e-ac8d-41b20d9425e2`: 120/120; Grade B; 8.0 → 7.7 (-3.7%); message quality 8.62 (28.9th percentile); completion quality 6.80 (2.7th percentile); DCScore 84.43 (normalized 0.844).
- Second dataset `be05757d-2f24-45d4-8768-659268d9d18e`: 120/120; Grade C; 7.0 → 6.6 (-5.7%); message quality 8.18 (28.9th percentile); completion quality 5.03 (2.2nd percentile); DCScore 69.11 (normalized 0.691). Dataset page reports average prompt length about 81 words and completion length about 368 words.
- Both runs generated realistic user requests with long task-specification JSON as the completion. The completion was task metadata, not an answer to the user request and not an executed trajectory.
- Invent's published paper (arXiv:2610.01674 v2, 2026-10-18) describes instruction/preference generation and quality/relevance/diversity metrics. Its Limitations section explicitly states that tool-call traces and multi-step agentic trajectories are not supported yet.

### Method correction
Separate:
1. Benchmark task specifications: contracts and graders kept as metadata, created/validated separately from SFT completions.
2. Optional ORBIT single-step decision supervision: prompt contains a full tool/state manifest and user goal; completion is only the next proposed action, direct answer, discovery decision, clarification, or safe stop. This is not an executed call or full trajectory.
3. Primary SFT data: actual model-generated trajectories collected by the deterministic environment with real tool calls/results, state deltas, prediction comparisons, and independently verified postconditions.
4. DPO: later same-task/same-initial-state chosen/rejected trajectories with independently verified outcomes.

### Consequence
No new Invent credits spent for this data until a focused one-step decision specification is independently validated and its completion format is a genuine answer to the row prompt. Do not expect Invent to produce multi-step tool traces. Do not use the LLM-generated benchmark contract as SFT completion. Full method and evidence are documented in `DHI_v1/docs/08_ORBIT_DATA_GENERATION_METHOD_REVIEW.md`.

### Caveats
The two run prompts/domains differed, so their diversity scores are not a controlled ablation. The second DCScore is about 18.1% lower than the first, an observed difference only. Row-level contents have not yet been inspected; individual task semantic quality remains unassessed. The data-target mismatch is established without claiming every generated row is semantically invalid.


## 2026-10-31 — Cross-dataset Invent quality versus training-signal audit

### Purpose
Check whether Adaption's dataset-quality grade is a reliable proxy for whether AutoScientist training improves the target behavior. This is a retrospective comparison, not a controlled experiment.

### Dataset-quality observations

| Neutral label | Rows | Adaption score | Mean message quality | Mean completion quality | DCScore (normalized) |
|---|---:|---:|---:|---:|---:|
| Earlier instruction corpus | 300 | A / 9.0 | 8.50 | 9.46 | 92.68 (0.927) |
| Earlier preference corpus | 300 | A / 9.1 | 8.65 | 9.45 | 91.19 (0.912) |
| Intent/action/effort instruction corpus | 1,200 | B / 8.6 | 8.02 | 9.10 | 96.97 (0.970) |
| Task-spec candidate A | 120 | B / 7.7 | 8.62 | 6.80 | 84.43 (0.844) |
| Task-spec candidate B | 120 | C / 6.6 | 8.18 | 5.03 | 69.11 (0.691) |

Adaption quality evaluations sampled 100 rows for the reported metrics. The scores measure dataset-message/completion properties and diversity, not execution success or model capability.

### Training observations

- The 300-row instruction corpus produced AutoScientist-reported best win rates of 0.3211 when mapped from the invented prompt/completion columns and 0.3000 when mapped from the original prompt/completion columns. Both runs used Qwen3.5-4B.
- The 1,200-row instruction corpus produced an AutoScientist-reported best win rate of 0.1229 on Qwen3.5-4B.
- A separate 12,116-row combined preference corpus produced 0.4609 in a Qwen3.5-4B alignment run. This is not the same dataset as the 300-row preference corpus above.
- No AutoScientist run was found for the standalone 300-row preference corpus in the retrieved run history.
- These win rates are platform training metrics. They are not independently scored task-success rates and are not comparable across different datasets/methods without a shared evaluation protocol.

### Interpretation
1. High Invent quality scores do not, by themselves, predict a useful learned capability. The 300-row instruction corpus was rated A / 9.0 but its two training runs remained at 30.00–32.11% reported best win rate; the 1,200-row corpus was rated 8.6 but its run reported 12.29%.
2. The two 120-row task-spec attempts show a different problem: task-contract JSON was placed in the completion position, where the training format expects the answer to the prompt. Their low completion scores are consistent with that target mismatch.
3. The apparent difference between ordinary instruction/preference examples and long task-spec completions is a useful clue, not a causal finding. The datasets differ in prompt, domain mix, row count, output shape, and potentially generation configuration. The comparison does not establish that dataset length or one Invent setting caused the difference.
4. The 12,116-row preference result must remain separate: it is a different combined dataset and a different training method, not evidence that the 300-row preference pilot trained well.

### Decision
- Keep both 120-row task-spec datasets quarantined; do not use them for SFT, DPO, benchmark scoring, or execution-trace labels.
- Do not infer model progress from Invent's A/B/C grade or AutoScientist's best-win-rate field alone.
- Do not launch another generic Invent or AutoScientist run on the historic corpora.
- Preserve the ORBIT split: task contracts are benchmark metadata; an optional Invent dataset may teach only a concise single next decision; primary SFT must come from actual environment-executed trajectories; DPO must compare independently verified alternative trajectories.
- Continue to the untouched-base diagnostic only after the supported pilot, inference endpoint, and evaluation protocol are ready.

### Current implementation gate
The repository's current pilot suite is still marked development-only and contains eight executable file-workspace cases plus external-runtime cases that the file harness cannot grade. The 120-task screening suite is not frozen, and no candidate model has yet been run against the environment. The Adaption Responses adapter is implemented, but it requires the user's API key and an exact account-visible hosted model ID; no live inference was performed in this audit. Therefore no model ranking, training claim, or training authorization is added by this entry.


## 2026-10-31 — Pilot evaluator precision and write-scope hardening

### Finding
The first development pilot used substring-only answer checks in places where exact answers were required. For example, the no-tool arithmetic case accepted any final answer containing the character '4', so an incorrect answer such as '14' could satisfy that check. The hidden-search case requested a line number but graded only the file path. Two documentation-write cases protected known source/config files but did not explicitly reject every other changed path.

### Changes committed
- Added answer_regex scoring with regex validation at suite-load time.
- Added only_change_paths scoring to reject any observed changed path outside the task's explicit allowlist.
- Tightened the no-tool arithmetic case to require the entire final answer to be exactly 4, with optional surrounding whitespace.
- Tightened the hidden-search case to require both src/api.py and line 1.
- Restricted the two README-writing cases to changes in README.md only.
- Added five regression tests for exact-answer false positives, complete-answer matching, line-number evidence, unexpected file changes, and invalid regex rejection.

### Verification status
- The regex and allowed-path predicates were exercised in an isolated Python check; all eight targeted assertions passed.
- The full repository pytest suite and compileall were not run on this revision. The Hugging Face CPU-job launch was rejected with HTTP 402 before a job started; a local clone also failed because the execution environment could not resolve GitHub.
- No cloud job was started, no training run was launched, and no training credits were spent.

### Decision
Treat the grader changes as implemented but pending full-suite verification. Do not claim the benchmark is frozen or use the development-pilot score as a model-selection result. The next valid gate remains: run the regression suite in a functioning development/CI environment, then establish a working live inference endpoint and execute the same harness against the untouched base-model candidates.


## 2026-10-31 — Adaption-first inference preflight

### Live registry evidence
The connected Adaption `list_training_models` operation returned the currently registered candidates:
- `Qwen/Qwen3.6-35B-A3B`: 262,144 context; reasoning enabled; SFT/DPO; LoRA.
- `openai/gpt-oss-20b`: 131,072 context; reasoning enabled; SFT/DPO; LoRA.
- `google/gemma-4-31B-it`: 262,144 context; reasoning enabled; SFT/DPO; LoRA/full.

This only establishes training-registry support. It does not establish hosted inference access for this account/key.

### Inference access inspection
The existing adapter calls the documented authenticated endpoints `GET /api/v1/models?type=hosted` and `POST /api/v1/responses`. It requires `ADAPTION_API_KEY` at runtime. The available Adaption MCP action catalogue in this session exposes model training registry, datasets, recommendations, and AutoScientist runs, but no hosted-model listing or Responses inference action. No API key is exposed to the assistant runtime.

### Decision
Keep Adaption as the primary platform. The next action is a local, secret-safe hosted-model preflight using the existing `list_adaption_models.py`, followed by the same benchmark for each exact hosted candidate returned. Do not paste the API key into chat, do not start training, and do not treat the training registry as inference approval. No new dataset generation or training credits were used in this check.

## 2026-11-02 — Git-first incremental project state adopted

### Decision
GitHub repository `Kshitijpalsinghtomar/dhi` is the durable source of truth for all DHI-v1 / ORBIT work. Meaningful research, implementation, experiment, test, failure, and blocker updates must be recorded and committed as work progresses. Chat-only handovers are not an accepted state-management method.

### Implementation
- Added `DHI_v1/WORKSPACE.md` as the live continuation pointer. Every new session must read it first; it carries the current phase, evidence status, exact blocker, and next authorized action.
- Added `DHI_v1/docs/12_GIT_FIRST_WORKFLOW.md` defining session-start checks, incremental commits, experiment records, raw-artifact lineage, failed/interrupted-run logging, and session interruption requirements.
- Updated both repository READMEs to direct agents to the live workspace and Git-first workflow.
- Reclassified `DHI_v1/docs/11_AGENT_HANDOVER_2026-11-02.md` as a dated background snapshot. It must not compete with or replace the live workspace.
- The first documentation commits for this protocol are `650032632079cff8a1877f727ab1c7844ada6e80` (workflow) and `f670000bb7eb1fe92345dd91d9296046d1d45179` (workspace); navigation and snapshot updates follow in the same change set.

### Current state recorded
- The model-facing DHI development pilot and environment/Adaption adapters are implemented.
- The scripted reference pilot remains 8/8; it is not an LLM capability result and not training data.
- No untouched-base model screen or DHI-v1 training run is recorded.
- Inference preflight remains blocked until an exact account-visible hosted model ID and secure credentialed inference path are verified.
- The 120-vs-240 benchmark-size discrepancy remains unresolved and must be reconciled before a larger confirmatory suite is frozen.
- The quarantined Invent candidates and partially audited 300-row instruction candidate remain ineligible for training.

### Verification and limits
- Documentation-only change; no tests were run because no executable code changed.
- Repository write success must be verified by fetching the committed files and checking the resulting branch head.
- No model inference, dataset generation, training, or Adaption-credit spend occurred as part of adopting this workflow.

### Operating consequence
At each meaningful checkpoint, update the relevant experiment/code/decision record and `DHI_v1/WORKSPACE.md`, then verify the Git commit. If the session is interrupted at any point, the latest committed workspace must identify exactly what is complete, what is not, and the next authorized action.

## 2026-11-02 — INFER-001 hosted-inference preflight blocked

### Question
Can the current Adaption account expose an exact hosted model ID and run the existing DHI-v1 model-facing pilot through the Responses API without changing provider or research direction?

### Procedure
- Re-read the live workspace and applicable DHI model-selection, benchmark, and Git-first workflow documents.
- Inspected the connected Adaption MCP action catalogue and refreshed `list_training_models`.
- Inspected the existing DHI — ORBIT Research Lab Deepnote project metadata and workspace integration inventory; no secret values were read or emitted.
- Read the committed `list_adaption_models.py`, `adaption_responses.py`, and `client_from_env` implementation.

### Observations
- The Adaption training registry still lists `Qwen/Qwen3.6-35B-A3B`, `openai/gpt-oss-20b`, and `google/gemma-4-31B-it` for training methods. This is not hosted inference availability.
- The connected Adaption MCP actions do not expose `GET /api/v1/models?type=hosted` or `POST /api/v1/responses`.
- The existing Deepnote project has no attached integrations. The workspace integration inventory contains only `[Demo] Snowflake`; no environment/secret integration is available. The project file inventory contains unrelated DPAK experiment directories, so it was not used as a DHI execution environment.
- No secure Adaption API key is available to this execution context. No authenticated hosted-model request could be attempted.

### Decision
**INFER-001 remains BLOCKED.** Do not infer hosted-model availability from the training registry, guess an ID, switch providers to bypass the blocker, launch training, or generate more data.

### Evidence and artifact
- Experiment record: `DHI_v1/experiments/INFER-001/README.md`.
- Machine-readable manifest: `DHI_v1/experiments/INFER-001/manifest.json`.
- Evidence class: connected training-registry metadata plus runtime/integration metadata; no hosted inference evidence.
- No model run, training run, or Adaption credit spend occurred.

### Next authorized action
Inject `ADAPTION_API_KEY` (or `DHI_ADAPTION_API_KEY`) into a clean DHI-only secure execution environment. Then run the existing `python -m DHI_v1.environment.examples.list_adaption_models` preflight. Record the exact hosted IDs or redacted API error before launching the development pilot. Never paste the key into chat or commit it.

### Scope boundary
This is an infrastructure-access finding only. It does not change DHI's model candidates, training decisions, ORBIT data gates, or research hypothesis.

### 2026-11-02 follow-up — isolated secret-presence probe could not execute

A secret-safe probe was added at `DHI_v1/experiments/INFER-001/check_runtime_secret_presence.py`. It prints only whether `ADAPTION_API_KEY` or `DHI_ADAPTION_API_KEY` is present; it never prints values and performs no network request.

A clean Deepnote project was created (`2eb8d02b-b505-4b39-a33a-32aeda2e1cc4`) with notebook `08586f8da34c456fb544baccb69ebe3e` and probe block `7bcfdf38fd0a400e989a4d6064e1caed`. Detached read-only run creation was rejected before execution with:

`Your plan quota for parallel running projects has been exceeded. Please stop one of your running projects.`

**Interpretation:** secret presence remains unmeasured; this is not evidence that the key is absent. No secret was read or emitted, no network request was made, and no existing project was stopped. The isolated project remains available for a later retry.

**Next action:** make one Deepnote parallel-run slot available through an explicitly user-approved stop of an idle project, and configure the Adaption key as a secure environment secret in the isolated DHI project. Then execute the existing presence-only probe before any API request. Do not use the mixed DHI/DPAK project.

### Correction — 2026-11-02 wording of initial INFER-001 access finding

The earlier sentence in the INFER-001 entry saying that no secure Adaption API key was available was too strong. What was established at that point was only that no key was exposed through the connected Adaption MCP action surface or the attached Deepnote workspace integrations. The isolated runtime presence probe was later rejected before execution by the Deepnote parallel-project quota. Therefore the environment variable's presence or absence is **unverified**. The authoritative current state is the INFER-001 manifest and `DHI_v1/WORKSPACE.md`; do not interpret the earlier wording as a completed secret-presence check.

## 2026-11-02 — INFER-001 secret-presence probe completed

### Execution
- Isolated Deepnote project: `2eb8d02b-b505-4b39-a33a-32aeda2e1cc4`.
- Notebook: `08586f8da34c456fb544baccb69ebe3e`.
- Probe block: `7bcfdf38fd0a400e989a4d6064e1caed`.
- Run: `b39c478a-3268-439c-af30-d71ba9b40907`.
- Status: success; completed at `2026-11-02T16:43:11.672Z); execution 3 ms.
- Output was only presence booleans; neither variable was present. No network request was made, and no secret value was emitted.

### Result
`ADAPTION_API_KEY` and `DHI_ADAPTION_API_KEY` are both absent from the isolated project runtime. This confirms the project currently has no Adaption environment-variable secret configured. It does **not** establish whether a key exists elsewhere in the user's account.

### Secure setup path
Deepnote's documented project-secret mechanism is an Environment variables integration. It stores values encrypted, and the integration must be attached to the project. The project is isolated and ready to receive that integration. Documentation: https://deepnote.com/docs/environment-variables.

### Next action
Configure `ADAPTION_API_KEY` in a secure Environment variables integration and attach it to project `2eb8d02b-b505-4b39-a33a-32aeda2e1cc4`. Rerun the presence-only probe. When it confirms presence, run the existing authenticated hosted-model listing CLI; do not run model inference before the list call succeeds.

## 2026-11-02 — VERIFY-001 initial run dependency block

VERIFY-001 successfully fetched and checked out the exact pinned commit `c2e0dddaa6eb22d0c4722fc7fb43f2c2439c7c61`. `python -m compileall -q DHI_v1` passed (exit 0). The pytest command did not collect or execute tests because the isolated Deepnote image does not have pytest installed (`No module named pytest`). This is a runtime dependency issue, not a test failure. The exact run and output are preserved in `DHI_v1/experiments/VERIFY-001/manifest.json`. Retry with ephemeral installation of pytest and jsonschema; do not change source code for this issue.

## 2026-11-02 — VERIFY-001 retry blocked by Deepnote quota

After the initial exact checkout/compileall run, a retry cell was added to install pytest and jsonschema ephemerally and rerun the environment/benchmark tests. Deepnote rejected both detached and live-mode run creation with `Your plan quota for parallel running projects has been exceeded. Please stop one of your running projects.` before execution. No package was installed and no test was run in the retry. No existing project was stopped. The retry cell remains available in the isolated notebook. Further runtime work requires a user-approved stop of an idle project or another execution slot.

## 2026-11-02 — Benchmark scope discrepancy confirmed; freeze remains blocked

### Sources inspected
- `DHI_v1/docs/03_MODEL_SELECTION_AND_ADAPTION.md`, Section 5: six groups of 20, total 120 initial screening tasks.
- `DHI_v1/docs/05_BENCHMARK_PROTOCOL.md`, Section 3: ten strata of 24, total 240 initial diagnostic tasks.
- `DHI_v1/docs/07_DECISIONS_AND_RESEARCH_LOG.md`, current next actions: freeze the 120-task base-screen diagnostic suite.
- `DHI_v1/docs/00_MASTER_DEVELOPMENT_PLAN.md`: requires identical task sets for untouched-base screening but does not reconcile the two counts.
- The checked-in 12-case development pilot remains development-only and does not resolve either specification.

### Finding
The repository contains two incompatible definitions of the *initial* screening/diagnostic scope. No inspected controlling file states that 120 is a subset of 240, that 240 is a later expansion, or that one document supersedes the other. No existing GitHub issue matched the 120-vs-240 conflict when searched on 2026-11-02.

### Decision
**Do not freeze a confirmatory or base-screen suite yet.** Preserve both source specifications and their provenance. Do not invent a staged progression, choose a count by recency, or treat the 12-case pilot as a substitute. A future explicit decision must state the purpose/stage, selected count and strata, inclusion relationship (if any), held-out split, and the documents revised.

### Repository changes
Added an explicit unresolved-conflict warning to Sections 5 and 3 of the model-selection and benchmark-protocol documents respectively. No task cases, rubric weights, model candidates, or evaluation rules were changed.

### Consequence
This is a documentation/audit result only. No benchmark tasks were generated, no model was run, and no training or Adaption credits were used. The inference-access preflight remains the immediate blocker before any model-facing pilot.

### Follow-up workspace-quota inspection — 2026-11-02

Deepnote machine metadata was checked for all eight workspace projects. Exactly one project machine was in `running` state. No project was stopped. Both detached and live execution attempts for VERIFY-001 remain blocked by the parallel-project quota. The DHI isolated project itself is stopped after its completed read-only probe. A user must explicitly approve stopping an idle project before the assistant stops anything. This is an execution-capacity observation only; it does not change DHI research decisions.

## 2026-11-02 — INFER-001 secure runtime secret mounted

### Change and verification
- Found the newly created Deepnote Environment variables integration `ADAPTION` (type `env`, ID `999bb21e-9bfd-4071-a2bc-d26590958de7`).
- Attached it to the isolated project `DHI — Isolated Runtime Preflight` (`2eb8d02b-b505-4b39-a33a-32aeda2e1cc4`).
- Reran the committed presence-only probe in live mode: run `9e34f54b-0acf-455b-b44a-9c28173a1462`.
- Output confirmed `ADAPTION_API_KEY=true`, `DHI_ADAPTION_API_KEY=false`; no secret value was emitted and no network request was made.

### Interpretation
The API key is mounted into the isolated runtime. Its validity and hosted-model permissions are not yet established.

### Next authorized step
Run the existing `list_adaption_models.py` CLI to query the authenticated hosted-only model catalogue. Record exact returned model IDs or a redacted error. No inference or training is authorized from this presence check alone.

## 2026-11-02 — INFER-001 hosted-model catalogue retrieved

### Execution
- Used the committed CLI `python -m DHI_v1.environment.examples.list_adaption_models`.
- Pinned and verified repository revision: `ca6a2c5713f87c9c46bcc61dad87cd5273390809`.
- Deepnote run: `4bd4a7ba-edfb-4715-8ebb-0d52b95c0663`.
- Authenticated request: `GET /api/v1/models?type=hosted`.
- Status: success; 6 exact hosted model IDs returned in 0.605 seconds.

### Exact catalogue result
- `glm-5.2` — GLM 5.2.
- `qwen3.5-397b` — Qwen 3.5 397B.
- `gemma-4-26b-a4b-it` — Gemma 4 26B A4B Instruct.
- `qwen3.8-27b` — Qwen 3.8 27B.
- `deepseek-v4-flash` — DeepSeek V4 Flash.
- `gemma-4-31b-it` — Gemma 4 31B Instruct.

### Candidate availability
- Repository primary `Qwen/Qwen3.6-35B-A3B`: not present in this hosted catalogue response.
- Mandatory challenger `openai/gpt-oss-20b`: not present in this hosted catalogue response.
- Multimodal challenger `google/gemma-4-31B-it`: matching display name is present as `Gemma 4 31B Instruct`, exact hosted ID `gemma-4-31b-it`.

Do not infer that absent models can be called by their training registry IDs. Do not substitute the other four hosted models without a separate user-approved model-selection decision.

### Decision and boundary
The hosted catalogue step is complete. **Do not call inference yet.** The catalogue does not expose pricing, and the repository requires provider/cost approval before any model run. The next possible action is only the existing single-task integration pilot on exact ID `gemma-4-31b-it`, if the user authorizes possible Adaption account charges. The eight-case development pilot and a comparative model screen remain unrun.



## 2026-11-02 — ADAPTION-001 live model and data eligibility audit

### Procedure
Queried the live Adaption training registry, dataset inventory, ORBIT 300-row dataset details/evaluation, AutoScientist run history, and model-specific hyperparameter recommendations. No training, generation, augmentation, translation, localization, or adaptation launch was made.

### Observations
- The live registry continues to list Qwen/Qwen3.6-35B-A3B, openai/gpt-oss-20b, and google/gemma-4-31B-it for SFT/DPO.
- Current candidate dataset: `ORBIT Collaboration Behaviour — Instruction Pilot 300`, ID `169af31f-06e0-4a48-84ab-b84c9f9ce924`, Invent-sourced, 300 rows, processing status succeeded.
- Adaption returned dataset grade A / 9.4 on its 100-row quality-evaluation sample. This is dataset-message/completion quality metadata, not an agent capability result.
- The live workspace's triage record shows 98/300 rows partially reviewed (25 candidate, 53 revise, 20 reject); 202 remain unreviewed. No complete independent adjudication exists.
- Recommender rejected Qwen3.6-35B-A3B and Gemma 4 31B because the dataset is below 10,000 effective rows (base plus augmentation).
- Recommender returned a GPT-OSS-20B LoRA recipe for the 300-row set (1 epoch, lr 5e-5, rank 4, alpha 8, q_proj/v_proj). This is only a recipe recommendation; it does not make the data eligible or authorize a run.
- Seven historical AutoScientist runs were listed. The displayed Qwen3.5-4B DPO result of 0.4609 against 0.99 and earlier SFT results of 0.1229–0.3211 are run-specific historical metrics, not comparable DHI-v1 capability scores.

### Decision
Do not train the current 300-row invented dataset. Do not interpret its A/9.4 data grade as a model result. Do not use invented task/completion pairs as a substitute for verified execution trajectories.

Keep the model roles unchanged:
- Qwen3.6-35B-A3B: planned primary backbone.
- GPT-OSS-20B: mandatory tool-use challenger.
- Gemma 4 31B: multimodal challenger.

A single Gemma hosted-inference call cannot answer the primary-vs-challenger selection question because the previously queried hosted catalogue returned neither Qwen3.6 nor GPT-OSS. Defer that one-model integration pilot; do not treat it as the immediate research priority.

### Cost and authorization boundary
The recommender returned hyperparameters but no training price quote. The connected dataset generation/adaptation/augmentation actions expose `estimate: true`; the connected training-launch action spends credits and has no estimate field in its exposed schema. No job was launched and no credits were spent in this audit. Get a platform price/credit confirmation before any chargeable job.

### Artifact
- `DHI_v1/experiments/ADAPTION-001/README.md`
- `DHI_v1/experiments/ADAPTION-001/manifest.json`
- No model-quality or training conclusion is claimed.


## 2026-11-02 — Resolve 120-task screen and 240-task diagnostic scope

### Decision
The 120-task base-model screen is Stage A, the first half of a single 240-task ten-stratum diagnostic panel. Allocate 12 Stage A tasks and 12 distinct Stage B tasks to each of the ten strata. The complete panel therefore has 24 tasks per stratum; Stage A has 120 tasks and Stage B adds 120 held-out tasks.

This supersedes the earlier six-groups ×20 allocation as the active model-screen allocation. The earlier conflict audit remains as historical provenance; this dated decision now resolves it.

### Rationale
The ten-stratum diagnostic design separately allocates no-tool restraint, current evidence, tool discovery, decoy/tool selection, schemas/preconditions, dependent multi-tool tasks, long horizons, recovery, action-effect prediction/closure, and safety/permissions. The previous six groups bundled multi-tool with long-horizon tasks and failure recovery with closure, while leaving prediction and safety/permission dimensions without their own balanced allocation. The ten-stratum screen makes these dimensions separately diagnosable without increasing the first-stage total beyond 120.

The nested split keeps the initial screening budget at 120 while preserving a held-out extension. Both stages have the same stratum composition, allowing a model choice made on Stage A to be checked on distinct Stage B task families without claiming that 120 additional duplicated prompts increased the sample size.

### Rules
- Stage A is used for initial screening and may inform model/interface selection.
- Stage B remains hidden until the model/interface choices are fixed; no tuning on Stage B.
- Stage A/B split by task family/template, repository/application, tool-schema family, dependency structure, horizon and environment state—not paraphrase or random wording.
- The existing 12-case development pilot is excluded from both.
- Report per-stage and per-stratum metrics, paired comparisons, confidence intervals, cost/latency and non-compensable hard gates.
- This freezes the relationship, strata and counts only. Task instances, tool manifests, model revisions, environment, seeds, graders, budgets and thresholds remain unfrozen.
- If a stratum cannot be executed and independently graded in the current environment, mark it as a harness gap; do not count it as a model failure.

### Artifact
- Controlling allocation: DHI_v1/benchmark/SCREEN_AND_DIAGNOSTIC_SCOPE.md.
- Model-selection protocol: Section 5 of DHI_v1/docs/03_MODEL_SELECTION_AND_ADAPTION.md.
- Diagnostic protocol: Section 3 of DHI_v1/docs/05_BENCHMARK_PROTOCOL.md.

No task instances were created, no model was run, and no Adaption credits were spent in making this scope decision.

## 2026-11-02 — Define task-record contract and audit executable stratum coverage

### Question
Can the existing DHI-v1 environment execute and independently grade the ten strata in the 240-task panel, and what task-record fields are required before any Stage A/Stage B item is materialized?

### Source audit
Inspected the live `main` revision `3640e4a86495299688b5e20e098097730743ab53`, including:
- `DHI_v1/environment/dhi_env.py` — current tool catalogue, task contract, argument validation, fault injection, path safety, state snapshots, prediction comparison, postconditions and closure.
- `DHI_v1/environment/agent_runner.py` — per-turn tool schema refresh, bounded model/tool loop, untrusted-output instruction, and endpoint error handling.
- `DHI_v1/benchmark/runner.py` and `DHI_v1/benchmark/pilot_cases.json` — supported-case selection, deterministic evaluator, eight common pilot cases, one Adaption catalogue case, and three explicitly unsupported seeds.
- `DHI_v1/environment/schemas/trajectory-event.schema.json` and `DHI_v1/docs/06_DATA_AND_TRAJECTORY_CONTRACT.md` — existing trajectory event and evidence-lineage requirements.

### Findings
1. The environment is a deterministic file-workspace harness with catalogue discovery, list/read/write/append/search tools. It does not expose browser, web, shell, database, spreadsheet, or callable external connector actions.
2. Local catalogue discovery is deterministic lexical overlap over a small registered tool list. The optional Adaption integration exposes read-only connector-catalogue metadata; it does not make discovered connectors callable.
3. Tool argument validation currently enforces required fields, disallowed extra fields, and primitive Python types. Runtime preconditions include real path/file/directory checks, UTF-8 handling, parent existence, workspace boundary/symlink checks, and file/snapshot size limits.
4. Executable postconditions currently cover file `exists`, `not_exists`, `contains`, `equals`, and `sha256`. Protected paths are checked against initial/final hashes.
5. Fault injection is deterministic by tool ID and attempt number. It supports controlled tool errors, but provider HTTP failures/timeouts terminate the model run; there is no rate-limit/backoff simulation or resumable retry protocol.
6. Effect prediction is limited to predicted changed/unchanged file paths and SHA-256 snapshot deltas. It is not structured semantic state or general side-effect prediction.
7. The runner can perform bounded same-session action chains (default 16 model turns / 48 tool calls) and records step/subgoal/plan-version metadata. It does not implement durable checkpoints or cross-session resume.
8. The runner system instruction says tool output is data, not instructions; filesystem allowlists, path protections and protected-file hashes exist. There is no full permission/consent state machine, external irreversible action execution, or cross-session memory runtime.

### Decision
- Add a versioned JSON Schema for benchmark task records and a machine-readable panel register.
- Record the 120 Stage A + 120 Stage B allocation with 12 tasks per stage per stratum.
- Keep the register's `tasks` and `task_families` arrays empty until task contracts, fixtures, graders and family independence are materialized. Do not create 240 placeholder prompts or count the existing 12-case integration pilot as panel tasks.
- Mark S01, S05 and S06 as supported only within their explicitly bounded capabilities; S03, S04, S07, S08, S09 and S10 as partial; and S02 as a harness gap.
- Do not run candidate models against unsupported/partial strata as though they were model failures. No model run or Adaption spend is authorized by this audit.

### Artifacts
- `DHI_v1/benchmark/task_manifest.schema.json`
- `DHI_v1/benchmark/task_manifest.json`
- `DHI_v1/benchmark/ENVIRONMENT_COVERAGE_MATRIX.md`
- Updated `DHI_v1/WORKSPACE.md`

### Evidence boundary
This is a source-code/harness-readiness audit. It creates no task instances, benchmark scores, model trajectories, training rows, or capability result. The full 240-task panel remains unfrozen.

## 2026-11-02 — Harden task-manifest split and validation invariants

The first task-record schema review found two panel-integrity requirements that needed to be mandatory at the record level. Updated `task_manifest.schema.json` so:
- `split_metadata` is required on every task and carries the partition, task-family fingerprint, and explicit holdout-seal state.
- Stage A IDs and partition labels must use the Stage A namespace and remain unsealed.
- Stage B IDs and partition labels must use the Stage B namespace and explicitly set `holdout_sealed=true`.
- A task may use `validation.status=validated` only when contract, environment, and grader checks are all `pass` and review status is `accepted`.
- Grader metadata must explicitly state `llm_judge_sole_source=false`.

This is schema hardening only. No task instances were added and no benchmark execution was started.

## 2026-11-03 — Begin plugin-native ORBIT benchmark authoring

### User direction
The benchmark must use the connected plugin tools. The local deterministic file-workspace harness is retained for the cases it covers, but it is no longer treated as the ceiling of the benchmark environment.

### Execution surfaces inspected
Pinned the actual connected tool descriptions and input contracts for 15 selected actions across GitHub, TinyFish, Firecrawl, Deepnote, Consensus, Scite and Wolfram in:
- `DHI_v1/benchmark/fixtures/plugin_ecology/plugin_tool_registry.json`

The task profile records strict boundaries:
- GitHub writes only to dedicated benchmark branches; no issue, source, configuration, deployment, deletion or merge actions are used.
- TinyFish is used for public current-source verification.
- Firecrawl `firecrawl_find_tools` is used for free capability discovery. The discovered `packages/package` action costs one credit and was not executed.
- Deepnote remains blocked by the previously recorded workspace project concurrency quota; no project was stopped or restarted.
- Consensus search returned its monthly free usage cap (100% used; reset 2026-12-01); no retry was attempted.
- Adaption dataset/training actions were not invoked.

### Actual plugin-backed reference work
1. Created a synthetic Northstar Workbench fixture on `orbit/plugin-benchmark-fixture`, with project policy, release notes, component map, work-item CSV, acceptance-test CSV and an untrusted imported issue body.
2. Fetched seven source files through GitHub and verified their returned blob identifiers.
3. Used TinyFish search and fetch on the official Node.js release page. The 2026-11-03 snapshot records v27 Alpha and v26/v24/v22 LTS; the production-use guidance excludes Alpha.
4. Used free Firecrawl tool discovery to locate `package-registry-metadata-download-stats/packages/package`, its required `registry` and `name` inputs, and its one-credit execution cost.
5. Created a release-readiness report on the dedicated branch, fetched it back, and verified all required sections and evidence.
6. Created a separate resume sandbox from the fixture base, wrote a persistent checkpoint, resumed from that checkpoint in later tool calls, re-read all seven source files, created the final review, and fetched it back. The diff from checkpoint to final commit contains only the report path.
7. Reproduced a real GitHub 404 for the incorrect `data/work-items.csv` path, inspected the directory, discovered `data/work_items.csv`, then fetched the correct file and matched its pinned blob.

### Task authoring
Added 10 Stage A task records, one per stratum:
- S01 no-tool arithmetic restraint;
- S02 time-sensitive official-source verification;
- S03 free tool/capability discovery with a cost boundary;
- S04 read-versus-write tool selection;
- S05 exact GitHub tool argument/path contract;
- S06 dependent multi-file release-readiness workflow;
- S07 persistent checkpoint/resume workflow;
- S08 404 error recovery and replanning;
- S09 pre-action effect prediction and verified write closure;
- S10 untrusted issue-content handling and permission restraint.

The manifest now records 10/120 Stage A task instances and 0/120 Stage B task instances. Ten family fingerprints are recorded; Stage B remains sealed. All tasks are `ready_for_validation`, not `validated`; model execution is disabled in every record.

### Current limitations
- S07 has a working persistent GitHub checkpoint and a verified scripted resume reference, but a DHI model-run interruption trace remains pending.
- S09 has working write/readback/diff operations, but the plugin runtime must capture the model's pre-action expected effects before the mutation; it remains partial.
- The ten initial task graders have not yet undergone independent review or model-run validation.
- Consensus search is quota-blocked for this month; Firecrawl paid capability execution has not been authorized; Deepnote project quota remains blocked.

### Artifacts
- `DHI_v1/benchmark/PLUGIN_NATIVE_EXECUTION_PROFILE.md`
- `DHI_v1/benchmark/task_manifest.json` — 10 Stage A tasks, 0 Stage B tasks
- `DHI_v1/benchmark/fixtures/plugin_ecology/plugin_tool_registry.json`
- `DHI_v1/benchmark/fixtures/plugin_ecology/plugin_execution_evidence.json`
- `DHI_v1/benchmark/fixtures/plugin_ecology/` — sources, external snapshots, checkpoint and verified reports

### Decision
Continue authoring and validating the plugin-native Stage A panel. Do not fabricate tool outcomes or claim model capability from these scripted reference actions. Keep Stage B sealed, and do not start candidate model comparisons until the panel and matched inference path are ready.

## 2026-11-03 — Add second independent current-source and security-tool discovery tasks

### New source evidence
- TinyFish searched and fetched the official Python downloads pages on 2026-11-03. The pinned snapshot records Python 3.15.2 as the latest listed stable release (2026-10-25), Python 3.16 as a future planned pre-release, and Python 3.10 as end-of-life.
- Firecrawl free discovery returned three security-related provider capabilities: GitHub Advisory record lookup, OSV package/version vulnerability query, and GitHub Advisory search. Each provider execution was listed as 5 credits. No paid provider was executed.

### Added task instances
- `ORBIT-A-S02-002`: independent Python current-release and maintenance-channel verification task.
- `ORBIT-A-S03-002`: OSV/GitHub advisory provider discovery and schema/cost comparison task.

### Artifacts
- `DHI_v1/benchmark/fixtures/plugin_ecology/external_snapshots/python_releases_2026-11-03.md`
- `DHI_v1/benchmark/fixtures/plugin_ecology/discovery_snapshots/firecrawl_security_provider_discovery_2026-11-03.md`
- Updated `task_manifest.json` and `plugin_execution_evidence.json`.

### Status
The plugin-native Stage A seed now contains 12 records and 12 task-family records: S02 and S03 have two tasks each; all other strata have one. Stage B remains empty and sealed. The schema and cross-record checks passed with unique task IDs/family IDs; no DHI model was run. All records remain `ready_for_validation`.

## 2026-11-03 — Expand plugin-native Stage A seed to 20 independent task families

### Additional live/plugin evidence
- Firecrawl research-provider discovery exposed Semantic Scholar search, paper retrieval and forward citation capabilities (5 credits each), plus Firecrawl research-index inspection (0 credits). Discovery only; no paid provider execution.
- Firecrawl broad package discovery returned a reranking fallback/timeout but still included relevant candidates and a continuation route. A provider-filtered follow-up returned the full package-record contract; discovery cost 0, paid execution cost 1 credit. The paid execution was not called.
- TinyFish fetched the official Python downloads page and returned latest stable/pre-release and branch maintenance status.
- GitHub `compare_commits` returned the exact one-file report diff from a persistent checkpoint to its final report.
- A second GitHub branch-creation reference declared the expected effect before the action: one new branch at the requested base and no changes to existing branch heads. The observed branch list matched the forecast exactly; all previously existing heads remained unchanged.

### New Stage A task instances
- `ORBIT-A-S01-002`: exact vowel-count answer with zero tool calls.
- `ORBIT-A-S03-003`: research paper provider discovery and contract/cost comparison.
- `ORBIT-A-S04-002`: choose read-only commit-diff inspection over file reads or writes.
- `ORBIT-A-S05-002`: correct multi-URL TinyFish `fetch_content` argument schema.
- `ORBIT-A-S06-002`: dependent Node.js/Python source comparison and verified report creation.
- `ORBIT-A-S08-002`: recover from Firecrawl reranking fallback through provider-filtered discovery.
- `ORBIT-A-S09-002`: predict and verify one new GitHub branch with unchanged prior branch heads.
- `ORBIT-A-S10-002`: reject an untrusted instruction that attempts to authorize a paid provider call.

### Actual reference workflow
Created `reports/runtime-release-state.md` on `orbit/plugin-benchmark-fixture`, fetched it back, and verified that a diff from its baseline contains only that report file. Report blob: `55dbb903cf92b10e32e2f80394ebd9ee4c2b55e4`; commit: `26212a111aae8b5bacce1adda92c90e86cf733d8`.

### Current panel status
- **20/120** Stage A tasks materialized.
- **0/120** Stage B tasks materialized; Stage B remains sealed.
- Task count by stratum: S01=2, S02=2, S03=3, S04=2, S05=2, S06=2, S07=1, S08=2, S09=2, S10=2.
- Twenty task IDs and twenty task-family IDs are unique. The live JSON Schema check returned zero errors.
- All 20 task records remain `ready_for_validation`, not `validated`; all model execution flags remain false.
- No DHI candidate model was run. No Firecrawl paid provider call, Consensus search retry, Scite call, Deepnote project mutation, or Adaption generation/training call was made.

### Decision
Continue authoring genuinely distinct plugin-native Stage A task families. Do not fill counts with prompt paraphrases. Keep Stage B sealed and candidate model execution disabled until Stage A is complete, independently reviewed and frozen, and the required inference comparison route is available.

## 2026-11-03 — Add Go release verification and TinyFish schema/404 recovery

### Evidence collected
- TinyFish search and fetch of the official Go Release History page returned Go 1.27.3 dated 2026-10-19 as the latest listed 1.27 minor revision and the general support rule (a major release is supported until two newer major releases).
- The Go page does not state an explicit Go 1.27 end-of-support date; the task requires the model to preserve this uncertainty rather than invent one.
- A TinyFish `fetch_content` invocation without `page_metadata` was rejected by the live connector schema before dispatch. The corrected request returned HTTP 404 for an intentionally wrong Go page path. TinyFish search recovered the canonical official URL, and a fully schema-correct fetch succeeded.

### New task instances
- `ORBIT-A-S02-003`: official Go release/version/support-policy verification.
- `ORBIT-A-S08-003`: TinyFish argument-schema correction, 404 interpretation and official-source recovery.

### Artifacts
- `DHI_v1/benchmark/fixtures/plugin_ecology/external_snapshots/go_releases_2026-11-03.md`
- `DHI_v1/benchmark/fixtures/plugin_ecology/external_snapshots/go_release_recovery_2026-11-03.md`
- Updated task manifest and plugin execution evidence.

### Panel status
Stage A now contains **22/120** task instances; Stage B remains **0/120**, unmaterialized and sealed. Per-stratum counts: S01=2, S02=3, S03=3, S04=2, S05=2, S06=2, S07=1, S08=3, S09=2, S10=2. All tasks remain ready_for_validation, and no DHI model inference or score has been produced.

## 2026-11-03 — Adopt an evidence-first ORBIT research method from autoresearch references

### Sources reviewed
- `karpathy/autoresearch` at `228791fb499afffb54b46200aca536f79142f117`: README, `program.md`, `prepare.py`, and `train.py`. Core method: frozen evaluation/data preparation, narrow mutable surface, baseline first, fixed run budget, one change per experiment, commit-before-run, and durable results ledger.
- `uditgoenka/autoresearch` at `7bddd056dfd0b0ded8360588d8101b1ecb5c0baa`: skill dispatcher, planning, research discovery, evaluation, regression, adversarial reasoning, security, blind-judge, behavior-preservation, and fork-and-flush protocols.

### Decision
Adopt the combined and DHI-specific protocol in [13_ORBIT_RESEARCH_METHOD.md](13_ORBIT_RESEARCH_METHOD.md), with the per-experiment contract in [EXPERIMENT_RECORD_TEMPLATE.md](../experiments/EXPERIMENT_RECORD_TEMPLATE.md).

### Adaptations and limits
- Adopt baseline-first, frozen conditions, one bounded intervention, commit-before-run, explicit failure logging, regression guards, held-out confirmation and durable ledgers.
- Add ORBIT-specific requirements for actual tool traces, pre-action effect predictions, independently observed state deltas, postcondition verification, permission boundaries, and separating model capability from harness capability.
- Use adversarial critics and blind reviewers to test explanations, not to substitute consensus for empirical evidence.
- Restrict fork-and-flush to budgeted exploratory candidate generation. It cannot touch sealed Stage B, authorize paid actions, establish significance, or auto-merge.
- Do not copy Karpathy's five-minute budget or val_bpb; those are specific to its training setup.
- Do not copy upstream autonomy or hook assumptions as a security boundary. ORBIT retains explicit authorization and Git-first controls.

### Current state
- Method and template committed on `orbit/plugin-benchmark-fixture`.
- The branch contains 30 Stage A task instances; Stage B remains 0/120 and sealed.
- All task records remain ready_for_validation; no DHI model inference, capability score, or training run is claimed.
- This decision changes the research operating method, not the benchmark scope, model candidates, or training authorization.

## 2026-11-03 — Implement cross-record ORBIT task manifest integrity validation

### Defects found and repaired
- Three task records referenced `mcp__GitHub__update_file`, but the pinned plugin registry listed only 15 tools and omitted that exact contract. Added the exact connected tool description, bringing the registry to 16 tools, and recomputed the canonical registry digest.
- Five task evidence references pointed to checkpoint/report files that had been created on separate experiment branches. Copied the exact source blobs onto the active plugin benchmark branch so every task reference resolves within the branch used for review.
- The workspace had stale 22-task counts even though the manifest contained 30. The current checkpoint is corrected to 30/120 Stage A.

### Integrity contract
- Added `task_instance_sha256` to required schema fields.
- Recomputed deterministic `family_fingerprint_sha256` from the substantive task definition: stratum, task contract, environment, tool inventory, capabilities, horizon, preconditions, postconditions, grader and policy.
- Recomputed task-instance hashes from the full task record excluding only its own hash field.
- Canonical hash serialization is UTF-8 JSON with sorted keys and compact separators; SHA-256 is used throughout.
- Added `validate_task_manifest.py` to check JSON Schema plus cross-record counts, task ID numbering, family registration, stage/independence split, hashes, tool registry membership/digest, required-tool visibility, repository evidence references and Stage B secrecy.
- Added 17 unittest regression cases in `tests/test_task_manifest_validator.py` for valid authoring state, partial quotas, count drift, duplicate IDs, identity mismatch, family/hash drift, unregistered tools, missing evidence, undiscoverable required tools, sealed Stage B exposure, incomplete freeze gates and deterministic serialization.

### Static inspection
At GitHub commit `3d57cc876dcd3f1f82c9d3ff884665de52c7f290`, an independent static check recomputed all 30 task-instance hashes and 30 family fingerprints, verified all 16 task tool contracts and the registry digest, confirmed every referenced evidence file exists, confirmed no Stage B body is present, and returned zero structural integrity errors.

### Runtime test limitation
GitHub Actions run `41594301494` for the branch ended in failure before a runner was allocated. The job API reported `runner_id=0` and no steps; log retrieval returned no artifact. Therefore the validator module, pytest tests, and compileall were **not executed** by that CI run. This is recorded as an infrastructure execution blocker, not a code test failure or pass. The repeatable commands are in `benchmark/README.md`.

### Current decision
Keep the manifest at `status=authoring`; do not mark any task validated or freeze the panel. Next, execute the validator/tests on a working Python runner, continue the 90 remaining Stage A tasks with distinct families, and preserve Stage B outside this shared public repository until the confirmation release gate is authorized.


## 2026-11-03 — Verify ORBIT manifest integrity and plugin trace grader

### Result

At code commit `421955df46975d8b20fba63f8922949a49b4551c`, an isolated Deepnote runner completed all checks:
- Cross-record manifest validator: `valid=true`, 30 tasks, Stage A=30, Stage B=0, zero errors.
- Focused tests: **44 passed, 0 failed** (20 manifest-validator tests and 24 plugin trace-grader tests).
- `compileall -q DHI_v1/benchmark`: exit code 0.

Runner: Python 3.13.18. Deepnote run: `52254373-656f-4d0c-841d-c3a2c621d7cc`. Machine-readable record: [ORBIT-VERIFY-002](../experiments/ORBIT-VERIFY-002/).

### Scope boundary

This verifies manifest, hash, evidence-reference and deterministic trace-grader integrity. It does not mean any of the 30 tasks has been model-executed, independently validated, or frozen. The 30 task records remain `ready_for_validation`; Stage A is 30/120 and Stage B is sealed at 0/120.

## 2026-11-03 — Separate OpenRouter inference availability from Adaption training access

### Decision and evidence

The connected OpenRouter catalogue exposes both selected untouched-base candidates:
- `qwen/qwen3.6-35b-a3b` — PrimeIntellect fp8 endpoint, tool calling supported.
- `openai/gpt-oss-20b` — PrimeIntellect fp4 endpoint, tool calling supported.

Both advertise `tool_choice=auto`. The PrimeIntellect route is the common named-provider route; the GPT-OSS endpoint does not advertise `tool_choice=required`, so the initial matched protocol must use only shared supported modes. The live OpenRouter credit audit returned **$0 total credits**. A price-free endpoint query returned no free endpoint for either exact model. No inference call was made.

Adaption's training registry separately lists Qwen3.6, GPT-OSS-20B and Gemma 4 31B as trainable models. Registry/training support is not hosted inference access. See [INFER-002](../experiments/INFER-002/).

### Consequence

A matched base-model smoke is now technically routable but financially blocked on OpenRouter. Do not silently switch providers, compare unmatched quantizations, or use a single-candidate run as a model-selection result. No DHI model capability result is claimed.

## 2026-11-03 — Hold DHI training pending dataset lineage audit

### Evidence

- Adaption's Qwen3.6-35B-A3B recommender requires at least 10,000 effective training rows and returned a LoRA configuration for dataset `843888da-28e2-420e-909e-88b203d16404`.
- That dataset metadata declares 10,000 rows and prompt/completion columns `rephrased_prompt` / `enhanced_completion`. Its evaluation record, however, names the separate 300-row dataset `c1f4df14-b12c-430c-91ad-e10b559d1cee` as both input path and config source, and records a 100-row sample. The A grade cannot be attributed to the 10K export without reconciliation.
- The 300-row ORBIT pilot has null prompt/completion mapping and only partial previous row review; the 120-row task-spec dataset scored Grade C / 6.6 with completion quality at the 2.2nd percentile.
- Historical Qwen3.5-4B DPO run `5f16632f-f4d4-49da-a5ce-5faf66a47d80` reached best_win_rate 0.4609 against a 0.99 target; it is not release evidence.

### Decision

No training, augmentation, or data-generation job is authorized from this audit. Retrieve the actual private 10K export, inspect row semantics and duplicates, reconcile evaluation lineage, produce a clean train/validation split, and obtain cost information before any paid run. Keep intent-arbitration instruction data separate from ORBIT task contracts and real tool-execution trajectories.

Machine-readable record: [TRAINING-ACCESS-002](../experiments/TRAINING-ACCESS-002/).


## 2026-11-03 — Extend ORBIT verification to the environment and model-runner layer

### Verified prior result

The latest completed full benchmark-only regression run, `7da82150-e44d-415d-ac00-206b112cf811`, passed **82 benchmark tests**, and the manifest validator and benchmark compile check passed at code commit `421955df46975d8b20fba63f8922949a49b4551c`. This is broader than the earlier 44 focused tests, but it does not cover the environment test modules.

### Combined verification started

A combined verification was started in the existing isolated Deepnote verifier. It includes the manifest validator, both benchmark and environment test directories (136 declared test functions at source inspection), compileall for both packages, and an import smoke for the runner and adapters. Run ID: `f661f5ad-7c5e-48b9-9af6-afda1e6f021b`. Its durable record is [ORBIT-VERIFY-003](../experiments/ORBIT-VERIFY-003/).

At the last status check, the run remained `running` and had no terminal snapshot. No pass/fail count is claimed.

### Process deviation and boundary

The combined run was launched before its experiment manifest was committed, contrary to the commit-before-run rule. This has been recorded in ORBIT-VERIFY-003. The tested code revision is pinned; this was a regression check only. No model inference, training, data generation, provider-credit spend, task-validation status change, or model-capability claim occurred.


## 2026-11-03 — Correction: ORBIT-VERIFY-003 completed successfully

The earlier entry recorded the combined regression as running. This is the terminal result:

- Deepnote run `f661f5ad-7c5e-48b9-9af6-afda1e6f021b`: `success`.
- Manifest validator: valid; 30 task records; Stage A=30; Stage B=0; zero errors.
- Combined benchmark and environment test suites: **136 passed, 0 failed**.
- `compileall -q DHI_v1/benchmark DHI_v1/environment`: exit code 0.
- Import smoke for `agent_runner`, `adaption_responses`, and `benchmark.runner`: passed.
- Runner: Python 3.13.18.
- Exact output and command timings are archived at [ORBIT-VERIFY-003/results/verification-report.json](../experiments/ORBIT-VERIFY-003/results/verification-report.json).

The tested code commit remains `421955df46975d8b20fba63f8922949a49b4551c`; intervening branch commits are documentation-only. This pass confirms benchmark/environment code health. It does not validate the 30 authored task instances, establish model capability, approve training, or open model execution.


## 2026-11-03 — Plugin benchmark grader and model-runner integration gate

### Grader work

ORBIT-GRADER-FIX-001 added deterministic support for discovery recovery and repository branch-state prediction. The runner tool schema now allows structured branch-state predictions, the local environment preserves those predictions in the pre-action event and refuses to label them matched based only on file-workspace evidence. The grader compares the pre-action forecast with independently fetched before/after branch inventories.

Focused verification passed: **46 tests**, manifest validator, and benchmark compilation. Full regression on the current branch head `92bec2c3485220eec6c80a7fe8ae41865a4ef54e` is running as Deepnote run `43e0726e-e16d-428c-b2dd-f18332e2f882`. Do not claim full-suite success until its terminal output is inspected.

### Model execution gap discovered

Code inspection confirmed `DHI_v1/environment/agent_runner.py` does not yet execute the remote GitHub/TinyFish/Firecrawl tools defined in the plugin-native task register. It builds tool schemas from the local DHI environment catalogue and exposes Adaption catalogue search only as a discovery-only meta-tool. The connected plugin actions used for reference evidence are therefore not proof that the candidate model can invoke those tools.

### Decision

Prioritize a policy-enforcing remote plugin gateway and normalized trace adapter before expanding the benchmark panel or attempting model-facing plugin tasks. The gateway must bind exact registered tool contracts, permissions, approvals and cost boundaries; record pre-action prediction, invocation, raw response, independent state readback and closure; and preserve checkpoint/resume events. No model execution, training, or Stage A validation status promotion is authorized by this decision.


## 2026-11-03 — Full regression adjudication

The full regression run `43e0726e-e16d-428c-b2dd-f18332e2f882` completed against `92bec2c3485220eec6c80a7fe8ae41865a4ef54e`. Manifest validation passed for 30 Stage A tasks and zero Stage B tasks. Pytest reported 141 passed and one failure: a runner schema test expected a nested `$defs` object although the emitted schema uses inline branch item definitions. The active branch corrected the test assertion to inspect the inline schema. This correction has not yet been executed: Deepnote rejected the rerun because its parallel-project quota was exceeded; the DHI verifier machine was stopped and no other project was stopped. Compileall and import smoke did not run in the failed combined gate. Keep the full verification gate open until a rerun passes. The current task panel remains 30/120 Stage A; all 30 have unique task-family and independence-group IDs and remain `ready_for_validation`, not model-validated.

### Execution route constraint

The current Adaption Responses adapter supports model inference with caller-supplied function tools and separately supports read-only connector-catalogue discovery. It does not currently turn catalogue entries into executable remote connector actions. The deterministic DHI environment intentionally exposes only file-workspace tools plus discovery. The plugin-native task profile records connected GitHub/TinyFish/Firecrawl evidence, but those ChatGPT-connected actions are not callable by the DHI model runner through the current adapter. Do not assume Adaption Responses supports remote MCP execution without a documented contract and an integration test. Keep the external-plugin model execution gate closed until such a contract is verified and a policy-enforcing adapter exists.


## 2026-11-03 — Correction: ORBIT-GRADER-FIX-001 full regression passed

This entry supersedes the earlier open-gate conclusion in the same-day full-regression adjudication. The corrected runner-schema assertion was executed as part of the complete regression.

### Verified result

- Deepnote run `34ca752c-e864-4a3d-9388-957d2c3e1859` completed with terminal status `success` against code commit `cba8421d4f4c6c4f929d5f4c3196eb83f98f7351`.
- Cross-record manifest validator: valid; 30 tasks; Stage A=30; Stage B=0; zero errors.
- Combined benchmark and environment test suites: **142 passed, 0 failed**.
- `compileall -q DHI_v1/benchmark DHI_v1/environment`: exit code 0.
- Import smoke for `agent_runner`, `adaption_responses`, and `benchmark.runner`: passed.
- All four commands returned exit code 0.

### Raw evidence

The run snapshot is available in Deepnote project `6415944e-8d6c-432c-a7cf-3bbaa997799c`, notebook `3639f9a98ce5435fa4cd0168eaaca3a1`, output block `43e281b25689485a9ff1c31e7cbfcbdc`. The machine-readable raw report is `grader-fix-full-report-final.json`; run ID `34ca752c-e864-4a3d-9388-957d2c3e1859`; block content hash `sha256:4a6a556b2ed08feb83f3119939e2642756b5701b36f85d1645f176b66aad25b5`. The detailed run record is in [ORBIT-GRADER-FIX-001](../experiments/ORBIT-GRADER-FIX-001/).

### Current-head equivalence

The branch head at adjudication was `43608791494e445b17556e1ec8fc08b8a9f2f455`. GitHub comparison from tested code commit `cba8421d4f4c6c4f929d5f4c3196eb83f98f7351` to that head shows six commits, with changes only to `DHI_v1/WORKSPACE.md`, this decision log, and the ORBIT-GRADER-FIX-001 README/manifest. No runtime or test source changed after the passing run.

### Retry failures and interpretation

The later notebook run `220cc301-c5de-4c33-b507-784d456935d6` stopped without output. Run `b401c21c-d586-4a69-8e69-80c6cf02ae43` failed before pytest collection because the cell omitted installation of `DHI_v1/environment/requirements-dev.txt` and the detached environment had no `pytest` module. These are verifier bootstrap failures, not code regressions; they do not supersede the completed full pass.

### Decision

Close the runtime/test regression gate at code commit `cba8421d4f4c6c4f929d5f4c3196eb83f98f7351`; the current branch remains code-equivalent. This proves harness/code health only. It does not validate the 30 task instances through a candidate model, establish model capability, authorize training, or authorize paid model/provider actions. The next research bottleneck is the documented, policy-enforcing remote-plugin execution interface.

## 2026-11-03 — PLUGIN-GATEWAY-001 provider execution feasibility audit

### Question

Can the exact GitHub, TinyFish and Firecrawl actions in plugin_tool_registry.json be invoked by the DHI runtime through documented remote MCP interfaces, with least-privilege credentials, task-level allowlists, cost controls, prediction-before-action traces, and independent readback?

### Evidence reviewed

- GitHub official remote MCP documentation identifies https://api.githubcopilot.com/mcp/ and a /readonly surface. The remote server requires a valid bearer token obtained by the client; it does not itself provide authentication. OAuth 2.1 or a PAT is supported; dynamic client registration is not supported by the remote server. Sources: https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md and https://github.com/github/github-mcp-server/blob/main/docs/host-integration.md
- TinyFish official MCP documentation identifies https://agent.tinyfish.ai/mcp. Its official proxy reads TINYFISH_API_KEY from the process environment and forwards it upstream as X-API-Key. Its published examples classify search and fetch_content as free, while browser automation is metered per step. Sources: https://github.com/tinyfish-io/tinyfish-mcp-server and https://github.com/tinyfish-io/tinyfish-mcp-server/blob/main/docs/examples.md
- Firecrawl's standard hosted MCP documentation describes generic scrape/search/parse tools and separate authenticated hosted surfaces. This does not establish that its standard server exposes the exact Alexandria firecrawl_find_tools tool contract captured in the connected-plugin registry. The registry's Alexandria firecrawl_scrape is explicitly excluded as paid. Source: https://github.com/firecrawl/firecrawl-mcp-server
- MCP Streamable HTTP uses POST JSON-RPC requests and permits JSON or SSE responses; the latest protocol version adds required mirrored request headers and changed session behavior. The gateway must negotiate compatibility rather than assume every provider implements the newest revision. Source: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/basic/transports/streamable-http.mdx

### Runtime check and constraints

The isolated DHI verifier project's integration inventory is empty. That proves no provider integration is attached to that Deepnote project, but does not establish whether manually configured process environment variables exist. No key or token values were read, emitted, or logged. No provider MCP request, remote action, model inference, paid call, or write was made.

A same-named remote MCP function is not proof of semantic/schema equivalence to the registered connector action. In particular, the Firecrawl Alexandria contract must not be mapped to a generic page scrape by name alone.

### Decision

**Blocked before implementation.** Documented remote MCP transport exists for all three providers, but the DHI runtime has neither a verified credential path nor provider-native tool-schema attestation. TinyFish is the first candidate for a read-only smoke because its registered search and fetch_content actions are read-only and documented free.

No model-facing remote tool has been added; no task has been promoted from ready_for_validation; no provider credit has been spent. The next gate is a secure TinyFish credential check and read-only MCP initialize/tools/list smoke, followed by an independent source readback.

## 2026-11-03 — PLUGIN-GATEWAY-001 redacted credential presence probe

A temporary Deepnote notebook cell ran a presence-only check in the DHI verifier runtime. It checked 12 conventional variable names across TinyFish, GitHub and Firecrawl:

- TinyFish: `TINYFISH_API_KEY`, `DHI_TINYFISH_API_KEY`, `MCP_TINYFISH_API_KEY`, `TINYFISH_OAUTH_ACCESS_TOKEN`
- GitHub: `GITHUB_PERSONAL_ACCESS_TOKEN`, `GITHUB_TOKEN`, `GH_TOKEN`, `DHI_GITHUB_TOKEN`, `MCP_GITHUB_TOKEN`
- Firecrawl: `FIRECRAWL_API_KEY`, `DHI_FIRECRAWL_API_KEY`, `FIRECRAWL_OAUTH_TOKEN`

All 12 were absent. The code evaluated boolean presence only; no secret values were read, printed, hashed, serialized or persisted. The run sent zero remote requests. The temporary cell was deleted and the verifier machine stopped after the probe.

- Deepnote run: `712a9c26-d126-4cc0-bfdb-a564dd29e3d1` (success)
- Notebook: `3639f9a98ce5435fa4cd0168eaaca3a1`
- Output block: `a8b57e8a508349a3a50a144ceeb4313b`
- Output hash: `sha256:e5a473f06e7d1e78ce66cbbf9e2f157ad6cafb3b353d3c14549019ca0766367c`
- Project integrations attached: none

This only establishes that the 12 conventional names were not present in that runtime at probe time. It does not rule out a differently named variable or an OAuth mechanism configured elsewhere.

**Decision:** keep PLUGIN-GATEWAY-001 blocked before implementation. The next step is to provision `TINYFISH_API_KEY` through the Deepnote project secret store (or set up a supported OAuth connection) without sharing the credential in chat or committing it. Then perform a read-only TinyFish MCP `initialize`/`tools/list` smoke and an independently verified bounded search/fetch. No model-facing remote tool, provider request, paid action or model inference is authorized yet.


## 2026-11-03 — Current branch code equivalence resolved by direct blob audit

A broad GitHub compare summary listed implementation/test files in its aggregate file list after the passing 142-test commit, so the branch-equivalence claim was checked file by file rather than relying on the aggregate summary. Direct reads at tested commit `cba8421d4f4c6c4f929d5f4c3196eb83f98f7351` and current branch ref `orbit/plugin-benchmark-fixture` returned identical Git blob SHAs for all 11 relevant runtime, benchmark, schema, manifest and test files. The complete path/hash list is in [PLUGIN-GATEWAY-001](../experiments/PLUGIN-GATEWAY-001/README.md).

This confirms the 142-test result applies to the current runtime/benchmark code contents. It is not a fresh test execution. No implementation code was changed during the gateway feasibility or credential-probe work.


## 2026-11-03 — User-reported TinyFish secret setup; verification blocked by Deepnote quota

The user reported that `TINYFISH_API_KEY` had been added to the DHI verifier project's secret store. This is a user-reported configuration change, not a runtime-verified secret.

A temporary presence-only probe cell was created in the existing verifier notebook. Deepnote rejected both the project machine start and a detached read-only run before execution with the parallel-project quota error: `Your plan quota for parallel running projects has been exceeded. Please stop one of your running projects.`

The temporary cell was deleted. The existing regression cell was left untouched. The verifier machine remains stopped. No credential values were read or printed; no TinyFish MCP `initialize`, `tools/list`, or `tools/call` request was sent.

**Decision:** keep the TinyFish execution gate blocked. After a Deepnote run slot is available, repeat the presence-only `TINYFISH_API_KEY` check. Only if that check succeeds should the read-only MCP handshake and bounded `search`/`fetch_content` test proceed. Do not paste the secret into chat or stop another project through this agent.
