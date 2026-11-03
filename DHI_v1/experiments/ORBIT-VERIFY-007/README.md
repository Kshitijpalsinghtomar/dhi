# ORBIT-VERIFY-007 — canonical TinyFish runtime bundle regression

**Status:** prepared  
**Code under test:** `28a0753c283cd0105d103ee4da11ac0847af0014`  
**Branch:** `orbit/plugin-benchmark-fixture`  
**Verifier:** Deepnote project `6415944e-8d6c-432c-a7cf-3bbaa997799c`, notebook `3639f9a98ce5435fa4cd0168eaaca3a1`

## Question

Does canonical TinyFish ID alignment, schema/handler bundling, and the existing DHI TinyFish client continue to pass the full benchmark/environment suite, and can the attached Deepnote TINYFISH integration prepare the canonical TinyFish-only task without a provider request?

## Frozen checks

1. Confirm changed TinyFish files and the plugin loader/dispatch boundary match the pinned GitHub branch.
2. Confirm the manifest remains the same immutable blob used by ORBIT-VERIFY-006.
3. Run manifest validation.
4. Run all benchmark and environment pytest tests.
5. Run compileall and entrypoint import smoke.
6. Resolve all 30 task plans; confirm model runs remain disabled.
7. Build the TinyFish schema/handler bundle from the actual Deepnote TINYFISH environment integration.
8. Prepare task `ORBIT-A-S02-001` through the plugin execution boundary using a local in-memory copy with execution enabled; do not modify the source manifest.
9. Do not invoke the TinyFish Search/Fetch endpoints, any other provider, a model, or training.
10. Archive raw stdout, return codes, elapsed times, Python/platform and exact commit.

Only the ORBIT-VERIFY-007 selected block is to be executed. Do not run the notebook's saved regression cell or any provider-probe cells.

## Source identity

The following files were compared byte-for-byte between Deepnote and GitHub at the pinned branch head:
- `DHI_v1/environment/tinyfish_client.py`
- `DHI_v1/environment/tests/test_tinyfish_client.py`
- `DHI_v1/benchmark/tests/test_tinyfish_plugin_bundle.py`
- `DHI_v1/benchmark/plugin_execution.py`
- `DHI_v1/benchmark/plugin_task_loader.py`

Task manifest blob SHA remains `f1a73f4cc377f0ea72a37f7d2f9a3e7476ffe033`, previously checked against the full 4,704-line manifest in 19 bounded windows.

## Focused TDD and runtime evidence

- Red: `62b94d25-bd3e-417a-8088-91f6bad009cc` — collection failed because `tinyfish_plugin_bundle_from_env` did not yet exist.
- Focused green: `be6a0185-5eb8-4385-8299-f9c7be2a8658` — **20 passed** across the new plugin-bundle tests and existing TinyFish client suite.
- Live no-network preflight: `571b0e74-fdf8-4c52-836e-ffc1a4b3a103` — the actual Deepnote environment reported the TINYFISH key present, schemas and handlers under both canonical IDs, successful preparation of `ORBIT-A-S02-001`, source manifest model execution still false, and zero external calls.

## Evidence boundary

This proves that the existing TinyFish runtime integration can be represented through the canonical plugin registry IDs and prepared by the tested dispatch boundary. It does not make the full model runner execute plugin tasks, perform real TinyFish requests, validate tasks end-to-end, or establish ORBIT model capability.
