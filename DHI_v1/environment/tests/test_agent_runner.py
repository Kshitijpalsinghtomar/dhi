from DHI_v1.environment.dhi_env import DHIEnvironment, TaskSpec
from DHI_v1.environment.agent_runner import run_agent_task


class FakeToolCallingClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.tool_sets = []

    def complete(self, *, messages, tools, temperature=0.0):
        self.tool_sets.append({tool["function"]["name"] for tool in tools})
        return self.responses.pop(0)


def tool_call(call_id, name, arguments):
    import json
    return {
        "choices": [{
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": call_id,
                    "type": "function",
                    "function": {"name": name, "arguments": json.dumps(arguments)},
                }],
            },
            "finish_reason": "tool_calls",
        }]
    }


def final_answer(text):
    return {"choices": [{"message": {"role": "assistant", "content": text}, "finish_reason": "stop"}]}


def make_task():
    return TaskSpec(
        task_id="agent-runner-hidden-search",
        prompt="Find the healthcheck function and report the file path.",
        goal="Identify the healthcheck function in the source file.",
        visible_tool_ids=["fs.list_files", "fs.read_file"],
        postconditions=[{"type": "contains", "path": "src/api.py", "text": "def healthcheck"}],
    )


def test_runner_refreshes_tool_schemas_after_successful_discovery(tmp_path):
    workspace = tmp_path / "workspace"
    (workspace / "src").mkdir(parents=True)
    (workspace / "src" / "api.py").write_text("def healthcheck():\n    return True\n", encoding="utf-8")
    env = DHIEnvironment(workspace)
    client = FakeToolCallingClient([
        tool_call("c1", "catalog_search", {"query": "search source text", "limit": 5}),
        tool_call("c2", "fs_search_text", {"query": "def healthcheck", "path": "src"}),
        final_answer("The function is in src/api.py.")
    ])

    result = run_agent_task(env, make_task(), client, max_model_turns=5)

    assert result.final_answer == "The function is in src/api.py."
    assert result.closure["success"] is True
    assert result.tool_call_count == 2
    assert "fs_search_text" not in client.tool_sets[0]
    assert "fs_search_text" in client.tool_sets[1]
    assert any(event["event_type"] == "tool_discovery" for event in env.events)


def test_runner_can_recover_when_model_first_calls_hidden_tool(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "README.md").write_text("the marker is here", encoding="utf-8")
    env = DHIEnvironment(workspace)
    task = TaskSpec(
        task_id="agent-runner-recovers-hidden-tool",
        prompt="Search for marker in the repository.",
        goal="Find the marker in README.md.",
        visible_tool_ids=["fs.list_files", "fs.read_file"],
        postconditions=[{"type": "contains", "path": "README.md", "text": "marker"}],
    )
    client = FakeToolCallingClient([
        tool_call("c1", "fs_search_text", {"query": "marker"}),
        tool_call("c2", "catalog_search", {"query": "search text in files"}),
        tool_call("c3", "fs_search_text", {"query": "marker"}),
        final_answer("Found marker in README.md.")
    ])

    result = run_agent_task(env, task, client, max_model_turns=6)

    assert result.closure["success"] is True
    failed_calls = [event for event in env.events if event.get("event_type") == "action_executed" and not event["actual_tool_result"]["ok"]]
    assert len(failed_calls) == 1
    assert "discover it first" in failed_calls[0]["actual_tool_result"]["error"]
    assert result.tool_call_count == 3


def test_runner_never_treats_model_done_message_as_verified_closure(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    env = DHIEnvironment(workspace)
    client = FakeToolCallingClient([final_answer("Done, the task is complete.")])

    result = run_agent_task(env, make_task(), client, max_model_turns=2)

    assert result.final_answer == "Done, the task is complete."
    assert result.closure["success"] is False
    assert result.closure["failed_postconditions"]


def test_runner_stops_after_model_turn_limit_without_claiming_success(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    env = DHIEnvironment(workspace)
    client = FakeToolCallingClient([tool_call("c1", "fs_list_files", {"path": ""})] * 3)

    result = run_agent_task(env, make_task(), client, max_model_turns=1)

    assert result.stopped_reason == "max_model_turns"
    assert result.closure["success"] is False


def test_discovery_and_hidden_call_in_same_model_turn_requires_schema_refresh(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "README.md").write_text("marker", encoding="utf-8")
    env = DHIEnvironment(workspace)
    task = TaskSpec(
        task_id="agent-runner-same-turn-schema-snapshot",
        prompt="Search the workspace for marker.",
        goal="Find marker in README.md.",
        visible_tool_ids=["fs.list_files", "fs.read_file"],
        postconditions=[{"type": "contains", "path": "README.md", "text": "marker"}],
    )
    client = FakeToolCallingClient([
        {
            "choices": [{"message": {"role": "assistant", "tool_calls": [
                {"id": "c1", "type": "function", "function": {"name": "catalog_search", "arguments": '{"query":"search text in files"}'}},
                {"id": "c2", "type": "function", "function": {"name": "fs_search_text", "arguments": '{"query":"marker"}'}},
            ]}}]
        },
        tool_call("c3", "fs_search_text", {"query": "marker"}),
        final_answer("Found marker in README.md."),
    ])

    result = run_agent_task(env, task, client, max_model_turns=5)

    blocked = [event for event in env.events if event.get("event_type") == "action_executed" and not event["actual_tool_result"]["ok"]]
    assert len(blocked) == 1
    assert "schema presented for this turn" in blocked[0]["actual_tool_result"]["error"]
    assert "fs_search_text" not in client.tool_sets[0]
    assert "fs_search_text" in client.tool_sets[1]
    assert result.closure["success"] is True


def test_runner_records_and_scores_pre_action_effect_forecast(tmp_path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "README.md").write_text("# Demo\n", encoding="utf-8")
    (workspace / "src").mkdir()
    (workspace / "src" / "api.py").write_text("def healthcheck():\n    return True\n", encoding="utf-8")
    env = DHIEnvironment(workspace)
    task = TaskSpec(
        task_id="agent-runner-predict-effects",
        prompt="Add a note that the healthcheck function is in src/api.py to README.md.",
        goal="README documents the healthcheck function path and source is unchanged.",
        visible_tool_ids=["fs.read_file", "fs.append_file"],
        protected_paths=["src/api.py"],
        postconditions=[{"type": "contains", "path": "README.md", "text": "healthcheck: src/api.py"}],
    )
    client = FakeToolCallingClient([
        tool_call("c1", "fs_append_file", {
            "path": "README.md",
            "content": "\nhealthcheck: src/api.py\n",
            "__dhi_expected_effects": {
                "changed_paths": ["README.md"],
                "unchanged_paths": ["src/api.py"],
            },
            "__dhi_subgoal": "Document the verified implementation location",
        }),
        final_answer("README now documents the healthcheck location."),
    ])

    result = run_agent_task(env, task, client, max_model_turns=3)

    executed = [event for event in env.events if event.get("event_type") == "action_executed"]
    assert len(executed) == 1
    assert executed[0]["expected_effects"]["changed_paths"] == ["README.md"]
    assert executed[0]["prediction_comparison"]["status"] == "matched"
    assert executed[0]["arguments"] == {"path": "README.md", "content": "\nhealthcheck: src/api.py\n"}
    assert result.closure["success"] is True
