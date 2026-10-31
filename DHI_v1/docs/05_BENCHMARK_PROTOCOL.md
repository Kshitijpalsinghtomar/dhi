# DHI-v1 Benchmark and Evaluation Protocol

**Version:** 1.0  
**Date:** 2026-10-31  
**Status:** Proposed; freeze exact instances, execution harness, graders, and thresholds before confirmatory runs.

## 1. What the benchmark must answer

The benchmark should tell us:
- Does DHI know when a tool is needed?
- Does it look beyond the tools immediately shown to it?
- Can it discover a suitable app/plugin/API from a dynamic catalogue?
- Can it select the right tool among many decoys or partial matches?
- Can it reason about tool schemas, permissions, preconditions, freshness, and side effects?
- Can it plan and execute multi-step workflows across several tools?
- Does it replan when an action fails or the environment changes?
- Does it predict the relevant effects of an action?
- Does it verify the actual final state instead of merely reporting success?
- Does it preserve task state over long horizons?
- Does it remain efficient and safe?

A benchmark reporting only a single end-to-end win rate is not enough. We need diagnostics that locate the source of failure.

## 2. External benchmarks to use

### Agent Planning Benchmark (APB) — priority diagnostic

- Paper: arXiv:2606.04874, posted 2026-06-05; listed in Findings of EMNLP 2026.
- 4,209 multimodal cases across 22 domains and five settings.
- Covers holistic planning, feedback-conditioned stepwise planning, and robustness with extraneous tools, broken tools, and unsolvable tasks.
- Directly relevant to the user's complaint about poor tool selection, shallow planning, and inability to recognize infeasible tasks.
- Use the authors' official code and task definitions: https://github.com/Mikivishy/AgentPlanningBenchmark

APB is a diagnostic benchmark, not a substitute for executing full workflows.

### τ-bench — stateful tool-agent-user interaction

- ICLR 2025.
- Covers retail and airline domains with API tools and domain policies.
- Evaluates final database state against an annotated goal state and uses pass^k to measure repeated-trial reliability.
- Useful for realistic conversations, policy constraints, stateful APIs, and consistency across trials.
- Paper: https://proceedings.iclr.cc/paper_files/paper/2025/hash/1b126cc38b8638e07bef37e7b2bb72bf-Abstract-Conference.html

### OSWorld — real computer use

- NeurIPS 2024 Datasets and Benchmarks Track.
- Evaluates multimodal agents in real computer environments and open-ended tasks.
- Use after the software/API agent baseline is stable and DHI begins UI/screenshot interaction.
- Paper: https://proceedings.neurips.cc/paper_files/paper/2024/hash/5d413e48f84dc61244b6be550f1cd8f5-Abstract-Datasets_and_Benchmarks_Track.html

### BFCL v4 — function/tool call diagnostics

- Berkeley Function Calling Leaderboard v4 includes single-turn, multi-turn, parallel, and agentic function-calling categories.
- Useful for schema and call correctness.
- Do not optimize to the aggregate score alone. Epoch AI's 2026-09-10 audit reported possible defects in 24 of 50 sampled tasks (48%); inspect task quality and use it as an auxiliary diagnostic.
- Official leaderboard: https://gorilla.cs.berkeley.edu/leaderboard

### AgentBench — broad interactive environments

- ICLR 2024.
- Eight distinct environments and analysis of long-term reasoning, decision making, and instruction following.
- Useful as a broad historical comparison, but newer planning/tool tests should supplement it.
- Paper: https://proceedings.iclr.cc/paper_files/paper/2024/hash/e9df36b21ff4ee211a8b71ee8b7e9f57-Abstract-Conference.html

### Coding benchmark caution

- OpenAI's 2026-02-23 analysis says SWE-bench Verified is increasingly contaminated and recommends against treating it as a frontier coding capability signal.
- OpenAI's 2026-07-08 audit of SWE-bench Pro reported task-quality issues in a significant portion of its audited set.
- Do not base DHI's model selection or public claim on a single public software benchmark. Use private, held-out repository tasks and independently checked task validity.
- References: https://openai.com/index/why-we-no-longer-evaluate-swe-bench-verified/ and https://openai.com/index/separating-signal-from-noise-coding-evaluations/

## 3. Internal DHI diagnostic suite

Build an initial **240-task** diagnostic suite, divided into ten strata of 24 tasks each:

1. No-tool-needed tasks and direct answers.
2. Current/time-sensitive facts requiring verification.
3. Tool discovery when a required capability is absent from the visible inventory.
4. Tool selection among relevant, irrelevant, misleading, and decoy tools.
5. Schema/argument correctness and precondition handling.
6. Multi-tool workflows with dependencies and state changes.
7. Long-horizon workflows with 8–30 actions and checkpoints.
8. Broken/unavailable tools, malformed responses, rate limits, and replanning.
9. Action-effect forecasts, side-effect prediction, and verified goal closure.
10. Permission boundaries, untrusted tool outputs, context continuity, and infeasible tasks.

Distribute tasks across software repositories, terminal, browser, documents, spreadsheets, APIs, data analysis, project management, and simulated communication/calendar systems. Use sandboxed services for all write actions.

