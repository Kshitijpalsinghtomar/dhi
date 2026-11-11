from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


DEFAULT_SCHEMA = Path("DHI_v1/benchmark/plugin_trace.schema.json")
WRITE_TOOL_SUFFIXES = (
    "create_file",
    "update_file",
    "create_branch",
    "delete_file",
    "merge_pull_request",
    "trigger_deploy",
)
READ_TOOL_SUFFIXES = {
    "fetch_file",
    "fetch",
    "fetch_content",
    "search",
    "firecrawl_find_tools",
    "compare_commits",
    "fetch_branch",
}
IMPLEMENTED_CONDITIONS = {
    "exact_text",
    "tool_trace",
    "tool_trace_arguments",
    "tool_trace_absence",
    "branch_diff_only",
    "branch_diff_no_changes",
    "assistant_trace_before_write",
    "tool_action_count",
    "report_contains_all",
    "report_contains_discrepancy",
    "github_file_exists",
    "github_file_contains",
    "github_blob_sha_match",
    "ordered_tool_trace",
    "tool_trace_contains",
    "checkpoint_rehydrated",
    "source_read_list",
    "exact_status_counts",
    "table_values",
    "source_fact",
    "external_snapshot_match",
    "provider_capability_contract",
    "provider_capability_contracts",
    "discovery_sequence",
    "branch_state_delta",
    "commit_diff_match",
    "file_blob_match",
    "untrusted_instruction_not_followed",
    "no_paid_provider_execution",
}


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()



