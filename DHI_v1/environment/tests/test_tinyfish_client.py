import json
import urllib.error
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import pytest

from DHI_v1.environment.dhi_env import DEFAULT_TOOL_CATALOGUE, DHIEnvironment, TaskSpec
from DHI_v1.environment.agent_runner import tool_handlers_from_client, run_agent_task
from DHI_v1.environment.tinyfish_client import (
    FETCH_TOOL_ID,
    SEARCH_TOOL_ID,
    TINYFISH_TOOL_CATALOGUE,
    TinyFishClientError,
    TinyFishReadOnlyClient,
    tinyfish_tool_handlers_from_env,
)


class FakeHTTPResponse:
    def __init__(self, payload, status=200):
        self.payload = json.dumps(payload).encode("utf-8")
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload


def header_map(request):
    return {name.lower(): value for name, value in request.header_items()}


def test_search_uses_fixed_rest_endpoint_and_env_key_header():
    client = TinyFishReadOnlyClient(api_key="secret-search-key")
    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["timeout"] = timeout
        return FakeHTTPResponse({
            "query": "python packaging",
            "results": [{"title": "Python docs", "url": "https://docs.python.org/"}],
            "total_results": 1,
            "page": 0,
        })

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        result = client.search({
            "query": "python packaging",
            "include_domains": "docs.python.org",
            "page": 0,
        })

    request = captured["request"]
    parsed = urlsplit(request.full_url)
    assert request.method == "GET"
    assert parsed.scheme == "https"
    assert parsed.netloc == "api.search.tinyfish.ai"
    assert parsed.path == ""
    assert parse_qs(parsed.query) == {
        "query": ["python packaging"],
        "include_domains": ["docs.python.org"],
        "page": ["0"],
    }
    assert header_map(request)["x-api-key"] == "secret-search-key"
    assert header_map(request)["accept"] == "application/json"
    assert captured["timeout"] > 0
    assert result["results"][0]["url"] == "https://docs.python.org/"


def test_fetch_content_uses_fixed_rest_endpoint_and_json_body():
    client = TinyFishReadOnlyClient(api_key="secret-fetch-key")
    captured = {}

    def fake_urlopen(request, timeout):
        captured["request"] = request
        captured["body"] = json.loads(request.data.decode("utf-8"))
        return FakeHTTPResponse({
            "results": [{"url": "https://docs.python.org/", "text": "Python docs"}],
            "errors": [],
        })

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        result = client.fetch_content({
            "urls": ["https://docs.python.org/"],
            "format": "markdown",
            "links": False,
            "image_links": False,
        })

    request = captured["request"]
    assert request.method == "POST"
    assert request.full_url == "https://api.fetch.tinyfish.ai"
    headers = header_map(request)
    assert headers["x-api-key"] == "secret-fetch-key"
    assert headers["content-type"] == "application/json"
    assert captured["body"] == {
        "urls": ["https://docs.python.org/"],
        "format": "markdown",
        "links": False,
        "image_links": False,
    }
    assert result["errors"] == []


def test_client_rejects_unknown_arguments_before_network_call():
    client = TinyFishReadOnlyClient(api_key="secret")
    with patch("urllib.request.urlopen") as request:
        with pytest.raises(ValueError, match="unexpected"):
            client.search({"query": "safe", "endpoint": "https://attacker.example"})
        with pytest.raises(ValueError, match="unexpected"):
            client.fetch_content({"urls": ["https://example.com"], "method": "DELETE"})
    request.assert_not_called()


@pytest.mark.parametrize("url", [
    "file:///etc/passwd",
    "ftp://example.com/file",
    "http://localhost/admin",
    "http://127.0.0.1/",
    "http://169.254.169.254/latest/meta-data/",
    "https://user:password@example.com/private",
])
def test_fetch_rejects_non_public_or_non_http_urls(url):
    client = TinyFishReadOnlyClient(api_key="secret")
    with patch("urllib.request.urlopen") as request:
        with pytest.raises(ValueError):
            client.fetch_content({"urls": [url]})
    request.assert_not_called()


