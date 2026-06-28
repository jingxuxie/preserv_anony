# LLM Adversarial Privacy Audit

The auditor sees only anonymized text. It does not receive gold privacy spans or the original text.

| Method | N | Mean severity | Severe >=2 | Direct flag | QI/linkage flag | New severe beyond deterministic |
|---|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 20 | 2.400 | 0.900 | 0.050 | 0.900 | 0.700 |
| generic_llm | 20 | 2.800 | 1.000 | 0.600 | 1.000 | 0.300 |
| privacy_first_llm | 20 | 1.800 | 0.700 | 0.000 | 0.700 | 0.650 |

## Clinical

| Method | N | Mean severity | Severe >=2 | Direct flag | QI/linkage flag |
|---|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 2 | 2.000 | 1.000 | 0.000 | 1.000 |
| generic_llm | 2 | 3.000 | 1.000 | 0.000 | 1.000 |
| privacy_first_llm | 2 | 2.000 | 0.500 | 0.000 | 0.500 |

## Legal

| Method | N | Mean severity | Severe >=2 | Direct flag | QI/linkage flag |
|---|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 18 | 2.444 | 0.889 | 0.056 | 0.889 |
| generic_llm | 18 | 2.778 | 1.000 | 0.667 | 1.000 |
| privacy_first_llm | 18 | 1.778 | 0.722 | 0.000 | 0.722 |