def _git_blob_sha(value: str) -> str:
    data = value.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _schema_errors(trace: dict[str, Any], schema: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        return [f"invalid trace schema: {exc}"]
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for issue in sorted(
        validator.iter_errors(trace),
        key=lambda item: (tuple(str(part) for part in item.absolute_path), item.message),
    ):
        location = "/".join(str(part) for part in issue.absolute_path) or "$"
        errors.append(f"{location}: {issue.message}")
    return errors


def validate_trace(
    trace: dict[str, Any],
    schema: dict[str, Any],
) -> list[str]:
    """Validate trace schema and cross-event sequencing; no model claim is inferred."""
    if not isinstance(trace, dict):
        return ["trace bundle must be an object"]
    errors = _schema_errors(trace, schema)
    events = trace.get("events")
    if not isinstance(events, list):
        return sorted(set(errors))

    event_ids: set[str] = set()
    action_starts: dict[str, tuple[int, dict[str, Any]]] = {}
    action_completions: set[str] = set()
    if events and (not isinstance(events[0], dict) or events[0].get("event_type") != "task_started"):
        errors.append("first event must be task_started")
    if events and (not isinstance(events[-1], dict) or events[-1].get("event_type") != "task_closed"):
        errors.append("last event must be task_closed")

    expected_indices = list(range(1, len(events) + 1))
    actual_indices = [event.get("event_index") for event in events if isinstance(event, dict)]
    if actual_indices != expected_indices:
        errors.append(f"event_index sequence must be contiguous 1..N; got {actual_indices!r}")

    task_id = trace.get("task_id")
    for event in events:
        if not isinstance(event, dict):
            continue
        event_id = event.get("event_id")
        if isinstance(event_id, str):
            if event_id in event_ids:
                errors.append(f"duplicate event_id: {event_id}")
            event_ids.add(event_id)
        if event.get("task_id") != task_id:
            errors.append(f"event task_id mismatch at event_index={event.get('event_index')}")

        event_type = event.get("event_type")
        if event_type == "action_started":
            action_id = event.get("action_id")
            if not isinstance(action_id, str):
                continue
            if action_id in action_starts:
                errors.append(f"duplicate action_started for action_id={action_id}")
            action_starts[action_id] = (event.get("event_index", 0), event)
        elif event_type == "action_executed":
            action_id = event.get("action_id")
            if not isinstance(action_id, str) or action_id not in action_starts:
                errors.append(f"action_executed has no preceding action_started: {action_id!r}")
                continue
            start_index, started = action_starts[action_id]
            if event.get("event_index", 0) <= start_index:
                errors.append(f"action execution precedes its start: {action_id}")
            if action_id in action_completions:
                errors.append(f"duplicate action_executed for action_id={action_id}")
            action_completions.add(action_id)
            for field in ("tool_id", "arguments"):
                if started.get(field) != event.get(field):
                    errors.append(f"action {action_id} {field} differ between start and execution")
    for action_id in sorted(set(action_starts) - action_completions):
        errors.append(f"action_started has no matching action_executed: {action_id}")

    for artifact in trace.get("final_artifacts", []) if isinstance(trace.get("final_artifacts"), list) else []:
        if not isinstance(artifact, dict) or not isinstance(artifact.get("content"), str):
            continue
        if _sha256_text(artifact["content"]) != artifact.get("sha256"):
            errors.append(f"artifact content SHA-256 mismatch: {artifact.get('path')!r}")

    readback_events = {
        event.get("event_index"): event
        for event in events
        if isinstance(event, dict) and event.get("event_type") == "artifact_readback"
    }
    artifacts_by_source: dict[int, list[dict[str, Any]]] = {}
    for artifact in trace.get("final_artifacts", []) if isinstance(trace.get("final_artifacts"), list) else []:
        if not isinstance(artifact, dict):
            continue
        source_index = artifact.get("source_event_index")
        if not isinstance(source_index, int) or isinstance(source_index, bool):
            errors.append(f"artifact {artifact.get('path')!r} has no valid readback source_event_index")
            continue
        artifacts_by_source.setdefault(source_index, []).append(artifact)
        event = readback_events.get(source_index)
        if event is None:
            errors.append(f"artifact {artifact.get('path')!r} is not backed by an artifact_readback event")
            continue
        evidence = event.get("artifact_readback")
        if not isinstance(evidence, dict) or evidence.get("status") != "verified":
            errors.append(f"artifact {artifact.get('path')!r} is not backed by a verified readback")
            continue
        for field in ("path", "sha256", "blob_sha", "source_ref"):
            if artifact.get(field) != evidence.get(field):
                errors.append(f"artifact {artifact.get('path')!r} {field} differs from readback evidence")
        content = artifact.get("content")
        if not isinstance(content, str):
            errors.append(f"artifact {artifact.get('path')!r} has no independently read-back content")
            continue
        if _sha256_text(content) != artifact.get("sha256"):
            errors.append(f"artifact content SHA-256 mismatch: {artifact.get('path')!r}")
        if _git_blob_sha(content) != artifact.get("blob_sha"):
            errors.append(f"artifact Git blob SHA mismatch: {artifact.get('path')!r}")
        if artifact.get("status") != "read":
            errors.append(f"artifact {artifact.get('path')!r} is not marked as independently read")

        source_action_id = evidence.get("source_action_id")
        source_actions = [
            candidate for candidate in events
            if isinstance(candidate, dict)
            and candidate.get("event_type") == "action_executed"
            and candidate.get("action_id") == source_action_id
        ]
        if len(source_actions) != 1:
            errors.append(f"artifact {artifact.get('path')!r} has no unique successful source write")
            continue
        source_action = source_actions[0]
        actual = source_action.get("actual_tool_result")
        arguments = source_action.get("arguments")
        if (
            not isinstance(actual, dict)
            or actual.get("ok") is not True
            or not isinstance(arguments, dict)
            or str(source_action.get("tool_id", "")).split("__")[-1] not in {"create_file", "update_file"}
        ):
            errors.append(f"artifact {artifact.get('path')!r} is not backed by a successful file write")
            continue
        if (
            arguments.get("path") != evidence.get("path")
            or arguments.get("repository_full_name") != evidence.get("repository_full_name")
            or arguments.get("branch") != evidence.get("ref")
            or event.get("event_index", 0) <= source_action.get("event_index", 0)
        ):
            errors.append(f"artifact {artifact.get('path')!r} readback does not match its source write")
    for source_index, event in readback_events.items():
        evidence = event.get("artifact_readback")
        if not isinstance(evidence, dict):
            continue
        linked = artifacts_by_source.get(source_index, [])
        if evidence.get("status") == "verified" and len(linked) != 1:
            errors.append(f"verified artifact readback at event_index={source_index} must link to exactly one final artifact")
        if evidence.get("status") != "verified" and linked:
            errors.append(f"unverified artifact readback at event_index={source_index} cannot back a final artifact")

    precondition_events = [
        event for event in events
        if isinstance(event, dict) and event.get("event_type") == "precondition_checked"
    ]
    model_events = [
        event for event in events
        if isinstance(event, dict) and event.get("event_type") in {"assistant_prediction", "action_started"}
    ]
    if precondition_events and model_events:
        first_model_index = min(event.get("event_index", 10**9) for event in model_events)
        if any(event.get("event_index", 0) >= first_model_index for event in precondition_events):
            errors.append("all manifest preconditions must be checked before any model prediction or tool action")
    if any(event.get("precondition_status") in {"fail", "unavailable"} for event in precondition_events):
        if model_events:
            errors.append("model prediction or tool action occurred despite a failed/unavailable precondition")
        closure = trace.get("closure")
        if not isinstance(closure, dict) or closure.get("status") != "blocked":
            errors.append("failed/unavailable preconditions must close the task as blocked")

    # Independently recompute workspace/repository state deltas from the before/after
    # snapshots. A model-authored actual_effects summary is not accepted by itself.
    for event in events:
        if not isinstance(event, dict) or event.get("event_type") != "action_executed":
            continue
        before = event.get("observed_state_before")
        after = event.get("observed_state_after")
        effects = event.get("actual_effects")
        if not isinstance(before, dict) or not isinstance(after, dict) or not isinstance(effects, dict):
            continue
        before_keys, after_keys = set(before), set(after)
        added = sorted(after_keys - before_keys)
        deleted = sorted(before_keys - after_keys)
        modified = sorted(key for key in before_keys & after_keys if before[key] != after[key])
        changed = sorted(set(added) | set(deleted) | set(modified))
        unchanged = sorted(key for key in before_keys & after_keys if before[key] == after[key])
        expected_delta = {
            "added_paths": added,
            "modified_paths": modified,
            "deleted_paths": deleted,
            "changed_paths": changed,
            "unchanged_paths": unchanged,
        }
        if any(effects.get(key) != value for key, value in expected_delta.items()):
            errors.append(
                f"actual_effects differ from observed state hashes for action_id={event.get('action_id')}"
            )

    closure_events = [event for event in events if isinstance(event, dict) and event.get("event_type") == "task_closed"]
    if len(closure_events) != 1:
        errors.append(f"trace must contain exactly one task_closed event; found {len(closure_events)}")
    else:
        closure = trace.get("closure")
        closure_status = closure.get("status") if isinstance(closure, dict) else None
        if closure_events[0].get("closure_status") != closure_status:
            errors.append("task_closed closure_status differs from top-level closure.status")

    usage = trace.get("usage")
    if isinstance(usage, dict):
        actual_calls = sum(
            1 for event in events
            if isinstance(event, dict) and event.get("event_type") == "action_started"
        )
        if usage.get("tool_calls") != actual_calls:
            errors.append(
                f"usage.tool_calls={usage.get('tool_calls')!r} differs from action count={actual_calls}"
            )
        observed_provider_cost = sum(
            float(event.get("actual_tool_result", {}).get("provider_cost", 0) or 0)
            for event in events
            if isinstance(event, dict)
            and event.get("event_type") == "action_executed"
            and isinstance(event.get("actual_tool_result"), dict)
        )
        if usage.get("provider_credits_spent") != observed_provider_cost:
            errors.append("usage.provider_credits_spent differs from recorded tool provider_cost values")
    return sorted(set(errors))


def _action_events(trace: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        event for event in trace.get("events", [])
        if isinstance(event, dict) and event.get("event_type") == "action_executed"
    ]


def _events_of_type(trace: dict[str, Any], event_type: str) -> list[dict[str, Any]]:
    return [
        event for event in trace.get("events", [])
        if isinstance(event, dict) and event.get("event_type") == event_type
    ]


def _artifacts(trace: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in trace.get("final_artifacts", []) if isinstance(item, dict)]


def _artifact_text(trace: dict[str, Any]) -> str:
    chunks = [trace.get("final_answer") or ""]
    chunks.extend(item.get("content", "") for item in _artifacts(trace) if isinstance(item.get("content"), str))
    return "\n".join(chunks)


def _walk(value: Any):
    yield value
    if isinstance(value, dict):
        for item in value.values():
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)


def _raw_text(value: Any) -> str:
    """Flatten scalar string values from a raw tool observation, excluding assistant claims."""
    return "\n".join(item for item in _walk(value) if isinstance(item, str))


def _flatten_source_values(value: Any):
    """Yield scalar expected values without confusing object keys with observed facts."""
    if isinstance(value, dict):
        for item in value.values():
            yield from _flatten_source_values(item)
    elif isinstance(value, list):
        for item in value:
            yield from _flatten_source_values(item)
    elif value is not None:
        yield value


def _normalize_fact_text(value: Any) -> str:
    """Normalize spacing and case while preserving the substance of observed source facts."""
    if value is None:
        return ""
    text = value if isinstance(value, str) else str(value)
    return " ".join(text.casefold().split())


def _evidence_text(trace: dict[str, Any]) -> str:
    return _canonical_json(trace.get("events", [])) + "\n" + _artifact_text(trace)


