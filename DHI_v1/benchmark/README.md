# DHI-v1 Agentic Pilot Cases — 0.1

This is a small, hand-authored diagnostic seed set, not the frozen 120-task base-screen benchmark and not training data. It exists to validate task categories and grading contracts before model inference is connected.

## Contents

pilot_cases.json contains 12 cases covering:
- no-tool restraint;
- workspace inspection;
- hidden capability discovery;
- multi-step work and goal closure;
- no-op recognition;
- broken-path recovery;
- unavailable-resource honesty;
- protected-file invariants;
- current-fact verification;
- external app/plugin discovery;
- decoy-tool and permission reasoning;
- long-horizon interruption and resume.

Only cases marked file_workspace are executable in the current deterministic file environment. The remaining cases deliberately mark the missing environment integration; they must not be scored by pretending the file harness supports live web search, app marketplaces, private documents, or cross-session persistence.

## Integrity rules

- Task descriptions are hand-authored specifications, not generated action traces.
- No tool outputs, state changes, test results, or success labels are fabricated.
- postconditions are executable environment predicates where supported; otherwise they identify the required external grader.
- A missing original prompt is not a defect for an invented benchmark task; provenance and purpose are explicit.
- This suite is a pilot. It is not statistically sufficient for a model-quality claim and must be expanded, reviewed for ambiguity, split by task structure, and frozen before confirmatory testing.
