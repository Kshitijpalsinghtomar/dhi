# DHI-v1 research code

This directory contains DHI research mechanisms. It is not the ORBIT benchmark runner.

## Joint state contract

`joint_state.py` stores independently observed task/world state and tool-ecosystem state, computes changes in each dimension, and scores pre-action forecasts against independently observed changes.

- Every snapshot has a source reference, revision, scope ID, and completeness flag.
- Diffs fail closed when scopes differ or snapshots are partial. Absence from a partial inventory is not evidence of removal.
- Unknown schema/capability/permission metadata is `None`; a known empty set is `()`.
- Renamed IDs are represented as removal plus addition. No identity alias is inferred.
- An omitted forecast (`None`) is unscored; an empty forecast (`()`) is a scored prediction of no change.
- World and ecosystem effects receive separate metrics.

This is a measurement contract and deterministic diff/scoring mechanism. It is **not** a learned belief model, planner, runtime integration, or DHI capability result.

## Focused tests

From the repository root:

```bash
python -m unittest discover -s DHI_v1/research/tests -v
python -m compileall -q DHI_v1/research
```

The next integration step is to populate these records from complete, independently sourced DHI environment observations. Do not put model forecasts into observed state. Do not connect this to the model runner until the provenance boundary is preserved end to end.
