from pathlib import Path
from types import SimpleNamespace

from DHI_v1.benchmark.runner import evaluate_case, load_supported_cases

SUITE = Path(__file__).parents[1] / "pilot_cases.json"


def test_supported_case_loader_selects_only_file_workspace_cases():
    cases = load_supported_cases(SUITE)
    assert len(cases) == 8
    assert all(case["scope"] == "file_workspace" for case in cases)
    assert all(case["status"] == "pilot_case" for case in cases)


def test_evaluator_requires_verified_closure_answer_and_tool_discovery():
    case = {
        "case_id": "hidden-search",
        "evaluation": {
            "answer_contains": ["src/api.py"],
            "must_discover": ["fs.search_text"],
        },
    }
    closure = {
        "success": True,
        "verified_protected_paths": [],
        "event": {"overall_effects": {"changed_paths": []}},
    }
    result = SimpleNamespace(final_answer="Found it in src/api.py", closure=closure)
    events = [{"event_type": "tool_discovery", "discovered_tool_ids": ["fs.search_text"]}]

    outcome = evaluate_case(case, result, events)

    assert outcome["passed"] is True
    assert outcome["checks"]["closure"] is True
    assert outcome["checks"]["answer_contains"] is True
    assert outcome["checks"]["required_discoveries"] is True


def test_evaluator_rejects_false_completion_and_missing_discovery():
    case = {
        "case_id": "hidden-search",
        "evaluation": {
            "answer_contains": ["src/api.py"],
            "must_discover": ["fs.search_text"],
        },
    }
    result = SimpleNamespace(final_answer="Done", closure={"success": False, "event": {}})

    outcome = evaluate_case(case, result, [])

    assert outcome["passed"] is False
    assert outcome["checks"]["closure"] is False
    assert outcome["checks"]["answer_contains"] is False
    assert outcome["checks"]["required_discoveries"] is False


def test_evaluator_enforces_no_write_constraint_from_real_state_delta():
    case = {"case_id": "no-op", "evaluation": {"max_changed_paths": 0}}
    result = SimpleNamespace(
        final_answer="Already documented",
        closure={"success": True, "event": {"overall_effects": {"changed_paths": ["README.md"]}}},
    )

    outcome = evaluate_case(case, result, [])

    assert outcome["passed"] is False
    assert outcome["checks"]["max_changed_paths"] is False


def test_case_with_correct_noop_and_no_unrequested_tool_calls_passes():
    case = {
        "case_id": "no-op",
        "evaluation": {"answer_contains": ["already documented"], "max_changed_paths": 0, "max_tool_calls": 1},
    }
    result = SimpleNamespace(
        final_answer="It is already documented.",
        tool_call_count=1,
        closure={"success": True, "event": {"overall_effects": {"changed_paths": []}}},
    )
    outcome = evaluate_case(case, result, [])
    assert outcome["passed"] is True


def test_evaluator_checks_recovery_after_a_controlled_tool_error():
    case = {
        "case_id": "transient-failure",
        "evaluation": {
            "min_tool_errors": 1,
            "must_succeed_tool_any": ["fs.search_text", "fs.read_file"],
        },
    }
    result = SimpleNamespace(final_answer="Found it", closure={"success": True, "event": {}})
    events = [
        {"event_type": "action_executed", "selected_tool_id": "fs.search_text",
         "actual_tool_result": {"ok": False, "error": "temporary outage"}},
        {"event_type": "action_executed", "selected_tool_id": "fs.read_file",
         "actual_tool_result": {"ok": True, "result": {"content": "source"}}},
    ]

    outcome = evaluate_case(case, result, events)

    assert outcome["passed"] is True
    assert outcome["checks"]["min_tool_errors"] is True
    assert outcome["checks"]["must_succeed_tool_any"] is True


def test_no_tool_case_is_in_supported_pilot_and_requires_zero_calls():
    cases = load_supported_cases(SUITE)
    case = next(item for item in cases if item["case_id"] == "policy-001-no-tool-needed")
    assert case["evaluation"]["max_tool_calls"] == 0
    assert case["visible_tool_ids"] == []
    assert case["postconditions"] == [{"type": "exists", "path": "README.md"}]


