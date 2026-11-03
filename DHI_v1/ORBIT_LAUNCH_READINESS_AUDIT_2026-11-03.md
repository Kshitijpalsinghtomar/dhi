# ORBIT Launch-Readiness Audit — 2026-11-03

**Decision:** NOT READY FOR MODEL TRAINING OR RELEASE  
**Authority:** This audit is subordinate to `DHI_v1/WORKSPACE.md`. It records an independent cross-check of repository state, Deepnote verifier contents, benchmark status, provider integration, inference access and data lineage.  
**Code branch at audit start:** `orbit/plugin-benchmark-fixture`  
**Code commit audited:** `5b144c531e8a548787918f0fcdf9e681f05d96e8`  
**Base:** `main` at `60bf0783a5ddac7a6727747fcad0dc3be0615ecc`  
**Branch relation at audit start:** 258 commits ahead, 0 behind; PR #1 open and draft.

## Executive decision

ORBIT has a substantial deterministic execution/evaluation harness, a constrained TinyFish integration, and a documented research protocol. It does **not** yet have demonstrated learned agent capability, an approved base-model winner, valid model-generated tool trajectories, DHI-v1 trained weights, or a release artifact.

The next milestone is a reproducible **base-model inference and benchmark pilot**, not another provider adapter and not an SFT launch.

## Independently reconciled evidence

| Area | Adjudication | Evidence boundary |
|---|---|---|
| Repository | Correct active branch found; 258 ahead / 0 behind main | Git metadata and compare endpoint |
| Deterministic harness | Historical combined regression: 136 passed at `421955d`; earlier 142 passed at `cba8421` | Neither is a fresh full regression of the TinyFish adapter commit |
| TinyFish provider | Credential presence, MCP initialize/tools/list, and bounded read-only Search/Fetch smoke recorded as successful | Provider smoke only; no model inference or training |
| TinyFish DHI adapter | 16 direct assertions and 6 in-memory source compilations passed | Scripted model; HTTP mocked; not pytest or full regression |
| Latest adapter full-suite gate | OPEN at audit start | No combined pytest/compileall run on adapter commit |
| Benchmark | 30 Stage A tasks authored across 10 strata | 30/120 Stage A; 0/120 Stage B; tasks ready for validation, not validated |
| Coverage | S07 and S09 partial | Cross-session model-run recovery and model-originated prediction/effect evidence incomplete |
| Model inference | NONE | No candidate model call or model-generated trajectory |
| Candidate access | Qwen3.6-35B-A3B and GPT-OSS-20B catalogued via OpenRouter | Last account audit: $0 credits; no inference call |
| Training data | NOT READY | Invent/task-spec and collaboration datasets quarantined; 10K augmented dataset has unresolved evaluation-lineage mismatch |
| Training | NOT AUTHORIZED / NOT RUN | No approved dataset, no selected base model, no cost approval |
| Model checkpoint | NONE for DHI-v1 | No trained weights or reproducible release artifact |

## Exact-head verification preparation

The existing Deepnote project is `DHI ORBIT exact-head verifier` (project `6415944e-8d6c-432c-a7cf-3bbaa997799c`; notebook `3639f9a98ce5435fa4cd0168eaaca3a1`). The TinyFish API key is held in the attached `TINYFISH` environment integration; no key value is read into this audit.

Before the next full test, the following source files were compared against GitHub branch `orbit/plugin-benchmark-fixture` and found byte-for-byte identical: agent runner, DHI environment, fixture manager, their relevant tests, TinyFish adapter and tests, benchmark trace/grader code and tests, trace schema, manifest schema, and manifest validator. The 4,704-line task manifest matched across all 19 250-line windows (final window 204 lines), ignoring only the trailing newline convention returned by the Deepnote file reader.

The notebook's original saved regression block is preserved. The next verification uses a new selected cell and must not execute that saved block or the temporary provider-probe cells.

## Material discrepancies corrected in this audit

