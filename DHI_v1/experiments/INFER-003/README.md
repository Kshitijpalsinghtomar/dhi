# INFER-003 — Live base-model route and runtime-readiness recheck

**Date:** 2026-11-03  
**Status:** blocked — zero credits and no OpenRouter secret attached to the DHI verifier  
**Evidence class:** read-only account, model endpoint and Deepnote integration inspection  
**No inference call was made.**

## Findings

### Account balance

OpenRouter `get_credits` returned:
- `total_credits = 0`
- `total_usage = 0.20190338`

The selected candidates have usable paid endpoints, but the account cannot call them until credits are added.

### Pinned common provider route

Live endpoint inspection found a common PrimeIntellect route for both required candidates:

| Candidate | Provider / quantization | Input price per 1M | Output price per 1M | Tool calls | `tool_choice` |
|---|---|---:|---:|---|---|
| `qwen/qwen3.6-35b-a3b` | PrimeIntellect / fp8 | $0.011 | $0.100 | Supported | auto, required |
| `openai/gpt-oss-20b` | PrimeIntellect / fp4 | $0.016 | $0.069 | Supported | auto |

Both endpoints were live in the endpoint catalogue at inspection time. Qwen's reported 1-day uptime was 100%; GPT-OSS's was approximately 99.93%. These are provider telemetry snapshots, not service guarantees.

**Frozen common mode:** `tool_choice=auto`. GPT-OSS's PrimeIntellect route does not advertise `required`, so forced-tool calls must not be used in a supposedly matched comparison.

No free endpoint was returned for the exact Qwen3.6-35B-A3B or GPT-OSS-20B candidate slugs. Free tool-capable alternatives exist in the wider catalogue, including Gemma 4 31B, but they are not substitutes for the primary/mandatory-challenger comparison. Gemma remains optional only when multimodal/UI tasks are in scope.

### DHI runtime boundary

The existing DHI runner already has a standard OpenAI-compatible client and supports dynamic function schemas. Its runtime configuration requires:
- `DHI_MODEL_PROVIDER=openai_compatible`
- `DHI_MODEL_BASE_URL=https://openrouter.ai/api/v1`
- `DHI_MODEL_API_KEY` supplied from a secret store
- `DHI_MODEL_NAME` set to the exact model slug

The verifier project currently has the `TINYFISH` environment integration only. A Deepnote workspace integration search for `OPENROUTER` returned none. The OpenRouter MCP `send_message` action available to ChatGPT accepts plain-text prompt messages; it does not accept function-tool schemas, so it cannot replace the OpenAI-compatible API call inside the DHI runner.

A second runtime gap was found: `OpenAICompatibleChatClient` sends `tool_choice=auto`, but it does not yet send an OpenRouter `provider` routing object. The experiment requires pinning PrimeIntellect to prevent provider/quantization drift. Add the optional provider restriction and its tests before inference; do not modify the client silently during a frozen benchmark run.

## Cost planning scenario

Illustrative first-order estimate only, assuming 120 Stage A tasks, a per-task aggregate budget of 40,000 input tokens and 12,000 output tokens:

- Qwen3.6-35B-A3B: about $0.197.
- GPT-OSS-20B: about $0.176.
- Both candidates: about $0.373 before additional tool-loop overhead or retries.

Real spend depends on actual conversation growth, reasoning tokens, tool-call turns and retries. The final preflight must estimate costs from measured pilot token counts and enforce an aggregate hard cap. These figures are not an invoice or a sufficient budget by themselves.

## Next actions

1. Finish ORBIT-VERIFY-004 exact-head regression.
2. Add the optional PrimeIntellect provider pin to the compatible client and test that the request body is deterministic; keep `tool_choice=auto`.
3. Provision `DHI_MODEL_API_KEY` securely as a Deepnote project environment secret; never place it in code, Git, notebook source or logs.
4. Add only the minimum required credits after agreeing a measured request budget.
5. Run a small matched smoke against both models; preserve exact model/provider/quantization, tool schemas, prompts, reasoning effort, decoding, token budgets and raw traces.
6. Do not open Stage A until the benchmark tasks and graders pass their validation gates.

## Decision

No model inference, model selection, training, data generation or paid request was performed in this experiment. The exact candidate routes are technically available, but the zero-credit account, absent runtime key and missing provider pin prevent a reproducible model-runner evaluation.


## Provider pin confirmation — 2026-11-03

A live OpenRouter `list_providers` query confirms the exact provider slug is **`primeintellect`** (display name `PrimeIntellect`). OpenRouter's own documentation search confirms provider routing is supplied in the request body for Chat Completions and Responses. The frozen hard-pin configuration for the DHI runner is:

```json
{"provider":{"only":["primeintellect"],"allow_fallbacks":false}}
```

This makes the provider constraint an allowlist and denies fallback to another provider. Use `tool_choice=auto` for both model candidates because GPT-OSS-20B's PrimeIntellect endpoint does not advertise `required`.

This resolves the *routing-configuration unknown*, not the implementation or funding blockers. The DHI client still needs a tested optional provider-routing field, the Deepnote verifier needs `DHI_MODEL_API_KEY` in a secret-backed environment integration, and the OpenRouter account must have a measured spend cap before any request. No inference call was made.
