# DHI-v1 Model Selection and Adaption Plan

**Version:** 1.0  
**Date of registry inspection:** 2026-10-31  
**Status:** Primary candidate selected; base-model screening still required.

## 1. Selection objective

Choose a backbone for the first DHI-v1 agentic prototype based on the intended capability mix:

- reasoning under long tasks;
- robust instruction following;
- native tool/function calling;
- software and general tool workflows;
- dynamic tool-schema conditioning;
- long context and preservation of task state;
- multimodal screen/document understanding where useful;
- compatible fine-tuning through the connected Adaption app;
- license and implementation constraints.

The goal is not to pick the largest parameter count or the model with the highest unrelated benchmark score.

## 2. Adaption registry facts captured on 2026-10-31

The connected Adaption model registry listed these candidates as follows:

| Model ID | Registry size | Context | Reasoning training flag | Supported AutoScientist methods | Training type |
|---|---:|---:|---|---|---|
| Qwen/Qwen3.6-35B-A3B | 35B | 262,144 | Yes | SFT, DPO | LoRA |
| openai/gpt-oss-20b | 20B | 131,072 | Yes | SFT, DPO | LoRA |
| google/gemma-4-31B-it | 31B | 262,144 | Yes | SFT, DPO | LoRA, full |
| nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16 | 30B | 131,072 | Yes | SFT, DPO | LoRA |

Registry properties can change; re-query before each run. These flags show platform support, not model quality.

## 3. Candidate comparison

### A. Qwen/Qwen3.6-35B-A3B — selected primary candidate

**Reasons**
- Adaption lists reasoning support and LoRA SFT/DPO.
- Hugging Face model details list the Qwen3.5-MoE model family, approximately 35.95B parameters, and image-text-to-text capability.
- Qwen's public release description positions it for agentic coding and multimodal reasoning.
- Public model metadata describes roughly 35B total parameters and approximately 3B active parameters, with a 262,144-token native context.
- Apache 2.0 is listed in its model metadata.
- Sparse activation makes it a useful balance of total capacity and per-token active computation for the first prototype.

**Why it fits DHI**
Software/terminal workflows are the first environment, but DHI must later reason across browser, documents, APIs, screens, and other modalities. Qwen gives a strong starting balance of code-oriented agentic capability, long context, multimodal input, and Adaption LoRA compatibility.

**Cautions**
- Approximately 3B active parameters does not mean the full 35B weights disappear from storage or training-memory requirements.
- Model-specific tool-call formatting, tokenizer/template, reasoning mode, and adapter compatibility must be tested.
- The 256K context window does not prove reliable long-horizon planning or memory.
- Published agentic-coding claims are not a substitute for the DHI tool-discovery and multi-app benchmark.

### B. openai/gpt-oss-20b — mandatory tool-use challenger

**Reasons**
- Adaption lists reasoning support and LoRA SFT/DPO.
- OpenAI describes it as a 21B-parameter, approximately 3.6B-active open-weight model.
- The published capability description explicitly includes native function calling, web search, Python execution, structured outputs, and adjustable reasoning effort.
- Apache 2.0 is listed in the official model documentation.

**Why it matters**
This model is a particularly important comparator for DHI's central tool-awareness problem. If GPT-OSS performs better than Qwen on tool discovery, action sequencing, and tool-use reliability before fine-tuning, that is strong evidence that the primary candidate should be reconsidered. It is text-only in the Hugging Face task metadata, so it is not the leading screen/video model.

### C. google/gemma-4-31B-it — multimodal challenger

**Reasons**
- Adaption lists reasoning support and supports both LoRA and full training for SFT/DPO.
- Google's model card describes text/image handling, video support, reasoning modes, native function calling, and context up to 256K for the 31B model.
- Multilingual capabilities are substantial according to the official model card.
- Apache 2.0 is listed by Google.

**Why it matters**
Gemma 4 is a strong alternative when screen, document, visual interface, or multilingual input is a major early requirement. The 31B model's training and inference cost must be measured; the presence of full fine-tuning in the registry is not a recommendation to use it.

### D. NVIDIA Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16 — reserve candidate

**Reasons**
- Adaption lists reasoning support and LoRA SFT/DPO.
- Hugging Face metadata describes an any-to-any multimodal model.
- The model is relevant if DHI's scope expands to richer audio/visual interaction.

**Why it is not first**
The inspected Hugging Face metadata lists a non-standard/other license and custom-code requirements. Unless audio/video or its specific architecture is required by the first benchmark, this adds integration and licensing review without a clearly demonstrated advantage for the initial software-agent task.

## 4. Final selection

**Primary:** Qwen/Qwen3.6-35B-A3B.  
**Mandatory comparator:** openai/gpt-oss-20b.  
**Multimodal challenger:** google/gemma-4-31B-it.

This is a research decision for the first prototype, not a claim that Qwen wins. The model-only screen must use identical task instances, tool manifests, execution harness, permissions, retry policy, and budget. If GPT-OSS or Gemma materially outperforms Qwen on the frozen DHI scorecard, change the primary before training.

## 5. Model-screening protocol before fine-tuning

Use the same small, frozen diagnostic set for each candidate:

