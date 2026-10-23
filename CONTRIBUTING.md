# Contributing

Thank you for your interest in `qwcert`. This repository is the reference implementation and
reproducibility package for the manuscript *Access-Aware Certification of Target-Dependent Hitting
Times in Reversible Markov Chains with Applications to Quantum-Walk Search*. Contributions that
improve correctness, reproducibility, portability, and documentation are welcome.

## Ways to contribute

- **Report a bug**: wrong numbers, crashes, or platform-specific failures
  ([bug report](https://github.com/Thien-y1502/quantumwalk-hitting-certification/issues/new?template=bug_report.yml)).
- **Report an independent reproduction**, whether or not your results match
  ([reproduction report](https://github.com/Thien-y1502/quantumwalk-hitting-certification/issues/new?template=reproduction_report.yml)).
  Runs on other machines, operating systems, and Python versions are especially valuable.
- **Ask a question** about the method or the code
  ([question](https://github.com/Thien-y1502/quantumwalk-hitting-certification/issues/new?template=question.yml)).
- **Open a pull request**: tests, documentation, portability fixes, or new graph families.

## Development setup

```bash
git clone https://github.com/Thien-y1502/quantumwalk-hitting-certification.git
cd quantumwalk-hitting-certification
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
```

To check that a change does not alter the published numbers:

```bash
python reproduce_all.py
python scripts/compare_results.py --ref-git v0.1.0
git checkout -- results/          # restore the frozen v0.1.0 outputs afterwards
```

`scripts/compare_results.py` documents its tolerance policy in its docstring.

## Pull request checklist

1. One logical change per pull request, with a short description of *why*.
2. `pytest -q` passes locally. CI runs the suite on Linux, Windows, and macOS with Python 3.11 to 3.13.
3. New behaviour comes with a test in `tests/`.
4. **Changes that affect numerical results** must say so in the pull request and include the output of
   `scripts/compare_results.py`. They must not overwrite the frozen `v0.1.0` results; use a new
   configuration profile (for example `configs/paper_v2.json`) and a new release instead.
5. Dependencies stay pinned in `requirements.txt`; justify any new one.

## The frozen artifact

Release `v0.1.0` is the companion artifact of the manuscript and is never rewritten. Its integrity is
checked in CI against `MANIFEST.sha256`. Fixes land on `main` and ship in later releases, and
`CHANGELOG.md` states whether a release changes any reported number.

## Code of conduct

Participation is governed by the [Code of Conduct](CODE_OF_CONDUCT.md).
