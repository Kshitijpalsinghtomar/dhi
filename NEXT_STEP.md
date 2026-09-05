# DHI-v0 — NEXT STEP

## Do this next. Nothing else.

Build the **controlled DHI teaching-data pilot**.

### Pipeline

```text
DHI behavior specification
        ↓
Qwen3-8B teacher
(generate / critique / verify reasoning)
        +
Sarvam
(native Hindi / Hinglish / Indic capability)
        ↓
source-aware filtering + deduplication
        ↓
small gold pilot + held-out variants
        ↓
QLoRA on Qwen3-1.7B-Base
        ↓
base vs trained evaluation
        ↓
source ablation
```

### Required implementation

Create one notebook/script that:

1. loads the DHI behavior seeds,
2. generates/derives candidate examples with Qwen3-8B and Sarvam,
3. records provenance,
4. validates and deduplicates the data,
5. creates train/validation/test splits,
6. renders the exact Qwen3 chat template,
7. verifies assistant-loss boundaries,
8. trains Qwen3-1.7B with QLoRA,
9. evaluates base and adapter under identical decoding,
10. writes an experiment manifest and results report.

### First pilot scope

Keep it small and high quality. Cover the core DHI behaviors and all three language conditions: Hindi, Hinglish, English.

### Locked constraints

- Student: Qwen3-1.7B-Base.
- Teacher: Qwen3-8B.
- Indic source: Sarvam.
- Initial adaptation: QLoRA/LoRA.
- No full fine-tuning yet.
- No DPO yet.
- No Skill Genes yet.
- No model-size escalation yet.
- No blind dataset scaling.
- No repeated audits unless they answer a concrete blocker.

### Success criterion

The trained student must show a **robust held-out improvement in DHI behaviors**, not merely produce outputs that look more like the reference answers.

If it fails, diagnose the specific stage that failed before changing the next variable.

---

**This file is the project navigation anchor for the next session.**
