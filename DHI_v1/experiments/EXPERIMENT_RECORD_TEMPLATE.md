# ORBIT Experiment Record Template

Copy this directory template to `DHI_v1/experiments/<ID>/` before an experiment starts. Fill every required field. Unknown values must be `unknown`, not guessed.

## README.md template

### Research question
- ID:
- Target capability:
- Question:
- Why it matters:
- Related prior experiments / decisions:

### Hypothesis
- Mechanism:
- Expected observation:
- Null / alternative:
- Falsifier:

### Frozen protocol
- Baseline commit:
- Candidate commit (before run):
- Model + exact revision:
- Tokenizer:
- Prompt / system interface hash:
- Task manifest hash:
- Stage / task IDs:
- Data hash and split:
- Tool manifest + schema hash:
- Environment + fixture hash:
- Permissions:
- Decode parameters:
- Seed(s):
- Primary metric, definition, direction:
- Independent guards:
- Minimum useful effect:
- Confirmation set:
- Budget (runs, wall time, tokens, compute, credits, tool calls):
- Exact execution command / invocation:

### Results
- Status: not_started | running | complete | crashed | blocked | invalid | inconclusive
- Raw artifact references and checksums:
- Baseline result:
- Candidate result:
- Paired delta + uncertainty:
- Per-stratum results:
- Guard outcomes:
- Resource use:
- Deviations from protocol:

### Adjudication
- Decision: keep_exploratory | reject | replicate | confirm | inconclusive | blocked | no_go
- Evidence class:
- Alternative explanations:
- Independent review:
- Limitations:
- Next falsifiable question:

## manifest.json minimum fields

```json
{
  "experiment_id": "EXP-XXX",
  "status": "not_started",
  "question": "",
  "hypothesis": {
    "mechanism": "",
    "expected_observation": "",
    "null": "",
    "falsifier": ""
  },
  "baseline": {
    "commit": "",
    "model_revision": "",
    "task_manifest_sha256": "",
    "environment_sha256": "",
    "tool_schema_sha256": ""
  },
  "candidate": {
    "commit": null,
    "intervention": "",
    "scope": []
  },
  "protocol": {
    "primary_metric": "",
    "direction": "",
    "independent_guards": [],
    "minimum_useful_effect": null,
    "seeds": [],
    "confirmation_split": "",
    "budget": {}
  },
  "results": {
    "raw_artifacts": [],
    "baseline": null,
    "candidate": null,
    "paired_delta": null,
    "confidence_interval": null,
    "per_stratum": {},
    "guard_failures": [],
    "decision": "pending"
  },
  "provenance": {
    "created_at_utc": "",
    "protocol_version": "ORBIT-RESEARCH-METHOD-1.0"
  }
}
```

## results.tsv

Use a tab-separated ledger. Header:

```text
experiment_id	commit	baseline_commit	hypothesis_id	intervention	primary_metric	metric_delta	guard_status	seed	status	decision	raw_artifact_ref
```

One row per run. Never omit crashes or failed attempts. Do not put tabs/newlines in field values.
