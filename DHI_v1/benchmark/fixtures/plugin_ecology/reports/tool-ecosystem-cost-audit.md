# Tool ecosystem cost and execution-boundary audit

**Task:** Resume the persistent tool-ecosystem audit  
**Checkpoint:** `checkpoints/tool-ecosystem-audit-A.md`  
**Pinned source revision:** `8c6295255c88b0baea04529a475af8f85a946cd6`  
**Discovery snapshot dates:** 2026-11-03

## Executive finding

The pinned discovery snapshots expose structured package, security and research capabilities. In the recorded discovery calls, tool discovery cost **0 credits**. Several provider executions cost credits, so discovery and execution must be treated separately. No paid provider capability was invoked for this audit.

The costs below are those advertised in the dated snapshots; this report does not claim a live price refresh or a retrieved package, vulnerability or paper result.

## Package registry capabilities

The package metadata snapshot and its recovery note establish:

- `package-registry-metadata-download-stats/packages/package` — retrieve a package record, including latest version, publication time, licence, repository links, version count and download summary where available. Required inputs: `registry` (npm, pypi, crates or maven) and `name`. Provider execution cost: **1 credit**.
- `package-registry-metadata-download-stats/packages/dependents` — retrieve reverse-dependency information for a package/version. Provider execution cost: **1 credit**.

The first broad discovery returned a reranking fallback but still included candidate matches and a scoped `nextTool` recovery. A provider-filtered follow-up exposed the full package-record contract. The correct recovery is to inspect usable fallback candidates and narrow discovery to the provider/capability, not to report that no tools were found or blindly retry the same broad query.

Discovery cost was **0 credits**. Neither package capability was executed.

## Security capabilities

The security discovery snapshot lists three distinct capabilities, each with a provider execution cost of **5 credits**:

- `github-com/repositories/advisory` — retrieve one GitHub Advisory record by GHSA ID, CVE ID or advisory URL; output includes severity, CVSS/EPSS, affected packages and patched versions.
- `osv-dev/vulnerabilities/query` — query a package/ecosystem/version or PURL; output includes aliases, severity, affected ranges and fixed versions.
- `github-com/repositories/search_advisories` — browse/filter advisory records by ecosystem, severity, CWE and dates.

These serve different jobs: one known advisory, package/version vulnerability assessment, and broader advisory browsing. The correct capability depends on the actual question. No security provider execution was made.

## Research capabilities

The research discovery snapshot lists:

- `semanticscholar-org/papers/search_papers` — topic search; **5 credits**.
- `semanticscholar-org/papers/get_paper` — metadata and abstract retrieval for a known paper ID, DOI, arXiv ID or supported URL; **5 credits**.
- `semanticscholar-org/papers/get_citations` — forward citation expansion with contexts/intents where available; **5 credits**.
- `firecrawl-research-index/inspect` — metadata and abstract for an index-native `paperId`; **0 credits** in the discovered contract.

The zero-credit index inspection is not interchangeable with Semantic Scholar citation expansion. It only accepts a paper ID produced by its own indexed-search workflow and returns the index's metadata/abstract.

No Semantic Scholar or research-index execution was performed during this audit.

## Operational decision table

| Need | Capability | Discovery cost | Provider execution cost |
|---|---|---:|---:|
| Current package record | `packages/package` | 0 | 1 credit |
| Reverse dependencies | `packages/dependents` | 0 | 1 credit |
| One known GHSA/CVE | `repositories/advisory` | 0 | 5 credits |
| Vulnerabilities for a package/version | `vulnerabilities/query` | 0 | 5 credits |
| Browse/filter advisories | `repositories/search_advisories` | 0 | 5 credits |
| Search academic papers | `papers/search_papers` | 0 | 5 credits |
| Read a known paper record | `papers/get_paper` | 0 | 5 credits |
| Expand forward citations | `papers/get_citations` | 0 | 5 credits |
| Inspect indexed paper metadata | `firecrawl-research-index/inspect` | 0 | 0 |

## Evidence sources and execution boundary

The audit re-read the checkpoint and all five pinned supporting sources at the checkpoint commit:

1. `plugin_tool_registry.json`
2. `discovery_snapshots/firecrawl_package_metadata_2026-11-03.md`
3. `discovery_snapshots/firecrawl_security_provider_discovery_2026-11-03.md`
4. `discovery_snapshots/firecrawl_research_provider_discovery_2026-11-03.md`
5. `discovery_snapshots/firecrawl_package_recovery_2026-11-03.md`

The tool registry lists 15 connected tool contracts. The provider costs and capability distinctions above are derived from the dated discovery snapshots, not from executed provider queries.

No paid provider action was executed, no credits were spent, and no external service was mutated. A discovery result is not authorization to execute a paid capability; any future paid run requires an explicit cost budget before invocation.