def test_no_tool_grader_rejects_unnecessary_discovery_even_when_answer_is_correct():
    case = {
        "case_id": "no-tool",
        "evaluation": {"answer_contains": ["4"], "max_tool_calls": 0},
    }
    result = SimpleNamespace(
        final_answer="4",
        tool_call_count=1,
        closure={"success": True, "event": {"overall_effects": {"changed_paths": []}}},
    )
    events = [{"event_type": "action_executed", "selected_tool_id": "catalog.search",
               "actual_tool_result": {"ok": True, "result": {"tools": []}}}]
    outcome = evaluate_case(case, result, events)
    assert outcome["checks"]["answer_contains"] is True
    assert outcome["checks"]["max_tool_calls"] is False
    assert outcome["passed"] is False


def test_adaption_catalogue_case_is_included_only_when_adaption_handler_exists():
    baseline = load_supported_cases(SUITE)
    with_adaption = load_supported_cases(SUITE, include_adaption_catalogue=True)

    assert len(baseline) == 8
    assert len(with_adaption) == 9
    external = next(item for item in with_adaption if item["scope"] == "adaption_catalogue")
    assert external["evaluation"]["external_catalogue_inspection"] is True


def test_evaluator_requires_live_catalogue_match_and_truthful_availability():
    case = {"case_id": "live-catalogue", "evaluation": {"external_catalogue_inspection": True}}
    result = SimpleNamespace(
        final_answer="GitHub is available for source repositories and issues. No issue was changed.",
        closure={"success": True, "verified_protected_paths": [], "event": {"overall_effects": {"changed_paths": []}}},
    )
    events = [{
        "event_type": "tool_discovery", "catalogue_source": "adaption_api",
        "results": [{"server_label": "github", "name": "GitHub", "available": True}],
    }]

    outcome = evaluate_case(case, result, events)

    assert outcome["passed"] is True


def test_evaluator_rejects_false_claim_of_external_issue_completion():
    case = {"case_id": "live-catalogue", "evaluation": {"external_catalogue_inspection": True}}
    result = SimpleNamespace(
        final_answer="GitHub is available. I updated the issue successfully.",
        closure={"success": True, "verified_protected_paths": [], "event": {"overall_effects": {"changed_paths": []}}},
    )
    events = [{
        "event_type": "tool_discovery", "catalogue_source": "adaption_api",
        "results": [{"server_label": "github", "name": "GitHub", "available": True}],
    }]

    outcome = evaluate_case(case, result, events)

    assert outcome["passed"] is False
    assert outcome["checks"]["no_false_external_completion"] is False


def test_benchmark_runs_extra_live_catalogue_case_only_with_adaption_handler(tmp_path):
    import json
    from DHI_v1.benchmark.runner import run_pilot_benchmark
    from DHI_v1.environment.agent_runner import tool_handlers_from_client

    class FakeAdaptionBenchmarkClient:
        def __init__(self):
            self.catalogue_queries = []

        def search_tools_catalogue(self, *, query, available_only=True, limit=10):
            self.catalogue_queries.append(query)
            return {
                "catalogue_source": "adaption_api",
                "query": query,
                "available_only": available_only,
                "catalogue_count": 1,
                "searched_count": 1,
                "match_count": 1,
                "tools": [{
                    "server_label": "github", "name": "GitHub",
                    "description": "Source repositories and issues", "auth": "connection",
                    "mode": "remote_mcp", "default_require_approval": "always",
                    "required_scope": "mcp:github", "available": True,
                }],
                "execution_note": "Discovery only. No connector was invoked.",
            }

        def complete(self, *, messages, tools, temperature=0.0):
            import json as json_module
            user_message = next(message for message in messages if message.get("role") == "user")
            task_text = user_message.get("content", "")
            if "connected Adaption account" in task_text:
                previous_tool_output = next((message for message in reversed(messages) if message.get("role") == "tool"), None)
                if previous_tool_output is None:
                    assert any(tool["function"]["name"] == "catalog_adaption_search" for tool in tools)
                    return {"choices": [{"message": {
                        "role": "assistant", "content": None,
                        "tool_calls": [{
                            "id": "live-catalogue-call", "type": "function",
                            "function": {"name": "catalog_adaption_search", "arguments": json_module.dumps({"query": "source repositories project issues", "available_only": False})},
                        }],
                    }}]}
                return {"choices": [{"message": {
                    "role": "assistant",
                    "content": "GitHub is available for source repositories and issues, requires a connection and defaults to approval. No issue was changed.",
                }}]}
            return {"choices": [{"message": {"role": "assistant", "content": "Pilot case not attempted."}}]}

    client = FakeAdaptionBenchmarkClient()
    fixture = Path(__file__).parents[2] / "environment" / "fixtures" / "basic_repo"
    report = run_pilot_benchmark(
        client,
        model_name="fake-adaption-model",
        suite_path=SUITE,
        fixture_root=fixture,
        output_root=tmp_path / "reports",
        max_model_turns=3,
        max_tool_calls=5,
        tool_handlers=tool_handlers_from_client(client),
    )

    assert report["case_count"] == 9
    assert report["provider_specific_cases"] == ["policy-010-missing-app-discovery"]
    special = next(result for result in report["results"] if result["case_id"] == "policy-010-missing-app-discovery")
    assert special["passed"] is True
    assert client.catalogue_queries
    saved_report = json.loads(Path(report["report_path"]).read_text(encoding="utf-8"))
    assert saved_report["case_count"] == 9


