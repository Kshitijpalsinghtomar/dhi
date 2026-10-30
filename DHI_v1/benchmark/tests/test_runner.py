from pathlib import Path
from types import SimpleNamespace

from DHI_v1.benchmark.runner import evaluate_case, load_supported_cases

SUITE = Path(__file__).parents[1] / "pilot_cases.json"


def test_supported_case_loader_selects_only_file_workspace_cases():
    cases = load_supported_cases(SUITE)
    assert len(cases) == 7
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
