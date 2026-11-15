# DHI-v1 / ORBIT — Research Status Tree

**As of:** 2026-11-15  
**Repository:** Kshitijpalsinghtomar/dhi  
**Active branch:** orbit/plugin-benchmark-fixture  
**Branch head at audit:** 28ed57fe4a320aee387f0d5d9ca1c3cdb2837a1c  
**Default branch:** main at c640e7152885e8c4e0171afd69b9a50ec711636a

> Scope is DHI-v1 / ORBIT only. This report does not combine GBA/DPAK, Oriael, FDLT, TENS or other programmes. GitHub remains the source of truth. No merge to main, model inference, training or provider-credit spending is authorized.

## 1. Research tree — what the work is and where it stands

    DHI-v1 — Predictive Agentic Intelligence
    └── ORBIT — empirical model-development programme
        ├── A. Research direction / novelty boundary
        │   ├── Earlier tool-acquisition/lifecycle novelty candidate
        │   │   └── REJECTED as insufficiently distinct from prior art
        │   ├── Joint task/world + tool-ecosystem state
        │   │   └── Implemented as measurement infrastructure, not a novelty claim
        │   └── Current question
        │       └── Can a learned policy improve real tool-use execution,
        │           recovery, prediction and verified goal closure?
        ├── B. Study 0 — untouched base-model capability screen [CURRENT GATE]
        │   ├── Stage A: 30 / 120 tasks materialized
        │   ├── Stage B: 0 / 120; sealed and unmaterialized
        │   ├── Deterministic grader checks: 20 / 30 pass; 10 not_run
        │   ├── Independent family review: 1 accepted; 29 not_reviewed
        │   ├── Model executions: 0 / 30
        │   └── Model-run permissions: 0 / 30 enabled
        ├── C. Study 1 — verified-execution trajectory SFT [NOT STARTED]
        │   ├── Requires real model-originated tool trajectories
        │   ├── Requires independently checked state deltas and postconditions
        │   └── Scripted fixtures and synthetic traces are not training positives
        ├── D. Study 2 — supervision ablations [PLANNED]
        │   ├── A: ordinary agentic SFT
        │   ├── B: A + pre-action effect prediction / observed state delta
        │   └── C: B + explicit goal-closure supervision
        └── E. Study 3 — generalization and robustness [PLANNED]
            ├── Held-out tools, schemas, combinations and task families
            ├── Controlled availability, schema, permission and state drift
            └── Safety, false closure, calibration, latency and cost guards

## 2. What is actually complete

- The plugin-native Stage A manifest contains 30 task instances across 10 strata.
- The tool registry, pinned synthetic environment/source fixtures, task contracts, trace grader and cross-record manifest validator are implemented.
- Twenty task-specific deterministic grader checks are recorded as passing; ten remain not_run.
- The latest integrated deterministic regression passed **134/134** in Deepnote run cda896d9-1462-421d-b1c5-9248ef945b48.
- Exact committed-manifest validation passed: Deepnote run 4d41b975-c1be-4f0a-8938-86db3a27192e, 30 tasks, zero validation errors; benchmark/environment compileall exit code 0.
- The research observer / joint-state measurement package passed 22/22 focused tests and compileall in run ca0c1e0e-bace-4927-ae65-5d83528eb59a.
- S06-002 cross-source report closure is integrated: two pinned sources, exact report readback and one-path compare. S07-001 checkpoint/resume and S09-001 effect-prediction verifier work are also covered by focused/integrated deterministic regressions.

**Evidence boundary:** these results verify code, fixtures, graders and reference workflows. They are not model-generated behavior, model capability scores, family acceptance or training evidence.

## 3. What is open / what we are solving now

**Immediate task: ORBIT-A-S08-002 — Firecrawl fallback recovery.**

Test the actual discovery decision chain using the pinned fixture:
1. Detect that the broad catalogue response contains a reranking fallback/timeout but still returns useful candidate items and nextTool.
2. Use the returned candidate/continuation evidence to make the provider-filtered packages/package discovery call.
3. Verify exact provider, capability, required inputs, ordering and discovery cost.
4. Keep execution cost separate from discovery cost. Do not execute the one-credit paid provider.
5. Add task-specific adversarial tests for false accepts before changing the grader.

After S08-002, the manifest still lists these ten grader checks as not_run:
S08-002, S09-002, S10-002, S02-003, S08-003, S06-003, S04-003, S07-002, S09-003, S06-004.

The 29 unreviewed task families remain a separate admission blocker. Do not convert grader-test passes into task-family acceptance. All 30 task executions remain not_run.

## 4. Open research questions — not conclusions

The current prior-art gate rejects a novelty claim based only on tool acquisition, lifecycle decisions, joint state, pre-action prediction or goal closure. The empirical questions still worth testing are:

- **H0 — modular baseline sufficiency:** does a strong modular agent with retrieval/planning/effect prediction match or beat a joint policy?
- **H1 — joint belief robustness:** does a jointly updated task/tool-ecosystem belief improve recovery under tool, schema, permission and availability drift?
- **H2 — feasibility and safe completion:** does explicit capability/dependency/permission feasibility reasoning reduce invalid actions and false completion without harming feasible-task success?
- **H3 — horizon interaction:** are any gains concentrated in long dependent workflows with mid-task ecosystem changes rather than short tasks?

These are falsifiable candidates from the research reset, not accepted novelty claims. The active prior-art gate requires matched comparisons and rejects gains that worsen safety, false closure, calibration, latency or cost.

## 5. Roadmap and gates

