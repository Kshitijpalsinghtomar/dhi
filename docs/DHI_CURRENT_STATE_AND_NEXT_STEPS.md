# DHI-v0 — Current State, Decisions, and Next Steps

Date: 2026-09-05
Status: ACTIVE

## What has been established

- Student: Qwen3-1.7B-Base.
- Teacher/tool: Qwen3-8B.
- Indic source/capability: Sarvam.
- DHI target: compact reasoning character + native Hindi/Hinglish/Indic competence.
- A 200-example native behavioral realization set was created and tested.
- A 150-record Pilot-002 training set was trained with LoRA/QLoRA.
- Pilot-002 produced a valid LoRA adapter and changed student generation.
- Pilot-002 did **not** constitute the final DHI pipeline because it did not properly integrate the intended Qwen3-8B + Sarvam + DHI teaching architecture.

## Important observed failures

### 1. Tokenizer confusion

At one point the trained student directory did not contain tokenizer files. A separate Qwen3 tokenizer was found and used. Later the actual student model directory was found to contain its tokenizer. Future experiments must keep the exact base-model tokenizer paired with the exact base checkpoint and save it with the experiment artifact.

### 2. Accidental base-model loading OOM

Loading the 1.7B model in bf16 onto one T4 caused OOM because the process already had substantial CUDA allocation. A two-GPU experiment showed that a plain `device_map="auto"` style load did not necessarily distribute the model as expected; the model ended up effectively on GPU 0. Future inference must use an explicit, controlled device strategy and clean CUDA state.

### 3. Generation/input bug

One evaluation attempt passed a tokenizer `BatchEncoding` object incorrectly into `generate`, causing `AttributeError: shape`. Future generation code must pass `input_ids` as a tensor and `attention_mask` separately, or use the BatchEncoding correctly with `**inputs`.

### 4. Pilot-002 output pathology

Base generation was already pathological for the selected prompt, while Pilot-002 changed the output but still produced truncation/repetition/multilingual artifacts. This does not by itself prove that the dataset was bad. It indicates that the complete pipeline, objective, prompt/template contract, inference configuration, and data quality must be isolated before interpreting the result.

### 5. PEFT/TorchAO environment mismatch

An earlier environment reported torchao 0.10 with a PEFT version requiring a newer torchao. The environment was later corrected to torchao 0.18, PEFT 0.19.1, transformers 5.0.0. Environment versions must be pinned/reported for every future run.

## Current decision

**Stop repeating audits unless an audit directly answers a current failure.**

The project now moves from checkpoint archaeology to the actual research pipeline.

The next run should NOT be another blind SFT of the 150-record set.

## Next sequence

### Step 1 — Freeze the experiment contract

Create one versioned configuration containing:

- base model identifier
- exact tokenizer
- Qwen3 reasoning/non-thinking mode
- teacher model
- Sarvam model/API/version used
- data sources
- train/validation/test split
- maximum sequence length
- loss masking policy
- LoRA/QLoRA configuration
- optimizer
- learning rate
- epochs
- seed
- evaluation metrics

### Step 2 — Build the teaching-data pipeline

Construct examples through four explicit stages:

```text
DHI behavior specification
        ↓
Qwen3-8B teacher generation / critique
        +
Sarvam Indic generation / linguistic grounding
        ↓
verification + selection
        ↓
DHI training records
```

Do not directly dump raw teacher or Sarvam outputs into training.

### Step 3 — Create a small gold pilot

Before scaling, make a compact, high-quality pilot containing:

- premise-integrity cases
- evidence-seeking cases
- causal reasoning cases
- uncertainty cases
- contradiction cases
- independent-judgment cases
- Hindi-native cases
- Hinglish cases
- English controls

Keep held-out variants that test the same behavior through different wording and contexts.

### Step 4 — Validate the data before training

Programmatically check:

- schema
- duplicate/near-duplicate contamination
- language distribution
- response length
- malformed Unicode
- chat-template rendering
- assistant-only loss boundaries
- train/validation separation
- source provenance
- obvious teacher artifacts

### Step 5 — Run one controlled QLoRA experiment

Use the exact contract. Do not simultaneously alter data, objective, model, tokenizer, LoRA configuration, and decoding.

### Step 6 — Evaluate base vs DHI

Use identical held-out prompts and decoding settings. Score behavior, not exact string matching.

### Step 7 — Ablate sources

Compare:

- DHI-only
- DHI + Qwen teacher
- DHI + Sarvam
- DHI + Qwen teacher + Sarvam

This tells us whether each source contributes real value.

### Step 8 — Scale only after a positive signal

Only after the controlled pilot demonstrates a robust held-out behavioral improvement should the dataset and training budget increase.

## Do not repeat these mistakes

- Do not keep running audits that do not change a decision.
- Do not treat a changed generation as proof of learning.
- Do not use only reference-answer similarity as the metric.
- Do not train without an explicit reasoning-mode/template contract.
- Do not mix base and adapter artifacts without recording their exact relationship.
- Do not let teacher style become the target behavior accidentally.
- Do not treat Sarvam as merely a translation layer.
- Do not add DPO, full fine-tuning, Skill Genes, merging, or larger models before the controlled SFT/QLoRA pipeline is demonstrated.
- Do not scale a questionable dataset to save time; that usually wastes more time.

## Immediate next deliverable

The next implementation artifact should be a **single reproducible DHI teaching-data + QLoRA pilot notebook/script**, not another audit notebook.

It should produce:

1. a versioned generated training dataset,
2. a held-out evaluation set,
3. a training configuration manifest,
4. a LoRA adapter,
5. base-vs-adapter evaluation results,
6. a concise experiment report.
