# INFER-001 — Adaption Hosted Inference Preflight

**Date:** 2026-11-02  
**Type:** access/integration preflight (not a model experiment)  
**Status:** BLOCKED — no credentialed hosted-inference route available in the connected execution context  
**Programme:** DHI-v1 / ORBIT  
**Controlling state:** `DHI_v1/WORKSPACE.md`

## Question

Can the current Adaption account expose at least one exact hosted model ID through the authenticated hosted-model catalogue, and can the existing DHI model-facing pilot call that model through Adaption Responses without changing the selected provider or research protocol?

## Procedure actually performed

1. Re-read the current DHI workspace, Git-first workflow, model-selection/Adaption plan, and development-pilot instructions at repository head `dd5268e62f9e8905c687b729094d5b12af9584f4`.
2. Inspected the connected Adaption tool inventory.
3. Queried the current Adaption training registry with `list_training_models`.
4. Inspected the existing Deepnote project metadata and its attached workspace integrations without reading or printing any secret values.
5. Inspected the repository's existing hosted-model catalogue CLI and Responses adapter implementation.
6. Did not make an authenticated `GET /api/v1/models?type=hosted` or `POST /api/v1/responses` request because no credential was available through a secure execution integration.

## Results

### Adaption training registry

The connected Adaption training registry currently lists the repository's selected candidates as training-compatible:

- `Qwen/Qwen3.6-35B-A3B` — SFT/DPO, LoRA.
- `openai/gpt-oss-20b` — SFT/DPO, LoRA.
- `google/gemma-4-31B-it` — SFT/DPO, LoRA/full.

This is **training-registry evidence only**. It does not establish that any of these IDs is available through hosted inference for the account's API key. No candidate is designated a measured winner.

### Connected Adaption action boundary

The available Adaption MCP actions include `list_training_models`, dataset operations, recommendations, and AutoScientist run operations. They do not include the hosted-model listing endpoint or Responses inference operation required by DHI's existing adapter.

### Deepnote runtime inspection

The existing project `DHI — ORBIT Research Lab` (`5a197ce3-f071-4a39-b2e4-937e7a52489a`) has no integrations attached. The workspace-wide integration inventory exposes only `[Demo] Snowflake`; no environment/secret integration is available to attach for an Adaption API key.

The existing project file inventory also contains unrelated DPAK experiment directories. It was not used to run DHI inference or to inspect secret values. Do not mix DHI execution with that workspace's unrelated research assets.

### Repository implementation

The existing code already provides the correct route:

```bash
python -m DHI_v1.environment.examples.list_adaption_models
```

It uses `ADAPTION_API_KEY` (or `DHI_ADAPTION_API_KEY`) to query the hosted-only model catalogue.

After an exact hosted model ID is returned and provider/cost are approved, the model-facing development pilot is:

```bash
DHI_MODEL_PROVIDER=adaption
DHI_MODEL_NAME=<exact-hosted-model-id>
python -m DHI_v1.benchmark.run_model_pilot
```

The API key must be injected through a secure runtime secret. It must not be pasted into chat, committed to Git, written into notebook output, or placed in experiment traces.

## Decision

**Keep the hosted-inference gate BLOCKED.**

Do not:
- infer hosted availability from the training registry;
- guess a hosted ID;
- switch provider to bypass the Adaption boundary;
- launch training or generate another dataset;
- claim the model-facing pilot ran;
- use the mixed DPAK/DHI Deepnote project as an execution environment.

## Required unblock

Provide a secure runtime path that injects `ADAPTION_API_KEY` into a clean DHI-only execution environment. Then run only the existing hosted-model listing CLI first. Record the exact returned model IDs and the access result here before running inference.

If the hosted endpoint rejects the key or returns no usable hosted model, record the actual HTTP/error response (with secrets redacted) and remain blocked. No provider change is implied.

## Evidence classification

- Training registry refresh: **observed platform metadata**.
- Hosted-model availability: **not tested**.
- Responses inference: **not tested**.
- DHI model capability: **no result**.
- DHI training: **not launched / not authorized**.
- Adaption credits spent in this preflight: **none**.

