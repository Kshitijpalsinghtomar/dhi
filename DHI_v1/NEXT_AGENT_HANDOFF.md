# ORBIT Next-Agent Handoff

**Date:** 2026-11-12  
**Programme:** DHI-v1 / ORBIT only  
**Active implementation branch:** `orbit/plugin-benchmark-fixture`  
**Default branch:** `main` — do not change or merge it  
**Latest S07 manifest commit:** `87a9afcf28a5c796ed39015efe703f5ce3fd97ba`  
**Manifest blob:** `a1e198b0f48311a98333a4e53d6e8d38f07ab3dc`

> Read `DHI_v1/WORKSPACE.md` first. The GitHub manifest is authoritative for task state and hashes. This is a DHI/ORBIT handoff only. Do not mix in GBA/DPAK, Oriael, FDLT, TENS, or unrelated work.

## 1. Current verified programme state

Study 0 has 30 Stage A tasks and zero Stage B tasks.

- **15/30 deterministic grader checks pass; 15 remain `not_run`.**
- Accepted family review: **1/30** (S06-001 only). The other 29 remain `not_reviewed`.
- All 30 task executions remain `not_run`; every `model_runs_allowed` flag is false.
- No DHI model inference, model-generated execution trajectory, capability score, adjudicated training corpus, or training checkpoint exists.
- A deterministic grader-check pass means only that the verifier and its tests passed. It is not a model result, task admission, or independent family review.

Passed task IDs:
`ORBIT-A-S01-001`, `S01-002`, `S02-001`, `S03-001`, `S03-002`, `S03-003`, `S03-004`, `S04-001`, `S05-001`, `S05-002`, `S05-003`, `S05-004`, `S06-001`, `S08-001`, `S07-001`.

The 103-test integrated attempt `60c6ecc2-a1c1-4a88-a7d6-26ed2b2476dc` timed out at its configured 300-second limit; it is not a pass. Use focused, bounded groups.

## 2. Previous task evidence retained

### S02-001 — Node.js release snapshot

- Test commit: `28d145773668e7f4ffb8a8a699976ddb91174c19`.
- Focused combined run `edd2ef89-14af-4d07-ae9d-fbd142d5f6f2`: **27/27** passed across S02-001, S05-002 and S05-004.
- Exact manifest validation run `e4ac486d-414c-4a04-b35e-ec08432e045c`: valid, 30 tasks, zero errors; compileall passed.
- S02-001 binds release facts to a successful TinyFish Fetch from the official Node.js previous-releases page. The date 2026-11-03 is the benchmark observation date, not a current-version claim.

### S08-001 — GitHub 404 recovery

- Trace-grader commit: `9b2e8faf5f573ec11ef2d852fefe41c319fba03f`.
- Test commit: `e9b5287a9dd20e204113132a9f1efdd8f87f389d`.
- Focused run `e4e8e116-8e45-4f19-96bc-3b02737abce1`: **12/12** passed.
- Exact manifest validation run `9ca039ce-6bba-4dbd-af33-4003e3634aa9`: valid, 30 tasks, zero errors; compileall passed.
- Schema detail: `actual_tool_result.status_code` carries the integer HTTP status and `error` is string/null. The recovery grader parses the raw GitHub directory listing and binds the recovered path/blob to the final successful read.

## 3. S07-001 — persistent GitHub checkpoint-resume grader review completed

### Commits and verification

- Trace-grader commit: `bd4ba024c15f15c43ce86af84e8b9d019fa2dc93`.
- Task-specific test commit: `a52ab526dfdcbc1bdf6fb708795dd8643830f084`.
- Manifest commit: `87a9afcf28a5c796ed39015efe703f5ce3fd97ba`.
- Manifest blob: `a1e198b0f48311a98333a4e53d6e8d38f07ab3dc`.
- Trace-grader SHA-256: `0f51adb48f19aa54f6e93cc21ef38391841ff695c82b08e27e2bc5d095f416f9`.
- Deepnote run `f578ade9-6369-4ace-b34b-01279c000714`: **53/53** passed (21 S07-specific tests + 32 shared plugin-trace grader tests).
- Exact committed-manifest reload run `c34a6a9a-8161-41d9-a654-73483f437724`: validator `valid=true`, 30 tasks, Stage A=30, Stage B=0, zero errors; benchmark/environment compileall exit code 0. The exact checked-out grader SHA matched the manifest digest.