1. `PLUGIN-GATEWAY-001/README.md` opens with an old “blocked before implementation” status. Later dated evidence and the live workspace record the successful TinyFish credential, MCP inventory and bounded read-only provider smoke. Treat the opening status as the original feasibility checkpoint, not the current provider status.
2. The TinyFish adapter's 16 direct assertions are not a pytest run. They use a scripted model and mocked HTTP. Do not report them as model inference or a real provider execution through the DHI model runner.
3. The successful ORBIT-VERIFY-003 run (136 tests) is pinned to `421955d`, before the TinyFish adapter changes. It does not validate the adapter commit.
4. The historical 142-test pass at `cba8421` likewise predates the TinyFish adapter. Neither historical result closes the latest exact-head gate.

## Missing gates before the first trained ORBIT checkpoint

### Gate 1 — exact-head engineering verification
- Run the full benchmark and environment pytest suites against the exact adapter code commit.
- Run manifest validation, compileall and import smoke in the same recorded verification.
- Preserve logs, exit codes, commit SHA and interpreter/environment metadata.
- Fix only demonstrated failures. Do not add features during this gate.

### Gate 2 — finish and freeze the benchmark
- Independently validate the existing 30 Stage A tasks first.
- Close S07 checkpoint/resume and S09 prediction/effect observability with executable, model-facing traces.
- Author and independently review the remaining 90 Stage A tasks.
- Freeze task bodies, grader versions, fixtures, schemas, seeds, budgets and split hashes before confirmatory evaluation.
- Materialize Stage B separately and keep its contents sealed.
- Never mark a task validated merely because a scripted reference workflow succeeds.

### Gate 3 — matched base-model inference
- Resolve an approved, funded route for both Qwen3.6-35B-A3B and GPT-OSS-20B; the last OpenRouter balance audit showed $0.
- Freeze matched prompts, model revisions, tool schemas, reasoning settings, decoding, token/action budgets and environment.
- Run a small smoke on both candidates, then the same Stage A panel.
- Preserve model-generated traces, raw tool responses, pre-action forecasts, state deltas, verifier outputs and costs.
- Select a base model only from preregistered comparative evidence.

### Gate 4 — valid training trajectories and data
- Generate trajectories by actual model execution in the deterministic environment and authorized tools.
- Capture prediction-before-action, actual observations, state changes, replanning, safety decisions and independently verified postconditions.
- Independently adjudicate and deduplicate trajectories; split by task family, tool schema and environment to prevent leakage.
- Reconcile the 10K dataset's source/evaluation lineage or exclude it. Its inherited Grade A score is not a training-readiness certificate.
- Obtain a real compute/cost estimate before any chargeable training job.

### Gate 5 — train and evaluate the first checkpoint
- Run one controlled SFT baseline on the selected base model.
- Do not introduce DPO, RL and custom latent architecture in the same first training run.
- Add predictive/closure supervision only as a separately controlled ablation after the ordinary SFT baseline is reproducible.
- Require held-out improvement, no safety hard-gate failures, no false-closure regression and independent reproduction.

### Gate 6 — package a launchable model
- Save model/tokenizer revisions, adapter and merged weights, inference configuration, tool protocol, environment requirements and license/usage notices.
- Provide reproducible loading/inference code and a small demo/evaluation card.
- Publish benchmark scope, uncertainty, limitations, costs and known failure modes.
- Keep product/runtime claims separate from learned model-capability claims.

## Recommended sequence — no side quests

1. Exact-head full regression.
2. Validate the existing 30 tasks; close S07/S09; finish Stage A.
3. Resolve inference funding and run matched Qwen/GPT-OSS base-model smoke tests.
4. Run the frozen base-model diagnostic and choose a winner.
5. Produce and adjudicate actual model-execution trajectories.
6. Run one controlled SFT experiment, evaluate it, and package the first checkpoint.

## Timeline estimate

These are planning estimates, not guarantees:

- **First matched base-model smoke:** 1–3 working days after inference funding/access is available and the exact-head gate passes.
- **Initial comparative Stage A screen:** approximately 3–7 working days after the panel is frozen and inference access is funded.
- **First SFT checkpoint:** approximately 1–3 additional weeks after a model is selected, valid trajectories are available, and a training route/cost is approved.
- **Responsible first checkpoint target:** roughly 3–6 weeks from removal of the current hard blockers. Public launch-quality packaging and independent validation can add another 1–2 weeks.

