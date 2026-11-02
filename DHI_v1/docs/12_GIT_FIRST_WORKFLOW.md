# Git-First Research Workflow

**Applies to:** DHI-v1 / ORBIT  
**Authority:** This protocol governs all future DHI work unless a later committed decision changes it.

## Non-negotiable rule

GitHub is the durable project memory and source of truth. Chat messages, assistant memory, browser tabs, notebook titles, and uncommitted local files are not authoritative project state.

Do not wait until the end of a session to write a handover. Record work as it happens. A new session must be able to resume from the repository alone.

## Session start

1. Read `DHI_v1/WORKSPACE.md` first. It is the live continuation pointer.
2. Fetch the latest `main` commit and confirm the workspace file's recorded head/status is not stale.
3. Read the controlling plan, relevant method/benchmark/data protocol, decision log, and the exact experiment record needed for the next action.
4. Check the latest commits and repository changes before editing. Never overwrite a newer update based on an old local copy.
5. Keep DHI-v0, GBA/DPAK, and unrelated projects separate unless a committed DHI decision explicitly links them.

## Record as work happens

For each meaningful unit of work, update and commit the relevant records before moving to an unrelated unit:

- **Code change:** commit implementation, its regression tests, and the corresponding documentation update. State exactly what changed and what was not changed.
- **Experiment:** record the question, status, protocol/version, model and revision, data and split hashes, environment, configuration, seed, execution command, timestamps, raw output locations, metrics, uncertainty, failures, interpretation, limitations, decision, and next step.
- **Research/reference review:** record the source/version/date, what was checked, relevant findings, how it affects the existing DHI decision, and any uncertainty. Do not silently convert a source into a new project hypothesis.
- **Decision:** append a dated entry to `DHI_v1/docs/07_DECISIONS_AND_RESEARCH_LOG.md`. Preserve old entries; corrections must be labelled as corrections.
- **Failed or inconclusive work:** record it too. A failed run, blocker, unavailable endpoint, invalid dataset, or interrupted experiment is part of the research record.
- **Long-running task:** before launch, commit the intended run ID, frozen settings, expected outputs, and status=`running`. After it ends or is interrupted, commit the actual status and evidence. Never report a run as complete from a launch response alone.
- **Private/raw artifacts:** keep secrets and sensitive data out of Git. Store permitted raw artifacts in the designated private Deepnote/workspace or artifact store, then commit exact project, notebook, run, path, artifact ID, checksum, and access limitation into the DHI record. A summary without a retrievable artifact reference is not sufficient for a claimed result.

## Live workspace contract

`DHI_v1/WORKSPACE.md` must always provide:

- active programme and current research question;
- current phase and status (not started / running / blocked / complete);
- last verified repository head;
- current experiment/run identifiers and exact status;
- completed work with commit links;
- evidence available and evidence explicitly absent;
- active blockers and their concrete cause;
- the single next authorized action, including the exact file/command/tool or required access;
- work that must not be repeated, promoted, or changed.

Update the workspace at every meaningful checkpoint and at session end. Do not use it as a replacement for detailed experiment records or the append-only decision log.

## Experiment record structure

When an experiment starts, create a stable directory under `DHI_v1/experiments/<experiment-id>/` with:

- `README.md`: purpose, protocol, frozen configuration, status, interpretation, and next step;
- `manifest.json`: machine-readable IDs, revisions, hashes, seed, environment, parameters, and artifact references;
- `results/`: raw or derived results that are safe and small enough for Git;
- links to private raw artifacts where outputs are too large or sensitive.

Never fabricate tool results, execution traces, state deltas, model outputs, test outcomes, or task-success labels. Separate scripted references, model-generated runs, human review, and independent verification.

## Evidence and claims

Every reported result must identify its evidence class:

- `scripted-reference`
- `model-generated`
- `environment-verified`
- `independently-reviewed`
- `exploratory`
- `inconclusive`
- `rejected`
- `frozen`

Do not describe the scripted 8/8 pilot as model capability. Do not describe dataset quality scores as model capability. Do not call any model a winner until the matched base-model screen has been run and independently scored.

## Commit discipline

- Make commits small and tied to a meaningful work unit.
- Use messages that state the actual change/result, not vague messages such as "progress" or "update".
- Keep implementation, tests, and records traceable to one another.
- After each commit, verify the commit exists on the intended branch and fetch the changed files again.
- Before starting another work unit, ensure the previous unit's status and next action are committed in `WORKSPACE.md`.
- If work is interrupted, leave a committed checkpoint. Do not leave the only explanation in chat.
- Never claim a change was saved unless the returned commit SHA and the resulting repository content have been checked.

## Session end / interruption

Do not produce a chat-only handover. Update the live workspace file with:
1. what was actually completed;
2. the commit(s) containing it;
3. exact tests/commands and their result;
4. what remains incomplete;
5. current blockers;
6. one next authorized action.

The chat response should be a brief pointer to the relevant Git commits/files. The repository must contain enough information for a fresh agent to continue without the previous conversation.

## Project boundary

This workflow applies to DHI-v1 / ORBIT only. It does not authorize importing GBA/DPAK experiments, claims, or hypotheses. Any cross-project dependency requires an explicit DHI decision and a precise reference.
