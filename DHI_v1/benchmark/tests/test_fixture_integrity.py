import unittest
from pathlib import Path

from DHI_v1.environment.fixture_manager import validate_fixture


FIXTURE_ROOT = Path(__file__).resolve().parents[2] / "environment" / "fixtures" / "basic_repo"


class TestPinnedBasicRepositoryFixture(unittest.TestCase):
    def test_checked_in_fixture_manifest_matches_all_payloads(self):
        manifest = validate_fixture(FIXTURE_ROOT)
        self.assertEqual(manifest["fixture_id"], "dhi-v1-basic-repository")
        self.assertEqual(manifest["file_count"], 3)
