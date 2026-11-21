# Firecrawl provider discovery snapshot

- Discovery date: 2026-11-03
- Tool: `mcp__Firecrawl__firecrawl_find_tools`
- Query: software release latest version package registry metadata
- Mode: semantic tool discovery
- Discovery call credit cost: 0

## Discovered capability

- Provider: `package-registry-metadata-download-stats`
- Capability: `packages/package`
- Display name: Package record
- Execution credit cost: 1
- Required input: `registry` (one of npm, pypi, crates, maven) and `name`
- Output includes: package name, latest version, publication time, description, license, homepage/repository/issues links, version count, and download summary where available.

The separate `packages/dependents` capability reports reverse-dependency information and is not a substitute for the package's current version record.

## Execution boundary

This benchmark scenario is discovery-only. The paid `packages/package` capability was not executed; do not spend the one provider credit unless a run budget explicitly authorizes it. Discovery establishes the capability contract and execution cost, not a retrieved package record.