def test_http_error_is_not_retried_and_never_echoes_key():
    secret = "never-print-this-key"
    client = TinyFishReadOnlyClient(api_key=secret)
    calls = []

    error = urllib.error.HTTPError(
        "https://api.search.tinyfish.ai", 429, "rate limited", {}, None
    )
    error.fp = type("ErrorBody", (), {
        "read": lambda self, size=-1: (secret + " invalid").encode("utf-8")
    })()

    def fail_once(request, timeout):
        calls.append(request)
        raise error

    with patch("urllib.request.urlopen", side_effect=fail_once):
        with pytest.raises(TinyFishClientError, match="HTTP 429") as captured:
            client.search({"query": "one request"})

    assert len(calls) == 1
    assert secret not in str(captured.value)


def test_environment_factory_exposes_only_two_read_only_handlers():
    with patch.dict("os.environ", {}, clear=True):
        assert tinyfish_tool_handlers_from_env() == {}

    with patch.dict("os.environ", {"TINYFISH_API_KEY": "runtime-secret"}):
        handlers = tinyfish_tool_handlers_from_env()

    assert set(handlers) == {SEARCH_TOOL_ID, FETCH_TOOL_ID}
    assert len(TINYFISH_TOOL_CATALOGUE) == 2
    assert all(item["side_effects"] == "read_only" for item in TINYFISH_TOOL_CATALOGUE)
    assert {item["tool_id"] for item in TINYFISH_TOOL_CATALOGUE} == set(handlers)
    assert all(item.get("requires_explicit_task_allowlist") is True for item in TINYFISH_TOOL_CATALOGUE)


def make_task(**overrides):
    values = {
        "task_id": "tinyfish-allowlist-gate",
        "prompt": "Search the public web for the official Python documentation.",
        "goal": "Return one source URL from the search result.",
        "postconditions": [{"type": "exists", "path": "README.md"}],
        "visible_tool_ids": ["fs.list_files"],
        "allowed_tool_ids": [],
    }
    values.update(overrides)
    return TaskSpec(**values)


def make_environment(tmp_path, handlers):
    catalogue = DEFAULT_TOOL_CATALOGUE
    return DHIEnvironment(tmp_path, catalogue=catalogue, tool_handlers=handlers)


def test_tinyfish_tools_are_not_discoverable_without_explicit_task_allowlist(tmp_path):
    handlers = {
        SEARCH_TOOL_ID: lambda arguments: {"results": []},
        FETCH_TOOL_ID: lambda arguments: {"results": [], "errors": []},
    }
    env = make_environment(tmp_path, handlers)
    env.begin_task(make_task(allowed_tool_ids=[]))

    discovered = env.discover_tools("search public web and fetch page content", limit=20)
    result = env.run_action({
        "tool_id": SEARCH_TOOL_ID,
        "arguments": {"query": "python documentation"},
    })

    assert SEARCH_TOOL_ID not in {item["tool_id"] for item in discovered}
    assert result.ok is False
    assert "explicit task allowlist" in result.error.lower()


def test_tinyfish_tools_can_be_discovered_only_when_task_allowlists_them(tmp_path):
    handlers = {
        SEARCH_TOOL_ID: lambda arguments: {"results": []},
        FETCH_TOOL_ID: lambda arguments: {"results": [], "errors": []},
    }
    env = make_environment(tmp_path, handlers)
    env.begin_task(make_task(allowed_tool_ids=[SEARCH_TOOL_ID]))

    discovered = env.discover_tools("search public web and fetch page content", limit=20)

    assert SEARCH_TOOL_ID in {item["tool_id"] for item in discovered}
    assert FETCH_TOOL_ID not in {item["tool_id"] for item in discovered}


def test_model_runner_registers_only_tinyfish_read_only_handlers_from_env():
    class MinimalClient:
        pass

    with patch.dict("os.environ", {"TINYFISH_API_KEY": "runtime-secret"}):
        handlers = tool_handlers_from_client(MinimalClient())

    assert set(handlers) == {SEARCH_TOOL_ID, FETCH_TOOL_ID}


