from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import replace
from pathlib import Path

from DHI_v1.benchmark.plugin_execution import prepare_plugin_execution
from DHI_v1.benchmark.plugin_runner import run_plugin_task
from DHI_v1.benchmark.plugin_task_loader import load_plugin_task
from DHI_v1.benchmark.plugin_trace import validate_trace


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"
REGISTRY = ROOT / "DHI_v1" / "benchmark" / "fixtures" / "plugin_ecology" / "plugin_tool_registry.json"
SCHEMA = json.loads((ROOT / "DHI_v1" / "benchmark" / "plugin_trace.schema.json").read_text(encoding="utf-8"))

FETCH_FILE = "mcp__GitHub__fetch_file"
CREATE_FILE = "mcp__GitHub__create_file"
COMPARE = "mcp__GitHub__compare_commits"
BASE_BRANCH = "orbit/sandbox/orbit-a-s06-001"

REPORT = """# Release readiness

Release: Northstar Workbench 1.4
Workload: 8 not Done; 35 estimated hours; 4 Open; 19 hours.
Dependencies: The blocked chain is recorded for owner review.
Acceptance: Passed: 3; Blocked: 1; Not Run: 1; Failed: 1. AT-03 and AT-06 require attention.
Recommendation: Hold until the acceptance conflicts are resolved.
"""


class DirectAnswerClient:
    def __init__(self, answer: str = "Finished.") -> None:
        self.calls = 0
        self.answer = answer

    def complete(self, *, messages, tools, temperature=0.0):
        self.calls += 1
        return {"choices": [{"message": {"role": "assistant", "content": self.answer}}]}


class CreateThenAnswerClient:
    def __init__(self, tool_name: str, arguments: dict) -> None:
        self.tool_name = tool_name
        self.arguments = arguments
        self.calls = 0

    def complete(self, *, messages, tools, temperature=0.0):
        self.calls += 1
        if self.calls == 1:
            return {"choices": [{"message": {
                "role": "assistant",
                "tool_calls": [{
                    "id": "create-report",
                    "type": "function",
                    "function": {"name": self.tool_name, "arguments": json.dumps(self.arguments)},
                }],
            }}]}
        return {"choices": [{"message": {"role": "assistant", "content": "Report created and checked."}}]}


def _task_and_plan():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    task_record = copy.deepcopy(next(t for t in manifest["tasks"] if t["task_id"] == "ORBIT-A-S06-001"))
    # Tests use an in-memory authorization copy. The committed manifest remains disabled.
    task_record["execution"]["model_runs_allowed"] = True
    plan = replace(
        load_plugin_task(MANIFEST, REGISTRY, "ORBIT-A-S06-001"),
        model_runs_allowed=True,
    )
    return task_record, plan


def _git_blob_sha(content: str) -> str:
    data = content.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _prepared(plan, state: dict[str, str]):
    schemas = {
        FETCH_FILE: {
            "type": "object",
            "properties": {
                "repository_full_name": {"type": "string"},
                "path": {"type": "string"},
                "ref": {"type": "string"},
            },
            "required": ["repository_full_name", "path"],
            "additionalProperties": False,
        },
        CREATE_FILE: {
            "type": "object",
            "properties": {
                "repository_full_name": {"type": "string"},
                "path": {"type": "string"},
                "content": {"type": "string"},
                "message": {"type": "string"},
                "branch": {"type": "string"},
            },
            "required": ["repository_full_name", "path", "content", "message"],
            "additionalProperties": False,
        },
        COMPARE: {
            "type": "object",
            "properties": {
                "repository_full_name": {"type": "string"},
                "base": {"type": "string"},
                "head": {"type": "string"},
            },
            "required": ["repository_full_name", "base", "head"],
            "additionalProperties": False,
        },
    }
    handlers = {
        FETCH_FILE: lambda args: {
            "content": REPORT,
            "sha": _git_blob_sha(REPORT),
            "display_url": f"https://github.com/{args['repository_full_name']}/blob/{args.get('ref', 'HEAD')}/{args['path']}",
        },
        CREATE_FILE: lambda args: (
            state.__setitem__(args["path"], hashlib.sha256(args["content"].encode("utf-8")).hexdigest())
            or {"commit_sha": "c" * 40}
        ),
        COMPARE: lambda args: {"files": []},
    }
    visible = set(plan.visible_tool_ids)
    handlers = {key: value for key, value in handlers.items() if key in visible}
    guards = {
        CREATE_FILE: lambda task, args: (
            task.task_id == "ORBIT-A-S06-001"
            and args.get("repository_full_name") == "Kshitijpalsinghtomar/dhi"
            and args.get("path") == "DHI_v1/benchmark/fixtures/plugin_ecology/reports/release-readiness.md"
            and args.get("branch") == BASE_BRANCH
        )
    }
    return prepare_plugin_execution(plan, schemas=schemas, handlers=handlers, write_guards=guards)


