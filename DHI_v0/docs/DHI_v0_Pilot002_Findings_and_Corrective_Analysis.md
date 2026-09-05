# DHI-v0 — Pilot-002 Findings & Corrective Analysis

Date: 2026-09-05

## Executive conclusion

Pilot-002 is **not sufficient evidence to reject the DHI dataset**. The strongest established issue is the experimental/evaluation pipeline, not the dataset itself.

Pilot-002 produced a LoRA adapter (`adapter_model.safetensors`). A later student-generation test loaded only the base checkpoint directory, so that test did not measure the trained Pilot-002 model. The earlier `paque`, `.RemoveEmptyEntries`, and repetitive outputs therefore cannot be used as a clean verdict on Pilot-002.

The actual Pilot-002 training log shows stable finite training and a falling loss: approximately 1.12 at step 1 to 0.57 at step 57, with final mean token accuracy about 0.837. This is evidence that the optimization run itself completed rather than immediately collapsing to NaN.

## What is established

### Base/model
- Qwen3-1.7B-Base remains the intended starting model.
- The local model has the expected Qwen3 architecture and approximately 1.72B parameters.
- The matching tokenizer is in `/kaggle/working/dhi_student/qwen3-1.7b-base`.
- The Qwen3 chat template is present.

### Pilot-002 artifacts
- Final adapter: `DHI_v0_Pilot002_FIXED/adapter_model.safetensors`
- Checkpoints: `checkpoint-19`, `checkpoint-38`, `checkpoint-57`
- Each checkpoint contains `adapter_model.safetensors` and `adapter_config.json`.

### Dataset
- 150 training records.
- 34 validation records.
- Conversational `messages` schema.
- Human-defined behavioral seeds/blueprints remain the source of the reasoning objective.

## Pilot-002 pipeline issues

1. The later evaluation omitted the LoRA adapter in one of the student-model tests. This invalidated the interpretation of those outputs as Pilot-002 behavior.

2. The training script did not pass the 34-record validation set into `SFTTrainer` as `eval_dataset`, so validation was not integrated into training monitoring.

3. The validation split does not provide complete coverage of all DHI behaviors; independent_judgment is absent from the reported validation set.

4. The training stack was unnecessarily complicated for a 1.7B pilot: 4-bit loading + LoRA + DDP + FP16 + manual FP32 mutation of trainable tensors. The manual dtype mutation should be removed from the next controlled run.

5. Qwen3 thinking/non-thinking mode was not made an explicit part of the training contract. Training and inference need the same reasoning-mode contract.

6. Assistant-only loss was not explicitly configured. For behavioral SFT, the target of optimization should be the assistant response rather than reproducing user tokens.

7. The Pilot-002 learning rate (`2e-4`) and three full epochs are aggressive for only 150 highly targeted examples. They are not intrinsically invalid, but they are poor defaults for a minimal behavioral-shift experiment.

## Corrected experimental method

Use one controlled question at a time:

> Can a small, carefully controlled behavioral SFT update move Qwen3-1.7B-Base toward DHI behaviors while preserving its native capability and language behavior?

Recommended near-term protocol:

- immutable Qwen3-1.7B base
- QLoRA/LoRA
- NF4 quantization
- `prepare_model_for_kbit_training()`
- LoRA rank 8, alpha 32, dropout 0.05
- `all-linear` targets as the initial reference configuration
- assistant-only loss where supported by the installed TRL/chat-template path
- explicit Qwen3 `/no_think` or equivalent non-thinking training contract for this first compact-response experiment
- `eval_dataset` supplied to trainer
- one process / one T4 for the pilot if it fits
- FP16 compute on T4
- no manual `.data.float()` mutation
- LR `1e-4` as the initial reference
- one epoch first, then evaluate before considering a second
- no packing initially
- max sequence length around 1024 for this pilot

## Dataset verdict

Do **not** discard or regenerate the 150-example dataset yet. The current evidence does not show that the dataset caused the pathological generation.

The next dataset work should focus on:

- behavioral diversity rather than paraphrase count
- answer diversity rather than a fixed linguistic reflex
- Hindi/Hinglish quality
- domain diversity
- counterexamples and transfer variants
- balanced held-out evaluation across behaviors

## Evaluation verdict

A valid evaluation must compare:

`Qwen3-1.7B-Base`

against

`Qwen3-1.7B-Base + Pilot-002 LoRA`

using the same prompts, template, decoding settings, and frozen validation records.

The evaluation should score behavioral correctness, premise identification, evidence awareness, calibration, language fidelity, repetition/pathology, and generalization—not only lexical similarity to the reference answer.

## Non-goals for the immediate stage

Do not start DPO, full fine-tuning, model fusion, or Skill Genes until the controlled SFT experiment gives a positive and interpretable behavioral signal.

## Final priority order

1. Correctly evaluate the actual Pilot-002 adapter.
2. Freeze and repair validation coverage.
3. Run a minimal clean SFT reproduction.
4. Evaluate behavior + regression.
5. Scale data only after a positive signal.
