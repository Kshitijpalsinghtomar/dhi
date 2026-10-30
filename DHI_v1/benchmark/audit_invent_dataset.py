"""Download and mechanically audit Adaption Invent task-specification datasets.

The audit is intentionally conservative. It identifies structural/repetitive rows
and completion text that resembles an execution report, but it does not judge
semantic correctness or automatically approve data for training.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
import tempfile
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path
from statistics import median
from typing import Any, Iterable

DEFAULT_API_BASE_URL = "https://api.prod.adaptionlabs.ai"
PROMPT_COLUMNS = (
    "invented_prompt", "enhanced_prompt", "rephrased_prompt", "input_prompt",
    "original_prompt", "prompt",
)
COMPLETION_COLUMNS = (
    "invent_completion", "enhanced_completion", "original_completion",
    "input_completion", "completion", "fused_generation", "single_generation",
)
ACCEPTANCE_LANGUAGE = re.compile(
    r"\b(acceptance criteria|success criteria|must|must not|should|should not|"
    r"preserve|verify|verification|constraint|constraints|only|report|expected|"
    r"ensure|avoid|do not|don't|never|no change|no-op|required|requirement)\b",
    re.IGNORECASE,
)
EXECUTION_CLAIM_PATTERNS = (
    re.compile(r"\b(?:i|we)\s+(?:have\s+|just\s+)?(?:updated|created|deleted|sent|deployed|executed|ran|tested|fixed|committed|pushed|merged)\b", re.I),
    re.compile(r"\b(?:all\s+)?tests\s+passed\b", re.I),
    re.compile(r"\b(?:successfully\s+)?(?:updated|created|deleted|sent|deployed|executed|committed|pushed|merged)\s+(?:the|your|this|a)\b", re.I),
    re.compile(r"\btask\s+(?:is|has been)\s+completed\b", re.I),
    re.compile(r"\bdeployment\s+(?:is\s+)?successful\b", re.I),
)
NEGATED_EXECUTION_CLAIM = re.compile(
    r"\b(?:do not|don't|never|must not|should not)\b.{0,80}\b(?:claim|say|report|state)\b",
    re.I,
)


def _is_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return value.strip().casefold() not in {"", "null", "none", "nan", "n/a"}
    return True


def normalize_text(value: str) -> str:
    """Normalize case, unicode compatibility forms, punctuation and whitespace.

    This detects normalized exact duplicates only. It is not semantic deduplication.
    """
    value = unicodedata.normalize("NFKC", value).casefold()
    value = "".join(char if char.isalnum() else " " for char in value)
    return " ".join(value.split())


def _read_rows(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise FileNotFoundError(path)
    suffix = path.suffix.casefold()
    rows: list[dict[str, Any]] = []
    if suffix in {".jsonl", ".ndjson"}:
        with path.open("r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSONL at line {line_number}: {exc.msg}") from exc
                if not isinstance(item, dict):
                    raise ValueError(f"JSONL row at line {line_number} must be an object")
                rows.append(item)
        return rows
    if suffix == ".json":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise ValueError(f"invalid JSON dataset: {exc.msg}") from exc
        if isinstance(data, dict) and isinstance(data.get("data"), list):
            data = data["data"]
        if not isinstance(data, list) or any(not isinstance(row, dict) for row in data):
            raise ValueError("JSON dataset must be an array of objects or an object containing data[]")
        return data
    if suffix == ".csv":
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if not reader.fieldnames:
                raise ValueError("CSV dataset is missing a header row")
            return [dict(row) for row in reader]
    raise ValueError("input must be .jsonl, .ndjson, .json or .csv")


def _resolve_column(
    rows: list[dict[str, Any]], explicit: str | None, candidates: Iterable[str], role: str
) -> str:
    columns = {key for row in rows for key in row}
    if explicit:
        if explicit not in columns:
            raise ValueError(f"requested {role} column {explicit!r} is not present")
        return explicit
    for candidate in candidates:
        if candidate in columns:
            return candidate
    raise ValueError(
        f"could not identify {role} column; pass it explicitly. Available columns: {sorted(columns)}"
    )


def _execution_claims(text: str) -> list[str]:
    if NEGATED_EXECUTION_CLAIM.search(text):
        return []
    matches = []
    for pattern in EXECUTION_CLAIM_PATTERNS:
        match = pattern.search(text)
        if match:
            matches.append(match.group(0))
    return matches


def inspect_task_spec_dataset(
    input_path: str | Path,
    *,
    prompt_column: str | None = None,
    completion_column: str | None = None,
    min_prompt_chars: int = 20,
    min_completion_chars: int = 20,
    snippet_chars: int = 360,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Return a mechanical quality report and flagged-row summaries.

    Every row remains training-ineligible. Semantic intent preservation and
    acceptance-criteria correctness require human review or execution-based grading.
    """
    path = Path(input_path).expanduser().resolve()
    rows = _read_rows(path)
    if not rows:
        raise ValueError("dataset contains no rows")
    if min_prompt_chars < 1 or min_completion_chars < 1 or snippet_chars < 1:
        raise ValueError("length limits must be positive")

    prompt_key = _resolve_column(rows, prompt_column, PROMPT_COLUMNS, "prompt")
    completion_key = _resolve_column(rows, completion_column, COMPLETION_COLUMNS, "completion")

    prompt_groups: dict[str, list[int]] = defaultdict(list)
    pair_groups: dict[str, list[int]] = defaultdict(list)
    prompt_lengths: list[int] = []
    completion_lengths: list[int] = []
    subdomains: Counter[str] = Counter()
    domains: Counter[str] = Counter()
    difficulty: Counter[str] = Counter()
    row_flags: dict[int, list[str]] = defaultdict(list)
    row_claims: dict[int, list[str]] = {}

    missing_prompt = 0
    missing_completion = 0
    short_prompt = 0
    short_completion = 0
    no_acceptance_language = 0
    rows_with_execution_claims = 0

    for index, row in enumerate(rows, start=1):
        prompt_value = row.get(prompt_key)
        completion_value = row.get(completion_key)
        prompt = str(prompt_value).strip() if _is_present(prompt_value) else ""
        completion = str(completion_value).strip() if _is_present(completion_value) else ""

        if not prompt:
            missing_prompt += 1
            row_flags[index].append("missing_prompt")
        else:
            if len(prompt) < min_prompt_chars:
                short_prompt += 1
                row_flags[index].append("short_prompt")
            normalized_prompt = normalize_text(prompt)
            if normalized_prompt:
                prompt_groups[normalized_prompt].append(index)
            prompt_lengths.append(len(prompt))

        if not completion:
            missing_completion += 1
            row_flags[index].append("missing_completion")
        else:
            if len(completion) < min_completion_chars:
                short_completion += 1
                row_flags[index].append("short_completion")
            completion_lengths.append(len(completion))
            normalized_completion = normalize_text(completion)
            if prompt and normalized_completion:
                pair_key = normalize_text(prompt) + "\u241f" + normalized_completion
                pair_groups[pair_key].append(index)
            if not ACCEPTANCE_LANGUAGE.search(completion):
                no_acceptance_language += 1
                row_flags[index].append("no_explicit_acceptance_or_constraint_language")
            claims = _execution_claims(completion)
            if claims:
                rows_with_execution_claims += 1
                row_claims[index] = claims
                row_flags[index].append("execution_claim_language_review")

        if _is_present(row.get("metadata_subdomain_primary")):
            subdomains[str(row["metadata_subdomain_primary"])] += 1
        if _is_present(row.get("metadata_primary_domain")):
            domains[str(row["metadata_primary_domain"])] += 1
        if _is_present(row.get("metadata_difficulty_score")):
            difficulty[str(row["metadata_difficulty_score"])] += 1

    duplicate_prompt_groups = {key: indexes for key, indexes in prompt_groups.items() if len(indexes) > 1}
    duplicate_pair_groups = {key: indexes for key, indexes in pair_groups.items() if len(indexes) > 1}
    duplicate_prompt_rows: set[int] = set()
    duplicate_pair_rows: set[int] = set()
    for indexes in duplicate_prompt_groups.values():
        duplicate_prompt_rows.update(indexes[1:])
    for indexes in duplicate_pair_groups.values():
        duplicate_pair_rows.update(indexes[1:])
    for index in duplicate_prompt_rows:
        row_flags[index].append("normalized_duplicate_prompt")
    for index in duplicate_pair_rows:
        row_flags[index].append("normalized_duplicate_prompt_completion_pair")

    flagged: list[dict[str, Any]] = []
    for index in sorted(row_flags):
        row = rows[index - 1]
        prompt = str(row.get(prompt_key) or "").strip()
        completion = str(row.get(completion_key) or "").strip()
        flagged.append({
            "row_number": index,
            "uuid": row.get("uuid") or row.get("id") or f"row-{index}",
            "flags": sorted(set(row_flags[index])),
            "prompt_preview": prompt[:snippet_chars],
            "completion_preview": completion[:snippet_chars],
            "execution_claim_matches": row_claims.get(index, []),
        })

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    report = {
        "dataset_file": path.name,
        "file_sha256": digest,
        "rows": len(rows),
        "minimum_prompt_characters": min_prompt_chars,
        "minimum_completion_characters": min_completion_chars,
        "prompt_column": prompt_key,
        "completion_column": completion_key,
        "missing_prompt_rows": missing_prompt,
        "missing_completion_rows": missing_completion,
        "short_prompt_rows": short_prompt,
        "short_completion_rows": short_completion,
        "rows_without_acceptance_or_constraint_language": no_acceptance_language,
        "rows_with_execution_claim_language": rows_with_execution_claims,
        "normalized_duplicate_prompt_groups": len(duplicate_prompt_groups),
        "rows_in_normalized_duplicate_prompt_groups": sum(len(x) for x in duplicate_prompt_groups.values()),
        "normalized_duplicate_prompt_completion_pair_groups": len(duplicate_pair_groups),
        "rows_in_normalized_duplicate_prompt_completion_pair_groups": sum(len(x) for x in duplicate_pair_groups.values()),
        "prompt_char_median": median(prompt_lengths) if prompt_lengths else None,
        "completion_char_median": median(completion_lengths) if completion_lengths else None,
        "domain_counts": dict(sorted(domains.items())),
        "subdomain_counts": dict(sorted(subdomains.items())),
        "difficulty_counts": dict(sorted(difficulty.items())),
        "flagged_rows": len(flagged),
        "semantic_intent_preservation_verified": False,
        "acceptance_criteria_correctness_verified": False,
        "execution_ground_truth_verified": False,
        "training_eligible": False,
        "note": (
            "Mechanical audit only. Normalized exact duplicates are not semantic duplicates. "
            "Execution-claim patterns are review flags, not proof of fabrication. "
            "Inspect sampled tasks and execute candidate tasks in the pinned environment before benchmark or training promotion."
        ),
    }
    return report, flagged


