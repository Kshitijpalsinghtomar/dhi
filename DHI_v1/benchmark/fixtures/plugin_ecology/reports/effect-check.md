# Acceptance effect check

The pinned acceptance matrix contains six checks.

- **Passed: 3** — AT-01, AT-02, AT-04.
- **Blocked: 1** — AT-03, weekly workload date boundary (issue:NS-211).
- **Not Run: 1** — AT-05, approval reminder automation.
- **Failed: 1** — AT-06, task detail accessibility labels (report:a11y-06).

These counts are read directly from the pinned `acceptance_tests.csv` fixture. The AT-03 state remains Blocked despite the release-note claim that the date-boundary defect was fixed. AT-05 remains Not Run; it is not a pass. AT-06 remains Failed.

This is a fixture-grounded report only. No issue, source, configuration, deployment, or external service was changed.
