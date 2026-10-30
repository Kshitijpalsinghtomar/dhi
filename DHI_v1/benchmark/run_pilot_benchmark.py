"""Run supported DHI-v1 file-workspace pilot cases against a served model.

Requires DHI_MODEL_BASE_URL, DHI_MODEL_API_KEY, and DHI_MODEL_NAME.
The pilot is not the frozen 120-task benchmark or a training dataset.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from DHI_v1.benchmark.runner import run_pilot_benchmark
from DHI_v1.environment.agent_runner import OpenAICompatibleChatClient


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=Path("DHI_v1/benchmark/pilot_cases.json"))
    parser.add_argument("--fixture", type=Path, default=Path("DHI_v1/environment/fixtures/basic_repo"))
    parser.add_argument("--output", type=Path, default=Path("outputs/pilot_benchmarks"))
    parser.add_argument("--max-model-turns", type=int, default=16)
    parser.add_argument("--max-tool-calls", type=int, default=48)
    args = parser.parse_args()

    base_url = os.environ.get("DHI_MODEL_BASE_URL", "").strip()
    api_key = os.environ.get("DHI_MODEL_API_KEY", "")
    model_name = os.environ.get("DHI_MODEL_NAME", "").strip()
    missing = [name for name, value in (
        ("DHI_MODEL_BASE_URL", base_url),
        ("DHI_MODEL_API_KEY", api_key),
        ("DHI_MODEL_NAME", model_name),
    ) if not value]
    if missing:
        raise SystemExit("Missing model endpoint configuration: " + ", ".join(missing))

    client = OpenAICompatibleChatClient(base_url=base_url, api_key=api_key, model=model_name)
    report = run_pilot_benchmark(
        client,
        model_name=model_name,
        suite_path=args.suite,
        fixture_root=args.fixture,
        output_root=args.output,
        max_model_turns=args.max_model_turns,
        max_tool_calls=args.max_tool_calls,
    )
    print(
        f"DHI pilot: {report['passed_cases']}/{report['case_count']} "
        f"cases passed ({report['pass_rate']:.1%})"
    )
    print(f"Report: {report['report_path']}")
    return 0 if report["passed_cases"] == report["case_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
