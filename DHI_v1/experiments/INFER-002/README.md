# INFER-002 — OpenRouter base-inference access preflight

**Date:** 2026-11-03  
**Status:** blocked — zero remaining account credits  
**Evidence class:** read-only catalogue and account-credit audit  
**No inference call was made.**

## Finding

The connected OpenRouter route now exposes both DHI model candidates. This resolves the previous catalogue-availability blocker, but not the execution or benchmark blocker.

| Role | Model | Context | PrimeIntellect price / 1M input-output tokens |
|---|---|---:|---:|
| Primary candidate | `qwen/qwen3.6-35b-a3b` | 262,144 | $0.01 / $0.092 |
| Challenger | `openai/gpt-oss-20b` | 131,072 | $0.009 / $0.038 |

PrimeIntellect serves Qwen in fp8 and GPT-OSS in fp4. Both support `tool_choice=auto`; GPT-OSS's PrimeIntellect endpoint does not advertise `tool_choice=required`. Therefore the matched initial smoke must use the shared `auto` mode. A forced-tool condition cannot be used unless a different matched route is selected and frozen.

GPT-OSS requires its reasoning parameter and offers low/medium/high effort (medium default). Qwen's reasoning is on by default but is not mandatory. These settings must be recorded and held constant in the candidate adapter protocol.

## Credit gate

The live account response returned **$0 total credits remaining** and $0.20190338 historical usage. No model generation was called. No charge was created by this read-only preflight.

## Decision

Do not launch inference yet. The next executable step is a small, matched base-model smoke on both model IDs through a frozen provider, using the same task prompts, tool schemas, budgets and decode rules. Only after the inference route and trace adapter pass should the larger Stage A evaluation begin.

This is not a model result, a benchmark score, or launch approval. DHI still has no recorded model-generated trajectories, no DHI-trained weights, and no verified comparative capability result.

Structured source evidence: [manifest.json](manifest.json).
