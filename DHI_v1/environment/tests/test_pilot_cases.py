import json
from pathlib import Path


def test_pilot_case_ids_are_unique_and_have_required_contract_fields():
    path = Path(__file__).parents[2] / "benchmark" / "pilot_cases.json"
    suite = json.loads(path.read_text(encoding="utf-8"))
    cases = suite["cases"]
    ids = [case["case_id"] for case in cases]

    assert len(cases) == 12
    assert len(ids) == len(set(ids))
    for case in cases:
        assert case["prompt"].strip()
        assert case["goal"].strip()
        assert case["tool_requirement"]
        assert case["horizon"] in {"short", "medium", "long"}
        assert case["grader"]
        assert case["status"]


def test_pilot_suite_explicitly_separates_supported_and_unsupported_cases():
    path = Path(__file__).parents[2] / "benchmark" / "pilot_cases.json"
    suite = json.loads(path.read_text(encoding="utf-8"))
    cases = suite["cases"]

    executable = [case for case in cases if case["scope"] == "file_workspace"]
    unsupported = [case for case in cases if case["status"] == "not_executable_in_file_workspace"]

    assert len(executable) == 7
    assert len(unsupported) == 5
    assert all(case["postconditions"] for case in executable if case["case_id"] != "file-007-unavailable-resource-honesty")