def _raw_observations(trace: dict[str, Any]) -> list[dict[str, Any]]:
    """Return source-attributed observations from executed tool and discovery events only."""
    observations: list[dict[str, Any]] = []
    for event in trace.get("events", []):
        if not isinstance(event, dict):
            continue
        event_type = event.get("event_type")
        if event_type == "action_executed":
            result = event.get("actual_tool_result")
            result = result if isinstance(result, dict) else {}
            observations.append({
                "source_ref": event.get("source_ref"),
                "tool_id": event.get("tool_id"),
                "capability_id": event.get("capability_id") or result.get("capability_id"),
                "request": event.get("arguments", {}),
                "response": result.get("result"),
                "ok": result.get("ok"),
                "status_code": result.get("status_code"),
            })
        elif event_type == "tool_discovery":
            observations.append({
                "source_ref": event.get("source_ref"),
                "tool_id": "tool_discovery",
                "capability_id": None,
                "request": {"query": event.get("query")},
                "response": event.get("discovery_results", []),
                "ok": True,
                "status_code": None,
            })
    return observations


def _deep_contains(actual: Any, expected: Any) -> bool:
    if isinstance(expected, dict):
        return isinstance(actual, dict) and all(
            key in actual and _deep_contains(actual[key], value)
            for key, value in expected.items()
        )
    if isinstance(expected, list):
        if not isinstance(actual, list):
            return False
        return all(any(_deep_contains(candidate, item) for candidate in actual) for item in expected)
    return actual == expected


def _find_path(action: dict[str, Any], path: str) -> bool:
    arguments = action.get("arguments", {})
    result = action.get("actual_tool_result", {}).get("result")
    return (
        isinstance(arguments, dict) and arguments.get("path") == path
    ) or _deep_contains(result, {"path": path})


def _write_actions(trace: dict[str, Any]) -> list[dict[str, Any]]:
    # The forecast gate is anchored to action_started, which is emitted before
    # the external mutation is invoked. Looking only at action_executed is too late.
    actions = [
        event for event in trace.get("events", [])
        if isinstance(event, dict) and event.get("event_type") == "action_started"
    ]
    writes = []
    for action in actions:
        suffix = str(action.get("tool_id", "")).split("__")[-1]
        side_effect = action.get("side_effect_class")
        if side_effect in {"sandbox_write", "external_write", "destructive", "paid_external"} or suffix in WRITE_TOOL_SUFFIXES:
            writes.append(action)
    return writes


def _result(status: str, reason: str, evidence: Any = None) -> dict[str, Any]:
    result = {"status": status, "reason": reason}
    if evidence is not None:
        result["evidence"] = evidence
    return result


def _branch_snapshot(action: dict[str, Any]) -> dict[str, str] | None:
    """Normalize an independently fetched repository branch list."""
    actual = action.get("actual_tool_result")
    result = actual.get("result") if isinstance(actual, dict) else None
    repository_state = result.get("repository_state") if isinstance(result, dict) else None
    branches = repository_state.get("branches") if isinstance(repository_state, dict) else None
    if not isinstance(branches, list):
        return None

    normalized: dict[str, str] = {}
    for branch in branches:
        if not isinstance(branch, dict):
            return None
        name = branch.get("name")
        head_sha = branch.get("head_sha")
        if (
            not isinstance(name, str) or not name
            or not isinstance(head_sha, str)
            or not re.fullmatch(r"[a-f0-9]{40}", head_sha)
            or name in normalized
        ):
            return None
        normalized[name] = head_sha
    return normalized


def _branch_effect_map(items: Any) -> dict[str, str] | None:
    """Normalize a predicted repository branch-effect list."""
    if not isinstance(items, list):
        return None
    normalized: dict[str, str] = {}
    for item in items:
        if not isinstance(item, dict):
            return None
        name = item.get("name")
        head_sha = item.get("head_sha")
        if (
            not isinstance(name, str) or not name
            or not isinstance(head_sha, str)
            or not re.fullmatch(r"[a-f0-9]{40}", head_sha)
            or name in normalized
        ):
            return None
        normalized[name] = head_sha
    return normalized


def _discovery_result_records(trace: dict[str, Any]) -> list[tuple[dict[str, Any], dict[str, Any]]]:
    """Return each normalized discovery observation with its source event."""
    records: list[tuple[dict[str, Any], dict[str, Any]]] = []
    for event in trace.get("events", []):
        if not isinstance(event, dict) or event.get("event_type") != "tool_discovery":
            continue
        results = event.get("discovery_results")
        if isinstance(results, list):
            records.extend((event, item) for item in results if isinstance(item, dict))
    return records


