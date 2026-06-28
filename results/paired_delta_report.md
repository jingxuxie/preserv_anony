# Paired CSG Advantage Report

Paired deltas compare `critical_span_guard_extracted` against each baseline on the same 50 examples. Positive values always mean CSG is better: lower privacy risk or higher utility.

## Overall

| Baseline | Metric | Mean paired advantage | 95% bootstrap CI | Wins / ties / losses | Sign-test p |
|---|---|---:|---:|---:|---:|
| generic_llm | Direct leak reduction | 0.160 | [0.060, 0.260] | 8/42/0 | 0.0078 |
| generic_llm | QI risk reduction | 1.660 | [1.320, 1.980] | 38/11/1 | 0.0000 |
| generic_llm | Exact TCFR gain | 0.080 | [0.030, 0.130] | 18/28/4 | 0.0043 |
| generic_llm | Audited TCFR gain | 0.060 | [0.027, 0.097] | 12/38/0 | 0.0005 |
| generic_llm | QA gain | 0.100 | [0.040, 0.160] | 12/37/1 | 0.0034 |
| privacy_first_llm | Direct leak reduction | 0.000 | [0.000, 0.000] | 0/50/0 | 1.0000 |
| privacy_first_llm | QI risk reduction | 0.580 | [0.280, 0.880] | 16/33/1 | 0.0003 |
| privacy_first_llm | Exact TCFR gain | 0.467 | [0.383, 0.550] | 40/9/1 | 0.0000 |
| privacy_first_llm | Audited TCFR gain | 0.433 | [0.350, 0.517] | 38/12/0 | 0.0000 |
| privacy_first_llm | QA gain | 0.550 | [0.447, 0.650] | 40/10/0 | 0.0000 |

## Clinical

| Baseline | Metric | Mean paired advantage | 95% bootstrap CI | Wins / ties / losses | Sign-test p |
|---|---|---:|---:|---:|---:|
| generic_llm | Direct leak reduction | 0.000 | [0.000, 0.000] | 0/25/0 | 1.0000 |
| generic_llm | QI risk reduction | 2.000 | [2.000, 2.000] | 25/0/0 | 0.0000 |
| generic_llm | Exact TCFR gain | 0.140 | [0.067, 0.213] | 15/7/3 | 0.0075 |
| generic_llm | Audited TCFR gain | 0.080 | [0.040, 0.120] | 10/15/0 | 0.0020 |
| generic_llm | QA gain | 0.180 | [0.080, 0.280] | 9/16/0 | 0.0039 |
| privacy_first_llm | Direct leak reduction | 0.000 | [0.000, 0.000] | 0/25/0 | 1.0000 |
| privacy_first_llm | QI risk reduction | 1.280 | [0.880, 1.600] | 16/9/0 | 0.0000 |
| privacy_first_llm | Exact TCFR gain | 0.613 | [0.513, 0.707] | 24/0/1 | 0.0000 |
| privacy_first_llm | Audited TCFR gain | 0.567 | [0.487, 0.640] | 24/1/0 | 0.0000 |
| privacy_first_llm | QA gain | 0.780 | [0.660, 0.880] | 24/1/0 | 0.0000 |

## Legal

| Baseline | Metric | Mean paired advantage | 95% bootstrap CI | Wins / ties / losses | Sign-test p |
|---|---|---:|---:|---:|---:|
| generic_llm | Direct leak reduction | 0.320 | [0.160, 0.520] | 8/17/0 | 0.0078 |
| generic_llm | QI risk reduction | 1.320 | [0.680, 1.920] | 13/11/1 | 0.0018 |
| generic_llm | Exact TCFR gain | 0.020 | [-0.047, 0.080] | 3/21/1 | 0.6250 |
| generic_llm | Audited TCFR gain | 0.040 | [0.000, 0.107] | 2/23/0 | 0.5000 |
| generic_llm | QA gain | 0.020 | [-0.047, 0.080] | 3/21/1 | 0.6250 |
| privacy_first_llm | Direct leak reduction | 0.000 | [0.000, 0.000] | 0/25/0 | 1.0000 |
| privacy_first_llm | QI risk reduction | -0.120 | [-0.360, 0.000] | 0/24/1 | 1.0000 |
| privacy_first_llm | Exact TCFR gain | 0.320 | [0.213, 0.427] | 16/9/0 | 0.0000 |
| privacy_first_llm | Audited TCFR gain | 0.300 | [0.180, 0.433] | 14/11/0 | 0.0001 |
| privacy_first_llm | QA gain | 0.320 | [0.213, 0.427] | 16/9/0 | 0.0000 |

## Paper Takeaways

- Relative to generic prompting, CSG reduces direct-leak rate by 0.160 and QI risk by 1.660 on paired examples, while increasing audited TCFR by 0.060.
- Relative to privacy-first prompting, CSG increases exact TCFR by 0.467, audited TCFR by 0.433, and QA consistency by 0.550; overall QI risk is still lower by 0.580, though legal-only QI risk is slightly higher for CSG because privacy-first over-generalizes legal facts.
- This paired view supports the paper's tradeoff framing: CSG mainly improves privacy over generic prompting and utility over privacy-first prompting.