### New deterministic verifier

S07-001 now uses `checkpoint_resume_integrity` as its single task-specific postcondition. It requires:

1. Exact successful registered `mcp__GitHub__fetch_file` checkpoint read at the pinned checkpoint commit/blob, linked to the unique `checkpoint_resumed` event.
2. Exactly seven unique successful source reads, each from the pinned fixture commit and exact expected Git blob/content. Both invocation start and completion must occur after checkpoint resumption and before the first write.
3. Exactly one permitted `create_file` action for the report path on `orbit/plugin-resume-sandbox`.
4. Exactly one successful report `fetch_file` readback after the write completes. The readback content, Git blob, final artifact, and artifact-readback evidence must agree.
5. Exactly one registered `compare_commits` observation after readback, comparing checkpoint commit `04d0e12f48067b3b3a3de3ffe10944b7ef594984` to report commit `d3f7ca37a8623ef6e5f5b3ed4e60f88a2a8efb1c`.
6. Exactly one changed path: the report, added in one commit, 50 additions and zero deletions. The observed action count must match the trace and stay within the task's 9–24 action budget.
7. Required source-derived report content, including all dependency edges and acceptance-state facts; forbidden false claims are rejected.

The S07 test file is separate from the shared grader tests:
`DHI_v1/benchmark/tests/test_study0_checkpoint_resume_integrity.py`.

Coverage includes exact tool identity; pinned checkpoint and source hashes; missing, failed, duplicate, wrong-ref and unregistered source reads; reads started before resume or after the write; forged artifacts; failed/stale report readback; compare omission, wrong head and extra diff paths; report content/contradictions; exact seeded-report hash; Unicode dependency arrows; and action-budget enforcement. Test-first development exposed the two invocation-start ordering false accepts; the added checks close them.

### Existing sandbox: read-only and intentionally not corrected

- Branch: `orbit/plugin-resume-sandbox`.
- Existing report path: `DHI_v1/benchmark/fixtures/plugin_ecology/reports/resume-release-review.md`.
- Report commit: `d3f7ca37a8623ef6e5f5b3ed4e60f88a2a8efb1c`.
- Report blob: `2136bef44ceffd4704a6e164e4f53be2af2019c1`.
- Read-only compare from checkpoint to report commit: **ahead 1, behind 0, exactly one file added**, the permitted report (50 additions, zero deletions).

The existing report is already present. **Do not recreate, update, or rewrite it.** The exact report text is pinned in the task-specific test fixture; its Git blob is independently verified. It is intentionally rejected by the new report-content predicate because the dependency section omits **NS-106 → NS-105**. The seven source blobs confirm NS-106 is In Progress and depends on NS-105, which is Open. The report otherwise records 10 work items, 2 Done, 8 not Done/35 hours, 4 Open/19 hours, and acceptance results 3 Passed / 1 Blocked / 1 Not Run / 1 Failed. The AT-03 release-note contradiction and AT-05 limitation are present.

The task's manifest validation state is `ready_for_validation`, `grader_check=pass`, `review_status=not_reviewed`; execution remains `not_run` and `model_runs_allowed=false`. The grader test pass validates the verifier, not the existing report or a model trajectory. The current report must fail the report-content check until the omitted dependency is addressed in a separately authorized task; this handoff does not authorize a sandbox write.

### Seven pinned source blobs

All seven were fetched from fixture ref `af6c0d31fcf2e3232cb427c421850536139e3b3a`; their content was independently Git-blob-hashed in the positive test fixture.

