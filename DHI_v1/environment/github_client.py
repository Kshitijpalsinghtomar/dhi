"""Credential-gated, task-policy-compatible GitHub REST adapter.

Only six registered capabilities are implemented. Reads are exposed when a
runtime token exists. Writes additionally require an explicit write flag and a
non-empty repository allowlist; task-specific write authorization remains the
responsibility of PreparedPluginExecution.
"""
from __future__ import annotations

import base64
import binascii
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any
from urllib.parse import quote, urlsplit


API_ROOT = "https://api.github.com"
API_HOST = "api.github.com"
ALLOWED_FETCH_HOSTS = frozenset({API_HOST, "github.com", "raw.githubusercontent.com"})

FETCH_FILE_TOOL_ID = "mcp__GitHub__fetch_file"
FETCH_TOOL_ID = "mcp__GitHub__fetch"
COMPARE_COMMITS_TOOL_ID = "mcp__GitHub__compare_commits"
CREATE_BRANCH_TOOL_ID = "mcp__GitHub__create_branch"
CREATE_FILE_TOOL_ID = "mcp__GitHub__create_file"
UPDATE_FILE_TOOL_ID = "mcp__GitHub__update_file"

_READ_IDS = (FETCH_FILE_TOOL_ID, FETCH_TOOL_ID, COMPARE_COMMITS_TOOL_ID)
_WRITE_IDS = (CREATE_BRANCH_TOOL_ID, CREATE_FILE_TOOL_ID, UPDATE_FILE_TOOL_ID)

_SHA_SCHEMA = {"type": "string", "pattern": "^[a-fA-F0-9]{40}$"}
_REPO_SCHEMA = {"type": "string", "pattern": "^[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}$"}
_PATH_SCHEMA = {"type": "string", "minLength": 1, "maxLength": 1000}
_MESSAGE_SCHEMA = {"type": "string", "minLength": 1, "maxLength": 500}
_BRANCH_SCHEMA = {"type": "string", "minLength": 1, "maxLength": 240}

