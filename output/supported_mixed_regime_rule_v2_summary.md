# Supported Mixed-Regime Rule V2 Summary

This rule set is a leakage-safe post-selector over forecast-time columns. It was designed to target
mixed morning-rebound/daytime-collapse/evening-transition regimes while retaining historical evidence.

## Metrics

| scope | WMAPE |
|---|---:|
| history all | 4.3634% |
| history 3m | 4.3283% |
| history 14d | 7.5152% |
| 2026-06-17 | 12.8428% |
| 2026-06-18 | 12.7386% |

## Applications

- history applications: `34`
- target applications: `10`
- history total absolute-error gain: `5226.91`
- target total absolute-error gain: `8660.23`
