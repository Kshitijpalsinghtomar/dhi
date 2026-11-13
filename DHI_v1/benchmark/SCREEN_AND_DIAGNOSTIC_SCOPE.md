# DHI-v1 Base Screen and Diagnostic Scope v1

**Decision date:** 2026-11-02  
**Programme:** DHI-v1 / ORBIT  
**Status:** scope allocation resolved; task instances and execution protocol remain unfrozen  
**Authority:** this file resolves the former 120-vs-240 conflict across the model-selection and benchmark-protocol documents.

## 1. Decision

The 120-task base-model screen is the first half of one 240-task, ten-stratum diagnostic panel. The two counts are not competing suite sizes and do not represent two unrelated benchmark designs.

- **Stage A — base-model screen:** 120 tasks, 12 tasks from each of the ten strata below.
- **Stage B — held-out confirmation/diagnostic extension:** 120 additional tasks, also 12 from each stratum.
- **Complete DHI-v1 diagnostic panel:** 240 unique tasks, 24 per stratum (Stage A + Stage B).

The Stage A task IDs are a strict subset of the Stage B-complete 240-task panel. Stage B contains no rephrased duplicates or reused task templates from Stage A. Stage A supports initial model screening and development decisions; Stage B is held back until model/interface choices are fixed and is used to test whether the Stage A choice generalizes.

This supersedes the earlier six-groups ×20 allocation in the model-selection document and the unresolved independent interpretation of the 240-task plan in the benchmark-protocol document. Those earlier specifications remain part of the decision history, not active allocations.

## 2. Ten strata and allocation

| # | Stratum | Stage A screen | Stage B holdout | Total |
|---:|---|---:|---:|---:|
| 1 | No-tool-needed tasks and direct answers | 12 | 12 | 24 |
| 2 | Current/time-sensitive facts requiring verification | 12 | 12 | 24 |
| 3 | Tool discovery when a required capability is absent from the visible inventory | 12 | 12 | 24 |
| 4 | Tool selection among relevant, irrelevant, misleading, and decoy tools | 12 | 12 | 24 |
| 5 | Schema/argument correctness and precondition handling | 12 | 12 | 24 |
| 6 | Multi-tool workflows with dependencies and state changes | 12 | 12 | 24 |
| 7 | Long-horizon workflows with 8–30 actions and checkpoints | 12 | 12 | 24 |
| 8 | Broken/unavailable tools, malformed responses, rate limits, and replanning | 12 | 12 | 24 |
| 9 | Action-effect forecasts, side-effect prediction, and verified goal closure | 12 | 12 | 24 |
| 10 | Permission boundaries, untrusted tool outputs, context continuity, and infeasible tasks | 12 | 12 | 24 |
| **Total** | | **120** | **120** | **240** |

All ten strata appear in the first screen. The earlier six-group allocation bundled multi-tool work with long-horizon behaviour and bundled recovery with closure, while giving no dedicated allocation to action-effect prediction or the safety/permission and untrusted-output dimensions. Ten balanced strata make these capabilities separately diagnosable without increasing the initial screen beyond 120 tasks.

## 3. Evaluation stages

### Stage A — base-model screen (120)

- Run each accessible required base candidate on the identical 120 Stage A tasks, tool manifests, environment states, permissions, prompts, decoding policy, retry policy, and budget.
- Primary planned candidates remain Qwen/Qwen3.6-35B-A3B and GPT-OSS-20B. Gemma 4 31B is included when multimodal/UI evaluation is in scope and the same task modality can be provided fairly.
- Preserve model-specific native tool formatting, but verify equivalent semantics and action opportunities. A broken adapter is an integration failure, not proof of weak model capability.
- Report overall results, all ten stratum results, hard safety gates, paired task differences, confidence intervals, latency, tokens, tool calls, and cost per successful task.
- Stage A may inform model and interface selection. Do not call a winner on a small subgroup alone. A 12-task stratum is screening resolution, not a precise estimate of that stratum's population performance.

### Stage B — held-out confirmation (120 additional)

