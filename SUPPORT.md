# Support policy

## Where to ask

| Need | Channel |
|---|---|
| Bug, wrong result, crash | [Bug report](https://github.com/Thien-y1502/quantumwalk-hitting-certification/issues/new?template=bug_report.yml) |
| Independent reproduction, matching or not | [Reproduction report](https://github.com/Thien-y1502/quantumwalk-hitting-certification/issues/new?template=reproduction_report.yml) |
| Question about the method or the code | [Question](https://github.com/Thien-y1502/quantumwalk-hitting-certification/issues/new?template=question.yml) |
| Security issue | [SECURITY.md](SECURITY.md); please do not open a public issue |

## What is supported

| Version | Status |
|---|---|
| `main` | Maintained; receives fixes |
| `v0.1.x` | Frozen manuscript artifact; problems are documented and fixed in later releases |

Supported platforms are Linux, Windows, and macOS with Python 3.11, 3.12, and 3.13, using the pinned
versions in `requirements.txt`. Every combination is tested in CI.

## Response targets

The authors maintain the project on a best-effort basis and aim to:

- acknowledge new issues within **7 days**;
- triage (label and prioritise) within **14 days**;
- handle issues that may affect a reported result before anything else.

## Issue handling process

1. **Label.** Each issue gets `bug`, `reproduction`, `question`, or `enhancement`. The issue templates
   apply the first label automatically.
2. **Triage.** A maintainer confirms the report, asks for anything missing (environment, command,
   logs), and sets a priority:
   - `priority: critical`: a number reported in the manuscript may be wrong;
   - `priority: high`: a crash or failure on a supported platform;
   - `priority: normal`: everything else.
3. **Fix.** A pull request references the issue. Numerical changes include a
   `scripts/compare_results.py` report.
4. **Release.** Fixes ship in the next release, and `CHANGELOG.md` says whether any reported result changed.
5. **Close.** Issues that wait 30 days for information from the reporter may be closed; they can be
   reopened at any time.

Reproduction reports are acknowledged, labelled `reproduction`, and recorded in
[`REPRODUCTIONS.md`](REPRODUCTIONS.md).
