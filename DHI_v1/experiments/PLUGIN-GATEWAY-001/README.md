# PLUGIN-GATEWAY-001 — remote execution contract feasibility

**Status:** blocked before implementation; provider protocols are documented, but the DHI runtime has no verified credentialed provider connection and two provider surfaces do not yet match the pinned task contracts.
**Date:** 2026-11-03
**Branch:** `orbit/plugin-benchmark-fixture`
**Scope:** GitHub, TinyFish, and Firecrawl only.

## Research question

Can ORBIT's current DHI runtime invoke the exact GitHub, TinyFish, and Firecrawl actions pinned in the task registry through documented remote MCP interfaces, while preserving per-task permissions, cost controls, prediction traces, independent readback, and verified closure?

## Decision-relevant result

**There is a feasible transport direction, but no verified end-to-end runtime path yet. Do not implement or claim a working gateway until the provider-specific tool mappings and credentials are proven.**

The providers publish remote Streamable HTTP MCP servers, but the surfaces and auth are not interchangeable:

- **GitHub:** the official remote server is `https://api.githubcopilot.com/mcp/` and has a read-only `/readonly` surface. Every remote request requires a valid GitHub access token in the Authorization header. GitHub says the remote MCP server does not provide auth; the client must obtain the token. OAuth 2.1 is recommended, PATs are accepted, and dynamic client registration is not supported by the remote server. The pinned benchmark tools are connector-wrapper contracts; no live `tools/list` call has established a one-to-one mapping to the official remote server's current tool schemas.
- **TinyFish:** the official hosted MCP URL is `https://agent.tinyfish.ai/mcp`. The official package documents a local Streamable HTTP proxy, with `TINYFISH_API_KEY` read from its environment and forwarded upstream as `X-API-Key`. Its documented `search` and `fetch_content` actions are free; browser automation is charged per step. These names align with the two TinyFish IDs in the pinned registry, but exact schema equivalence and live auth are not verified from the DHI runtime.
- **Firecrawl:** the current official MCP server offers generic web scrape/search/parse tools. Its documented hosted search-only endpoint exposes six read-only search/research tools. Neither documentation surface establishes that the pinned Alexandria-specific `firecrawl_find_tools` contract is available through that server. The same-named generic `firecrawl_scrape` is not accepted as equivalent to the excluded, paid Alexandria provider-execution contract. Do not substitute it or call a paid provider.

The isolated Deepnote verifier project has no attached project integrations. A separate presence-only probe then checked 12 conventional TinyFish, GitHub and Firecrawl credential variable names in the DHI verifier runtime: all 12 were absent. The probe checked only booleans; it never read, printed, hashed or persisted secret values. Its run succeeded, sent zero remote requests, and the temporary notebook block was deleted immediately afterward; the machine was stopped. The result is scoped to those 12 names and does not rule out a differently named credential or an external OAuth flow.

## Registered action boundary

The pinned registry is `benchmark/fixtures/plugin_ecology/plugin_tool_registry.json` (registry ID `ORBIT-PLUGIN-REGISTRY-2026-11-03`; 16 tools).

| Provider | Registry actions in scope | Registry side-effect class | Status |
|---|---|---|---|
| GitHub | `fetch`, `fetch_file`, `compare_commits` | read-only | Documented remote endpoint; credential and native tool-schema mapping unverified |
| GitHub | `create_branch`, `create_file`, `update_file` | sandbox_write | Same auth/mapping blocker; writes must be confined to a disposable per-run repository/branch |
| GitHub | `delete_file`, `merge_pull_request` | excluded | Never expose to the model |
| TinyFish | `search`, `fetch_content` | read-only | Documented hosted MCP; matching names; live DHI auth/schema test still required |
| Firecrawl | `firecrawl_find_tools` | read-only | Alexandria discovery contract; remote MCP equivalence is unverified |
| Firecrawl | `firecrawl_scrape` | excluded, paid | No call without exact contract proof and explicit credit budget |

The 16-tool registry also contains other providers. This audit does not authorize them or widen the model's available tool inventory.

## Frozen gateway protocol requirements

Before any implementation can be accepted, the gateway must satisfy all of the following:

