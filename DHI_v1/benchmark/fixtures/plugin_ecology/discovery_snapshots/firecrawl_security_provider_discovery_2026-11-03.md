# Firecrawl security-provider discovery snapshot

- Discovery date: 2026-11-03
- Tool: `mcp__Firecrawl__firecrawl_find_tools`
- Query: software security advisories CVE affected package version severity patched version
- Discovery call credit cost: 0

## Provider capabilities returned

| Provider | Capability | Purpose | Execution cost |
|---|---|---|---:|
| github-com | repositories/advisory | One GitHub Advisory record by GHSA, CVE or advisory URL; includes severity, CVSS, EPSS, affected packages and patched versions. | 5 credits |
| osv-dev | vulnerabilities/query | Query known vulnerabilities for a package/ecosystem/version or PURL; includes aliases, severity, affected ranges and fixed versions. | 5 credits |
| github-com | repositories/search_advisories | Browse/filter GitHub Advisory Database entries by ecosystem, severity, CWE and dates. | 5 credits |

## Useful contract distinction

The single-record GitHub advisory lookup accepts one of `ghsa_id`, `cve_id`, or `url`. The OSV query accepts a `purl`, or an `ecosystem` plus `name`, with an optional `version`. The broad GitHub advisory search is a browse/filter capability, not the most direct tool for checking one named package version.

## Execution boundary

Discovery only. No 5-credit provider capability was invoked. This snapshot proves that tool discovery exposed the provider contracts and costs; it does not contain a vulnerability query result.
