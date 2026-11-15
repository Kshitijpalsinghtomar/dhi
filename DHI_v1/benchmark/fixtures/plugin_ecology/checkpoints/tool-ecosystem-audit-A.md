# Tool ecosystem cost audit — checkpoint A

**Task:** Produce an evidence-backed inventory of discoverable research, package and security tools, including credit costs and execution boundaries.  
**Source baseline:** 95753ed8c317bad88f43e548658b18100d9c2fd6  
**Checkpoint state:** initial discovery snapshots identified; source re-reading and synthesis still required.

## Provisional findings (not ground truth)
- Package-record lookup is discoverable through Firecrawl and costs one credit to execute.
- Security advisory and OSV package queries were discovered with five-credit execution costs.
- Research paper metadata/search and forward citation tools were discovered with five-credit execution costs, while one Firecrawl research-index inspect operation is listed at zero credits.
- Discovery actions themselves were free in the recorded calls.
- No paid provider action has been executed.

## Required resume protocol
1. Re-read this checkpoint after the interruption.
2. Re-read the current tool registry and all three provider discovery snapshots (package, security, research), plus the package discovery recovery snapshot.
3. Recompute the list of providers/capabilities and costs from those source files; do not rely on this checkpoint summary.
4. Distinguish free discovery from credit-consuming provider execution.
5. Create `reports/tool-ecosystem-cost-audit.md` on this branch.
6. Fetch the final report back and compare the branch diff with this checkpoint commit.
7. Do not invoke paid provider capabilities, spend credits, or mutate any external service.

This is an intentionally incomplete checkpoint. It contains hints, not verified final findings.
