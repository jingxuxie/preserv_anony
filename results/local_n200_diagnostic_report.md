# Local n200 Diagnostic Expansion

Generated: 2026-06-28

This report is a no-API local diagnostic expansion from 100 to 200 examples. It uses deterministic local baselines and gold-informed oracle variants only; it is not a replacement for the promoted n150 non-oracle LLM headline.

## Data Integrity

- Benchmark rows: 200 (clinical=100, legal=100).
- Output rows: 1000; judgment rows: 1000.
- Methods: `regex_rules`=200, `presidio_baseline`=200, `direct_span_oracle`=200, `privacy_first_oracle`=200, `critical_span_guard_oracle`=200.

## n200 Local Diagnostic Result

| Method | N | Direct leak | QI risk | TCFR | QA |
|---|---:|---:|---:|---:|---:|
| `regex_rules` | 200 | 0.075 | 1.780 | 0.993 | 0.993 |
| `presidio_baseline` | 200 | 0.490 | 2.490 | 0.678 | 0.786 |
| `direct_span_oracle` | 200 | 0.000 | 2.810 | 1.000 | 1.000 |
| `privacy_first_oracle` | 200 | 0.000 | 0.005 | 0.448 | 0.336 |
| `critical_span_guard_oracle` | 200 | 0.000 | 0.225 | 1.000 | 1.000 |

## n100 to n200 Directional Stability

| Method | n100 QI | n200 QI | n100 TCFR | n200 TCFR | n100 QA | n200 QA |
|---|---:|---:|---:|---:|---:|---:|
| `regex_rules` | 1.700 | 1.780 | 1.000 | 0.993 | 1.000 | 0.993 |
| `presidio_baseline` | 2.490 | 2.490 | 0.697 | 0.678 | 0.802 | 0.786 |
| `direct_span_oracle` | 2.810 | 2.810 | 1.000 | 1.000 | 1.000 | 1.000 |
| `privacy_first_oracle` | 0.010 | 0.005 | 0.478 | 0.448 | 0.365 | 0.336 |
| `critical_span_guard_oracle` | 0.170 | 0.225 | 1.000 | 1.000 | 1.000 | 1.000 |

## Directional Checks

- PASS: `direct_span_oracle_high_qi`.
- PASS: `privacy_first_oracle_utility_loss`.
- PASS: `csg_oracle_frontier`.
- PASS: `presidio_legal_direct_leak_failure`.

## Interpretation

- The local n200 slice preserves the same diagnostic frontier as n100: direct-span-only masking keeps utility but leaves high QI risk, while privacy-first oracle redaction minimizes QI risk at large utility cost.
- Gold-informed CSG remains an upper-bound diagnostic: zero measured direct leaks, perfect exact TCFR/QA, and much lower QI risk than direct-span-only masking.
- Presidio remains a useful negative baseline for legal snippets, with high direct-leak rate on the n200 legal split.
- Do not mix this local/oracle diagnostic with the n150 non-oracle LLM headline; use it to address sample-size sensitivity of the benchmark and local baseline phenomena.
