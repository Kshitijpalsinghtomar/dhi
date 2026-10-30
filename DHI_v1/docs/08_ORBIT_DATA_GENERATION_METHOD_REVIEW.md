# ORBIT — Synthetic Data Method Review and Reset

**Date:** 2026-10-31  
**Status:** Method correction. No further Invent generation or model training authorized until the relevant gate below passes.  
**External codename:** ORBIT. Generated dataset names, task IDs, prompts, and row metadata must not contain the internal programme name.

## 1. Decision in one paragraph

The two failed Invent runs are primarily a **data-target mismatch**, not evidence that the underlying agentic capability is impossible to train. We asked Adaption Invent to return a natural-language user task as the prompt and a long JSON benchmark/task specification as its completion. Invent's instruction-dataset format treats that completion as the answer the model should learn to produce. A task contract is not the answer to the user request, and it is not an executed agent trajectory. The low completion-quality scores are therefore consistent with the format we asked it to produce. Making that contract more elaborate worsened the measured results. Do not repeat this generation shape.

## 2. What Invent is actually designed to do

Adaption's published Invent research (arXiv:2610.01674, v2 dated 2026-10-18) describes a prompt-based system that starts from a dataset description and generates model-ready **instruction datasets** (prompt/completion) or **preference pairs**. Its benchmark evaluates generated prompt quality, completion quality, relevance, and diversity. It does not evaluate real tool execution, state mutation, task closure, or agentic competence.

The paper's experimental setup uses a single dataset request and generates the corpus in one call. For comparisons against ordinary model APIs, the authors also study one-by-one, fixed-batch, and maximum-batch generation; one-by-one prompting suffered near-total diversity collapse. Their evaluated requests are conventional datasets such as QA, customer support, summaries, and structured responses—not environment-coupled tool-use trajectories.

The paper's quality measures are:
- Prompt quality, 0–10: specificity, scope, completeness, and clarity.
- Completion quality, 0–10: response quality, structure, and adherence to the prompt's constraints.
- Relevance, 0–10: whether the generated sample matches the requested task type, scope, language, and stated format/style constraints.
- Diversity: semantic DCScore and lexical prompt metrics such as n-gram diversity, compression ratio, and exact-duplicate rate.

These are dataset-generation diagnostics. They are **not** the internal 100-point agent capability rubric, an execution verifier, or proof that a row is solvable.

Most importantly, the paper's Limitations section explicitly says Invent currently produces instruction and preference datasets but does **not** generate tool-call traces or multi-step agentic trajectories from an agent driving a harness. The authors identify this as future work because traces depend on environment-specific tools, signatures, and control flow. This is decisive for our method choice.

Sources:
- https://arxiv.org/abs/2610.01674
- https://docs.adaptionlabs.ai/adaptive-data/invent-a-dataset/
- https://docs.adaptionlabs.ai/adaptive-data/overview/

## 3. What our two actual runs show

Both datasets completed 120/120 rows. Generation success only means the platform created rows; it does not mean the rows are valid task specifications, usable benchmark cases, or training traces.

| Run | Dataset ID | Grade / score | Before → after | Prompt/message mean | Completion mean | Completion percentile | Diversity |
|---|---|---:|---:|---:|---:|---:|---:|
| First task-spec attempt | `1eccaa36-bdc7-4d6e-ac8d-41b20d9425e2` | B / 7.7 | 8.0 → 7.7 (-3.7%) | 8.62 (28.9th percentile) | 6.80 | 2.7th | DCScore 84.43 (normalized 0.844) |
| Rubric-heavy task-spec attempt | `be05757d-2f24-45d4-8768-659268d9d18e` | C / 6.6 | 7.0 → 6.6 (-5.7%) | 8.18 (28.9th percentile) | 5.03 | 2.2nd | DCScore 69.11 (normalized 0.691) |

The second dataset page also reports an average prompt length of about **81 words** and an average completion length of about **368 words**. The generated completions were long JSON task contracts, not concise agent responses or real action/observation sequences.

### Interpretation

1. Prompt/message quality stayed moderate and relatively stable (8.62 to 8.18).
2. Completion quality was the dominant failure in both attempts (6.80 then 5.03), with a very low reference percentile.
3. The second run's completion median was 2 and standard deviation 4.0, indicating especially inconsistent completion quality.
4. The second run's DCScore was 15.32 points lower (about 18.1% relative). This is an observed difference, **not a clean causal ablation**: the two prompts and domain mixes differed, so it cannot be attributed to one constraint alone.
5. The platform's before/after score is an Adaptive Data quality comparison, not a model benchmark score and not a training result.

