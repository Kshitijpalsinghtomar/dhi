"""Run one model task through Adaption Responses or an OpenAI-compatible endpoint.

For Adaption: set ADAPTION_API_KEY, DHI_MODEL_PROVIDER=adaption, and DHI_MODEL_NAME.
For another provider: set DHI_MODEL_PROVIDER=openai_compatible, DHI_MODEL_BASE_URL,
DHI_MODEL_API_KEY, and DHI_MODEL_NAME.

This is an integration pilot, not a benchmark score or training-data exporter.
"""
from __future__ import annotations

import json
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

from DHI_v1.environment.agent_runner import client_from_env, run_agent_task, tool_handlers_from_client
from DHI_v1.environment.dhi_env import DHIEnvironment, TaskSpec
from DHI_v1.environment.fixture_manager import materialize_fixture


def main() -> int:
    client, model_name = client_from_env()

    repo_root = Path(__file__).resolve().parents[3]
    fixture_root = Path(__file__).parents[1] / "fixtures" / "basic_repo"
    run_id = uuid.uuid4().hex[:12]
    output_dir = repo_root / "outputs" / "model_pilots"
    output_dir.mkdir(parents=True, exist_ok=True)
    trace_path = output_dir / (
        f"{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{run_id}.jsonl"
    )

    with tempfile.TemporaryDirectory(prefix="dhi-v1-model-pilot-") as temporary:
        workspace = Path(temporary) / "workspace"
        materialize_fixture(fixture_root, workspace)
        task = TaskSpec(
            task_id=f"dhi-v1-model-pilot-{run_id}",
            prompt=(
                "Inspect the repository, locate the healthcheck function, and add its "
                "exact file/function location to README.md. Do not modify source code "
                "or project configuration. If text search is needed and not visible, "
                "discover the appropriate workspace tool first."
            ),
            goal="README documents src/api.py#healthcheck; source and project configuration remain byte-identical.",
            hard_constraints=["Do not modify src/api.py", "Do not modify pyproject.toml"],
            visible_tool_ids=["fs.list_files", "fs.read_file", "fs.append_file"],
            protected_paths=["src/api.py", "pyproject.toml"],
            postconditions=[
                {"type": "contains", "path": "README.md", "text": "Health-check function: src/api.py#healthcheck"}
            ],
            split="integration_pilot_not_benchmark",
            metadata={
                "origin": "pinned local fixture",
                "fixture_id": "dhi-v1-basic-repository",
                "model_name": model_name,
                "training_eligible": False,
            },
        )
        environment = DHIEnvironment(workspace, trace_path=trace_path, tool_handlers=tool_handlers_from_client(client))
        result = run_agent_task(environment, task, client, max_model_turns=12, max_tool_calls=24)

    summary = {
        "run_id": run_id,
        "model_name": model_name,
        "stopped_reason": result.stopped_reason,
        "model_turn_count": result.model_turn_count,
        "tool_call_count": result.tool_call_count,
        "final_answer": result.final_answer,
        "verified_closure": result.closure,
        "trace_path": str(trace_path),
        "training_eligible": False,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0 if result.closure.get("success") and result.final_answer else 1


if __name__ == "__main__":
    raise SystemExit(main())
