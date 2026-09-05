# DHI-v0 — Design Methodology & Experimental Constitution

Status: ACTIVE / controlling methodology
Date: 2026-09-05

## 1. Purpose

DHI-v0 is a research project to create a genuinely differentiated compact reasoning model, starting from Qwen3-1.7B-Base, with strong reasoning character and real Hindi/Hinglish/Indic competence.

The objective is **not** to make a small model imitate a collection of reference answers. The objective is to induce a compact, generalizable behavioral policy while preserving useful native capabilities.

Core behaviors include:

- premise integrity
- evidence seeking
- causal reasoning
- uncertainty calibration
- contradiction handling
- independent judgment
- novel reasoning
- safe agency

The model should reason appropriately across English, Hindi, and Hinglish rather than merely translating an English behavior into Hindi.

## 2. System architecture

DHI is a student-centered system with distinct roles:

```text
                         DHI BEHAVIOR SPEC
                                |
                                v
                     TEACHING / DATA PIPELINE
                                |
               +----------------+----------------+
               |                                 |
               v                                 v
        Qwen3-8B Teacher                      Sarvam
        reasoning / analysis              Indic language,
        / verification                    knowledge/capability
               |                                 |
               +----------------+----------------+
                                |
                                v
                       DHI TRAINING DATA
                                |
                                v
                      Qwen3-1.7B Student
                                |
                       controlled adaptation
                                |
                                v
                             DHI-v0
```

### Role boundaries

**Qwen3-1.7B-Base** is the model being changed and ultimately evaluated.

**Qwen3-8B** is a teacher/tooling source. Its role is to help generate, reason over, critique, verify, expand, or rank training material. It does not define DHI merely because it is larger.

**Sarvam** is an Indic capability source. It is used to improve language-native quality, linguistic coverage, cultural/semantic grounding, and other capabilities that are appropriate to its verified role in the pipeline.

**DHI specification** defines the behavior we want. Neither teacher output nor Sarvam output becomes the definition of DHI automatically.

## 3. Design principles

### 3.1 Behavior before volume

A larger dataset is not automatically better. We first establish that the pipeline produces the intended behavior on held-out examples. Only then do we scale data.

### 3.2 Generalization before memorization

Examples are instruments for inducing a policy. We prefer diverse situations, reasoning structures, languages, domains, and counterexamples over many paraphrases of the same answer.

### 3.3 Minimal intervention

The first training stages should change the smallest amount of the base model necessary to produce the desired behavioral shift. This reduces regression risk and makes experiments interpretable.

### 3.4 Native Indic competence

Hindi/Hinglish quality is a first-class objective. We do not accept an English reasoning policy mechanically rendered into Hindi as the end state.

### 3.5 Evidence over intuition

Every major architecture or training decision should correspond to an observed problem, an explicit hypothesis, or a documented project constraint. We do not change multiple major variables at once without recording why.

### 3.6 Reproducibility

Every experiment must record:

- exact base model identifier/path
- teacher and language-source versions where applicable
- dataset version and split
- prompt/template contract
- tokenizer version/path
- training configuration
- inference configuration
- random seed
- hardware/environment
- output artifact/checkpoint location
- evaluation results

## 4. Constraints

### Compute

Primary development environment: Kaggle, typically 2x Tesla T4 GPUs with approximately 16 GB class memory each.

This constraint favors parameter-efficient adaptation and small controlled experiments over full fine-tuning of large models.

### Student size

The initial student is Qwen3-1.7B-Base. We are not allowed to increase model size merely to solve a problem that should be addressed by data, methodology, or training quality.

### Teacher size

Qwen3-8B is available as the larger teacher/tooling model. Teacher use must remain deliberate because teacher generation is not free and can inject stylistic or factual errors.

### Indic source

Sarvam is included because native Indic competence is part of the research objective. Its exact contribution must be measurable and documented rather than assumed.

### Storage

Kaggle working storage is limited. Do not duplicate large model directories unnecessarily. Preserve critical checkpoints and manifests, and use the GitHub project repository for textual methodology, code, metadata, and experiment records.

## 5. Controlled research cycle

Every experiment follows this sequence:

```text
QUESTION
  -> HYPOTHESIS
  -> DESIGN
  -> MINIMAL TEST
  -> EVALUATION
  -> DECISION
  -> RECORD
  -> NEXT EXPERIMENT
```

A run is not allowed to generate an unrelated follow-up merely because a tool, library, or checkpoint issue appears. Engineering fixes must remain subordinate to the research question.

## 6. Data construction methodology

The data pipeline should separate **generation**, **verification**, **selection**, and **packaging**.

### Stage A — source material

Use the DHI behavior specification, seed bank, language requirements, and domain coverage requirements.

### Stage B — teacher generation

Use Qwen3-8B where deeper reasoning, counterexample creation, candidate generation, critique, or structured transformation is useful.

### Stage C — Indic generation/quality

Use Sarvam where native Hindi/Hinglish/Indic language quality, linguistic variation, or source-specific capability is required.

### Stage D — cross-model checking

Where practical, compare or critique candidate material rather than accepting a single model's output blindly.

### Stage E — quality filtering

Reject examples that are:

- factually unsupported or internally inconsistent
- linguistically unnatural for the target language
- obvious paraphrases of existing examples
- behaviorally ambiguous
- overly dependent on a particular wording
- contaminated by artifacts from source models/templates
- likely to teach a superficial lexical shortcut