Our main design error was asking Invent to produce **benchmark metadata as the supervised answer**. The output schema contained task IDs, strata, rubric mappings, environment contracts, tool configuration, graders, and provenance. Those are useful authoring fields for us, but they are not what a capable agent should say or do in response to the user prompt. The model would be trained to emit benchmark paperwork instead of performing the task.

The second prompt compounded this mismatch with many simultaneous constraints: ten exact strata, fixed counts, long JSON schema, many rubric fields, environment compatibility rules, and extra per-row quality requirements. The Invent paper reports that additional output constraints reduce diversity by 15–22% for the other evaluated generators; Invent is more robust in the paper's tested setting, but that is not a guarantee for highly nested, environment-specific schemas. Our own diversity decrease is consistent with the risk, although not proof of causation.

No model has executed these tasks. Neither run provides evidence of actual tool selection, correct tool calls, state changes, replanning, or closure.

## 4. What the Adaption pipeline can and cannot certify

### Invent
Use for:
- zero-seed prompt/completion instruction data;
- zero-seed preference-pair candidates;
- concise examples of a single decision or response when the completion is a real answer to the prompt.

Do not use as the source of:
- real tool-call trajectories;
- actual tool results;
- environment state changes;
- tests, postconditions, or verified closure;
- multi-step agent execution traces.

### Adaptive Data
The product workflow can import data, map prompt/completion/context/chat columns, apply recipes such as prompt rephrasing and deduplication, expand/translate/localize, apply brand controls, and adapt/evaluate. Its quality comparisons do not replace task execution or an independent outcome grader. Rephrasing and augmentation must not be used to inflate row counts or silently change task meaning.

### AutoScientist
Supports registered SFT/instruction and preference/alignment training workflows. Training support does not make unsuitable rows valid. We must not launch a run simply because a dataset is marked ready.

The live platform's exact model registry, minimum row requirements, and training formats must be re-checked when the real training data is ready.

## 5. Correct data architecture: three separate products

### Product A — ORBIT benchmark task specifications

Purpose: construct a valid hidden/development benchmark.

Each case contains a realistic user request plus a separate task contract with:
- stable task ID and template-family ID;
- task goal and hard constraints;
- initial-state/fixture definition;
- exact visible and allowed tool manifest;
- supported environment and version;
- deterministic postconditions or named human-review procedure;
- primary capability dimension and limited secondary dimensions;
- difficulty and expected action horizon;
- failure modes and critical safety conditions.

The task contract is evaluation metadata. **It is not the model's SFT completion.**

Method:
1. Design task families from the capability rubric and known failure modes.
2. Produce prompts and contracts using an authoring model/process separate from Invent's prompt/completion training-data generator.
3. Validate JSON schema, exact tool IDs, tool schemas, fixture references, and postcondition types mechanically.
4. Run duplicate and near-duplicate checks across task prompts, template families, and splits.
5. Independently review prompt/contract alignment and task solvability.
6. Materialize supported cases in a pinned environment and run the grader against known reference actions or scripted validation.
7. Freeze a development set and a sealed set only after task validity is established.

A generated case is not benchmark-ready merely because its JSON parses. The current file-workspace harness only supports its implemented tools and postcondition types. Unsupported tasks must remain future-adapter tasks and cannot receive a pass/fail score in that harness.

### Product B — ORBIT one-step decision supervision (optional Invent use)

Purpose: teach a narrow pre-execution decision skill that can be expressed as ordinary prompt/completion examples.

A row's **prompt** must contain the complete decision context:
- the user's actual goal;
- current observed state or an explicitly described synthetic snapshot;
- the available tool manifest, including relevant schemas, preconditions, permissions, freshness, and side effects;
- the applicable constraints.

The **completion** must be the concise decision the agent should make next, for example:
- answer directly / no tool;
- discover a missing capability;
- select a particular tool and provide schema-valid arguments;
- ask one necessary clarification;
- refuse or safe-stop due to authorization/availability;
- verify a named condition before claiming closure.

Do not output a giant task-spec JSON object as the answer. Use a small, fixed action format with only the fields necessary for the decision. A tool call in this dataset means a **proposed next action**, not an executed call. Never include fabricated tool results or claim an action happened.

Use codename **ORBIT** and IDs such as `ORB-TU-0001`; do not include the internal project name in dataset names, prompts, completions, or task IDs.

