# DHI-v1 — Predictive Agentic Intelligence

**Created:** 2026-10-31  
**Status:** Active research and runnable evaluation harness. No DHI-v1 model has been benchmarked yet.

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
- [Adaption Responses API adapter](environment/adaption_responses.py)
- [Live Adaption connector discovery handler](environment/agent_runner.py)
- [Single-task model integration pilot](environment/examples/run_model_pilot.py)
- [Eight-case model-facing benchmark entrypoint](benchmark/run_model_pilot.py)
- [12-case diagnostic seed suite](benchmark/README.md)
- [Benchmark runner](benchmark/runner.py)
- [Benchmark CLI](benchmark/run_pilot_benchmark.py)
- [Invent task-spec audit CLI](benchmark/audit_invent_dataset.py)

## Current executable evaluation

- **Eight common cases:** no-tool restraint, source inspection, local hidden-tool discovery, multi-step editing, no-op handling, transient failure recovery, unavailable-resource honesty, and protected-file editing.
- **One Adaption-only case:** the model may search the live account connector catalogue and must report current availability, scope and approval metadata without claiming or executing an external connector action.
- **Three unsupported cases:** live current-source verification, decoy-tool choice across external providers, and cross-session long-horizon resume.

For Adaption runs, the connector catalogue is fetched once and reused throughout the run. Its SHA-256 snapshot is recorded so model comparisons can verify that both models saw the same available connectors. The Adaption meta-tool is read-only. Two 120-row Invent task-spec candidates completed but failed the data-method gate (first: Grade B / 7.7; second: Grade C / 6.6). Both remain quarantined. The latest methodology review concludes that the prompt/completion target was mismatched: long benchmark-spec JSON was generated as if it were an answer to the user task. See [ORBIT data-generation method review](docs/08_ORBIT_DATA_GENERATION_METHOD_REVIEW.md).

Local verification on 2026-10-31: **75 tests passed** across environment and benchmark tests; Python compileall passed; the scripted smoke trace produced 13 events and passed the checked-in event schema. The smoke pilot is hand-scripted, not model-generated, and not training data.

## Current status

- [x] DHI-v0 history preserved separately.
- [x] DHI-v1 model strategy, capability rubric, methods, benchmark protocol, and trajectory contract documented.
- [x] Deterministic file-workspace environment and pinned fixture implemented.
- [x] Model-to-tool runner implemented with per-turn schema refresh.
- [x] Eight common benchmark cases and observable evaluator implemented.
- [x] Adaption Responses API and live connector catalogue adapters implemented.
- [x] Read-only Adaption discovery exposed as a model-callable meta-tool.
- [x] Per-run connector-catalogue snapshot fingerprint added to traces and reports.
- [ ] Use a live Adaption API key to list actual hosted models and run untouched model comparisons.
- [ ] Obtain row-level export for both quarantined Invent task-spec candidates and audit prompt/spec quality; row-level review is separate from the current method-mismatch finding.
- [ ] Collect model-generated execution trajectories from a sandbox and independently verify them.
- [ ] Estimate and run the first Adaption SFT experiment after data and benchmark gates pass.
- [ ] Compare ordinary agentic SFT with predictive/closure supervision.
- [ ] Investigate custom latent predictive architecture in GBA after the controlled ablations.

## Important constraints

Adaption's connected MCP integration does not expose its Responses or connector-list REST endpoints. DHI therefore uses the documented Adaption REST API: `POST /api/v1/responses`, `GET /api/v1/models`, and `GET /api/v1/tools`. A live API key and account-visible hosted model ID are still required to exercise it.

The Adaption connector meta-tool only discovers catalogue entries. It does not invoke external MCP tools or perform issue/file/email mutations. A later execution bridge must include operation-level tool schemas, permission/approval handling, per-action traces and independently verifiable goal closure before those actions enter the scored benchmark.

The file environment is not a production OS/container sandbox. Local catalogue search is a small lexical fixture. No DHI-v1 model score, training run or architecture novelty result is claimed.

## Read the controlling documents

1. [Agent handover and current continuation state](docs/11_AGENT_HANDOVER_2026-11-02.md)
2. [Master development plan](docs/00_MASTER_DEVELOPMENT_PLAN.md)
3. [Capability rubric](docs/01_CAPABILITY_RUBRIC_AND_SCORECARD.md)
4. [Tool awareness and long-horizon planning](docs/02_TOOL_AWARENESS_AND_LONG_HORIZON.md)
5. [Model selection and Adaption limits](docs/03_MODEL_SELECTION_AND_ADAPTION.md)
6. [Methods and intervention gates](docs/04_METHODS_AND_WHEN_TO_USE.md)
7. [Benchmark protocol](docs/05_BENCHMARK_PROTOCOL.md)
8. [Trajectory/data contract](docs/06_DATA_AND_TRAJECTORY_CONTRACT.md)
9. [Decision log](docs/07_DECISIONS_AND_RESEARCH_LOG.md)
