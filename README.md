# QuantumWalk Hitting-Time Certification

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

The experiment configuration is stored in `configs/paper_v1.json`. The run is deterministic under the declared seeds.

## Repository layout

```text
configs/        experiment configuration
src/qwcert/     core implementation
scripts/        figure generation
results/raw/    per-run numerical outputs
results/tables/ aggregate tables
results/figures generated figures
results/audits/ environment and run metadata
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

## Citation

Citation metadata are provided in `CITATION.cff`.

## Release and archival

The public source repository is maintained at
[`Thien-y1502/quantumwalk-hitting-certification`](https://github.com/Thien-y1502/quantumwalk-hitting-certification).
Release `v0.1.0` is the frozen companion artifact for the manuscript. Its
archival Zenodo DOI will be added to this README and `CITATION.cff` after the
release record is published.

## License

MIT License. See `LICENSE`.