### Stage F — final training records

Only selected records enter the training set. Training metadata must preserve provenance so an example can be traced back to its source and generation process.

## 7. Training methodology

The first controlled adaptation should use parameter-efficient fine-tuning rather than full fine-tuning.

Reference approach:

- QLoRA / 4-bit NF4 loading
- `prepare_model_for_kbit_training()`
- LoRA rather than full-weight updates
- initial low-rank configuration around r=8, alpha=32, dropout=0.05
- initial learning rate around 1e-4
- assistant-only loss where supported and correctly verified
- explicit Qwen3 reasoning-mode contract
- small number of epochs, beginning with one
- no packing for the first controlled run
- moderate context length around 1024 for the pilot

These are **experimental defaults**, not immutable truths. A change requires a documented hypothesis.

## 8. Reasoning-mode contract

Qwen3 has explicit thinking/non-thinking behavior. Training and inference must agree about the mode.

For the first compact behavioral SFT stage, use a deliberate non-thinking contract unless an experiment explicitly studies the thinking mode. The prompt/template, training labels, generation settings, and evaluation procedure must be consistent.

Do not interpret generation pathologies without first checking that this contract is consistent.

## 9. Evaluation methodology

Evaluation must test the model, not the dataset's formatting alone.

### Required comparison

At minimum compare:

1. untouched Qwen3-1.7B-Base
2. trained DHI student

using identical evaluation prompts, tokenization/template rules, and decoding conditions.

### Required dimensions

- behavioral correctness
- premise recognition
- evidence awareness
- causal reasoning
- uncertainty/calibration
- contradiction handling
- independent judgment
- novelty/generalization
- safe agency
- Hindi/Hinglish naturalness
- English quality
- repetition/pathology
- unwanted multilingual artifacts
- regression on native capabilities

### Generalization principle

The model should not only reproduce training-style answers. Held-out prompts must alter wording, surface form, context, domain, and language while preserving the underlying reasoning demand.

## 10. Experimental isolation

One experiment should answer one main question.

Examples:

- Does teacher-generated data improve behavior?
- Does Sarvam-derived data improve Indic quality?
- Does combining the two sources outperform either source alone?
- Does LoRA adaptation induce the target behavior without unacceptable regression?

Do not change dataset, teacher, tokenizer contract, LoRA configuration, decoding method, and evaluation metric simultaneously and then attempt to infer causality.

## 11. Baseline ladder

DHI-v0 should progress through interpretable baselines:

### Baseline A — native student

Qwen3-1.7B-Base with no DHI training.

### Baseline B — controlled behavioral SFT

A small, clean DHI dataset with verified formatting and evaluation.

### Baseline C — teacher-enhanced DHI data

Behavioral examples generated/expanded/criticked with Qwen3-8B.

### Baseline D — Indic-enhanced DHI data

Add verified Sarvam-derived language capability material.

### Baseline E — combined pipeline

Combine the verified teacher and Indic sources, then evaluate against all prior baselines.

Only improvements that survive held-out evaluation become part of the main DHI pipeline.

## 12. What we must not do

### Do not mistake an engineering success for a research success

A training run finishing without NaNs does not show that DHI behavior was learned.

### Do not evaluate the wrong model

A base model without its adapter is not the trained DHI model.

### Do not treat a larger teacher as the target identity

Qwen3-8B is a source/tool, not the definition of DHI.

### Do not throw away data prematurely

A failed experiment is not proof that the dataset is bad. First isolate pipeline, formatting, objective, inference, and evaluation issues.

### Do not scale before evidence

More records, more epochs, larger LoRA rank, DPO, full fine-tuning, model merging, or Skill Genes should not be introduced simply because the first pilot is disappointing.

### Do not silently change methodology

Every significant change must be recorded with a reason and expected effect.

### Do not optimize for reference-answer similarity alone

DHI is a behavior. Exact wording overlap is not the objective.

### Do not allow evaluation leakage

Validation/test records must remain held out from training and must be meaningfully different from training examples.

## 13. Decision gates

A training stage advances only if it passes the relevant gate.

### Gate 1 — pipeline validity

Data format, tokenization, model/adapters, labels, and inference path are verified.

### Gate 2 — behavioral signal

The trained student shows a measurable improvement in target DHI behaviors over base on held-out data.

### Gate 3 — language integrity

Hindi/Hinglish/English quality remains acceptable and no major multilingual artifacts appear.

### Gate 4 — capability preservation

Useful base-model behavior does not regress unacceptably.

### Gate 5 — source ablation

When teacher/Sarvam contributions are introduced, their marginal value is tested rather than assumed.

## 14. Current project position

The 200 native reasoning realizations and the 150-record controlled pilot are valuable artifacts, but they belong to an earlier behavioral-data stage.

Pilot-002 demonstrated that a LoRA adapter could be trained and could change generation, but the run did not implement the full teacher + Sarvam + DHI-data methodology. It therefore should not be treated as the definitive DHI training pipeline.

The next research work returns to the architecture above and explicitly constructs the data/teaching pipeline before additional student training.

## 15. North-star rule

When the project becomes confusing, return to this question:

> **What information or training signal is this experiment giving Qwen3-1.7B that should cause a generalizable DHI behavior, and how will we know that it did?**

If that question cannot be answered clearly, the experiment is not ready to run.