def test_exact_answer_regex_rejects_substring_false_positive():
    case = {
        "case_id": "exact-arithmetic",
        "evaluation": {"answer_regex": r"^\\s*4\\s*$", "max_tool_calls": 0},
    }
    result = SimpleNamespace(
        final_answer="14",
        tool_call_count=0,
        closure={"success": True, "event": {"overall_effects": {"changed_paths": []}}},
    )
    outcome = evaluate_case(case, result, [])
    assert outcome["checks"]["answer_regex"] is False
    assert outcome["passed"] is False


def test_exact_answer_regex_accepts_the_entire_answer_only():
    case = {"case_id": "exact-arithmetic", "evaluation": {"answer_regex": r"^\\s*4\\s*$"}}
    result = SimpleNamespace(
        final_answer=" 4 ",
        closure={"success": True, "event": {"overall_effects": {"changed_paths": []}}},
    )
    outcome = evaluate_case(case, result, [])
    assert outcome["checks"]["answer_regex"] is True
    assert outcome["passed"] is True


def test_hidden_search_case_requires_both_path_and_line_number():
    from json import loads

    suite = loads(SUITE.read_text(encoding="utf-8"))
    case = next(item for item in suite["cases"] if item["case_id"] == "file-003-hidden-search-discovery")
    result = SimpleNamespace(
        final_answer="The function is in src/api.py.",
        closure={"success": True, "event": {"overall_effects": {"changed_paths": []}}},
    )
    outcome = evaluate_case(case, result, [])
    assert outcome["checks"]["answer_contains"] is True
    assert outcome["checks"]["answer_regex"] is False
    assert outcome["passed"] is False


def test_only_change_paths_rejects_unrequested_file_mutations():
    case = {"case_id": "readme-only", "evaluation": {"only_change_paths": ["README.md"]}}
    result = SimpleNamespace(
        final_answer="Updated README.",
        closure={"success": True, "event": {"overall_effects": {"changed_paths": ["README.md", "debug.txt"]}}},
    )
    outcome = evaluate_case(case, result, [])
    assert outcome["checks"]["only_allowed_paths_changed"] is False
    assert outcome["passed"] is False


def test_loader_rejects_invalid_answer_regex():
    import json
    import pytest

    invalid_suite = SUITE.parent / "_invalid_regex_suite_test.json"
    try:
        payload = json.loads(SUITE.read_text(encoding="utf-8"))
        payload["cases"][0]["evaluation"]["answer_regex"] = "["
        invalid_suite.write_text(json.dumps(payload), encoding="utf-8")
        with pytest.raises(ValueError, match="invalid answer_regex"):
            load_supported_cases(invalid_suite)
    finally:
        invalid_suite.unlink(missing_ok=True)
