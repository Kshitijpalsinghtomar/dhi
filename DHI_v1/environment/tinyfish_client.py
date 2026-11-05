"""Policy-limited, read-only TinyFish Search and Fetch REST client.

The client intentionally exposes only the two public-web retrieval surfaces.
It never exposes browser automation, monitors, datasets, deep research, wallet
operations, or any provider write action to a DHI model.
"""
from __future__ import annotations

import ipaddress
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from typing import Any
from urllib.parse import urlsplit


SEARCH_ENDPOINT = "https://api.search.tinyfish.ai"
FETCH_ENDPOINT = "https://api.fetch.tinyfish.ai"
SEARCH_TOOL_ID = "mcp__TinyFish__search"
FETCH_TOOL_ID = "mcp__TinyFish__fetch_content"

_SEARCH_PROPERTIES: dict[str, dict[str, Any]] = {
    "query": {"type": "string", "minLength": 1, "maxLength": 2000},
    "purpose": {"type": "string", "minLength": 1, "maxLength": 2000},
    "location": {"type": "string", "minLength": 2, "maxLength": 2},
    "language": {"type": "string", "minLength": 2, "maxLength": 12},
    "include_domains": {"type": "string", "minLength": 1, "maxLength": 2000},
    "exclude_domains": {"type": "string", "minLength": 1, "maxLength": 2000},
    "domain_type": {"type": "string", "enum": ["web", "news", "research_paper"]},
    "recency_minutes": {"type": "integer", "minimum": 1, "maximum": 5256000},
    "after_date": {"type": "string", "format": "date"},
    "before_date": {"type": "string", "format": "date"},
    "pub_year_min": {"type": "integer", "minimum": 0, "maximum": 9999},
    "pub_year_max": {"type": "integer", "minimum": 0, "maximum": 9999},
    "page": {"type": "integer", "minimum": 0, "maximum": 10},
}
_FETCH_PROPERTIES: dict[str, dict[str, Any]] = {
    "urls": {"type": "array", "minItems": 1, "maxItems": 10},
    "purpose": {"type": "string", "minLength": 1, "maxLength": 2000},
    "format": {"type": "string", "enum": ["markdown", "html", "json"]},
    "links": {"type": "boolean"},
    "image_links": {"type": "boolean"},
    "iframe_links": {"type": "boolean"},
    "ttl": {"type": "integer", "minimum": 0},
    "per_url_timeout_ms": {"type": "integer", "minimum": 1, "maximum": 110000},
    "if_none_match": {"type": "string", "minLength": 1},
    "if_modified_since": {"type": "string", "minLength": 1},
    "include_etag_and_last_modified": {"type": "boolean"},
    "include_selectors": {"type": "array", "minItems": 1, "maxItems": 20},
    "exclude_selectors": {"type": "array", "minItems": 1, "maxItems": 20},
}

TINYFISH_TOOL_CATALOGUE: list[dict[str, Any]] = [
    {
        "tool_id": SEARCH_TOOL_ID,
        "name": "TinyFish public web search",
        "description": (
            "Search public web pages and return structured titles, snippets, URLs "
            "and dates. Read-only. Use this to discover sources before fetching them."
        ),
        "tags": ["tinyfish", "web", "public", "internet", "search", "research", "source", "discovery"],
        "input_schema": {
            "type": "object",
            "required": ["query"],
            "properties": _SEARCH_PROPERTIES,
            "additionalProperties": False,
        },
        "side_effects": "read_only",
        "permission_scope": "public_web_read",
        "preconditions": ["TINYFISH_API_KEY is available in the runtime environment"],
        "cost_class": "free_with_daily_quota",
        "reversible": True,
        "requires_handler": True,
        "requires_explicit_task_allowlist": True,
    },
    {
        "tool_id": FETCH_TOOL_ID,
        "name": "TinyFish fetch page content",
        "description": (
            "Fetch one to ten public HTTP(S) URLs and extract clean Markdown, HTML "
            "or JSON. Read-only. Use after search or when a task supplies a URL."
        ),
        "tags": ["tinyfish", "fetch", "read", "page", "content", "extract", "public", "web"],
        "input_schema": {
            "type": "object",
            "required": ["urls"],
            "properties": _FETCH_PROPERTIES,
            "additionalProperties": False,
        },
        "side_effects": "read_only",
        "permission_scope": "public_web_read",
        "preconditions": ["TINYFISH_API_KEY is available in the runtime environment"],
        "cost_class": "free_with_daily_quota",
        "reversible": True,
        "requires_handler": True,
        "requires_explicit_task_allowlist": True,
    },
]


class TinyFishClientError(ValueError):
    """A safe, task-visible TinyFish request or response error."""