def test_manifest_branch_head_precondition_blocks_model_before_first_completion():
    task_record, plan = _task_and_plan()
    state = {"README.md": "a" * 64}
    prepared = _prepared(plan, state)
    client = DirectAnswerClient()

    result = run_plugin_task(
        task_record,
        prepared,
        client,
        observe_state=lambda: dict(state),
        precondition_observer=lambda task, item: {
            "branch_name": BASE_BRANCH,
            "head_sha": "0" * 40,
        },
    )

    assert client.calls == 0
    assert result.stopped_reason == "precondition_blocked"
    assert result.trace["closure"]["status"] == "blocked"
    checked = [e for e in result.trace["events"] if e["event_type"] == "precondition_checked"]
    assert len(checked) == 1
    assert checked[0]["precondition_status"] == "fail"
    assert checked[0]["precondition_observation"]["branch_name"] == BASE_BRANCH
    assert result.trace_validation_errors == []


def test_successful_write_is_only_a_final_artifact_after_independent_readback():
    task_record, plan = _task_and_plan()
    path = "DHI_v1/benchmark/fixtures/plugin_ecology/reports/release-readiness.md"
    state = {"README.md": "a" * 64}
    prepared = _prepared(plan, state)
    client = CreateThenAnswerClient(
        prepared.tool_name_by_id[CREATE_FILE],
        {
            "repository_full_name": "Kshitijpalsinghtomar/dhi",
            "path": path,
            "content": REPORT,
            "message": "create fixture report",
            "branch": BASE_BRANCH,
            "__dhi_expected_effects": {
                "added_paths": [path],
                "modified_paths": [],
                "deleted_paths": [],
                "changed_paths": [path],
            },
        },
    )
    readbacks = []

    def read_artifact(repository_full_name, artifact_path, ref):
        readbacks.append((repository_full_name, artifact_path, ref))
        return {
            "content": REPORT,
            "sha": _git_blob_sha(REPORT),
            "display_url": f"https://github.com/{repository_full_name}/blob/{ref}/{artifact_path}",
        }

    result = run_plugin_task(
        task_record,
        prepared,
        client,
        observe_state=lambda: dict(state),
        precondition_observer=lambda task, item: {
            "branch_name": BASE_BRANCH,
            "head_sha": item["condition"]["commit"],
        },
        artifact_reader=read_artifact,
    )

    assert result.grade["status"] == "pass", result.grade
    assert readbacks == [("Kshitijpalsinghtomar/dhi", path, BASE_BRANCH)]
    assert len(result.trace["final_artifacts"]) == 1
    artifact = result.trace["final_artifacts"][0]
    assert artifact["path"] == path
    assert artifact["content"] == REPORT
    assert artifact["blob_sha"] == _git_blob_sha(REPORT)
    source_event = next(e for e in result.trace["events"] if e["event_index"] == artifact["source_event_index"])
    assert source_event["event_type"] == "artifact_readback"
    assert source_event["artifact_readback"]["status"] == "verified"
    assert result.trace_validation_errors == []
    assert validate_trace(result.trace, SCHEMA) == []



class FetchThenAnswerClient:
    def __init__(self, tool_name: str, arguments: dict) -> None:
        self.tool_name = tool_name
        self.arguments = arguments
        self.calls = 0

    def complete(self, *, messages, tools, temperature=0.0):
        self.calls += 1
        if self.calls == 1:
            return {"choices": [{"message": {
                "role": "assistant",
                "tool_calls": [{
                    "id": "resume-checkpoint",
                    "type": "function",
                    "function": {"name": self.tool_name, "arguments": json.dumps(self.arguments)},
                }],
            }}]}
        return {"choices": [{"message": {"role": "assistant", "content": "Checkpoint rehydrated."}}]}


