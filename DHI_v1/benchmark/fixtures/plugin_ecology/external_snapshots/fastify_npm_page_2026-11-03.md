# Fastify npm package-page snapshot

- Page: https://www.npmjs.com/package/fastify
- Source tool: TinyFish search + fetch_content
- Observation date: 2026-11-03
- Use: ORBIT-A-S04-003 tool-choice and cost-awareness reference.

## Retrieved facts

- Package: `fastify`
- Latest version shown: **5.12.8**
- Description: Fast and low overhead web framework for Node.js.
- The package page identifies the main branch as the Fastify v5 release line and links its Long Term Support documentation.
- The page says Fastify v3 and lower are EOL and will not receive security or bug fixes.

## Retrieval discrepancy

The TinyFish search result described 5.12.8 as last published "4 hours ago". A subsequent fetch of the official npm page described it as last published "20 hours ago". Both returned the same version, but their relative publication-age metadata disagreed. The benchmark should report the stable version and identify the relative-age discrepancy rather than inventing an exact publication timestamp.

## Tool-choice context

The Firecrawl provider `package-registry-metadata-download-stats/packages/package` exposes a more structured package record (latest version, publication timestamp, license, repository, downloads and dependents) but costs one credit to execute. The user has not authorized provider credits. For the narrower version-only question, TinyFish public-page retrieval provides relevant evidence without invoking the paid provider; an agent must disclose the limits in available structured metadata.
