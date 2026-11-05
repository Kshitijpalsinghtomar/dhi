# ORBIT-S07-001 — persistent checkpoint resume and source re-read smoke

**Task:** ORBIT-A-S07-001  
**Checkpoint commit:** `04d0e12f48067b3b3a3de3ffe10944b7ef594984`  
**Sandbox branch:** `orbit/sandbox/orbit-a-s07-001`  
**Result:** Manual checkpoint/source re-read plus one-file report closure verified; model execution not run.

## Exact pinned source evidence

The checkpoint and seven source files were fetched at the exact checkpoint commit. Their observed Git blob IDs:

| File | Blob SHA |
|---|---|
| `checkpoints/resume-task-A.md` | `c1a32746e5b2dbdb02aa9fa2fd3c9b9e66b79827` |
| `PROJECT_BRIEF.md` | `67dc8bd65e032626371d521fec42655714f062f3` |
| `TASK_POLICY.md` | `0e5d3c519749651ad5f5ec728622895cfc44a649` |
| `RELEASE_NOTES.md` | `46bbe988868472d317df3161180444e93f9524b8` |
| `data/work_items.csv` | `fe9f3fec31796694ec44711dfaf8a2dc1acbfe2d` |
| `data/acceptance_tests.csv` | `8e496af712058bb4ca120fd8003b0495e35f0e85` |
| `architecture/COMPONENTS.md` | `30e91a8406847b27039dd7149154a708bf0c5dae` |
| `untrusted/issue_body.md` | `6a4327137be6a33fc31802729168ada1b36e6a00` |

## Report and branch diff

- Report: `DHI_v1/benchmark/fixtures/plugin_ecology/reports/resume-release-review.md`
- Report blob: `7141b3e77a7ee86832ac91de410a5f94d98aa924`
- Branch head/commit: `ee4215bf6f71e3d901987465fc1cf7eee10a2456`
- Compare from checkpoint: ahead=1, behind=0; exactly one file added; 58 additions, zero deletions.
- The report covers Release, Workload, Dependencies, Acceptance and Recommendation, and keeps AT-03 Blocked, AT-05 Not Run, and AT-06 Failed.

## Engineering changes exercised

- Trusted runtime supports `github_file_blob` preconditions and checks path, pinned commit, Git blob SHA and content/blob integrity.
- Runner records `checkpoint_resumed` only after a successful fetch of the matching pinned checkpoint.
- Runtime writes remain on a task-specific sandbox branch; checkpoint/source branches are read-only inputs.
- Focused checkpoint/action-horizon regression tests and the four affected test files passed in the current Deepnote project.

## Evidence boundary

This is a manual provider/source workflow and harness regression evidence. It is not an ORBIT model-generated trajectory, not a training result, and not an ORBIT capability score. Manifest execution remains `not_run`; `model_runs_allowed=false`.
