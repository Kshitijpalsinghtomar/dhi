import json
from pathlib import Path

import pytest

from DHI_v1.environment.fixture_manager import FixtureError, materialize_fixture, validate_fixture

FIXTURE = Path(__file__).parents[1] / "fixtures" / "basic_repo"


def test_pinned_fixture_validates_with_expected_hashes():
    result = validate_fixture(FIXTURE)
    assert result["fixture_id"] == "dhi-v1-basic-repository"
    assert result["version"] == "1.0.0"
    assert result["file_count"] == 3
    assert result["total_bytes"] > 0


def test_fixture_materializes_into_new_workspace_and_rechecks_hashes(tmp_path):
    destination = tmp_path / "task-001-workspace"
    result = materialize_fixture(FIXTURE, destination)
    assert result["verified"] is True
    assert (destination / "README.md").is_file()
    assert (destination / "src" / "api.py").read_text(encoding="utf-8").startswith("def healthcheck")
    assert result["files"] == validate_fixture(FIXTURE)["files"]


def test_materializer_refuses_to_overwrite_nonempty_destination(tmp_path):
    destination = tmp_path / "existing"
    destination.mkdir()
    protected = destination / "keep.txt"
    protected.write_text("do not delete", encoding="utf-8")
    with pytest.raises(FileExistsError, match="must be empty"):
        materialize_fixture(FIXTURE, destination)
    assert protected.read_text(encoding="utf-8") == "do not delete"


def test_fixture_hash_mismatch_is_detected(tmp_path):
    import shutil
    copied_fixture = tmp_path / "fixture"
    shutil.copytree(FIXTURE, copied_fixture)
    (copied_fixture / "README.md").write_text("tampered", encoding="utf-8")
    with pytest.raises(FixtureError, match="SHA-256 mismatch"):
        validate_fixture(copied_fixture)


def test_manifest_path_traversal_is_rejected(tmp_path):
    import shutil
    copied_fixture = tmp_path / "fixture"
    shutil.copytree(FIXTURE, copied_fixture)
    manifest_path = copied_fixture / "fixture.manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["files"]["../escape.txt"] = "0" * 64
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(FixtureError, match="escapes"):
        validate_fixture(copied_fixture)


def test_materializer_rejects_fixture_source_nested_inside_destination(tmp_path):
    import shutil
    destination = tmp_path / "parent"
    nested_source = destination / "fixture"
    nested_source.parent.mkdir()
    shutil.copytree(FIXTURE, nested_source)
    with pytest.raises(FixtureError, match="source must not be inside"):
        materialize_fixture(nested_source, destination)