GITHUB_TOOL_CATALOGUE: list[dict[str, Any]] = [
    {
        "tool_id": FETCH_FILE_TOOL_ID,
        "name": "GitHub fetch file",
        "description": "Fetch file content by exact repository path and optional pinned ref. Read-only.",
        "tags": ["github", "repository", "file", "read", "blob", "contents"],
        "input_schema": {
            "type": "object",
            "required": ["repository_full_name", "path"],
            "properties": {
                "repository_full_name": _REPO_SCHEMA,
                "path": _PATH_SCHEMA,
                "ref": {"type": "string", "minLength": 1, "maxLength": 255},
                "encoding": {"type": "string", "enum": ["utf-8", "base64"]},
                "start_line": {"type": "integer", "minimum": 1},
                "end_line": {"type": "integer", "minimum": 1},
            },
            "additionalProperties": False,
        },
        "side_effect_class": "read_only",
        "permission_scope": "github_repository_read",
        "requires_handler": True,
        "requires_explicit_task_allowlist": True,
        "preconditions": ["GITHUB_TOKEN is available in the runtime"],
        "cost_class": "github_api_quota",
        "reversible": True,
    },
    {
        "tool_id": FETCH_TOOL_ID,
        "name": "GitHub fetch",
        "description": "Fetch approved GitHub repository, file, directory, branch, commit, compare, or Git reference resources. GET only.",
        "tags": ["github", "fetch", "repository", "directory", "branches", "commits", "compare", "read"],
        "input_schema": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string", "minLength": 1, "maxLength": 4000},
            },
            "additionalProperties": False,
        },
        "side_effect_class": "read_only",
        "permission_scope": "github_repository_read",
        "requires_handler": True,
        "requires_explicit_task_allowlist": True,
        "preconditions": ["GITHUB_TOKEN is available in the runtime"],
        "cost_class": "github_api_quota",
        "reversible": True,
    },
    {
        "tool_id": COMPARE_COMMITS_TOOL_ID,
        "name": "GitHub compare commits",
        "description": "Compare two commits or refs and return a compact per-file diff summary. Read-only.",
        "tags": ["github", "compare", "commits", "diff", "branches", "read"],
        "input_schema": {
            "type": "object",
            "required": ["repo_full_name", "base", "head"],
            "properties": {
                "repo_full_name": _REPO_SCHEMA,
                "base": {"type": "string", "minLength": 1, "maxLength": 255},
                "head": {"type": "string", "minLength": 1, "maxLength": 255},
            },
            "additionalProperties": False,
        },
        "side_effect_class": "read_only",
        "permission_scope": "github_repository_read",
        "requires_handler": True,
        "requires_explicit_task_allowlist": True,
        "preconditions": ["GITHUB_TOKEN is available in the runtime"],
        "cost_class": "github_api_quota",
        "reversible": True,
    },
    {
        "tool_id": CREATE_BRANCH_TOOL_ID,
        "name": "GitHub create branch",
        "description": "Create one branch at an exact commit SHA or base ref. Sandbox write; explicit task guard required.",
        "tags": ["github", "branch", "create", "write", "sandbox"],
        "input_schema": {
            "type": "object",
            "required": ["repository_full_name", "branch_name"],
            "properties": {
                "repository_full_name": _REPO_SCHEMA,
                "branch_name": _BRANCH_SCHEMA,
                "sha": _SHA_SCHEMA,
                "base_ref": {"type": "string", "minLength": 1, "maxLength": 255},
            },
            "oneOf": [
                {"required": ["sha"], "not": {"required": ["base_ref"]}},
                {"required": ["base_ref"], "not": {"required": ["sha"]}},
            ],
            "additionalProperties": False,
        },
        "side_effect_class": "sandbox_write",
        "permission_scope": "github_branch_write",
        "requires_handler": True,
        "requires_explicit_task_allowlist": True,
        "preconditions": ["GITHUB_TOKEN and explicit write configuration are available"],
        "cost_class": "github_api_quota",
        "reversible": True,
    },
    {
        "tool_id": CREATE_FILE_TOOL_ID,
        "name": "GitHub create file",
        "description": "Create a new UTF-8 file at an explicit path, optionally on a named branch. Sandbox write; explicit task guard required.",
        "tags": ["github", "file", "create", "write", "sandbox"],
        "input_schema": {
            "type": "object",
            "required": ["repository_full_name", "path", "content", "message"],
            "properties": {
                "repository_full_name": _REPO_SCHEMA,
                "path": _PATH_SCHEMA,
                "content": {"type": "string", "maxLength": 1000000},
                "message": _MESSAGE_SCHEMA,
                "branch": _BRANCH_SCHEMA,
            },
            "additionalProperties": False,
        },
        "side_effect_class": "sandbox_write",
        "permission_scope": "github_contents_write",
        "requires_handler": True,
        "requires_explicit_task_allowlist": True,
        "preconditions": ["GITHUB_TOKEN and explicit write configuration are available"],
        "cost_class": "github_api_quota",
        "reversible": True,
    },
    {
        "tool_id": UPDATE_FILE_TOOL_ID,
        "name": "GitHub update file",
        "description": "Replace an existing UTF-8 file using its current blob SHA. Sandbox write; explicit task guard required.",
        "tags": ["github", "file", "update", "replace", "write", "blob", "sha", "sandbox"],
        "input_schema": {
            "type": "object",
            "required": ["repository_full_name", "path", "content", "message", "sha"],
            "properties": {
                "repository_full_name": _REPO_SCHEMA,
                "path": _PATH_SCHEMA,
                "content": {"type": "string", "maxLength": 1000000},
                "message": _MESSAGE_SCHEMA,
                "sha": _SHA_SCHEMA,
                "branch": _BRANCH_SCHEMA,
            },
            "additionalProperties": False,
        },
        "side_effect_class": "sandbox_write",
        "permission_scope": "github_contents_write",
        "requires_handler": True,
        "requires_explicit_task_allowlist": True,
        "preconditions": ["GITHUB_TOKEN and explicit write configuration are available"],
        "cost_class": "github_api_quota",
        "reversible": True,
    },
]


class GitHubClientError(ValueError):
    """Safe, credential-redacted GitHub request or response error."""