| Order | Gate | Current status | Exit condition |
|---|---|---|---|
| 1 | Benchmark implementation and deterministic regression | Verified | Graders, schemas, manifest and runtime checks pass |
| 2 | Finish remaining grader checks | In progress; 20/30 | All selected task graders validated with source-bound tests |
| 3 | Independent task-family review | Blocked; 1/30 accepted | Every admitted task reviewed or explicitly excluded |
| 4 | Freeze a genuine multi-task Stage A subset and matched protocol | Not ready | Exact tasks, graders, permissions, model revisions, seeds and budgets frozen |
| 5 | Study 0 untouched base-model screen | Not started / unauthorized | Approved funded route and explicit authorization; raw traces preserved |
| 6 | Failure analysis and trajectory collection | Not started | Real executions and independent closure evidence |
| 7 | Study 1 verified-trajectory SFT | Not started / unauthorized | Adjudicated, deduplicated, family-separated trajectories |
| 8 | Study 2 prediction / closure ablations | Planned | Matched A/B/C interventions; one factor changed at a time |
| 9 | Study 3 held-out transfer and drift robustness | Planned | Independent held-out evaluation and safety/cost analysis |

**How far along are we?** The evaluation infrastructure is materially built, but the scientific experiment has not begun. Stage A authoring is 25% of its 120-task target; deterministic grader checks are 20/30; independent family review is 1/30. Model inference, model-generated trajectories, capability scoring and training are all at zero. There is no defensible overall project-completion percentage yet.

## 6. Detours and decisions

- **Novelty hunting:** stopped on 2026-11-11 after the prior-art review found direct overlap. Do not keep expanding this line without new evidence.
- **Joint-state observer:** retained as measurement infrastructure; 22/22 deterministic tests pass. It is not a learned model or a novelty result.
- **Invent task-spec datasets:** two 120-row candidates were quarantined because the generated target did not match the user-task completion / valid execution-trajectory objective. They are not training data.
- **Adaption / inference access:** prior preflight and data-eligibility work did not produce an authorized, funded inference route. The last recorded OpenRouter balance was zero credits (2026-11-11). Do not route around this by switching to a free endpoint.
- **Benchmark branch integration:** work on task graders, reports and branch fixtures is preparation for Study 0, not evidence that Study 0 has run.

The main sideways drift was spending substantial effort on infrastructure, dataset generation and novelty exploration before producing model-originated evidence. The 2026-11-11 reset narrows the work: finish the existing 30-task screening slice, review it, then run the first controlled model screen when authorized. Do not expand the panel or add another provider adapter as a substitute for that gate.

## 7. Branch / PR / issue maintenance map

There are **13 branches total**: main plus 12 working/reference branches. They are not 12 competing implementation lines; most are pinned task fixtures or isolated reference outcomes.

| Branch | Role | Maintenance decision |
|---|---|---|
| main | Default baseline | Leave untouched |
| orbit/plugin-benchmark-fixture | Active implementation and manifest branch | Keep; PR #1 |
| orbit/plugin-resume-sandbox | S07-001 checkpoint/resume reference | Keep immutable |
| orbit/s06-runtime-report | S06-002 cross-source report reference | Keep immutable |
| orbit/s09-effect-prediction | S09-001 effect-prediction reference | Keep immutable |
| orbit/effect-forecast-check | S09-002 seeded check fixture | Keep as task fixture |
| orbit/effect-forecast-update | S09-003 existing-file update fixture | Keep as task fixture |
| orbit/tool-ecosystem-audit | S07-002 checkpoint/audit fixture | Keep as task fixture |
| orbit/sandbox/orbit-a-s06-001 | S06-001 isolated task sandbox | Keep as task fixture |
| orbit/sandbox/orbit-a-s07-001 | S07-001 isolated task sandbox | Keep as task fixture |
| orbit/sandbox/orbit-a-s07-002 | S07-002 isolated task sandbox | Keep as task fixture |
| orbit/sandbox/orbit-a-s09-001 | S09-001 isolated task sandbox | Keep as task fixture |
| orbit/sandbox/orbit-a-s09-003 | S09-003 isolated task sandbox | Keep as task fixture |

**PRs:** only PR #1 is open. It is the draft carrying the active branch and is intentionally unmerged. Keep it open as draft; refresh its description rather than opening a duplicate.

**Issues:** only issue #2 is open. It is the Study 0 control issue. Keep it open and update its stale status/next action; do not create a second tracker.

No branch was deleted: the sandbox/reference branches preserve reproducible task states and are either named by task or referenced by the manifest/handoff. Deleting them before a committed fixture-retention decision would damage reproducibility. No PR was merged or closed.

## 8. Current operating constraints

- Work only in Kshitijpalsinghtomar/dhi and on orbit/plugin-benchmark-fixture.
- Do not merge or modify main.
- Keep the task-specific reference/sandbox branches unchanged.
- Do not run model inference, training, paid provider execution or spend provider credits.
- Keep all task execution states not_run and all model_runs_allowed=false.
- Do not mark a task validated or a family accepted from synthetic trace fixtures or grader tests alone.
- Record each meaningful change, test result and next action in GitHub before moving to another work unit.

## Sources of truth

- Live workspace: WORKSPACE.md
- Next-agent handoff: NEXT_AGENT_HANDOFF.md
- Study 0 issue #2: https://github.com/Kshitijpalsinghtomar/dhi/issues/2
- Draft PR #1: https://github.com/Kshitijpalsinghtomar/dhi/pull/1
- Prior-art / novelty gate: docs/15_PRIOR_ART_AND_NOVELTY_GATE_2026-11-11.md
- Research direction reset: docs/14_RESEARCH_DIRECTION_RESET_2026-11-11.md
- ORBIT research method: docs/13_ORBIT_RESEARCH_METHOD.md
- Task manifest: benchmark/task_manifest.json
