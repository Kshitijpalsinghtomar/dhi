# DHI-v0 — Decisions, Work History & Things Not To Repeat

## Current state

DHI-v0 is being developed as a compact reasoning model experiment around Qwen3-1.7B-Base, with Hindi/Hinglish/Indic competence and explicit reasoning behaviors. Pilot-002 was the first controlled LoRA/QLoRA behavioral SFT attempt documented here.

## Work completed

### Validation set
- Created and restored a 34-record validation set.
- Validation records use a conversational user/assistant schema with metadata.
- Example behavior: `premise_integrity`.

### Pilot-002 training
- 150 training records.
- Qwen3-1.7B-Base.
- 4-bit NF4 quantization.
- LoRA applied to attention and MLP projection modules.
- 3 epochs, LR 2e-4, batch size 1, gradient accumulation 4.
- DDP across two T4s.
- Produced final and intermediate LoRA adapters.

### Investigation after Pilot-002
- Base tokenizer was initially missing from a copied student output directory; matching tokenizer was located in the Qwen3-1.7B base directory.
- Direct base inference produced malformed/repetitive output.
- Memory problems occurred when trying to load the full 1.7B model in an already occupied single T4 process.
- Two-GPU loading was subsequently used successfully, but the model was placed entirely on GPU 0 because that was the selected device map; this is not evidence that two-GPU inference was actually required.
- Pilot-002 output inspection confirmed the trained artifact is a LoRA adapter, not a full merged model.
- An attempted adapter load failed because the environment had an incompatible `torchao` version; a later environment check showed `torch 2.10.0+cu128`, `torchao 0.18.0`, `peft 0.19.1`, `transformers 5.0.0`, which passed the compatibility check.
- A subsequent evaluation cell failed because `validation_records` was not present; the validation data was restored from `validation.jsonl`.

## Critical lesson
The experiment repeatedly mixed three separate things:
1. base-model integrity,
2. adapter/training integrity,
3. evaluation/inference integrity.

They must be isolated. A base-only generation is not a Pilot-002 test. An adapter-loading failure is not a dataset failure. A tokenizer/environment failure is not a model-behavior result.

## Specific mistakes to avoid

- Do not repeatedly audit artifacts without a decision they enable.
- Do not call a base-only generation a trained-model evaluation.
- Do not infer dataset failure from malformed output until adapter loading, tokenizer, prompt template, decoding, and environment are verified.
- Do not repeatedly change multiple pipeline variables in one experiment.
- Do not manually mutate trainable parameter dtype with `.data` as a workaround in the next run.
- Do not use an aggressive training setup on a tiny behavioral dataset without an immediate held-out evaluation.
- Do not let the validation set disappear from notebook state; load it explicitly in every standalone evaluation cell.
- Do not assume two GPUs are being used merely because two GPUs are available.
- Do not overwrite or delete the base model while trying to create a student checkpoint.
- Do not regenerate the dataset merely because the first evaluation pipeline was broken.

## Decision record

### Decision A — Keep the dataset
The current evidence is insufficient to blame the 150 examples. Keep them as the controlled training corpus until a correctly evaluated reproduction demonstrates a data problem.

### Decision B — Evaluate Pilot-002 before replacing it
The existing adapter is valuable experimental evidence. First run a correct base-vs-adapter comparison.

### Decision C — Simplify Pilot-003
Reduce moving parts. One controlled SFT run should establish whether the training method can produce a healthy behavioral shift.

### Decision D — Validation is mandatory
Future training runs should expose held-out validation during training/evaluation, not only after the fact.

## Current next experiment
Pilot-003 clean controlled SFT, following `docs/NEXT_STEPS.md`, after correct Pilot-002 adapter evaluation.