def _validate_object(arguments: Any, properties: dict[str, dict[str, Any]], required: list[str]) -> dict[str, Any]:
    if not isinstance(arguments, dict):
        raise ValueError("TinyFish tool arguments must be an object")
    missing = sorted(set(required) - set(arguments))
    if missing:
        raise ValueError("missing required argument(s): " + ", ".join(missing))
    unexpected = sorted(set(arguments) - set(properties))
    if unexpected:
        raise ValueError("unexpected TinyFish argument(s): " + ", ".join(unexpected))

    types: dict[str, Any] = {
        "string": str,
        "boolean": bool,
        "integer": int,
        "array": list,
    }
    for name, value in arguments.items():
        schema = properties[name]
        expected_type = schema["type"]
        accepted = types[expected_type]
        if expected_type == "integer" and isinstance(value, bool):
            raise ValueError(f"argument {name!r} must be integer")
        if not isinstance(value, accepted):
            raise ValueError(f"argument {name!r} must be {expected_type}")
        if expected_type == "string":
            minimum = schema.get("minLength", 0)
            maximum = schema.get("maxLength")
            if len(value.strip()) < minimum:
                raise ValueError(f"argument {name!r} must not be empty")
            if maximum is not None and len(value) > maximum:
                raise ValueError(f"argument {name!r} exceeds its maximum length")
        if expected_type == "integer":
            if value < schema.get("minimum", value) or value > schema.get("maximum", value):
                raise ValueError(f"argument {name!r} is outside the allowed range")
        if "enum" in schema and value not in schema["enum"]:
            raise ValueError(f"argument {name!r} must be one of {schema['enum']!r}")
        if expected_type == "array":
            minimum = schema.get("minItems", 0)
            maximum = schema.get("maxItems")
            if len(value) < minimum or (maximum is not None and len(value) > maximum):
                raise ValueError(f"argument {name!r} has an invalid item count")
    return dict(arguments)


def _validate_date(value: str, name: str) -> None:
    try:
        date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError(f"argument {name!r} must use YYYY-MM-DD") from exc


def _validate_search(arguments: Any) -> dict[str, Any]:
    args = _validate_object(arguments, _SEARCH_PROPERTIES, ["query"])
    if "recency_minutes" in args and ("after_date" in args or "before_date" in args):
        raise ValueError("recency_minutes cannot be combined with after_date or before_date")
    if "after_date" in args:
        _validate_date(args["after_date"], "after_date")
    if "before_date" in args:
        _validate_date(args["before_date"], "before_date")
    if "after_date" in args and "before_date" in args and args["after_date"] > args["before_date"]:
        raise ValueError("after_date must be less than or equal to before_date")
    if args.get("domain_type") == "research_paper" and any(
        name in args for name in ("recency_minutes", "after_date", "before_date")
    ):
        raise ValueError("research_paper search uses pub_year_min/pub_year_max, not date or recency filters")
    if "pub_year_min" in args and "pub_year_max" in args and args["pub_year_min"] > args["pub_year_max"]:
        raise ValueError("pub_year_min must be less than or equal to pub_year_max")
    if any(name in args for name in ("pub_year_min", "pub_year_max")) and args.get("domain_type", "web") != "research_paper":
        raise ValueError("publication-year filters require domain_type=research_paper")
    return args


