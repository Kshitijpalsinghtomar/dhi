from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

REPO_ROOT_DEFAULT = Path.cwd()
DEFAULT_MANIFEST = Path("DHI_v1/benchmark/task_manifest.json")
DEFAULT_SCHEMA = Path("DHI_v1/benchmark/task_manifest.schema.json")
TOOL_REGISTRY = Path("DHI_v1/benchmark/fixtures/plugin_ecology/plugin_tool_registry.json")
EXPECTED_STRATA = {f"S{index:02d}" for index in range(1, 11)}
TASK_ID_RE = re.compile(r"^ORBIT-(A|B)-(S(?:0[1-9]|10))-([0-9]{3})$")

# The family fingerprint binds the substantive task definition. It deliberately
# excludes record identity, authoring provenance, validation state and run state.
FAMILY_FIELDS = (
    "stratum_id",
    "task_contract",
    "environment",
    "tool_inventory",
    "required_capabilities",
    "horizon",
    "preconditions",
    "postconditions",
    "grader",
    "policy",
)


def canonical_json(value: Any) -> str:
    """Canonical UTF-8 JSON representation used by all ORBIT integrity hashes."""
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()


def family_fingerprint(task: dict[str, Any]) -> str:
    material = {field: task[field] for field in FAMILY_FIELDS}
    return sha256_json(material)


def task_instance_fingerprint(task: dict[str, Any]) -> str:
    material = json.loads(canonical_json(task))
    split = material.get("split_metadata", {})
    split.pop("task_instance_sha256", None)
    return sha256_json(material)


def _safe_repo_path(repo_root: Path, relative_path: str) -> Path | None:
    pure = PurePosixPath(relative_path)
    if pure.is_absolute() or not pure.parts or any(part in {"", ".", ".."} for part in pure.parts):
        return None
    root = repo_root.resolve()
    candidate = root.joinpath(*pure.parts).resolve()
    try:
        candidate.relative_to(root)
    except ValueError:
        return None
    return candidate


def _record_error(errors: list[str], code: str, message: str) -> None:
    errors.append(f"[{code}] {message}")


def _validate_schema(
    manifest: dict[str, Any],
    schema: dict[str, Any],
    errors: list[str],
) -> None:
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:  # jsonschema reports several schema exception types
        _record_error(errors, "schema-definition", str(exc))
        return

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for issue in sorted(
        validator.iter_errors(manifest),
        key=lambda item: (tuple(str(part) for part in item.absolute_path), item.message),
    ):
        location = "/".join(str(part) for part in issue.absolute_path) or "$"
        _record_error(errors, "schema", f"{location}: {issue.message}")


def _load_tool_registry(
    repo_root: Path,
    errors: list[str],
) -> tuple[dict[str, dict[str, Any]], str | None]:
    path = _safe_repo_path(repo_root, TOOL_REGISTRY.as_posix())
    if path is None or not path.is_file():
        _record_error(errors, "tool-registry", f"missing registry file: {TOOL_REGISTRY.as_posix()}")
        return {}, None
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        _record_error(errors, "tool-registry", f"cannot read registry: {exc}")
        return {}, None

    tools = registry.get("tools")
    if not isinstance(tools, list):
        _record_error(errors, "tool-registry", "registry.tools must be an array")
        return {}, None

    ids: dict[str, dict[str, Any]] = {}
    for index, tool in enumerate(tools):
        if not isinstance(tool, dict) or not isinstance(tool.get("tool_id"), str):
            _record_error(errors, "tool-registry", f"registry.tools[{index}] has no string tool_id")
            continue
        tool_id = tool["tool_id"]
        if tool_id in ids:
            _record_error(errors, "tool-registry", f"duplicate tool_id: {tool_id}")
        ids[tool_id] = tool

    computed = sha256_json(tools)
    recorded = registry.get("tool_schema_sha256")
    if recorded != computed:
        _record_error(
            errors,
            "tool-registry",
            f"tool_schema_sha256 mismatch: recorded={recorded!r}, computed={computed}",
        )
    return ids, computed