- Stage B remains hidden from model developers and must not be used for prompt, adapter, tool-manifest, or model selection changes before the confirmation run.
- After Stage A has fixed the candidate/interface choices, run the selected model and at least its mandatory challenger on the same Stage B tasks under matched conditions.
- Do not use Stage B to tune the system. If a protocol or implementation change is required after inspecting Stage B, label the result exploratory and create a new holdout before confirmatory claims.
- Report Stage A and Stage B separately, then report the combined 240-task panel with uncertainty. A candidate can only support a broader model-selection claim if the independent Stage B result corroborates the Stage A result and all hard gates pass.

### Repeated trials

Predeclare which tasks are stochastic and the number/seeds of repeated trials before running any model. Keep all candidate trial counts and seeds matched. Do not selectively rerun only failures or retain only the best run. Report pass@1 and pass^k/reliability where appropriate.

## 4. Task validity, independence and splits

1. Task instances must be authored or sourced with explicit goal, required capabilities, visible tools, hidden/discoverable tools where relevant, hard constraints, executable postconditions, grader, environment state, and failure conditions.
2. Split Stage A and Stage B by task family/template, repository or application, tool-schema family, dependency pattern, horizon, and environment-state variant—not random wording alone.
3. Stage B must use distinct underlying task structures, not paraphrases, prompt variants, or alternate names for Stage A tasks.
4. Tool names and schemas should be varied across tasks. A sealed subset must contain unseen names/schemas and combinations, not merely renamed copies of a familiar single-step function.
5. Include domains across software repositories, terminal, browser, documents, spreadsheets, APIs, data analysis, project management, and simulated communication/calendar systems as executable support becomes available.
6. Every write action must run in a sandbox with explicit permissions and state verification.
7. The existing 12-case hand-authored development pilot is excluded from both Stage A and Stage B. It remains an integration/harness smoke test, not part of the 240-task panel and not training data.
8. Public benchmark items may be used for auxiliary comparison only when licenses and versions are checked; do not place public benchmark items or near-duplicates into the private holdout.

## 5. Freeze gates — not yet passed

This decision freezes only the suite relationship, strata and allocation. It does **not** freeze task instances, prompts, tool inventory, model revisions, seeds, graders, environment images, cost caps or statistical thresholds.

Do not start a comparative model screen until:

- the 120/240 task IDs and Stage A/B family split are materialized and hashed;
- the environment supports each scored capability, or unsupported items are explicitly excluded from the executable pilot with a documented reason;
- graders and postconditions are mechanically tested where possible and independently reviewed where semantic;
- native model tool-call templates and adapter parity are verified;
- a validation/development route is distinct from Stage B;
- inference access and equal budgets are available for the required candidates.

The current 12-case file-workspace pilot does not yet implement all ten strata. In particular, current-source verification, broad external tool discovery/permissioned operation, long-horizon persistence, and general cross-application execution need additional environments. Do not mark these as model failures while the harness cannot execute them.

## 6. Non-negotiable scoring rules

- Primary outcome: mandatory postconditions satisfied in the actual environment.
- Score process diagnostics separately: no-tool restraint, discovery recall, selection, invocation validity, plan correctness, replanning, prediction accuracy, false closure, safety, transfer, and efficiency.
- Use environment state, tests, schemas, permissions and event traces; an LLM judge cannot be the sole grader.
- Report failures, invalid tasks, unavailable tools, unsafe actions, and incomplete runs; never silently drop them.
- Safety/authorization, truthful execution reporting, verified goal closure, data integrity, and evaluation integrity are non-compensable gates.
- A 100/100 result refers only to the frozen task panel and its stated conditions, not universal real-world intelligence.

## 7. Immediate implementation sequence

1. Keep the existing 12-case suite as a development-only integration smoke test.
2. Use [the task-record schema](task_manifest.schema.json) and [task register](task_manifest.json) as the machine-readable contract for all ten strata and Stage A/B metadata.
3. Use the [environment coverage audit](ENVIRONMENT_COVERAGE_MATRIX.md) to gate task authoring; unsupported capabilities remain harness gaps rather than fake model failures.
4. Build and independently review the Stage A/B tasks in separate files/partitions; hash and commit the manifest before any model run.
5. Resolve comparable base inference access for Qwen3.6 and GPT-OSS, then run Stage A.
6. Only after model/interface selection, run Stage B as the held-out confirmation set.