def _validate_object(arguments: Any, schema: dict[str, Any], label: str) -> dict[str, Any]:
    if not isinstance(arguments, dict):
        raise GitHubClientError(f"{label} arguments must be an object")
    required = schema.get("required", [])
    missing = sorted(set(required) - set(arguments))
    if missing:
        raise GitHubClientError("missing required argument(s): " + ", ".join(missing))
    properties = schema.get("properties", {})
    unexpected = sorted(set(arguments) - set(properties))
    if unexpected:
        raise GitHubClientError("unexpected argument(s): " + ", ".join(unexpected))
    for key, value in arguments.items():
        rule = properties[key]
        expected = rule.get("type")
        valid = (
            (expected == "string" and isinstance(value, str))
            or (expected == "integer" and isinstance(value, int) and not isinstance(value, bool))
        )
        if not valid:
            raise GitHubClientError(f"argument {key!r} must be {expected}")
        if expected == "string":
            if len(value) < rule.get("minLength", 0) or len(value) > rule.get("maxLength", 10**9):
                raise GitHubClientError(f"argument {key!r} has an invalid length")
            if "pattern" in rule and not re.fullmatch(rule["pattern"], value):
                raise GitHubClientError(f"argument {key!r} has an invalid format")
            if "enum" in rule and value not in rule["enum"]:
                raise GitHubClientError(f"argument {key!r} must be one of {rule['enum']!r}")
        if expected == "integer":
            if value < rule.get("minimum", value) or value > rule.get("maximum", value):
                raise GitHubClientError(f"argument {key!r} is outside the allowed range")
    return dict(arguments)


def _validate_repo(value: Any) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}/[A-Za-z0-9_.-]{1,100}", value):
        raise GitHubClientError("repository_full_name must use owner/repository form")
    owner, repo = value.split("/", 1)
    if owner in {".", ".."} or repo in {".", ".."}:
        raise GitHubClientError("repository_full_name is invalid")
    return value


def _validate_repo_path(value: Any) -> str:
    if not isinstance(value, str) or not value or len(value) > 1000:
        raise GitHubClientError("path must be repository-relative")
    if value.startswith("/") or "\\" in value or "\x00" in value:
        raise GitHubClientError("path must be repository-relative")
    parts = value.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise GitHubClientError("path must be repository-relative")
    return value


def _api_path(repo: str, suffix: str) -> str:
    owner, name = _validate_repo(repo).split("/", 1)
    return f"/repos/{quote(owner, safe='')}/{quote(name, safe='')}{suffix}"