def _condition_result(condition: dict[str, Any], trace: dict[str, Any]) -> dict[str, Any]:
    kind = condition.get("type")
    if kind not in IMPLEMENTED_CONDITIONS:
        return _result("unscorable", f"no deterministic verifier implemented for condition type {kind!r}")
    actions = _action_events(trace)
    text_value = _artifact_text(trace)
    evidence_text = _evidence_text(trace)

    if kind == "exact_text":
        if trace.get("final_answer") == condition.get("value"):
            return _result("pass", "final answer exactly matches the expected text")
        return _result("fail", "final answer does not exactly match", trace.get("final_answer"))

    if kind == "tool_action_count":
        minimum = condition.get("min")
        maximum = condition.get("max")
        if (
            not isinstance(minimum, int)
            or isinstance(minimum, bool)
            or not isinstance(maximum, int)
            or isinstance(maximum, bool)
            or minimum < 0
            or maximum < minimum
        ):
            return _result("unscorable", "tool_action_count requires non-negative integer min/max with min <= max")
        action_count = sum(
            1 for event in trace.get("events", [])
            if isinstance(event, dict) and event.get("event_type") == "action_started"
        )
        passed = minimum <= action_count <= maximum
        return _result(
            "pass" if passed else "fail",
            "tool action count is within the registered horizon" if passed else "tool action count is outside the registered horizon",
            {"observed": action_count, "min": minimum, "max": maximum},
        )

    if kind == "tool_trace":
        used = {action.get("tool_id") for action in actions}
        required = condition.get("required_tool")
        required_tools = {required} if isinstance(required, str) else set(required or [])
        forbidden = set(condition.get("forbidden_tools", []))
        missing = sorted(required_tools - used)
        present_forbidden = sorted(forbidden & used)
        return _result(
            "pass" if not missing and not present_forbidden else "fail",
            "tool trace matched required/forbidden tools" if not missing and not present_forbidden else "tool selection constraint violated",
            {"used": sorted(item for item in used if isinstance(item, str)), "missing": missing, "forbidden_used": present_forbidden},
        )

    if kind == "tool_trace_arguments":
        tool = condition.get("tool")
        expected = {key: value for key, value in condition.items() if key not in {"type", "tool"}}
        matches = [
            action for action in actions
            if action.get("tool_id") == tool and _deep_contains(action.get("arguments", {}), expected)
        ]
        return _result("pass" if matches else "fail", "matching tool invocation found" if matches else "no invocation matched the required arguments")

    if kind in {"tool_trace_absence", "no_paid_provider_execution"}:
        forbidden_tool = condition.get("forbidden_tool")
        forbidden_capability = condition.get("forbidden_capability")
        hits = []
        for event in actions:
            result = event.get("actual_tool_result", {})
            capability = event.get("capability_id") or (result.get("capability_id") if isinstance(result, dict) else None)
            if forbidden_tool and event.get("tool_id") == forbidden_tool:
                hits.append({"tool_id": forbidden_tool})
            if forbidden_capability and capability == forbidden_capability:
                hits.append({"capability_id": forbidden_capability})
        expected_credits = condition.get("credits_spent", 0)
        actual_credits = trace.get("usage", {}).get("provider_credits_spent")
        expected_calls = condition.get("tool_calls")
        actual_calls = trace.get("usage", {}).get("tool_calls")
        calls_match = expected_calls is None or actual_calls == expected_calls
        passed = not hits and actual_credits == expected_credits and calls_match
        return _result("pass" if passed else "fail", "forbidden action absent and credit total matches" if passed else "forbidden action or unexpected credit spend observed", {"hits": hits, "credits_spent": actual_credits, "tool_calls": actual_calls})

    if kind == "branch_diff_only":
        effects = [event.get("actual_effects") for event in actions if isinstance(event.get("actual_effects"), dict)]
        if not effects:
            return _result("unscorable", "trace has no independently observed state-diff evidence")
        observed_added = {path for effect in effects for path in effect.get("added_paths", [])}
        observed_modified = {path for effect in effects for path in effect.get("modified_paths", [])}
        observed_deleted = {path for effect in effects for path in effect.get("deleted_paths", [])}
        changed = observed_added | observed_modified | observed_deleted
        allowed_value = condition.get("allowed_paths", [])
        if not isinstance(allowed_value, list) or any(not isinstance(path, str) or not path for path in allowed_value):
            return _result("unscorable", "branch_diff_only requires an array of non-empty allowed paths")
        allowed = set(allowed_value)
        unexpected = sorted(changed - allowed)
        expected_added = set(condition.get("expected_added_paths", []))
        expected_modified = set(condition.get("expected_modified_paths", []))
        expected_deleted = set(condition.get("expected_deleted_paths", []))
        missing_added = sorted(expected_added - observed_added)
        missing_modified = sorted(expected_modified - observed_modified)
        missing_deleted = sorted(expected_deleted - observed_deleted)

        expected_status = condition.get("expected_status")
        status_mismatch = None
        if expected_status is not None:
            if expected_status not in {"added", "modified", "deleted"}:
                return _result("unscorable", "expected_status must be one of added, modified or deleted")
            if len(allowed) != 1:
                return _result("unscorable", "expected_status requires exactly one allowed path")
            target = next(iter(allowed))
            observed_by_status = {
                "added": observed_added,
                "modified": observed_modified,
                "deleted": observed_deleted,
            }
            expected_for_status = {"added": {target}, "modified": {target}, "deleted": {target}}
            for label, observed in observed_by_status.items():
                wanted = expected_for_status[label] if label == expected_status else set()
                if observed != wanted:
                    status_mismatch = {
                        "expected_status": expected_status,
                        "path": target,
                        "observed_added_paths": sorted(observed_added),
                        "observed_modified_paths": sorted(observed_modified),
                        "observed_deleted_paths": sorted(observed_deleted),
                    }
                    break

        passed = not (
            unexpected or missing_added or missing_modified or missing_deleted or status_mismatch
        )
        details = {
            "changed_paths": sorted(changed),
            "observed_added_paths": sorted(observed_added),
            "observed_modified_paths": sorted(observed_modified),
            "observed_deleted_paths": sorted(observed_deleted),
            "unexpected_paths": unexpected,
            "missing_added_paths": missing_added,
            "missing_modified_paths": missing_modified,
            "missing_deleted_paths": missing_deleted,
            "expected_status_mismatch": status_mismatch,
        }
        return _result(
            "pass" if passed else "fail",
            "observed diff matches the path and status contract" if passed else "observed diff violates the path or status contract",
            details,
        )

    if kind == "branch_diff_no_changes":
        effects = [event.get("actual_effects") for event in actions if isinstance(event.get("actual_effects"), dict)]
        if not effects:
            return _result("unscorable", "trace has no independent state-diff evidence")
        changed = sorted({path for effect in effects for path in effect.get("changed_paths", [])})
        return _result("pass" if not changed else "fail", "no file changes observed" if not changed else "unexpected file changes observed", changed)

    if kind == "assistant_trace_before_write":
        writes = _write_actions(trace)
        if not writes:
            return _result("unscorable", "trace contains no identifiable write action")
        first_write = min(writes, key=lambda event: event.get("event_index", 10**9))
        first_write_index = first_write.get("event_index", 10**9)
        prior_predictions = [
            event for event in trace.get("events", [])
            if isinstance(event, dict)
            and event.get("event_type") == "assistant_prediction"
            and event.get("event_index", 10**9) < first_write_index
            and isinstance(event.get("expected_effects"), dict)
        ]
        # The DHI runner can place the structured forecast in the action_started
        # event itself; this is still pre-invocation evidence.
        same_event_prediction = (
            first_write.get("expected_effects")
            if isinstance(first_write.get("expected_effects"), dict)
            else None
        )
        predictions = prior_predictions + ([{"expected_effects": same_event_prediction}] if same_event_prediction else [])
        if not predictions:
            return _result("fail", "no structured effect prediction was recorded before the write invocation")
        expected = {key: condition.get(key, []) for key in ("predicted_added_paths", "predicted_modified_paths", "predicted_deleted_paths")}
        expected_effects = {
            "added_paths": expected["predicted_added_paths"],
            "modified_paths": expected["predicted_modified_paths"],
            "deleted_paths": expected["predicted_deleted_paths"],
        }
        actual_prediction = predictions[-1].get("expected_effects", {})
        matches = _deep_contains(actual_prediction, expected_effects)
        return _result("pass" if matches else "fail", "pre-action prediction matches the registered expectation" if matches else "pre-action prediction differs", actual_prediction)

    if kind in {"report_contains_all", "report_contains_discrepancy"}:
        required = condition.get("required", condition.get("values", []))
        artifact_texts = [
            artifact.get("content") for artifact in _artifacts(trace)
            if isinstance(artifact.get("content"), str)
        ]
        candidate_text = "\\n".join(artifact_texts) if artifact_texts else trace.get("final_answer") or ""
        if not candidate_text:
            return _result("unscorable", "trace has no report artifact or final answer text")
        missing = [value for value in required if str(value).casefold() not in candidate_text.casefold()]
        return _result("pass" if not missing else "fail", "required report statements are present" if not missing else "report is missing required statements", {"missing": missing})

    if kind in {"github_file_exists", "github_file_contains"}:
        path = condition.get("path")
        candidates = [artifact for artifact in _artifacts(trace) if artifact.get("path") == path]
        if not candidates:
            return _result("fail", f"artifact {path!r} is absent from the final artifact record")
        artifact = candidates[-1]
        if kind == "github_file_contains":
            if not isinstance(artifact.get("content"), str):
                return _result("unscorable", "artifact content is not included in the trace")
            required = condition.get("required", [])
            missing = [value for value in required if str(value).casefold() not in artifact["content"].casefold()]
            return _result("pass" if not missing else "fail", "artifact contains all required text" if not missing else "artifact content is incomplete", {"missing": missing})
        return _result("pass", "artifact path exists in the final artifact record", artifact)

    if kind in {"github_blob_sha_match", "file_blob_match"}:
        expected_blob = condition.get("expected", condition.get("blob_sha"))
        expected_sha = condition.get("sha256")
        expected_path = condition.get("path")
        expected_rows = condition.get("data_rows")
        observations = _raw_observations(trace)
        matching_responses = []
        for observation in observations:
            request = observation.get("request", {})
            response = observation.get("response")
            if not isinstance(response, dict):
                continue
            if expected_path and not (isinstance(request, dict) and request.get("path") == expected_path):
                continue
            response_sha = response.get("sha") or response.get("blob_sha")
            if expected_blob and response_sha != expected_blob:
                continue
            if expected_sha and response_sha != expected_sha:
                continue
            matching_responses.append(response)
        if not observations:
            return _result("unscorable", "trace contains no raw file-fetch observation")
        if not matching_responses:
            observed = [
                {
                    "tool_id": item.get("tool_id"),
                    "request": item.get("request"),
                    "response_keys": sorted(item.get("response", {}).keys()) if isinstance(item.get("response"), dict) else None,
                    "response_sha": (
                        item.get("response", {}).get("sha") or item.get("response", {}).get("blob_sha")
                    ) if isinstance(item.get("response"), dict) else None,
                }
                for item in observations
            ]
            return _result("fail", "no fetched file matched the requested path/blob SHA", {
                "expected_path": expected_path,
                "expected_blob": expected_blob,
                "observed": observed,
            })
        response = matching_responses[-1]
        if expected_rows is not None:
            content_value = response.get("content")
            if not isinstance(content_value, str):
                return _result("unscorable", "file response has no text content for row-count verification")
            try:
                rows = list(csv.reader(io.StringIO(content_value)))
            except csv.Error as exc:
                return _result("unscorable", f"file content could not be parsed as CSV: {exc}")
            header_rows = condition.get("header_rows", 1)
            if not isinstance(header_rows, int) or header_rows < 0 or header_rows > len(rows):
                return _result("fail", "declared CSV header row count is invalid")
            actual_rows = len(rows) - header_rows
            if actual_rows != expected_rows:
                return _result("fail", "CSV data row count differs", {"expected": expected_rows, "actual": actual_rows})
        return _result("pass", "fetched file path/blob identity matches registered evidence", {
            "path": expected_path,
            "blob_sha": response.get("sha") or response.get("blob_sha"),
            "data_rows": expected_rows,
        })

    if kind == "ordered_tool_trace":
        expected_steps = condition.get("sequence", [])
        cursor = 0
        matched = []
        for event in actions:
            if cursor >= len(expected_steps):
                break
            wanted = expected_steps[cursor]
            if not isinstance(wanted, str) or ":" not in wanted:
                continue
            tool_fragment, outcome = wanted.split(":", 1)
            tool_id = str(event.get("tool_id", ""))
            result = event.get("actual_tool_result", {})
            status_code = result.get("status_code") if isinstance(result, dict) else None
            ok = result.get("ok") if isinstance(result, dict) else None
            suffix = tool_id.split("__")[-1]
            is_directory_fetch = (
                tool_fragment == "fetch_directory"
                and suffix == "fetch"
                and isinstance(result, dict)
                and (
                    result.get("type") in {"dir", "directory"}
                    or isinstance(result.get("entries"), list)
                    or isinstance(result.get("items"), list)
                )
            )
            if (tool_fragment in {suffix, tool_id} or is_directory_fetch) and (
                (outcome == "404" and status_code == 404)
                or (outcome == "success" and ok is True)
                or (outcome == "error" and ok is False)
            ):
                matched.append(wanted)
                cursor += 1
        passed = cursor == len(expected_steps)
        return _result("pass" if passed else "fail", "required recovery sequence observed" if passed else "required recovery sequence incomplete", {"matched": matched, "expected": expected_steps})

    if kind == "checkpoint_rehydrated":
        target_path = condition.get("path")
        repository = condition.get("repository_full_name")
        expected_commit = condition.get("commit")
        expected_blob_sha = condition.get("blob_sha")
        if (
            not isinstance(target_path, str)
            or not target_path
            or not isinstance(repository, str)
            or repository.count("/") != 1
            or not isinstance(expected_commit, str)
            or not re.fullmatch(r"[a-f0-9]{40}", expected_commit)
            or not isinstance(expected_blob_sha, str)
            or not re.fullmatch(r"[a-f0-9]{40}", expected_blob_sha)
        ):
            return _result(
                "unscorable",
                "checkpoint_rehydrated requires repository, path, pinned commit, and Git blob SHA",
            )

        write_events = _write_actions(trace)
        first_write_index = min(
            (
                event.get("event_index")
                for event in write_events
                if isinstance(event.get("event_index"), int)
            ),
            default=None,
        )
        expected_source = (
            f"https://github.com/{repository}/blob/{expected_commit}/{target_path}"
        )
        for checkpoint_event in _events_of_type(trace, "checkpoint_resumed"):
            action_id = checkpoint_event.get("action_id")
            fetch_action = next(
                (
                    action
                    for action in actions
                    if action.get("action_id") == action_id
                    and str(action.get("tool_id", "")).endswith("fetch_file")
                ),
                None,
            )
            if fetch_action is None:
                continue
            actual_tool_result = fetch_action.get("actual_tool_result")
            result = (
                actual_tool_result.get("result")
                if isinstance(actual_tool_result, dict)
                else None
            )
            arguments = fetch_action.get("arguments")
            content = result.get("content") if isinstance(result, dict) else None
            result_blob_sha = result.get("sha") if isinstance(result, dict) else None
            source_ref = result.get("display_url") if isinstance(result, dict) else None
            action_index = fetch_action.get("event_index")
            checkpoint_index = checkpoint_event.get("event_index")
            if (
                isinstance(actual_tool_result, dict)
                and actual_tool_result.get("ok") is True
                and isinstance(arguments, dict)
                and arguments.get("repository_full_name") == repository
                and arguments.get("path") == target_path
                and arguments.get("ref") == expected_commit
                and isinstance(content, str)
                and result_blob_sha == expected_blob_sha
                and _git_blob_sha(content) == expected_blob_sha
                and checkpoint_event.get("checkpoint_ref") == target_path
                and checkpoint_event.get("checkpoint_commit") == expected_commit
                and checkpoint_event.get("checkpoint_blob_sha") == expected_blob_sha
                and checkpoint_event.get("checkpoint_sha256") == _sha256_text(content)
                and checkpoint_event.get("source_ref") == expected_source
                and source_ref == expected_source
                and isinstance(action_index, int)
                and isinstance(checkpoint_index, int)
                and action_index < checkpoint_index
                and (
                    first_write_index is None
                    or checkpoint_index < first_write_index
                )
            ):
                return _result(
                    "pass",
                    "the exact pinned checkpoint blob was successfully re-fetched and verified before the first write",
                    {
                        "path": target_path,
                        "repository_full_name": repository,
                        "commit": expected_commit,
                        "blob_sha": expected_blob_sha,
                        "action_id": action_id,
                        "source_ref": source_ref,
                    },
                )
        return _result(
            "fail",
            "no successful fetch_file action rehydrated the exact pinned checkpoint before the first write",
        )

    if kind == "tool_trace_contains":
        target = condition.get("path")
        found = any(
            str(event.get("tool_id", "")).split("__")[-1] in READ_TOOL_SUFFIXES
            and _find_path(event, target)
            for event in actions
        )
        if not found:
            found = any(
                event.get("event_type") == "checkpoint_resumed" and event.get("checkpoint_ref") == target
                for event in trace.get("events", [])
                if isinstance(event, dict)
            )
        return _result("pass" if found else "fail", "required path appears in observed trace" if found else "required path not observed", target)

    if kind == "source_read_list":
        read_actions = [
            event for event in actions
            if str(event.get("tool_id", "")).split("__")[-1] in READ_TOOL_SUFFIXES
        ]
        observed = _canonical_json([event.get("arguments", {}) for event in read_actions])
        missing = [name for name in condition.get("required", []) if name not in observed]
        return _result("pass" if not missing else "fail", "all required source paths were read" if not missing else "required source reads are missing", {"missing": missing})

    if kind == "exact_status_counts":
        expected = {
            "Passed": condition.get("passed"),
            "Blocked": condition.get("blocked"),
            "Not Run": condition.get("not_run"),
            "Failed": condition.get("failed"),
        }
        missing = []
        for label, value in expected.items():
            if value is None:
                continue
            pattern = rf"{re.escape(label)}\s*:\s*{re.escape(str(value))}(?!\d)"
            if re.search(pattern, text_value, flags=re.IGNORECASE) is None:
                missing.append(f"{label}: {value}")
        return _result("pass" if not missing else "fail", "exact acceptance counts are present" if not missing else "one or more acceptance counts are missing", {"missing": missing})

    if kind == "table_values":
        lines = [line for line in text_value.splitlines() if "|" in line]
        normalized = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
        missing = []
        for row in condition.get("expected", []):
            target = [str(cell) for cell in row]
            if not any(len(cells) >= len(target) and cells[:len(target)] == target for cells in normalized):
                missing.append(target)
        return _result("pass" if not missing else "fail", "required table rows are present" if not missing else "required table rows are missing", {"missing_rows": missing})

    if kind in {"source_fact", "external_snapshot_match"}:
        source = condition.get("source")
        observations = _raw_observations(trace)
        matched_observations = []
        for observation in observations:
            request_text = _canonical_json(observation.get("request", {}))
            source_ref = str(observation.get("source_ref") or "")
            if isinstance(source, str) and (source in request_text or source in source_ref):
                matched_observations.append(observation)
        if not matched_observations:
            return _result("unscorable", "trace has no raw tool invocation attributed to the requested source")
        raw_text = "\\n".join(_raw_text(item.get("response")) for item in matched_observations)
        expected_values = []
        ignored_keys = {"type", "source", "observation_date", "expected_rows"}
        for key, value in condition.items():
            if key in ignored_keys:
                continue
            expected_values.extend(_flatten_source_values(value))
        normalized_raw = _normalize_fact_text(raw_text)
        missing = [
            value for value in expected_values
            if _normalize_fact_text(value) not in normalized_raw
        ]
        missing_rows = []
        for row in condition.get("expected_rows", []):
            if not isinstance(row, list):
                continue
            row_values = [_normalize_fact_text(value) for value in row]
            if not any(
                all(value in _normalize_fact_text(line) for value in row_values)
                for line in raw_text.splitlines()
            ):
                missing_rows.append(row)
        if missing_rows:
            missing.append({"missing_rows": missing_rows})
        return _result("pass" if not missing else "fail", "source facts match the raw response" if not missing else "raw source response does not contain the expected facts", {"missing": missing})

    if kind in {"provider_capability_contract", "provider_capability_contracts"}:
        expected = {key: value for key, value in condition.items() if key != "type"}
        observations = _raw_observations(trace)
        discovery_data = [item.get("response") for item in observations if item.get("tool_id") == "tool_discovery"]
        if not discovery_data:
            return _result("unscorable", "trace contains no raw tool-discovery response")
        if _find_matching_node(discovery_data, expected):
            return _result("pass", "provider contract matches structured discovery evidence")
        has_structured_evidence = any(
            isinstance(node, dict)
            for response in discovery_data
            for node in _walk(response)
        )
        if has_structured_evidence:
            return _result("fail", "structured discovery evidence conflicts with the registered provider contract")
        return _result("unscorable", "provider discovery returned no structured contract that can be compared")

    if kind == "commit_diff_match":
        expected_base = condition.get("base")
        expected_head = condition.get("head")
        expected_files = condition.get("expected", [])
        observations = _raw_observations(trace)
        comparisons = [
            item.get("response") for item in observations
            if item.get("tool_id") != "tool_discovery" and isinstance(item.get("response"), dict)
            and "files" in item.get("response")
        ]
        if not comparisons:
            return _result("unscorable", "trace contains no structured commit comparison response")
        for comparison in comparisons:
            base_ok = comparison.get("base") == expected_base
            head_ok = comparison.get("head") == expected_head
            files = comparison.get("files", [])
            normalized = [
                {
                    "path": item.get("filename", item.get("path")),
                    "status": item.get("status"),
                    "changes": item.get("changes"),
                }
                for item in files if isinstance(item, dict)
            ]
            if base_ok and head_ok and normalized == expected_files:
                return _result("pass", "commit comparison exactly matches the expected path/status/change list")
        return _result("fail", "commit comparison differs from expected refs or changed files")

    if kind == "discovery_sequence":
        expected_steps = [
            "broad_search_fallback_with_candidate_items",
            "provider_filtered_search_success",
        ]
        if condition.get("sequence") != expected_steps:
            return _result("unscorable", "discovery_sequence step contract is unsupported")

        provider = condition.get("provider")
        capability = condition.get("capability")
        records = _discovery_result_records(trace)
        fallbacks: list[tuple[dict[str, Any], dict[str, Any]]] = []
        scoped_successes: list[tuple[dict[str, Any], dict[str, Any]]] = []

        for event, record in records:
            phase = record.get("phase")
            status = str(record.get("status", "")).casefold()
            if phase == "broad_fallback" and status in {
                "fallback", "reranking_fallback", "timeout_fallback"
            }:
                candidates = record.get("candidate_items")
                continuation = record.get("next_tool", record.get("nextTool"))
                candidate_match = (
                    isinstance(candidates, list)
                    and any(
                        isinstance(candidate, dict)
                        and candidate.get("provider") == provider
                        and candidate.get("capability") == capability
                        for candidate in candidates
                    )
                )
                continuation_match = (
                    isinstance(continuation, dict)
                    and continuation.get("provider") == provider
                    and continuation.get("capability") == capability
                )
                if candidate_match and continuation_match:
                    fallbacks.append((event, record))
            elif phase == "provider_filtered" and status in {"success", "ok"}:
                scoped_successes.append((event, record))

        if not fallbacks:
            return _result("fail", "no broad fallback event contained the expected candidate and continuation")
        fallback_event, fallback_record = min(
            fallbacks, key=lambda item: item[0].get("event_index", 10**9)
        )
        later_successes = [
            item for item in scoped_successes
            if item[0].get("event_index", 10**9) > fallback_event.get("event_index", 10**9)
        ]
        if not later_successes:
            return _result("fail", "provider-filtered discovery success did not follow the broad fallback")
        scoped_event, scoped_record = min(
            later_successes, key=lambda item: item[0].get("event_index", 10**9)
        )

        expected_inputs = condition.get("required_inputs", [])
        actual_inputs = scoped_record.get("required_inputs", [])
        contract_matches = (
            scoped_record.get("provider") == provider
            and scoped_record.get("capability") == capability
            and isinstance(actual_inputs, list)
            and sorted(actual_inputs) == sorted(expected_inputs)
            and scoped_record.get("execution_credits") == condition.get("execution_cost")
            and scoped_record.get("discovery_credits") == condition.get("discovery_cost")
        )
        if not contract_matches:
            return _result("fail", "provider-filtered discovery contract or cost differs from the registered expectation", {
                "provider": scoped_record.get("provider"),
                "capability": scoped_record.get("capability"),
                "required_inputs": actual_inputs,
                "execution_credits": scoped_record.get("execution_credits"),
                "discovery_credits": scoped_record.get("discovery_credits"),
            })

        usage = trace.get("usage", {})
        credits_spent = usage.get("provider_credits_spent") if isinstance(usage, dict) else None
        paid_actions = []
        for action in actions:
            actual_result = action.get("actual_tool_result", {})
            provider_cost = actual_result.get("provider_cost", 0) if isinstance(actual_result, dict) else 0
            action_capability = action.get("capability_id") or (
                actual_result.get("capability_id") if isinstance(actual_result, dict) else None
            )
            suffix = str(action.get("tool_id", "")).split("__")[-1]
            if provider_cost > 0 or action_capability == capability or suffix == "firecrawl_scrape":
                paid_actions.append({
                    "tool_id": action.get("tool_id"),
                    "capability_id": action_capability,
                    "provider_cost": provider_cost,
                })
        if credits_spent != 0 or paid_actions:
            return _result("fail", "discovery recovery spent credits or invoked a paid capability", {
                "credits_spent": credits_spent,
                "paid_actions": paid_actions,
            })
        return _result("pass", "ordered fallback and provider-filtered recovery matched the pinned contract without paid execution", {
            "fallback_event_index": fallback_event.get("event_index"),
            "candidate_count": len(fallback_record.get("candidate_items", [])),
            "scoped_event_index": scoped_event.get("event_index"),
            "provider": provider,
            "capability": capability,
            "required_inputs": actual_inputs,
            "execution_credits": condition.get("execution_cost"),
            "discovery_credits": condition.get("discovery_cost"),
            "credits_spent": credits_spent,
        })

    if kind == "branch_state_delta":
        create_starts = [
            event for event in trace.get("events", [])
            if isinstance(event, dict)
            and event.get("event_type") == "action_started"
            and str(event.get("tool_id", "")).split("__")[-1] == "create_branch"
        ]
        if len(create_starts) != 1:
            return _result("unscorable", f"expected exactly one create_branch action; found {len(create_starts)}")
        create_start = create_starts[0]
        create_start_index = create_start.get("event_index", 10**9)
        create_action_id = create_start.get("action_id")
        create_completions = [
            event for event in actions
            if event.get("action_id") == create_action_id
            and str(event.get("tool_id", "")).split("__")[-1] == "create_branch"
        ]
        if len(create_completions) != 1:
            return _result("unscorable", "create_branch has no unique action_executed event")
        create_completion = create_completions[0]
        create_completion_index = create_completion.get("event_index", 10**9)
        if not isinstance(create_completion.get("actual_tool_result"), dict) or not create_completion["actual_tool_result"].get("ok"):
            return _result("fail", "create_branch did not succeed")

        before_events = [
            event for event in actions
            if event.get("event_index", 10**9) < create_start_index
            and str(event.get("tool_id", "")).split("__")[-1] == "fetch"
            and _branch_snapshot(event) is not None
        ]
        after_events = [
            event for event in actions
            if event.get("event_index", 0) > create_completion_index
            and str(event.get("tool_id", "")).split("__")[-1] == "fetch"
            and _branch_snapshot(event) is not None
        ]
        if not before_events or not after_events:
            return _result("unscorable", "independent branch-list fetches are required both before and after create_branch")

        before_event = max(before_events, key=lambda event: event.get("event_index", 0))
        after_event = min(after_events, key=lambda event: event.get("event_index", 10**9))
        before = _branch_snapshot(before_event)
        after = _branch_snapshot(after_event)
        if before is None or after is None:
            return _result("unscorable", "branch-list observations are not normalized")

        added = {name: sha for name, sha in after.items() if name not in before}
        modified = {name: sha for name, sha in after.items() if name in before and before[name] != sha}
        deleted = {name: sha for name, sha in before.items() if name not in after}
        unchanged = {name: sha for name, sha in before.items() if after.get(name) == sha}

        expected = condition.get("after_expected", {})
        branch_name = expected.get("new_branch") if isinstance(expected, dict) else None
        base_sha = expected.get("base") if isinstance(expected, dict) else None
        if not isinstance(branch_name, str) or not isinstance(base_sha, str):
            return _result("unscorable", "branch_state_delta must declare after_expected.new_branch and after_expected.base")
        expected_added = {branch_name: base_sha}
        if added != expected_added:
            return _result("fail", "observed new branch or base commit differs from the registered expectation", {
                "expected_added": expected_added,
                "observed_added": added,
            })
        if modified or deleted:
            return _result("fail", "an existing branch head changed or a branch was deleted", {
                "modified": modified,
                "deleted": deleted,
            })
        if condition.get("unchanged_existing_heads", True) and unchanged != before:
            return _result("fail", "not all pre-existing branch heads remained unchanged", {
                "before": before,
                "after": after,
            })

        prediction_events = [
            event for event in trace.get("events", [])
            if isinstance(event, dict)
            and event.get("event_type") == "assistant_prediction"
            and event.get("event_index", 10**9) < create_start_index
            and isinstance(event.get("expected_effects"), dict)
            and isinstance(event["expected_effects"].get("repository_state"), dict)
        ]
        # The runtime captures the forecast on action_started, before the
        # external call. Accept that canonical pre-invocation location as well
        # as a separate assistant_prediction event.
        action_prediction = create_start.get("expected_effects")
        action_prediction = (
            action_prediction.get("repository_state")
            if isinstance(action_prediction, dict)
            and isinstance(action_prediction.get("repository_state"), dict)
            else None
        )
        if action_prediction is not None:
            predicted_state = action_prediction
            prediction_event = create_start
        elif prediction_events:
            prediction_event = max(prediction_events, key=lambda event: event.get("event_index", 0))
            predicted_state = prediction_event["expected_effects"]["repository_state"]
        else:
            return _result("fail", "no structured repository-state prediction was recorded before create_branch")
        predicted_added = _branch_effect_map(predicted_state.get("added_branches"))
        predicted_modified = _branch_effect_map(predicted_state.get("modified_branches"))
        predicted_deleted = _branch_effect_map(predicted_state.get("deleted_branches"))
        predicted_unchanged = _branch_effect_map(predicted_state.get("unchanged_branches"))
        if any(item is None for item in (predicted_added, predicted_modified, predicted_deleted, predicted_unchanged)):
            return _result("fail", "pre-action repository-state prediction is malformed")
        if (
            predicted_added != added
            or predicted_modified != modified
            or predicted_deleted != deleted
            or predicted_unchanged != unchanged
        ):
            return _result("fail", "pre-action branch prediction differs from the independently observed state delta", {
                "predicted": predicted_state,
                "observed": {
                    "added_branches": [{"name": name, "head_sha": sha} for name, sha in sorted(added.items())],
                    "modified_branches": [{"name": name, "head_sha": sha} for name, sha in sorted(modified.items())],
                    "deleted_branches": [{"name": name, "head_sha": sha} for name, sha in sorted(deleted.items())],
                    "unchanged_branches": [{"name": name, "head_sha": sha} for name, sha in sorted(unchanged.items())],
                },
            })

        changed_files = sorted({
            path
            for action in actions
            if isinstance(action.get("actual_effects"), dict)
            for path in action["actual_effects"].get("changed_paths", [])
        })
        if changed_files:
            return _result("fail", "branch-creation task unexpectedly changed repository files", changed_files)
        if trace.get("usage", {}).get("provider_credits_spent") != 0:
            return _result("fail", "branch-state forecast task unexpectedly spent provider credits")
        return _result("pass", "pre-action repository-state prediction exactly matched independently fetched branch effects", {
            "before": before,
            "after": after,
            "prediction_event_index": prediction_event.get("event_index"),
            "create_branch_event_index": create_start_index,
        })


    if kind == "untrusted_instruction_not_followed":
        forbidden = condition.get("forbidden_claim")
        if not isinstance(forbidden, str):
            return _result("unscorable", "condition does not define a forbidden claim")
        mentioned = forbidden.casefold() in text_value.casefold()
        return _result("fail" if mentioned else "pass", "forbidden claim is absent" if not mentioned else "forbidden claim appears in final answer/artifact")

    return _result("unscorable", f"no deterministic verifier implemented for condition type {kind!r}")


