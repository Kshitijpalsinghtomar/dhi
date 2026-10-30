"""Adaption Responses API client compatible with DHI's ChatCompletionClient.

The adapter maps DHI's OpenAI-style tool loop onto Adaption's Responses API:
- chat messages become Responses input messages/function-call items;
- visible DHI tools become Responses function tool definitions;
- function_call outputs are mapped back into the existing runner protocol.

No credential is read from source code or written to traces.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

from .agent_runner import ModelClientError


DEFAULT_ADAPTION_API_BASE_URL = "https://api.prod.adaptionlabs.ai"


def messages_to_responses_input(messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Translate the runner's message history into Responses API input items."""
    items: list[dict[str, Any]] = []
    for message in messages:
        role = message.get("role")
        if role in {"system", "developer", "user"}:
            content = message.get("content")
            if content is not None:
                items.append({"role": role, "content": content})
            continue

        if role == "assistant":
            content = message.get("content")
            if content is not None:
                items.append({"role": "assistant", "content": content})
            for call in message.get("tool_calls") or []:
                function = call.get("function") or {}
                items.append({
                    "type": "function_call",
                    "call_id": str(call.get("id") or ""),
                    "name": str(function.get("name") or ""),
                    "arguments": function.get("arguments", "{}"),
                })
            continue

        if role == "tool":
            items.append({
                "type": "function_call_output",
                "call_id": str(message.get("tool_call_id") or ""),
                "output": str(message.get("content") or ""),
            })
            continue

        raise ModelClientError(f"unsupported DHI conversation role for Adaption Responses API: {role!r}")
    return items


