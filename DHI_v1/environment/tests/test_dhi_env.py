import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from DHI_v1.environment.dhi_env import DHIEnvironment, TaskSpec


def make_task(**overrides):
    values = {
        "task_id": "task-readme-update",
        "prompt": "Add an installation heading to the README.",
        "goal": "README contains an Installation heading.",
        "hard_constraints": ["Do not modify pyproject.toml"],
        "postconditions": [
            {"type": "contains", "path": "README.md", "text": "## Installation"}
        ],
    }
    values.update(overrides)
    return TaskSpec(**values)


def test_write_action_produces_replayable_trace_and_verified_closure(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "README.md").write_text("# Demo\n", encoding="utf-8")
    trace = tmp_path / "trace.jsonl"
    env = DHIEnvironment(workspace, trace_path=trace)
    env.begin_task(make_task())

    result = env.run_action({
        "tool_id": "fs.append_file",
        "arguments": {"path": "README.md", "content": "\n## Installation\n"},
        "expected_effects": {
            "changed_paths": ["README.md"],
            "unchanged_paths": [],
        },
    })
    closure = env.close_task()

    assert result.ok is True
    assert result.actual_effects["modified_paths"] == ["README.md"]
    assert result.prediction_comparison["status"] == "matched"
    assert closure["success"] is True
    assert closure["failed_postconditions"] == []

    events = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines()]
    assert [event["event_type"] for event in events] == [
        "task_started", "action_started", "action_executed", "task_closed"
    ]
    assert events[2]["actual_tool_result"]["ok"] is True
    assert events[1]["step_id"] == events[2]["step_id"]
    assert {event["trajectory_id"] for event in events} == {"task-readme-update"}


def test_catalogue_discovers_capability_not_in_visible_tool_list(tmp_path):
    env = DHIEnvironment(
        tmp_path,
        visible_tool_ids={"fs.read_file", "fs.list_files"},
    )
    env.begin_task(make_task(visible_tool_ids=["fs.read_file", "fs.list_files"]))

    discovered = env.discover_tools("search text within files")

    assert any(tool["tool_id"] == "fs.search_text" for tool in discovered)
    assert "fs.search_text" in {tool["tool_id"] for tool in env.list_tools(visible_only=True)}
    assert "fs.search_text" in {tool["tool_id"] for tool in env.list_tools(visible_only=False)}
    assert env.events[-1]["event_type"] == "tool_discovery"


def test_catalogue_search_is_a_first_class_tool_available_even_when_not_in_task_list(tmp_path):
    env = DHIEnvironment(tmp_path, visible_tool_ids={"fs.read_file", "fs.list_files"})
    env.begin_task(make_task(visible_tool_ids=["fs.read_file", "fs.list_files"]))

    result = env.run_action({
        "tool_id": "catalog.search",
        "arguments": {"query": "search text within files"},
    })

    assert result.ok is True
    assert any(item["tool_id"] == "fs.search_text" for item in result.result["tools"])
    assert "catalog.search" in {item["tool_id"] for item in env.list_tools(visible_only=True)}
    assert result.event["actual_tool_result"]["ok"] is True


