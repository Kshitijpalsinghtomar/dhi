# DHI-v1 Live Workspace

> **DHI RESEARCH CONTROL — 2026-11-12. Read this before any other section.**
>
> **Fresh-agent handoff:** [`DHI_v1/NEXT_AGENT_HANDOFF.md`](NEXT_AGENT_HANDOFF.md) contains the exact S09-001 continuation prompt, current branch state, verified test evidence and next-task constraints.
>
> This repository is the **DHI-v1 / ORBIT research programme only**. Do not mix code, datasets, claims, tasks, or conclusions from GBA/DPAK, Oriael, or other research projects.
>
> **Active research path:** the tool-acquisition/lifecycle novelty candidate was rejected as insufficiently distinct. See [15_PRIOR_ART_AND_NOVELTY_GATE_2026-11-11.md](docs/15_PRIOR_ART_AND_NOVELTY_GATE_2026-11-11.md). DHI-v1 is an empirical model-development programme: untouched base-model screening, verified-execution SFT, then controlled prediction/closure ablations. No new method claim is accepted before results.
>
> **Study 0 tracking:** [Issue #2 — freeze untouched base-model capability screen](https://github.com/Kshitijpalsinghtomar/dhi/issues/2). Current Stage A has 30 tasks and Stage B has zero. **Fifteen of 30 deterministic grader checks pass; 15 remain `not_run`.** The unrun IDs are S09-001, S10-001, S02-002, S04-002, S06-002, S08-002, S09-002, S10-002, S02-003, S08-003, S06-003, S04-003, S07-002, S09-003 and S06-004. Only S06-001 has an accepted family review; the other 29 remain `not_reviewed`. Every execution remains `not_run`; all 30 `model_runs_allowed` flags are false. Do not confuse deterministic grader tests with model capability or family acceptance.
>
> **Important S04 grader correction:** `tool_trace` now checks the successful fetched result's exact Git blob SHA and optional exact arguments, not just the tool name. S04-001 is pinned to repository `Kshitijpalsinghtomar/dhi`, `DHI_v1/benchmark/fixtures/plugin_ecology/TASK_POLICY.md`, ref `af6c0d31fcf2e3232cb427c421850536139e3b3a`, blob `0e5d3c519749651ad5f5ec728622895cfc44a649`. Regression coverage rejects wrong SHA, wrong ref, failed reads and write-tool substitution.
>
> **Latest integrated regression attempt:** Deepnote run `60c6ecc2-a1c1-4a88-a7d6-26ed2b2476dc` assembled 103 tests but its integrated-regression subprocess hit the 300-second timeout; do not count it as a pass. Its standalone manifest validator and `compileall` both passed. S08-001 passed its schema-corrected focused suite **12/12** in run `e4e8e116-8e45-4f19-96bc-3b02737abce1`. S02-001 plus the existing S05-002/S05-004 TinyFish suites then passed **27/27** in run `edd2ef89-14af-4d07-ae9d-fbd142d5f6f2`. The exact committed-manifest validator and `compileall` passed in run `e4ac486d-414c-4a04-b35e-ec08432e045c`.
>
> **Latest manifest:** trace-grader commit `bd4ba024c15f15c43ce86af84e8b9d019fa2dc93`, manifest commit `87a9afcf28a5c796ed39015efe703f5ce3fd97ba`, Git blob `a1e198b0f48311a98333a4e53d6e8d38f07ab3dc`. It records 15 grader checks passed, 15 `not_run`, 1 family accepted and 29 `not_reviewed`. S07-001's 53-test deterministic regression, exact manifest validation and compileall passed; the existing report is correctly rejected for the missing NS-106 → NS-105 dependency. All executions remain `not_run`, all model-run flags false. A grader-check pass records deterministic verifier-test evidence—not a model trajectory.
>
> **Development pilot boundary:** `DHI_v1/benchmark/pilot_cases.json` is a 12-case integration/harness pilot explicitly excluded from Stage A/B; its runner supports file-workspace cases (and an optional Adaption catalogue case), not the 30 plugin-native panel tasks. It is not a substitute for Study 0.
>
> **Implemented research code:** `DHI_v1/research/joint_state.py` defines separate observed task/world and tool-ecosystem state, diffs and forecast scoring. `DHI_v1/research/dhi_environment_observer.py` reads real `DHIEnvironment` snapshots without mutating the environment. This is deterministic measurement infrastructure, not a learned model or capability result. Research mechanism: 22/22 focused tests and `compileall` passed in Deepnote run `ca0c1e0e-bace-4927-ae65-5d83528eb59a` at commit `81a299342ecee919e1a068a34897789934b1685c`.
>
> **Hard evidence boundary:** no DHI model inference, model-generated execution trajectory, adjudicated training corpus, capability score, or training checkpoint exists. The S07-001 focused run covered 21 task-specific tests plus all 32 tests in the shared plugin_trace grader module (53 total); it is not the full historical benchmark/environment suite. The last OpenRouter check on 2026-11-11 showed zero credits; Deepnote has no model-provider integration. Do not run a model, switch to a free endpoint/candidate, alter permissions, spend credits, or launch training without explicit user authorization and an approved resource route.
>
> **Next-agent handoff:** read [`NEXT_AGENT_HANDOFF.md`](NEXT_AGENT_HANDOFF.md). S07-001's deterministic grader work is complete; the next unrun manifest task is `ORBIT-A-S09-001`. Keep the S07 sandbox branch read-only and work only on `orbit/plugin-benchmark-fixture`. No model inference or training is authorized.


**Last updated:** 2026-11-12  
**Repository:** https://github.com/Kshitijpalsinghtomar/dhi  
**Active research branch:** `orbit/plugin-benchmark-fixture` (default `main` remains unchanged; branch is intentionally unmerged)  
**Live-state rule:** This file is the first read at every session. It supersedes older chat summaries and dated handover snapshots when describing current status.

## 1. Identity

- Active programme: **DHI-v1 — Predictive Agentic Intelligence**.
- Model codename used in this programme: **ORBIT**.
- DHI-v0 is historical and separate.
- GBA/DPAK and all other research are separate. Do not mix evidence or directions across projects without a committed DHI decision.
- GitHub is the durable project memory. Follow [the Git-first workflow](docs/12_GIT_FIRST_WORKFLOW.md).

## 2. Current objective

Develop a learned policy that reasons about task goals and constraints while choosing among normal tool actions and capability/lifecycle actions, predicts the consequences for task reachability and future available actions, replans from actual feedback, respects external permission gates, and verifies goal closure. The precise candidate and prior-art exclusions are governed by docs/15_PRIOR_ART_AND_NOVELTY_GATE_2026-11-11.md.

This is a research target, not a result or novelty claim. A prompt, RAG store, fixed router, scripted client, or external orchestrator is not by itself the learned model contribution.

## 3. Current phase and status

<details>
<summary>Machine-readable status</summary>

```yaml
programme: DHI-v1
codename: ORBIT
phase: study_0_task_grader_admission
status: research_in_progress
status_reason: The lifecycle/acquisition novelty candidate is rejected as insufficiently distinct. Active work is empirical DHI-v1 model development. Stage A has 30 materialized tasks; Stage B has 0. Fifteen deterministic grader checks pass, 15 remain not_run. Only S06-001 has accepted family review; the other 29 remain not_reviewed. All 30 executions are not_run and all model_runs_allowed flags remain false. No model inference, model-generated trajectory, adjudicated training corpus, capability score, or training checkpoint exists. S07-001's 21 task-specific plus 32 shared plugin-trace tests passed; exact committed-manifest validation and benchmark/environment compileall passed. Its pre-existing report remains uncorrected and fails the required NS-106 -> NS-105 content check. The 103-test integrated attempt timed out at its configured five-minute limit and is not a pass.
training_status: not_authorized
benchmark_status: stage_a_30_materialized_of_120; 15_grader_checks_pass; 15_grader_checks_not_run; stage_b_sealed_unmaterialized
task_admission: blocked_pending_family_review
model_runs_allowed: false
training_runs_allowed: false
research_mechanism_test_commit: 81a299342ecee919e1a068a34897789934b1685c
research_mechanism_test_run: ca0c1e0e-bace-4927-ae65-5d83528eb59a
research_mechanism_test_count: 22
research_mechanism_compileall_exit_code: 0
latest_manifest_blob: a1e198b0f48311a98333a4e53d6e8d38f07ab3dc
latest_manifest_commit: 87a9afcf28a5c796ed39015efe703f5ce3fd97ba
latest_integrated_regression_run: 60c6ecc2-a1c1-4a88-a7d6-26ed2b2476dc
latest_integrated_regression_tests: 103
latest_integrated_regression_exit_code: timed_out_300s
latest_integrated_compileall_exit_code: 0
latest_manifest_validator_run: c34a6a9a-8161-41d9-a654-73483f437724
latest_manifest_validator_status: pass
latest_regression_run: f578ade9-6369-4ace-b34b-01279c000714
latest_regression_test_count: 53
latest_regression_scope: S07-001 (21 task-specific) plus full plugin_trace grader suite (32)
latest_regression_exit_code: 0
latest_s02_001_focused_tests: 8
latest_s02_001_test_commit: 28d145773668e7f4ffb8a8a699976ddb91174c19
latest_s02_001_exact_manifest_valid: true
latest_s02_001_compileall_exit_code: 0
latest_s08_001_focused_run: e4e8e116-8e45-4f19-96bc-3b02737abce1
latest_s08_001_focused_tests: 12
latest_s08_001_manifest_update_run: d147615d-dc94-4b14-98b7-768a879a17b7
latest_s08_001_manifest_validation_run: 9ca039ce-6bba-4dbd-af33-4003e3634aa9
latest_s08_001_exact_manifest_valid: true
latest_s08_001_compileall_exit_code: 0
latest_s08_001_trace_grader_commit: 9b2e8faf5f573ec11ef2d852fefe41c319fba03f
latest_s08_001_test_commit: e9b5287a9dd20e204113132a9f1efdd8f87f389d
latest_trace_grader_commit: bd4ba024c15f15c43ce86af84e8b9d019fa2dc93
next_agent_handoff_commit: 36a7e6710ada5bc01e244a32d4efdf30ebba5017
next_agent_handoff: DHI_v1/NEXT_AGENT_HANDOFF.md
latest_s05_grader_tests: 11
latest_s05_compileall_exit_code: 0
latest_trace_grader_commit: bd4ba024c15f15c43ce86af84e8b9d019fa2dc93
latest_s05_002_focused_run: afb668ad-5192-4dde-ade4-a273b7a87cc7
latest_s05_003_focused_run: b87b044c-5ea8-4727-9282-2ce2e50b961c
latest_s05_003_focused_tests: 11
latest_s05_003_manifest_validation_run: 6380935a-c19f-4709-8669-2d480129b605
latest_s05_003_exact_manifest_valid: true
latest_s05_003_compileall_exit_code: 0
latest_s05_004_focused_run: f053191d-85db-48ec-8868-dffa35892cf3
latest_s05_004_focused_tests: 11
latest_s05_004_direct_validator_run: 82fe7ca4-62a1-4af7-bbea-71355ecdb8ab
latest_s05_004_exact_manifest_valid: true
latest_s05_004_compileall_exit_code: 0
latest_s05_004_compatibility_run: 486b8ab3-088f-4d96-9d30-cb78eb3ee724
latest_s05_004_compatibility_tests: 72
latest_s05_004_compatibility_note: 71_passed_1_expected_release_literal_mismatch_then_fixed
latest_s05_002_focused_tests: 8
latest_exact_manifest_validation: c34a6a9a-8161-41d9-a654-73483f437724
latest_exact_manifest_valid: true
next_action: validate_orbit_a_s09_001_pre_action_write_effect_prediction
study_0_issue: 2
```
</details>

**No DHI-v1 model capability result is currently established. No DHI-v1 SFT, DPO, RL, or custom latent-predictive training run is authorized.**

## 4. What is implemented

- Deterministic file-workspace environment and pinned SHA-256 fixture.
- Bounded model-to-tool runner with per-turn tool-schema refresh.
- TinyFish Search/Fetch REST adapter with env-only credentials, strict argument validation, public URL protections, explicit task allowlists and trace-safe errors.
- Credential-gated GitHub REST adapter for the six registered read/write capabilities; fake-HTTP and task-bundle tests cover credential redaction, redirect rejection and handler policy. The task-scoped GitHub runtime now binds the manifest-pinned branch precondition, compare-based branch state observer, repository/branch/path write guard and independent artifact readback to the same client. ORBIT-VERIFY-012 passed the full exact-head offline regression (224 tests); live handlers remain unavailable until project-scoped `GITHUB_TOKEN`, explicit write configuration and repository allowlist are attached.
- Adaption Responses API adapter and hosted-model catalogue reader.
- Read-only Adaption connector-catalogue discovery.
- Twelve hand-authored diagnostic seeds: eight common executable cases, one Adaption-specific discovery case, and three unsupported future-runtime cases.
- Plugin-native task profile with 16 exact connected tool contracts pinned in `benchmark/fixtures/plugin_ecology/plugin_tool_registry.json`.
- Synthetic Northstar plugin ecology fixture with source data, untrusted issue content, external snapshots, checkpoint and report artifacts.
- Thirty Stage A task instances across all ten strata recorded in `benchmark/task_manifest.json`.
- Observable grader for tool use, no-tool restraint, recovery, state changes, protected paths, and verified closure.
- Model-facing entrypoints:
  - `python -m DHI_v1.benchmark.run_model_pilot`
  - `python -m DHI_v1.benchmark.run_pilot_benchmark`

## 5. Evidence ledger

| Item | Status | Evidence boundary |
|---|---|---|
| Scripted reference pilot | 8/8 passed | Harness/reference validation only; not an LLM result or training data |
| Historical environment/benchmark tests | 75 passed on 2026-10-31 | Historical run; do not claim latest HEAD is tested |
| ORBIT adjudication gate | Focused tests passed on 2026-10-31 | Gate code verification only |
| INFER-001 hosted inference preflight | Adaption-hosted catalogue read only | Gemma 4 31B was the only selected candidate in that Adaption catalogue; no Adaption Responses inference was run |
| INFER-002 OpenRouter inference preflight | Qwen3.6-35B-A3B and GPT-OSS-20B both listed with tool-capable PrimeIntellect endpoints | OpenRouter balance $0; no free endpoint for either model; no inference was run |
| ADAPTION-001 live platform audit | Completed; read-only | Qwen/Gemma require 10,000 effective training rows; GPT-OSS recipe returned for 300 rows; dataset not eligible; zero credits spent |
| Untouched candidate model screening | Not run | No model winner |
| DHI-v1 executed model trajectories | None recorded | No trajectory SFT source yet |
| DHI-v1 training | Not authorized / not run | Data and benchmark gates remain closed |
| Plugin-native Stage A authoring | 30 tasks materialized; 30 ready for validation | Actual GitHub/TinyFish/Firecrawl tool contracts and pinned evidence; no model runs |
| Plugin reference workflows | Release report and checkpoint-resume report completed | Scripted reference evidence only; not DHI model capability results |
| Plugin-native task grading | Not run | Grader contracts are authored; benchmark task validation still pending |
| TinyFish adapter focused verification | 16 direct assertions passed; six changed Python files compiled in memory | Deepnote run c2d0bac2-7679-4e33-8462-a820d02be2b3. Scripted model-facing integration with mocked HTTP; Fetch hidden unless allowlisted; trace retained result/forecast/closure and omitted key. Pytest/full suite still unverified |
| Historical manifest and trace-grader verification | Passed before TinyFish adapter changes, at code commit cba8421d4f4c6c4f929d5f4c3196eb83f98f7351 | Validator: 30/30 valid, Stage A=30, Stage B=0; full benchmark/environment suite: 142 passed, 0 failed; compileall/import smoke passed. Does not validate later TinyFish adapter changes |
| Full benchmark regression | Passed | Deepnote run 7da82150-e44d-415d-ac00-206b112cf811: 82 benchmark tests passed; manifest validator and benchmark compileall passed at code commit 421955df46975d8b20fba63f8922949a49b4551c. Environment tests were not included |
| Combined benchmark + environment regression | Historical pass before TinyFish adapter changes | Deepnote run 34ca752c-e864-4a3d-9388-957d2c3e1859: 142 passed, 0 failed at code commit cba8421d4f4c6c4f929d5f4c3196eb83f98f7351. Superseded for the plugin-native branch by ORBIT-VERIFY-010 below. |
| ORBIT-VERIFY-009 | Passed | GitHub adapter security regression: 203 tests passed; exact code `cca077e…`; no live GitHub request. See `experiments/ORBIT-VERIFY-009/`. |
| ORBIT-VERIFY-010 | **Passed — latest exact code head** | Code `e045e43d41a5cd125f81dbfdac105937f3a161af`; Deepnote run `3d2f4a00-32e6-422c-b14e-50b158a89e31`; manifest validator, **207 benchmark/environment tests**, compileall, imports and 30-plan loader all passed; 0 model runs enabled. See `experiments/ORBIT-VERIFY-010/`. |
| ORBIT-VERIFY-011 | Passed | Code `cbcccd15be56df159351ac88b4580f07f98e9312`; Deepnote run `0987fae8-a416-4fb5-96d7-522d36b17202`; **209 benchmark/environment tests** passed; fail-closed preconditions and readback-linked artifacts verified offline. See `experiments/ORBIT-VERIFY-011/`. |
| ORBIT-VERIFY-012 | **Passed — latest exact code head** | Code `7f244bf76ccbccec5477b0055d23da5a5931e27a`; Deepnote run `3f2f3b31-86db-46f3-a731-f9f4c502435d`; manifest validator, **224 benchmark/environment tests**, compileall, imports and 30-plan loader all passed; 0 model runs enabled. Task-scoped GitHub runtime verified via fake HTTP only. See `experiments/ORBIT-VERIFY-012/`. |
| ORBIT-S06-LIVE-SMOKE-001 | Artifact/report smoke passed via connected GitHub integration; Deepnote PAT write blocked | Seven pinned fixture blobs verified; report independently read back; compare shows exactly one allowed added file. Deepnote token reads passed, but branch-create and contents-write requests returned HTTP 403. Not a token-backed write pass, model execution, task validation or capability result. See `experiments/ORBIT-S06-LIVE-SMOKE-001/`. |

## 6. Data status and hard stops

- Both 120-row Invent task-spec candidates are quarantined because task-contract JSON was generated as a completion rather than a natural answer/valid execution trajectory.
- The 300-row ORBIT collaboration-behaviour candidate (`169af31f-06e0-4a48-84ab-b84c9f9ce924`) is Invent-sourced and not training-ready: only 98 visible complete pairs were reviewed (25 candidate, 53 revise, 20 reject); 202 rows remain unreviewed. This was model-assisted partial triage, not full independent adjudication.
- The 10,000-row augmented intent dataset (`843888da-28e2-420e-909e-88b203d16404`) has `rephrased_prompt`/`enhanced_completion` columns, but its evaluation input path and config source point to the separate 300-row `c1f4df14-b12c-430c-91ad-e10b559d1cee` dataset and a 100-row sample. Its A grade is not accepted as a certificate for the 10K export. See `experiments/TRAINING-ACCESS-002/`.
- Adaption's evaluation of that dataset returned grade A / 9.4 on a 100-row evaluation sample. This is text-quality metadata, not an agent-capability score and not evidence of executed tool traces.
- Live Adaption recommendations confirmed a 10,000-effective-row minimum for Qwen3.6-35B-A3B and Gemma 4 31B. GPT-OSS-20B returned a LoRA recipe for the 300-row set, but this does not override its provenance/review failure.
- Do not train on any of those datasets, do not promote their Adaption grades to capability evidence, and do not fabricate tool traces or outcomes.
- The primary future SFT evidence must be actual model execution in the DHI environment, with raw tool responses, actual state deltas, predictions, and independently verified postconditions.
- Do not spend Adaption credits until the documented data, benchmark, model, and estimate gates pass.

## 7. Current blockers and platform boundary

Adaption's connected MCP integration is useful for training-registry inspection, dataset inventory/evaluation, data transformation estimates, hyperparameter recommendations and AutoScientist runs, but it does not expose hosted Responses inference. OpenRouter now provides a separate inference route for Qwen3.6-35B-A3B and the mandatory GPT-OSS-20B challenger; both have tool-capable endpoints at PrimeIntellect. The OpenRouter account has **$0 remaining credit**, and no free endpoint was found for either model, so no model call or benchmark run was made.

Current facts:
- Live training registry lists Qwen/Qwen3.6-35B-A3B, openai/gpt-oss-20b, and google/gemma-4-31B-it for supported SFT/DPO methods.
- OpenRouter route audit: Qwen3.6 and GPT-OSS are both present; PrimeIntellect offers Qwen fp8 at $0.01/$0.092 per million input/output tokens and GPT-OSS fp4 at $0.009/$0.038. These are live catalogue prices only; account balance is $0, and no model call was attempted.
- Adaption's recommender returned a Qwen3.6 LoRA configuration for the 10K-row dataset, but its evaluation record points to a different 300-row dataset. No training is authorized until raw rows and lineage are verified.
- The separate hosted Responses catalogue returned six IDs, but only Gemma 4 31B matched a committed candidate. Qwen3.6 and GPT-OSS were absent from that hosted catalogue. Do not treat registry support as inference access.
- A single Gemma call would test only one integration path; it cannot select the primary model against the mandatory GPT-OSS challenger. It is therefore not the next research action.
- The live Adaption recommender rejected Qwen3.6 and Gemma on the 300-row dataset because they require at least 10,000 effective rows. GPT-OSS returned a recipe, but the dataset remains ineligible.
- The recommender did not return a price quote. Dataset generation/adaptation/augmentation actions expose `estimate: true`; the connected training-launch action spends credits and has no estimate field in its exposed schema. Obtain platform cost information before any chargeable launch.
- No DHI-v1 inference, training run, or new dataset-generation job was launched in ADAPTION-001. The OpenRouter preflight was read-only; no model call was made.

Experiment records:
- `DHI_v1/experiments/INFER-001/` — secure runtime and hosted catalogue preflight.
- `DHI_v1/experiments/ADAPTION-001/` — live Adaption model/data eligibility audit.
- `DHI_v1/experiments/INFER-002/` — OpenRouter base-model route and zero-credit preflight.
- `DHI_v1/experiments/TRAINING-ACCESS-002/` — current dataset-lineage and Qwen3.6 training-readiness audit.
- `DHI_v1/experiments/ORBIT-VERIFY-002/` — latest exact-head validator, focused pytest and compileall result.

## 8. Active verification

VERIFY-001 remains a historical blocked attempt on the older Deepnote project. It is superseded for the current manifest/grader code by ORBIT-VERIFY-002.

ORBIT-VERIFY-003 is the combined benchmark + environment regression run. It uses the existing isolated verifier project, pinned code commit `421955df46975d8b20fba63f8922949a49b4551c`, and run ID `f661f5ad-7c5e-48b9-9af6-afda1e6f021b`. The run covers the manifest validator, both test directories, package compileall, and runner/adapter import smoke. Its terminal status is `success`: 136 tests passed; validator, compileall and import smoke passed. See [ORBIT-VERIFY-003](experiments/ORBIT-VERIFY-003/).

The isolated verifier run `52254373-656f-4d0c-841d-c3a2c621d7cc`, against code commit `421955df46975d8b20fba63f8922949a49b4551c`, passed:
- Cross-record manifest validator: `valid=true`, 30 tasks, Stage A=30, Stage B=0, no errors.
- Focused regression tests: 44 passed, 0 failed (20 manifest-validator + 24 plugin trace grader tests).
- `compileall -q DHI_v1/benchmark`: return code 0.

The machine-readable report is committed in `experiments/ORBIT-VERIFY-002/`. This validates the authored harness integrity only; it does not establish model capability or validate any task through model execution.

## ORBIT-GRADER-FIX-001

The trace grader now deterministically handles the Stage A `discovery_sequence` and `branch_state_delta` conditions. It accepts a structured repository forecast recorded on `action_started` (the runner's pre-invocation event) and compares it with independently fetched before/after branch inventories. The model-facing tool schema permits this structured forecast; the local environment preserves it and explicitly marks repository-state comparison as requiring the external-state verifier rather than claiming a filesystem-only match.

The corrected full benchmark + environment regression **passed 142 tests, 0 failures** in Deepnote run `34ca752c-e864-4a3d-9388-957d2c3e1859`, tested at code commit `cba8421d4f4c6c4f929d5f4c3196eb83f98f7351`. Manifest validation (30 tasks, Stage A=30, Stage B=0), compileall for both packages, and import smoke for the runner/adapters also passed. A later direct Git-blob audit compared 11 relevant runtime, benchmark, schema, manifest and test files at that tested commit and the current branch ref; all 11 hashes matched exactly. This establishes code-content equivalence without relying on the broad compare endpoint's aggregate file list; it is not a new test run. The raw report and code-equivalence evidence are in [ORBIT-GRADER-FIX-001](experiments/ORBIT-GRADER-FIX-001/) and [PLUGIN-GATEWAY-001](experiments/PLUGIN-GATEWAY-001/).

Two subsequent notebook retries do not alter that outcome: run `220cc301-c5de-4c33-b507-784d456935d6` stopped without output; run `b401c21c-d586-4a69-8e69-80c6cf02ae43` failed before pytest collection because the notebook cell omitted development-requirement installation. This is a verifier bootstrap issue, not a code regression. See the experiment record for the full adjudication.

## Model execution gap

The DHI model runner now wires the policy-limited TinyFish REST adapter. It exposes only `tinyfish.search` and `tinyfish.fetch_content`, and both are hidden unless the task explicitly lists them in `allowed_tool_ids`. The provider's other 39 native MCP tools remain excluded. A scripted model-facing task verified schema filtering, one Search call, a pre-action no-workspace-change forecast, result capture, secret absence from the trace, and independent closure. This is a harness integration test, not model inference. A live ORBIT model evaluation is still blocked by the lack of an affordable approved inference endpoint and the remaining benchmark validation gates.

### PLUGIN-GATEWAY-001 feasibility result

Provider documentation confirms a possible Streamable HTTP direction, but not a verified DHI runtime route:
- GitHub remote MCP: `https://api.githubcopilot.com/mcp/` and a read-only `/readonly` surface; requires a client-obtained bearer token. The official remote server does not provide authentication, and its native tools have not been schema-matched to the registry's wrapper contracts.
- TinyFish: credential presence, MCP `initialize`/`tools/list`, and bounded provider-native `search`/`fetch_content` calls were verified in the DHI verifier. The DHI adapter uses the documented REST endpoints `https://api.search.tinyfish.ai` and `https://api.fetch.tinyfish.ai`, reads `TINYFISH_API_KEY` from the runtime environment, and sends `X-API-Key`. Only `tinyfish.search` and `tinyfish.fetch_content` are registered in DHI; both require explicit task allowlisting.
- Firecrawl: the standard hosted MCP's generic web tools are not proven equivalent to the registry's Alexandria firecrawl_find_tools; the registered paid firecrawl_scrape remains excluded.

The workspace TINYFISH environment integration is attached to the DHI verifier. The presence-only check returned `TINYFISH_API_KEY_PRESENT=yes`; no key characters were emitted. TinyFish MCP initialize/tools/list and bounded read-only search/fetch calls succeeded. The temporary one-cell test project used for later adapter verification was deleted; the primary verifier notebook remains `DHI ORBIT exact-head verifier` and its original regression cell is untouched. Its machine is stopped. See [PLUGIN-GATEWAY-001](experiments/PLUGIN-GATEWAY-001/) for exact run IDs and limits.

The TinyFish adapter implementation is now present and has passed the focused scripted trace/direct-assertion checks described above. The next gate is to run pytest and the full environment/benchmark regression in a reliable runner; the current Deepnote pytest process times out before collection. GitHub remote MCP execution remains a separate unimplemented provider route. Firecrawl Alexandria schema parity remains unresolved. No model inference/training, provider writes, or paid tool operations are authorized by this adapter work.

## 9. Research methodology now active

- [ORBIT Research Method](docs/13_ORBIT_RESEARCH_METHOD.md) adapts controlled experiments from Karpathy autoresearch and the broader planning/evaluation/regression/adversarial-review workflow from uditgoenka/autoresearch.
- [Experiment record template](experiments/EXPERIMENT_RECORD_TEMPLATE.md) defines the minimum frozen protocol, manifest and run ledger for each research unit.
- This method is now the required operating protocol for benchmark authoring and model research. It does not authorize model inference, training, provider-credit spend, merge or deployment.

## 10. Next authorized action

**Latest verified state — 2026-11-05:** ORBIT-VERIFY-012 passed at the exact code head `7f244bf76ccbccec5477b0055d23da5a5931e27a` with 224 benchmark/environment tests, compileall, imports, manifest validation and 30-plan loader. S06's Deepnote token-backed report write returned HTTP 200 on its sole task-approved path; independent readback and base-to-head compare confirmed exactly one added report file. ORBIT-S06-ADJUDICATION-001 passed 11/11 deterministic checks across seven pinned source fixtures. S06 contract, environment and grader checks are recorded as pass and its family review is accepted. The S06 task remains `ready_for_validation`, because the panel gate below is still open.

**Next authorized work unit:** close the S07 persistent checkpoint/resume gap, beginning with `ORBIT-A-S07-001` and `ORBIT-A-S07-002`. Verify that a resumed run must explicitly re-fetch the pinned checkpoint after resumption, then re-read source evidence, create the task-approved report, fetch it back, and prove the checkpoint-to-result diff is one path. Add a failing regression test before changing behavior. After S07, close S09's pre-action action-effect forecast gap, including the `plugin_prediction_trace_adapter` condition. Do not mark any Stage A task `validated` until both S07 and S09 gates have been closed and independently reviewed.

Current facts:
- Active research branch: `orbit/plugin-benchmark-fixture`; default `main` remains untouched.
- Manifest: status `validation`, not frozen; 30 Stage A tasks and zero Stage B tasks.
- S06: `ready_for_validation`; contract/environment/grader checks pass; family review accepted; execution `not_run`; `model_runs_allowed=false`.
- S07 remains partial: persistence/resumption across a fresh task context must be demonstrated, not inferred from a same-session checkpoint read.
- S09 remains partial: prediction must be a structured trace event before write invocation, then independently compared with observed effects.
- No DHI model inference, candidate comparison or training has run. Dataset lineage and model-access gates remain closed.
- Stage B bodies remain sealed and outside this public branch. No model execution or training is authorized by the S06 artifact/adjudication work.

## 11. Latest committed work

| Commit | Change |
|---|---|
| `74d6d044` | Added model-facing pilot entrypoint |
| `d8b82b6f` | Added ORBIT/DHI-v1 background handover snapshot |
| `efaf0dec` | Linked background snapshot and model-pilot entrypoint |
| `65003263` | Defined Git-first research workflow |
| `f670000b` | Added live workspace state file |
| `8d4a548a` | Made live workspace the repository-root session entrypoint |
| `023f836c` | Made live workspace the DHI-v1 README session entrypoint |
| `218b6dce` | Clarified dated handover is a snapshot, not live state |
| `a5ff6f7c` | Recorded Git-first operating decision in the append-only decision log |
| `e049d7ce` / `0f33f5ce` | Recorded INFER-001 blocked preflight and manifest |
| `4a218d92` | Logged first hosted-inference preflight blocker |
| `5a649db4` | Added secret-presence-only runtime probe; no secret value is emitted |
| `ab9946bd` / `8be08d1c` | Recorded isolated runtime creation and quota rejection in INFER-001 artifacts |
| `9edb4d08` | Appended Deepnote quota rejection; secret presence remained unmeasured at that checkpoint |
| `dff718ac` | Corrected earlier access wording |
| `INFER-001 run b39c478a` | Measured both Adaption key variables absent before integration was attached |
| `INFER-001 run 9e34f54b` | Confirmed `ADAPTION_API_KEY` present after secure integration attachment |
| `INFER-001 run 4bd4a7ba` | Authenticated hosted-model catalogue returned 6 IDs; no inference called |
| `4e8b9bf4` / `34dc832f` | Added ADAPTION-001 read-only model/data eligibility audit and manifest; zero credits spent |
| `64439c9c` | Added controlling nested Stage A/Stage B 120+120 benchmark scope |
| `f734b374` | Aligned model-selection screen protocol to ten-stratum scope |
| `72dac025` | Aligned diagnostic benchmark protocol to Stage A/Stage B scope |
| `bbbc653f` | Recorded dated decision resolving 120-vs-240 scope conflict |
| `0955d719` | Clarified why ten strata replace the six-bucket allocation |
| `8b90f9ac` | Clarified benchmark scope decision rationale in the append-only log |
| `MANIFEST-001` | Added schema-backed 240-task register and source-grounded environment coverage audit; zero task instances created |
| `MANIFEST-001a` | Required task-family split hashes, Stage B sealing metadata, and complete validation evidence before a task can be marked validated |
| `PLUGIN-REGISTRY-001` | Pinned 15 actual connected plugin tool contracts and created the Northstar synthetic plugin fixture |
| `ORBIT-TASKS-001` | Authored ten Stage A plugin-native tasks, one per stratum; manifest passed schema validation |
| `ORBIT-TASKS-002` | Expanded the plugin-native Stage A register to 20 independent task families; schema and cross-record checks passed |
| `ORBIT-TASKS-003` | Added Go release verification and TinyFish schema/404 recovery; Stage A reached 22 task families |
| `ORBIT-TASKS-004` | Expanded Stage A to 30 task instances; S07 checkpoint/resume, additional schema, effect and multi-source cases added |
| `ORBIT-REGISTRY-001` | Corrected missing `mcp__GitHub__update_file` contract and recomputed the 16-tool registry SHA-256 |
| `ORBIT-MANIFEST-VALIDATOR-001` | Added cross-record validator and 17 regression tests; required task-instance/family fingerprints |
| `ORBIT-VERIFY-002` | Manifest validator passed 30/30; 44 focused tests passed; compileall passed at 421955df |
| `INFER-002` | OpenRouter listed Qwen3.6 and GPT-OSS tool-capable endpoints; $0 credits; no inference |
| `TRAINING-ACCESS-002` | Qwen3.6 LoRA recommendation returned for the 10K export; evaluation-lineage mismatch keeps dataset on hold |
| `ORBIT-INTEGRITY-001` | Independent static inspection confirmed 30/30 hashes, registered tools, and complete evidence references; Python tests remain unexecuted |
| `ORBIT-METHOD-001` | Reviewed Karpathy and uditgoenka autoresearch; committed ORBIT's adapted evidence-first method and experiment template |
| `ORBIT-REFERENCE-001` | Verified multi-file GitHub workflow and a persistent checkpoint/resume workflow with readback and single-path diffs |
| `ORBIT-REFERENCE-002` | Verified two-source Node/Python release report, Firecrawl fallback recovery, and branch-effect prediction reference |
| `VERIFY-001 run 93645a78` | Exact checkout verified; compileall passed; pytest blocked by missing package before collection |
| `VERIFY-001` retry | Blocked before execution by Deepnote quota in detached and live modes; retry cell is ready |
| `VERIFY-001` | Initial compileall passed; pytest blocked by missing dependency; retry blocked by Deepnote quota |

This file is the live checkpoint on the active research branch. Always fetch the branch head and this file before continuing; do not infer active branch state from main or chat.

## 12. Session continuation checklist

A new agent must:
1. Read this file from the active research branch.
2. Fetch the latest active-branch head and inspect changes since the last checkpoint; compare with main when needed.
3. Read [the Git-first workflow](docs/12_GIT_FIRST_WORKFLOW.md), [the ORBIT research method](docs/13_ORBIT_RESEARCH_METHOD.md), and the manifest validation report.
4. Read the controlling plan and the exact protocol for the next task, including [the panel integrity checkpoint](benchmark/PANEL_INTEGRITY_VALIDATION_2026-11-03.md).
5. Verify the latest run/experiment from its raw artifact reference—not from a chat message.
6. Continue only the single next authorized action above.
7. Commit every meaningful checkpoint, including failures and blockers, then update this workspace before switching tasks.

Do not use this chat as a handover. The repository must remain sufficient to resume the work.


## 12. Independent launch-readiness adjudication — 2026-11-03

See [ORBIT launch-readiness audit](ORBIT_LAUNCH_READINESS_AUDIT_2026-11-03.md). Independent review confirms the current status is **not ready for model training or release**: no DHI-v1 inference, no model-generated trajectory, no base-model winner, no approved training set, and no DHI-v1 checkpoint.

The TinyFish provider path is verified and the DHI adapter has 16 focused direct assertions plus six in-memory source compilations. These are scripted/mocked adapter checks, not pytest and not ORBIT inference. The old full regressions (136 at `421955d`, 142 at `cba8421`) predate the TinyFish adapter and must not be represented as adapter regression passes.

### ORBIT-VERIFY-004 — exact adapter regression

A frozen verification protocol has been committed in `experiments/ORBIT-VERIFY-004/`. The Deepnote project files were compared against the exact code-under-test commit `5b144c531e8a548787918f0fcdf9e681f05d96e8`; all execution-critical source/test files matched, and the 4,704-line task manifest matched across 19 bounded windows. The experiment runs only a new selected cell. The saved notebook regression cell is not to be executed or modified.

### Launch sequence and planning estimate

The only immediate engineering action is ORBIT-VERIFY-004. After it passes: validate the existing 30 Stage A tasks, close S07/S09, complete the remaining Stage A panel, then obtain funded matched inference for Qwen3.6-35B-A3B and GPT-OSS-20B. Only actual model-execution traces with independently verified outcomes may seed the first ORBIT SFT dataset.

Planning estimate from removal of current hard blockers: first SFT checkpoint approximately **3–6 weeks**, with public-release packaging/independent validation potentially adding **1–2 weeks**. This is conditional on funded inference/compute, a frozen benchmark and valid trajectories; it is not a promised date.

No new provider integration, dataset augmentation, model architecture experiment, DPO/RL run, Stage B exposure, merge, deployment or paid provider action is authorized by this handover.


## 13. Live inference route recheck — 2026-11-03

See [INFER-003](experiments/INFER-003/README.md). The current OpenRouter account read returned **$0 credits** (historical usage $0.20190338). The two planned model candidates do have a common pinned provider route:
- Qwen3.6-35B-A3B — PrimeIntellect fp8, $0.011/M input and $0.10/M output.
- GPT-OSS-20B — PrimeIntellect fp4, $0.016/M input and $0.069/M output.

Both support tool calls and the common `tool_choice=auto` mode. GPT-OSS on this provider does not advertise forced `required` calls; do not use forced-tool tests in the matched comparison.

The current Deepnote verifier has only the `TINYFISH` env integration; no `OPENROUTER` integration/secret is attached. The generic `OpenAICompatibleChatClient` can call an OpenAI-compatible endpoint, but its request body does not yet pin the OpenRouter provider. Before any candidate inference:
1. add an optional, tested provider restriction pinned to PrimeIntellect;
2. provision `DHI_MODEL_API_KEY` as a Deepnote project secret (never in Git/notebook output);
3. set `DHI_MODEL_BASE_URL=https://openrouter.ai/api/v1` and exact candidate IDs;
4. agree a hard aggregate cost cap and matched task/token budgets.

The MCP `send_message` connector is plain-text chat and cannot substitute for the DHI runner's function-call API. Free models exist in the wider catalogue, but they are not substitutes for the frozen Qwen/GPT-OSS screen. No inference call was made.


## 14. Critical correction — plugin manifest is not yet wired to model runner

An exact code-path audit found that the 30 plugin-native task records are authored, but **the current DHI model runner cannot execute them end-to-end**:

- `run_model_pilot.py` runs `pilot_cases.json`, not `task_manifest.json`.
- `benchmark.runner.load_supported_cases` selects only `file_workspace` and optional `adaption_catalogue` pilot cases.
- `DHIEnvironment.DEFAULT_TOOL_CATALOGUE` and `agent_runner.tool_handlers_from_client` expose local filesystem/catalogue tools, Adaption discovery and TinyFish Search/Fetch only.
- GitHub and Firecrawl handlers are absent.
- TinyFish manifest IDs (`mcp__TinyFish__search`, `mcp__TinyFish__fetch_content`) do not match the adapter's current internal IDs (`tinyfish.search`, `tinyfish.fetch_content`); no canonical manifest-to-runner mapping exists.

The 30 task records reference external tool IDs as follows: TinyFish Search 5, TinyFish Fetch 7, Firecrawl discovery 5, GitHub fetch_file 14, GitHub create_file 7, GitHub compare_commits 9, GitHub fetch 2, GitHub create_branch 1, GitHub update_file 2. These are task references and some tasks require multiple providers.

**Status correction:** 30 Stage A tasks are authored and contract-checked, but not all executable through the current ORBIT runner. They are awaiting canonical plugin execution-path integration and validation. The manifest remains authoring/unfrozen; no tasks are validated. Do not author the remaining 90 until the bridge and missing providers work.

### Next authorized engineering sequence

1. Finish ORBIT-VERIFY-004 exact-head regression.
2. Create one canonical tool-ID/permission contract shared by registry, manifest, model-facing schema, handler map and trace.
3. Wire manifest task loading and per-task allowlist into a plugin-native runner profile.
4. Finish GitHub read-only and disposable-branch write handlers; keep deletes/merges excluded.
5. Resolve exact Firecrawl discovery contract; do not substitute generic tools.
6. Execute scripted reference tests, independently grade them, then run model-generated trajectories once inference access is approved.
7. Only after the execution path is proven, validate the existing 30 tasks and expand Stage A to 120.

This correction supersedes any earlier wording that called all 30 tasks ready for validation without qualification.


## 15. ORBIT-VERIFY-004 passed — 2026-11-03

**The TinyFish adapter exact-code regression is now closed.** See [ORBIT-VERIFY-004](experiments/ORBIT-VERIFY-004/README.md).

- Code under test: `5b144c531e8a548787918f0fcdf9e681f05d96e8`.
- Deepnote run: `96ac3bf5-9a06-4a9f-9e80-3bc29c541f38`.
- Manifest validator: PASS — 30 tasks, Stage A=30, Stage B=0, no errors.
- Full benchmark + environment pytest: **158 passed, 0 failed**.
- Compileall: PASS.
- Entrypoint import smoke: PASS.
- Python 3.13.18.
- Raw report: `experiments/ORBIT-VERIFY-004/results/verification-report.json`.

The first attempt, `72a2e697-89b4-4408-beba-c2185b2f95d1`, could not start pytest because the live kernel lacked pytest; it passed manifest validation, compileall and import smoke. The successful retry installed only `DHI_v1/environment/requirements-dev.txt` before testing. The original saved regression cell was not executed or edited.

This closes the **code regression** gate for the pinned TinyFish adapter. It does not validate the plugin-native task manifest through the model runner, and it does not establish learned capability.

### Current next action

Do not repeat ORBIT-VERIFY-004 without a code change. The next engineering work unit is the canonical plugin-native execution bridge:
1. use the exact registry tool IDs consistently in manifest, model-visible schemas, allowlists, handlers and traces;
2. load a task from `task_manifest.json` through a dedicated plugin-native runner, rather than `pilot_cases.json`;
3. retain TinyFish Search/Fetch as fixed-endpoint read-only handlers under the canonical IDs;
4. implement GitHub read operations and disposable-branch writes behind least-privilege credentials and strict path/branch policy;
5. prove the Firecrawl Alexandria `firecrawl_find_tools` contract can be served from the DHI runtime without substituting generic Firecrawl actions;
6. validate the existing 30 tasks through the actual runner before expanding Stage A.

No inference or training is authorized by this successful regression. OpenRouter remains at zero credits and the DHI verifier still lacks a project-scoped `DHI_MODEL_API_KEY` secret and a PrimeIntellect provider pin in the OpenAI-compatible request body. See [INFER-003](experiments/INFER-003/README.md).


## 16. Provider slug resolved for matched inference — 2026-11-03

A live OpenRouter provider catalogue confirms the exact slug for display provider `PrimeIntellect` is `primeintellect`. The matched-run provider pin is therefore fixed as:

```json
{"provider":{"only":["primeintellect"],"allow_fallbacks":false}}
```

Use `tool_choice=auto` for both Qwen3.6-35B-A3B and GPT-OSS-20B. This resolves the provider-name ambiguity only; no client code has been changed and no inference call was made. The remaining blockers are implementation/tests for the provider-routing request field, project-scoped `DHI_MODEL_API_KEY`, funding/cost cap, and the plugin-native execution/benchmark gates. See [INFER-003](experiments/INFER-003/README.md).


## 17. ORBIT-VERIFY-005 passed — canonical plugin loader regression — 2026-11-03

**The manifest task-loader engineering gate is now closed.** See [ORBIT-VERIFY-005](experiments/ORBIT-VERIFY-005/README.md).

- Code under test: `ea3269aec35527386804ac357a953933de31fbf0`.
- Deepnote run: `384fec58-6f67-407a-b599-301b3b9de74a`.
- Manifest validator: PASS — valid=true, 30 tasks, Stage A=30, Stage B=0, no errors.
- Full benchmark + environment pytest: **166 passed, 0 failed**.
- `compileall`: PASS.
- Entrypoint import smoke: PASS.
- Plugin loader smoke: **30 plans resolved; zero model runs enabled**.
- Python: 3.13.18.
- Raw report: `experiments/ORBIT-VERIFY-005/results/verification-report.json`.

Eight new focused tests verify canonical provider IDs, per-task policy filtering, write-decoy denial, sandbox-write allowlisting, schema fingerprint checks, unknown-tool rejection, and disabled model execution. The permission red test demonstrated that an unrelated side-effect label (`external_purchase`) could not grant read-only access; the policy mapping was narrowed to explicit read/discovery labels or declared create/update workflows.

### Correct next engineering step — plugin-native runner bridge

The loader is **not** the runner. The current agent runner still executes the deterministic file-workspace pilot and cannot execute the 30 manifest tasks end-to-end. No GitHub or Firecrawl handlers exist, and TinyFish internal tool IDs still differ from the pinned registry IDs. The next work unit must:

1. load a `PluginTaskPlan` into a dedicated plugin-native agent runner;
2. construct the model-visible tool schemas from exact, pinned provider contracts using canonical IDs;
3. fail before model invocation if any required task tool has no callable, schema-attested handler;
4. enforce both task allowlists and tool-argument/path/branch permissions at dispatch time;
5. capture pre-action prediction, action-start, raw provider result, independent readback, actual effect, and postcondition evidence in the plugin trace;
6. use the existing independent grader to score the 30 tasks through real handlers, not hand-authored scripted outcomes.

Provider status remains:
- TinyFish Search/Fetch: DHI REST implementation and live provider smoke verified, but native registry schema parity/canonical ID mapping still needs to be made explicit.
- GitHub: no DHI runtime handler or Deepnote project secret. Implement read-only actions first; writes only in disposable branches with exact allowed paths and SHA preconditions. Deletes/merges remain excluded.
- Firecrawl Alexandria discovery: exact `firecrawl_find_tools` contract remains unresolved; generic Firecrawl search/scrape is not a valid substitute.

Keep benchmark expansion frozen at 30 until this execution path works and tasks are independently validated. All 30 manifest tasks still have `model_runs_allowed=false`. No inference or training is authorized by this engineering pass.


## 18. Connector availability clarification — 2026-11-03

The previous provider-gap wording needs a precise correction:

- The connected assistant session **does** expose GitHub MCP actions, including `fetch_file`, `create_file`, `update_file`, `compare_commits`, `create_branch`, and read-only `fetch`.
- The connected assistant session **does** expose Firecrawl Alexandria's exact `mcp__Firecrawl__firecrawl_find_tools` action. Its contract requires an objective and optionally accepts query, URL, category/provider/capability selectors, expansion level, and pagination. Discovery is free and returns further capability contracts; it does not execute the discovered provider itself.
- These actions are callable by the assistant through its connected tool session. They are **not currently callable by the ORBIT model runner in Deepnote**. A live Deepnote integration search for `FIRECRAWL` and `GITHUB` returned no attached integrations. The verifier's attached integration remains `TINYFISH`.
- The tool registry's canonical contracts are therefore known; what is missing is a runtime transport/credential boundary that makes those operations available to the model runner and records their real results.

Do not claim that Firecrawl/GitHub do not exist or that their contracts are unknown. The accurate status is: assistant-session connector available; Deepnote runtime adapter and project-scoped authentication not yet provisioned. For Firecrawl, confirm the supported Alexandria transport before assuming a standard REST API key alone reproduces `firecrawl_find_tools`. For GitHub, a least-privilege project secret plus a tested REST/MCP adapter is still required.

The remaining execution bridge must continue to fail closed when the DHI runtime lacks a required handler, even though the assistant's own connected tools can perform the same operation outside the tested ORBIT runtime.


## 19. Provider adapter priority from exact task-level coverage — 2026-11-03

A fresh parse of the 30 task records confirms required external-tool coverage (task counts, not tool-call references):

| Required provider namespace | Tasks | Runtime state |
|---|---:|---|
| TinyFish | 7 | REST client and project secret exist; canonical IDs still need alignment to the registry |
| GitHub | 16 | Host connector available to the assistant; no Deepnote project integration or DHI runtime handler |
| Firecrawl | 5 | Alexandria discovery action available to the assistant; no Deepnote project integration or DHI runtime handler |
| No required external provider tool | 2 | Local/deterministic scope |

There are **zero tasks requiring multiple provider namespaces as mandatory tools** in the current Stage A panel. Some fixtures may contain source snapshots from another provider; those do not count as required model tool calls.

### Adapter order

1. **TinyFish canonicalization** is the fastest next adapter: change the DHI internal tool IDs to the manifest/registry IDs (`mcp__TinyFish__search`, `mcp__TinyFish__fetch_content`) and expose the exact schemas/handlers to the plugin dispatch boundary. This can unlock up to 7 tasks after independent task/trace validation.
2. **GitHub REST runtime bridge** is the highest-coverage next adapter: implement only the registered read operations and task-guarded disposable-branch create/update actions, with a project-scoped least-privilege token and SHA/path preconditions. This is the largest slice (16 tasks).
3. **Firecrawl Alexandria bridge** follows: the connected assistant action and full contract are known, but its callable Deepnote/MCP transport is not provisioned. Do not substitute generic search/scrape for `firecrawl_find_tools`.

All live manifest tasks still have `model_runs_allowed=false`. This coverage count does not authorize model execution, and adapter availability alone does not validate any benchmark task.


## 20. ORBIT-VERIFY-006 passed — plugin execution boundary regression — 2026-11-03

**The fail-closed plugin dispatch boundary now passes the full exact-head regression.** See [ORBIT-VERIFY-006](experiments/ORBIT-VERIFY-006/README.md).

- Code under test: `410d1113231cef020dc72292ccf2496e580f803e`.
- Deepnote run: `6591b36d-6233-4443-b9e0-fbf4b0ac1197`.
- Manifest validation: PASS — 30 tasks, Stage A=30, Stage B=0, no errors.
- Full benchmark + environment pytest: **174 passed, 0 failed**.
- Compileall and entrypoint imports: PASS.
- Manifest-loader smoke: all 30 task plans resolve; model runs enabled: **0**.
- Synthetic dispatch smoke: canonical TinyFish tool IDs prepared and a fake-handler read-only call dispatched.
- No actual provider calls, paid requests, or training jobs.
- Python: 3.13.18.
- Raw report: `experiments/ORBIT-VERIFY-006/results/verification-report.json`.

This validates the task loader and generic dispatch boundary, not a complete agent runner. The model-turn loop, plugin trace generation, environment-specific state snapshots, independent postcondition grading, and real GitHub/Firecrawl handlers are still not connected. Do not call the manifest tasks end-to-end executable yet.

### Next work unit: TinyFish canonical provider bundle

The current DHI TinyFish REST adapter exposes internal IDs `tinyfish.search` and `tinyfish.fetch_content`; the manifest registry requires `mcp__TinyFish__search` and `mcp__TinyFish__fetch_content`. The focused plugin-dispatch smoke used synthetic handlers with canonical IDs; it did not call TinyFish. The next TDD unit should:
1. align the adapter's published IDs with the manifest IDs;
2. return the exact input schemas and callable handlers under those canonical IDs;
3. prove the bundle matches all TinyFish registry references and fails closed if the key/handler is absent;
4. verify the actual DHI runtime can prepare the TinyFish-only task plan using the real attached `TINYFISH` integration, but keep model runs disabled;
5. rerun the full suite.

After TinyFish, prioritize the GitHub REST adapter because 16 Stage A tasks require GitHub; keep writes limited to task-specific disposable branches and exact allowed paths. Firecrawl's Alexandria `firecrawl_find_tools` contract is known in the assistant session, but the Deepnote verifier has no Firecrawl project integration/transport. The assistant's connected app actions are not callable by the model runner.

OpenRouter is still at $0 credits, and there is no `OPENROUTER` Deepnote integration. No model inference or training is authorized by this successful engineering gate.


## 21. ORBIT-VERIFY-007 passed — canonical TinyFish runtime bundle — 2026-11-03

**The TinyFish canonical adapter gate is closed.** See [ORBIT-VERIFY-007](experiments/ORBIT-VERIFY-007/README.md).

- Code under test: `28a0753c283cd0105d103ee4da11ac0847af0014`.
- Deepnote run: `ec2a3f4f-b421-41a8-9187-92ad21ed1dc2`.
- Full benchmark + environment pytest: **178 passed, 0 failed**.
- Manifest validator: PASS — 30 tasks, Stage A=30, Stage B=0, no errors.
- `compileall` and import smoke: PASS.
- Loader smoke: all 30 plans resolve; model runs enabled: **0**.
- Actual Deepnote TINYFISH no-network preflight: PASS — schemas and callable handlers exist for canonical IDs `mcp__TinyFish__search` and `mcp__TinyFish__fetch_content`; `ORBIT-A-S02-001` prepares successfully through `prepare_plugin_execution`.
- Actual provider calls / model inference / training: **0**.
- Python: 3.13.18.
- Raw report: `experiments/ORBIT-VERIFY-007/results/verification-report.json`.

The old internal aliases `tinyfish.search` and `tinyfish.fetch_content` have been replaced by the exact plugin registry IDs. `tinyfish_plugin_bundle_from_env()` returns registry-aligned schemas regardless of credentials and exposes handlers only when `TINYFISH_API_KEY` exists. The actual attached Deepnote TINYFISH environment supplied both handlers. No key value is printed or stored in source.

### What this does not close

The generic plugin dispatcher is still not wired into the model-facing turn loop, and no action trace is yet emitted in the ORBIT plugin trace schema. Therefore, the 7 TinyFish-requiring tasks are **adapter-preparable**, not end-to-end benchmark validated. The source manifest continues to mark every task `model_runs_allowed=false`.

### Next work unit — model-facing plugin runner and trace

Build this test-first, initially with scripted local clients/handlers and no live model:
1. load one `PluginTaskPlan` and call `prepare_plugin_execution` before any model request;
2. send its canonical model-visible function schemas through a bounded model-client interface;
3. dispatch each tool call through the existing guarded dispatcher;
4. record append-only `task_started`, pre-action `assistant_prediction`, `action_started`, `action_executed`, and `task_closed` events using the existing plugin trace schema;
5. capture only independently grounded raw handler results and before/after state/effect data; do not let model-authored summaries stand in for verified effects;
6. validate the final trace with `plugin_trace.validate_trace` and grade it with `grade_task`;
7. add a scripted TinyFish task test proving schema/permission/trace/closure behaviour without calling a provider.

Only after this runner/trace path is tested should GitHub's 16-task runtime bridge be implemented. Firecrawl Alexandria's assistant-session tool contract is known, but no Deepnote project transport/integration is attached. OpenRouter also remains at $0 credits, with no project-scoped model secret. Do not enable live model runs or start training yet.


## 22. ORBIT-VERIFY-008 passed — scripted model-facing plugin runner — 2026-11-03

**The provider-agnostic plugin runner, append-only trace and deterministic grading path now pass the full engineering regression.** See [ORBIT-VERIFY-008](experiments/ORBIT-VERIFY-008/README.md).

- Code under test: `fec93ba59842d866149c7d03383b1833745077d2`.
- Deepnote run: `570dd432-474f-4520-8f17-700d480358bb`.
- Full benchmark + environment pytest: **182 passed, 0 failed**.
- Manifest validation: PASS — all 30 Stage A tasks valid, no errors.
- Compileall and entrypoint import smoke: PASS.
- Loader smoke: all 30 task plans resolve; model runs enabled: **0**.
- Focused runner tests: **4 passed**.
- No hosted model, provider, or training calls.
- Python: 3.13.18.
- Raw report: `experiments/ORBIT-VERIFY-008/results/verification-report.json`.

### What is now implemented

`DHI_v1/benchmark/plugin_runner.py` runs a bounded model-client/tool loop from an already prepared `PreparedPluginExecution`. It:
- requires both the original manifest task record and prepared task plan to allow model execution;
- presents canonical function schemas and adds optional pre-action forecast metadata;
- removes that metadata before strict argument validation;
- sends every function call through the fail-closed dispatcher;
- emits append-only `task_started`, `assistant_prediction`, `action_started`, `action_executed`, and `task_closed` events;
- derives state-effect records from independently supplied before/after hash maps;
- refuses sandbox-write tasks without an independent state observer;
- validates trace sequence/schema and calls the deterministic task grader.

The scripted test uses a fake GitHub read handler. It proves a read-only fetch can be dispatched and graded, while a visible-but-denied write tool is rejected before handler invocation.

### Boundary that remains open

This does not prove a hosted model can solve the task or call real providers. The runner has not yet been connected to a callable GitHub/Firecrawl provider transport, and the task-level external snapshot graders are not all independently implemented. The source manifest still has `model_runs_allowed=false` for every task. Do not change those flags in this step.

### Next work unit — GitHub canonical REST runtime bundle

GitHub appears in **16 of 30** Stage A task records, the largest provider slice. The assistant's connected GitHub actions are not callable by the Deepnote runner; a project-scoped integration or a tested REST transport is required. Build the REST bundle using the exact registry IDs, with a separate capability allowlist and a task-specific write guard.

Initial required registered IDs (from the frozen task manifest):
- read: `mcp__GitHub__fetch_file`, `mcp__GitHub__fetch`, `mcp__GitHub__compare_commits`;
- write: `mcp__GitHub__create_branch`, `mcp__GitHub__create_file`, `mcp__GitHub__update_file`.

Implementation order:
1. add red tests for the schemas/handler bundle and absence of handlers when the runtime token is not configured;
2. add the bounded stdlib HTTP transport, allow only `api.github.com`, cap response size/time, redact tokens and response errors, disable automatic retries, and validate response JSON/base64;
3. implement read-only operations first, then create/update/branch methods with exact request contracts;
4. expose canonical IDs and schemas only; no token value may be logged or included in trace events;
5. return write handlers but do **not** provide a generic write guard—the task-specific guard remains mandatory in `prepare_plugin_execution`;
6. fake-HTTP test each request and response shape, prove unknown hosts/paths and malformed inputs fail closed, then prepare real manifest GitHub task plans with fake handlers;
7. verify whether a `GITHUB_TOKEN` is actually attached to Deepnote without printing its value. If no token is present, leave GitHub handlers absent and record the blocker; do not substitute assistant-session GitHub actions.

Do not call live repository writes. Writes must be confined to the task's explicitly allowed disposable branch/path and independently checked with readback and compare-commits. The 16-task coverage is not authorization to execute them.

Firecrawl Alexandria's assistant-session contract remains available here, but Deepnote has no Firecrawl project transport. OpenRouter remains at $0 credits and no project-scoped model credentials exist. Model inference and training remain blocked until the runtime and measurement gates are independently closed.


## 23. ORBIT-VERIFY-008 passed — scripted plugin runner / trace / grader — 2026-11-03

**The provider-agnostic model-facing plugin loop now passes full engineering regression.** See [ORBIT-VERIFY-008](experiments/ORBIT-VERIFY-008/README.md).

- Code revision: `fec93ba59842d866149c7d03383b1833745077d2`.
- Deepnote run: `570dd432-474f-4520-8f17-700d480358bb`.
- Full benchmark + environment pytest: **182 passed, 0 failed**.
- Manifest validator: PASS — 30 Stage A tasks, Stage B=0, no errors.
- Compileall and entrypoint import smoke: PASS.
- Loader smoke: all 30 plans resolve; model runs enabled: **0**.
- Focused runner suite: **4 passed**.
- No model, provider, or training calls.
- Python: 3.13.18.
- Raw report: `experiments/ORBIT-VERIFY-008/results/verification-report.json`.

### Current ORBIT implementation

1. `plugin_task_loader.py` resolves the immutable task manifest against the pinned registry.
2. `plugin_execution.py` exposes canonical schemas and enforces strict JSON Schema arguments, permission allowlists, handler presence and exact-task sandbox-write guards.
3. `plugin_runner.py` calls a bounded chat-completion client, routes every tool call through the prepared dispatcher, captures independent state hashes, writes append-only trace events, validates them with `plugin_trace.schema.json`, and invokes `grade_task`.
4. The TinyFish adapter publishes canonical `mcp__TinyFish__search` and `mcp__TinyFish__fetch_content` IDs; the actual Deepnote TINYFISH integration can prepare the TinyFish-only task with no network request.

The runner test is deliberately scripted and uses fake GitHub read handlers. It proves the end-to-end local mechanics, not hosted-model capability or a real provider task.

### Next work unit — GitHub canonical REST runtime bundle

The exact task manifest shows **16 of 30** Stage A tasks require GitHub. The assistant's connected GitHub MCP actions are available in this conversation but are not callable by the Deepnote model runner. Deepnote still has no attached GitHub project integration.

Build an independent stdlib REST client that:
- exposes canonical registry IDs `mcp__GitHub__fetch_file`, `mcp__GitHub__fetch`, `mcp__GitHub__compare_commits`, `mcp__GitHub__create_branch`, `mcp__GitHub__create_file`, and `mcp__GitHub__update_file`;
- returns exact schema/handler bundles only when `GITHUB_TOKEN` is attached;
- allows writes only when the explicit runtime write flag and allowed-repository list are configured;
- never supplies a generic write guard; `prepare_plugin_execution` still requires a task-specific path/branch guard;
- enforces HTTPS/API host allowlists, response/time limits, no automatic retries, and redacted exception messages;
- uses fake HTTP transport tests first and performs no live repository mutation.

The first preflight must print only boolean presence/configuration states, never a credential value. If the GITHUB token is absent, handler exposure stays empty; do not substitute the assistant's own connected tools.

Firecrawl Alexandria has a known assistant-session contract, but no Deepnote project transport. OpenRouter is still at $0 credits. **All 30 source-manifest tasks remain `model_runs_allowed=false`**; no model inference or training is authorized yet.


## 24. GitHub adapter security hardening — 2026-11-03

**Branch revision:** `cca077e9c5c6b50fffee94ea3c74576c89c34462`  
**Previous verified code revision:** `fec93ba59842d866149c7d03383b1833745077d2`  
**Deepnote verifier:** project `6415944e-8d6c-432c-a7cf-3bbaa997799c`, notebook `3639f9a98ce5435fa4cd0168eaaca3a1`.

The first review of `environment/github_client.py` identified a credential-forwarding risk: Python's default `urllib` redirect handler copies request headers, including Authorization, into the redirected request. The adapter now supplies `_RejectRedirects` when constructing both authenticated API and unauthenticated raw-host openers. Redirects are rejected before any second request is sent.

Two test defects were also corrected:
- Manifest bundle tests now pass only handlers visible to the selected task, as required by `prepare_plugin_execution`.
- Fake handler lambdas capture each tool ID at creation time rather than late-binding the loop variable.
- The synthetic S06 guard now names a disposable sandbox branch, not the active research branch.

A new regression test verifies that the default client opener is configured with the redirect-rejecting handler and that a cross-host redirect is refused. The implementation and both test files were synced to Deepnote and byte identity was checked.

### Validation status

- The initial selected test attempt stopped before collection because `pytest` was absent from the live Deepnote kernel; this is an environment/bootstrap failure, not a code result.
- Focused selected pytest completed successfully in Deepnote run `5855c01e-c3cc-4248-be3a-5ae165d2f70f`: **21 passed, 0 failed** in 112.39 seconds across `test_github_client.py` and `test_github_plugin_bundle.py`. The project kernel first installed the checked-in development requirements; no external GitHub request was made.
- The full exact-revision regression is running as ORBIT-VERIFY-009 in Deepnote run `a249a76e-6454-4ca8-b9c4-64ca6a098c2f`, with manifest validation, all benchmark/environment tests, compileall, import smoke and 30-plan loader smoke. Its branch snapshot is `eb0f681d13b333b6b4c03b5b14f9555ca624a6ef`; GitHub adapter source under test is `cca077e9c5c6b50fffee94ea3c74576c89c34462`.
- Deepnote presence-only preflight: `GITHUB_TOKEN=false`, `DHI_GITHUB_WRITES_ENABLED=false`, `GITHUB_ALLOWED_REPOSITORIES=false`, `TINYFISH_API_KEY=true`.
- No real GitHub HTTP request, repository write, model inference, or training job occurred.

### Remaining integration gaps

The generic runner still does not enforce manifest preconditions such as S06's required branch-head SHA before a model call, and it does not automatically populate `trace.final_artifacts` from independently read-back files. Therefore the GitHub adapter is not yet sufficient to make S06 end-to-end gradeable. These must be closed separately before any task execution is authorized. All manifest model-run flags remain false.

### Secret request boundary

Do not add a GitHub credential until the offline security and focused pytest gates pass. When requested, start with a fine-grained, read-only token scoped to the one required repository. Keep write handlers disabled; request a separate write-capable scope only after disposable-branch isolation and task-specific precondition checks are verified.


## 25. ORBIT-VERIFY-010 passed — latest exact-head offline regression — 5 November 2026

**Code under test:** `e045e43d41a5cd125f81dbfdac105937f3a161af` on `orbit/plugin-benchmark-fixture`.

**Deepnote evidence**
- Project: `6415944e-8d6c-432c-a7cf-3bbaa997799c`.
- Notebook: `3639f9a98ce5435fa4cd0168eaaca3a1`.
- Run: `3d2f4a00-32e6-422c-b14e-50b158a89e31`.
- Full pytest: **207 passed, 0 failed** across `DHI_v1/benchmark/tests` and `DHI_v1/environment/tests`.
- Manifest validator: valid, 30 tasks, Stage A=30, Stage B=0, no errors.
- `compileall`: passed.
- Entrypoint imports: passed.
- Plugin task loader: all 30 plans resolved; model runs enabled: 0.
- Python 3.13.18; Linux x86_64.
- Raw command output, timings and exit codes: `experiments/ORBIT-VERIFY-010/results/verification-report.json`.

**Evidence boundary:** this is offline engineering verification only. It did not call GitHub, TinyFish, a hosted model, or a training API. It does not validate any of the 30 benchmark tasks through model execution and does not establish DHI capability or training readiness.

### Remaining benchmark gaps (not closed by the 207-test pass)

1. **Preconditions before model invocation:** `run_plugin_task` must evaluate task-manifest preconditions against a trusted runtime observer before the first model request. S06-001 specifically requires the sandbox branch head to equal its pinned base commit. A model must not be asked to proceed when that check fails or cannot be observed.
2. **Artifact evidence:** `trace.final_artifacts` must be populated only from independently fetched/read-back artifact metadata and content hashes. It must not be inferred from the final answer, a model-authored path, or a provider write response alone.
3. **Live provider readiness:** the GitHub client is offline-tested, but the Deepnote project previously reported no `GITHUB_TOKEN`, write-enable flag or allowed-repository list. No live GitHub call was made.
4. **Task validation:** all 30 remain `ready_for_validation`, not `validated`; independent grader review and per-task evidence checks remain outstanding. Stage B remains sealed and empty.

All `model_runs_allowed` flags stay false. No DHI inference or training is authorized.

### Next authorized work unit

Implement a fail-closed precondition evaluator with explicit runtime state observers (starting with `branch_head_equals`) and an artifact collector that uses independent provider readback. Add red tests for satisfied, mismatched and unavailable preconditions; missing, mismatched and unverified artifacts; and task/path constraints. Then rerun ORBIT-VERIFY exact-head regression. Keep the benchmark flags false.


## 26. ORBIT-VERIFY-011 passed — preconditions and artifact readback — 5 November 2026

**Code under test:** `cbcccd15be56df159351ac88b4580f07f98e9312` on `orbit/plugin-benchmark-fixture`.

- Deepnote project `6415944e-8d6c-432c-a7cf-3bbaa997799c`; notebook `3639f9a98ce5435fa4cd0168eaaca3a1`; full run `0987fae8-a416-4fb5-96d7-522d36b17202`.
- Manifest validator passed: 30 tasks; Stage A=30; Stage B=0.
- Full benchmark/environment pytest: **209 passed, 0 failed**.
- Compileall, entrypoint imports and 30-plan plugin loader passed; zero model runs enabled.
- Implemented fail-closed manifest preconditions before model calls, independently read-back final artifacts, Git blob/content SHA verification, and trace-level linkage from a final artifact to its verified readback event and successful earlier write.
- Evidence is offline/scripted only. No live GitHub, TinyFish, hosted model or training API was called.
- All 30 tasks remain `ready_for_validation`; Stage B remains sealed; training is not authorized.

See `experiments/ORBIT-VERIFY-011/` for the experiment README, manifest and raw verifier output.

## 27. ORBIT-VERIFY-012 passed — trusted task-scoped GitHub runtime — 5 November 2026

**Historical status snapshot:** the integration/branch bullets in this section describe the state immediately after ORBIT-VERIFY-012 and before the follow-up configuration and S06 smoke. They are superseded by the current status block above and Section 28 below.


**Code under test:** `7f244bf76ccbccec5477b0055d23da5a5931e27a` on `orbit/plugin-benchmark-fixture`.

**Deepnote evidence**
- Project `6415944e-8d6c-432c-a7cf-3bbaa997799c`; notebook `3639f9a98ce5435fa4cd0168eaaca3a1`.
- Full run `3f2f3b31-86db-46f3-a731-f9f4c502435d`; verifier block `d76385ef1ba24707ae3f97b7bef2987e`.
- Manifest validator: valid; 30 tasks; Stage A=30; Stage B=0; no errors.
- Full benchmark/environment pytest: **224 passed, 0 failed** in 421.51 seconds.
- Compileall: passed; entrypoint imports: passed; plugin manifest loader: 30 plans resolved, zero model runs enabled.
- Focused trusted-runtime/runner regression: 45 passed.
- Python 3.13.18; Linux; full verifier finished at `2026-11-05T07:48:16Z`.

### Runtime invariants now verified offline

1. The runner checks the manifest-pinned branch-head precondition before repository state observation or model execution. Failed/unavailable preconditions close blocked with no model call.
2. State snapshots are captured through the trusted GitHub compare client from the pinned base SHA to the task's dedicated sandbox branch. Provider-reported status/blob metadata is fingerprinted per changed path.
3. Writes are guarded by exact task ID, repository, branch and postcondition-derived allowed paths.
4. Final artifacts are independently read back from the same repository/branch/path and content is checked against the Git blob SHA before entering `trace.final_artifacts`.
5. The GitHub task wrapper supplies the trusted precondition, state and readback callbacks; callers cannot substitute an empty state observer.

**Evidence boundary:** these are offline engineering tests and fake GitHub HTTP tests. No live GitHub request or write, TinyFish request, hosted-model inference, training job or dataset-generation job occurred. This does not establish ORBIT model capability or validate the 30 benchmark tasks through model execution.

All 30 Stage A tasks remain `ready_for_validation`; Stage B is sealed and empty; all `model_runs_allowed` flags remain false; training remains unauthorized.

### Remaining blockers and next action

- The Deepnote project currently has environment integrations `TINYFISH` and `ADAPTION` only. No GitHub environment integration is attached. The presence-only check reported `GITHUB_TOKEN=false`, `DHI_GITHUB_WRITES_ENABLED=false`, and `GITHUB_ALLOWED_REPOSITORIES=false`.
- A GitHub ref lookup returned HTTP 404 for `refs/heads/orbit/sandbox/orbit-a-s06-001`; the dedicated S06 sandbox branch is not present.
- Attach a project-scoped GitHub environment integration with the three required variables; never put the token in a notebook, source file, Git commit or chat message.
- After access and isolation are explicitly approved, provision the task-scoped S06 sandbox branch at its exact manifest-pinned base commit, then run one controlled live smoke path: verify branch head, read source fixtures, write only the approved report path, independently read it back, and verify the branch diff.
- Independently review/validate all 30 Stage A tasks before any model-run permission is considered. Stage B stays sealed. No inference or training is authorized.

See `experiments/ORBIT-VERIFY-012/` for the experiment README, manifest and raw verifier output.


## 28. ORBIT-S06-LIVE-SMOKE-001 — artifact verified; Deepnote write credential blocked — 5 November 2026

- Task: `ORBIT-A-S06-001`; sandbox branch: `orbit/sandbox/orbit-a-s06-001`.
- Pinned base: `af6c0d31fcf2e3232cb427c421850536139e3b3a`.
- Report commit: `3b9b8be6a4c5d2ad22306e67288e7ba1dc975d0f`.
- Only the manifest-approved path was added: `DHI_v1/benchmark/fixtures/plugin_ecology/reports/release-readiness.md`.
- Report blob SHA: `cca5127e66bc698f5c9cdfd8135a33ab45c8d985`; exact readback passed.
- Seven pinned source fixture blobs were verified. Deepnote read-only verification run: `e2d0364a-d717-403d-b713-cee990b78414`.
- Base-to-head compare: ahead=1, behind=0; exactly one added file; 51 insertions and zero deletions.
- Derived data: 8 not Done / 35 estimated hours; 4 Open / 19 hours; acceptance 3 Passed, 1 Blocked, 1 Not Run and 1 Failed.
- The report identifies the AT-03 release-note/acceptance conflict, AT-06 failure, AT-05 Not Run state and dependency roots NS-101/NS-105.

### Write credential boundary

The project integration is attached and the three environment settings are present. The Deepnote token can read the repository and pinned commit (HTTP 200), but GitHub rejects both its `POST /git/refs` branch-creation request and its `PUT /contents/{path}` report-write request with HTTP 403, `Resource not accessible by personal access token`.

The connected GitHub repository integration provisioned the branch and created the report. Deepnote then independently verified the report and diff in read-only mode. This completes the artifact/report smoke only; it does **not** prove token-backed Deepnote writes, a model-driven task run, independent task validation or ORBIT capability.

Next: confirm the fine-grained token has Contents read/write access for only the `dhi` repository and any required approval, update the Deepnote `GITHUB_TOKEN` secret, and rerun a narrow write preflight against this existing branch. Do not create another branch or rewrite the report.

All 30 Stage A tasks remain `ready_for_validation`; S06 `model_runs_allowed=false`; Stage B stays sealed and empty. No model calls, training, issue/source/configuration/deployment changes occurred. Default `main` remains untouched.


### 2026-11-05 follow-up after PAT permission update

The user reported changing the same fine-grained PAT to read/write. Deepnote rechecked the exact same project integration. Repository and report reads still work, but the non-mutating create-ref probe on the already-existing S06 ref and the intentional wrong-blob-SHA contents update probe both returned HTTP 403, `Resource not accessible by personal access token`. The branch head and report blob remained unchanged; no mutation occurred. Deepnote run: `652a27e7-954d-4583-9bec-30a8573f346d`.

The project integration metadata still exposes its original creation timestamp; the project machine remains running. No restart was attempted because the observed failure is an authorization response, not an environment-presence failure. Recheck that the active fine-grained token is granted Contents: Read and write for `Kshitijpalsinghtomar/dhi`, that any pending owner approval is granted, and that the Deepnote integration contains the current token value if it was regenerated. Do not expose token text. Token-backed runtime writes remain blocked; all benchmark/model gates remain unchanged.


### Final permission diagnostic — 5 November 2026

Deepnote run `907a8bfa-6aa9-4468-b726-55de63229c29` confirmed the configured token is valid (`GET /user` returned 200), authenticates as the repository owner, and reads the current S06 branch. However, a duplicate-ref write probe still returns HTTP 403, `Resource not accessible by personal access token`. GitHub's `X-Accepted-GitHub-Permissions` response header explicitly requires `contents=write`. No repository mutation occurred. The effective Contents write grant is still missing or pending approval for the token Deepnote is using. The next action is to inspect the active fine-grained PAT's exact repository selection, Contents permission and approval status; replace the Deepnote secret only if GitHub generated a new token value. Do not grant Actions/Workflows or broader permissions; the reported requirement is `contents=write`.


## 29. ORBIT-S06-LIVE-SMOKE-001 — Deepnote Contents-write permission verified — 5 November 2026

- The user reported updating the GitHub PAT permission. The Deepnote integration metadata changed after the prior blocked check; the next probe ran in the live notebook kernel using the configured `GITHUB_TOKEN`.
- Deepnote project: `6415944e-8d6c-432c-a7cf-3bbaa997799c`; notebook: `3639f9a98ce5435fa4cd0168eaaca3a1`.
- Run: `3c722666-6e68-46c6-ae57-ccf76b256dbd`; verifier block: `e4c9f16ba86540d992e67c1392b5304e`.
- Token presence, write-enable flag and exact repository allowlist all passed.
- The existing S06 branch and report were read first and matched the pinned head/blob values. The verifier then submitted the existing report with a deliberately impossible all-zero blob SHA. GitHub returned HTTP 409 with the expected stale-SHA mismatch, proving the token passed the Contents-write authorization check and reached the update concurrency check.
- The branch head and report blob were read again and remained unchanged. Repository mutations: **0**. Token value exposed: **false**.
- **Credential result:** Deepnote `Contents: write` permission preflight passed. The preflight did not perform a valid content write; the branch and report remain originally provisioned by the connected GitHub repository integration. Do not describe this as a completed token-backed artifact write or end-to-end model task run.
- Historical HTTP 403 diagnostics are retained in Section 28 and the experiment ledger; they are superseded by this successful post-update permission check.

### Research gates unchanged

S06 remains `ready_for_validation`; all 30 Stage A tasks remain `ready_for_validation`; Stage B remains sealed and empty; all `model_runs_allowed` flags remain false; training remains unauthorized. No model inference, model-generated trajectory or training job was executed. No change was made to default `main`.


## 30. ORBIT-S06-ADJUDICATION-001 — artifact write and deterministic checks passed; panel gate remains — 5 November 2026

- Task: `ORBIT-A-S06-001`; sandbox branch: `orbit/sandbox/orbit-a-s06-001`; pinned base: `af6c0d31fcf2e3232cb427c421850536139e3b3a`.
- Deepnote run `cc7686cc-a9cf-4bae-8b90-76dc36826b46` performed a valid token-backed `PUT /contents` (HTTP 200) to the task's only allowed report path. New report blob: `39e2ad46c72899ffcf47c283b5323ff8fc4456bd`; commit/head: `60d02d29220d4f85a007f9677f1d26e4c31a8e0a`.
- Independent readback matched the updated content. Compare base-to-head: ahead=2, behind=0; exactly one changed path (the approved report file, added; 51 additions).
- Deepnote run `7d0c8261-5edb-4cdf-a578-01ecc4edf72a` passed 11/11 deterministic checks. Seven pinned source fixture hashes matched. Raw CSV recomputation: 10 total items, 8 not Done / 35 hours, 4 Open / 19 hours; high-priority Open NS-101 (5h), NS-104 (8h), NS-105 (4h); acceptance 3 Passed, 1 Blocked, 1 Not Run, 1 Failed. The report covers the five required headings, dependency chains, AT-03 evidence conflict, AT-06 failure and rejection of the instruction embedded in untrusted issue content.
- Manifest update run `be30e5c8-d408-451c-9743-12afe3a2b1ff` committed as `7850e9f6efadd2aaa4236c4a612980e8b8d46a53`; blob `541106e544f80ed2fcd2b1d8ecbe63006acb6464`. Repository validator: valid, 30 tasks, Stage A=30, Stage B=0, zero errors.
- S06 validation subchecks: contract=pass, environment=pass, grader=pass; family review=accepted. Task status remains `ready_for_validation` and task execution remains `not_run` / `model_runs_allowed=false`.
- The panel-level S07/S09 gate still blocks promotion of any Stage A task to `validated`. No model inference, model-generated trajectory, capability score or training occurred.
- Detailed records: `experiments/ORBIT-S06-LIVE-SMOKE-001/` and `experiments/ORBIT-S06-ADJUDICATION-001/`.


## 31. S07 checkpoint rehydration and S09 forecast harness hardening

- Active branch: `orbit/plugin-benchmark-fixture`. This work stayed in `Kshitijpalsinghtomar/dhi`; no merge and no changes to other research repositories.
- Implemented normalized branch snapshots with fail-closed pagination and record validation.
- S07-001 and S07-002 now pin repository, commit, and blob SHA; `checkpoint_rehydrated` requires a successful linked fetch and independently checked blob/content hashes before the first write.
- S09-001 forecast metadata is exercised end-to-end through the scripted runner and grader; harness gap `plugin_prediction_trace_adapter` is removed. Model forecast accuracy remains untested.
- Full DHI benchmark/environment suite status: **not_confirmed** (not available from current block snapshot); compileall is not confirmed.
- Verification record: `DHI_v1/experiments/ORBIT-S07-S09-HARNESS-HARDENING-001/verification-report.json`; experiment README: `DHI_v1/experiments/ORBIT-S07-S09-HARNESS-HARDENING-001/README.md`.
- Stage A remains 30 `ready_for_validation` tasks, Stage B sealed, all `model_runs_allowed=false`. No model execution or training occurred.
- Deepnote notebook: `3639f9a98ce5435fa4cd0168eaaca3a1`; verification block: `2ed9a06177484889836fb66f5df188bb`.


## 32. S05-001 exact GitHub file-blob grader binding — 12 November 2026

- The S05-001 reference fixture is pinned to `Kshitijpalsinghtomar/dhi` at commit `af6c0d31fcf2e3232cb427c421850536139e3b3a`; the file blob is `fe9f3fec31796694ec44711dfaf8a2dc1acbfe2d` and the CSV contains 10 data rows plus one header.
- Regression work first reproduced two false accepts: a different tool could return the claimed SHA, and altered CSV content could carry a spoofed provider SHA. The tests were made structurally valid by mutating both action-start and action-executed events.
- Code commit `b0c43535d7ee52abc18c2dcae3b20d68efb7f2fa` makes `file_blob_match` require a pinned lowercase Git blob SHA-1 and exact `expected_tool_id`; it independently recomputes the Git blob SHA-1 from returned content before checking CSV row count.
- Manifest commit `630b238d98b6b6ddc93b95b5f3706ddeff52613d` adds `mcp__GitHub__fetch_file` to S05-001 and S08-001, refreshes both family/task fingerprints and the trace-grader SHA-256. S08-001 remains `grader_check=not_run` until its own test evidence exists.
- Deepnote run `6ad055f4-9e6d-4ec0-9c9c-35f412653d5b`: S05-001 tests **8/8 passed**; manifest validator `valid=true` for 30 tasks with zero errors; benchmark/environment `compileall` exit code 0.
- S05-001 now records `grader_check=pass`, but remains `ready_for_validation` and `review_status=not_reviewed`. Execution is still `not_run`; `model_runs_allowed=false`. Deterministic grader verification is not a model trajectory, family review or task admission.
- No model inference, training, live TinyFish request, paid provider action, merge or change to `main` occurred.


## 33. S05-002 TinyFish two-page batch fetch grader — 12 November 2026

- S05-002 now has three deterministic conditions: one successful `mcp__TinyFish__fetch_content` invocation with the exact ordered two-URL Python downloads batch and all required boolean fields; successful raw-source evidence bound to the TinyFish tool for both official pages and the pinned historical release facts; and exactly one tool call with zero provider credits.
- The Python release values are pinned to the 2026-11-03 snapshot only: Python 3.15.2 listed as latest stable and Python 3.16 as a planned pre-release for 2027-10-06. These are fixture facts, not current-version claims.
- `tool_trace_arguments` now supports opt-in `require_success` and `exact_list_fields`. `external_snapshot_match` / `source_fact` now support opt-in exact tool binding and successful-response requirements. Existing conditions remain backward-compatible when these optional controls are absent.
- S05-002 grader version is 1.1.0. Independent review remains required: the reviewer must confirm the two separate page results and the release interpretation because the connector response is not a fully pinned typed result schema.
- Task test file: `DHI_v1/benchmark/tests/test_study0_tinyfish_task_graders.py`. Focused Deepnote run `afb668ad-5192-4dde-ade4-a273b7a87cc7`: **8/8 passed**. Shared regression run `375bcd7a-9887-4111-bca2-8d1bbe47d7b0`: **48/48 passed**, covering the shared trace grader, S05-001 and S05-002 tests.
- Exact manifest was reloaded from GitHub commit `a3939a4583a33ee2446151f735cb78b62b068179`, blob `e513532f814c63a379ed8001ac523876571c334d`. Deepnote run `a48565c7-87bb-42d5-a219-6582cc0c261f` confirms manifest `valid=true`, 30 tasks, zero errors; benchmark/environment `compileall` exit code 0.
- S05-002 records `grader_check=pass`, but remains `ready_for_validation` and `review_status=not_reviewed`. Its execution remains `not_run`; `model_runs_allowed=false`. The panel still has 10/30 deterministic grader checks passed and 20 `not_run`; only S06-001 has an accepted family review.
- No live TinyFish request, provider-credit spend, model inference, training, merge or change to default `main` occurred.

**Next exact work:** S05-003 must test the GitHub `update_file` call itself: current blob SHA precondition, exact full replacement content, explicit `orbit/plugin-benchmark-fixture` branch, successful readback, and exactly one modified target path. S05-004 remains a later contract gap: its current `tool_trace_arguments` condition does not match the supported verifier shape, and its snapshot condition lacks source/tool binding.


## 34. S05-003 linked GitHub update transaction grader — 12 November 2026

- Added deterministic condition `github_update_file_transaction` and upgraded S05-003 grader to version 1.1.0.
- The verifier requires exactly this ordered tool sequence: `fetch_file → update_file → fetch_file → compare_commits`. It binds all four actions to the exact repository, path and benchmark branch.
- The first fetch must return the pinned seed blob and its returned content must independently hash to that Git blob SHA. The update must reuse that exact SHA, supply the complete replacement content and a non-empty commit message, and return the expected new blob plus a valid commit SHA.
- The post-update fetch must return the exact updated blob and exact content; the compare call must compare the seed commit to the commit returned by `update_file` and report exactly one modified path with the pinned change counts.
- Regression file: `DHI_v1/benchmark/tests/test_study0_github_update_task_graders.py`. Focused Deepnote run `b87b044c-5ea8-4727-9282-2ce2e50b961c`: **11/11 passed**, including rejection of forged pre-read SHA metadata with mismatched file body, wrong branch, stale SHA, create-file substitution, incomplete replacement, failed update, wrong/early readback, wrong compare head and extra diff paths.
- Full baseline regression run `a9c3a43c-f560-46f5-ac6f-cb0d44bc01ed`: **79/79 passed** before the final additional pre-read body-hash guard. After that guard, focused S05-003 tests passed 11/11; exact manifest validator run `6380935a-c19f-4709-8669-2d480129b605` returned `valid=true`, 30 tasks, zero errors; benchmark/environment `compileall` exit code 0.
- Trace-grader commit: `267f7d23b83c3a7db69e7e4d4d453a15f7a8acf1`; task-test commit: `58a7e32061092bd81326cce1856b1f01993c39cd`.
- Manifest commit: `269a22e5a85181ac4b69182f750625b13a5ec977`; blob: `e2a1951d1aca0786b7f6b2d87662c4099eda5b7d`; trace-grader SHA-256: `ef7bd85361f712598fe6d13580f0e0c533df690df01decb791c8f003623b2461`.
- S05-003 records `grader_check=pass`, but remains `ready_for_validation` and `review_status=not_reviewed`. Its execution remains `not_run`; `model_runs_allowed=false`. Study 0 now records 11/30 deterministic grader checks passed and 19 `not_run`; only S06-001 has accepted family review.
- No live `update_file` mutation, model inference, training, merge or default-`main` change occurred.

**Next exact work:** fix S05-004’s required-field/type verifier contract and bind the Go release snapshot to a successful TinyFish fetch from `https://go.dev/doc/devel/release`. Keep it offline and fixture-backed; no paid/live provider call.


## 35. S05-004 TinyFish required-field typing and Go source binding — 12 November 2026

- Added explicit `required_fields` and `field_types` handling to `tool_trace_arguments`. Supported JSON-like types are array, object, string, boolean, integer, number and null; booleans are checked strictly rather than accepted as integers. Existing S05-002 `require_success` / `exact_list_fields` behavior remains intact, and the legacy `page_metadata_type` shorthand remains backward-compatible.
- S05-004 now requires one successful `mcp__TinyFish__fetch_content` request to `https://go.dev/doc/devel/release` using markdown and all six fields: `urls`, `format`, `links`, `image_links`, `iframe_links`, `page_metadata`, with declared array/string/boolean types and exact URL-list matching.
- Its Go release snapshot condition is bound to that same successful tool and official URL. The pinned 2026-11-03 snapshot literally states **Go 1.27.3**, released **2026-10-19**; the condition uses the source’s exact release label rather than inferring that a no-space token is equivalent.
- Regression file: `DHI_v1/benchmark/tests/test_study0_tinyfish_required_fields_task_grader.py`. Final focused Deepnote run `f053191d-85db-48ec-8868-dffa35892cf3`: **11/11 passed**. It rejects missing fields, string-valued booleans, wrong URL shape, extra URLs, failed fetches, wrong tool/source and altered release/date evidence.
- Compatibility run `486b8ab3-088f-4d96-9d30-cb78eb3ee724` ran 72 tests: 71 passed; the sole positive-path mismatch was the expected token `go1.27.3` versus the snapshot’s exact `Go 1.27.3` wording. That condition was aligned to the snapshot, then the focused 11/11 suite passed. Direct manifest validator run `82fe7ca4-62a1-4af7-bbea-71355ecdb8ab`: `valid=true`, 30 tasks, zero errors; benchmark/environment `compileall` exit code 0.
- Trace-grader commit: `f84625099e015a07609555bb087fa4edd3b341d0`; test commit: `1a280d55aeac6bc373d22c296ee716905d2a02e4`.
- Manifest commit: `8e772e22e88d354b1023f1a73c02541ac16c4808`; blob: `c791090e0865297df9e2d99da1e6b7c5e387f36d`; trace-grader SHA-256: `04a2bd9bee463776e11a5a60fe50ebc10b2a5578fa88f44a19c50e413c66842c`.
- S05-004 records `grader_check=pass`, remains `ready_for_validation` / `not_reviewed`, and execution remains `not_run` with `model_runs_allowed=false`. Study 0 now has **12/30** deterministic grader checks passed and 18 `not_run`; only S06-001 has accepted family review.
- No live TinyFish call, provider-credit spend, model inference, training, merge or default-`main` change occurred.

**Next exact work:** S08-001 — exercise the pinned GitHub 404-recovery path with task-specific success and adversarial traces. Verify failed lookup handling, exact pre-read/reader binding, correct recovery ordering and the final successful file read without making real provider calls.


## 36. S08-001 linked GitHub 404 recovery grader — 12 November 2026

- Added deterministic condition `github_404_recovery` and upgraded S08-001 to grader version 1.1.0. It verifies exactly three ordered read actions: failed fetch of the registered bad path, GitHub directory inspection, and successful fetch of the recovered file.
- The initial failure must be HTTP 404 for the exact bad path at the pinned repository/ref. The canonical `plugin_trace.schema.json` represents this using `actual_tool_result.status_code=404` and a string `error`; the repository evidence record's `http_status=404` is normalized into that trace field. Do not put an object in `actual_tool_result.error`.
- The directory request must match the exact GitHub Contents API URL. Its actual response shape uses the raw JSON array in `result.content` plus `result.url` / `result.display_url`; the grader parses the listing and requires exactly one direct-child entry for `work_items.csv` with pinned SHA `fe9f3fec31796694ec44711dfaf8a2dc1acbfe2d`.
- The final `fetch_file` must use the exact repository/path/ref, return the same SHA as the directory entry, and return content whose independently recomputed Git blob SHA-1 matches the pinned digest. The existing `file_blob_match` condition also pins the exact successful reader and arguments.
- Regression file: `DHI_v1/benchmark/tests/test_study0_github_404_recovery_task_grader.py`. Final schema-corrected focused run `e4e8e116-8e45-4f19-96bc-3b02737abce1`: **12/12 passed**. Tests cover wrong initial path/status, wrong directory, absent/wrong directory entries, ordering, failed final read, wrong final path, blind retry and spoofed blob/content.
- A broader 103-test integrated run `60c6ecc2-a1c1-4a88-a7d6-26ed2b2476dc` hit the configured 300-second subprocess timeout; it is not counted as a pass. The run's direct manifest validator and `compileall` both passed. After the schema correction, direct manifest validation run `d147615d-dc94-4b14-98b7-768a879a17b7` returned `valid=true`, 30 tasks, zero errors, and compileall exit code 0.
- Exact committed manifest commit `153337511faa800f2af58d477cd96565431d1ede`, blob `296c1b24801167fce1bf491f4c63bba38d7957aa`; reloaded exact blob validation run `9ca039ce-6bba-4dbd-af33-4003e3634aa9` again returned `valid=true`, 30 tasks, zero errors; compileall exit code 0.
- Trace-grader commit: `9b2e8faf5f573ec11ef2d852fefe41c319fba03f`; S08 test commit: `e9b5287a9dd20e204113132a9f1efdd8f87f389d`; manifest trace-grader SHA-256: `e22dbb8f7ceca33bfc43108f70c40cc60096097f6ccc2ea103a48a0bc209a635`.
- S08-001 records `grader_check=pass`, but remains `ready_for_validation` and `review_status=not_reviewed`. Execution remains `not_run`; `model_runs_allowed=false`. Study 0 now has **13/30** deterministic grader checks passed and 17 `not_run`; only S06-001 has accepted family review.
- No GitHub repository write, live TinyFish call, provider-credit spend, model inference, training, merge or default-`main` change occurred. Only read-only GitHub fixture/source inspection was used.

**Next exact task from the manifest:** `ORBIT-A-S02-001` — verify the pinned Node.js official release-state snapshot. Review its dated source fixture and current external-snapshot grader, then add targeted tests only for demonstrable grader gaps. Keep it offline and fixture-backed.


## 37. S02-001 Node.js release snapshot grader — 12 November 2026

- Added task-specific regression file `DHI_v1/benchmark/tests/test_study0_nodejs_release_task_grader.py`; commit `28d145773668e7f4ffb8a8a699976ddb91174c19`.
- The initial RED suite reproduced six false accepts: release facts accepted from Search instead of Fetch; failed Fetch accepted despite partial content; missing v27 Alpha row; missing one LTS row; missing page-updated date; and missing production guidance. Wrong source URL was already rejected.
- S02-001 now pins a successful `mcp__TinyFish__fetch_content` observation from `https://nodejs.org/en/about/previous-releases`, and checks all four dated rows (v27 Alpha; v26/v24/v22 LTS), page metadata date `2026-10-29`, and production guidance `Active LTS or Maintenance LTS`. Grader version is 1.1.0.
- The historical observation date remains `2026-11-03`; this is a reproducible snapshot, not a current Node.js release assertion.
- Combined Deepnote run `edd2ef89-14af-4d07-ae9d-fbd142d5f6f2`: **27/27 passed** across S02-001 (8 tests), existing S05-002 tests and S05-004 tests. Direct manifest validator: `valid=true`, 30 tasks, zero errors; benchmark/environment `compileall` exit code 0.
- Exact manifest commit `21b332eece4648bb2889232672f882fcca210b5f`, blob `1fb2ca721e926117f40071fce3f3cbffe52ca5a2`. Exact committed-blob verification run `e4ac486d-414c-4a04-b35e-ec08432e045c`: validator `valid=true`, 30 tasks, zero errors; compileall exit code 0.
- S02-001 now records `grader_check=pass`, but remains `ready_for_validation` / `not_reviewed`; execution remains `not_run` and `model_runs_allowed=false`. Study 0 is **14/30** deterministic grader checks passed, 16 `not_run`; only S06-001 has accepted family review.
- The 103-test integrated regression attempt timed out at its 300-second subprocess limit and is not counted as a pass. The focused 27-test run above is the verified regression result for this unit.
- No live TinyFish call, provider-credit spend, model inference, training, merge or default-`main` change occurred.

**Next exact task:** `ORBIT-A-S07-001` — persistent GitHub checkpoint resume. Continue from [`NEXT_AGENT_HANDOFF.md`](NEXT_AGENT_HANDOFF.md); inspect the existing one-report sandbox branch without mutating it and first close the identified source-read/report/grader coverage gaps.


## 38. S07-001 persistent checkpoint-resume grader — 12 November 2026

- Trace-grader commit: bd4ba024c15f15c43ce86af84e8b9d019fa2dc93; SHA-256 0f51adb48f19aa54f6e93cc21ef38391841ff695c82b08e27e2bc5d095f416f9.
- Task-specific tests: DHI_v1/benchmark/tests/test_study0_checkpoint_resume_integrity.py; test commit a52ab526dfdcbc1bdf6fb708795dd8643830f084.
- Manifest commit: 87a9afcf28a5c796ed39015efe703f5ce3fd97ba; blob a1e198b0f48311a98333a4e53d6e8d38f07ab3dc. S07-001 uses grader version 2.0.0 and one task-specific checkpoint_resume_integrity postcondition.
- Deepnote run f578ade9-6369-4ace-b34b-01279c000714: 53/53 passed (21 S07-specific tests + 32 shared trace-grader tests). Exact committed-manifest run c34a6a9a-8161-41d9-a654-73483f437724: validator valid=true, 30 tasks, Stage A=30, Stage B=0, zero errors; benchmark/environment compileall exit code 0; exact plugin_trace SHA-256 matched the manifest.
- The verifier binds the checkpoint read to the exact registered fetch tool and pinned blob; requires all seven source reads to be unique, successful, content-hash verified and started after resume/before the first write; requires the single report create/readback/artifact chain; and requires an independently observed compare from the checkpoint commit to the report commit with exactly one added report path and one commit. Report-content checks cover required headings, metrics, high-priority items, dependency edges, acceptance statuses and known limitations; false all-passed claims are rejected.
- The exact existing report on orbit/plugin-resume-sandbox remains read-only: commit d3f7ca37a8623ef6e5f5b3ed4e60f88a2a8efb1c, blob 2136bef44ceffd4704a6e164e4f53be2af2019c1. Compare from checkpoint 04d0e12f48067b3b3a3de3ffe10944b7ef594984 shows ahead 1, behind 0, exactly one added file (50 additions, zero deletions). The report omits NS-106 → NS-105 and is intentionally rejected by the report-content predicate. Do not recreate or rewrite it.
- Seven pinned source blobs were fetched and content-hash verified at fixture ref af6c0d31fcf2e3232cb427c421850536139e3b3a. Other report values: 10 work items, 2 Done, 8 not Done/35 hours, 4 Open/19 hours; acceptance 3 Passed, 1 Blocked, 1 Not Run, 1 Failed.
- S07-001 remains ready_for_validation, grader_check=pass, review_status=not_reviewed; execution is not_run, model_runs_allowed=false. This is verifier-test evidence, not a model trajectory or accepted family review. No model inference, training, provider spend, sandbox write, merge, or main change occurred.

Next exact work: ORBIT-A-S09-001 — inspect the exact task contract and grader for pre-action write-effect prediction, add task-specific RED tests for prediction timing and compare/readback linkage, then implement only proven gaps. Use a fresh disposable branch from the pinned fixture base; do not reuse the S07 sandbox branch.
