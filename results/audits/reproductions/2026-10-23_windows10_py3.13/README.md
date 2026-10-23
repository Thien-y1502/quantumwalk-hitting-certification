# Re-run of v0.1.0 on Windows, 2026-10-23

Performed by the authors from a fresh clone of tag `v0.1.0`, with the pinned dependencies in
`requirements.txt` installed into a clean Python 3.13.15 virtual environment.

| File | Content |
|---|---|
| `pytest.txt` | `pytest -q` output (4 passed) |
| `reproduce_stdout.txt` | full stdout of `python reproduce_all.py` |
| `run_audit.json`, `run_manifest.json` | audit and manifest written by that run (elapsed 57.5 s) |
| `compare_vs_v0.1.0.txt`, `compare_vs_v0.1.0.json` | `scripts/compare_results.py --ref-git v0.1.0` (10/10 files match) |
| `pip_freeze.txt` | exact installed package versions |

The regenerated CSVs and figures themselves are not committed: the frozen `v0.1.0` outputs under
`results/` remain the reference.