No task cases were generated or run as part of this scope decision.

## 8. Plugin-native execution layer — 2026-11-03

The local file-workspace harness coverage above remains accurate for that harness. ORBIT now adds a separate plugin-native execution profile using real connected GitHub, TinyFish and Firecrawl tools. The plugin contracts and usage boundaries are pinned in [PLUGIN_NATIVE_EXECUTION_PROFILE.md](PLUGIN_NATIVE_EXECUTION_PROFILE.md) and [plugin_tool_registry.json](fixtures/plugin_ecology/plugin_tool_registry.json).

Ten initial Stage A task instances (one per stratum) are now materialized in [task_manifest.json](task_manifest.json). S02 current-source verification is supported through TinyFish; S03 free capability discovery is supported through Firecrawl; GitHub supports exact file reads, sandbox-branch writes, state verification, and a real 404 recovery. S07 checkpoint/resume and S09 pre-action prediction capture remain partial. All twelve task records are ready for model validation, not validated. Stage B remains unmaterialized and sealed.

The synthetic plugin fixture includes exact source files, current-source and tool-discovery snapshots, an untrusted issue body, a persistent resume checkpoint, and verified reference reports. No DHI model run or capability score was produced. A credit-consuming Firecrawl provider execution was not run.

## 9. Plugin-native task authoring increment — 2026-11-03

The plugin-native Stage A register now contains **20 task instances** across the ten strata, with 20 distinct task-family records. Distribution: S01=2, S02=2, S03=3, S04=2, S05=2, S06=2, S07=1, S08=2, S09=2, S10=2. The 120-task Stage A target and sealed 120-task Stage B target are unchanged.

New task families cover direct-answer restraint, research-provider discovery, GitHub commit-diff selection, TinyFish multi-URL argument correctness, Node/Python cross-source synthesis, Firecrawl degraded-discovery recovery, GitHub branch-effect prediction, and untrusted paid-action instructions.

A Node/Python comparison report was created on the dedicated GitHub branch, fetched back, and diff-checked as the only new path from its baseline. The task manifest passed the committed JSON Schema and cross-record uniqueness/count checks with zero schema errors. All 20 tasks remain ready for validation, not validated; no model execution or capability score is claimed. Stage B is still empty and sealed.

## 10. Third plugin-native authoring increment — 2026-11-03

The plugin-native Stage A register now has **22/120** task instances. A third independent S02 task adds Go release-history verification; a third S08 task adds live TinyFish argument-schema recovery, 404 interpretation, and search-based recovery to the canonical source. Both task families are independent from the earlier Node.js/Python currentness and GitHub/Firecrawl recovery cases.

The Go source snapshot and recovery sequence are pinned under `fixtures/plugin_ecology/external_snapshots/`. All records remain ready_for_validation; the Stage B holdout remains empty and sealed. No model run or benchmark score is claimed.

## 11. Current task-panel integrity checkpoint — 2026-11-03

The active plugin-native task manifest contains **30/120 Stage A tasks**, distributed S01=2, S02=3, S03=4, S04=3, S05=4, S06=4, S07=2, S08=3, S09=3 and S10=2. Stage B has **0/120** records and remains sealed.

A cross-record validator and 14 regression tests are committed. It verifies schema compliance, task/family registration, deterministic task and family hashes, exact tool registry membership/digest, task-ID numbering, referenced evidence paths, cross-stage split isolation, per-stratum quotas and the Stage B release boundary. The manifest schema now requires `task_instance_sha256`.

An independent static inspection of the GitHub branch at commit `3d57cc876dcd3f1f82c9d3ff884665de52c7f290` recomputed all 30 task hashes and family fingerprints, confirmed every referenced evidence file exists, confirmed all task tool IDs are present and allowed in the pinned registry, and returned zero structural integrity errors.

Python validator/pytest execution remains outstanding. GitHub Actions run `41594301494` failed before runner allocation; its job reported no runner and no steps. This is not a passing test result and is not evidence of a code failure.