def test_path_traversal_is_rejected_without_modifying_outside_workspace(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "outside.txt"
    outside.write_text("safe", encoding="utf-8")
    env = DHIEnvironment(workspace)
    env.begin_task(make_task())

    result = env.run_action({
        "tool_id": "fs.write_file",
        "arguments": {"path": "../outside.txt", "content": "compromised"},
    })

    assert result.ok is False
    assert "workspace" in result.error.lower() or "path" in result.error.lower()
    assert outside.read_text(encoding="utf-8") == "safe"


def test_tool_outside_task_allowlist_is_rejected(tmp_path):
    env = DHIEnvironment(tmp_path)
    env.begin_task(make_task(allowed_tool_ids=["fs.read_file"]))

    result = env.run_action({
        "tool_id": "fs.write_file",
        "arguments": {"path": "README.md", "content": "hello"},
    })

    assert result.ok is False
    assert "not allowed" in result.error.lower()
    assert not (tmp_path / "README.md").exists()


def test_task_does_not_close_when_a_required_postcondition_is_missing(tmp_path):
    env = DHIEnvironment(tmp_path)
    env.begin_task(make_task())

    closure = env.close_task()

    assert closure["success"] is False
    assert len(closure["failed_postconditions"]) == 1
    assert closure["verified_postconditions"][0]["passed"] is False


def test_search_returns_real_line_matches(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("def run():\n    return 42\n", encoding="utf-8")
    env = DHIEnvironment(tmp_path, visible_tool_ids={"fs.search_text"})
    env.begin_task(make_task(visible_tool_ids=["fs.search_text"]))

    result = env.run_action({
        "tool_id": "fs.search_text",
        "arguments": {"query": "return 42", "path": "src"},
    })

    assert result.ok is True
    assert result.result["matches"] == [
        {"path": "src/main.py", "line": 2, "text": "    return 42"}
    ]


def test_second_task_cannot_start_before_current_task_closes(tmp_path):
    env = DHIEnvironment(tmp_path)
    env.begin_task(make_task())

    with pytest.raises(RuntimeError, match="already active"):
        env.begin_task(make_task(task_id="task-2"))

    env.close_task()
    env.begin_task(make_task(task_id="task-2"))
    assert env.active_task_id == "task-2"


def test_task_requires_at_least_one_explicit_postcondition():
    with pytest.raises(ValueError, match="postcondition"):
        make_task(postconditions=[])


def test_prediction_detects_unexpected_change_to_protected_file(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "README.md").write_text("# Demo\n", encoding="utf-8")
    env = DHIEnvironment(workspace)
    env.begin_task(make_task())

    result = env.run_action({
        "tool_id": "fs.append_file",
        "arguments": {"path": "README.md", "content": "\n## Installation\n"},
        "expected_effects": {
            "changed_paths": [],
            "unchanged_paths": ["README.md"],
        },
    })

    assert result.ok is True
    assert result.prediction_comparison["status"] == "mismatched"
    assert result.prediction_comparison["unchanged_path_violations"] == ["README.md"]


def test_tool_schema_rejects_unknown_arguments(tmp_path):
    env = DHIEnvironment(tmp_path)
    env.begin_task(make_task())

    result = env.run_action({
        "tool_id": "fs.read_file",
        "arguments": {"path": "README.md", "shell": "rm -rf /"},
    })

    assert result.ok is False
    assert "unexpected argument" in result.error.lower()


def test_closure_fails_if_a_protected_path_changes(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "README.md").write_text("# Demo\n", encoding="utf-8")
    (workspace / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
    env = DHIEnvironment(workspace)
    task = make_task(protected_paths=["pyproject.toml"])
    env.begin_task(task)

    result = env.run_action({
        "tool_id": "fs.write_file",
        "arguments": {"path": "pyproject.toml", "content": "tampered"},
    })
    closure = env.close_task()

    assert result.ok is True
    assert closure["success"] is False
    assert closure["failed_protected_paths"][0]["path"] == "pyproject.toml"


def test_snapshot_ignores_git_and_vendor_directories(tmp_path):
    workspace = tmp_path / "workspace"
    (workspace / ".git" / "objects").mkdir(parents=True)
    (workspace / "node_modules" / "package").mkdir(parents=True)
    (workspace / "src").mkdir()
    (workspace / ".git" / "objects" / "large.bin").write_bytes(b"x" * 100)
    (workspace / "node_modules" / "package" / "index.js").write_text("vendor", encoding="utf-8")
    (workspace / "src" / "main.py").write_text("print('ok')", encoding="utf-8")
    env = DHIEnvironment(workspace)

    snapshot = env.snapshot()

    assert list(snapshot) == ["src/main.py"]


def test_symlink_inside_workspace_cannot_escape_boundary(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    outside = tmp_path / "secret.txt"
    outside.write_text("private", encoding="utf-8")
    (workspace / "leak.txt").symlink_to(outside)
    env = DHIEnvironment(workspace)
    env.begin_task(make_task())

    result = env.run_action({"tool_id": "fs.read_file", "arguments": {"path": "leak.txt"}})

    assert result.ok is False
    assert "symlink" in result.error.lower()


def test_generated_trace_events_validate_against_checked_in_schema(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "README.md").write_text("# Demo\n", encoding="utf-8")
    trace_path = tmp_path / "trace.jsonl"
    env = DHIEnvironment(workspace, trace_path=trace_path)
    env.begin_task(make_task())
    result = env.run_action({
        "tool_id": "fs.append_file",
        "arguments": {"path": "README.md", "content": "\n## Installation\n"},
        "expected_effects": {"changed_paths": ["README.md"], "unchanged_paths": []},
    })
    assert result.ok is True
    assert env.close_task()["success"] is True

    schema_path = Path(__file__).parents[1] / "schemas" / "trajectory-event.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    events = [json.loads(line) for line in trace_path.read_text(encoding="utf-8").splitlines()]
    assert len(events) == 4
    errors = [error for event in events for error in validator.iter_errors(event)]
    assert errors == []


def test_missing_protected_path_is_rejected_before_task_starts(tmp_path):
    env = DHIEnvironment(tmp_path)
    task = make_task(protected_paths=["missing.txt"])

    with pytest.raises(ValueError, match="protected path must already exist"):
        env.begin_task(task)

    assert env.active_task_id is None


def test_existing_trace_file_is_not_silently_appended(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    trace = tmp_path / "existing.jsonl"
    trace.write_text("previous trajectory\\n", encoding="utf-8")

    with pytest.raises(FileExistsError, match="trace file already exists"):
        DHIEnvironment(workspace, trace_path=trace)

    assert trace.read_text(encoding="utf-8") == "previous trajectory\\n"


def test_discovery_promotes_hidden_tool_into_visible_callable_inventory(tmp_path):
    env = DHIEnvironment(tmp_path, visible_tool_ids={"fs.read_file", "fs.list_files"})
    env.begin_task(make_task(visible_tool_ids=["fs.read_file", "fs.list_files"]))

    before = {tool["tool_id"] for tool in env.list_tools(visible_only=True)}
    env.discover_tools("search text within files")
    after = {tool["tool_id"] for tool in env.list_tools(visible_only=True)}

    assert "fs.search_text" not in before
    assert "fs.search_text" in after


def test_hidden_tool_cannot_be_called_before_discovery(tmp_path):
    (tmp_path / "README.md").write_text("marker", encoding="utf-8")
    env = DHIEnvironment(tmp_path, visible_tool_ids={"fs.read_file", "fs.list_files"})
    env.begin_task(make_task(visible_tool_ids=["fs.read_file", "fs.list_files"]))

    result = env.run_action({"tool_id": "fs.search_text", "arguments": {"query": "marker"}})

    assert result.ok is False
    assert "discover it first" in result.error.lower()


def test_deterministic_fault_injection_fails_once_then_tool_can_recover(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "main.py").write_text("def run():\n    return 7\n", encoding="utf-8")
    env = DHIEnvironment(tmp_path, visible_tool_ids={"fs.search_text"})
    task = make_task(visible_tool_ids=["fs.search_text"], fault_injections=[{
        "tool_id": "fs.search_text",
        "attempt": 1,
        "error": "temporary search index outage",
    }])
    env.begin_task(task)

    first = env.run_action({"tool_id": "fs.search_text", "arguments": {"query": "return 7"}})
    second = env.run_action({"tool_id": "fs.search_text", "arguments": {"query": "return 7"}})
    closure = env.close_task()

    assert first.ok is False
    assert "temporary search index outage" in first.error
    assert first.event["fault_injection"]["attempt"] == 1
    assert second.ok is True
    assert second.result["count"] == 1
    assert closure["success"] is False


def test_fault_injection_rejects_unknown_tool_ids_at_task_start(tmp_path):
    env = DHIEnvironment(tmp_path)
    task = make_task(fault_injections=[{
        "tool_id": "unknown.tool",
        "attempt": 1,
        "error": "temporary failure",
    }])

    with pytest.raises(ValueError, match="fault injection references unknown tool"):
        env.begin_task(task)

    assert env.active_task_id is None