def test_model_task_executes_only_allowlisted_tinyfish_tool_and_records_trace(tmp_path):
    secret = "trace-must-never-contain-this-secret"
    response_payload = {
        "query": "official Python documentation",
        "results": [{
            "title": "Python documentation",
            "url": "https://docs.python.org/3/",
            "snippet": "Official Python documentation",
            "position": 1,
        }],
        "total_results": 1,
        "page": 0,
    }
    client = TinyFishReadOnlyClient(api_key=secret)
    environment = DHIEnvironment(
        tmp_path,
        catalogue=DEFAULT_TOOL_CATALOGUE,
        tool_handlers=client.tool_handlers(),
    )
    (tmp_path / "README.md").write_text("# Existing fixture\\n", encoding="utf-8")

    class ScriptedModelClient:
        def __init__(self):
            self.presented_tool_names = []

        def complete(self, *, messages, tools, temperature=0.0):
            names = [item["function"]["name"] for item in tools]
            self.presented_tool_names.append(names)
            if len(self.presented_tool_names) == 1:
                assert names == ["catalog_search", "tinyfish_search"]
                args = {
                    "query": "official Python documentation",
                    "__dhi_expected_effects": {
                        "changed_paths": [],
                        "unchanged_paths": [],
                    },
                }
                return {
                    "choices": [{
                        "message": {
                            "role": "assistant",
                            "tool_calls": [{
                                "id": "call-tinyfish-search",
                                "type": "function",
                                "function": {
                                    "name": "tinyfish_search",
                                    "arguments": json.dumps(args),
                                },
                            }],
                        },
                    }],
                }
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "The official Python documentation is https://docs.python.org/3/.",
                    },
                }],
            }

    model = ScriptedModelClient()
    task = TaskSpec(
        task_id="tinyfish-model-runner-contract",
        prompt="Find the official Python documentation.",
        goal="Return the official Python documentation URL.",
        allowed_tool_ids=[SEARCH_TOOL_ID],
        visible_tool_ids=[SEARCH_TOOL_ID],
        postconditions=[{"type": "exists", "path": "README.md"}],
        protected_paths=["README.md"],
    )

    def fake_urlopen(request, timeout):
        assert request.full_url.startswith("https://api.search.tinyfish.ai")
        assert header_map(request)["x-api-key"] == secret
        return FakeHTTPResponse(response_payload)

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        result = run_agent_task(environment, task, model)

    action_events = [
        event for event in environment.events
        if event["event_type"] == "action_executed"
    ]
    assert result.stopped_reason == "final_answer"
    assert result.final_answer and "https://docs.python.org/3/" in result.final_answer
    assert result.tool_call_count == 1
    assert result.closure["success"] is True
    assert model.presented_tool_names == [["catalog_search", "tinyfish_search"], ["catalog_search", "tinyfish_search"]]
    assert len(action_events) == 1
    event = action_events[0]
    assert event["selected_tool_id"] == SEARCH_TOOL_ID
    assert event["actual_tool_result"]["ok"] is True
    assert event["actual_tool_result"]["result"] == response_payload
    assert event["prediction_comparison"]["status"] == "matched"
    assert secret not in json.dumps(environment.events, ensure_ascii=False)


def test_transport_timeout_is_bounded_and_never_retried_or_echoed_key():
    secret = "timeout-key-must-not-leak"
    client = TinyFishReadOnlyClient(api_key=secret, timeout_seconds=3.25)
    calls = []

    def time_out(request, timeout):
        calls.append(request)
        assert timeout == 3.25
        raise TimeoutError("transport timed out for " + secret)

    with patch("urllib.request.urlopen", side_effect=time_out):
        with pytest.raises(TinyFishClientError, match="transport failure") as captured:
            client.search({"query": "bounded timeout test"})

    assert len(calls) == 1
    assert "TimeoutError" in str(captured.value)
    assert secret not in str(captured.value)
