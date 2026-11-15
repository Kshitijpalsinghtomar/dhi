# Firecrawl package-tool discovery recovery snapshot

- Date: 2026-11-03
- Initial tool: `mcp__Firecrawl__firecrawl_find_tools`
- Initial query: software release latest version package registry metadata

## Initial degraded response

The initial broad semantic discovery returned a reranking fallback due to timeout. The response still contained matching provider items and a `nextTool` instruction that scoped discovery to the exact package provider/capability. It was not a total search failure and must not be reported as "no tools found."

## Recovery action

A second free discovery call used:
- provider: `package-registry-metadata-download-stats`
- capability: `packages/package`
- level: `tools`
- expanded fields: options and response

The scoped response returned exactly one item with the full contract:
- required inputs: `registry` (npm, pypi, crates, maven) and `name`;
- output includes `latest_version`, `latest_published_at`, `license`, `repository`, `downloads`, `dependents`, source URLs and warnings;
- discovery cost: 0 credits;
- provider execution cost: 1 credit.

## Boundary

No provider execution occurred. The correct recovery is to inspect the returned fallback items and run a provider-filtered discovery request; do not retry the same broad query blindly and do not execute the paid action.