def _with_file_blob_precondition(plan, path: str, content: str, commit: str):
    condition = {
        "type": "github_file_blob",
        "path": path,
        "commit": commit,
        "blob_sha": _git_blob_sha(content),
    }
    preconditions = ({"precondition_id": "resume_checkpoint_exists", "condition": condition},)
    return replace(plan, preconditions=preconditions), condition


def test_github_file_blob_precondition_passes_only_for_exact_pinned_blob():
    task_record, plan = _task_and_plan()
    checkpoint_path = "DHI_v1/benchmark/fixtures/plugin_ecology/checkpoints/resume-task-A.md"
    commit = "a" * 40
    plan, condition = _with_file_blob_precondition(plan, checkpoint_path, REPORT, commit)
    prepared = _prepared(plan, {"README.md": "a" * 64})
    client = DirectAnswerClient()

    result = run_plugin_task(
        task_record,
        prepared,
        client,
        observe_state=lambda: {"README.md": "a" * 64},
        precondition_observer=lambda task, item: {
            "path": condition["path"],
            "commit": condition["commit"],
            "blob_sha": condition["blob_sha"],
        },
    )

    assert client.calls == 1
    checked = next(event for event in result.trace["events"] if event["event_type"] == "precondition_checked")
    assert checked["precondition_status"] == "pass"
    assert checked["precondition_observation"]["path"] == checkpoint_path
    assert result.trace_validation_errors == []


def test_github_file_blob_precondition_mismatch_blocks_before_model_call():
    task_record, plan = _task_and_plan()
    checkpoint_path = "DHI_v1/benchmark/fixtures/plugin_ecology/checkpoints/resume-task-A.md"
    commit = "a" * 40
    plan, condition = _with_file_blob_precondition(plan, checkpoint_path, REPORT, commit)
    prepared = _prepared(plan, {"README.md": "a" * 64})
    client = DirectAnswerClient()

    result = run_plugin_task(
        task_record,
        prepared,
        client,
        observe_state=lambda: {"README.md": "a" * 64},
        precondition_observer=lambda task, item: {
            "path": condition["path"],
            "commit": condition["commit"],
            "blob_sha": "0" * 40,
        },
    )

    assert client.calls == 0
    assert result.stopped_reason == "precondition_blocked"
    checked = next(event for event in result.trace["events"] if event["event_type"] == "precondition_checked")
    assert checked["precondition_status"] == "fail"
    assert "blob" in checked["precondition_reason"].lower()
    assert result.trace_validation_errors == []


def test_runner_records_checkpoint_resumed_only_after_verified_pinned_file_read():
    task_record, plan = _task_and_plan()
    checkpoint_path = "DHI_v1/benchmark/fixtures/plugin_ecology/checkpoints/resume-task-A.md"
    commit = "a" * 40
    plan, condition = _with_file_blob_precondition(plan, checkpoint_path, REPORT, commit)
    state = {"README.md": "a" * 64}
    prepared = _prepared(plan, state)
    client = FetchThenAnswerClient(
        prepared.tool_name_by_id[FETCH_FILE],
        {
            "repository_full_name": "Kshitijpalsinghtomar/dhi",
            "path": checkpoint_path,
            "ref": commit,
        },
    )

    result = run_plugin_task(
        task_record,
        prepared,
        client,
        observe_state=lambda: dict(state),
        precondition_observer=lambda task, item: {
            "path": condition["path"],
            "commit": condition["commit"],
            "blob_sha": condition["blob_sha"],
        },
    )

    resumed = [event for event in result.trace["events"] if event["event_type"] == "checkpoint_resumed"]
    assert len(resumed) == 1
    assert resumed[0]["checkpoint_ref"] == checkpoint_path
    assert resumed[0]["checkpoint_sha256"] == hashlib.sha256(REPORT.encode("utf-8")).hexdigest()
    assert resumed[0]["source_ref"].startswith("https://github.com/")
    assert result.trace_validation_errors == []
    assert validate_trace(result.trace, SCHEMA) == []
