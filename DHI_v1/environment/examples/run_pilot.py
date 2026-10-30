"""Run a deterministic DHI-v1 environment smoke task and write a JSONL trace.

The action sequence is scripted to validate the environment and trace contract.
It is NOT a model-generated trajectory and must NOT be used as training data.
"""
from __future__ import annotations

import argparse
import json
import tempfile
from pathlib import Path

from DHI_v1.environment.dhi_env import DHIEnvironment, TaskSpec


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("outputs/pilot_trace.jsonl"))
    args = parser.parse_args()
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="dhi-v1-pilot-") as temporary:
        workspace = Path(temporary) / "workspace"
        (workspace / "src").mkdir(parents=True)
        (workspace / "README.md").write_text("# Demo repository\n\nA small repository for DHI environment validation.\n", encoding="utf-8")
        (workspace / "src" / "api.py").write_text(
            'def healthcheck():\n    return {"status": "ok"}\n', encoding="utf-8"
        )
        (workspace / "pyproject.toml").write_text("[project]\nname = 'demo'\n", encoding="utf-8")

        task = TaskSpec(
            task_id="dhi-v1-pilot-discover-search-update-readme",
            prompt="Find the health-check endpoint in the source and document it in the README.",
            goal="The README documents the verified health-check function location without changing source or project configuration.",
            hard_constraints=["Do not modify source code or project configuration."],
            postconditions=[
                {"type": "contains", "path": "README.md", "text": "Health-check function: src/api.py#healthcheck"}
            ],
            protected_paths=["src/api.py", "pyproject.toml"],
            visible_tool_ids=["fs.list_files", "fs.read_file", "fs.append_file"],
            split="smoke_fixture_not_training",
            metadata={
                "origin": "hand-authored deterministic smoke fixture",
                "model_generated": False,
                "training_eligible": False,
            },
        )

        env = DHIEnvironment(workspace, trace_path=output)
        env.begin_task(task)

        actions = [
            {
                "tool_id": "fs.list_files",
                "arguments": {"path": ""},
                "subgoal": "Inspect repository structure",
            },
            {
                "tool_id": "catalog.search",
                "arguments": {"query": "search source code for text", "limit": 5},
                "subgoal": "Discover a capability absent from the initially visible tools",
            },
            {
                "tool_id": "fs.search_text",
                "arguments": {"query": "def healthcheck", "path": "src"},
                "subgoal": "Find the health-check implementation",
            },
            {
                "tool_id": "fs.read_file",
                "arguments": {"path": "src/api.py"},
                "subgoal": "Inspect the source evidence",
            },
            {
                "tool_id": "fs.append_file",
                "arguments": {"path": "README.md", "content": "\nHealth-check function: src/api.py#healthcheck\n"},
                "expected_effects": {
                    "changed_paths": ["README.md"],
                    "unchanged_paths": ["src/api.py", "pyproject.toml"],
                },
                "subgoal": "Document the verified function location",
            },
        ]
        for action in actions:
            result = env.run_action(action)
            if not result.ok:
                print(json.dumps({"ok": False, "error": result.error, "trace": str(output)}, indent=2))
                return 1

        closure = env.close_task()
        summary = {
            "ok": closure["success"],
            "task_id": task.task_id,
            "action_count": len(actions),
            "event_count": len(env.events),
            "verified_postconditions": closure["verified_postconditions"],
            "verified_protected_paths": closure["verified_protected_paths"],
            "trace_path": str(output),
            "training_eligible": False,
        }
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return 0 if closure["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
