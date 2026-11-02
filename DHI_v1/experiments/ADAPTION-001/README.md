# ADAPTION-001 — Live Adaption model and dataset audit

**Date:** 2026-11-02  
**Programme:** DHI-v1 / ORBIT  
**Type:** read-only platform capability and training-eligibility audit  
**Status:** completed; no training or data-generation job launched

## Question

What does the connected Adaption account actually support for the DHI-v1 candidate models, and is the current 300-row ORBIT collaboration dataset ready for a first SFT run?

## Procedure

1. Queried the live Adaption training-model registry using `list_training_models`.
2. Queried the authenticated Adaption dataset inventory using `list_datasets(limit=100)`.
3. Inspected the exact dataset record and its quality-evaluation result for the 300-row ORBIT collaboration-behaviour pilot.
4. Queried the AutoScientist history to distinguish earlier DHI-v0/experimental runs from DHI-v1 results.
5. Requested hyperparameter recommendations (not training runs) for the 300-row candidate on Qwen3.6-35B-A3B, GPT-OSS-20B, and Gemma 4 31B.
6. Did not call `create_autoscientist_run`, `generate_dataset`, augmentation, translation, or adaptation. No Adaption credits were spent.

## Observations

### Live training registry

The currently returned registry contains the three DHI-v1 candidates:

- `Qwen/Qwen3.6-35B-A3B` — SFT and DPO; LoRA; reasoning flag enabled; 262,144 context.
- `openai/gpt-oss-20b` — SFT and DPO; LoRA; reasoning flag enabled; 131,072 context.
- `google/gemma-4-31B-it` — SFT and DPO; LoRA/full; reasoning flag enabled; 262,144 context.

This proves current **training-registry** support only. It is not a model-quality result or evidence that the same IDs are available on the hosted Responses inference endpoint.

### Current ORBIT collaboration dataset

- Dataset: `ORBIT Collaboration Behaviour — Instruction Pilot 300`
- ID: `169af31f-06e0-4a48-84ab-b84c9f9ce924`
- Status: `succeeded` in Adaption's dataset-processing workflow.
- Source: Invent; row count: 300.
- Adaption evaluation: grade A, score 9.4, with 100 rows represented in the evaluation summary. This is a dataset-text quality score, not a DHI task-success or agent-capability score.
- Available columns include original/invented prompts and completions, enhanced variants, and reasoning-trace fields. The dataset record does not establish executed tool traces, real tool responses, or independently verified environment postconditions.

The live workspace's existing triage record says 98 visible complete pairs were partially reviewed: 25 candidate, 53 revise, and 20 reject; 202 rows remain unreviewed. That triage remains partial/model-assisted and is not independent full adjudication.

**Conclusion:** the 300-row dataset is not approved for DHI-v1 training. Its processing status and grade do not override the provenance and review gates.

### Live model-specific recommendation results on the 300-row dataset

The recommender is not a training run and did not spend credits.

| Candidate | Result |
|---|---|
| Qwen/Qwen3.6-35B-A3B | Rejected: fewer than 10,000 effective training rows required |
| openai/gpt-oss-20b | Returned a LoRA recommendation: 1 epoch, batch size max, learning rate 5e-5, rank 4, alpha 8, q_proj/v_proj, linear schedule, warmup 0.03 |
| google/gemma-4-31B-it | Rejected: fewer than 10,000 effective training rows required |

The Qwen and Gemma validation messages both state the same 10,000-effective-row minimum (base plus augmentation). The GPT-OSS recipe is only a platform recommendation. It does not make the current data valid, and it is not an authorization to train.

### Historical AutoScientist runs

The account history returned seven previous runs, predominantly Qwen3.5-4B runs on earlier DHI-v0/experimental datasets. The largest displayed historical DPO result was 0.4609 against a 0.99 target; earlier SFT scores included 0.1229, 0.2135, 0.3000, 0.3085, and 0.3211 on different datasets/configurations.

These metrics are run-specific AutoScientist results, not an independent common benchmark. None is a DHI-v1 capability result, and none validates the current ORBIT dataset.

## What the model is for

DHI-v1/ORBIT is intended to make agentic competence a learned model capability, not merely a prompt or external router. The model should learn to:

- extract goals, constraints, and final postconditions;
- recognize when tools or fresh evidence are needed—and when they are not;
- discover tools beyond the immediately visible inventory;
- compare tool affordances, schemas, preconditions, permissions, costs, and side effects;
- plan and sequence dependent actions;
- predict relevant action effects, observe actual outcomes, and replan;
- preserve task state across long workflows;
- verify final environment state before claiming completion.

Adaption's role is to provide supported foundation-model backbones, dataset processing, SFT/DPO baselines, and training recommendations/runs. It does not provide custom architecture graphs, custom latent predictive losses, or the custom environment-grounded RL loop. Those remain code/research work in DHI and the separate GBA track.

## Decision and next work

1. Keep Qwen3.6-35B-A3B as the planned primary and GPT-OSS-20B as the mandatory challenger; keep Gemma 4 31B as a multimodal challenger. Registry support is not a ranking.
2. Do not train the current 300-row ORBIT Invent dataset. Complete provenance review only if it remains useful as auxiliary behaviour data; it cannot substitute for real executed trajectories.
3. Build the first valid SFT corpus from actual executions in the deterministic DHI environment: raw tool responses, pre-action predictions, actual state deltas, and independently checked postconditions.
4. Reconcile the 120-task base-screen versus 240-task diagnostic-scope discrepancy before freezing the evaluation set.
5. Obtain model-comparable untouched-base inference access for Qwen3.6 and GPT-OSS before choosing a winner or fine-tuning. The earlier hosted Responses catalogue exposed Gemma 4 31B but not the other two; do not silently substitute Gemma or treat training-registry access as inference access.
6. Use Adaption estimates before any dataset generation/adaptation/augmentation launch. The connected `create_autoscientist_run` action launches a credit-consuming training run; this audit did not launch one.

## Evidence boundary

- Live training registry: observed platform metadata.
- Dataset status, columns, and quality summary: observed platform metadata.
- Model-specific row minimum and GPT-OSS recipe: observed recommender responses.
- Model capability: not tested by this audit.
- DHI-v1 training: not launched.
- Credits spent in this audit: zero.
