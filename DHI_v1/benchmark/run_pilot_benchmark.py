"""Run supported DHI-v1 file-workspace pilot cases against a served model.

Provider selection: DHI_MODEL_PROVIDER=adaption with ADAPTION_API_KEY, or
DHI_MODEL_PROVIDER=openai_compatible with DHI_MODEL_BASE_URL and DHI_MODEL_API_KEY.
Both require DHI_MODEL_NAME. This is not the frozen 120-task benchmark.
"""
from __future__ import annotations

import argparse
from pathlib import Path

from DHI_v1.benchmark.runner import run_pilot_benchmark
from DHI_v1.environment.agent_runner import client_from_env, tool_handlers_from_client


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--suite", type=Path, default=Path("DHI_v1/benchmark/pilot_cases.json"))
    parser.add_argument("--fixture", type=Path, default=Path("DHI_v1/environment/fixtures/basic_repo"))
    parser.add_argument("--output", type=Path, default=Path("outputs/pilot_benchmarks"))
    parser.add_argument("--max-model-turns", type=int, default=16)
    parser.add_argument("--max-tool-calls", type=int, default=48)
    args = parser.parse_args()

    client, model_name = client_from_env()
    tool_handlers = tool_handlers_from_client(client)

    report = run_pilot_benchmark(
        client,
        model_name=model_name,
        suite_path=args.suite,
        fixture_root=args.fixture,
        output_root=args.output,
        max_model_turns=args.max_model_turns,
        max_tool_calls=args.max_tool_calls,
        tool_handlers=tool_handlers,
    )
    print(
        f"DHI pilot: {report['passed_cases']}/{report['case_count']} "
        f"cases passed ({report['pass_rate']:.1%})"
    )
    print(f"Report: {report['report_path']}")
    return 0 if report["passed_cases"] == report["case_count"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