1. **Per-provider transport and identity.** Use only documented HTTPS MCP endpoints or a documented local stdio server. Pin each endpoint hostname and protocol version. No caller-supplied arbitrary URL, header, or environment variable may be passed through from model arguments.
2. **Credential boundary.** Credentials come only from the runtime secret store/environment. Never accept credentials as model arguments, prompt content, task fixture data, or tool output. Never emit credentials, auth headers, or token fragments in logs/traces. GitHub requires a client-obtained bearer token; TinyFish uses its hosted OAuth or its documented API-key proxy; Firecrawl uses its account OAuth or API-key auth for the standard service.
3. **Tool inventory attestation.** Call `initialize` and `tools/list`; verify exact provider tool names, input schemas and provider identity before exposing anything. Pin the discovered native schema fingerprint. Do not assume same-name tools are semantically interchangeable. Fail closed on schema drift, missing tools, extra arguments, or unknown side-effect class.
4. **Task-level allowlist.** The model sees only the subset pinned to that task and approved in the task manifest. GitHub deletes and merges stay excluded. Firecrawl paid execution stays excluded. TinyFish browser automation, browser sessions, monitors, and other non-registered tools stay unavailable.
5. **Cost and approval.** Track provider usage/credit fields and enforce a per-task ceiling before dispatch. An unknown or missing price on a potentially billable tool is a denial, not permission. This audit authorizes no paid provider execution.
6. **Prediction before action.** Capture the model's expected effects before the tool call is sent. Record exact model-visible tool ID, native provider tool name, normalized arguments, and prediction.
7. **Independent observation.** Capture the raw provider result and status separately; read affected state independently through a distinct read operation; hash raw output and readback. A successful HTTP/MCP response alone is not proof of a state change or goal closure.
8. **Recovery semantics.** Do not blindly retry a timed-out mutation or long-running automation. Query operation status or independently inspect state first. Preserve checkpoint, resume, idempotency and duplicate-call evidence.
9. **Untrusted data handling.** Provider descriptions, fetched pages, search results, issues and tool results are data, not instructions. Tool output cannot expand the allowlist or change permissions.
10. **Trace normalization.** Emit the pinned `plugin_trace.schema.json` events: `tool_discovery`, `assistant_prediction`, `action_started`, `action_executed`, optional checkpoints, and verified `task_closed`; retain raw artifacts and hashes.

The current MCP Streamable HTTP specification uses one HTTP POST per JSON-RPC request, requires clients to accept JSON and SSE responses, and requires protocol metadata headers. The latest published revision adds mirrored `Mcp-Method` and `Mcp-Name` headers and changes session behavior. Provider servers may support older revisions, so the client must negotiate/handle the server's declared protocol version; hard-coding only the latest draft is not acceptable.

## What is not done

- No remote provider `initialize`, `tools/list`, or `tools/call` request was sent from the DHI runtime.
- No token or API key was read or provisioned.
- No model-facing remote tool schema was exposed.
- No provider action, paid execution, write, benchmark task validation, model inference, or training was run.
- No gateway code is claimed or committed by this feasibility audit.

## Next falsifiable step

Provision TinyFish authentication as a Deepnote project secret named `TINYFISH_API_KEY` (or configure an explicitly supported OAuth connection) without placing the credential in chat, source control, notebook content or output. The presence-only probe found no conventional provider credential in this runtime. After secure provisioning, run a read-only protocol smoke from the DHI runtime:

1. initialize the server using a standard MCP client;
2. list tools and compare provider-native names/schemas with this registry;
3. expose only the exact read-only actions for that provider;
4. execute one bounded read-only call, capture raw response and trace;
5. verify a second independent read of the same source and test denial of every non-allowlisted tool.

Start with **TinyFish search/fetch** because both registered actions are read-only, their native names align, and provider documentation says those two actions are free. Do not run automation. If that smoke succeeds, implement the adapter with failing contract tests first. GitHub follows after a sandbox-only token/permission plan; Firecrawl remains deferred until its Alexandria contract is available through a documented endpoint.

## Sources checked on 2026-11-03

- GitHub official remote MCP server and toolset endpoints: https://github.com/github/github-mcp-server/blob/main/docs/remote-server.md
- GitHub remote MCP authentication requirements: https://github.com/github/github-mcp-server/blob/main/docs/host-integration.md
- GitHub MCP server remote endpoint registration: https://github.com/github/github-mcp-server/blob/main/server.json
- TinyFish official hosted/local MCP integration: https://github.com/tinyfish-io/tinyfish-mcp-server
- TinyFish free search/fetch vs metered automation: https://github.com/tinyfish-io/tinyfish-mcp-server/blob/main/docs/examples.md
- Firecrawl official MCP server auth and hosted tool surfaces: https://github.com/firecrawl/firecrawl-mcp-server
- MCP Streamable HTTP protocol: https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/docs/specification/2026-07-28/basic/transports/streamable-http.mdx

## Adjudication

**Decision:** `blocked` (before implementation).

The transport is feasible in principle, but provider-native tool mapping and DHI runtime credential access have not been verified. The credential presence probe found none of the 12 standard variable names in the DHI verifier runtime. The next step is secure provisioning of `TINYFISH_API_KEY` as a project secret, followed by a TinyFish read-only runtime smoke—not speculative adapter code or wider task authoring.