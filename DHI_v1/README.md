# DHI-v1 — Predictive Agentic Intelligence

**Created:** 2026-10-31  
**Status:** Active research and first executable prototype. No DHI-v1 model has been benchmarked yet.

## North-star definition

DHI-v1 is intended to become a general-purpose model that can reason about a user's goal, discover and select relevant tools from a changing tool ecosystem, plan and execute long-horizon workflows, predict the consequences of actions, adapt when reality differs from its plan, and verify that the requested outcome was actually achieved.

The intelligence must be learned in the model. A runtime may expose tools, credentials, permissions, sandboxes, and persistent execution state; those are necessary interfaces, not substitutes for learned tool awareness, planning, reasoning, or predictive ability.

## Research thesis

The programme combines:
1. The observed weakness that assistants can remain narrow, use only familiar or preloaded tools, fail to discover available apps/connectors, and lose awareness in long workflows.
2. A predictive model direction: learn task-relevant state representations, forecast action effects, condition decisions on goals and constraints, and verify closure against actual environment state.

This is a research direction, not a proven architecture or novelty claim.

## Selected backbone candidates

- **Primary Adaption candidate:** `Qwen/Qwen3.6-35B-A3B`
- **Mandatory tool-use challenger:** `openai/gpt-oss-20b`
- **Multimodal challenger:** `google/gemma-4-31B-it`

This is a candidate selection, not a measured ranking. Base screening must precede fine-tuning.

## Executable assets

- [Deterministic environment and pinned fixture](environment/README.md)
- [Model-to-environment runner](environment/agent_runner.py)
- [Single-task model integration pilot](environment/examples/run_model_pilot.py)
- [12-case diagnostic seed suite](benchmark/README.md)
- [Benchmark runner](benchmark/runner.py)
- [Benchmark CLI](benchmark/run_pilot_benchmark.py)

The deterministic file-workspace harness has eight supported diagnostic cases: no-tool restraint, source inspection, hidden-tool discovery, multi-step editing, no-op handling, transient failure recovery, unavailable-resource honesty, and protected-file editing. Four additional cases require future runtime integrations and are currently excluded.

Local verification on 2026-10-31: **54 tests passed** across environment and benchmark tests; Python compileall passed; the scripted smoke trace produced 13 events and passed the checked-in event schema. The smoke pilot is hand-scripted, not model-generated, and not training data.

## Current status

- [x] DHI-v0 history preserved separately.
- [x] DHI-v1 model strategy, capability rubric, methods, benchmark protocol, and trajectory contract documented.
- [x] Deterministic file-workspace environment and pinned fixture implemented.
- [x] Model-to-tool runner implemented with per-turn schema refresh after tool discovery.
- [x] Eight-case executable pilot and observable evaluator implemented.
- [x] Adaption Responses API client, hosted-model catalogue, and live connector catalogue commands implemented.
- [x] Controlled transient tool failure and no-tool restraint cases added.
- [ ] Set an Adaption API key, list available hosted model IDs, and run untouched candidate models through the Responses adapter under identical conditions.
- [ ] Inspect and validate the Adaption-generated 120-task specification seed.
- [ ] Collect model-generated execution trajectories from a sandbox and independently verify them.
- [ ] Estimate and run the first Adaption SFT experiment after data and benchmark gates pass.
- [ ] Compare ordinary agentic SFT with predictive/closure supervision.
- [ ] Investigate custom latent predictive architecture in GBA after the controlled ablations.

## Important constraints

The connected Adaption MCP tool set exposes dataset creation/adaptation and AutoScientist SFT/DPO, but not inference. The platform REST API does expose `POST /api/v1/responses` and `GET /api/v1/models`; DHI now has an adapter. A live API key and account-visible hosted model ID are still needed to exercise it. Adaption does not create or edit inference stacks through the API; those are configured in the app.

The current file environment is not a production OS/container sandbox and its catalogue is a small lexical fixture, not a live app/plugin marketplace. No DHI-v1 model benchmark, training run, or architecture result is claimed.

## Read the controlling documents

1. [Master development plan](docs/00_MASTER_DEVELOPMENT_PLAN.md)
2. [Capability rubric](docs/01_CAPABILITY_RUBRIC_AND_SCORECARD.md)
3. [Tool awareness and long-horizon planning](docs/02_TOOL_AWARENESS_AND_LONG_HORIZON.md)
4. [Model selection and Adaption limits](docs/03_MODEL_SELECTION_AND_ADAPTION.md)
5. [Methods and intervention gates](docs/04_METHODS_AND_WHEN_TO_USE.md)
6. [Benchmark protocol](docs/05_BENCHMARK_PROTOCOL.md)
7. [Trajectory/data contract](docs/06_DATA_AND_TRAJECTORY_CONTRACT.md)
8. [Decision log](docs/07_DECISIONS_AND_RESEARCH_LOG.md)
