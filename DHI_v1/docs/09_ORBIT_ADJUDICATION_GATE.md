# ORBIT adjudication and training-promotion gate

**Date:** 2026-10-31  
**Status:** Implemented; full-dataset promotion is blocked pending complete export and review.

## 1. Why this gate exists

Adaption's generation-quality score is a generation-process signal. It is not proof that a completion is factually correct, safe, executable, source-grounded, or appropriate as a DHI training target.

ORBIT's visible sample contains fluent but materially flawed answers, including:
- unsupported scientific precision and incorrect scientific mechanisms;
- unsafe or incomplete low-level code;
- false claims that files were changed or tests were run;
- unsupported claims about private repositories and model identity;
- overconfident legal, medical, and safety conclusions;
- evaluation logic that mistakes robustness failures for proof of data contamination.

Accordingly, a generated row is not promoted from an Adaption quality grade alone.

## 2. Current audit scope and result

The Adaption dataset reports 300 processed rows. The connected View page exposed 100 top-level table slots. A depth-aware table parser yielded:
- 98 complete prompt/completion pairs;
- 2 incomplete slots (visible rows 30 and 65);
- 0 normalized duplicate prompts among the 98 complete pairs;
- 0 exact duplicate completions among the 98 complete pairs.

The 98 complete rows received a conservative model-assisted semantic triage:
- **25 candidate** — potentially useful after independent verification;
- **53 revise** — meaningful idea, but requires substantial correction or qualification;
- **20 reject** — serious technical/factual, safety, provenance, or false-completion failure.

This is a partial-sample adjudication, not an independent human expert review and not a verdict on the unobserved 200 rows.

## 3. Stable review lineage

The View table does not expose a stable dataset UUID for each row. Visible row numbers are positions, not reliable join keys.

Each visible prompt is assigned a SHA-256 fingerprint over NFKC-normalized, case-folded text with punctuation normalized to spaces. The fingerprint manifest is retained alongside the adjudication file so judgements can be reconciled against the full dataset export.

The View headers are ENHANCED PROMPT and ENHANCED COMPLETION. The evaluation mapping suggested these correspond to raw fields invented_prompt and invent_completion, respectively, but this raw-field mapping remains provisional until the fingerprints are matched against the complete export. Do not silently substitute original_prompt/original_completion.

## 4. Provisional files in the Deepnote research workspace

In project DHI — ORBIT Research Lab:
- data/orbit_visible_rows.jsonl — 98 complete visible source pairs.
- audit/orbit_first100_manual_judgement.json — row-level judgements and prompt fingerprints.
- audit/orbit_first100_manual_judgement.csv — compact judgement table.
- audit/orbit_first100_fingerprint_manifest.csv — stable fingerprints for reconciliation.
- audit/orbit_candidate_rows_provisional.jsonl — 25 provisional candidates.
- audit/orbit_revise_rows_provisional.jsonl — 53 rows needing revision.
- audit/orbit_reject_rows_provisional.jsonl — 20 excluded rows.
- audit/orbit_candidate_manifest.csv — candidate reasons and issue categories.

Every row in all three split files has train_eligible=false. The provisional candidate set is not a training set.

## 5. Executable promotion gate

New files:
- DHI_v1/benchmark/orbit_adjudication.py
- DHI_v1/benchmark/tests/test_orbit_adjudication.py

The gate requires:
1. The exact expected row count (default 300) to be present. Partial exports fail closed.
2. Explicit prompt and completion column names. There is no silent column guessing.
3. A stable source uuid or id per row.
4. Unique normalized prompt fingerprints so review joins are unambiguous.
5. Exactly one review record for every source prompt and no unmatched judgement records.
6. A row verdict of candidate, revise, or reject.
7. All four independent checks explicitly true for promotion: semantic correctness, factual support, execution-claim verification, and safety review.
8. An explicit train, validation, or test split and a group_id.
9. Every row with the same group_id to remain in one split.

Incomplete candidates and all revise/reject rows are held out. The gate emits a stable report with source and judgement hashes. It does not treat an LLM's self-evaluation as independent evidence.

### Focused test result

Seven standard-library unittest tests passed in the connected Deepnote CPU workspace on 2026-10-31. They cover partial-dataset rejection, explicit column mapping, incomplete verification, valid promotion, duplicate prompts, incomplete review coverage, and split leakage.

This is a focused unit-test pass for the adjudication gate only. It is not a full DHI repository test-suite pass and does not establish model capability.

### Invocation after the complete export and review are available

    python DHI_v1/benchmark/orbit_adjudication.py --input outputs/orbit_full_300.jsonl --judgements outputs/orbit_full_300_judgements.json --expected-rows 300 --prompt-column invented_prompt --completion-column invent_completion

Use those two raw column names only after matching all 98 known prompt fingerprints to the full export. If another field matches, use that field explicitly instead.

## 6. Current training decision

**SFT and DPO remain blocked.** The current dataset does not have full 300-row audit coverage, and the 98-row sample has 20 rejects plus 53 revision cases. Furthermore, the examples are mostly standalone instruction/answer pairs, not verified environment-interaction trajectories. They may support a small generic instruction-following pilot later, but they are not sufficient as the core DHI collaboration/tool-use behaviour dataset.

Next:
1. Obtain the complete 300-row JSONL export through the authenticated Adaption download endpoint.
2. Reconcile the 98 fingerprints and establish the exact prompt/completion columns.
3. Adjudicate the remaining 202 rows with the same rubric.
4. Correct or discard revision cases; retain rejected cases only as negative diagnostics, not as positive SFT examples.
5. Independently verify all proposed candidates and assign grouped train/validation/test splits.
6. Run the promotion gate and inspect the generated report.
7. Only then consider a small, compute-conscious Qwen3.5-4B SFT run and compare it with the untouched base on a frozen behavioural evaluation set.

Do not inflate the dataset with duplicates to meet platform row minimums. If the verified candidate count is too small, build more tasks and real execution trajectories instead.


## 7. DHI environment and reference-pilot validation (2026-10-31)

While the full ORBIT export remains unavailable, the connected DHI environment was advanced independently so the project does not stall on dataset access.

The following repository defects were found and fixed:
- bare JSON `true`/`false` values in the Python tool catalogue prevented a clean environment import;
- the basic fixture manifest contained a stale README SHA-256 and correctly blocked fixture materialization;
- the no-op fixture variant used Markdown inline code while its postcondition expected unformatted text, causing a correct no-write action to fail closure.

Regression tests now cover all three conditions. Eleven focused standard-library tests passed: 2 tool-catalogue tests, 7 ORBIT promotion-gate tests, and 2 fixture integrity/no-op tests.

The eight supported file-workspace cases were then executed individually through `run_pilot_benchmark` using a deterministic scripted reference client. All 8/8 passed, with 12 tool calls, 20 turns, and 8 successful closures. The only changed file in mutating tasks was README.md. These are reference-policy harness results, not LLM capability results; the scripted client is not a model and the traces are not eligible as model-generated training data.

See [`10_DHI_SCRIPTED_REFERENCE_PILOT_RESULTS.md`](10_DHI_SCRIPTED_REFERENCE_PILOT_RESULTS.md) for case-level results, interpretation, and the next model-facing evaluation design.
