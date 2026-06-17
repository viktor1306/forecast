# Sub-10 Trust Signal V1 Summary

This post-selector uses forecast-time trust gates over `supported_mixed_regime_rule_v2_pred`.
It was built to get at least one target day below 10% WMAPE without 3m/14d regression.

## Metrics

| scope | baseline v2 | sub10 trust v1 | delta |
|---|---:|---:|---:|
| history 3m | 4.3283% | 4.3015% | -0.0268 p.p. |
| history 14d | 7.5152% | 7.4704% | -0.0448 p.p. |
| 2026-06-17 |  | 9.9096% |  |
| 2026-06-18 |  | 12.7386% |  |

## Applications

- history applications: `31`
- target applications: `7`
- history absolute-error gain: `3312.36`
- target absolute-error gain: `5537.50`
