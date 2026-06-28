# Paired CSG Advantage Report

Paired deltas compare `critical_span_guard_extracted` against each baseline on the same 120 examples. Positive values always mean CSG is better: lower privacy risk or higher utility.

## Overall

| Baseline | Metric | Mean paired advantage | 95% bootstrap CI | Wins / ties / losses | Sign-test p |
|---|---|---:|---:|---:|---:|
| generic_llm | Direct leak reduction | 0.183 | [0.117, 0.258] | 22/98/0 | 0.0000 |
| generic_llm | QI risk reduction | 1.600 | [1.358, 1.825] | 88/29/3 | 0.0000 |
| generic_llm | Exact TCFR gain | 0.071 | [0.043, 0.100] | 40/73/7 | 0.0000 |
| generic_llm | Audited TCFR gain | 0.054 | [0.033, 0.078] | 27/92/1 | 0.0000 |
| generic_llm | QA gain | 0.088 | [0.053, 0.124] | 23/96/1 | 0.0000 |
| privacy_first_llm | Direct leak reduction | 0.000 | [0.000, 0.000] | 0/120/0 | 1.0000 |
| privacy_first_llm | QI risk reduction | 0.458 | [0.267, 0.650] | 33/82/5 | 0.0000 |
| privacy_first_llm | Exact TCFR gain | 0.483 | [0.425, 0.540] | 93/26/1 | 0.0000 |
| privacy_first_llm | Audited TCFR gain | 0.451 | [0.396, 0.507] | 92/28/0 | 0.0000 |
| privacy_first_llm | QA gain | 0.557 | [0.489, 0.625] | 92/28/0 | 0.0000 |

## Clinical

| Baseline | Metric | Mean paired advantage | 95% bootstrap CI | Wins / ties / losses | Sign-test p |
|---|---|---:|---:|---:|---:|
| generic_llm | Direct leak reduction | 0.033 | [0.000, 0.083] | 2/58/0 | 0.5000 |
| generic_llm | QI risk reduction | 2.033 | [2.000, 2.083] | 60/0/0 | 0.0000 |
| generic_llm | Exact TCFR gain | 0.117 | [0.078, 0.158] | 35/19/6 | 0.0000 |
| generic_llm | Audited TCFR gain | 0.067 | [0.042, 0.092] | 22/37/1 | 0.0000 |
| generic_llm | QA gain | 0.150 | [0.092, 0.208] | 18/42/0 | 0.0000 |
| privacy_first_llm | Direct leak reduction | 0.000 | [0.000, 0.000] | 0/60/0 | 1.0000 |
| privacy_first_llm | QI risk reduction | 1.100 | [0.867, 1.333] | 33/27/0 | 0.0000 |
| privacy_first_llm | Exact TCFR gain | 0.636 | [0.572, 0.694] | 58/1/1 | 0.0000 |
| privacy_first_llm | Audited TCFR gain | 0.544 | [0.494, 0.589] | 57/3/0 | 0.0000 |
| privacy_first_llm | QA gain | 0.783 | [0.708, 0.858] | 57/3/0 | 0.0000 |

## Legal

| Baseline | Metric | Mean paired advantage | 95% bootstrap CI | Wins / ties / losses | Sign-test p |
|---|---|---:|---:|---:|---:|
| generic_llm | Direct leak reduction | 0.333 | [0.217, 0.450] | 20/40/0 | 0.0000 |
| generic_llm | QI risk reduction | 1.167 | [0.733, 1.583] | 28/29/3 | 0.0000 |
| generic_llm | Exact TCFR gain | 0.025 | [-0.006, 0.058] | 5/54/1 | 0.2188 |
| generic_llm | Audited TCFR gain | 0.042 | [0.008, 0.081] | 5/55/0 | 0.0625 |
| generic_llm | QA gain | 0.025 | [-0.006, 0.058] | 5/54/1 | 0.2188 |
| privacy_first_llm | Direct leak reduction | 0.000 | [0.000, 0.000] | 0/60/0 | 1.0000 |
| privacy_first_llm | QI risk reduction | -0.183 | [-0.367, -0.033] | 0/55/5 | 0.0625 |
| privacy_first_llm | Exact TCFR gain | 0.331 | [0.250, 0.414] | 35/25/0 | 0.0000 |
| privacy_first_llm | Audited TCFR gain | 0.358 | [0.267, 0.450] | 35/25/0 | 0.0000 |
| privacy_first_llm | QA gain | 0.331 | [0.250, 0.414] | 35/25/0 | 0.0000 |

## Paper Takeaways

- Relative to generic prompting, CSG reduces direct-leak rate by 0.183 and QI risk by 1.600 on paired examples, while increasing audited TCFR by 0.054.
- Relative to privacy-first prompting, CSG increases exact TCFR by 0.483, audited TCFR by 0.451, and QA consistency by 0.557; overall QI risk is still lower by 0.458, though legal-only QI risk is slightly higher for CSG because privacy-first over-generalizes legal facts.
- This paired view supports the paper's tradeoff framing: CSG mainly improves privacy over generic prompting and utility over privacy-first prompting.
