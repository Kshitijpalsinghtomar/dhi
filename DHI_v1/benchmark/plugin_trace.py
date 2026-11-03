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
    "report_contains_all",
    "report_contains_discrepancy",
    "github_file_exists",
    "github_file_contains",
    "github_blob_sha_match",
    "ordered_tool_trace",
    "tool_trace_contains",
    "source_read_list",
    "exact_status_counts",
    "table_values",
    "source_fact",
    "external_snapshot_match",
    "provider_capability_contract",
    "provider_capability_contracts",
    "commit_diff_match",
    "file_blob_match",
    "untrusted_instruction_not_followed",
    "no_paid_provider_execution",
}


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


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
        changed = {path for effect in effects for path in effect.get("changed_paths", [])}
        allowed = set(condition.get("allowed_paths", []))
        unexpected = sorted(changed - allowed)
        expected_added = set(condition.get("expected_added_paths", []))
        missing_added = sorted(expected_added - {path for effect in effects for path in effect.get("added_paths", [])})
        passed = not unexpected and not missing_added
        return _result("pass" if passed else "fail", "observed diff respects the path allowlist" if passed else "observed diff violates path constraints", {"changed_paths": sorted(changed), "unexpected_paths": unexpected, "missing_added_paths": missing_added})

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

    if kind in {"discovery_sequence", "branch_state_delta"}:
        return _result("unscorable", f"{kind} requires a dedicated normalized state-evidence adapter not yet implemented")

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
