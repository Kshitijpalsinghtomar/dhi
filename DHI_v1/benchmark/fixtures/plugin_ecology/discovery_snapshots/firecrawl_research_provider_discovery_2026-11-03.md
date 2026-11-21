# Firecrawl research-provider discovery snapshot

- Discovery date: 2026-11-03
- Tool: `mcp__Firecrawl__firecrawl_find_tools`
- Query: academic research paper metadata abstract citation context full text
- Discovery call credit cost: 0

## Provider capabilities returned

| Provider | Capability | Purpose | Execution cost |
|---|---|---|---:|
| semanticscholar-org | papers/search_papers | Search papers by topic and filters. | 5 credits |
| semanticscholar-org | papers/get_paper | Retrieve full metadata/abstract for a paper ID/DOI/arXiv identifier. | 5 credits |
| semanticscholar-org | papers/get_citations | Forward citation expansion with citation contexts/intents when available. | 5 credits |
| firecrawl-research-index | inspect | Read metadata and abstract for an indexed paperId returned by the research index. | 0 credits |

## Contract distinctions
- Semantic Scholar `papers/search_papers` requires a topic query and supports continuation, field-of-study filters and a bounded page size.
- Semantic Scholar `papers/get_paper` requires a paper identifier (paper ID, CorpusId, DOI, arXiv ID, or supported URL).
- Semantic Scholar `papers/get_citations` requires a paper identifier and returns citation contexts and intents where available; it is paginated.
- Firecrawl research-index `inspect` requires a `paperId` produced by its own indexed search workflow; a generic web URL ID is not accepted.

## Execution boundary
Discovery only. No Semantic Scholar provider action was executed. The four capabilities above were not invoked; this snapshot records their advertised contracts and discovery-time prices only.