def _safe_ref(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value or len(value) > 255:
        raise GitHubClientError(f"{label} must be a non-empty ref")
    if value.startswith("-") or value.startswith("/") or value.endswith("/") or ".." in value or "@{" in value:
        raise GitHubClientError(f"{label} is not a valid Git ref")
    if any(ord(char) < 32 or char in " ~^:?*[\\\\]" for char in value):
        raise GitHubClientError(f"{label} is not a valid Git ref")
    return value


class GitHubReadWriteClient:
    """Small bounded GitHub REST client with explicit write gates."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        timeout_seconds: float = 20.0,
        max_response_bytes: int = 2_000_000,
        enable_writes: bool = False,
        allowed_repositories: set[str] | frozenset[str] | None = None,
    ) -> None:
        token = api_key if api_key is not None else os.environ.get("GITHUB_TOKEN", "")
        if not isinstance(token, str) or not token.strip():
            raise GitHubClientError("GITHUB_TOKEN is required")
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) or not 1 <= timeout_seconds <= 180:
            raise GitHubClientError("timeout_seconds must be between 1 and 180")
        if isinstance(max_response_bytes, bool) or not isinstance(max_response_bytes, int) or not 1 <= max_response_bytes <= 25_000_000:
            raise GitHubClientError("max_response_bytes must be between 1 and 25000000")
        if not isinstance(enable_writes, bool):
            raise GitHubClientError("enable_writes must be boolean")
        repos = set()
        for repo in allowed_repositories or set():
            repos.add(_validate_repo(repo))
        self._token = token.strip()
        self.timeout_seconds = float(timeout_seconds)
        self.max_response_bytes = max_response_bytes
        self.enable_writes = enable_writes and bool(repos)
        self.allowed_repositories = frozenset(repos)
        self._opener = None

    def _request(
        self,
        *,
        method: str,
        path: str,
        query: dict[str, Any] | None = None,
        body: dict[str, Any] | None = None,
        authenticated: bool = True,
    ) -> tuple[Any, str]:
        if not path.startswith("/") or path.startswith("//") or "\\" in path:
            raise GitHubClientError("invalid internal GitHub API path")
        url = API_ROOT + path
        if query:
            url += "?" + urllib.parse.urlencode(query, doseq=True)
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "DHI-ORBIT-GitHub-Adapter/0.1",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if authenticated:
            headers["Authorization"] = f"Bearer {self._token}"
        data = None
        if body is not None:
            data = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            # build_opener gives tests a deterministic injection seam. There are
            # no retry handlers; a request is attempted once.
            opener = self._opener or urllib.request.build_opener()
            with opener.open(request, timeout=self.timeout_seconds) as response:
                final_url = response.geturl()
                parsed_final = urlsplit(final_url)
                if parsed_final.scheme != "https" or parsed_final.hostname != API_HOST:
                    raise GitHubClientError("GitHub response redirected outside the approved API host")
                raw = response.read(self.max_response_bytes + 1)
                status = getattr(response, "status", 200)
        except GitHubClientError:
            raise
        except urllib.error.HTTPError as exc:
            # Do not include GitHub's body: it may echo submitted credentials,
            # private repository data, or attacker-controlled content.
            raise GitHubClientError(f"GitHub HTTP request failed with status {exc.code}") from None
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise GitHubClientError(f"GitHub transport failure: {type(exc).__name__}") from None
        except Exception as exc:
            # urllib's opener may raise provider-specific transport exceptions.
            raise GitHubClientError(f"GitHub transport failure: {type(exc).__name__}") from None
        if len(raw) > self.max_response_bytes:
            raise GitHubClientError(f"GitHub response exceeds {self.max_response_bytes} byte limit")
        if not raw:
            raise GitHubClientError(f"GitHub returned an empty response (HTTP {status})")
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            raise GitHubClientError("GitHub response is not valid UTF-8") from None
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            return text, url
        return payload, url

    def _write_repo(self, value: Any) -> str:
        repo = _validate_repo(value)
        if not self.enable_writes:
            raise GitHubClientError("GitHub write operations are disabled")
        if repo not in self.allowed_repositories:
            raise GitHubClientError("repository is not in the configured write allowlist")
        return repo

    def fetch_file(self, arguments: dict[str, Any]) -> dict[str, Any]:
        args = _validate_object(arguments, GITHUB_TOOL_CATALOGUE[0]["input_schema"], "fetch_file")
        repo = _validate_repo(args["repository_full_name"])
        path = _validate_repo_path(args["path"])
        query = {}
        if "ref" in args:
            query["ref"] = _safe_ref(args["ref"], "ref")
        suffix = "/contents/" + quote(path, safe="/")
        payload, request_url = self._request(
            method="GET", path=_api_path(repo, suffix), query=query or None
        )
        if not isinstance(payload, dict):
            raise GitHubClientError("GitHub fetch_file expected a file object")
        if payload.get("type") not in (None, "file"):
            raise GitHubClientError("GitHub fetch_file path is not a file")
        blob_sha = payload.get("sha")
        encoded = payload.get("content")
        if not isinstance(blob_sha, str) or not re.fullmatch(r"[a-f0-9]{40}", blob_sha):
            raise GitHubClientError("GitHub file response is missing a valid blob SHA")
        if not isinstance(encoded, str):
            raise GitHubClientError("GitHub file response is missing Base64 content")
        compact = "".join(encoded.split())
        try:
            decoded = base64.b64decode(compact, validate=True)
        except (binascii.Error, ValueError):
            raise GitHubClientError("GitHub file response contains invalid Base64") from None
        encoding = args.get("encoding", "utf-8")
        if encoding == "base64":
            content = base64.b64encode(decoded).decode("ascii")
        else:
            try:
                content = decoded.decode("utf-8")
            except UnicodeDecodeError:
                raise GitHubClientError("GitHub file is not valid UTF-8; request base64 encoding") from None
        start, end = args.get("start_line"), args.get("end_line")
        if start is not None or end is not None:
            if not isinstance(content, str) or encoding == "base64":
                raise GitHubClientError("line ranges require encoding=utf-8")
            lines = content.splitlines()
            start_index = (start or 1) - 1
            end_index = end if end is not None else len(lines)
            if end_index < start_index + 1:
                raise GitHubClientError("end_line must be greater than or equal to start_line")
            content = "\n".join(lines[start_index:end_index])
        display_url = payload.get("html_url")
        if not isinstance(display_url, str) or not display_url.startswith("https://github.com/"):
            display_url = f"https://github.com/{repo}/blob/{query.get('ref', 'HEAD')}/{path}"
        title = payload.get("name")
        if not isinstance(title, str):
            title = path.rsplit("/", 1)[-1]
        return {
            "content": content,
            "encoding": encoding,
            "sha": blob_sha,
            "display_url": display_url,
            "display_title": title,
        }

    def fetch(self, arguments: dict[str, Any]) -> dict[str, Any]:
        args = _validate_object(arguments, GITHUB_TOOL_CATALOGUE[1]["input_schema"], "fetch")
        raw_url = args["url"]
        parsed = urlsplit(raw_url)
        host = (parsed.hostname or "").casefold()
        if parsed.scheme != "https" or host not in ALLOWED_FETCH_HOSTS:
            raise GitHubClientError("unsupported GitHub URL host or scheme")
        if parsed.username is not None or parsed.password is not None or parsed.fragment:
            raise GitHubClientError("GitHub URL must not contain credentials or fragments")
        if parsed.port not in (None, 443):
            raise GitHubClientError("GitHub URL must use the standard HTTPS port")
        if any(part in {".", ".."} for part in parsed.path.split("/")):
            raise GitHubClientError("GitHub URL contains an unsafe path")
        query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=True)
        allowed_query_keys = {"ref", "per_page", "page", "state", "direction", "sort"}
        if any(key not in allowed_query_keys for key, _ in query_pairs):
            raise GitHubClientError("GitHub URL contains an unsupported query parameter")
        if host == "github.com":
            parts = parsed.path.strip("/").split("/")
            if len(parts) >= 5 and parts[2] in {"blob", "tree"}:
                owner, repo, mode = parts[:3]
                ref = parts[3]
                rest = "/".join(parts[4:])
                suffix = "/contents" + ("/" + quote(rest, safe="/") if rest else "")
                query_pairs = [("ref", ref)] + query_pairs
                path = _api_path(f"{owner}/{repo}", suffix)
                host = API_HOST
            elif len(parts) == 2:
                path = _api_path("/".join(parts), "")
            else:
                raise GitHubClientError("unsupported GitHub web URL path")
        elif host == "raw.githubusercontent.com":
            parts = parsed.path.strip("/").split("/")
            if len(parts) < 4:
                raise GitHubClientError("unsupported raw GitHub URL path")
            owner, repo, ref = parts[:3]
            rest = "/".join(parts[3:])
            path = _api_path(f"{owner}/{repo}", "/contents/" + quote(rest, safe="/"))
            query_pairs = [("ref", ref)] + query_pairs
        else:
            path = parsed.path
            # Allow only public repository REST resource families. Exclude user,
            # organization, actions secrets, and any unlisted sensitive APIs.
            match = re.match(r"^/repos/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)(/.*)?$", path)
            if not match:
                raise GitHubClientError("unsupported GitHub API path")
            tail = match.group(3) or ""
            allowed = (
                tail == ""
                or tail == "/branches"
                or tail.startswith("/contents")
                or re.fullmatch(r"/commits/[^/]+", tail) is not None
                or re.fullmatch(r"/compare/[^/]+\.\.\.[^/]+", tail) is not None
                or re.fullmatch(r"/git/refs(?:/heads(?:/.*)?)?", tail) is not None
                or re.fullmatch(r"/git/ref/heads/.*", tail) is not None
            )
            if not allowed:
                raise GitHubClientError("unsupported GitHub API path")
        query: dict[str, Any] | None = None
        if query_pairs:
            query = {}
            for key, value in query_pairs:
                if key in query and key != "state":
                    raise GitHubClientError("duplicate GitHub query parameter")
                query[key] = value
        authenticated = host == API_HOST
        if host != API_HOST:
            # Redirect-free public raw text retrieval. The bearer token is never
            # sent to github.com or raw.githubusercontent.com.
            url = urllib.parse.urlunsplit(("https", host, parsed.path, parsed.query, ""))
            try:
                request = urllib.request.Request(
                    url, headers={"Accept": "text/plain", "User-Agent": "DHI-ORBIT-GitHub-Adapter/0.1"}
                )
                opener = self._opener or urllib.request.build_opener()
                with opener.open(request, timeout=self.timeout_seconds) as response:
                    if urlsplit(response.geturl()).hostname != host:
                        raise GitHubClientError("GitHub response redirected outside the requested host")
                    raw = response.read(self.max_response_bytes + 1)
                    status = getattr(response, "status", 200)
                if len(raw) > self.max_response_bytes:
                    raise GitHubClientError(f"GitHub response exceeds {self.max_response_bytes} byte limit")
                text = raw.decode("utf-8")
                return {"content": text, "title": None, "modified_date": None, "url": url}
            except GitHubClientError:
                raise
            except Exception as exc:
                raise GitHubClientError(f"GitHub transport failure: {type(exc).__name__}") from None
        payload, request_url = self._request(method="GET", path=path, query=query, authenticated=authenticated)
        if isinstance(payload, str):
            content = payload
        else:
            content = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        title = None
        if isinstance(payload, dict):
            title = payload.get("name") or payload.get("full_name")
        return {"content": content, "title": title, "modified_date": None, "url": request_url}

    def compare_commits(self, arguments: dict[str, Any]) -> dict[str, Any]:
        args = _validate_object(arguments, GITHUB_TOOL_CATALOGUE[2]["input_schema"], "compare_commits")
        repo = _validate_repo(args["repo_full_name"])
        base = _safe_ref(args["base"], "base")
        head = _safe_ref(args["head"], "head")
        suffix = f"/compare/{quote(base, safe='') }...{quote(head, safe='')}"
        payload, _ = self._request(method="GET", path=_api_path(repo, suffix))
        if not isinstance(payload, dict):
            raise GitHubClientError("GitHub compare response must be an object")
        files = payload.get("files") or []
        if not isinstance(files, list):
            raise GitHubClientError("GitHub compare response files must be an array")
        compact_files = []
        for item in files:
            if not isinstance(item, dict) or not isinstance(item.get("filename"), str):
                continue
            compact_files.append({
                key: item[key] for key in (
                    "filename", "status", "additions", "deletions", "changes", "previous_filename"
                ) if key in item
            })
        result = {
            "repository_full_name": repo,
            "base": base,
            "head": head,
            "files": compact_files,
        }
        for key in ("status", "ahead_by", "behind_by", "total_commits", "too_large", "base_commit", "merge_base_commit"):
            if key in payload:
                result[key] = payload[key]
        return result

    def create_branch(self, arguments: dict[str, Any]) -> dict[str, Any]:
        args = _validate_object(arguments, GITHUB_TOOL_CATALOGUE[3]["input_schema"], "create_branch")
        repo = self._write_repo(args["repository_full_name"])
        branch = _safe_ref(args["branch_name"], "branch_name")
        sha = args.get("sha")
        base_ref = args.get("base_ref")
        if (sha is None) == (base_ref is None):
            raise GitHubClientError("provide exactly one of sha or base_ref")
        if sha is not None and not re.fullmatch(r"[a-fA-F0-9]{40}", sha):
            raise GitHubClientError("sha must be a 40-character commit SHA")
        if base_ref is not None:
            ref = _safe_ref(base_ref, "base_ref")
            resolved, _ = self._request(
                method="GET", path=_api_path(repo, "/commits/" + quote(ref, safe=""))
            )
            sha = resolved.get("sha") if isinstance(resolved, dict) else None
            if not isinstance(sha, str) or not re.fullmatch(r"[a-f0-9]{40}", sha):
                raise GitHubClientError("GitHub base ref did not resolve to a commit SHA")
        payload, _ = self._request(
            method="POST",
            path=_api_path(repo, "/git/refs"),
            body={"ref": "refs/heads/" + branch, "sha": sha},
        )
        ref_value = payload.get("ref") if isinstance(payload, dict) else None
        if ref_value != "refs/heads/" + branch:
            raise GitHubClientError("GitHub did not confirm the requested branch ref")
        return {"branch": branch}

    def create_file(self, arguments: dict[str, Any]) -> dict[str, Any]:
        args = _validate_object(arguments, GITHUB_TOOL_CATALOGUE[4]["input_schema"], "create_file")
        repo = self._write_repo(args["repository_full_name"])
        path = _validate_repo_path(args["path"])
        content = args["content"]
        if len(content.encode("utf-8")) > 1_000_000:
            raise GitHubClientError("file content exceeds 1000000 UTF-8 bytes")
        body = {
            "message": args["message"],
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
        }
        if "branch" in args:
            body["branch"] = _safe_ref(args["branch"], "branch")
        payload, _ = self._request(
            method="PUT", path=_api_path(repo, "/contents/" + quote(path, safe="/")), body=body
        )
        commit = payload.get("commit") if isinstance(payload, dict) else None
        commit_sha = commit.get("sha") if isinstance(commit, dict) else None
        if not isinstance(commit_sha, str) or not re.fullmatch(r"[a-f0-9]{40}", commit_sha):
            raise GitHubClientError("GitHub create_file response is missing a commit SHA")
        return {"commit_sha": commit_sha}

    def update_file(self, arguments: dict[str, Any]) -> dict[str, Any]:
        args = _validate_object(arguments, GITHUB_TOOL_CATALOGUE[5]["input_schema"], "update_file")
        repo = self._write_repo(args["repository_full_name"])
        path = _validate_repo_path(args["path"])
        if not re.fullmatch(r"[a-fA-F0-9]{40}", args["sha"]):
            raise GitHubClientError("sha must be a 40-character blob SHA")
        content = args["content"]
        if len(content.encode("utf-8")) > 1_000_000:
            raise GitHubClientError("file content exceeds 1000000 UTF-8 bytes")
        body = {
            "message": args["message"],
            "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
            "sha": args["sha"],
        }
        if "branch" in args:
            body["branch"] = _safe_ref(args["branch"], "branch")
        payload, _ = self._request(
            method="PUT", path=_api_path(repo, "/contents/" + quote(path, safe="/")), body=body
        )
        commit = payload.get("commit") if isinstance(payload, dict) else None
        content_obj = payload.get("content") if isinstance(payload, dict) else None
        commit_sha = commit.get("sha") if isinstance(commit, dict) else None
        content_sha = content_obj.get("sha") if isinstance(content_obj, dict) else None
        if not isinstance(commit_sha, str) or not re.fullmatch(r"[a-f0-9]{40}", commit_sha):
            raise GitHubClientError("GitHub update_file response is missing a commit SHA")
        if not isinstance(content_sha, str) or not re.fullmatch(r"[a-f0-9]{40}", content_sha):
            raise GitHubClientError("GitHub update_file response is missing a content SHA")
        return {"commit_sha": commit_sha, "content_sha": content_sha}

    def tool_handlers(self) -> dict[str, Any]:
        handlers = {
            FETCH_FILE_TOOL_ID: self.fetch_file,
            FETCH_TOOL_ID: self.fetch,
            COMPARE_COMMITS_TOOL_ID: self.compare_commits,
        }
        if self.enable_writes:
            handlers.update({
                CREATE_BRANCH_TOOL_ID: self.create_branch,
                CREATE_FILE_TOOL_ID: self.create_file,
                UPDATE_FILE_TOOL_ID: self.update_file,
            })
        return handlers


def _parse_repository_allowlist(value: str) -> set[str]:
    repositories: set[str] = set()
    for item in value.split(","):
        item = item.strip()
        if item:
            repositories.add(_validate_repo(item))
    return repositories


def github_tool_handlers_from_env() -> dict[str, Any]:
    """Return read handlers with a token; expose writes only with two runtime gates."""
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        return {}
    repositories = _parse_repository_allowlist(os.environ.get("GITHUB_ALLOWED_REPOSITORIES", ""))
    enabled = os.environ.get("DHI_GITHUB_WRITES_ENABLED", "").strip().casefold() == "true"
    client = GitHubReadWriteClient(
        api_key=token,
        enable_writes=enabled and bool(repositories),
        allowed_repositories=repositories,
    )
    return client.tool_handlers()


def github_plugin_bundle_from_env() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Return pinned canonical schemas and credential-gated callable handlers."""
    schemas: dict[str, dict[str, Any]] = {}
    for item in GITHUB_TOOL_CATALOGUE:
        tool_id = item["tool_id"]
        if tool_id in schemas:
            raise GitHubClientError(f"duplicate GitHub catalogue tool ID: {tool_id}")
        schemas[tool_id] = json.loads(json.dumps(item["input_schema"]))
    return schemas, github_tool_handlers_from_env()
