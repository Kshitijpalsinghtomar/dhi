# ORBIT task-panel integrity checkpoint — 2026-11-03

**Evidence class:** source-level static integrity inspection  
**Inspected branch:** `orbit/plugin-benchmark-fixture`  
**Inspected commit:** `3d57cc876dcd3f1f82c9d3ff884665de52c7f290`  
**Manifest:** `DHI_v1/benchmark/task_manifest.json`  
**Validator implementation:** `DHI_v1/benchmark/validate_task_manifest.py`  
**Regression suite:** `DHI_v1/benchmark/tests/test_task_manifest_validator.py`

## Result of the static integrity inspection

The manifest, schema, registry and referenced repository tree were fetched from the pinned GitHub commit. JSON parsing and an independent source-level recomputation of the canonical SHA-256 values were performed.

| Check | Observed | Result |
|---|---:|---|
| Stage A task records | 30 / 120 | Correct partial authoring state |
| Stage B task records | 0 / 120 | Empty; sealed |
| Task-family records | 30 | One record per referenced family |
| Unique task IDs | 30 / 30 | Pass |
| Unique family IDs | 30 / 30 | Pass |
| Deterministic task-instance hashes | 30 / 30 recomputed | Pass |
| Deterministic family fingerprints | 30 / 30 recomputed | Pass |
| Tool registry entries | 16 exact tool contracts | Pass |
| Task tool IDs registered and allowed | All visible/discoverable/required IDs | Pass |
| Task tool-schema fingerprints | All match pinned registry digest | Pass |
| Evidence references | 18 references, 0 missing | Pass |
| Cross-stage family/group overlap | None | Pass |
| Stage B task-body exposure | None | Pass |
| Structural integrity errors in the independent check | 0 | Pass |

### Task distribution

| Stratum | Stage A | Stage B |
|---|---:|---:|
| S01 | 2 | 0 |
| S02 | 3 | 0 |
| S03 | 4 | 0 |
| S04 | 3 | 0 |
| S05 | 4 | 0 |
| S06 | 4 | 0 |
| S07 | 2 | 0 |
| S08 | 3 | 0 |
| S09 | 3 | 0 |
| S10 | 2 | 0 |
| **Total** | **30** | **0** |

## Hash contract now recorded in code

- Canonical serialization: UTF-8 JSON, object keys sorted, compact separators, non-finite numbers rejected.
- Tool-registry hash: SHA-256 of the complete `tools` array after canonical serialization.
- Family fingerprint: SHA-256 of the canonical task definition fields: stratum, contract, environment, tool inventory, required capabilities, horizon, preconditions, postconditions, grader and policy.
- Task-instance hash: SHA-256 of the full task record after removing only `split_metadata.task_instance_sha256`.
- The JSON Schema now requires a task-instance hash. The validator recomputes both task and family hashes rather than merely checking their 64-character format.

The registry was corrected to include `mcp__GitHub__update_file`, which was already used by three task records. The registry now contains 16 tools and its digest is `76a1795899d4ba8e4c75efcb26896bf9f3926f485b2fb11392d84cd64d8e44f6`.

## Runtime test status — not executed

The Python implementation and 14 regression tests are committed, but they have **not** been executed in a Python runtime.

GitHub Actions run `41594301494` was triggered for commit `3d57cc876dcd3f1f82c9d3ff884665de52c7f290` and ended with conclusion `failure`. The job endpoint reported `runner_id=0` and an empty `steps` array; the log download returned no artifact. Therefore no pytest, compileall, or validator command ran. The failure is not evidence that the Python implementation or tests failed.

Repeat these commands from the repository root when a working Python runner is available:

```bash
python -m DHI_v1.benchmark.validate_task_manifest
python -m pytest -q DHI_v1/benchmark/tests/test_task_manifest_validator.py
python -m pytest -q DHI_v1/environment/tests DHI_v1/benchmark/tests
python -m compileall -q DHI_v1/environment DHI_v1/benchmark
```

## Decision and next action

Keep the panel in `authoring`; do not mark tasks validated or freeze it. No DHI model inference, candidate comparison, training run, or training-data promotion is authorized from this check.

Next: obtain a usable Python test runner, execute the validator and focused/full tests, repair any proven failures, then continue authoring independently grounded Stage A task families. Keep Stage B outside this shared manifest until its release gate is satisfied.
