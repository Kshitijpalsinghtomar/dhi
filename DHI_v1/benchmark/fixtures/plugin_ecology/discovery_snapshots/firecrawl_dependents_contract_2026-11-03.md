# Firecrawl package-dependents discovery snapshot

- Discovery date: 2026-11-03
- Tool: `mcp__Firecrawl__firecrawl_find_tools`
- Provider filter: `package-registry-metadata-download-stats`
- Capability filter: `packages/dependents`
- Discovery call cost: 0 credits

## Capability contract

- Provider: `package-registry-metadata-download-stats`
- Capability: `packages/dependents`
- Execution cost: **1 credit**
- Required inputs: `registry` and `name`
- Optional input: exact `version`; if omitted, the default/latest version is used.
- Optional crates-only input: `sample` (0–100), default 20.

## Output

The capability reports total/direct/indirect package dependents for a version from deps.dev. For crates it also returns package-wide reverse-dependency counts from crates.io and an optional sample of dependent crates. Output includes registry/name/version, source URLs, warnings and observation time.

## Distinction

This capability is not the package-record lookup:
- `packages/package` answers latest version, publish time, licence, repository, downloads and package metadata.
- `packages/dependents` answers how many packages depend on the selected version.

No provider execution occurred. Discovery was free; the capability's execution is one credit and was not authorized.
