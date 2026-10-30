import json
import urllib.error
from unittest.mock import patch

import pytest

from DHI_v1.environment.adaption_responses import (
    AdaptionResponsesClient,
    chat_tools_to_responses,
    messages_to_responses_input,
    responses_to_chat_completion,
)
from DHI_v1.environment.agent_runner import ModelClientError


def test_chat_history_maps_tool_calls_and_outputs_to_responses_input_items():
    messages = [
        {"role": "system", "content": "You are an agent."},
        {"role": "user", "content": "Find a file."},
        {
            "role": "assistant",
            "content": None,
            "tool_calls": [{
                "id": "call-1",
                "type": "function",
                "function": {"name": "fs_read_file", "arguments": '{"path":"README.md"}'},
            }],
        },
        {"role": "tool", "tool_call_id": "call-1", "content": '{"ok":true}'},
    ]

    items = messages_to_responses_input(messages)

    assert items[0] == {"role": "system", "content": "You are an agent."}
    assert items[1] == {"role": "user", "content": "Find a file."}
    assert items[2] == {
        "type": "function_call",
        "call_id": "call-1",
        "name": "fs_read_file",
        "arguments": '{"path":"README.md"}',
    }
    assert items[3] == {
        "type": "function_call_output",
        "call_id": "call-1",
        "output": '{"ok":true}',
    }


def test_chat_function_schemas_convert_to_responses_function_definitions():
    tools = [{
        "type": "function",
        "function": {
            "name": "fs_read_file",
            "description": "Read a file.",
            "parameters": {"type": "object", "properties": {"path": {"type": "string"}}},
        },
    }]

    result = chat_tools_to_responses(tools)

    assert result == [{
        "type": "function",
        "name": "fs_read_file",
        "description": "Read a file.",
        "parameters": {"type": "object", "properties": {"path": {"type": "string"}}},
        "strict": False,
    }]


def test_responses_output_maps_text_and_function_calls_back_to_runner():
    response = {
        "output": [
            {"type": "reasoning", "summary": []},
            {"type": "function_call", "call_id": "call-9", "name": "fs_search_text", "arguments": '{"query":"TODO"}'},
        ],
        "output_text": None,
    }

    mapped = responses_to_chat_completion(response)
    message = mapped["choices"][0]["message"]

    assert message["role"] == "assistant"
    assert message["tool_calls"][0]["id"] == "call-9"
    assert message["tool_calls"][0]["function"]["name"] == "fs_search_text"
    assert mapped["choices"][0]["finish_reason"] == "tool_calls"


def test_responses_output_text_maps_to_final_assistant_message():
    response = {
        "output": [{
            "type": "message",
            "content": [{"type": "output_text", "text": "Found src/api.py."}],
        }],
        "output_text": "Found src/api.py.",
    }

    mapped = responses_to_chat_completion(response)

    assert mapped["choices"][0]["message"]["content"] == "Found src/api.py."
    assert mapped["choices"][0]["finish_reason"] == "stop"


class FakeHTTPResponse:
    def __init__(self, payload):
        self.payload = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload


def test_adaption_client_sends_responses_request_without_persisting_history():
    client = AdaptionResponsesClient(
        api_key="test-secret",
        model="some-hosted-model",
        base_url="https://api.test.invalid",
        organization_id="org-demo",
    )
    response_body = {
        "output": [{
            "type": "message",
            "content": [{"type": "output_text", "text": "2"}],
        }],
        "output_text": "2",
    }
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        captured["headers"] = dict(request.header_items())
        captured["body"] = json.loads(request.data)
        captured["timeout"] = timeout
        return FakeHTTPResponse(response_body)

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        result = client.complete(
            messages=[{"role": "user", "content": "What is 1 + 1?"}],
            tools=[],
        )

    assert captured["url"] == "https://api.test.invalid/api/v1/responses"
    assert captured["headers"]["Authorization"] == "Bearer test-secret"
    assert captured["headers"]["X-organization-id"] == "org-demo"
    assert captured["body"]["model"] == "some-hosted-model"
    assert captured["body"]["tools"] == []
    assert captured["body"]["tool_choice"] == "none"
    assert captured["body"]["store"] is False
    assert captured["body"]["agentic_memory"] is False
    assert result["choices"][0]["message"]["content"] == "2"