## Reproducibility metadata

See `manifest.json` for inspected repository revision, tool surface, candidate IDs, runtime metadata, and exact test boundaries.

## Follow-up isolated runtime probe — 2026-11-02

A clean, separate Deepnote notebook project was created to check only whether `ADAPTION_API_KEY` or `DHI_ADAPTION_API_KEY` is present in its runtime. The probe source is committed at `DHI_v1/experiments/INFER-001/check_runtime_secret_presence.py` (commit `5a649db4635245f4ece1895f1931ea3a2dcd5c94`). It emits presence booleans only and makes no network request.

- Isolated project: `DHI — Isolated Runtime Preflight`, project ID `2eb8d02b-b505-4b39-a33a-32aeda2e1cc4`.
- Notebook ID: `08586f8da34c456fb544baccb69ebe3e`.
- Probe block ID: `7bcfdf38fd0a400e989a4d6064e1caed`.
- A detached read-only run was requested.
- Deepnote rejected run creation **before execution**: `Your plan quota for parallel running projects has been exceeded. Please stop one of your running projects.`

Therefore secret presence was **not measured**. No project was stopped, no secret was read/emitted, and no network request or Adaption API call occurred. The isolated project is left available for a later retry. Do not use the mixed DHI/DPAK workspace instead.

### Additional unblock requirement

The isolated project needs the Adaption key supplied through a secure project/runtime secret, and Deepnote needs one parallel-running-project slot available. Do not stop any existing user project automatically; request user action before doing so.



## Follow-up secret-presence run — 2026-11-02

The previously blocked detached run was accepted and completed.

- Run ID: `b39c478a-3268-439c-af30-d71ba9b40907`.
- Status: `success`.
- Notebook: `08586f8da34c456fb544baccb69ebe3e`.
- Probe block: `7bcfdf38fd0a400e989a4d6064e1caed`.
- Execution: 3 ms.
- Output: `ADAPTION_API_KEY=false`, `DHI_ADAPTION_API_KEY=false`, `any_adaption_secret_present=false`, `network_requests_made=0`, `secret_values_emitted=false`.

**Result:** neither supported key variable is configured in this isolated project runtime. This is a measured runtime result, not a key-validity check. No hosted-model request was made.

### Secure secret configuration (user action)

Deepnote stores project secrets through an **Environment variables** integration. In the Deepnote workspace, create or open an Environment variables integration and add `ADAPTION_API_KEY` with the key value; then connect that integration to the isolated project `DHI — Isolated Runtime Preflight`. Do not put the value in notebook code, notebook inputs, Git, or chat. Deepnote documents this integration flow at https://deepnote.com/docs/environment-variables.

After the integration is attached, rerun the presence-only probe. The next check should report `ADAPTION_API_KEY=true` without exposing the value; only then run `python -m DHI_v1.environment.examples.list_adaption_models`.


## Secure runtime configured — 2026-11-02

The user created a Deepnote **Environment variables** integration named `ADAPTION`. It was attached to the isolated DHI project:

- Project: `DHI — Isolated Runtime Preflight` (`2eb8d02b-b505-4b39-a33a-32aeda2e1cc4`).
- Integration: `ADAPTION`, type `env`, integration ID `999bb21e-9bfd-4071-a2bc-d26590958de7`.
- Presence probe run: `9e34f54b-0acf-455b-b44a-9c28173a1462` (success).
- Result: `ADAPTION_API_KEY=true`; `DHI_ADAPTION_API_KEY=false`; no secret values emitted; zero network requests in this probe.

The key is now present in this isolated project runtime. This proves only environment-variable presence, not that the key is valid or that any hosted models are enabled.

### Next action

Run the existing `python -m DHI_v1.environment.examples.list_adaption_models` command from a pinned checkout of this repository in this project. This makes the authenticated `GET /api/v1/models?type=hosted` request only. Record exact returned IDs or a redacted error; do not call inference until the catalogue request succeeds.
