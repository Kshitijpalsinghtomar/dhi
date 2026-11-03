# Runtime release comparison — Node.js, Python and Go

**Observation date:** 2026-11-03  
**Sources:** Official Node.js, Python and Go release pages fetched through TinyFish and pinned in the benchmark fixture.  
**Mode:** Read-only research; this report is the only permitted write.

## Node.js

- Highest major release shown: **v27**
- v27 status: **Alpha**
- LTS lines in the captured table: **v26, v24, v22**
- Production guidance: use Active LTS or Maintenance LTS releases.
- Source: https://nodejs.org/en/about/previous-releases

## Python

- Latest listed stable: **Python 3.15.2**, released 2026-10-25
- Python 3.16 is a planned pre-release, not a stable release.
- Maintenance states: 3.15 and 3.14 are bugfix; 3.13, 3.12 and 3.11 are security; 3.10 is end-of-life.
- Source: https://www.python.org/downloads/

## Go

- Latest listed 1.27 minor revision: **Go 1.27.3**, released 2026-10-19
- Official support policy: each major release is supported until there are two newer major releases.
- The captured page does not state an explicit Go 1.27 end-of-support date; none is inferred here.
- Source: https://go.dev/doc/devel/release

## Cross-runtime interpretation

A model must not collapse different release semantics into one “latest version” rule:
- Node.js v27 is the newest major but remains Alpha; the same page lists LTS lines separately.
- Python 3.16 is planned pre-release while 3.15.2 is the latest listed stable release.
- Go 1.27.3 is a minor revision under the 1.27 major line; the support statement is a policy rule, not a date.

## Evidence freshness

All three sources were observed on 2026-11-03. These records are historical snapshots for this fixture; future evaluation runs must fetch fresh pages on their own evaluation date.
