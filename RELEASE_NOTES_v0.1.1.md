# Release v0.1.1

Maintenance release that adds verification and community infrastructure.
**No algorithm, configuration, or reported number changes.** Release `v0.1.0` remains the frozen
companion artifact of the manuscript.

## What's new

- **CI on three operating systems.** `pytest` runs on Linux, Windows, and macOS with Python 3.11,
  3.12, and 3.13 on every push and pull request; the `v0.1.0` files are verified against
  `MANIFEST.sha256`.
- **Automated reproduction.** A `reproduce` workflow re-runs the full pipeline on demand and
  monthly, compares it with the committed results, and uploads the logs.
- **Result comparison tool.** `scripts/compare_results.py` checks regenerated outputs against any git
  revision with a documented tolerance policy: discrete outcomes must match exactly, floats within
  `rtol=1e-6`.
- **Cross-platform re-run recorded.** On Windows 10 with Python 3.13.15, all 10 result files match
  `v0.1.0`; every convergence flag, coverage flag, iteration count, and audit count is identical, and
  the largest relative drift in a float quantity is 2.4e-7. Logs are in
  `results/audits/reproductions/2026-10-23_windows10_py3.13/`.
- **Community files.** `CONTRIBUTING.md`, `SUPPORT.md` (supported versions, response targets,
  issue-handling process), `SECURITY.md`, `CODE_OF_CONDUCT.md`, issue templates including a
  reproduction report, and a pull-request template. `REPRODUCTIONS.md` records every known run.

## Reproduce

```bash
pip install -r requirements.txt
pytest -q
python reproduce_all.py
python scripts/compare_results.py --ref-git v0.1.0
```

Independent reproductions, matching or not, are welcome through the reproduction-report issue template.
