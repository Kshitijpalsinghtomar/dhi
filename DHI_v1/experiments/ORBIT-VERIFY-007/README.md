# ORBIT-VERIFY-007 — canonical TinyFish runtime bundle regression

<badge>PASS</badge> **Final status: all checks passed**

**Code under test:** `28a0753c283cd0105d103ee4da11ac0847af0014`  
**Branch:** `orbit/plugin-benchmark-fixture`  
**Verifier:** Deepnote project `6415944e-8d6c-432c-a7cf-3bbaa997799c`, notebook `3639f9a98ce5435fa4cd0168eaaca3a1`  
**Successful run:** `ec2a3f4f-b421-41a8-9187-92ad21ed1dc2`

## Question

Does canonical TinyFish ID alignment, schema/handler bundling, and the existing DHI TinyFish client continue to pass the full benchmark/environment suite, and can the attached Deepnote TINYFISH integration prepare the canonical TinyFish-only task without a provider request?

## Source identity

The following files were compared byte-for-byte between Deepnote and GitHub at the pinned branch head:
- `DHI_v1/environment/tinyfish_client.py`
- `DHI_v1/environment/tests/test_tinyfish_client.py`
- `DHI_v1/benchmark/tests/test_tinyfish_plugin_bundle.py`
- `DHI_v1/benchmark/plugin_execution.py`
- `DHI_v1/benchmark/plugin_task_loader.py`

Task manifest blob SHA remains `f1a73f4cc377f0ea72a37f7d2f9a3e7476ffe033`, previously checked against the full 4,704-line manifest in 19 bounded windows.

## Focused TDD and live runtime evidence

- Red: `62b94d25-bd3e-417a-8088-91f6bad009cc` — collection failed because `tinyfish_plugin_bundle_from_env` did not yet exist.
- Focused green: `be6a0185-5eb8-4385-8299-f9c7be2a8658` — **20 passed** across the new plugin-bundle tests and existing TinyFish client tests.
- Live no-network preflight: `571b0e74-fdf8-4c52-836e-ffc1a4b3a103` — the actual Deepnote environment reported the TINYFISH key present, schemas and handlers under both canonical IDs, successful preparation of `ORBIT-A-S02-001`, source manifest model execution still false, and zero external calls.

## Full exact-head result

- Manifest validator: **PASS** — valid=true, 30 tasks, Stage A=30, Stage B=0, no errors.
- Combined benchmark + environment pytest: **178 passed, 0 failed** in 390.936 seconds (pytest summary: 343.92 seconds).
- `compileall`: **PASS** — exit code 0.
- Entrypoint imports: **PASS**.
- Plugin loader smoke: **PASS** — 30 task plans; **0 model runs enabled**.
- Actual TinyFish runtime no-network preflight: **PASS** — `TINYFISH_API_KEY` is present; both canonical schema IDs and handler IDs are available; `ORBIT-A-S02-001` prepares successfully through the generic dispatch boundary.
- Actual TinyFish Search/Fetch requests: **0**.
- Model inference / training / paid provider operations: **0**.
- Python: 3.13.18.

Full commands, outputs, exit codes, timings and environment details are archived in [results/verification-report.json](results/verification-report.json).

## Evidence boundary

This closes the **TinyFish canonical adapter engineering gate**. It proves that:
- the DHI TinyFish client publishes the manifest's canonical IDs;
- its schema bundle is available even without a credential, while handlers are exposed only when the runtime key exists;
- the real Deepnote TINYFISH environment exposes both canonical handlers;
- the TinyFish-only task can be prepared with those real schemas/handlers without making a network request.

It does **not** connect the generic dispatcher to the full model-turn loop, perform actual Search/Fetch calls, validate benchmark tasks end-to-end, or establish model capability. All live manifest tasks still have `model_runs_allowed=false`.

## Next gate

The next engineering task is the model-facing plugin runner/trace path: call the model with prepared canonical schemas, dispatch tool calls through the permission gate, write append-only plugin trace events, independently verify observed effects and postconditions, and pass traces to the existing grader. Start with a no-model scripted runner test and preserve model runs disabled. After that, implement the GitHub runtime bridge (16 task coverage); Firecrawl Alexandria transport remains absent from the Deepnote project. See [WORKSPACE.md](../../WORKSPACE.md).
