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