The 240-task suite is a pilot diagnostic, not a statistically definitive final benchmark. Expand to a separate confirmatory test after reviewing the pilot failures.

## 4. Generalization and contamination controls

Split by more than wording:
- repositories/projects;
- app/tool domains;
- tool schema families;
- task templates;
- dependency structures;
- task horizon;
- failure modes;
- environment state variants.

Hold out entire repositories or tool families where practical. Do not put a near-duplicate task template in train and test. Rename tools and change schemas at test time to assess affordance generalization. Keep a sealed set of unseen tools and task compositions.

Use public APB/τ-bench/OSWorld/BFCL for comparison, but never let public benchmark rows contaminate the internal confirmatory test.

## 5. Evaluation procedure

For every candidate model:

1. Freeze model revision, tokenizer, system interface, tool manifest, prompts, permissions, environment version, and decoding settings.
2. Run the same tasks and tool availability conditions.
3. Save full action and state traces.
4. Verify results against the external environment.
5. Recompute all metrics from raw logs.
6. Use paired task comparisons against the untouched base.
7. Repeat stochastic tasks with predeclared seeds/trials; report pass@1 and pass^k or equivalent.
8. Provide confidence intervals and per-stratum results.
9. Have an independent evaluator inspect a blinded sample.
10. Preserve failed, unsafe, invalid, and incomplete runs.

Do not tune on the sealed test set. Use a development set for iteration and a validation set for model selection.

## 6. Primary metrics

| Metric | Definition |
|---|---|
| End-to-end task success | All mandatory postconditions hold in the environment. |
| Tool discovery recall | Fraction of tasks requiring discovery where the model finds a suitable available capability. |
| Tool-use precision | Fraction of tool calls that were justified and relevant. |
| No-tool restraint | Correctly avoids calls when existing knowledge is enough and no external action is required. |
| Tool selection accuracy | Selected tool matches task affordances and constraints. |
| Invocation validity | Correct schema, arguments, types, and preconditions. |
| Plan correctness | Dependencies, constraints, and milestones correctly represented. |
| Horizon success | Task success by action horizon; report degradation from short to long tasks. |
| Replanning recovery | Success after a deliberately introduced failure/change. |
| Prediction accuracy | Correctness of pre-action forecast against actual relevant state changes. |
| False closure rate | Fraction of tasks marked complete while mandatory postconditions are false/unverified. |
| Regression rate | Previously passing requirements broken by an action. |
| Context continuity | Retention of goal, constraints, completed steps, and unresolved work after interruption/resume. |
| Cost/efficiency | Tool calls, model tokens, latency, retries, and monetary cost per successful task. |
| Safety | Unauthorized side effects, privacy violations, unsafe calls, and trust-boundary violations. |

## 7. Model comparison

Compare at minimum:
- Qwen3.6-35B-A3B base.
- GPT-OSS-20B base.
- Gemma 4 31B base when multimodal UI is in scope.
- Selected base plus DHI-v1 SFT.
- Selected base plus forecast-supervised SFT.
- Selected base plus forecast-and-closure training.

Keep model tools, external execution harness, and budget matched. Report any differences in native tool protocol or model-specific templates.

The existing Qwen3.5-4B DPO/SFT outcomes are historical references, not a comparable DHI-v1 baseline.

## 8. Statistical and release gates

- Report paired confidence intervals for task success differences.
- Report subgroup results for short/long horizon, known/unseen tools, direct-answer/no-tool cases, and failure recovery.
- Use exact binomial intervals for hard safety failures where appropriate.
- For repeated interactive tasks, report pass^k/reliability and variance, not a single lucky run.
- A model advances only when the preregistered primary metric passes, no safety hard gate fails, and no invalidity/leakage remains.
- A 100/100 score is a stretch goal on the frozen internal challenge set; report benchmark scope and uncertainty.

## 9. Benchmark integrity

External public scores can be stale, flawed, contaminated, or measured under different harnesses. Verify benchmark revision, task validity, licenses, and evaluator. The DHI internal suite must include its own task validity audit and executable outcome graders.

No LLM judge alone can establish task success. Use environment state, tests, schemas, and human review for semantic judgments.


## 2026-10-31 — Deepnote static integrity validation of the development pilot

The `DHI_v1/benchmark/pilot_cases.json` file at repository HEAD `0753bcae9d0937dda187bc6033a0dce6e9d65c5d` was parsed in the connected Deepnote CPU workspace.

Checks passed:
- 12 cases with unique case IDs and explicit postconditions.
- 8 common `file_workspace` pilot cases.
- 1 Adaption catalogue-only case.
- 3 cases explicitly marked `not_executable_in_file_workspace` (external-source, external-tool-registry, and cross-session runtime scope).
- Both answer-regex patterns compile.
- The no-tool grader accepts exactly `4` and rejects `14`.
- The hidden-search grader distinguishes line 1 from line 2.
- Both write cases restrict changed paths to `README.md`.

This is a static suite/grader-integrity check only. It did not execute the agent runner, any model, tools, or environment tasks. It is not a pytest pass and does not establish model capability. The full focused Python test suite remains unverified; do not report the pilot as a completed model benchmark.
