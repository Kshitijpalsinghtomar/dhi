# Plugin update contract — verified result

Status: complete

The TinyFish release snapshots and Firecrawl provider discovery records are pinned under `fixtures/plugin_ecology/`.

The ORBIT GitHub update_file action must use the exact current blob SHA returned by fetch_file, the complete replacement content, a non-empty commit message, and the explicit benchmark branch `orbit/plugin-benchmark-fixture`.

The update is verified only after fetching this file again and confirming that the branch diff from the seed commit contains this path as modified, with no other paths changed.

No source, task policy, issue state, deployment or external provider has been changed.