def download_adaption_dataset(
    *,
    dataset_id: str,
    api_key: str,
    destination: str | Path,
    base_url: str = DEFAULT_API_BASE_URL,
    file_format: str = "jsonl",
    timeout_seconds: float = 180.0,
) -> Path:
    """Download a processed dataset without overwriting existing files or logging credentials."""
    if not isinstance(dataset_id, str) or not dataset_id.strip():
        raise ValueError("dataset_id is required")
    if not api_key:
        raise ValueError("Adaption API key is required")
    if file_format not in {"csv", "json", "jsonl", "parquet"}:
        raise ValueError("file_format must be csv, json, jsonl or parquet")
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")
    if not base_url.startswith("https://"):
        raise ValueError("base_url must use HTTPS")

    target = Path(destination).expanduser().resolve()
    if target.exists():
        raise FileExistsError(f"refusing to overwrite existing dataset export: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)
    encoded_id = urllib.parse.quote(dataset_id.strip(), safe="")
    url = f"{base_url.rstrip('/')}/api/v1/datasets/{encoded_id}/download?fileFormat={file_format}"
    request = urllib.request.Request(
        url,
        headers={"Authorization": f"Bearer {api_key}", "Accept": "application/octet-stream"},
        method="GET",
    )
    temporary: Path | None = None
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix=f".{target.name}.", delete=False) as handle:
                temporary = Path(handle.name)
                for chunk in iter(lambda: response.read(1024 * 1024), b""):
                    handle.write(chunk)
                handle.flush()
                os.fsync(handle.fileno())
        if temporary.stat().st_size == 0:
            raise ValueError("Adaption returned an empty dataset export")
        os.replace(temporary, target)
        temporary = None
        return target
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"Adaption dataset download failed with HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"Adaption dataset download failed: {type(exc).__name__}") from exc
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def write_audit_outputs(
    report: dict[str, Any],
    flagged_rows: list[dict[str, Any]],
    *,
    report_path: str | Path,
    flagged_path: str | Path,
) -> None:
    report_file = Path(report_path)
    flagged_file = Path(flagged_path)
    if report_file.resolve() == flagged_file.resolve():
        raise ValueError("report and flagged outputs must be different files")
    for path in (report_file, flagged_file):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite existing audit output: {path}")
        path.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    with flagged_file.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=[
            "row_number", "uuid", "flags", "prompt_preview", "completion_preview", "execution_claim_matches"
        ])
        writer.writeheader()
        for row in flagged_rows:
            writer.writerow({**row, "flags": ";".join(row["flags"]),
                             "execution_claim_matches": ";".join(row["execution_claim_matches"])})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="Existing JSONL/JSON/CSV dataset export")
    parser.add_argument("--dataset-id", default=None, help="Download a dataset through the Adaption REST API")
    parser.add_argument("--download-to", type=Path, default=Path("outputs/dhi_invent_export.jsonl"))
    parser.add_argument("--prompt-column", default=None)
    parser.add_argument("--completion-column", default=None)
    parser.add_argument("--report", type=Path, default=Path("outputs/dhi_invent_audit_report.json"))
    parser.add_argument("--flagged", type=Path, default=Path("outputs/dhi_invent_flagged_rows.csv"))
    args = parser.parse_args()

    source = args.input
    if args.dataset_id:
        api_key = os.environ.get("ADAPTION_API_KEY") or os.environ.get("DHI_ADAPTION_API_KEY") or ""
        if not api_key:
            raise SystemExit("Set ADAPTION_API_KEY (or DHI_ADAPTION_API_KEY) in the local environment.")
        source = download_adaption_dataset(
            dataset_id=args.dataset_id,
            api_key=api_key,
            destination=args.download_to,
            base_url=os.environ.get("DHI_ADAPTION_API_BASE_URL", DEFAULT_API_BASE_URL),
            file_format="jsonl",
        )
    if source is None:
        raise SystemExit("Pass --input <export.jsonl> or --dataset-id <id>.")

    report, flagged = inspect_task_spec_dataset(
        source, prompt_column=args.prompt_column, completion_column=args.completion_column
    )
    write_audit_outputs(report, flagged, report_path=args.report, flagged_path=args.flagged)
    print(json.dumps({
        "dataset_file": report["dataset_file"],
        "rows": report["rows"],
        "prompt_column": report["prompt_column"],
        "completion_column": report["completion_column"],
        "flagged_rows": report["flagged_rows"],
        "report_path": str(args.report),
        "flagged_rows_path": str(args.flagged),
        "training_eligible": False,
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