- 20 no-tool / tool-unnecessary examples;
- 20 current-evidence and tool-necessity examples;
- 20 tool-discovery / unknown-app examples;
- 20 tool-selection and schema examples;
- 20 multi-tool/long-horizon workflow examples;
- 20 failure recovery, replan, and closure examples.

Total: 120 initial screening tasks. These are diagnostic tasks, not enough to claim broad benchmark superiority. Use repeated trials for stochastic cases.

Measure:
- task success;
- tool discovery rate when discovery is needed;
- unnecessary tool calls;
- tool selection and argument validity;
- plan correctness and replan quality;
- execution success and goal closure;
- critical safety violations;
- latency, tokens, and inference cost.

A base model that cannot be run with the correct native tool format should not be scored as if its tool ability were absent; fix the harness/model template before comparing.

## 6. Adaption recommender: what it tells us and what it does not

On 2026-10-31, the Adaption hyperparameter recommender was queried on the existing 12,116-row DHI preference dataset for:
- Qwen/Qwen3.6-35B-A3B;
- NVIDIA Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16;
- openai/gpt-oss-20b.

It returned the same initial reference recipe for those three models:
- one epoch;
- learning rate 1e-4;
- LoRA rank 8 and alpha 8;
- q_proj and v_proj trainable modules;
- cosine scheduler;
- warmup ratio 0.1;
- max batch size;
- train_on_inputs false.

This is a recipe recommendation for the existing preference dataset. It is **not** a comparative quality evaluation, not proof that all models train equally well, and not a frozen recipe for DHI-v1 trajectory SFT. Re-query the recommender on the actual DHI-v1 SFT data and inspect the model-specific training format before creating a run.

## 7. Adaption capabilities and limitations

### Available in the connected app/API as inspected

- Invent new instruction and preference datasets.
- Augment datasets with domain/general/similar rows.
- Adapt imported datasets using column mapping and selected recipes.
- Inspect dataset schema, status, export links, and quality evaluation.
- Use Visualize Data in the app.
- Use AutoScientist SFT/instruction and DPO/alignment with registered models.
- Fine-tune registered models using LoRA; selected registry entries may support full training.
- Inspect recommended model/hyperparameter settings.
- Explore the Inference Stacks / self-improving-model app surface separately.

### Not exposed in the connected AutoScientist API

- Arbitrary new neural architecture definitions.
- Custom JEPA/latent-transition losses.
- Custom model heads and full model-graph changes.
- User-defined environment-grounded RL reward functions and rollout loops.
- Full pretraining of a new foundation architecture from scratch.

Custom predictive architecture work therefore belongs in DHI/GBA code and an external training stack. Adaption is the first-stage backbone/data training platform, not the entire DHI research infrastructure.

## 8. Historical Adaption results that must not be misread

Earlier Qwen3.5-4B AutoScientist runs include approximately 0.2135, 0.3000, 0.3085, 0.3211, and 0.4609 on different runs/datasets/methods. These are training-run-specific AutoScientist metrics, not one common independent benchmark or general model accuracy. They do not prove the 4B base is useless, nor do they validate DHI-v1.

The earlier 1,200-row invented Core v2 run scored 0.1229. The 12,116-row preference DPO run reached 0.4609. The UI SFT comparison screenshot showed 58 for base and 42 for adapted on its displayed evaluation. Keep these as negative/limited historical evidence; do not reuse the datasets as the v1 trajectory corpus.

Adaption support explained on 2026-10-30 that recursive augmentation from an already-augmented invented seed likely caused repeated rows, invented rows naturally lack original user prompts, and the Grade A label had been copied from the source dataset rather than freshly computed. Support said they were fixing grading for augmentation. Always verify a fresh evaluation timestamp and source before accepting a grade.

## 9. Spend-control rules

Before any new Adaption job:
1. Confirm the actual final dataset columns and source lineage.
2. Inspect rows with Visualize and the available quality checklist.
3. Confirm that examples have genuine executed outcomes where required.
4. Obtain a current estimate for the selected model and exact dataset.
5. Confirm model-specific data format, native chat template, and tool-call representation.
6. Ensure a frozen held-out evaluation exists.
7. Run only one controlled first SFT experiment.
8. Do not launch DPO until the SFT baseline provides a valid behavioral signal and preference pairs have independent quality checks.

Earlier Adaption attempts enforced a minimum of 1,000 effective SFT rows and 12,000 effective preference pairs for DPO. Treat these as observed previous platform gates, not permanent guarantees; re-check the live requirement before a job.

## 10. Primary sources

- Qwen3.6-35B-A3B model card: https://huggingface.co/Qwen/Qwen3.6-35B-A3B
- Qwen3.6 public release description: https://www.alibabacloud.com/blog/qwen3-6-35b-a3b-thinking-open-weights-uncompromised-agentic-coding_603043
- GPT-OSS-20B official model description: https://developers.openai.com/api/docs/models/gpt-oss-20b
- Introducing GPT-OSS: https://openai.com/index/introducing-gpt-oss/
- Gemma 4 official model card: https://ai.google.dev/gemma/docs/core/model_card_4
- Nemotron model card: https://huggingface.co/nvidia/Nemotron-3-Nano-Omni-30B-A3B-Reasoning-BF16

All technical and availability claims must be rechecked for the exact model revision and Adaption registry at the time of a run.
