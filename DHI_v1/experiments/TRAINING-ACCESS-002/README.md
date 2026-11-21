# TRAINING-ACCESS-002 — Adaption training-readiness audit

**Date:** 2026-11-03  
**Status:** hold — dataset lineage and cost gate  
**Evidence:** read-only model registry, dataset metadata/evaluations, run history and recommender calls. No training or data-generation job was launched.

## Finding

Adaption currently lists Qwen3.6-35B-A3B, GPT-OSS-20B and Gemma 4 31B as trainable through supported SFT/DPO methods. Qwen3.6 is LoRA-only in the returned registry and its recommender requires at least **10,000 effective rows**. A Qwen3.6 LoRA configuration was returned for the existing 10,000-row dataset. This confirms that the platform can propose a configuration; it does not certify the dataset.

## Data decisions

- **ORBIT 300-row collaboration pilot (169af31f…) — quarantined.** Adaption reports A / 9.4 from a 100-row sample, but prompt/completion columns are null in dataset metadata. A prior partial row audit found only 98 complete visible pairs among the first 100 slots. The score is text-quality metadata, not an agentic score.
- **120-row task-spec Invent dataset (be05757d…) — quarantined.** Grade C / 6.6; completion quality 5.03 and 2.2nd percentile. A task contract generated as completion text is not an executed trajectory.
- **300-row intent-arbitration pilot (c1f4df14…) — not ready.** Grade A / 9.0 on 100 sampled rows, but explicit prompt/completion mapping is null and it is too small for Qwen3.6.
- **10K-row augmented intent dataset (843888da…) — evaluation-lineage hold.** Metadata says 10,000 rows with rephrased_prompt and enhanced_completion, but its evaluation input path and config source point to the separate 300-row c1f4df14… dataset and its 100-row sample. Do not assign that A grade to the 10K export before reconciling lineage and auditing actual rows.

The 10K dataset is private on Hugging Face. The connected Hub metadata/README action did not expose row preview or dataset-structure operations in its available schema during this audit. No unseen rows are assumed to be correct.

## Recommender result — configuration only

For the 10K dataset and Qwen/Qwen3.6-35B-A3B, Adaption returned a LoRA suggestion:

n_epochs=1, batch=max, lr=1e-4, r=8, alpha=8, dropout=0, modules=q_proj,v_proj, cosine, warmup=0.1, weight_decay=0, train_on_inputs=false.

This is not an executed run, cost quote, validation result, or training approval.

## Historical run boundary

The latest listed 12,116-row Qwen3.5-4B DPO/alignment run 5f16632f… completed five iterations but reached best_win_rate **0.4609** against a 0.99 target. It is not launch or release evidence.

## Decision

No training, dataset-generation, or augmentation jobs are authorized from this audit. The next step is to retrieve and inspect the 10K export itself, reconcile evaluation lineage, and only then ask Adaption for cost/compute details. Keep actual ORBIT tool-execution traces separate from intent-arbitration prompt/completion data.

Structured details: [manifest.json](manifest.json).
