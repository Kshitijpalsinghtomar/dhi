"""Fail-closed adjudication gate for ORBIT-style instruction datasets.

A generation-quality grade is not a correctness label. This module requires full
row coverage, explicit data-column mapping, prompt-hash lineage, independent
verification flags, and group-safe split assignments before a candidate can be
promoted for training or evaluation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable

ALLOWED_VERDICTS = {"candidate", "revise", "reject"}
ALLOWED_SPLITS = {"train", "validation", "test"}
REQUIRED_CHECKS = (
    "semantic_correctness",
    "factual_support",
    "execution_claims",
    "safety_review",
)


class AdjudicationError(ValueError):
    """Raised when dataset lineage or adjudication coverage is unsafe."""


def normalize_text(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    value = "".join(char if char.isalnum() else " " for char in value)
    return " ".join(value.split())


def prompt_fingerprint(value: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise AdjudicationError("prompt text must be a non-empty string")
    normalized = normalize_text(value)
    if not normalized:
        raise AdjudicationError("prompt is empty after normalization")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _stable_digest(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _review_rows(judgements: Any) -> list[dict[str, Any]]:
    if isinstance(judgements, dict):
        items = judgements.get("rows")
    else:
        items = judgements
    if not isinstance(items, list) or any(not isinstance(item, dict) for item in items):
        raise AdjudicationError("judgements must be a list or an object containing rows[]")
    return items


def adjudicate_rows(
    rows: Iterable[dict[str, Any]],
    judgements: Any,
    *,
    prompt_column: str | None,
    completion_column: str | None,
    expected_row_count: int,
) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """Return a report, approved candidates, and held/rejected rows.

    Judgements are joined by SHA-256 of normalized prompt text, not unstable UI
    row positions. A candidate is only promoted when every independent check is
    explicitly true and it has a group-safe split assignment.
    """
    source_rows = list(rows)
    reviews = _review_rows(judgements)

    if not isinstance(expected_row_count, int) or expected_row_count < 1:
        raise AdjudicationError("expected_row_count must be a positive integer")
    if len(source_rows) != expected_row_count:
        raise AdjudicationError(
            f"partial dataset: expected {expected_row_count} rows, received {len(source_rows)}"
        )
    if not isinstance(prompt_column, str) or not prompt_column.strip():
        raise AdjudicationError("prompt_column must be selected explicitly")
    if not isinstance(completion_column, str) or not completion_column.strip():
        raise AdjudicationError("completion_column must be selected explicitly")

    available_columns = {key for row in source_rows for key in row}
    if prompt_column not in available_columns:
        raise AdjudicationError(f"prompt column {prompt_column!r} is absent")
    if completion_column not in available_columns:
        raise AdjudicationError(f"completion column {completion_column!r} is absent")

    source_by_fingerprint: dict[str, dict[str, Any]] = {}
    source_ids: set[str] = set()
    for index, row in enumerate(source_rows, start=1):
        if not isinstance(row, dict):
            raise AdjudicationError(f"source row {index} is not an object")
        prompt = row.get(prompt_column)
        completion = row.get(completion_column)
        if not isinstance(prompt, str) or not prompt.strip():
            raise AdjudicationError(f"source row {index} has no usable prompt")
        if not isinstance(completion, str) or not completion.strip():
            raise AdjudicationError(f"source row {index} has no usable completion")
        source_id = row.get("uuid") or row.get("id")
        if not isinstance(source_id, str) or not source_id.strip():
            raise AdjudicationError(f"source row {index} has no stable uuid/id")
        if source_id in source_ids:
            raise AdjudicationError(f"duplicate stable row id: {source_id}")
        source_ids.add(source_id)
        fingerprint = prompt_fingerprint(prompt)
        if fingerprint in source_by_fingerprint:
            raise AdjudicationError("duplicate normalized prompts make review matching ambiguous")
        source_by_fingerprint[fingerprint] = row

    reviews_by_fingerprint: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(reviews, start=1):
        fingerprint = item.get("prompt_sha256")
        if not isinstance(fingerprint, str) or not re.fullmatch(r"[0-9a-f]{64}", fingerprint):
            raise AdjudicationError(f"judgement {index} has an invalid prompt_sha256")
        if fingerprint in reviews_by_fingerprint:
            raise AdjudicationError("duplicate prompt_sha256 in judgement file")
        verdict = item.get("verdict")
        if verdict not in ALLOWED_VERDICTS:
            raise AdjudicationError(f"judgement {index} has an invalid verdict")
        if not isinstance(item.get("reason"), str) or not item["reason"].strip():
            raise AdjudicationError(f"judgement {index} has no reason")
        reviews_by_fingerprint[fingerprint] = item

    source_fingerprints = set(source_by_fingerprint)
    review_fingerprints = set(reviews_by_fingerprint)
    missing_reviews = source_fingerprints - review_fingerprints
    unmatched_reviews = review_fingerprints - source_fingerprints
    if missing_reviews or unmatched_reviews:
        raise AdjudicationError(
            f"review coverage mismatch: {len(missing_reviews)} source rows unreviewed; "
            f"{len(unmatched_reviews)} judgements unmatched"
        )

    approved: list[dict[str, Any]] = []
    held: list[dict[str, Any]] = []
    group_splits: dict[str, set[str]] = defaultdict(set)
    verdict_counts = {name: 0 for name in sorted(ALLOWED_VERDICTS)}

    for fingerprint, row in source_by_fingerprint.items():
        review = reviews_by_fingerprint[fingerprint]
        verdict = review["verdict"]
        verdict_counts[verdict] += 1
        source_id = str(row.get("uuid") or row.get("id"))
        base = {
            "source_id": source_id,
            "prompt_sha256": fingerprint,
            "verdict": verdict,
            "reason": review["reason"],
        }

        if verdict != "candidate":
            held.append({**base, "hold_reason": "revision_required" if verdict == "revise" else "rejected"})
            continue

        checks = review.get("independent_checks")
        complete_checks = isinstance(checks, dict) and all(checks.get(name) is True for name in REQUIRED_CHECKS)
        split = review.get("split")
        group_id = review.get("group_id")
        if not complete_checks:
            held.append({**base, "hold_reason": "independent_checks_incomplete"})
            continue
        if split not in ALLOWED_SPLITS or not isinstance(group_id, str) or not group_id.strip():
            held.append({**base, "hold_reason": "split_or_group_missing"})
            continue

        group_splits[group_id].add(split)
        approved.append({
            "source_id": source_id,
            "prompt": row[prompt_column],
            "completion": row[completion_column],
            "split": split,
            "group_id": group_id,
            "prompt_sha256": fingerprint,
            "source_content_hash": row.get("content_hash"),
        })

    inconsistent_groups = {group: sorted(splits) for group, splits in group_splits.items() if len(splits) > 1}
    if inconsistent_groups:
        raise AdjudicationError(
            f"task groups cross data splits: {json.dumps(inconsistent_groups, sort_keys=True)}"
        )

    report = {
        "schema_version": "1.0",
        "expected_rows": expected_row_count,
        "observed_rows": len(source_rows),
        "reviewed_rows": len(reviews),
        "prompt_column": prompt_column,
        "completion_column": completion_column,
        "source_sha256": _stable_digest(source_rows),
        "judgements_sha256": _stable_digest(reviews),
        "verdict_counts": verdict_counts,
        "approved_rows": len(approved),
        "held_rows": len(held),
        "training_eligible": bool(approved),
        "approval_rule": (
            "candidate verdict + all independent checks true + explicit train/validation/test "
            "split + group_id kept within one split"
        ),
        "required_independent_checks": list(REQUIRED_CHECKS),
    }
    return report, approved, held


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    rows: list[dict[str, Any]] = []
    with source.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                item = json.loads(line)
            except json.JSONDecodeError as exc:
                raise AdjudicationError(f"invalid JSONL at line {line_number}: {exc.msg}") from exc
            if not isinstance(item, dict):
                raise AdjudicationError(f"JSONL row {line_number} is not an object")
            rows.append(item)
    return rows


def write_jsonl(path: str | Path, rows: Iterable[dict[str, Any]]) -> None:
    destination = Path(path)
    if destination.exists():
        raise FileExistsError(f"refusing to overwrite {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="Full processed dataset JSONL")
    parser.add_argument("--judgements", type=Path, required=True, help="JSON/JSONL row judgements")
    parser.add_argument("--expected-rows", type=int, default=300)
    parser.add_argument("--prompt-column", required=True)
    parser.add_argument("--completion-column", required=True)
    parser.add_argument("--approved", type=Path, default=Path("outputs/orbit_approved.jsonl"))
    parser.add_argument("--held", type=Path, default=Path("outputs/orbit_held.jsonl"))
    parser.add_argument("--report", type=Path, default=Path("outputs/orbit_adjudication_report.json"))
    args = parser.parse_args()

    raw_rows = read_jsonl(args.input)
    try:
        judgement_data = json.loads(args.judgements.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid judgement JSON: {exc.msg}") from exc

    report, approved, held = adjudicate_rows(
        raw_rows,
        judgement_data,
        prompt_column=args.prompt_column,
        completion_column=args.completion_column,
        expected_row_count=args.expected_rows,
    )
    if any(path.exists() for path in (args.approved, args.held, args.report)):
        raise SystemExit("Refusing to overwrite existing adjudication outputs.")
    write_jsonl(args.approved, approved)
    write_jsonl(args.held, held)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
