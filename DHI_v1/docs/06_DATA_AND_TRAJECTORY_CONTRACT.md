# DHI-v1 Data and Execution-Trajectory Contract

**Version:** 1.0  
**Date:** 2026-10-31  
**Status:** Proposed schema. Implement and validate before dataset scaling.

## 1. Core rule

DHI-v1 needs examples of an agent acting in an environment, not merely an LLM describing how an agent might act.

**Invented task prompts may be synthetic. Ground-truth tool outputs, state changes, test results, and task completion labels must be produced by real sandbox execution or independently verified authoritative records.**

Do not treat an LLM-written imagined tool result as an observed result.

## 2. Separation of data generation stages

Keep these as separate operations:

1. **Task invention:** create diverse tasks, constraints, and edge cases.
2. **Environment setup:** create/reset a reproducible sandbox with known initial state.
3. **Tool inventory:** record the actual tools and schemas available to the agent.
4. **Agent execution:** run the model and capture every action and observation.
5. **Outcome verification:** compute real state diffs, tests, and postconditions.
6. **Quality review:** inspect labels, source lineage, duplicates, and semantic consistency.
7. **Dataset packaging:** convert verified traces to SFT or preference rows with immutable identifiers.

Adaption Invent can help generate task descriptions and variants. It must not invent ground-truth state transitions. Adaptive Data/Visualize can support inspection and filtering; they do not replace environment execution or independent evaluation.

## 3. Required trajectory schema

Each task/trajectory should contain the following top-level fields:

| Field | Type | Required | Meaning |
|---|---|---|---|
| trajectory_id | string | yes | Immutable trajectory identifier. |
| task_id | string | yes | Stable task instance identifier. |
| task_prompt | string | yes | Exact user task presented to the model. |
| task_goal | object/string | yes | Intended outcome and task-level intent. |
| hard_constraints | array | yes | Must-preserve constraints. |
| preferences | array | yes | Soft preferences where applicable. |
| initial_state_ref | string/object | yes | Reproducible environment snapshot or reset identifier. |
| environment_type | string | yes | Repository, terminal, browser, database, spreadsheet, app, etc. |
| environment_version | string | yes | Image, commit, API fixture, or environment release. |
| tool_manifest | array/object | yes | Exact tools, schemas, permissions, and availability at start. |
| discovery_events | array | no | Catalogue searches and discovered tool candidates. |
| plan_version | integer | yes | Versioned plan state. |
| action_steps | array | yes | Ordered action/observation records. |
| final_state_ref | string/object | yes | Reproducible final environment state. |
| postconditions | array | yes | Executable or independently checkable final criteria. |
| verified_outcome | object | yes | Task success/partial/failure/infeasible with evidence. |
| provenance | object | yes | Source, generator, runner, timestamps, model, and version lineage. |
| split | string | yes | train / validation / test / sealed. |

## 4. Action-step schema

Each action step should capture:

| Field | Meaning |
|---|---|
| step_id / sequence | Stable identity and position. |
| observed_state_ref | State and relevant observations before action. |
| task_subgoal | Current milestone/subgoal. |
| available_tools | Exact visible tool subset at decision time. |
| missing_capability | The capability, if any, not represented in the visible set. |
| discovery_query | Catalogue query and discovered results, if used. |
| candidate_actions | Candidate actions/tools when available. |
| selected_action | Direct answer, tool discovery, tool call, parallel calls, delegate, clarify, safe stop, or replan. |
| selected_tool_id | Exact tool identifier when calling. |
| arguments | Actual serialized arguments. |
| expected_effects | Pre-action prediction of relevant state changes, invariants, and side effects. |
| expected_evidence | What evidence should appear if the action works. |
| actual_tool_result_ref | Raw output/log reference, not a generated paraphrase. |
| actual_state_delta | Computed state changes after execution. |
| tests_and_checks | Test results, schema checks, or authoritative verification. |
| prediction_comparison | Correct, partially correct, incorrect, or unscorable with reason. |
| plan_update | How task state and future steps changed. |
| safety_and_permission_check | Permission/consent and side-effect result. |
| action_cost | Tokens, latency, tool cost, retries where measurable. |

Do not require the model to expose private hidden chain-of-thought. The target can contain a concise action rationale, explicit predictions, structured plan state, tool calls, observations, and verification outcomes. Train decisions and behavior, not disclosure of hidden reasoning.

## 5. SFT target format

For SFT, preserve the sequence:
- task and constraints;
- relevant context and tool inventory;
- concise plan or next milestone when useful;
- tool discovery or invocation decision;
- actual tool calls in the model's native format;
- actual observations;
- plan updates;
- final verified answer/report.

Do not force every task into a long multi-section answer. Direct-answer examples should remain direct. A one-step task should not be inflated into a 20-step trace.

