from __future__ import annotations

import base64
import hashlib
import json
from dataclasses import replace
from pathlib import Path
from urllib.parse import urlsplit

from DHI_v1.benchmark.plugin_github_runtime import build_github_plugin_runtime
from DHI_v1.benchmark.plugin_task_loader import load_plugin_task
from DHI_v1.environment.github_client import GitHubReadWriteClient


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"
REGISTRY = ROOT / "DHI_v1" / "benchmark" / "fixtures" / "plugin_ecology" / "plugin_tool_registry.json"
REPOSITORY = "Kshitijpalsinghtomar/dhi"
TASK_ID = "ORBIT-A-S06-001"
BASE_COMMIT = "af6c0d31fcf2e3232cb427c421850536139e3b3a"
BRANCH = "orbit/sandbox/orbit-a-s06-001"
REPORT_PATH = "DHI_v1/benchmark/fixtures/plugin_ecology/reports/release-readiness.md"
REPORT = "# Release readiness\n8 not Done; 35 estimated hours; 4 Open; 19 hours.\n"


def _blob_sha(content: str) -> str:
    data = content.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


class FakeResponse:
    status = 200

    def __init__(self, url: str, payload: dict):
        self._url = url
        self._payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def geturl(self):
        return self._url

    def read(self, size=-1):
        return self._payload[:size]


class FakeGitHubHTTP:
    """In-memory HTTP boundary used by the real GitHubReadWriteClient."""

    def __init__(self):
        self.calls = []
        self.files = {}
        self.branch_sha = BASE_COMMIT

    def open(self, request, timeout):
        url = request.full_url
        parsed = urlsplit(url)
        method = request.get_method()
        self.calls.append({
            "url": url,
            "method": method,
            "authorization": request.get_header("Authorization"),
            "timeout": timeout,
        })
        prefix = f"/repos/{REPOSITORY}"
        ref_path = f"{prefix}/git/ref/heads/{BRANCH}"
        file_path = f"{prefix}/contents/{REPORT_PATH}"

        if method == "GET" and parsed.path == ref_path:
            return FakeResponse(url, {
                "ref": f"refs/heads/{BRANCH}",
                "object": {"sha": self.branch_sha},
            })

        if method == "GET" and parsed.path.startswith(f"{prefix}/compare/"):
            files = [
                {"filename": path, "status": "added", "sha": _blob_sha(content)}
                for path, content in sorted(self.files.items())
            ]
            return FakeResponse(url, {"files": files})

        if method == "PUT" and parsed.path == file_path:
            body = json.loads(request.data.decode("utf-8"))
            assert body["branch"] == BRANCH
            content = base64.b64decode(body["content"]).decode("utf-8")
            self.files[REPORT_PATH] = content
            return FakeResponse(url, {"commit": {"sha": "c" * 40}})

        if method == "GET" and parsed.path == file_path:
            content = self.files[REPORT_PATH]
            return FakeResponse(url, {
                "type": "file",
                "sha": _blob_sha(content),
                "content": base64.b64encode(content.encode("utf-8")).decode("ascii"),
                "html_url": f"https://github.com/{REPOSITORY}/blob/{BRANCH}/{REPORT_PATH}",
            })

        raise AssertionError(f"unexpected fake GitHub request: {method} {url}")


def _plan():
    return replace(
        load_plugin_task(MANIFEST, REGISTRY, TASK_ID),
        model_runs_allowed=True,
    )


def test_real_github_adapter_is_bound_to_one_task_branch_for_observe_write_readback():
    http = FakeGitHubHTTP()
    client = GitHubReadWriteClient(
        api_key="fake-test-token",
        enable_writes=True,
        allowed_repositories={REPOSITORY},
    )
    client._opener = http

    runtime = build_github_plugin_runtime(_plan(), client, repository_full_name=REPOSITORY)
    observation = runtime.precondition_observer(
        {"task_id": TASK_ID},
        {"condition": {"type": "branch_head_equals", "commit": BASE_COMMIT}},
    )
    assert observation == {"branch_name": BRANCH, "head_sha": BASE_COMMIT}
    assert runtime.state_observer() == {}

    function_name = runtime.prepared.tool_name_by_id["mcp__GitHub__create_file"]
    result = runtime.prepared.dispatch(function_name, {
        "repository_full_name": REPOSITORY,
        "path": REPORT_PATH,
        "content": REPORT,
        "message": "create release report",
        "branch": BRANCH,
    })
    assert result == {"commit_sha": "c" * 40}
    state = runtime.state_observer()
    assert set(state) == {REPORT_PATH}
    assert len(state[REPORT_PATH]) == 64

    artifact = runtime.artifact_reader(REPOSITORY, REPORT_PATH, BRANCH)
    assert artifact["content"] == REPORT
    assert artifact["sha"] == _blob_sha(REPORT)
    assert artifact["display_url"].startswith(f"https://github.com/{REPOSITORY}/blob/{BRANCH}/")

    assert [call["method"] for call in http.calls] == ["GET", "PUT", "GET"]
    assert all(call["authorization"] == "Bearer fake-test-token" for call in http.calls)
    assert all(call["timeout"] == 20.0 for call in http.calls)


def test_real_github_adapter_wrong_branch_head_is_observed_not_rewritten():
    http = FakeGitHubHTTP()
    http.branch_sha = "d" * 40
    client = GitHubReadWriteClient(
        api_key="fake-test-token",
        enable_writes=True,
        allowed_repositories={REPOSITORY},
    )
    client._opener = http
    runtime = build_github_plugin_runtime(_plan(), client, repository_full_name=REPOSITORY)

    observed = runtime.precondition_observer(
        {"task_id": TASK_ID},
        {"condition": {"type": "branch_head_equals", "commit": BASE_COMMIT}},
    )
    assert observed == {"branch_name": BRANCH, "head_sha": "d" * 40}
    assert http.calls[0]["method"] == "GET"
    assert http.files == {}
