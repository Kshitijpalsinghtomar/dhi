from __future__ import annotations

import os
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pytest

from DHI_v1.benchmark.plugin_execution import prepare_plugin_execution
from DHI_v1.benchmark.plugin_task_loader import load_plugin_task
from DHI_v1.environment.tinyfish_client import (
    FETCH_TOOL_ID,
    SEARCH_TOOL_ID,
    TINYFISH_TOOL_CATALOGUE,
    TinyFishReadOnlyClient,
    tinyfish_plugin_bundle_from_env,
)


ROOT = Path(__file__).resolve().parents[3]
MANIFEST = ROOT / "DHI_v1" / "benchmark" / "task_manifest.json"
REGISTRY = ROOT / "DHI_v1" / "benchmark" / "fixtures" / "plugin_ecology" / "plugin_tool_registry.json"


def test_tinyfish_runtime_ids_match_the_canonical_plugin_registry():
    assert SEARCH_TOOL_ID == "mcp__TinyFish__search"
    assert FETCH_TOOL_ID == "mcp__TinyFish__fetch_content"
    assert {item["tool_id"] for item in TINYFISH_TOOL_CATALOGUE} == {
        SEARCH_TOOL_ID, FETCH_TOOL_ID
    }


def test_bundle_keeps_schemas_available_but_no_handlers_without_runtime_key(monkeypatch):
    monkeypatch.delenv("TINYFISH_API_KEY", raising=False)

    schemas, handlers = tinyfish_plugin_bundle_from_env()

    assert set(schemas) == {SEARCH_TOOL_ID, FETCH_TOOL_ID}
    assert set(handlers) == set()


def test_bundle_pairs_canonical_schemas_and_handlers_when_key_is_configured():
    fake_handlers = {
        "mcp__TinyFish__search": lambda arguments: {"synthetic": "search", "arguments": arguments},
        "mcp__TinyFish__fetch_content": lambda arguments: {"synthetic": "fetch", "arguments": arguments},
    }
    with patch.dict(os.environ, {"TINYFISH_API_KEY": "unit-test-secret"}):
        with patch.object(TinyFishReadOnlyClient, "tool_handlers", return_value=fake_handlers):
            schemas, handlers = tinyfish_plugin_bundle_from_env()

    assert set(schemas) == set(handlers) == {SEARCH_TOOL_ID, FETCH_TOOL_ID}
    assert schemas[SEARCH_TOOL_ID]["required"] == ["query"]
    assert schemas[FETCH_TOOL_ID]["required"] == ["urls"]


def test_live_manifest_tinyfish_task_can_be_prepared_from_the_runtime_bundle():
    fake_handlers = {
        "mcp__TinyFish__search": lambda arguments: {"synthetic": "search", "arguments": arguments},
        "mcp__TinyFish__fetch_content": lambda arguments: {"synthetic": "fetch", "arguments": arguments},
    }
    base_plan = load_plugin_task(MANIFEST, REGISTRY, "ORBIT-A-S02-001")
    # A copy with execution explicitly enabled tests the adapter boundary only.
    # The source manifest continues to keep all model runs disabled.
    plan = replace(base_plan, model_runs_allowed=True)

    with patch.dict(os.environ, {"TINYFISH_API_KEY": "unit-test-secret"}):
        with patch.object(TinyFishReadOnlyClient, "tool_handlers", return_value=fake_handlers):
            schemas, handlers = tinyfish_plugin_bundle_from_env()
            prepared = prepare_plugin_execution(
                plan, schemas=schemas, handlers=handlers
            )

    result = prepared.dispatch(
        prepared.tool_name_by_id[SEARCH_TOOL_ID],
        {"query": "synthetic canonical adapter smoke"},
    )
    assert result == {
        "synthetic": "search",
        "arguments": {"query": "synthetic canonical adapter smoke"},
    }
    assert set(prepared.tool_name_by_id) == {SEARCH_TOOL_ID, FETCH_TOOL_ID}
