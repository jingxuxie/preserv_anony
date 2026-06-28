# Paired CSG Advantage Report

Paired deltas compare `critical_span_guard_extracted` against each baseline on the same 150 examples. Positive values always mean CSG is better: lower privacy risk or higher utility.

## Overall

| Baseline | Metric | Mean paired advantage | 95% bootstrap CI | Wins / ties / losses | Sign-test p |
|---|---|---:|---:|---:|---:|
| generic_llm | Direct leak reduction | 0.180 | [0.120, 0.247] | 27/123/0 | 0.0000 |
| generic_llm | QI risk reduction | 1.607 | [1.407, 1.807] | 111/35/4 | 0.0000 |
| generic_llm | Exact TCFR gain | 0.071 | [0.048, 0.096] | 48/95/7 | 0.0000 |
| generic_llm | Audited TCFR gain | 0.057 | [0.038, 0.078] | 34/115/1 | 0.0000 |
| generic_llm | QA gain | 0.087 | [0.056, 0.119] | 28/121/1 | 0.0000 |
| privacy_first_llm | Direct leak reduction | 0.000 | [0.000, 0.000] | 0/150/0 | 1.0000 |
| privacy_first_llm | QI risk reduction | 0.447 | [0.280, 0.607] | 40/103/7 | 0.0000 |
| privacy_first_llm | Exact TCFR gain | 0.487 | [0.434, 0.538] | 118/31/1 | 0.0000 |
| privacy_first_llm | Audited TCFR gain | 0.466 | [0.416, 0.514] | 118/32/0 | 0.0000 |
| privacy_first_llm | QA gain | 0.560 | [0.498, 0.620] | 116/34/0 | 0.0000 |

## Clinical

| Baseline | Metric | Mean paired advantage | 95% bootstrap CI | Wins / ties / losses | Sign-test p |
|---|---|---:|---:|---:|---:|
| generic_llm | Direct leak reduction | 0.027 | [0.000, 0.067] | 2/73/0 | 0.5000 |
| generic_llm | QI risk reduction | 2.027 | [2.000, 2.067] | 75/0/0 | 0.0000 |
| generic_llm | Exact TCFR gain | 0.116 | [0.080, 0.151] | 42/27/6 | 0.0000 |
| generic_llm | Audited TCFR gain | 0.062 | [0.040, 0.084] | 26/48/1 | 0.0000 |
| generic_llm | QA gain | 0.147 | [0.100, 0.200] | 22/53/0 | 0.0000 |
| privacy_first_llm | Direct leak reduction | 0.000 | [0.000, 0.000] | 0/75/0 | 1.0000 |
| privacy_first_llm | QI risk reduction | 1.067 | [0.827, 1.280] | 40/35/0 | 0.0000 |
| privacy_first_llm | Exact TCFR gain | 0.627 | [0.573, 0.678] | 73/1/1 | 0.0000 |
| privacy_first_llm | Audited TCFR gain | 0.538 | [0.493, 0.580] | 71/4/0 | 0.0000 |
| privacy_first_llm | QA gain | 0.773 | [0.707, 0.840] | 71/4/0 | 0.0000 |

## Legal

| Baseline | Metric | Mean paired advantage | 95% bootstrap CI | Wins / ties / losses | Sign-test p |
|---|---|---:|---:|---:|---:|
| generic_llm | Direct leak reduction | 0.333 | [0.227, 0.440] | 25/50/0 | 0.0000 |
| generic_llm | QI risk reduction | 1.187 | [0.813, 1.547] | 36/35/4 | 0.0000 |
| generic_llm | Exact TCFR gain | 0.027 | [-0.002, 0.058] | 6/68/1 | 0.1250 |
| generic_llm | Audited TCFR gain | 0.051 | [0.020, 0.087] | 8/67/0 | 0.0078 |
| generic_llm | QA gain | 0.027 | [-0.002, 0.058] | 6/68/1 | 0.1250 |
| privacy_first_llm | Direct leak reduction | 0.000 | [0.000, 0.000] | 0/75/0 | 1.0000 |
| privacy_first_llm | QI risk reduction | -0.173 | [-0.333, -0.053] | 0/68/7 | 0.0156 |
| privacy_first_llm | Exact TCFR gain | 0.347 | [0.276, 0.418] | 45/30/0 | 0.0000 |
| privacy_first_llm | Audited TCFR gain | 0.393 | [0.311, 0.473] | 47/28/0 | 0.0000 |
| privacy_first_llm | QA gain | 0.347 | [0.276, 0.418] | 45/30/0 | 0.0000 |

## Paper Takeaways

- Relative to generic prompting, CSG reduces direct-leak rate by 0.180 and QI risk by 1.607 on paired examples, while increasing audited TCFR by 0.057.
- Relative to privacy-first prompting, CSG increases exact TCFR by 0.487, audited TCFR by 0.466, and QA consistency by 0.560; overall QI risk is still lower by 0.447, though legal-only QI risk is slightly higher for CSG because privacy-first over-generalizes legal facts.
- This paired view supports the paper's tradeoff framing: CSG mainly improves privacy over generic prompting and utility over privacy-first prompting.
