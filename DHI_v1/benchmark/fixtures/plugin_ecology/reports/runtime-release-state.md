# Runtime release-state comparison

**Observation date:** 2026-11-03  
**Sources:** Official Node.js and Python release pages, retrieved with TinyFish and pinned in this fixture.  
**Mode:** Read-only source research; this report is the only permitted write.

## Node.js

- Highest major release in the official release table: **v27**
- v27 lifecycle state: **Alpha**
- LTS lines shown in the captured table: **v26, v24 and v22**
- Production guidance: use Active LTS or Maintenance LTS, not Alpha.
- Source: https://nodejs.org/en/about/previous-releases
- Pinned evidence: `external_snapshots/nodejs_releases_2026-11-03.md`

## Python

- Latest listed stable release: **Python 3.15.2**, released October 25, 2026
- Python 3.16 is shown as a planned pre-release, not a stable release; its planned release date is October 6, 2027.
- Branch maintenance states in the captured page:
  - 3.15 and 3.14: bugfix
  - 3.13, 3.12 and 3.11: security
  - 3.10: end-of-life; support ended October 1, 2026
- Source: https://www.python.org/downloads/
- Pinned evidence: `external_snapshots/python_releases_2026-11-03.md`

## Comparison

The highest numbered release is not necessarily the production recommendation: Node.js v27 is Alpha while the listed LTS lines are the production-oriented options. Python 3.16 is planned pre-release, while 3.15.2 is the latest listed stable release. Python 3.10 is already end-of-life.

The snapshots are historical and pinned to the 2026-11-03 observation. They must not be reused as current facts in a future benchmark date; a new task run must fetch fresh official pages.
