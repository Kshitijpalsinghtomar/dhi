from __future__ import annotations

import base64
import json
import os
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import pytest

from DHI_v1.environment.github_client import (
    COMPARE_COMMITS_TOOL_ID,
    CREATE_BRANCH_TOOL_ID,
    CREATE_FILE_TOOL_ID,
    FETCH_FILE_TOOL_ID,
    FETCH_TOOL_ID,
    UPDATE_FILE_TOOL_ID,
    GitHubClientError,
    GitHubReadWriteClient,
    GITHUB_TOOL_CATALOGUE,
    github_plugin_bundle_from_env,
)


TOKEN = "github-unit-test-secret"
REPO = "acme/northstar"
BASE_SHA = "a" * 40
COMMIT_SHA = "b" * 40
BLOB_SHA = "c" * 40


class FakeHTTPResponse:
    def __init__(self, payload, status=200):
        self.payload = (
            payload if isinstance(payload, bytes)
            else json.dumps(payload).encode("utf-8")
        )
        self.status = status
        self.closed = False

    def read(self, size=-1):
        if size is None or size < 0:
            return self.payload
        return self.payload[:size]

    def geturl(self):
        return "https://api.github.com/fake"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.closed = True
        return False


class ScriptedOpener:
    def __init__(self, responses):
        self.responses = list(responses)
        self.requests = []
        self.timeouts = []

    def open(self, request, timeout=None):
        self.requests.append(request)
        self.timeouts.append(timeout)
        if not self.responses:
            raise AssertionError("unexpected outbound GitHub request")
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


def _patch_opener(opener):
    return patch("urllib.request.build_opener", return_value=opener)


def _file_payload(text="Northstar policy", sha=BLOB_SHA):
    return {
        "name": "TASK_POLICY.md",
        "path": "docs/TASK_POLICY.md",
        "sha": sha,
        "encoding": "base64",
        "content": base64.b64encode(text.encode("utf-8")).decode("ascii"),
        "html_url": f"https://github.com/{REPO}/blob/main/docs/TASK_POLICY.md",
    }


def _write_env(monkeypatch, *, token=TOKEN, enabled="true", repositories=REPO):
    monkeypatch.setenv("GITHUB_TOKEN", token)
    monkeypatch.setenv("DHI_GITHUB_WRITES_ENABLED", enabled)
    if repositories is None:
        monkeypatch.delenv("GITHUB_ALLOWED_REPOSITORIES", raising=False)
    else:
        monkeypatch.setenv("GITHUB_ALLOWED_REPOSITORIES", repositories)


