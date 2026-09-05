# DHI-v0 — Next Steps

## Immediate objective
Get one clean, interpretable behavioral SFT result from Qwen3-1.7B-Base. Do not add new training methods until this is validated.

## Step 1 — Evaluate Pilot-002 correctly
Load the original Qwen3-1.7B base plus:
`/kaggle/working/DHI_v0_Pilot002_FIXED/adapter_model.safetensors`

Use the exact same 34 validation records and chat-template contract. Compare base vs base+adapter side by side.

## Step 2 — Repair the evaluation protocol
The evaluator must:
- explicitly load the adapter
- generate from assistant turn only
- use fixed decoding settings
- record EOS, output length, repetition, malformed text, and behavioral score
- preserve the exact validation set

## Step 3 — Run a clean Pilot-003
Use the existing 150-example training set first. Do not regenerate it yet.

Reference setup:
- Qwen3-1.7B-Base
- QLoRA 4-bit NF4
- LoRA r=8, alpha=32, dropout=0.05
- target all linear layers initially
- assistant-only loss
- explicit non-thinking response contract
- one epoch
- LR 1e-4
- batch size 1 + gradient accumulation 4
- max sequence length 1024
- no packing
- FP16 compute on T4
- no manual dtype mutation
- validation dataset supplied to trainer

## Step 4 — Evaluate before scaling
Pass criteria are behavioral, not merely matching the reference wording:
- premise integrity improves
- reasoning responses remain coherent
- Hindi generation remains healthy
- no `paque`/token-loop pathology
- no severe repetition
- base capabilities do not visibly regress

## Step 5 — Only then modify data
If Pilot-003 is healthy but weak, improve dataset diversity/coverage. If it is pathological, debug the training/evaluation pipeline before changing the dataset.

## Do not do yet
- DPO
- full fine-tuning
- model merging
- Skill Genes
- large data expansion
- architecture changes

The next concrete run is **Pilot-003 clean controlled SFT**, but only after the existing Pilot-002 adapter has been evaluated correctly.
