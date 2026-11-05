# ORBIT-VERIFY-011 — preconditions and readback exact-head regression

**Status:** PASS — exact-head offline regression passed.
**Code under test:** `cbcccd15be56df159351ac88b4580f07f98e9312`
**Branch:** `orbit/plugin-benchmark-fixture`

## Scope

This verification follows the implementation of two fail-closed gates in the plugin-native runner:

1. Manifest preconditions are evaluated through a trusted runtime observer before any model prediction or tool action. A failed or unavailable precondition closes the run as blocked with zero model calls.
2. Final artifacts are admitted only from successful declared file writes followed by independent provider readback. The content SHA-256 and Git blob SHA must match, and the trace must contain a verified readback event linked to the originating write.

The trace schema and deterministic validator now reject final artifacts that lack a verified readback event, contain mismatched content/hash/source metadata, or do not map to a successful earlier write. They also reject model/tool activity after failed or unavailable preconditions.

## Deepnote execution

- Project: `6415944e-8d6c-432c-a7cf-3bbaa997799c`
- Notebook: `3639f9a98ce5435fa4cd0168eaaca3a1`
- Full verifier block: `89c005b54269422d892c78584471717a`
- Full verifier run: `0987fae8-a416-4fb5-96d7-522d36b17202`
- Focused RED run: `88ee8db4-d085-4ca0-898e-f96fb9b3bfa3`
- Focused GREEN run: `27fef662-603f-44dd-b590-2b11a0048395`
- Python: 3.13.18
- Platform: Linux

## Results

| Gate | Result |
|---|---|
| Manifest validator | PASS — valid; 30 tasks; Stage A=30; Stage B=0; no errors |
| Full benchmark + environment pytest | **209 passed, 0 failed** |
| compileall | PASS |
| Entrypoint import smoke | PASS |
| Plugin task loader | PASS — 30 plans; 0 model runs enabled |

The raw verifier record includes exact argv, stdout, return codes and timings in [verification-report.json](results/verification-report.json).

## TDD evidence

- The two new regression tests were committed before implementation.
- Baseline RED: the runner rejected the new `precondition_observer` argument; both target regressions failed against the old runner.
- After implementation, the focused precondition/runner/trace-grader suite passed **31 tests**.
- The full exact-head regression then passed 209 tests.

New tests:
- `test_manifest_branch_head_precondition_blocks_model_before_first_completion`
- `test_successful_write_is_only_a_final_artifact_after_independent_readback`

## Evidence boundary

This is **offline engineering and harness verification only**:
- no GitHub, TinyFish, hosted-model or training API requests;
- no model inference or model-generated trajectory;
- no training or dataset-generation job;
- no benchmark task promoted to validated;
- no model-run permission enabled.

The source manifest remains authoring: all 30 Stage A tasks are `ready_for_validation`; Stage B is sealed and empty. All 30 `model_runs_allowed` flags remain false.

## Remaining blockers

1. **Trusted runtime wiring:** the new observer and readback callbacks are tested with scripted state and fake provider responses. A production/task-execution factory still needs to bind them to an authenticated GitHub runtime and the task's pinned sandbox branch. The branch name must be bound from trusted task/sandbox configuration, not chosen by model output.
2. **Live GitHub access:** prior Deepnote presence-only checks found no project-scoped `GITHUB_TOKEN`, write-enable flag or repository allowlist. No live provider call was attempted.
3. **Task validation:** independent reviewer/grader validation for all 30 tasks remains open.
4. **Model access:** no comparable untouched-model inference or training has run; the prior OpenRouter balance observation was $0.

## Next authorized work unit

Implement the trusted task-scoped runtime factory: resolve the dedicated sandbox branch from the environment fixture, check its branch/head before inference, bind write guards to that same branch and approved path set, and wire independent readback through the authenticated GitHub client. Test this with a fake GitHub server and explicit wrong-branch/readback-mismatch negatives. Preserve all manifest model-run flags as false.