def _validate_evidence_references(
    task: dict[str, Any],
    repo_root: Path,
    errors: list[str],
) -> None:
    environment = task.get("environment") if isinstance(task.get("environment"), dict) else {}
    inventory = task.get("tool_inventory") if isinstance(task.get("tool_inventory"), dict) else {}
    grader = task.get("grader") if isinstance(task.get("grader"), dict) else {}
    candidates = {
        "environment.external_snapshot_ref": environment.get("external_snapshot_ref"),
        "tool_inventory.inventory_snapshot_ref": inventory.get("inventory_snapshot_ref"),
        "grader.review_rubric_ref": grader.get("review_rubric_ref"),
    }
    for label, reference in candidates.items():
        if reference is None:
            continue
        if not isinstance(reference, str) or not reference:
            _record_error(errors, "evidence-ref", f"{task.get('task_id')}: {label} is not a non-empty path")
            continue
        path = _safe_repo_path(repo_root, reference)
        if path is None:
            _record_error(errors, "evidence-ref", f"{task.get('task_id')}: unsafe repository path {reference!r}")
        elif not path.is_file():
            _record_error(errors, "evidence-ref", f"missing {reference!r} referenced by {task.get('task_id')}")


def collect_manifest_errors(
    manifest: dict[str, Any],
    schema: dict[str, Any],
    *,
    repo_root: Path | str | None = None,
    require_frozen: bool = False,
) -> list[str]:
    """Return all schema and cross-record integrity errors in stable order."""
    errors: list[str] = []
    root = Path(repo_root).resolve() if repo_root is not None else None
    _validate_schema(manifest, schema, errors)
    if not isinstance(manifest, dict):
        return errors

    tasks = manifest.get("tasks", [])
    families = manifest.get("task_families", [])
    strata = manifest.get("strata", [])
    if not isinstance(tasks, list) or not isinstance(families, list) or not isinstance(strata, list):
        return errors

    # Top-level counts and the declared ten-stratum partition.
    if manifest.get("materialized_task_count") != len(tasks):
        _record_error(
            errors,
            "count",
            f"materialized_task_count={manifest.get('materialized_task_count')!r}, actual={len(tasks)}",
        )
    actual_stage_counts = Counter(
        task.get("stage")
        for task in tasks
        if isinstance(task, dict) and isinstance(task.get("stage"), str)
    )
    declared_stage_counts = manifest.get("materialized_stage_counts", {})
    if not isinstance(declared_stage_counts, dict):
        declared_stage_counts = {}
    for stage in ("A", "B"):
        if declared_stage_counts.get(stage) != actual_stage_counts.get(stage, 0):
            _record_error(
                errors,
                "stage-count",
                f"stage {stage}: declared={declared_stage_counts.get(stage)!r}, actual={actual_stage_counts.get(stage, 0)}",
            )

    stratum_ids = [
        item.get("stratum_id")
        for item in strata
        if isinstance(item, dict) and isinstance(item.get("stratum_id"), str)
    ]
    duplicate_strata = sorted(key for key, count in Counter(stratum_ids).items() if count > 1)
    if duplicate_strata:
        _record_error(errors, "strata", f"duplicate stratum IDs: {', '.join(duplicate_strata)}")
    missing_strata = sorted(EXPECTED_STRATA - set(stratum_ids))
    unexpected_strata = sorted(set(stratum_ids) - EXPECTED_STRATA)
    if missing_strata or unexpected_strata:
        _record_error(
            errors,
            "strata",
            f"missing={missing_strata}, unexpected={unexpected_strata}",
        )

    target = manifest.get("per_stratum_stage_target", 12)
    per_stratum: dict[tuple[str, str], list[int]] = defaultdict(list)
    seen_task_ids: set[str] = set()
    task_family_ids: set[str] = set()
    task_groups_by_stage: dict[str, set[str]] = defaultdict(set)
    task_fingerprints_by_family: dict[str, set[str]] = defaultdict(set)
    registry: dict[str, dict[str, Any]] = {}
    registry_hash: str | None = None
    if root is not None:
        registry, registry_hash = _load_tool_registry(root, errors)

    for task in tasks:
        if not isinstance(task, dict):
            continue
        task_id = task.get("task_id")
        match = TASK_ID_RE.fullmatch(task_id) if isinstance(task_id, str) else None
        if isinstance(task_id, str):
            if task_id in seen_task_ids:
                _record_error(errors, "task-id", f"duplicate task_id: {task_id}")
            seen_task_ids.add(task_id)

        stage = task.get("stage")
        stratum = task.get("stratum_id")
        if match:
            id_stage, id_stratum, ordinal_text = match.groups()
            ordinal = int(ordinal_text)
            if id_stage != stage or id_stratum != stratum:
                _record_error(
                    errors,
                    "task-id",
                    f"identity mismatch for {task_id}: record says stage={stage}, stratum={stratum}",
                )
            per_stratum[(id_stage, id_stratum)].append(ordinal)
        elif task_id is not None:
            _record_error(errors, "task-id", f"non-canonical task ID: {task_id!r}")

        valid_stage = stage in ("A", "B") if isinstance(stage, str) else False
        if valid_stage and isinstance(stratum, str):
            count = sum(1 for row in tasks if isinstance(row, dict) and row.get("stage") == stage and row.get("stratum_id") == stratum)
            if count > target:
                _record_error(errors, "quota", f"{stage}/{stratum} has {count} tasks; target is {target}")

        family_id = task.get("task_family_id")
        group_id = task.get("independence_group_id")
        if isinstance(family_id, str):
            task_family_ids.add(family_id)
        if isinstance(group_id, str) and valid_stage:
            task_groups_by_stage[stage].add(group_id)

        split = task.get("split_metadata")
        if not isinstance(split, dict):
            split = {}
        expected_partition = "stage_a" if stage == "A" else "stage_b" if stage == "B" else None
        if expected_partition and split.get("partition") != expected_partition:
            _record_error(errors, "split", f"{task_id}: stage {stage} requires partition {expected_partition}")
        expected_sealed = stage == "B"
        if valid_stage and split.get("holdout_sealed") is not expected_sealed:
            _record_error(
                errors,
                "split",
                f"{task_id}: stage {stage} requires holdout_sealed={str(expected_sealed).lower()}",
            )

        if isinstance(task, dict) and all(field in task for field in FAMILY_FIELDS):
            computed_family_hash = family_fingerprint(task)
            declared_family_hash = split.get("family_fingerprint_sha256")
            if declared_family_hash != computed_family_hash:
                _record_error(
                    errors,
                    "family",
                    f"fingerprint mismatch for {task_id}: declared={declared_family_hash!r}, computed={computed_family_hash}",
                )
            if isinstance(family_id, str):
                task_fingerprints_by_family[family_id].add(computed_family_hash)

        declared_instance_hash = split.get("task_instance_sha256")
        if declared_instance_hash is not None:
            computed_instance_hash = task_instance_fingerprint(task)
            if declared_instance_hash != computed_instance_hash:
                _record_error(
                    errors,
                    "task-hash",
                    f"task instance hash mismatch for {task_id}: declared={declared_instance_hash!r}, computed={computed_instance_hash}",
                )

        inventory = task.get("tool_inventory")
        if not isinstance(inventory, dict):
            inventory = {}
        visible = set(item for item in inventory.get("visible_tool_ids", []) if isinstance(item, str))
        discoverable = set(item for item in inventory.get("discoverable_tool_ids", []) if isinstance(item, str))
        required = set(item for item in inventory.get("required_tool_ids", []) if isinstance(item, str))
        unavailable = sorted(required - visible - discoverable)
        for tool_id in unavailable:
            _record_error(errors, "tool-inventory", f"{task_id}: required tool {tool_id} is neither visible nor discoverable")

        if root is not None:
            expected_tool_hash = registry_hash
            if expected_tool_hash and inventory.get("tool_schema_sha256") != expected_tool_hash:
                _record_error(
                    errors,
                    "tool-registry",
                    f"{task_id}: tool_schema_sha256 does not match pinned registry",
                )
            all_ids = visible | discoverable | required
            for tool_id in sorted(all_ids):
                record = registry.get(tool_id)
                if record is None:
                    _record_error(errors, "tool-registry", f"unregistered tool {tool_id} in {task_id}")
                elif record.get("allowed_in_benchmark") is not True:
                    _record_error(errors, "tool-registry", f"tool {tool_id} is not allowed in benchmark ({task_id})")

        if root is not None:
            _validate_evidence_references(task, root, errors)

    # Task ordinals are assigned only after materialization and must be gap-free.
    for (stage, stratum), ordinals in sorted(per_stratum.items()):
        expected = list(range(1, len(ordinals) + 1))
        if sorted(ordinals) != expected:
            _record_error(
                errors,
                "task-id",
                f"non-contiguous ordinals for {stage}/{stratum}: {sorted(ordinals)}, expected {expected}",
            )

    # Family register and task records must be a one-to-one mapping at family level.
    family_by_id: dict[str, dict[str, Any]] = {}
    family_fingerprints: dict[str, str] = {}
    for family in families:
        if not isinstance(family, dict):
            continue
        family_id = family.get("family_id")
        if not isinstance(family_id, str):
            continue
        if family_id in family_by_id:
            _record_error(errors, "family", f"duplicate family registry record: {family_id}")
        family_by_id[family_id] = family
        fingerprint = family.get("family_fingerprint_sha256")
        if isinstance(fingerprint, str):
            other = family_fingerprints.get(fingerprint)
            if other is not None and other != family_id:
                _record_error(errors, "family", f"duplicate fingerprint used by {other} and {family_id}")
            family_fingerprints[fingerprint] = family_id

    if set(family_by_id) != task_family_ids:
        _record_error(
            errors,
            "family",
            f"family registry/task mismatch: missing_records={sorted(task_family_ids - set(family_by_id))}, unused_records={sorted(set(family_by_id) - task_family_ids)}",
        )

    task_family_meta: dict[str, set[tuple[Any, Any, Any]]] = defaultdict(set)
    for task in tasks:
        if not isinstance(task, dict):
            continue
        family_id = task.get("task_family_id")
        family = family_by_id.get(family_id)
        if family is None:
            _record_error(errors, "family", f"task {task.get('task_id')} references unknown family {family_id!r}")
            continue
        metadata = (
            task.get("stage"),
            task.get("independence_group_id"),
            task.get("split_metadata", {}).get("family_fingerprint_sha256"),
        )
        task_family_meta[family_id].add(metadata)
        expected = (
            family.get("stage"),
            family.get("independence_group_id"),
            family.get("family_fingerprint_sha256"),
        )
        if metadata != expected:
            _record_error(errors, "family", f"metadata mismatch for task family {family_id}")
        expected_computed_hashes = task_fingerprints_by_family.get(family_id, set())
        if len(expected_computed_hashes) > 1:
            _record_error(errors, "family", f"family {family_id} contains inconsistent task definitions")

    # Family/independence groups are the split unit, never prompt wording.
    stage_family_ids: dict[str, set[str]] = defaultdict(set)
    stage_group_ids: dict[str, set[str]] = defaultdict(set)
    for family_id, family in family_by_id.items():
        stage = family.get("stage")
        group = family.get("independence_group_id")
        if isinstance(stage, str) and stage in ("A", "B"):
            stage_family_ids[stage].add(family_id)
            if isinstance(group, str):
                stage_group_ids[stage].add(group)
    if stage_family_ids["A"] & stage_family_ids["B"]:
        _record_error(errors, "split", "family IDs overlap between Stage A and Stage B")
    if stage_group_ids["A"] & stage_group_ids["B"]:
        _record_error(errors, "split", "independence groups overlap between Stage A and Stage B")

    # Stage B task bodies may not live in a manifest whose policy says the holdout
    # is not materialized or remains sealed/restricted from model developers.
    stage_b_policy = manifest.get("stage_b_policy", {})
    if not isinstance(stage_b_policy, dict):
        stage_b_policy = {}
    stage_b_count = actual_stage_counts.get("B", 0)
    if stage_b_count:
        if (
            stage_b_policy.get("state") != "released_for_confirmation"
            or stage_b_policy.get("visibility") != "released"
        ):
            _record_error(
                errors,
                "stage-b",
                "Stage B task bodies are present while the holdout is not explicitly released for confirmation",
            )

    # Frozen panels have exact quotas and completed validation/review evidence.
    frozen = manifest.get("frozen") is True or manifest.get("status") == "frozen" or require_frozen
    if frozen:
        if manifest.get("status") != "frozen" or manifest.get("frozen") is not True:
            _record_error(errors, "frozen", "both status='frozen' and frozen=true are required")
        if len(tasks) != 240 or actual_stage_counts.get("A", 0) != 120 or actual_stage_counts.get("B", 0) != 120:
            _record_error(errors, "frozen", "a frozen panel must contain exactly 240 tasks (120 per stage)")
        for stratum in sorted(EXPECTED_STRATA):
            for stage in ("A", "B"):
                actual = sum(1 for task in tasks if task.get("stage") == stage and task.get("stratum_id") == stratum)
                if actual != target:
                    _record_error(errors, "frozen", f"{stage}/{stratum} has {actual} tasks; exactly {target} required")
        for task in tasks:
            if not isinstance(task, dict):
                continue
            validation = task.get("validation")
            if not isinstance(validation, dict):
                validation = {}
            if (
                validation.get("status") != "validated"
                or validation.get("contract_check") != "pass"
                or validation.get("environment_check") != "pass"
                or validation.get("grader_check") != "pass"
                or validation.get("review_status") != "accepted"
            ):
                _record_error(errors, "frozen", f"{task.get('task_id')} has incomplete validation/review gates")
        if any(item.get("review_status") != "accepted" for item in families if isinstance(item, dict)):
            _record_error(errors, "frozen", "every task family must have review_status='accepted'")

    if require_frozen and not frozen:
        _record_error(errors, "frozen", "manifest is not frozen")

    return sorted(set(errors))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate the DHI-v1 ORBIT task manifest and cross-record integrity.")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST, help="Path to task_manifest.json")
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA, help="Path to task_manifest.schema.json")
    parser.add_argument("--repo-root", type=Path, default=REPO_ROOT_DEFAULT, help="Repository root for evidence/tool-registry checks")
    parser.add_argument("--require-frozen", action="store_true", help="Require the complete frozen 240-task panel")
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable validation report")
    args = parser.parse_args(argv)

    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        schema = json.loads(args.schema.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Cannot read manifest/schema: {exc}", file=sys.stderr)
        return 2

    errors = collect_manifest_errors(
        manifest,
        schema,
        repo_root=args.repo_root,
        require_frozen=args.require_frozen,
    )
    task_count = len(manifest.get("tasks", [])) if isinstance(manifest, dict) else 0
    report = {
        "valid": not errors,
        "task_count": task_count,
        "stage_counts": manifest.get("materialized_stage_counts", {}) if isinstance(manifest, dict) else {},
        "errors": errors,
    }
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif errors:
        print(f"Manifest INVALID: {len(errors)} error(s)")
        for error in errors:
            print(f"- {error}")
    else:
        print(
            f"Manifest valid: {task_count} task(s); "
            f"Stage A={report['stage_counts'].get('A', 0)}, "
            f"Stage B={report['stage_counts'].get('B', 0)}"
        )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
