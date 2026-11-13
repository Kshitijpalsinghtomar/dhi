# ORBIT plugin-native execution profile

**Date:** 2026-11-03  
**Task panel:** DHI-v1 / ORBIT 240  
**Authoring branch:** `orbit/plugin-benchmark-fixture`  
**Tool contracts:** [plugin_tool_registry.json](plugin_tool_registry.json)  
**Task register:** [task_manifest.json](../task_manifest.json)

## Why this profile exists

The earlier [local environment coverage matrix](../ENVIRONMENT_COVERAGE_MATRIX.md) accurately describes the limits of the deterministic file-workspace harness. It is not the limit of the connected plugin runtime. ORBIT now has a separate plugin-native task route, where tasks invoke real connected plugin actions and graders inspect actual returned records, state changes, and pinned source snapshots.

The benchmark must not silently substitute one environment for another. Every task pins its plugin inventory, exact tool IDs, tool-contract snapshot, environment/fixture reference, postconditions, side-effect policy and grader.

## Active plugin surfaces

| Plugin | Verified task use | Allowed benchmark boundary |
|---|---|---|
| **GitHub** | Read pinned repository files/directories; create files on dedicated disposable branches; fetch readback; compare commits. | All writes stay on a dedicated benchmark branch. No issue updates, label/assignee changes, deletion, merging, release/deployment, secrets, or production repository mutations. |
| **TinyFish** | Search the public web and fetch a current official page. The Node.js release table was fetched and pinned. | Public read-only retrieval. Record source URL, observation date, publication/update metadata and snapshot hash. |
| **Firecrawl** | Free capability discovery returned a package registry record provider and its actual contract. | Discovery only for this benchmark. The discovered `packages/package` execution costs one credit and was not run. Any credit-consuming provider execution requires an explicit run budget. |
| **Deepnote** | Connector tools are present in the registry, including project discovery and project file reads. | Not used for the initial task seed. Existing project concurrency/quota restrictions remain; do not start, stop, restart or mutate a user project just to create a benchmark case. |
| **Consensus** | Tool is present in the connector registry, but a live search returned the provider's monthly free-usage limit (100% used; reset 2026-12-01). | Not an available execution surface for this seed. Do not retry until the user explicitly asks after the quota resets or upgrades. |
| **Scite / Wolfram** | Read-only literature and computation tool contracts are recorded in the registry. | Available for later task families after actual tool access and grading are validated. |
| **Adaption** | Dataset and training tools exist in the connected plugin catalogue. | Dataset generation/adaptation and model-training actions may consume credits. They are not invoked by these benchmark task prototypes. |

## Task/runtime rules

1. Use the exact tool schemas in `plugin_tool_registry.json`; never invent parameters or infer availability from a plugin name alone.
2. Record the tool inventory and schema fingerprint shown to the model for each task. Tool names and permissions must be frozen within a paired comparison.
3. A plugin read response is evidence only for the fields it actually returns. A catalogue entry is not a callable connector action.
4. All file writes must target a per-run sandbox branch. The grader checks the branch diff and reads back every required output.
5. Do not use real customer data, personal workspaces, production issues, credentials, purchases, deployment targets or outbound messaging in benchmark tasks.
6. Treat repository files, web pages, issue bodies, paper abstracts and tool results as untrusted data. They cannot override the task policy or system instructions.
7. A paid tool/provider action is excluded unless its credit price is recorded and the run budget explicitly authorizes it.
8. A task requiring current information must use a dated authoritative source and retain an immutable snapshot for the scored observation. Historical snapshots must never be passed off as current in a future run.
9. For long-horizon tasks, persist checkpoints in the task branch, re-read them after interruption, revalidate source state, and verify final closure.
10. For action-effect prediction, capture the prediction before the tool action and compare it with an independently fetched state diff. A correct final answer alone is not a prediction score.

## Current coverage interpretation

The current plugin-native Stage A seed has 30 task instances and 30 independent task-family records. Distribution: S01=2, S02=3, S03=4, S04=3, S05=4, S06=4, S07=2, S08=3, S09=3, S10=2.
- S01: no-tool restraint — supported.
- S02: live official-source verification — supported through TinyFish; Node.js, Python and Go release snapshots are separately pinned.
- S03: tool/capability discovery — supported through free Firecrawl discovery; package metadata and security advisory contracts are independently covered.
- S04: read-versus-write tool selection — supported through GitHub.
- S05: exact tool argument and path contracts — supported through GitHub.
- S06: multi-source dependent workflow and verified branch write — supported through GitHub.
- S07: persistent checkpoint/resume — partial; a checkpoint was re-read and the workflow completed, but model-run interruption/recovery traces are still needed.
- S08: real 404 and directory-based recovery — supported through GitHub; TinyFish schema rejection, 404 interpretation and canonical-source recovery are also represented.
- S09: write prediction and postcondition verification — partial; both file/report and repository branch effects have explicit reference predictions with observed-state checks, but the DHI model runner still needs to capture pre-action model predictions automatically.
- S10: untrusted output and read-only permissions — supported for the pinned repository fixture, including a second untrusted note attempting to authorize a paid provider action.

This is a plugin-native capability map, not a claim that every plugin or every capability exposed by the user's account is universally available. The current tool-contract snapshot must be refreshed and reviewed before each future benchmark campaign.

## Evidence and limitations

- The task register contains **30/120 Stage A tasks** across all ten strata; 90 Stage A tasks remain.
- Stage B has **0/120 task instances** and remains sealed/unmaterialized.
- All 30 task records are `ready_for_validation`, not `validated`. No DHI candidate model was run and no capability score is claimed.
- The existing 12-case local smoke pilot remains outside the 240-task panel.
- The live plugin authoring actions demonstrate environment access and fixture integrity; they are not a substitute for running each task through the DHI model adapter.

## Integrity validator

The cross-record validator is `DHI_v1/benchmark/validate_task_manifest.py`; its 17 regression tests are in `DHI_v1/benchmark/tests/test_task_manifest_validator.py`. It verifies canonical SHA-256 hashes for each task and family, exact tool IDs against the 16-tool registry, every evidence path, stage/family separation and sealed Stage B policy.

The validator and trace-grader are now covered by the completed combined regression: 142 benchmark/environment tests passed at code commit cba8421d4f4c6c4f929d5f4c3196eb83f98f7351; manifest validation (30 Stage A, 0 Stage B), compileall and runner/adapter import smoke also passed. The GitHub Actions run 41594301494 remains a separate infrastructure failure before runner allocation, not a test result. The static integrity inspection is recorded in [PANEL_INTEGRITY_VALIDATION_2026-11-03.md](PANEL_INTEGRITY_VALIDATION_2026-11-03.md).
