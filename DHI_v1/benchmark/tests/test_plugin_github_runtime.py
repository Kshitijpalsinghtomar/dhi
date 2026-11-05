from __future__ import annotations

import hashlib
import json
from dataclasses import replace
from pathlib import Path

import pytest

from DHI_v1.benchmark.plugin_task_loader import load_plugin_task
from DHI_v1.benchmark.plugin_github_runtime import (
    GitHubTaskRuntimeError,
    build_github_plugin_runtime,
)
from DHI_v1.environment.github_client import (
    CREATE_FILE_TOOL_ID,
    FETCH_FILE_TOOL_ID,
)


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"
REGISTRY = ROOT / "DHI_v1" / "benchmark" / "fixtures" / "plugin_ecology" / "plugin_tool_registry.json"
REPOSITORY = "Kshitijpalsinghtomar/dhi"
TASK_ID = "ORBIT-A-S06-001"
BASE_COMMIT = "af6c0d31fcf2e3232cb427c421850536139e3b3a"
EXPECTED_BRANCH = "orbit/sandbox/orbit-a-s06-001"
REPORT_PATH = "DHI_v1/benchmark/fixtures/plugin_ecology/reports/release-readiness.md"
REPORT = "# Release readiness\n8 not Done; 35 estimated hours; 4 Open; 19 hours.\n"


def _blob_sha(content: str) -> str:
    data = content.encode("utf-8")
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def _plan():
    plan = load_plugin_task(MANIFEST, REGISTRY, TASK_ID)
    return replace(plan, model_runs_allowed=True)


class FakeGitHubClient:
    enable_writes = True
    allowed_repositories = frozenset({REPOSITORY})

    def __init__(self):
        self.branch_sha = BASE_COMMIT
        self.returned_ref = f"refs/heads/{EXPECTED_BRANCH}"
        self.files = {}
        self.created = []
        self.fetches = []
        self.file_reads = []

    def tool_handlers(self):
        return {
            FETCH_FILE_TOOL_ID: self.fetch_file,
            CREATE_FILE_TOOL_ID: self.create_file,
            "mcp__GitHub__compare_commits": self.compare_commits,
        }

    def compare_commits(self, arguments):
        assert arguments["repo_full_name"] == REPOSITORY
        assert arguments["base"] == BASE_COMMIT
        assert arguments["head"] == EXPECTED_BRANCH
        return {
            "repository_full_name": REPOSITORY,
            "base": BASE_COMMIT,
            "head": EXPECTED_BRANCH,
            "files": [
                {"filename": path, "status": "added", "sha": _blob_sha(content)}
                for path, content in sorted(self.files.items())
            ],
        }

    def fetch(self, arguments):
        self.fetches.append(dict(arguments))
        assert arguments["url"] == (
            f"https://api.github.com/repos/{REPOSITORY}/git/ref/heads/{EXPECTED_BRANCH}"
        )
        return {
            "content": json.dumps({
                "ref": self.returned_ref,
                "object": {"sha": self.branch_sha},
            }),
            "url": arguments["url"],
        }

    def fetch_file(self, arguments):
        self.file_reads.append(dict(arguments))
        content = self.files[arguments["path"]]
        return {
            "content": content,
            "sha": _blob_sha(content),
            "display_url": (
                f"https://github.com/{arguments['repository_full_name']}/blob/"
                f"{arguments['ref']}/{arguments['path']}"
            ),
        }

    def create_file(self, arguments):
        self.created.append(dict(arguments))
        self.files[arguments["path"]] = arguments["content"]
        return {"commit_sha": "c" * 40}


def test_runtime_refuses_model_execution_when_manifest_flag_is_false():
    plan = load_plugin_task(MANIFEST, REGISTRY, TASK_ID)
    client = FakeGitHubClient()
    with pytest.raises(GitHubTaskRuntimeError, match="model_runs_allowed=false"):
        build_github_plugin_runtime(plan, client, repository_full_name=REPOSITORY)


def test_runtime_binds_precondition_readback_and_write_to_one_pinned_sandbox_branch():
    client = FakeGitHubClient()
    runtime = build_github_plugin_runtime(
        _plan(), client, repository_full_name=REPOSITORY
    )

    observation = runtime.precondition_observer(
        {"task_id": TASK_ID},
        {"condition": {"type": "branch_head_equals", "commit": BASE_COMMIT}},
    )
    assert observation == {"branch_name": EXPECTED_BRANCH, "head_sha": BASE_COMMIT}
    assert runtime.expected_branch == EXPECTED_BRANCH
    assert runtime.expected_base_commit == BASE_COMMIT


def test_runtime_denies_write_to_another_branch_or_repository():
    client = FakeGitHubClient()
    runtime = build_github_plugin_runtime(_plan(), client, repository_full_name=REPOSITORY)
    name = runtime.prepared.tool_name_by_id[CREATE_FILE_TOOL_ID]

    with pytest.raises(Exception, match="write guard denied"):
        runtime.prepared.dispatch(name, {
            "repository_full_name": REPOSITORY,
            "path": REPORT_PATH,
            "content": REPORT,
            "message": "create report",
            "branch": "main",
        })
    assert client.created == []


def test_runtime_denies_any_path_outside_manifest_output_allowlist():
    client = FakeGitHubClient()
    runtime = build_github_plugin_runtime(_plan(), client, repository_full_name=REPOSITORY)
    name = runtime.prepared.tool_name_by_id[CREATE_FILE_TOOL_ID]

    with pytest.raises(Exception, match="write guard denied"):
        runtime.prepared.dispatch(name, {
            "repository_full_name": REPOSITORY,
            "path": "README.md",
            "content": REPORT,
            "message": "create report",
            "branch": EXPECTED_BRANCH,
        })
    assert client.created == []


