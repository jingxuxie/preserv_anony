# Paired CSG Advantage Report

Paired deltas compare `critical_span_guard_extracted` against each baseline on the same 100 examples. Positive values always mean CSG is better: lower privacy risk or higher utility.

## Overall

| Baseline | Metric | Mean paired advantage | 95% bootstrap CI | Wins / ties / losses | Sign-test p |
|---|---|---:|---:|---:|---:|
| generic_llm | Direct leak reduction | 0.190 | [0.110, 0.270] | 19/81/0 | 0.0000 |
| generic_llm | QI risk reduction | 1.710 | [1.470, 1.930] | 75/24/1 | 0.0000 |
| generic_llm | Exact TCFR gain | 0.075 | [0.045, 0.107] | 35/59/6 | 0.0000 |
| generic_llm | Audited TCFR gain | 0.057 | [0.035, 0.082] | 23/77/0 | 0.0000 |
| generic_llm | QA gain | 0.090 | [0.050, 0.130] | 20/79/1 | 0.0000 |
| privacy_first_llm | Direct leak reduction | 0.000 | [0.000, 0.000] | 0/100/0 | 1.0000 |
| privacy_first_llm | QI risk reduction | 0.540 | [0.350, 0.740] | 29/69/2 | 0.0000 |
| privacy_first_llm | Exact TCFR gain | 0.515 | [0.453, 0.578] | 81/18/1 | 0.0000 |
| privacy_first_llm | Audited TCFR gain | 0.485 | [0.425, 0.545] | 80/20/0 | 0.0000 |
| privacy_first_llm | QA gain | 0.577 | [0.505, 0.650] | 80/20/0 | 0.0000 |

## Clinical

| Baseline | Metric | Mean paired advantage | 95% bootstrap CI | Wins / ties / losses | Sign-test p |
|---|---|---:|---:|---:|---:|
| generic_llm | Direct leak reduction | 0.040 | [0.000, 0.100] | 2/48/0 | 0.5000 |
| generic_llm | QI risk reduction | 2.040 | [2.000, 2.100] | 50/0/0 | 0.0000 |
| generic_llm | Exact TCFR gain | 0.130 | [0.087, 0.177] | 31/14/5 | 0.0000 |
| generic_llm | Audited TCFR gain | 0.073 | [0.047, 0.103] | 19/31/0 | 0.0000 |
| generic_llm | QA gain | 0.160 | [0.100, 0.230] | 16/34/0 | 0.0000 |
| privacy_first_llm | Direct leak reduction | 0.000 | [0.000, 0.000] | 0/50/0 | 1.0000 |
| privacy_first_llm | QI risk reduction | 1.160 | [0.880, 1.440] | 29/21/0 | 0.0000 |
| privacy_first_llm | Exact TCFR gain | 0.657 | [0.590, 0.720] | 49/0/1 | 0.0000 |
| privacy_first_llm | Audited TCFR gain | 0.563 | [0.510, 0.613] | 48/2/0 | 0.0000 |
| privacy_first_llm | QA gain | 0.780 | [0.700, 0.860] | 48/2/0 | 0.0000 |

## Legal

| Baseline | Metric | Mean paired advantage | 95% bootstrap CI | Wins / ties / losses | Sign-test p |
|---|---|---:|---:|---:|---:|
| generic_llm | Direct leak reduction | 0.340 | [0.200, 0.480] | 17/33/0 | 0.0000 |
| generic_llm | QI risk reduction | 1.380 | [0.940, 1.800] | 25/24/1 | 0.0000 |
| generic_llm | Exact TCFR gain | 0.020 | [-0.013, 0.057] | 4/45/1 | 0.3750 |
| generic_llm | Audited TCFR gain | 0.040 | [0.007, 0.080] | 4/46/0 | 0.1250 |
| generic_llm | QA gain | 0.020 | [-0.013, 0.057] | 4/45/1 | 0.3750 |
| privacy_first_llm | Direct leak reduction | 0.000 | [0.000, 0.000] | 0/50/0 | 1.0000 |
| privacy_first_llm | QI risk reduction | -0.080 | [-0.220, 0.000] | 0/48/2 | 0.5000 |
| privacy_first_llm | Exact TCFR gain | 0.373 | [0.283, 0.467] | 32/18/0 | 0.0000 |
| privacy_first_llm | Audited TCFR gain | 0.407 | [0.303, 0.507] | 32/18/0 | 0.0000 |
| privacy_first_llm | QA gain | 0.373 | [0.283, 0.467] | 32/18/0 | 0.0000 |

## Paper Takeaways

- Relative to generic prompting, CSG reduces direct-leak rate by 0.190 and QI risk by 1.710 on paired examples, while increasing audited TCFR by 0.057.
- Relative to privacy-first prompting, CSG increases exact TCFR by 0.515, audited TCFR by 0.485, and QA consistency by 0.577; overall QI risk is still lower by 0.540, though legal-only QI risk is slightly higher for CSG because privacy-first over-generalizes legal facts.
- This paired view supports the paper's tradeoff framing: CSG mainly improves privacy over generic prompting and utility over privacy-first prompting.