The model must experience both:
- tasks where tools are required;
- tasks where no tool should be used.

## 6. Preference-pair format for DPO

A preference pair should contain:
- the same task and equivalent initial state;
- two complete or comparable action/response trajectories;
- chosen trajectory with verified better task outcome;
- rejected trajectory with a specific failure reason;
- evaluator and provenance;
- whether the preference is outcome-based, policy-based, safety-based, efficiency-based, or a combination.

Valid preference contrasts include:
- correct tool discovery vs stopping at the visible tool list;
- suitable tool vs misleading/irrelevant tool;
- safe dependency-aware plan vs destructive sequence;
- useful parallelism vs conflicting parallel writes;
- adaptive replanning vs repeating failed calls;
- verified completion vs false completion;
- direct answer vs unnecessary tool call.

Do not derive a chosen/rejected pair by paraphrasing one answer twice. Do not treat a model's own preference score as the only ground truth.

## 7. Data lineage and quality fields

Keep:
- original task source (human, public benchmark, synthetic task specification, user-authorized task);
- task generator/model and version if synthetic;
- environment generator/version;
- executor/model version;
- actual tools used and schemas;
- raw tool logs or references;
- test/postcondition grader version;
- data transformation history;
- parent/child dataset lineage;
- timestamps;
- content hashes;
- train/validation/test split identity;
- reviewer and review outcome.

An invented task may legitimately lack an original human user prompt. A sourced real task should retain its source. Never classify a missing field without considering the row's provenance.

## 8. Data quality gates

Before a row is accepted:
1. Schema validation passes.
2. Exact and near-duplicate checks run across train and held-out splits.
3. Prompt and trajectory describe the same task.
4. Tool outputs are linked to real execution logs.
5. State diffs and postconditions are reproducible.
6. No invented numeric achievements, files, test results, API outputs, or permissions appear as facts.
7. The chosen tool was actually available/authorized in the recorded environment.
8. Argument schema matches the tool version.
9. The final completion label is consistent with the actual final state.
10. The task's difficulty, horizon, domain, and tool complexity are tagged.
11. The example is not a near-duplicate of validation/test content.
12. High-risk actions are tested in a sandbox and have permission labels.

## 9. Adaption-specific lessons

Adaption support stated on 2026-10-30:
- repeated content can result from augmentation being run multiple times from an already augmented invented seed;
- invented rows may naturally lack an original user prompt because they were not sourced from an original user;
- the augmentation grade was being copied from the source dataset, and Adaption said it was fixing grading to run fresh evaluation on augmentation.

Operational rules:
- Never recursively augment an already-augmented seed as the default data-scaling strategy.
- Treat an inherited grade as inherited until a new evaluation timestamp/source proves otherwise.
- Inspect rows with Visualize Data and the new quality-checklist feature where available.
- Separate missing original-source fields from broken prompt/response pairs.
- Maintain lineage and rejection reasons.
- Re-check that the actual data columns used for training match the intended prompt/completion or chat schema.

Earlier AutoScientist attempts enforced 1,000 effective SFT rows and 12,000 effective preference pairs for DPO. Verify the current platform requirements before future runs; do not pad with duplicates.

## 10. Data volumes: do not confuse minimum rows with useful data

Initial pilot:
- 120 model-screening tasks are evaluation items, not necessarily training rows.
- Build a small execution pilot first to validate the runner and schema.
- Inspect coverage and label correctness before scaling.

First Adaption SFT candidate:
- Must meet the platform's live minimum.
- Use 1,000+ genuinely distinct, verified trajectory examples only if they exist.
- If the pilot does not produce enough high-quality rows, extend task coverage and execution collection; do not repeat/duplicate rows.

DPO:
- Build only from real paired trajectory outcomes.
- Re-check the live effective-pair minimum.
- Do not start DPO until SFT/base behavior and preference quality are understood.

## 11. Adaption feature usage

- **Invent:** create task specifications, constraints, variants, and edge cases. Do not ask it to fabricate tool execution outcomes.
- **Adaptive Data:** apply quality checks, deduplication, and filtering where controls are exposed. Preserve rejection reasons.
- **Visualize Data:** inspect distributions, suspicious clusters, domain coverage, row-level examples, and lineage.
- **AutoScientist:** train supported SFT/DPO runs after schema, estimate, and benchmark gates pass.
- **Inference Stacks:** evaluate separately for inference-time routing/context/runtime improvement. Do not label it a learned-weight architecture change without evidence.

## 12. Storage and privacy

Use sandboxed fake accounts and test data for email, calendar, purchases, cloud, and other external side effects. Never store API keys or user credentials in dataset rows or public GitHub. Keep private environment snapshots, raw logs, and sensitive task payloads outside public repository commits. Commit schemas, manifests, synthetic safe examples, and reproducibility code.