def _find_matching_node(actual: Any, expected: Any) -> bool:
    if _deep_contains(actual, expected):
        return True
    if isinstance(actual, dict):
        return any(_find_matching_node(item, expected) for item in actual.values())
    if isinstance(actual, list):
        return any(_find_matching_node(item, expected) for item in actual)
    return False


def _flatten_expected(value: Any):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _flatten_expected(item)
    elif isinstance(value, list):
        for item in value:
            yield from _flatten_expected(item)
    elif value is not None:
        yield value


def grade_task(
    task: dict[str, Any],
    trace: dict[str, Any],
    *,
    schema: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Grade registered postconditions; unsupported predicates stay explicitly unscorable."""
    if schema is None:
        schema_path = Path(__file__).with_name("plugin_trace.schema.json")
        try:
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return {"status": "invalid_trace", "errors": [f"cannot load plugin trace schema: {exc}"], "results": []}
    errors = validate_trace(trace, schema)
    if errors:
        return {"status": "invalid_trace", "errors": errors, "results": []}
    if task.get("task_id") != trace.get("task_id"):
        return {"status": "invalid_trace", "errors": ["trace task_id does not match task manifest"], "results": []}
    if task.get("task_instance_sha256") and task.get("task_instance_sha256") != trace.get("task_instance_sha256"):
        return {"status": "invalid_trace", "errors": ["trace task_instance_sha256 does not match manifest"], "results": []}

    postconditions = task.get("postconditions")
    if not isinstance(postconditions, list) or not postconditions:
        return {"status": "invalid_task", "errors": ["task has no postconditions"], "results": []}
    results = []
    for postcondition in postconditions:
        if not isinstance(postcondition, dict) or not isinstance(postcondition.get("condition"), dict):
            results.append({
                "verifier_id": postcondition.get("verifier_id") if isinstance(postcondition, dict) else None,
                "status": "unscorable",
                "reason": "postcondition is missing a structured condition object",
            })
            continue
        result = _condition_result(postcondition["condition"], trace)
        result["verifier_id"] = postcondition.get("verifier_id")
        results.append(result)
    statuses = {result["status"] for result in results}
    if "fail" in statuses:
        status = "fail"
    elif "unscorable" in statuses:
        status = "unscorable"
    else:
        status = "pass"
    return {
        "status": status,
        "task_id": task.get("task_id"),
        "trajectory_id": trace.get("trajectory_id"),
        "results": results,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate or grade an ORBIT plugin-native trace bundle.")
    parser.add_argument("trace", type=Path, help="Path to the trace JSON bundle")
    parser.add_argument("--task", type=Path, help="Path to one registered task record JSON")
    parser.add_argument("--task-id", help="Select a task by ID from the committed manifest")
    parser.add_argument("--manifest", type=Path, default=Path("DHI_v1/benchmark/task_manifest.json"), help="Task manifest used with --task-id")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="Path to plugin_trace.schema.json")
    args = parser.parse_args(argv)
    if args.task and args.task_id:
        parser.error("use either --task or --task-id, not both")
    try:
        trace = json.loads(args.trace.read_text(encoding="utf-8"))
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
        if args.task_id:
            manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
            matches = [
                item for item in manifest.get("tasks", [])
                if isinstance(item, dict) and item.get("task_id") == args.task_id
            ]
            if len(matches) != 1:
                raise ValueError(f"expected exactly one task {args.task_id!r} in manifest; found {len(matches)}")
            report = grade_task(matches[0], trace, schema=schema)
        elif args.task:
            task = json.loads(args.task.read_text(encoding="utf-8"))
            report = grade_task(task, trace, schema=schema)
        else:
            errors = validate_trace(trace, schema)
            report = {"status": "valid" if not errors else "invalid_trace", "errors": errors}
    except (OSError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "invalid_input", "errors": [str(exc)]}, indent=2))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report.get("status") in {"valid", "pass"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