def _validate_public_url(value: Any) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("each fetch URL must be a non-empty string")
    parsed = urlsplit(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("fetch URLs must be absolute HTTP(S) URLs")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("fetch URLs must not contain embedded credentials")
    host = parsed.hostname.casefold().rstrip(".")
    if host in {"localhost", "metadata.google.internal"} or host.endswith((".localhost", ".local", ".internal")):
        raise ValueError("fetch URL host is not public")
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        address = None
    if address is not None and (
        address.is_private or address.is_loopback or address.is_link_local
        or address.is_multicast or address.is_reserved or address.is_unspecified
    ):
        raise ValueError("fetch URL must not target a private or special-use IP address")
    return value


def _validate_fetch(arguments: Any) -> dict[str, Any]:
    args = _validate_object(arguments, _FETCH_PROPERTIES, ["urls"])
    args["urls"] = [_validate_public_url(url) for url in args["urls"]]
    if any(name in args for name in ("if_none_match", "if_modified_since")) and len(args["urls"]) != 1:
        raise ValueError("conditional fetch validators require exactly one URL")
    for name in ("include_selectors", "exclude_selectors"):
        if name in args:
            if any(not isinstance(selector, str) or not selector.strip() or len(selector) > 1000
                   for selector in args[name]):
                raise ValueError(f"{name} must contain non-empty CSS selector strings up to 1000 characters")
    return args


class TinyFishReadOnlyClient:
    """Call only TinyFish's documented Search and Fetch REST endpoints.

    The endpoint host is fixed in code, the API key is read from the runtime
    environment, and no automatic retries or provider-side mutations are used.
    """

    def __init__(self, *, api_key: str | None = None, timeout_seconds: float = 120.0) -> None:
        resolved_key = api_key if api_key is not None else os.environ.get("TINYFISH_API_KEY", "")
        if not isinstance(resolved_key, str) or not resolved_key.strip():
            raise ValueError("TINYFISH_API_KEY is required")
        if isinstance(timeout_seconds, bool) or not isinstance(timeout_seconds, (int, float)) or not 1 <= timeout_seconds <= 180:
            raise ValueError("timeout_seconds must be between 1 and 180")
        self._api_key = resolved_key.strip()
        self.timeout_seconds = float(timeout_seconds)

    def _request(self, *, operation: str, method: str, endpoint: str,
                 query: dict[str, Any] | None = None, body: dict[str, Any] | None = None) -> dict[str, Any]:
        url = endpoint
        data = None
        headers = {
            "Accept": "application/json",
            "User-Agent": "DHI-ORBIT-TinyFish-Adapter/0.1",
        }
        if method == "GET":
            if body is not None:
                raise TinyFishClientError("internal request configuration error")
            if query:
                url += "?" + urllib.parse.urlencode(query)
        elif method == "POST":
            if query is not None:
                raise TinyFishClientError("internal request configuration error")
            data = json.dumps(body or {}, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            headers["Content-Type"] = "application/json"
        else:
            raise TinyFishClientError("unsupported TinyFish HTTP method")

        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        # Keep API credentials out of Request.headers: urllib's default redirect
        # handler copies ordinary headers to the redirected request.
        request.add_unredirected_header("X-API-Key", self._api_key)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                status = response.status
                raw = response.read()
        except urllib.error.HTTPError as exc:
            error_code = None
            try:
                payload = json.loads(exc.read(4096).decode("utf-8", errors="replace"))
                error = payload.get("error") if isinstance(payload, dict) else None
                if isinstance(error, dict):
                    candidate = error.get("code")
                    if isinstance(candidate, str) and re.fullmatch(r"[A-Z0-9_]{1,64}", candidate):
                        error_code = candidate
            except Exception:
                error_code = None
            suffix = f" ({error_code})" if error_code else ""
            raise TinyFishClientError(f"TinyFish {operation} HTTP {exc.code}{suffix}") from None
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            raise TinyFishClientError(
                f"TinyFish {operation} transport failure: {type(exc).__name__}"
            ) from None

        try:
            payload = json.loads(raw.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError):
            raise TinyFishClientError(f"TinyFish {operation} returned invalid JSON (HTTP {status})") from None
        if not isinstance(payload, dict):
            raise TinyFishClientError(f"TinyFish {operation} returned a non-object response (HTTP {status})")
        return payload

    def search(self, arguments: dict[str, Any]) -> dict[str, Any]:
        args = _validate_search(arguments)
        result = self._request(
            operation="search", method="GET", endpoint=SEARCH_ENDPOINT, query=args
        )
        if not isinstance(result.get("results"), list):
            raise TinyFishClientError("TinyFish search response is missing results[]")
        return result

    def fetch_content(self, arguments: dict[str, Any]) -> dict[str, Any]:
        args = _validate_fetch(arguments)
        result = self._request(
            operation="fetch_content", method="POST", endpoint=FETCH_ENDPOINT, body=args
        )
        if not isinstance(result.get("results"), list) or not isinstance(result.get("errors"), list):
            raise TinyFishClientError("TinyFish fetch response must contain results[] and errors[]")
        return result

    def tool_handlers(self) -> dict[str, Any]:
        return {
            SEARCH_TOOL_ID: self.search,
            FETCH_TOOL_ID: self.fetch_content,
        }


def tinyfish_tool_handlers_from_env() -> dict[str, Any]:
    """Return the two read-only handlers only when the runtime key is configured."""
    api_key = os.environ.get("TINYFISH_API_KEY", "").strip()
    if not api_key:
        return {}
    return TinyFishReadOnlyClient(api_key=api_key).tool_handlers()


def tinyfish_plugin_bundle_from_env() -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    """Return canonical registry schemas and key-gated TinyFish handlers.

    Schemas are available independently of credentials so callers can construct
    a task contract and report a precise missing-handler blocker. The handler
    mapping is empty unless TINYFISH_API_KEY is configured in the runtime.
    """
    schemas: dict[str, dict[str, Any]] = {}
    for item in TINYFISH_TOOL_CATALOGUE:
        tool_id = item["tool_id"]
        if tool_id in schemas:
            raise TinyFishClientError(f"duplicate TinyFish catalogue tool ID: {tool_id}")
        schemas[tool_id] = json.loads(json.dumps(item["input_schema"]))
    return schemas, tinyfish_tool_handlers_from_env()
