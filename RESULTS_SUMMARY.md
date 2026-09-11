# Reproduction results

The values below are generated from `configs/paper_v1.json` by `python reproduce_all.py`.

## Main benchmark

Across 375 graph-mark-policy evaluations and five floor choices (1,875 floating-point certificate runs):

| Floor | Coverage | Convergence | Median interval width | P90 interval width | Median floor-bound looseness | P90 floor-bound looseness |
|---|---:|---:|---:|---:|---:|---:|
| Reference Dirichlet | 1.000 | 0.933 | 0.0276 | 0.0482 | 1.016 | 1.666 |
| Global gap-mass | 1.000 | 0.933 | 0.0268 | 0.0461 | 8.387 | 144.146 |
| Marked-rooted | 1.000 | 0.933 | 0.0308 | 0.0471 | 3.241 | 7.912 |
| Hybrid maximum | 1.000 | 0.933 | 0.0303 | 0.0470 | 3.241 | 7.783 |
| Multi-forest hybrid | 1.000 | 0.933 | 0.0295 | 0.0471 | 2.895 | 5.388 |

The marked-rooted floor improves the global floor on 350 of 375 evaluations (93.33%). The multi-forest refinement improves the single-forest result on 216 of 375 evaluations.

## Cubic construction

The seven realized graph orders are `32, 52, 96, 172, 320, 600, 1152`, with three graph seeds at each order. At `N=1152`, the hard/easy hitting-time ratios are approximately `28.627`, `28.558`, and `28.531`, with median `28.558`. The descriptive log-log median fit exponent is approximately `0.756`. The largest sparse-solve relative residual over the 21 paired instances is approximately `1.83e-11`.

## Exact-rational validation

Six selected cases, including cubic instances through `N=1152`, are post-validated with exact rational arithmetic after converting each binary64 proposal component to its exact dyadic value. A separate 14-case proposal-degradation sweep uses two graphs and seven corruption levels; all exact intervals retain the numerical reference value within the stated comparison tolerance.

## Metrics

`rel_width` measures the final proposal-dependent interval width. `floor_bound_looseness = 1/(ell * H_ref)` measures the standalone upper bound implied by a spectral or Dirichlet floor. These quantities are reported separately.