def chat_tools_to_responses(tools: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert Chat Completions function schemas to Responses function tools."""
    result: list[dict[str, Any]] = []
    for tool in tools:
        function = tool.get("function") if isinstance(tool, dict) else None
        if not isinstance(function, dict):
            raise ModelClientError("DHI tool schema is missing its function object")
        name = function.get("name")
        parameters = function.get("parameters")
        if not isinstance(name, str) or not name:
            raise ModelClientError("DHI function schema is missing a function name")
        if not isinstance(parameters, dict):
            raise ModelClientError(f"DHI function schema {name!r} is missing parameters")
        result.append({
            "type": "function",
            "name": name,
            "description": function.get("description", ""),
            "parameters": parameters,
            "strict": False,
        })
    return result


def responses_to_chat_completion(response: dict[str, Any]) -> dict[str, Any]:
    """Translate Responses output items into the runner's expected chat shape."""
    output = response.get("output")
    if not isinstance(output, list):
        raise ModelClientError("Adaption response is missing the output array")

    text_parts: list[str] = []
    tool_calls: list[dict[str, Any]] = []
    for item in output:
        if not isinstance(item, dict):
            continue
        item_type = item.get("type")
        if item_type == "message":
            for part in item.get("content") or []:
                if not isinstance(part, dict):
                    continue
                if part.get("type") == "output_text" and isinstance(part.get("text"), str):
                    text_parts.append(part["text"])
                elif part.get("type") == "refusal" and isinstance(part.get("refusal"), str):
                    text_parts.append(part["refusal"])
        elif item_type == "function_call":
            tool_calls.append({
                "id": str(item.get("call_id") or item.get("id") or ""),
                "type": "function",
                "function": {
                    "name": str(item.get("name") or ""),
                    "arguments": item.get("arguments", "{}"),
                },
            })

    # output_text is a convenience field in the Responses API. Use it only
    # when the individual output message parts did not already supply text.
    if not text_parts and isinstance(response.get("output_text"), str):
        text_parts.append(response["output_text"])

    message: dict[str, Any] = {
        "role": "assistant",
        "content": "\n".join(text_parts) if text_parts else None,
    }
    if tool_calls:
        message["tool_calls"] = tool_calls
    finish_reason = "tool_calls" if tool_calls else "stop"
    return {"choices": [{"message": message, "finish_reason": finish_reason}]}


class AdaptionResponsesClient:
    """HTTP client for Adaption's authenticated Responses API."""
    def __init__(
        self,
        *,
        api_key: str,
        model: str | None = None,
        base_url: str = DEFAULT_ADAPTION_API_BASE_URL,
        organization_id: str | None = None,
        timeout_seconds: float = 180.0,
        max_output_tokens: int = 4096,
        max_tool_calls: int = 64,
    ) -> None:
        if not api_key:
            raise ValueError("Adaption API key is required")
        if model is not None and (not isinstance(model, str) or not model.strip()):
            raise ValueError("Adaption model ID must be a non-empty string when supplied")
        if not base_url.startswith(("https://", "http://")):
            raise ValueError("base_url must be an HTTP(S) URL")
        if timeout_seconds <= 0 or max_output_tokens < 1 or not 1 <= max_tool_calls <= 64:
            raise ValueError("invalid timeout/output/tool-call limit")
        self.api_key = api_key
        self.model = model.strip() if model is not None else None
        self.base_url = base_url.rstrip("/")
        self.organization_id = organization_id
        self.timeout_seconds = timeout_seconds
        self.max_output_tokens = max_output_tokens
        self.max_tool_calls = max_tool_calls

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        url = f"{self.base_url}/api/v1/{path.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        if body is not None:
            headers["Content-Type"] = "application/json"
        if self.organization_id:
            headers["X-Organization-Id"] = self.organization_id
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                payload = response.read()
        except urllib.error.HTTPError as exc:
            detail = exc.read(2048).decode("utf-8", errors="replace")
            raise ModelClientError(f"Adaption API HTTP {exc.code}: {detail}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise ModelClientError(f"Adaption API request failed: {exc}") from exc
        try:
            result = json.loads(payload)
        except json.JSONDecodeError as exc:
            raise ModelClientError("Adaption API returned invalid JSON") from exc
        if not isinstance(result, dict):
            raise ModelClientError("Adaption API response must be a JSON object")
        return result

    def list_models(self, *, hosted_only: bool = False) -> list[dict[str, Any]]:
        """List models the current API key can call through Responses."""
        path = "models"
        if hosted_only:
            path += "?type=hosted"
        result = self._request("GET", path)
        models = result.get("data")
        if not isinstance(models, list):
            raise ModelClientError("Adaption model catalogue is missing data[]")
        return models

    def list_tools_catalogue(self) -> list[dict[str, Any]]:
        """List Adaption host-side MCP connectors and caller availability."""
        result = self._request("GET", "tools")
        tools = result.get("data")
        if not isinstance(tools, list) or any(not isinstance(item, dict) for item in tools):
            raise ModelClientError("Adaption tool catalogue is missing a valid data[] array")
        return tools

    @staticmethod
    def _catalogue_tokens(value: str) -> set[str]:
        return {token for token in re.findall(r"[a-z0-9_]+", value.casefold()) if len(token) > 1}

    def search_tools_catalogue(
        self, *, query: str, available_only: bool = True, limit: int = 10
    ) -> dict[str, Any]:
        """Search the live Adaption connector inventory; this never executes a connector."""
        if not isinstance(query, str) or not query.strip():
            raise ValueError("catalogue search query must be a non-empty string")
        if not isinstance(available_only, bool):
            raise ValueError("available_only must be a boolean")
        if not isinstance(limit, int) or isinstance(limit, bool) or not 1 <= limit <= 50:
            raise ValueError("catalogue search limit must be an integer from 1 to 50")

        catalogue = self.list_tools_catalogue()
        query_terms = self._catalogue_tokens(query)
        scored: list[tuple[int, str, dict[str, Any]]] = []
        filtered_count = 0
        for item in catalogue:
            if available_only and item.get("available") is not True:
                continue
            filtered_count += 1
            searchable = " ".join(str(item.get(key, "")) for key in (
                "server_label", "name", "description", "auth", "connect", "mode",
                "default_require_approval", "required_scope", "unavailable_reason",
            ))
            score = len(query_terms & self._catalogue_tokens(searchable))
            if score:
                scored.append((score, str(item.get("server_label", "")), item))

        scored.sort(key=lambda row: (-row[0], row[1]))
        matches = [{**dict(item), "relevance_score": score} for score, _, item in scored[:limit]]
        return {
            "catalogue_source": "adaption_api",
            "query": query,
            "available_only": available_only,
            "catalogue_count": len(catalogue),
            "searched_count": filtered_count,
            "match_count": len(matches),
            "tools": matches,
            "execution_note": "Discovery only. No connector was invoked and no external state was changed.",
        }

    def complete(
        self,
        *,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        temperature: float = 0.0,
    ) -> dict[str, Any]:
        if not self.model:
            raise ValueError("Adaption model ID is required for inference")
        body: dict[str, Any] = {
            "model": self.model,
            "input": messages_to_responses_input(messages),
            "tool_choice": "auto",
            "max_output_tokens": self.max_output_tokens,
            "max_tool_calls": self.max_tool_calls,
            "temperature": temperature,
            "agentic_memory": False,
            "store": False,
        }
        if tools:
            body["tools"] = chat_tools_to_responses(tools)
        else:
            body["tools"] = []
            body["tool_choice"] = "none"

        result = self._request("POST", "responses", body)
        status = result.get("status")
        if status is not None and status != "completed":
            details = result.get("error") or result.get("incomplete_details") or status
            raise ModelClientError(f"Adaption response did not complete ({status}): {details}")
        if result.get("error"):
            error = result["error"]
            if isinstance(error, dict):
                raise ModelClientError(f"Adaption inference error: {error.get('code')}: {error.get('message')}")
            raise ModelClientError(f"Adaption inference error: {error}")
        return responses_to_chat_completion(result)


def adaption_client_from_env() -> AdaptionResponsesClient:
    """Build the Adaption Responses client from environment variables."""
    api_key = os.environ.get("ADAPTION_API_KEY") or os.environ.get("DHI_ADAPTION_API_KEY") or ""
    model = os.environ.get("DHI_MODEL_NAME", "").strip()
    base_url = os.environ.get("DHI_ADAPTION_API_BASE_URL", DEFAULT_ADAPTION_API_BASE_URL)
    organization_id = os.environ.get("DHI_ADAPTION_ORGANIZATION_ID") or None
    if not api_key:
        raise SystemExit("Set ADAPTION_API_KEY (or DHI_ADAPTION_API_KEY) before running the Adaption model pilot.")
    if not model:
        raise SystemExit("Set DHI_MODEL_NAME to an exact ID from GET /api/v1/models or stack:<slug>.")
    return AdaptionResponsesClient(
        api_key=api_key, model=model, base_url=base_url,
        organization_id=organization_id,
    )
