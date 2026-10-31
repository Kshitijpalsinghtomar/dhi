from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "orbit_adjudication.py"
SPEC = importlib.util.spec_from_file_location("orbit_adjudication", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Cannot load {MODULE_PATH}")
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


def make_row(index: int, prompt: str = "A grounded task prompt", completion: str = "A grounded answer") -> dict:
    return {
        "uuid": f"row-{index}",
        "invented_prompt": f"{prompt} {index}",
        "invent_completion": f"{completion} {index}",
        "content_hash": f"hash-{index}",
    }


def make_review(row: dict, *, checks: dict | None = None, split: str = "train", group: str = "family-a") -> dict:
    return {
        "prompt_sha256": module.prompt_fingerprint(row["invented_prompt"]),
        "verdict": "candidate",
        "reason": "Verified useful candidate",
        "issue_type": "technical_reasoning",
        "independent_checks": checks or {},
        "split": split,
        "group_id": group,
    }


class OrbitAdjudicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.checks = {
            "semantic_correctness": True,
            "factual_support": True,
            "execution_claims": True,
            "safety_review": True,
        }

    def test_rejects_partial_dataset(self) -> None:
        rows = [make_row(1)]
        reviews = [make_review(rows[0], checks=self.checks)]
        with self.assertRaises(module.AdjudicationError):
            module.adjudicate_rows(
                rows, reviews,
                prompt_column="invented_prompt",
                completion_column="invent_completion",
                expected_row_count=2,
            )

    def test_requires_explicit_prompt_and_completion_columns(self) -> None:
        rows = [make_row(1)]
        reviews = [make_review(rows[0], checks=self.checks)]
        with self.assertRaises(module.AdjudicationError):
            module.adjudicate_rows(
                rows, reviews,
                prompt_column=None,
                completion_column="invent_completion",
                expected_row_count=1,
            )

    def test_candidate_without_all_independent_checks_is_held(self) -> None:
        rows = [make_row(1)]
        reviews = [make_review(rows[0], checks={"semantic_correctness": True})]
        report, approved, held = module.adjudicate_rows(
            rows, reviews,
            prompt_column="invented_prompt",
            completion_column="invent_completion",
            expected_row_count=1,
        )
        self.assertEqual(report["approved_rows"], 0)
        self.assertEqual(held[0]["hold_reason"], "independent_checks_incomplete")
        self.assertEqual(approved, [])

    def test_verified_candidate_requires_explicit_split_and_is_promoted(self) -> None:
        rows = [make_row(1)]
        reviews = [make_review(rows[0], checks=self.checks, split="validation")]
        report, approved, held = module.adjudicate_rows(
            rows, reviews,
            prompt_column="invented_prompt",
            completion_column="invent_completion",
            expected_row_count=1,
        )
        self.assertEqual(report["approved_rows"], 1)
        self.assertEqual(approved[0]["split"], "validation")
        self.assertEqual(held, [])

    def test_duplicate_prompts_are_rejected_before_hash_matching(self) -> None:
        first = make_row(1, prompt="same prompt")
        second = make_row(2, prompt="same prompt")
        reviews = [make_review(first, checks=self.checks)]
        with self.assertRaises(module.AdjudicationError):
            module.adjudicate_rows(
                [first, second], reviews,
                prompt_column="invented_prompt",
                completion_column="invent_completion",
                expected_row_count=2,
            )

    def test_missing_or_unmatched_review_fails_closed(self) -> None:
        rows = [make_row(1), make_row(2)]
        reviews = [make_review(rows[0], checks=self.checks)]
        with self.assertRaises(module.AdjudicationError):
            module.adjudicate_rows(
                rows, reviews,
                prompt_column="invented_prompt",
                completion_column="invent_completion",
                expected_row_count=2,
            )

    def test_inconsistent_group_splits_are_rejected(self) -> None:
        first = make_row(1)
        second = make_row(2)
        reviews = [
            make_review(first, checks=self.checks, split="train", group="same-family"),
            make_review(second, checks=self.checks, split="test", group="same-family"),
        ]
        with self.assertRaises(module.AdjudicationError):
            module.adjudicate_rows(
                [first, second], reviews,
                prompt_column="invented_prompt",
                completion_column="invent_completion",
                expected_row_count=2,
            )


if __name__ == "__main__":
    unittest.main()
