# ORBIT 240-task panel — environment coverage audit

**Audit date:** 2026-11-02  
**Audited revision:** `3640e4a86495299688b5e20e098097730743ab53` (`main`)  
**Scope authority:** [SCREEN_AND_DIAGNOSTIC_SCOPE.md](SCREEN_AND_DIAGNOSTIC_SCOPE.md)  
**Status:** first-pass source audit; coverage is bounded to the currently committed harness, not a claim that each stratum is ready for 24 task instances.

## Coverage decision

| Stratum | Current status | Evidence in the repository | What can be scored now | Required harness work / boundary |
|---|---|---|---|---|
| **S01 — No-tool-needed and direct answers** | **Supported** | `pilot_cases.json` has `policy-001-no-tool-needed`; its grader enforces zero tool calls, zero changed paths, and a whole-answer regex. `runner.py` evaluates these checks from the run result. | Stable, self-contained answers with deterministic exact-answer checks and no-tool restraint. | Keep this narrow. Current direct-answer examples do not establish current-fact verification or broad knowledge accuracy. |
| **S02 — Current/time-sensitive facts** | **Harness gap** | The registered tool catalogue has no web/current-source retrieval tool. The optional Adaption tool exposes connector metadata only. Existing `policy-009-current-fact-verification` is explicitly marked `not_executable_in_file_workspace`. | Nothing that should count as a scored current-source task. | Add a controlled web/source adapter, timestamped authoritative snapshots, source provenance, observation-time recording, and an independent currentness/citation grader. Until then, no S02 task IDs. |
| **S03 — Discovery of hidden capabilities** | **Partial** | `catalog.search` discovers hidden entries by lexical overlap in the small local catalogue; tests cover hidden `fs.search_text`. Optional `catalog.adaption_search` queries the live connector catalogue and records availability/auth/scope metadata. | Discovering a hidden local filesystem search tool; optionally identifying external connector candidates from a frozen/read-only catalogue snapshot. | Catalogue search is lexical and deterministic, not a broad semantic marketplace. Adaption results are discovery evidence only: they do not expose callable external tools. Split local discovery from external discovery in task tags and report them separately. |
| **S04 — Selection among relevant, irrelevant and decoy tools** | **Partial** | Tool schemas include descriptions, preconditions, side-effect class, permission scope, cost class and reversibility. Task allowlists reject disallowed tools. The seed `policy-011-deceptive-decoy-tool` is explicitly unsupported. | Basic choice among the registered file tools and correct restraint when a task allowlist blocks a tool. | No currently executable public/private decoy pair or realistic alternative auth scopes. Add task-local decoy catalogue fixtures, safe callable handlers, permission-distinct schemas, and graders that inspect the selected tool and attempted side effects. |
| **S05 — Schema/argument correctness and preconditions** | **Supported, bounded** | `_validate_arguments` enforces required keys, rejects extra keys when disallowed, and checks primitive argument types. Dispatch checks real path existence, directory/file type, UTF-8, parent existence, path boundaries and size limits. | Invalid/missing/extra arguments and filesystem precondition handling for the existing tool schemas. | This is not a general JSON Schema validator: enum/range/length/nested constraints are not enforced by the current runtime. Task contracts must stay within the implemented schema subset until validator coverage expands. |
| **S06 — Dependent multi-tool workflows and state changes** | **Supported, file-workspace only** | `TaskSpec`, the model runner, append-only JSONL events, SHA-256 snapshots/diffs, protected paths, and executable postconditions support sequential dependent workflows. Existing README-update cases are development-only evidence. | Multi-step read/search/write workflows where later actions depend on earlier observed file state. | The environment is not a terminal, browser, database, spreadsheet, or arbitrary application runtime. Do not generalize file-workspace results to other domains. |
| **S07 — 8–30 action workflows with checkpoints** | **Partial** | The runner defaults to 16 model turns and 48 tool calls; trace events record step IDs, subgoals and plan versions. The existing long-horizon resume seed is marked unsupported. | Same-session workflows of 8–30 tool actions can fit within current limits when each action is supported by the file environment. | There is no durable checkpoint object, interruption/resume API, cross-session task state, or checkpoint-level verifier. Add checkpoint persistence/replay and a resume test before claiming the full stratum. |
| **S08 — Tool failures, malformed responses, rate limits and replanning** | **Partial** | `fault_injections` deterministically fails a named tool on a selected attempt; the pilot has a transient search-failure case. Tool-argument parsing/schema errors are recorded as failed actions. | Replanning after a controlled tool failure or invalid tool arguments, with the error preserved in the trace. | Model-endpoint HTTP errors/timeouts stop the run as model/protocol errors; there is no deterministic 429/rate-limit/timeout injection with retry/backoff semantics. Add those controls before scoring provider outage recovery. |
| **S09 — Effect forecasts, side-effect prediction and closure** | **Partial** | The runner captures optional pre-action `changed_paths`/`unchanged_paths` forecasts, hashes file state before/after actions, calculates path-level precision/recall/F1, verifies postconditions, and checks protected-file hashes. | File-path mutation forecasts, exact file invariants and verified file-workspace goal closure. | This is not structured prediction of semantic state, permissions, external side effects, data dependencies, or uncertainty/calibration. Score only path-level claims until structured state predicates exist. |
| **S10 — Permissions, untrusted outputs, continuity and infeasible tasks** | **Partial** | Task tool allowlists, path traversal/symlink protections, protected-path hashing and permission metadata are implemented. The model-runner system instruction explicitly treats tool output as data rather than instructions. | File-workspace allowlist boundaries, protected-file preservation, and same-session handling of untrusted file content when a deterministic grader exists. | No cross-session continuity, irreversible external actions, role-based approval state machine, taint-labelled hostile-output corpus, or general infeasibility oracle. Add explicit adversarial fixtures and permission/consent graders before broader scoring. |

## Summary for task authoring

- **Supported within the current domain:** S01, S05 (only the registered schema subset), and S06 (file-workspace only).
- **Partial and requiring explicit scope limits:** S03, S04, S07, S08, S09, S10.
- **Blocked by a missing environment capability:** S02.

“Supported” does not mean a stratum's 12+12 tasks already exist. It means the current runner has a credible execution and grading path for a constrained slice of that stratum. The panel still needs distinct task families, fixtures, independent review, and tested graders.

## Authoring rules

1. Do not instantiate tasks for S02 until the current-source adapter and timestamped-source grader are implemented.
2. Do not label S03 external connector discovery as external tool execution.
3. Do not claim decoy selection (S04) from the current basic filesystem catalogue; add actual decoy tool fixtures and permission-distinct handlers first.
4. Use only implemented argument-schema constraints in S05; add validator tests before introducing richer schema keywords.
5. Keep S06 tasks within the pinned file-workspace environment and record every dependent state transition.
6. S07 can test same-session long chains as a partial probe, but the full checkpoint/resume claim stays blocked until persistent resume works.
7. S08 task faults must be declared and deterministic; provider/network recovery remains out of scope until explicit fault injection and retry semantics exist.
8. S09 predictions are file-path forecasts only. Do not score semantic action-effect prediction from path hashes.
9. S10 tasks must identify the precise boundary being tested; tool allowlisting is not equivalent to full external consent/approval reasoning.
10. Every task requires a non-vacuous postcondition and a grader with an evidence path independent of the model's final claim.

## What this audit does not establish

No Stage A or Stage B task instance has been authored, no model has been run, no benchmark result exists, and no task family has been certified independent. The 12-case development pilot remains excluded from the 240-task panel. This audit is a harness-readiness map, not a capability result.
