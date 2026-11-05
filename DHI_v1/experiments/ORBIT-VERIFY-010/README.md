# ORBIT-VERIFY-010 — exact-head plugin-native harness regression

**Status:** PASS — all offline engineering checks passed at the exact branch head.

- **Code under test / branch head:** `e045e43d41a5cd125f81dbfdac105937f3a161af`
- **Branch:** `orbit/plugin-benchmark-fixture`
- **Deepnote project:** `6415944e-8d6c-432c-a7cf-3bbaa997799c`
- **Notebook:** `3639f9a98ce5435fa4cd0168eaaca3a1`
- **Run:** `3d2f4a00-32e6-422c-b14e-50b158a89e31`
- **Verifier block:** `4c65dea71add40e4bf2165b8a81878e6`
- **Python:** 3.13.18
- **Execution platform:** Linux x86_64

## Results

| Gate | Result |
|---|---|
| Task manifest validator | PASS — 30 tasks, Stage A 30, Stage B 0, no errors |
| Full benchmark + environment tests | **207 passed, 0 failed** |
| Compileall | PASS |
| Runtime/entrypoint import smoke | PASS |
| Plugin task loader | PASS — 30 plans resolved; 0 model runs enabled |

The full command output, exact argv, return codes and timings are in [verification-report.json](results/verification-report.json).

## Research boundary

This is an **engineering / harness verification** result only.

- No live GitHub request or repository write was made.
- No TinyFish request was made by this run.
- No hosted model inference was called.
- No training or dataset-generation job was launched.
- All 30 source-manifest tasks remain `model_runs_allowed=false`.
- The manifest remains `authoring`, not frozen; all 30 tasks remain `ready_for_validation`, not validated.
- Stage B remains sealed and has 0 materialized tasks.

The run does not establish ORBIT model capability, a benchmark score, task-family independence, or training eligibility.

## Remaining blockers

1. **S06 precondition enforcement:** the plugin runner must evaluate manifest preconditions (including the exact branch-head SHA) before the first model call. The current run does not close that gap.
2. **Final artifact grounding:** `trace.final_artifacts` must be populated only from independently fetched/read-back artifacts, not the model's final answer or an unverified path claim.
3. **Live GitHub runtime:** Deepnote previously reported no project-scoped `GITHUB_TOKEN`, write flag or repository allowlist. The verified client remains offline-tested; no live provider request was made.
4. **Benchmark validation:** independent task review and grader validation are still open. Do not enable any model-run flags.
5. **Model access:** OpenRouter balance was previously observed at $0; no Qwen3.6/GPT-OSS base-model comparison is available yet.

## Next authorized work unit

Implement precondition evaluation and evidence-backed final-artifact collection in the plugin runner, test them with scripted handlers and fake provider state, and rerun the complete exact-head regression. Preserve model-run flags as false.