Scope limits:
- This product can teach atomic decisions and schema-aware next actions.
- It does not teach an agent to execute a long workflow, respond to real feedback, or prove closure.
- Any synthetic state must be labelled as a hypothetical input state, not an observed environment result.
- Independently validate selected tool IDs and arguments against the supplied tool manifest; audit semantic correctness with a separate reviewer.
- Keep this as an auxiliary dataset, not the primary evidence for agentic SFT.

Before running Invent again, create **one** small focused specification, estimate it, and inspect the target format. Do not combine all 15 capabilities, all domains, and all ten benchmark strata into one overloaded generation request. Generate only one narrow behavior family per dataset and compare its outputs to the task's actual target format.

### Product C — ORBIT executed agent trajectories (primary SFT source)

Purpose: teach actual agent behavior.

This product must be collected by running an untouched base model in the real DHI environment. For each trajectory capture:
1. Exact user request, goal, constraints, and pinned initial state.
2. Exact tool inventory and schemas visible at each step.
3. Model's observable plan/milestone and selected next action.
4. Actual tool call with serialized arguments.
5. Raw tool result or error from real execution.
6. Actual state delta from the environment.
7. Pre-action predicted effects and comparison against observed effects.
8. Plan changes after feedback or failure.
9. Independent tests and postcondition results.
10. Final verified outcome and honest user-facing report.

Never ask Invent or another text generator to invent fields 4–10. The runner and environment supply those facts. The model should not be required to reveal private hidden chain-of-thought; capture concise plans, action rationales, predictions, and observable decisions.

### Product D — ORBIT preference pairs (later DPO source)

Use only after Product C exists. Each chosen/rejected pair must use the same task and equivalent initial state. The chosen trajectory must be better according to independently verified outcome, policy, safety, or efficiency evidence. The rejected trajectory must have a specific defect. Do not ask one generator to invent both sides and declare its own winner.

## 6. Capability coverage and benchmark methodology

The 100-point capability rubric remains the evaluation authority. The task-quality rubric is a separate authoring audit. Never substitute one for the other.

Each task should emphasize one primary capability and at most two secondary capabilities. Balance the overall suite across:
- no-tool restraint and direct answers;
- current-source evidence and freshness;
- hidden capability discovery;
- tool affordance and permission selection;
- invocation/schema correctness;
- dependency-aware multi-tool work;
- long-horizon planning;
- feedback-based recovery and replanning;
- action-effect prediction and invariants;
- verification/closure;
- safety, untrusted outputs, continuity, and honest infeasibility.

Do not assign equal task counts to dimensions merely because the rubric has 15 dimensions. Allocate by the research hypotheses and expected failure modes. A task must have a meaningful, independently checkable success condition.

Benchmark splits must be grouped by template family, environment, tool schema family, and domain—not random row-level splits alone. Keep sealed test prompts, schemas, and grader answers out of training data.

## 7. Updated decision gates

| Gate | Required evidence | Current status |
|---|---|---|
| Invent output-format fit | Prompt/completion pairs are actual agent decisions, not task-spec metadata | **Failed for both current runs** |
| Task-spec validity | Mechanical schema, prompt alignment, uniqueness, and environment checks | Not established; row-level exports unavailable |
| Atomic decision dataset | Valid manifests, concise next-action completions, schema validation, independent audit | Not started |
| Base-model screen | Untouched candidate models run on same frozen cases/harness/budget | Not run |
| Trajectory collection | Model-generated calls plus real observations/state deltas | Not started |
| SFT eligibility | Executed, verified trajectories pass quality and split-integrity gates | Not eligible |
| DPO eligibility | Same-task paired trajectories with independent outcome ranking | Not eligible |

**Immediate decision:** quarantine both Invent task-spec datasets. Do not spend more credits on another 120-row run, do not train from either dataset, and do not treat their scores as model capability scores. First correct the target format and the data-product separation.

## 8. Source references

- Invent paper: https://arxiv.org/abs/2610.01674
- Invent API overview: https://docs.adaptionlabs.ai/adaptive-data/invent-a-dataset/
- Adaptive Data overview: https://docs.adaptionlabs.ai/adaptive-data/overview/
- Internal capability rubric: `DHI_v1/docs/01_CAPABILITY_RUBRIC_AND_SCORECARD.md`
- Internal methods gate: `DHI_v1/docs/04_METHODS_AND_WHEN_TO_USE.md`
- Internal trajectory contract: `DHI_v1/docs/06_DATA_AND_TRAJECTORY_CONTRACT.md`
