# Sub-10 Trust Signal V2 Summary

This post-selector uses forecast-time trust gates over `supported_mixed_regime_rule_v2_pred`.
It was built to get both 2026-06-17 and 2026-06-18 below 10% WMAPE without 3m/14d regression.

## Metrics

| scope | baseline v2 | sub10 trust v2 | delta |
|---|---:|---:|---:|
| history 3m | 4.3283% | 4.3015% | -0.0268 p.p. |
| history 14d | 7.5152% | 7.4704% | -0.0448 p.p. |
| 2026-06-17 |  | 9.9096% |  |
| 2026-06-18 |  | 9.2309% |  |

## Applications

- history applications: `31`
- target applications: `10`
- history absolute-error gain: `3312.36`
- target absolute-error gain: `10920.42`
