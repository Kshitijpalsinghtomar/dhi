# DHI-v1 — Predictive Agentic Intelligence

**Created:** 2026-10-31  
**Status:** Research/design plus first runnable environment prototype. No DHI-v1 model, model-generated trajectory dataset, or positive benchmark result exists yet.

## North-star definition

DHI-v1 is intended to become a general-purpose model that can reason about a user's goal, discover and select relevant tools from a changing tool ecosystem, plan and execute long-horizon workflows, predict the consequences of actions, adapt when reality differs from its plan, and verify that the requested outcome was actually achieved.

The intelligence must be learned in the model. A runtime may expose tools, credentials, permissions, sandboxes, and persistent execution state; those are necessary interfaces, not substitutes for learned tool awareness, planning, reasoning, or predictive ability.

## The combined research thesis

This programme combines two inputs:

1. **User-originated problem statement:** current AI agents often remain narrow, rely on the tools already placed in front of them, fail to discover apps/connectors when capability is missing, use a one-pass or shallow loop, and lose awareness during long workflows.
2. **Research direction:** learn a task-relevant predictive state, forecast action effects, condition decisions on goals and constraints, and verify final goal closure against real environment state.

The candidate mechanism is a **goal-conditioned predictive agentic model** with learned tool-affordance reasoning, hierarchical planning, action-effect prediction, and verifiable task closure.

## Development strategy

- First build and benchmark the model's agentic capability using a supported backbone and Adaption.
- Use real sandbox-executed trajectories, not fabricated tool outcomes.
- Test tool discovery, multi-tool selection, long-horizon planning, re-planning, failure recovery, context continuity, safety, and task closure.
- Add action-effect forecast supervision only after the ordinary agentic baseline and trace quality are valid.
- Investigate a trainable latent predictive state mechanism in the custom GBA/architecture track only after forecast supervision demonstrates a real benefit.

## Selected backbone strategy

**Primary Adaption candidate:** Qwen/Qwen3.6-35B-A3B.  
**Mandatory tool-use challenger:** openai/gpt-oss-20b.  
**Multimodal challenger:** google/gemma-4-31B-it.

Qwen is selected as the initial build candidate because Adaption exposes reasoning-capable LoRA SFT/DPO support for it; the model is a sparse 35B/approximately 3B-active multimodal MoE with a 262K context window and strong agentic-coding positioning. GPT-OSS-20B is a necessary challenger because its published capabilities explicitly include native function calling, tool use, structured outputs, and adjustable reasoning effort. Gemma 4 31B is a strong alternative when screenshot, video, or broad multimodal handling is a central requirement. See the model-selection record for constraints and evidence.

This is a candidate choice, not a claim that Qwen is empirically best. All three base models must be compared on the same DHI diagnostic tasks before training.

## First executable assets

- [Deterministic environment and pinned fixture](environment/README.md)
- [12-case agentic pilot suite](../DHI_v1/benchmark/README.md)

Local verification as of 2026-10-31: 26 tests pass, including fixture integrity, workspace materialization, hidden-tool discovery, state deltas, protected files, and trace validation. The hand-scripted smoke pilot is not model-generated or training data.

## Read the controlling documents

1. [Master development plan](docs/00_MASTER_DEVELOPMENT_PLAN.md)
2. [Capability rubric](docs/01_CAPABILITY_RUBRIC_AND_SCORECARD.md)
3. [Tool awareness and long-horizon planning](docs/02_TOOL_AWARENESS_AND_LONG_HORIZON.md)
4. [Model selection and Adaption limits](docs/03_MODEL_SELECTION_AND_ADAPTION.md)
5. [Methods and intervention gates](docs/04_METHODS_AND_WHEN_TO_USE.md)
6. [Benchmark protocol](docs/05_BENCHMARK_PROTOCOL.md)
7. [Trajectory/data contract](docs/06_DATA_AND_TRAJECTORY_CONTRACT.md)
8. [Decision log](docs/07_DECISIONS_AND_RESEARCH_LOG.md)

## Current execution state

- [x] DHI-v0 history inspected and preserved.
- [x] Adaption model registry inspected.
- [x] Three candidate backbones selected for comparative screening.
- [x] Capability rubric and evaluation gates specified.
- [x] Deterministic tool/environment harness v0.1 built and locally tested (15 tests passed).
- [ ] Connect an inference endpoint and compare untouched base models on the frozen DHI diagnostic suite.
- [ ] Real trajectory pilot collected and independently validated.
- [ ] Adaption SFT estimate and training run.
- [ ] Predictive/closure ablations.
- [ ] Custom latent architecture investigation.

The OpenAI-compatible model runner is ready at [agent_runner.py](environment/agent_runner.py). The connected Adaption API currently lacks an inference method, so no model comparison has been run yet.

No new Adaption dataset generation or training run is authorized by this plan alone.


## First executable environment

The first deterministic file-workspace tool environment is implemented under [environment/](environment/). It supports tool-catalogue discovery, file inspection/search/writes, action-start and action-result traces, SHA-256 state deltas, predicted-effect comparison, protected paths, and executable goal postconditions.

- [Environment README](environment/README.md)
- [Environment implementation](environment/dhi_env.py)
- [15 unit/integration tests](environment/tests/test_dhi_env.py)
- [Trajectory event JSON Schema](environment/schemas/trajectory-event.schema.json)
- [Deterministic smoke pilot](environment/examples/run_pilot.py)
- [GitHub Actions workflow](../../.github/workflows/dhi-v1-environment.yml)

Local verification on 31 October 2026: **15 tests passed**; compileall passed; the scripted smoke pilot emitted 13 events and passed the README postcondition while preserving two protected files. The pilot is hand-scripted, not model-generated, and is not training data.

The harness is deliberately file-only and is not an OS/container sandbox. Catalogue discovery is a lexical fixture, not a real app/plugin marketplace. No model is connected and no DHI-v1 training run has been launched.

## First executable milestone

The deterministic file-workspace environment is implemented in [DHI_v1/environment](environment/README.md). It supports a visible tool subset, catalogue discovery, file operations, action-effect comparison, verified postconditions, and append-only event traces. Local verification: 17 tests passed; the scripted smoke trace contains 13 schema-valid events. The pilot is not model-generated and is not training data.
