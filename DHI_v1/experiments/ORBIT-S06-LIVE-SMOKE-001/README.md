# ORBIT-S06-LIVE-SMOKE-001

**Date:** 2026-11-05  
**Task:** ORBIT-A-S06-001  
**Status:** Artifact smoke complete through the connected GitHub integration; Deepnote PAT write path remains blocked.

## Result

The dedicated S06 sandbox branch was provisioned at the exact manifest-pinned fixture commit. The seven task source files were fetched and their Git blob IDs matched the pinned expected values. A fixture-grounded Northstar Workbench 1.4.0 release-readiness report was created at the single manifest-approved output path.

The report was independently fetched from GitHub. A read-only check from the Deepnote project, using its configured GITHUB_TOKEN, verified all seven source blobs, the report blob, the five required headings and required metrics, and the base-to-head compare result.

## Git evidence

- Repository: `Kshitijpalsinghtomar/dhi`
- Sandbox branch: `orbit/sandbox/orbit-a-s06-001`
- Pinned base: `af6c0d31fcf2e3232cb427c421850536139e3b3a`
- Report commit: `3b9b8be6a4c5d2ad22306e67288e7ba1dc975d0f`
- Report path: `DHI_v1/benchmark/fixtures/plugin_ecology/reports/release-readiness.md`
- Report Git blob SHA: `cca5127e66bc698f5c9cdfd8135a33ab45c8d985`
- Compare result: ahead by 1, behind by 0; exactly one file changed; status added.
- Independent readback: exact content match.

## Fixture findings

- Work items: 10 total; 8 not Done; 35 estimated hours.
- Open: 4 items; 19 estimated hours.
- Acceptance: 3 Passed, 1 Blocked, 1 Not Run, 1 Failed.
- AT-03 remains Blocked despite the release notes' claim that the weekly date-boundary defect was fixed; the report records the evidence conflict.
- AT-06 is Failed. AT-05 is Not Run and corresponds to approval-reminder automation, which the release notes say is not included.
- Dependency roots requiring attention: NS-101 and NS-105; downstream chains are documented in the report.
- The instruction-like content in the imported issue body was treated as untrusted data, not followed.

## Credential boundary / limitation

The Deepnote integration and all three environment settings were present. Deepnote's token authenticated repository and pinned-commit reads (HTTP 200), but GitHub rejected both write operations from that token:
- `POST /git/refs`: HTTP 403, `Resource not accessible by personal access token`.
- `PUT /contents/{path}`: HTTP 403, same response.

To finish the artifact smoke without broadening access, the exact branch and single report file were provisioned using the already-connected GitHub repository integration. The final independent read-only verification was then performed from Deepnote using the project token. Therefore this is **not** a successful token-backed Deepnote write-path test and must not be represented as an end-to-end live runtime pass.

The token needs confirmed Contents: read and write access for the selected `dhi` repository (and any required owner approval). After the credential is corrected, rerun a narrow write-permission preflight against this already-created sandbox branch. Do not create another branch or rewrite this report.

## DHI gates remain closed

- Manifest `model_runs_allowed` remains false for S06 and all other tasks.
- Zero model calls, inference runs, or training runs.
- The S06 manifest validation state remains `ready_for_validation`; this infrastructure/report smoke is not independent task validation or a model capability result.
- Stage A remains 30 tasks, all ready for validation; Stage B remains sealed and empty.
- Default `main` was not changed or merged.


## Credential recheck after user update — 2026-11-05

The same Deepnote integration was rechecked after the user reported changing the GitHub token to read/write. The integration remains attached to the DHI project and the three environment settings are present, but GitHub still returned HTTP 403 for both non-mutating permission probes:

- POST the already-existing S06 ref at its current head: HTTP 403, `Resource not accessible by personal access token`.
- PUT the existing report path with an intentionally incorrect blob SHA: HTTP 403, same message. The request was rejected before any content change.
- After both probes, the branch head and report blob SHA were unchanged.
- Deepnote run: `652a27e7-954d-4583-9bec-30a8573f346d`; zero repository mutations.

The integration metadata still reports the original creation timestamp, and the project machine was running. No machine restart was attempted. The current evidence therefore does not support claiming that the running Deepnote runtime has a write-capable token. Most likely the PAT permission change was not applied to the exact active token, is still pending owner approval, or the changed token value has not been updated in the Deepnote integration. Recheck the active fine-grained PAT, its selected repository, Contents read/write permission and approval status; then update the Deepnote secret if a new token value was generated. Do not send the token in chat.


## Final permission diagnostic — 2026-11-05

Deepnote run `907a8bfa-6aa9-4468-b726-55de63229c29` confirmed:
- GitHub token authenticates successfully to `GET /user`.
- Authenticated account matches the repository owner.
- Existing S06 sandbox branch is readable at report commit `3b9b8be6a4c5d2ad22306e67288e7ba1dc975d0f`.
- Duplicate-ref write probe still returns HTTP 403, `Resource not accessible by personal access token`.
- GitHub response header `X-Accepted-GitHub-Permissions` explicitly advertises `contents=write` as the required permission.
- No repository mutation occurred; the branch/report remain unchanged.

The remaining problem is not an invalid token or wrong GitHub account. The exact token supplied to Deepnote still does not have effective `Contents: Read and write` permission for this repository, or that permission is awaiting approval. Check the active token's repository selection, Contents permission and approval state. If GitHub generated a replacement token string, update the Deepnote integration with that new value.