def test_runtime_artifact_readback_is_locked_to_expected_branch_and_allowed_path():
    client = FakeGitHubClient()
    runtime = build_github_plugin_runtime(_plan(), client, repository_full_name=REPOSITORY)
    client.files[REPORT_PATH] = REPORT

    evidence = runtime.artifact_reader(REPOSITORY, REPORT_PATH, EXPECTED_BRANCH)

    assert evidence["content"] == REPORT
    assert evidence["sha"] == _blob_sha(REPORT)
    assert client.file_reads == [{
        "repository_full_name": REPOSITORY,
        "path": REPORT_PATH,
        "ref": EXPECTED_BRANCH,
    }]


def test_runtime_rejects_wrong_repository_and_wrong_branch_readback():
    client = FakeGitHubClient()
    runtime = build_github_plugin_runtime(_plan(), client, repository_full_name=REPOSITORY)

    with pytest.raises(GitHubTaskRuntimeError, match="outside"):
        runtime.artifact_reader("other/repo", REPORT_PATH, EXPECTED_BRANCH)
    with pytest.raises(GitHubTaskRuntimeError, match="outside"):
        runtime.artifact_reader(REPOSITORY, REPORT_PATH, "main")


def test_runtime_precondition_fails_closed_when_git_ref_payload_returns_another_branch():
    client = FakeGitHubClient()
    client.returned_ref = "refs/heads/main"
    runtime = build_github_plugin_runtime(_plan(), client, repository_full_name=REPOSITORY)

    with pytest.raises(GitHubTaskRuntimeError, match="did not match"):
        runtime.precondition_observer(
            {"task_id": TASK_ID},
            {"condition": {"type": "branch_head_equals", "commit": BASE_COMMIT}},
        )


def test_runtime_refuses_when_github_write_configuration_is_not_enabled():
    client = FakeGitHubClient()
    client.enable_writes = False

    with pytest.raises(GitHubTaskRuntimeError, match="write"):
        build_github_plugin_runtime(_plan(), client, repository_full_name=REPOSITORY)


def test_runtime_refuses_repository_outside_client_write_allowlist():
    client = FakeGitHubClient()
    client.allowed_repositories = frozenset({"somewhere/else"})

    with pytest.raises(GitHubTaskRuntimeError, match="allowlist"):
        build_github_plugin_runtime(_plan(), client, repository_full_name=REPOSITORY)


class DirectAnswerModel:
    def __init__(self, before_complete=None):
        self.calls = 0
        self.before_complete = before_complete

    def complete(self, *, messages, tools, temperature=0.0):
        self.calls += 1
        if self.before_complete is not None:
            self.before_complete()
        return {"choices": [{"message": {"role": "assistant", "content": "I will not claim the report is complete."}}]}


def _task_record():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    record = next(task for task in manifest["tasks"] if task["task_id"] == TASK_ID)
    # In-memory test authorization only. The committed source manifest stays false.
    record["execution"]["model_runs_allowed"] = True
    return record


def test_runtime_bound_runner_checks_real_branch_precondition_before_model_call():
    from DHI_v1.benchmark.plugin_github_runtime import run_github_plugin_task

    client = FakeGitHubClient()
    client.branch_sha = "d" * 40
    runtime = build_github_plugin_runtime(_plan(), client, repository_full_name=REPOSITORY)
    model = DirectAnswerModel()

    result = run_github_plugin_task(
        _task_record(),
        runtime,
        model,
    )

    assert model.calls == 0
    assert result.stopped_reason == "precondition_blocked"
    assert result.trace["closure"]["status"] == "blocked"
    checked = [event for event in result.trace["events"] if event["event_type"] == "precondition_checked"]
    assert len(checked) == 1
    assert checked[0]["precondition_status"] == "fail"
    assert result.trace_validation_errors == []


def test_runtime_bound_runner_passes_branch_precondition_before_model_call():
    from DHI_v1.benchmark.plugin_github_runtime import run_github_plugin_task

    client = FakeGitHubClient()
    runtime = build_github_plugin_runtime(_plan(), client, repository_full_name=REPOSITORY)
    model = DirectAnswerModel(before_complete=lambda: (
        None if client.fetches else (_ for _ in ()).throw(AssertionError("model called before trusted branch observation"))
    ))

    result = run_github_plugin_task(
        _task_record(),
        runtime,
        model,
        observe_state=lambda: {},
    )

    assert model.calls == 1
    checked = next(event for event in result.trace["events"] if event["event_type"] == "precondition_checked")
    assert checked["precondition_status"] == "pass"
    assert client.fetches == [{
        "url": f"https://api.github.com/repos/{REPOSITORY}/git/ref/heads/{EXPECTED_BRANCH}"
    }]
    assert result.trace_validation_errors == []


def test_runtime_owns_independent_full_branch_diff_state_observer():
    client = FakeGitHubClient()
    runtime = build_github_plugin_runtime(_plan(), client, repository_full_name=REPOSITORY)

    assert runtime.state_observer() == {}
    client.files[REPORT_PATH] = REPORT
    state = runtime.state_observer()

    assert set(state) == {REPORT_PATH}
    assert len(state[REPORT_PATH]) == 64
    assert state[REPORT_PATH] == hashlib.sha256(
        json.dumps(
            {"blob_sha": _blob_sha(REPORT), "status": "added"},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