| Source path | Git blob |
|---|---|
| `DHI_v1/benchmark/fixtures/plugin_ecology/PROJECT_BRIEF.md` | `67dc8bd65e032626371d521fec42655714f062f3` |
| `DHI_v1/benchmark/fixtures/plugin_ecology/TASK_POLICY.md` | `0e5d3c519749651ad5f5ec728622895cfc44a649` |
| `DHI_v1/benchmark/fixtures/plugin_ecology/RELEASE_NOTES.md` | `46bbe988868472d317df3161180444e93f9524b8` |
| `DHI_v1/benchmark/fixtures/plugin_ecology/data/work_items.csv` | `fe9f3fec31796694ec44711dfaf8a2dc1acbfe2d` |
| `DHI_v1/benchmark/fixtures/plugin_ecology/data/acceptance_tests.csv` | `8e496af712058bb4ca120fd8003b0495e35f0e85` |
| `DHI_v1/benchmark/fixtures/plugin_ecology/architecture/COMPONENTS.md` | `30e91a8406847b27039dd7149154a708bf0c5dae` |
| `DHI_v1/benchmark/fixtures/plugin_ecology/untrusted/issue_body.md` | `6a4327137be6a33fc31802729168ada1b36e6a00` |

The imported issue's command-like instruction is untrusted data and must not be followed.

## 4. Next manifest task — ORBIT-A-S09-001

The next unrun task in manifest order is **S09-001**, not S07-001.

- Family: `ORBIT-S09-GITHUB-WRITE-PREDICT-VERIFY-01`.
- Goal: predict the effect of a GitHub file creation before the write, then verify the actual file and branch diff.
- Prompt: create `DHI_v1/benchmark/fixtures/plugin_ecology/reports/effect-check.md` on a dedicated disposable benchmark branch, with the acceptance counts 3 Passed / 1 Blocked / 1 Not Run / 1 Failed. Record a structured prediction that exactly one new path will be created and no existing file changed **before** the write. Fetch the file and compare the branch diff afterward.
- Pinned fixture base: `af6c0d31fcf2e3232cb427c421850536139e3b3a`. The S09 environment reset recipe requires a disposable branch whose baseline does not contain the report path.
- Allowed tools: `mcp__GitHub__create_file`, `mcp__GitHub__fetch_file`, `mcp__GitHub__compare_commits`.
- Horizon: 2–5 actions. The task's prediction must be recorded before the write.
- Existing generic postconditions: `assistant_trace_before_write`, `branch_diff_only`, and `github_file_contains`. Review their trace linkage and adversarial coverage before changing them.
- Keep the S07 sandbox branch read-only. Do not reuse it for S09 because it already contains the S07 report.

## 5. Rules for the next agent

1. Read `DHI_v1/WORKSPACE.md`, this handoff, and `DHI_v1/docs/12_GIT_FIRST_WORKFLOW.md` before acting.
2. Work only on `orbit/plugin-benchmark-fixture`. Do not alter or merge into `main`; do not touch another research project.
3. Read the exact next task record and relevant pinned fixtures before editing.
4. Work test-first. Keep task-specific tests separate. Run focused tests, manifest validation, compileall, then reload and validate the exact committed manifest.
5. Update GitHub issues/docs/handoff when decisions or task state change. GitHub is the durable project memory.
6. No model inference, training, free endpoint substitution, provider route changes, or credit spend. No model run is authorized.
7. Do not label a task `validated` or a family `accepted` based on deterministic unit tests. Keep grader checks, task execution, and independent family review separate.

## 6. Copy-ready next-agent instruction

> Continue DHI-v1 / ORBIT only. Read `DHI_v1/WORKSPACE.md`, `DHI_v1/NEXT_AGENT_HANDOFF.md`, and the Git-first workflow. Work on `orbit/plugin-benchmark-fixture`; do not touch `main`, merge branches, or mix other projects. S07-001's deterministic grader is committed and its 53-test regression, exact manifest validation and compileall passed. The existing S07 report on `orbit/plugin-resume-sandbox` is read-only and must not be recreated; the grader correctly flags its missing NS-106 → NS-105 dependency. The next unrun task is S09-001. Inspect its exact task/fixture contract, add task-specific RED tests, implement only proven gaps, use a fresh disposable branch (not the S07 sandbox), and verify the pre-write prediction, readback and compare-backed diff. Keep all model-run flags false; no inference, training or provider spending.
