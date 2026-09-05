# DHI-v0 — Decision Log

## 2026-09-05 — Return to the intended architecture

### Decision
DHI-v0 will use Qwen3-1.7B-Base as the student, Qwen3-8B as a teacher/tool, and Sarvam as an Indic capability/source component. The target is a genuinely differentiated compact reasoning model, not a lightly adapted copy of the teacher.

### Why
Pilot-002 demonstrated adapter training and behavioral change, but it was effectively a small conversational SFT experiment. It did not implement the intended teacher + Sarvam + DHI pipeline strongly enough to answer the research question.

### Consequence
Do not treat Pilot-002 as the final model. Preserve it as an experimental baseline and failure/learning artifact.

---

## 2026-09-05 — Stop audit loops

### Decision
Engineering audits are only performed when they resolve a concrete uncertainty or unblock a run.

### Why
Repeated tokenizer, checkpoint, GPU, and file audits consumed effort without advancing the research question.

### Consequence
The next work product is the teaching/data pipeline and one controlled experiment.

---

## 2026-09-05 — Preserve source separation

### Decision
Qwen3-8B, Sarvam, and DHI-generated material must retain provenance and roles.

### Why
Otherwise the experiment cannot determine whether improvements come from the intended DHI behavior, teacher imitation, or Indic-language data.

### Consequence
Training records need source metadata and later ablation experiments.

---

## 2026-09-05 — Controlled adaptation before scaling

### Decision
Use parameter-efficient QLoRA/LoRA as the initial student adaptation method.

### Why
The available Kaggle T4 environment favors PEFT, and it allows interpretable changes with lower compute and lower regression risk than full fine-tuning.

### Consequence
Do not move to full fine-tuning or more elaborate preference/skill training until the basic behavioral signal is demonstrated.

---

## Current research question

**Can a carefully constructed DHI teaching signal, combining verified reasoning supervision with native Indic capability, induce robust DHI behaviors in Qwen3-1.7B-Base without unacceptable loss of general capability?**

### Immediate experiment
Build and run a small, high-quality, source-traceable pilot; compare against untouched Qwen3-1.7B-Base on held-out behavioral and language evaluations; then perform source ablations.
