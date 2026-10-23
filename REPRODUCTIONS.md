# Reproduction log

Each row is a complete run of `python reproduce_all.py` followed by
`python scripts/compare_results.py --ref-git v0.1.0`. Logs for maintainer runs are stored under
`results/audits/reproductions/`; independent runs link to their reproduction-report issue.

| Date | Who | Version | Platform | Python | Runtime | Result | Evidence |
|---|---|---|---|---|---|---|---|
| 2026-09-11 | Authors (original run) | v0.1.0 | Linux 6.18, x86_64 | 3.13.5 | n/a | Reference results | `results/audits/` at tag `v0.1.0` |
| 2026-10-23 | Authors (re-run) | v0.1.0 | Windows 10 (19045), x86_64 | 3.13.15 | 57 s | 10/10 files match; max relative drift 2.4e-7 | [`results/audits/reproductions/2026-10-23_windows10_py3.13/`](results/audits/reproductions/2026-10-23_windows10_py3.13/) |

Independent reproductions are very welcome. Please use the
[reproduction report](https://github.com/Thien-y1502/quantumwalk-hitting-certification/issues/new?template=reproduction_report.yml)
template; runs that do **not** match are just as useful as runs that do.

## What "match" means

`scripts/compare_results.py` compares every CSV under `results/raw/` and `results/tables/`, plus
`results/audits/run_audit.json`, against the frozen `v0.1.0` outputs:

- non-float columns (graph families, marks, iteration counts, convergence and coverage flags) and
  the audit counts must be identical;
- float columns must agree within `rtol=1e-6`, `atol=1e-8`;
- solver residual columns are compared with an absolute tolerance of `1e-6`, since they only record
  how accurately a linear system was solved.

In the 2026-10-23 Windows re-run every discrete outcome was identical to the Linux reference. The
largest relative drift in a reported float quantity was 2.4e-7, in the global gap-mass floor of the
main benchmark and the bounds derived from it; aggregate and family summary tables drifted by at most 1.1e-8.