def test_adaption_model_catalogue_can_be_filtered_to_hosted_models():
    client = AdaptionResponsesClient(
        api_key="test-secret",
        model="qwen",
        base_url="https://api.test.invalid",
    )
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        return FakeHTTPResponse({"object": "list", "data": [{"id": "qwen-hosted"}]})

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        models = client.list_models(hosted_only=True)

    assert captured["url"] == "https://api.test.invalid/api/v1/models?type=hosted"
    assert models == [{"id": "qwen-hosted"}]


def test_adaption_http_error_does_not_echo_secret_in_public_exception():
    client = AdaptionResponsesClient(
        api_key="never-print-this-secret",
        model="qwen",
        base_url="https://api.test.invalid",
    )

    error = urllib.error.HTTPError(
        "https://api.test.invalid/api/v1/models", 401, "unauthorized", {}, None
    )
    error.fp = type("ErrorBody", (), {"read": lambda self, size=-1: b"unauthorized"})()

    with patch("urllib.request.urlopen", side_effect=error):
        with pytest.raises(ModelClientError, match="HTTP 401") as error:
            client.list_models()

    assert "never-print-this-secret" not in str(error.value)


def test_adaption_client_sends_responses_function_tool_schema():
    client = AdaptionResponsesClient(
        api_key="test-secret", model="hosted-model", base_url="https://api.test.invalid"
    )
    captured = {}

    def fake_urlopen(request, timeout):
        captured["body"] = json.loads(request.data)
        return FakeHTTPResponse({
            "status": "completed",
            "output": [{"type": "function_call", "call_id": "call-x", "name": "fs_read_file", "arguments": '{"path":"README.md"}'}],
        })

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        result = client.complete(
            messages=[{"role": "user", "content": "Read README."}],
            tools=[{"type": "function", "function": {
                "name": "fs_read_file",
                "description": "Read a file.",
                "parameters": {"type": "object", "properties": {"path": {"type": "string"}}},
            }}],
        )

    assert captured["body"]["tools"][0]["type"] == "function"
    assert captured["body"]["tools"][0]["name"] == "fs_read_file"
    assert result["choices"][0]["message"]["tool_calls"][0]["id"] == "call-x"


def test_adaption_client_lists_live_tool_catalogue_with_availability():
    client = AdaptionResponsesClient(api_key="test-secret", base_url="https://api.test.invalid")
    payload = {"object": "list", "data": [
        {"server_label": "github", "name": "GitHub", "available": True, "auth": "connection"},
        {"server_label": "slack", "name": "Slack", "available": False, "unavailable_reason": "requires_scope"},
    ]}
    captured = {}

    def fake_urlopen(request, timeout):
        captured["url"] = request.full_url
        return FakeHTTPResponse(payload)

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        tools = client.list_tools_catalogue()

    assert captured["url"] == "https://api.test.invalid/api/v1/tools"
    assert tools[0]["available"] is True
    assert tools[1]["unavailable_reason"] == "requires_scope"


def test_adaption_incomplete_response_is_not_returned_as_a_valid_answer():
    client = AdaptionResponsesClient(api_key="test-secret", model="hosted-model", base_url="https://api.test.invalid")

    def fake_urlopen(request, timeout):
        return FakeHTTPResponse({"status": "incomplete", "incomplete_details": {"reason": "max_output_tokens"}, "output": []})

    with patch("urllib.request.urlopen", side_effect=fake_urlopen):
        with pytest.raises(ModelClientError, match="did not complete"):
            client.complete(messages=[{"role": "user", "content": "Hi"}], tools=[])
