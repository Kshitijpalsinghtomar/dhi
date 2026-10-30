import json
from pathlib import Path
from unittest.mock import patch

import pytest

from DHI_v1.benchmark.audit_invent_dataset import (
    download_adaption_dataset,
    inspect_task_spec_dataset,
    normalize_text,
    write_audit_outputs,
)


def write_jsonl(path: Path, rows):
    path.write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows), encoding="utf-8")


def test_audit_uses_adaption_invent_prompt_and_completion_columns(tmp_path):
    source = tmp_path / "dataset.jsonl"
    write_jsonl(source, [
        {
            "uuid": "r1", "invented_prompt": "Find the function in the repository.",
            "invent_completion": "Acceptance criteria: report the verified file path.",
            "metadata_subdomain_primary": "code.python",
        },
        {
            "uuid": "r2", "invented_prompt": "Update a README section without touching source.",
            "invent_completion": "Constraints: preserve the source and verify the README.",
            "metadata_subdomain_primary": "code.react",
        },
    ])

    report, flagged = inspect_task_spec_dataset(source)

    assert report["rows"] == 2
    assert report["prompt_column"] == "invented_prompt"
    assert report["completion_column"] == "invent_completion"
    assert report["missing_prompt_rows"] == 0
    assert report["missing_completion_rows"] == 0
    assert report["training_eligible"] is False
    assert flagged == []


def test_audit_flags_missing_fields_exact_duplicates_and_execution_claims(tmp_path):
    source = tmp_path / "dataset.jsonl"
    write_jsonl(source, [
        {"uuid": "r1", "invented_prompt": "Search for the setup file.",
         "invent_completion": "Acceptance criteria: give the exact path."},
        {"uuid": "r2", "invented_prompt": "  SEARCH   for the setup file. ",
         "invent_completion": "I updated the file and all tests passed."},
        {"uuid": "r3", "invented_prompt": "",
         "invent_completion": "Preserve existing files and do not invent outputs."},
        {"uuid": "r4", "invented_prompt": "Find the config file.", "invent_completion": None},
    ])

    report, flagged = inspect_task_spec_dataset(source)

    assert report["missing_prompt_rows"] == 1
    assert report["missing_completion_rows"] == 1
    assert report["normalized_duplicate_prompt_groups"] == 1
    assert report["rows_with_execution_claim_language"] == 1
    assert report["training_eligible"] is False
    reasons = {item["uuid"]: set(item["flags"]) for item in flagged}
    assert "normalized_duplicate_prompt" in reasons["r2"]
    assert "execution_claim_language_review" in reasons["r2"]
    assert "missing_prompt" in reasons["r3"]
    assert "missing_completion" in reasons["r4"]


def test_explicit_columns_override_default_invent_columns(tmp_path):
    source = tmp_path / "dataset.jsonl"
    write_jsonl(source, [{"task": "Inspect the repository", "criteria": "Report the exact path"}])

    report, flagged = inspect_task_spec_dataset(source, prompt_column="task", completion_column="criteria")

    assert report["prompt_column"] == "task"
    assert report["completion_column"] == "criteria"
    assert report["rows"] == 1
    assert flagged == []


def test_audit_rejects_malformed_jsonl_with_line_number(tmp_path):
    source = tmp_path / "broken.jsonl"
    source.write_text('{"invented_prompt":"ok","invent_completion":"ok"}\n{broken}\n', encoding="utf-8")

    with pytest.raises(ValueError, match="line 2"):
        inspect_task_spec_dataset(source)


def test_normalize_text_collapses_case_spacing_and_punctuation():
    assert normalize_text("  Search   the Repo, Please! ") == "search the repo please"


def test_download_adaption_dataset_streams_jsonl_without_logging_api_key(tmp_path):
    destination = tmp_path / "export.jsonl"
    captured = {}

    class FakeResponse:
        def __init__(self):
            self.sent = False

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, size=-1):
            if self.sent:
                return b""
            self.sent = True
            return b'{"invented_prompt":"task","invent_completion":"criteria"}\n'

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["auth"] = request.get_header("Authorization")
        return FakeResponse()

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        returned = download_adaption_dataset(
            dataset_id="1eccaa36-bdc7-4d6e-ac8d-41b20d9425e2",
            api_key="test-secret",
            destination=destination,
            base_url="https://api.test.invalid",
            file_format="jsonl",
        )

    assert returned == destination
    assert captured["url"] == "https://api.test.invalid/api/v1/datasets/1eccaa36-bdc7-4d6e-ac8d-41b20d9425e2/download?fileFormat=jsonl"
    assert captured["auth"] == "Bearer test-secret"
    assert destination.read_text(encoding="utf-8").startswith('{"invented_prompt"')


def test_download_adaption_dataset_refuses_overwrite_and_rejects_invalid_format(tmp_path):
    destination = tmp_path / "existing.jsonl"
    destination.write_text("preserve", encoding="utf-8")

    with pytest.raises(FileExistsError):
        download_adaption_dataset(
            dataset_id="dataset-id", api_key="key", destination=destination,
            base_url="https://api.test.invalid", file_format="jsonl",
        )
    with pytest.raises(ValueError, match="file_format"):
        download_adaption_dataset(
            dataset_id="dataset-id", api_key="key", destination=tmp_path / "x",
            base_url="https://api.test.invalid", file_format="yaml",
        )
    assert destination.read_text(encoding="utf-8") == "preserve"


def test_audit_output_writer_creates_json_report_and_flagged_csv(tmp_path):
    report_path = tmp_path / "audit.json"
    flagged_path = tmp_path / "flagged.csv"
    report = {"rows": 1, "training_eligible": False}
    flagged = [{
        "row_number": 1,
        "uuid": "row-1",
        "flags": ["missing_prompt", "short_completion"],
        "prompt_preview": "",
        "completion_preview": "too short",
        "execution_claim_matches": [],
    }]

    write_audit_outputs(report, flagged, report_path=report_path, flagged_path=flagged_path)

    assert json.loads(report_path.read_text(encoding="utf-8")) == report
    csv_text = flagged_path.read_text(encoding="utf-8")
    assert "missing_prompt;short_completion" in csv_text
    assert "row-1" in csv_text


def test_audit_output_writer_refuses_same_path_for_report_and_csv(tmp_path):
    same_path = tmp_path / "same.txt"
    with pytest.raises(ValueError, match="different files"):
        write_audit_outputs({"rows": 1}, [], report_path=same_path, flagged_path=same_path)
