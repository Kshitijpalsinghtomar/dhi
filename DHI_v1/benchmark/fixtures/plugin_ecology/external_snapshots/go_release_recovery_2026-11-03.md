# Go release-page recovery snapshot

- Date: 2026-11-03
- Tool: TinyFish fetch_content + search
- Initial request: `https://go.dev/doc/devel/releases-does-not-exist`
- Initial outcome: HTTP 404 / `page_not_found`

## Schema failure observed before the HTTP request

An initial fetch_content call omitted `page_metadata`. The live tool schema rejected the invocation before dispatch because the field is required, despite the descriptive docs indicating a default. The corrected call supplied `page_metadata: true`.

## Recovery

1. Correct the input schema by including the required `page_metadata` boolean.
2. The corrected request reached the source and returned `page_not_found` with HTTP 404 for the intentionally incorrect path.
3. Search the official domain for Go release history; TinyFish returned the canonical `https://go.dev/doc/devel/release` URL.
4. Fetch the recovered URL with the complete required schema. It returned the official Release History page, including Go 1.27.3 dated 2026-10-19.

## Boundary

This snapshot records one argument-schema rejection followed by a real 404 and a successful recovery. No page was changed and no external side effect occurred.
