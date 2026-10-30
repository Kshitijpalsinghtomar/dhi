"""Pinned, hash-verified initial workspaces for reproducible DHI-v1 tasks."""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any

MANIFEST_NAME = "fixture.manifest.json"
DEFAULT_MAX_FILE_BYTES = 10_000_000
DEFAULT_MAX_TOTAL_BYTES = 100_000_000


class FixtureError(Exception):
    """Invalid or unsafe benchmark fixture."""


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _safe_relative_path(value: Any) -> PurePosixPath:
    if not isinstance(value, str) or not value:
        raise FixtureError("fixture file path must be a non-empty string")
    if "\\" in value:
        raise FixtureError("fixture paths must use POSIX separators")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise FixtureError(f"fixture path escapes its root: {value}")
    if value == MANIFEST_NAME:
        raise FixtureError("manifest must not list itself as a fixture payload")
    return path


def validate_fixture(
    fixture_root: str | Path,
    *,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
) -> dict[str, Any]:
    """Validate manifest hashes, exact file inventory, and absence of symlinks."""
    root = Path(fixture_root).expanduser().resolve()
    manifest_path = root / MANIFEST_NAME
    if not root.is_dir() or manifest_path.is_symlink() or not manifest_path.is_file():
        raise FixtureError(f"fixture root or manifest is missing: {root}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise FixtureError(f"cannot read fixture manifest: {exc}") from exc

    fixture_id = manifest.get("fixture_id")
    version = manifest.get("version")
    files = manifest.get("files")
    if not isinstance(fixture_id, str) or not fixture_id.strip():
        raise FixtureError("manifest fixture_id is required")
    if not isinstance(version, str) or not version.strip():
        raise FixtureError("manifest version is required")
    if not isinstance(files, dict) or not files:
        raise FixtureError("manifest files must be a non-empty object")

    expected: dict[str, str] = {}
    for raw_path, digest in files.items():
        rel = _safe_relative_path(raw_path)
        if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise FixtureError(f"invalid SHA-256 digest for {raw_path}")
        expected[rel.as_posix()] = digest

    observed_paths: set[str] = set()
    total_bytes = 0
    ignored_generated_dirs = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".git", ".venv", "venv", "node_modules"}
    for current, directories, filenames in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        for directory in list(directories):
            candidate = current_path / directory
            if candidate.is_symlink():
                raise FixtureError(f"symlink directory is not allowed: {candidate.relative_to(root)}")
        directories[:] = [directory for directory in directories if directory not in ignored_generated_dirs]
        for filename in filenames:
            candidate = current_path / filename
            if candidate == manifest_path:
                continue
            if candidate.is_symlink() or not candidate.is_file():
                raise FixtureError(f"fixture payload must be a regular file: {candidate.relative_to(root)}")
            relative = candidate.relative_to(root).as_posix()
            observed_paths.add(relative)
            size = candidate.stat().st_size
            if size > max_file_bytes:
                raise FixtureError(f"fixture file exceeds size limit: {relative}")
            total_bytes += size
            if total_bytes > max_total_bytes:
                raise FixtureError("fixture exceeds total size limit")

    if observed_paths != set(expected):
        missing = sorted(set(expected) - observed_paths)
        extra = sorted(observed_paths - set(expected))
        raise FixtureError(f"fixture inventory mismatch; missing={missing}, extra={extra}")

    for relative, expected_hash in expected.items():
        actual_hash = sha256_file(root / relative)
        if actual_hash != expected_hash:
            raise FixtureError(f"SHA-256 mismatch for fixture file: {relative}")

    return {
        "fixture_id": fixture_id,
        "version": version,
        "files": dict(sorted(expected.items())),
        "file_count": len(expected),
        "total_bytes": total_bytes,
    }


def materialize_fixture(
    fixture_root: str | Path,
    destination: str | Path,
    *,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
) -> dict[str, Any]:
    """Copy a validated fixture into a new/empty workspace without deleting data.

    The destination must be absent or empty. This deliberately avoids a
    destructive reset that could erase a user's existing files.
    """
    source = Path(fixture_root).expanduser().resolve()
    target = Path(destination).expanduser().resolve()
    try:
        target.relative_to(source)
        raise FixtureError("destination must not be inside the fixture source")
    except ValueError:
        pass
    try:
        source.relative_to(target)
        raise FixtureError("fixture source must not be inside the destination")
    except ValueError:
        pass

    manifest = validate_fixture(source, max_file_bytes=max_file_bytes, max_total_bytes=max_total_bytes)
    if target.exists():
        if target.is_symlink() or not target.is_dir():
            raise FileExistsError(f"destination exists and is not a regular directory: {target}")
        if any(target.iterdir()):
            raise FileExistsError(f"destination must be empty; refusing to delete or overwrite: {target}")
    else:
        target.mkdir(parents=True, exist_ok=False)

    for relative in manifest["files"]:
        source_file = source / relative
        destination_file = target / relative
        destination_file.parent.mkdir(parents=True, exist_ok=True)
        payload = source_file.read_bytes()
        temporary: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(dir=destination_file.parent, prefix=f".{destination_file.name}.", delete=False) as handle:
                temporary = Path(handle.name)
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, destination_file)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink(missing_ok=True)

    copied = {relative: sha256_file(target / relative) for relative in manifest["files"]}
    if copied != manifest["files"]:
        raise FixtureError("materialized workspace hash verification failed")
    return {**manifest, "destination": str(target), "verified": True}
