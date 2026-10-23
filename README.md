# QuantumWalk Hitting-Time Certification

[![tests](https://github.com/Thien-y1502/quantumwalk-hitting-certification/actions/workflows/tests.yml/badge.svg)](https://github.com/Thien-y1502/quantumwalk-hitting-certification/actions/workflows/tests.yml)
[![reproduce](https://github.com/Thien-y1502/quantumwalk-hitting-certification/actions/workflows/reproduce.yml/badge.svg)](https://github.com/Thien-y1502/quantumwalk-hitting-certification/actions/workflows/reproduce.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
![Python 3.11 | 3.12 | 3.13](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.13-blue)

Reference implementation and reproducibility package for the manuscript *Access-Aware Certification of Target-Dependent Hitting Times in Reversible Markov Chains with Applications to Quantum-Walk Search*.

The repository implements the numerical experiments used in the current manuscript, including:

- one-half-lazy simple random walks and stationary-conditioned hitting times;
- the global gap-mass floor;
- the marked-rooted resistance-congestion floor;
- the hybrid and multi-forest target-aware floors;
- the finite cubic block-chain construction;
- exact-rational post-validation of floating-point proposals;
- fixed-proposal floor ablation;
- proposal-degradation stress tests.

The software evaluates classical certification quantities associated with the quantum-walk resource analysis. It does not implement or benchmark a quantum processor.

## Installation

Python 3.11 or later is recommended.

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Reproduce the results

Run the test suite first:

```bash
pytest -q
```

Then execute the complete experiment pipeline:

```bash
python reproduce_all.py
```

The experiment configuration is stored in `configs/paper_v1.json`. The run is deterministic under the declared seeds and takes about one minute on a desktop CPU.

To check a run against the frozen `v0.1.0` outputs:

```bash
python scripts/compare_results.py --ref-git v0.1.0
git checkout -- results/   # restore the frozen outputs afterwards
```

Discrete outcomes (convergence, coverage, iteration counts, audit counts) must match exactly; floating-point quantities must agree within `rtol=1e-6`. See [`REPRODUCTIONS.md`](REPRODUCTIONS.md) for the recorded runs and the full tolerance policy.

## Continuous integration

- [`tests`](.github/workflows/tests.yml) runs `pytest` on Linux, Windows, and macOS with Python 3.11, 3.12, and 3.13 on every push and pull request, and verifies the `v0.1.0` files against `MANIFEST.sha256`.
- [`reproduce`](.github/workflows/reproduce.yml) re-runs the full pipeline on demand and monthly, compares it with the committed results, and uploads the logs as a workflow artifact.

## Repository layout

```text
configs/        experiment configuration
src/qwcert/     core implementation
scripts/        figure generation and result comparison
results/raw/    per-run numerical outputs
results/tables/ aggregate tables
results/figures generated figures
results/audits/ environment and run metadata; reproductions/ holds re-run logs
tests/          unit tests
```

## Experiment configuration

The main benchmark evaluates seven graph families at requested sizes `[32, 64, 128, 256, 512]`. Deterministic graph families use one graph per size; random-regular and stochastic block-model families use five graph seeds per size. Five singleton mark policies are evaluated for each graph.

The finite cubic study uses core sizes `[16, 32, 64, 128, 256, 512, 1024]`. After inserting `L=floor(sqrt(m))` four-vertex blocks, the realized graph orders are `32, 52, 96, 172, 320, 600, 1152`.

The `multi_forest` comparator evaluates several positively perturbed Dijkstra forests. The path system from each trial is scored using the original conductances, and the largest valid floor is retained.

## Exact validation

For exact post-validation, transition probabilities and stationary weights are represented with `fractions.Fraction`. Each binary64 proposal component is converted to its exact dyadic rational value before recomputing the energy, residual, and interval endpoints.

## Results

A compact summary is provided in `RESULTS_SUMMARY.md`. Raw outputs, aggregate tables, and figures are included under `results/` and can be regenerated with `python reproduce_all.py`.

## Reproductions

| Date | Platform | Result |
|---|---|---|
| 2026-09-11 | Linux, Python 3.13.5 | Reference results (`v0.1.0`) |
| 2026-10-23 | Windows 10, Python 3.13.15 | 10/10 files match, max relative drift 2.4e-7 |

Independent reproductions are welcome, whether or not they match: please open a [reproduction report](https://github.com/Thien-y1502/quantumwalk-hitting-certification/issues/new?template=reproduction_report.yml).

## Contributing and support

- [`CONTRIBUTING.md`](CONTRIBUTING.md): development setup and pull-request rules
- [`SUPPORT.md`](SUPPORT.md): supported versions, response targets, and the issue-handling process
- [`SECURITY.md`](SECURITY.md) and [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)
- [`CHANGELOG.md`](CHANGELOG.md): what changed in each release, and whether any reported number changed

## Citation

Citation metadata are provided in `CITATION.cff`.

## Release and archival

The public source repository is maintained at
[`Thien-y1502/quantumwalk-hitting-certification`](https://github.com/Thien-y1502/quantumwalk-hitting-certification).
Release `v0.1.0` is the frozen companion artifact for the manuscript, and
`MANIFEST.sha256` lists the SHA-256 checksums of its files (verified in CI against
that tag). Later releases add tooling without changing any reported result; see
`CHANGELOG.md`. The archival Zenodo DOI will be added to this README and
`CITATION.cff` after the release record is published.

## License

MIT License. See `LICENSE`.
