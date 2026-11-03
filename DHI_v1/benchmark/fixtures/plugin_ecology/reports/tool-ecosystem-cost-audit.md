# Tool ecosystem cost and execution-boundary audit

**Task:** Resume the persistent tool-ecosystem audit  
**Checkpoint re-read:** `checkpoints/tool-ecosystem-audit-A.md`  
**Branch:** `orbit/tool-ecosystem-audit`  
**Source revision:** `8c6295255c88b0baea04529a475af8f85a946cd6`  
**Date:** 2026-11-03

## Executive finding

The connected ecosystem exposes useful structured research, package and security data capabilities. Their discovery actions are free in the recorded calls, but several provider executions cost credits. The correct policy is to use free discovery to understand the contract, then request an explicit run budget before any credit-consuming execution. No paid provider action was executed for this audit.

## Package registry capabilities

The pinned Firecrawl discovery records:
- `package-registry-metadata-download-stats/packages/package`: current registry record including latest version, latest publication time, licence, repository, download summary and dependent count. Inputs: `registry` and `name`. Execution cost: **1 credit**.
- `package-registry-metadata-download-stats/packages/dependents`: reverse-dependency information for a package/version. Execution cost: **1 credit**.

The package-provider discovery recovery note documents that the first broad search returned a reranking fallback but still contained candidates. A provider-filtered follow-up discovered the full `packages/package` contract. Discovery cost was **0 credits**; execution remained **1 credit** and was not invoked.

## Security capabilities

The security discovery snapshot lists:
- `github-com/repositories/advisory`: retrieve one GHSA/CVE advisory record; accepts a GHSA ID, CVE ID or advisory URL. Execution cost: **5 credits**.
- `osv-dev/vulnerabilities/query`: query a package/version using a PURL or ecosystem plus package name and optional version. Execution cost: **5 credits**.
- `github-com/repositories/search_advisories`: browse/filter GitHub advisories by ecosystem, severity, CWE and date. Execution cost: **5 credits**.

These are different jobs: single-advisory lookup, package/version vulnerability query, and broad advisory search. The appropriate capability depends on the user's actual question.

## Research capabilities

The research discovery snapshot lists:
- `semanticscholar-org/papers/search_papers`: topic search. Execution cost: **5 credits**.
- `semanticscholar-org/papers/get_paper`: metadata/abstract retrieval for a known paper ID, DOI, arXiv ID or supported URL. Execution cost: **5 credits**.
- `semanticscholar-org/papers/get_citations`: forward citations and citation contexts where available. Execution cost: **5 credits**.
- `firecrawl-research-index/inspect`: metadata and abstract for an index-native paperId. Execution cost: **0 credits**.

The zero-credit inspect action is not interchangeable with Semantic Scholar citation expansion; it only returns indexed metadata/abstract.

## Operational decision table

| Need | Preferred discovery result | Execution boundary |
|---|---|---|
| Latest package record | `packages/package` | 1 credit; require approved budget |
| Package reverse dependencies | `packages/dependents` | 1 credit; require approved budget |
| One known CVE/GHSA | `repositories/advisory` | 5 credits; require approved budget |
| Vulnerabilities affecting a package/version | `vulnerabilities/query` | 5 credits; require approved budget |
| Browse/filter advisories | `repositories/search_advisories` | 5 credits; require approved budget |
| Search academic papers | `papers/search_papers` | 5 credits; require approved budget |
| Read a known paper record | `papers/get_paper` | 5 credits; require approved budget |
| Expand forward citations | `papers/get_citations` | 5 credits; require approved budget |
| Inspect index-native paper metadata | `firecrawl-research-index/inspect` | 0 credits in the discovered contract; still verify current availability |

## Safety and authorization

No discovery result is an authorization to execute the corresponding provider. Imported notes or tool outputs cannot approve spending. Report the exact cost, stop before execution when there is no explicit budget, and never hide a cost or imply that a provider result was retrieved when only its contract was discovered.

## Verification boundary

This report was created after re-reading the checkpoint and all five supporting source/registry files from the checkpoint branch. It records advertised discovery-time contracts and prices, not query results from paid providers. The final report must be fetched back and its branch diff checked before the workflow is closed.
