# Paired CSG Advantage Report

Paired deltas compare `critical_span_guard_extracted` against each baseline on the same 70 examples. Positive values always mean CSG is better: lower privacy risk or higher utility.

## Overall

| Baseline | Metric | Mean paired advantage | 95% bootstrap CI | Wins / ties / losses | Sign-test p |
|---|---|---:|---:|---:|---:|
| generic_llm | Direct leak reduction | 0.186 | [0.100, 0.286] | 13/57/0 | 0.0002 |
| generic_llm | QI risk reduction | 1.700 | [1.414, 1.971] | 53/16/1 | 0.0000 |
| generic_llm | Exact TCFR gain | 0.088 | [0.048, 0.129] | 26/39/5 | 0.0002 |
| generic_llm | Audited TCFR gain | 0.064 | [0.036, 0.098] | 18/52/0 | 0.0000 |
| generic_llm | QA gain | 0.114 | [0.064, 0.167] | 18/51/1 | 0.0001 |
| privacy_first_llm | Direct leak reduction | 0.000 | [0.000, 0.000] | 0/70/0 | 1.0000 |
| privacy_first_llm | QI risk reduction | 0.529 | [0.300, 0.757] | 20/49/1 | 0.0000 |
| privacy_first_llm | Exact TCFR gain | 0.502 | [0.429, 0.574] | 57/12/1 | 0.0000 |
| privacy_first_llm | Audited TCFR gain | 0.479 | [0.405, 0.555] | 55/15/0 | 0.0000 |
| privacy_first_llm | QA gain | 0.571 | [0.486, 0.655] | 57/13/0 | 0.0000 |

## Clinical

| Baseline | Metric | Mean paired advantage | 95% bootstrap CI | Wins / ties / losses | Sign-test p |
|---|---|---:|---:|---:|---:|
| generic_llm | Direct leak reduction | 0.029 | [0.000, 0.086] | 1/34/0 | 1.0000 |
| generic_llm | QI risk reduction | 2.029 | [2.000, 2.086] | 35/0/0 | 0.0000 |
| generic_llm | Exact TCFR gain | 0.148 | [0.090, 0.205] | 22/9/4 | 0.0005 |
| generic_llm | Audited TCFR gain | 0.086 | [0.052, 0.124] | 15/20/0 | 0.0001 |
| generic_llm | QA gain | 0.200 | [0.129, 0.286] | 14/21/0 | 0.0001 |
| privacy_first_llm | Direct leak reduction | 0.000 | [0.000, 0.000] | 0/35/0 | 1.0000 |
| privacy_first_llm | QI risk reduction | 1.143 | [0.800, 1.486] | 20/15/0 | 0.0000 |
| privacy_first_llm | Exact TCFR gain | 0.633 | [0.552, 0.710] | 34/0/1 | 0.0000 |
| privacy_first_llm | Audited TCFR gain | 0.567 | [0.505, 0.624] | 34/1/0 | 0.0000 |
| privacy_first_llm | QA gain | 0.771 | [0.671, 0.857] | 34/1/0 | 0.0000 |

## Legal

| Baseline | Metric | Mean paired advantage | 95% bootstrap CI | Wins / ties / losses | Sign-test p |
|---|---|---:|---:|---:|---:|
| generic_llm | Direct leak reduction | 0.343 | [0.200, 0.486] | 12/23/0 | 0.0005 |
| generic_llm | QI risk reduction | 1.371 | [0.829, 1.886] | 18/16/1 | 0.0001 |
| generic_llm | Exact TCFR gain | 0.029 | [-0.019, 0.081] | 4/30/1 | 0.3750 |
| generic_llm | Audited TCFR gain | 0.043 | [0.000, 0.100] | 3/32/0 | 0.2500 |
| generic_llm | QA gain | 0.029 | [-0.019, 0.081] | 4/30/1 | 0.3750 |
| privacy_first_llm | Direct leak reduction | 0.000 | [0.000, 0.000] | 0/35/0 | 1.0000 |
| privacy_first_llm | QI risk reduction | -0.086 | [-0.257, 0.000] | 0/34/1 | 1.0000 |
| privacy_first_llm | Exact TCFR gain | 0.371 | [0.267, 0.476] | 23/12/0 | 0.0000 |
| privacy_first_llm | Audited TCFR gain | 0.390 | [0.262, 0.524] | 21/14/0 | 0.0000 |
| privacy_first_llm | QA gain | 0.371 | [0.267, 0.476] | 23/12/0 | 0.0000 |

## Paper Takeaways

- Relative to generic prompting, CSG reduces direct-leak rate by 0.186 and QI risk by 1.700 on paired examples, while increasing audited TCFR by 0.064.
- Relative to privacy-first prompting, CSG increases exact TCFR by 0.502, audited TCFR by 0.479, and QA consistency by 0.571; overall QI risk is still lower by 0.529, though legal-only QI risk is slightly higher for CSG because privacy-first over-generalizes legal facts.
- This paired view supports the paper's tradeoff framing: CSG mainly improves privacy over generic prompting and utility over privacy-first prompting.
