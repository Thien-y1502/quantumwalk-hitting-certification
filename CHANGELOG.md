# Changelog

Each entry states whether it changes any number reported in the manuscript.

## v0.1.1 (2026-10-23)

**Reported results: unchanged.** The algorithms, configuration, and committed outputs are identical
to `v0.1.0`.

### Added
- Continuous integration: `pytest` on Linux, Windows, and macOS with Python 3.11, 3.12, and 3.13,
  plus SHA-256 verification of the `v0.1.0` files against `MANIFEST.sha256`.
- `reproduce` workflow: full pipeline re-run on demand and monthly, compared with the committed
  results; logs are uploaded as workflow artifacts.
- `scripts/compare_results.py`: compares regenerated outputs with any git revision or directory under
  a documented tolerance policy.
- Recorded cross-platform re-run (Windows 10, Python 3.13.15): 10/10 result files match `v0.1.0`,
  maximum relative drift 2.4e-7. Logs in `results/audits/reproductions/`.
- `REPRODUCTIONS.md`, `CONTRIBUTING.md`, `SUPPORT.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, issue
  templates (bug, reproduction report, question), and a pull-request template.
- `.gitattributes` keeps LF line endings so that checksums verify after a Windows checkout.

## v0.1.0 (2026-09-11)

Initial public release and frozen companion artifact of the manuscript. See `RELEASE_NOTES.md`.
