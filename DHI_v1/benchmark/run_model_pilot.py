"""Run the model-facing DHI development pilot using runtime environment config.

Example:
  DHI_MODEL_PROVIDER=openai_compatible
  DHI_MODEL_BASE_URL=https://openrouter.ai/api/v1
  DHI_MODEL_NAME=<exact-model-slug>
  DHI_MODEL_API_KEY=<set through your secret manager, never commit it>
  python -m DHI_v1.benchmark.run_model_pilot

This invokes the configured model and may incur provider charges. It does not
run automatically on import. The suite is a development pilot, not a frozen
benchmark, and results are not training data.
"""
from __future__ import annotations

import json
import os
from pathlib import Path


def main() -> int:
    from DHI_v1.benchmark.runner import run_pilot_benchmark
    from DHI_v1.environment.agent_runner import client_from_env

    project_root = Path(__file__).resolve().parents[2]
    dhi_root = project_root / "DHI_v1"
    output_root = Path(os.environ.get(
        "DHI_OUTPUT_ROOT", str(project_root / "outputs" / "model_pilot")
    )).expanduser()

    client, model_name = client_from_env()
    report = run_pilot_benchmark(
        client,
        model_name=model_name,
        suite_path=dhi_root / "benchmark" / "pilot_cases.json",
        fixture_root=dhi_root / "environment" / "fixtures" / "basic_repo",
        output_root=output_root,
        max_model_turns=int(os.environ.get("DHI_MAX_MODEL_TURNS", "16")),
        max_tool_calls=int(os.environ.get("DHI_MAX_TOOL_CALLS", "48")),
    )
    print(json.dumps({
        "benchmark_id": report["benchmark_id"],
        "model_name": report["model_name"],
        "case_count": report["case_count"],
        "passed_cases": report["passed_cases"],
        "pass_rate": report["pass_rate"],
        "report_path": report["report_path"],
        "training_eligible": report["training_eligible"],
    }, indent=2))
    return 0 if report["case_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