def test_github_catalogue_exposes_exact_canonical_ids_and_closed_object_schemas(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    schemas, handlers = github_plugin_bundle_from_env()

    expected = {
        FETCH_FILE_TOOL_ID, FETCH_TOOL_ID, COMPARE_COMMITS_TOOL_ID,
        CREATE_BRANCH_TOOL_ID, CREATE_FILE_TOOL_ID, UPDATE_FILE_TOOL_ID,
    }
    assert {item["tool_id"] for item in GITHUB_TOOL_CATALOGUE} == expected
    assert set(schemas) == expected
    assert handlers == {}
    assert all(schema["type"] == "object" for schema in schemas.values())
    assert all(schema["additionalProperties"] is False for schema in schemas.values())


def test_no_token_exposes_schemas_but_never_exposes_handlers(monkeypatch):
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    monkeypatch.setenv("DHI_GITHUB_WRITES_ENABLED", "true")
    monkeypatch.setenv("GITHUB_ALLOWED_REPOSITORIES", REPO)

    schemas, handlers = github_plugin_bundle_from_env()

    assert set(schemas) == {
        FETCH_FILE_TOOL_ID, FETCH_TOOL_ID, COMPARE_COMMITS_TOOL_ID,
        CREATE_BRANCH_TOOL_ID, CREATE_FILE_TOOL_ID, UPDATE_FILE_TOOL_ID,
    }
    assert handlers == {}


def test_token_without_explicit_write_flag_exposes_only_read_handlers(monkeypatch):
    monkeypatch.setenv("GITHUB_TOKEN", TOKEN)
    monkeypatch.delenv("DHI_GITHUB_WRITES_ENABLED", raising=False)
    monkeypatch.setenv("GITHUB_ALLOWED_REPOSITORIES", REPO)

    schemas, handlers = github_plugin_bundle_from_env()

    assert set(handlers) == {
        FETCH_FILE_TOOL_ID, FETCH_TOOL_ID, COMPARE_COMMITS_TOOL_ID
    }
    assert set(schemas) == {item["tool_id"] for item in GITHUB_TOOL_CATALOGUE}


def test_write_handlers_require_both_explicit_flag_and_repository_allowlist(monkeypatch):
    _write_env(monkeypatch, enabled="true", repositories=REPO)
    schemas, handlers = github_plugin_bundle_from_env()

    assert set(handlers) == {
        FETCH_FILE_TOOL_ID, FETCH_TOOL_ID, COMPARE_COMMITS_TOOL_ID,
        CREATE_BRANCH_TOOL_ID, CREATE_FILE_TOOL_ID, UPDATE_FILE_TOOL_ID,
    }

    monkeypatch.delenv("GITHUB_ALLOWED_REPOSITORIES", raising=False)
    _, no_allowlist = github_plugin_bundle_from_env()
    assert set(no_allowlist) == {
        FETCH_FILE_TOOL_ID, FETCH_TOOL_ID, COMPARE_COMMITS_TOOL_ID
    }


def test_fetch_file_uses_exact_path_ref_headers_and_decodes_base64_without_leaking_token():
    client = GitHubReadWriteClient(api_key=TOKEN)
    opener = ScriptedOpener([FakeHTTPResponse(_file_payload("line one\nline two\nline three"))])
    arguments = {
        "repository_full_name": REPO,
        "path": "docs/TASK_POLICY.md",
        "ref": "release/1",
        "encoding": "utf-8",
        "start_line": 2,
        "end_line": 2,
    }

    with _patch_opener(opener):
        result = client.fetch_file(arguments)

    request = opener.requests[0]
    parsed = urlsplit(request.full_url)
    assert parsed.scheme == "https"
    assert parsed.netloc == "api.github.com"
    assert parsed.path == f"/repos/{REPO}/contents/docs/TASK_POLICY.md"
    assert parse_qs(parsed.query) == {"ref": ["release/1"]}
    assert request.get_method() == "GET"
    assert request.get_header("Authorization") == f"Bearer {TOKEN}"
    assert request.get_header("Accept") == "application/vnd.github+json"
    assert request.get_header("X-github-api-version") == "2022-11-28"
    assert result == {
        "content": "line two",
        "encoding": "utf-8",
        "sha": BLOB_SHA,
        "display_url": f"https://github.com/{REPO}/blob/main/docs/TASK_POLICY.md",
        "display_title": "TASK_POLICY.md",
    }
    assert TOKEN not in json.dumps(result)


def test_fetch_directory_returns_structured_json_text_for_recovery():
    payload = [
        {"name": "work_items.csv", "path": "data/work_items.csv", "type": "file"},
        {"name": "acceptance_tests.csv", "path": "data/acceptance_tests.csv", "type": "file"},
    ]
    client = GitHubReadWriteClient(api_key=TOKEN)
    opener = ScriptedOpener([FakeHTTPResponse(payload)])

    with _patch_opener(opener):
        result = client.fetch({"url": f"https://api.github.com/repos/{REPO}/contents/data?ref=main"})

    assert json.loads(result["content"]) == payload
    assert result["url"].startswith(f"https://api.github.com/repos/{REPO}/contents/data")
    assert "data/work_items.csv" in result["content"]


def test_compare_commits_maps_only_registered_fields():
    payload = {
        "status": "ahead",
        "ahead_by": 1,
        "behind_by": 0,
        "total_commits": 1,
        "too_large": False,
        "base_commit": {"sha": BASE_SHA, "url": "https://api.github.com/base"},
        "merge_base_commit": {"sha": BASE_SHA},
        "files": [{
            "filename": "reports/release.md",
            "status": "added",
            "additions": 4,
            "deletions": 0,
            "changes": 4,
        }],
        "commits": [{"sha": "not-returned-by-the-connector-contract"}],
    }
    client = GitHubReadWriteClient(api_key=TOKEN)
    opener = ScriptedOpener([FakeHTTPResponse(payload)])

    with _patch_opener(opener):
        result = client.compare_commits({
            "repo_full_name": REPO, "base": BASE_SHA, "head": COMMIT_SHA
        })

    assert result["repository_full_name"] == REPO
    assert result["base"] == BASE_SHA
    assert result["head"] == COMMIT_SHA
    assert result["status"] == "ahead"
    assert result["files"] == [{
        "filename": "reports/release.md",
        "status": "added",
        "additions": 4,
        "deletions": 0,
        "changes": 4,
    }]
    assert "commits" not in result
    assert "/compare/" in opener.requests[0].full_url


def test_create_branch_sends_exact_refs_payload_only_for_allowlisted_repository():
    client = GitHubReadWriteClient(
        api_key=TOKEN, enable_writes=True, allowed_repositories={REPO}
    )
    opener = ScriptedOpener([FakeHTTPResponse({
        "ref": "refs/heads/orbit/effect-forecast-check",
        "object": {"sha": BASE_SHA},
    })])

    with _patch_opener(opener):
        result = client.create_branch({
            "repository_full_name": REPO,
            "branch_name": "orbit/effect-forecast-check",
            "sha": BASE_SHA,
        })

    request = opener.requests[0]
    assert request.get_method() == "POST"
    assert request.full_url == f"https://api.github.com/repos/{REPO}/git/refs"
    assert json.loads(request.data) == {
        "ref": "refs/heads/orbit/effect-forecast-check",
        "sha": BASE_SHA,
    }
    assert result == {"branch": "orbit/effect-forecast-check"}


def test_create_file_base64_encodes_content_and_returns_commit_sha():
    client = GitHubReadWriteClient(
        api_key=TOKEN, enable_writes=True, allowed_repositories={REPO}
    )
    opener = ScriptedOpener([FakeHTTPResponse({
        "content": {"sha": BLOB_SHA},
        "commit": {"sha": COMMIT_SHA},
    })])
    arguments = {
        "repository_full_name": REPO,
        "path": "reports/new.md",
        "content": "verified report",
        "message": "Create verified report",
        "branch": "orbit/sandbox",
    }

    with _patch_opener(opener):
        result = client.create_file(arguments)

    request = opener.requests[0]
    assert request.get_method() == "PUT"
    assert request.full_url == f"https://api.github.com/repos/{REPO}/contents/reports/new.md"
    payload = json.loads(request.data)
    assert payload == {
        "message": "Create verified report",
        "content": base64.b64encode(b"verified report").decode("ascii"),
        "branch": "orbit/sandbox",
    }
    assert result == {"commit_sha": COMMIT_SHA}


def test_update_file_requires_current_blob_sha_and_returns_next_content_sha():
    client = GitHubReadWriteClient(
        api_key=TOKEN, enable_writes=True, allowed_repositories={REPO}
    )
    opener = ScriptedOpener([FakeHTTPResponse({
        "content": {"sha": "d" * 40},
        "commit": {"sha": COMMIT_SHA},
    })])

    with _patch_opener(opener):
        result = client.update_file({
            "repository_full_name": REPO,
            "path": "reports/existing.md",
            "content": "replacement",
            "message": "Update verified report",
            "sha": BLOB_SHA,
            "branch": "orbit/sandbox",
        })

    payload = json.loads(opener.requests[0].data)
    assert payload["sha"] == BLOB_SHA
    assert payload["content"] == base64.b64encode(b"replacement").decode("ascii")
    assert result == {"commit_sha": COMMIT_SHA, "content_sha": "d" * 40}


def test_write_methods_reject_non_allowlisted_repository_before_network():
    client = GitHubReadWriteClient(
        api_key=TOKEN, enable_writes=True, allowed_repositories={REPO}
    )
    opener = ScriptedOpener([])

    with _patch_opener(opener):
        with pytest.raises(GitHubClientError, match="not in the configured write allowlist"):
            client.create_file({
                "repository_full_name": "other/repo",
                "path": "report.md",
                "content": "x",
                "message": "x",
            })

    assert opener.requests == []


def test_write_methods_are_disabled_without_runtime_write_flag():
    client = GitHubReadWriteClient(
        api_key=TOKEN, enable_writes=False, allowed_repositories={REPO}
    )
    with pytest.raises(GitHubClientError, match="write operations are disabled"):
        client.create_branch({
            "repository_full_name": REPO,
            "branch_name": "orbit/sandbox",
            "sha": BASE_SHA,
        })


def test_rejects_unsupported_hosts_and_path_traversal_without_network():
    client = GitHubReadWriteClient(api_key=TOKEN)
    opener = ScriptedOpener([])

    with _patch_opener(opener):
        with pytest.raises(GitHubClientError, match="unsupported GitHub URL host"):
            client.fetch({"url": "https://example.com/repos/acme/project"})
        with pytest.raises(GitHubClientError, match="path must be repository-relative"):
            client.fetch_file({"repository_full_name": REPO, "path": "../secrets.txt"})

    assert opener.requests == []


def test_transport_errors_are_bounded_and_do_not_echo_token():
    client = GitHubReadWriteClient(api_key=TOKEN)
    opener = ScriptedOpener([TimeoutError(f"timed out with {TOKEN}")])

    with _patch_opener(opener):
        with pytest.raises(GitHubClientError, match="transport failure") as captured:
            client.fetch_file({"repository_full_name": REPO, "path": "README.md"})

    assert len(opener.requests) == 1
    assert TOKEN not in str(captured.value)


def test_response_size_limit_is_enforced_before_json_decode():
    client = GitHubReadWriteClient(api_key=TOKEN, max_response_bytes=8)
    opener = ScriptedOpener([FakeHTTPResponse(b'{"oversized": true}')])

    with _patch_opener(opener):
        with pytest.raises(GitHubClientError, match="response exceeds"):
            client.fetch_file({"repository_full_name": REPO, "path": "README.md"})

    assert len(opener.requests) == 1