The largest uncertainty is not code-writing time. It is access to inference/compute, finishing a defensible benchmark, and collecting real verified trajectories. A checkpoint can be produced sooner by weakening those gates, but it would not meet the stated ORBIT objective.

## Explicit non-goals for the next work unit

No new provider integration, adapter expansion, dataset augmentation, model architecture experiment, Stage B exposure, paid action, model training, merge or deployment. The only immediate work is exact-head verification and then closing the benchmark/inference blockers.


## Critical execution-path audit — 2026-11-03

A second independent code trace found that the 30-task plugin-native manifest is **not wired to the current model-facing pilot runner**:

- `run_model_pilot.py` invokes `run_pilot_benchmark` over `benchmark/pilot_cases.json`; it does not load `benchmark/task_manifest.json`.
- `benchmark/runner.py` currently selects only `file_workspace` and optional `adaption_catalogue` pilot cases.
- `DHIEnvironment.DEFAULT_TOOL_CATALOGUE` exposes local catalogue/filesystem IDs, Adaption catalogue discovery and the TinyFish internal catalogue IDs.
- `agent_runner.tool_handlers_from_client` adds only Adaption catalogue discovery and TinyFish Search/Fetch. It has no GitHub or Firecrawl handler.
- The plugin-native manifest instead requires `mcp__TinyFish__search`, `mcp__TinyFish__fetch_content`, `mcp__GitHub__*` and `mcp__Firecrawl__firecrawl_find_tools` IDs. The TinyFish internal IDs are not identical to the manifest IDs; there is no canonical mapping in the runner.

The 30 task records require these external tool IDs (counts are task references, not unique tasks): TinyFish Search 5, TinyFish Fetch 7, Firecrawl discovery 5, GitHub fetch_file 14, GitHub create_file 7, GitHub compare_commits 9, GitHub fetch 2, GitHub create_branch 1 and GitHub update_file 2. Many tasks have multiple required tools.

**Correction to status wording:** 30 Stage A task records are authored and contract-checked, but they are not all end-to-end executable through the current ORBIT runner. Their status is *authored / ready for execution-path integration and validation*, not benchmark-validated. Do not expand Stage A to 120 or claim task validation until the manifest-to-runner bridge and the missing provider handlers are implemented and tested.

### Required implementation boundary

1. Canonicalize tool IDs against `plugin_tool_registry.json`; the manifest, tool schema, allowlist, runner handler map and trace must use the same stable ID.
2. Add a plugin-native execution profile that loads a manifest task, constructs only its visible tool schemas, enforces its per-task allowlist, and dispatches to provider handlers.
3. Keep TinyFish Search/Fetch under the canonical registry identity while preserving their fixed endpoints, secret redaction and read-only policy.
4. Implement GitHub read operations first; allow sandbox branch/file writes only after a separate disposable-repository/branch and token-permission contract is tested. Deletes and merges stay excluded.
5. Resolve Firecrawl Alexandria discovery against its exact registered contract; do not substitute generic Firecrawl search/scrape tools.
6. Run scripted contract tests and then model-generated traces. Scripted reference executions are not ORBIT capability evidence.

This gap is more fundamental than writing the remaining 90 task records. The next engineering priority after ORBIT-VERIFY-004 is the canonical plugin execution path, not further task authoring.


## Connector availability clarification — 2026-11-03

The connected assistant session has GitHub MCP actions and Firecrawl Alexandria's `firecrawl_find_tools` action. Their exact contracts are available to this assistant; the prior statement that Firecrawl discovery was “unresolved” referred to the DHI runtime bridge and should not be read as absence of the connected tool.

A live Deepnote integration search for `FIRECRAWL` and `GITHUB` returned no attached project integrations. The verifier has `TINYFISH` attached only. Therefore, assistant-session connector access does not establish that the ORBIT model runner can invoke those actions. The plugin-native runtime still needs a tested MCP/REST transport, project-scoped credentials, canonical ID/schema parity and permission guards. In particular, do not assume a generic Firecrawl REST API key is equivalent to the Alexandria `firecrawl_find_tools` operation without validating its supported transport.
