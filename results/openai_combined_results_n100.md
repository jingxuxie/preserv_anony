# Combined LLM Results

Deterministic privacy metrics plus exact-string and LLM-audited utility metrics.

| Method | N | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA consistency ↑ |
|---|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 100 | 0.000 | 0.090 | 0.898 | 0.995 | 0.982 |
| generic_llm | 100 | 0.190 | 1.800 | 0.823 | 0.938 | 0.892 |
| privacy_first_llm | 100 | 0.000 | 0.630 | 0.383 | 0.510 | 0.405 |

## Clinical

| Method | N | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA consistency ↑ |
|---|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 50 | 0.000 | 0.000 | 0.833 | 1.000 | 1.000 |
| generic_llm | 50 | 0.040 | 2.040 | 0.703 | 0.927 | 0.840 |
| privacy_first_llm | 50 | 0.000 | 1.160 | 0.177 | 0.437 | 0.220 |

## Legal

| Method | N | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA consistency ↑ |
|---|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 50 | 0.000 | 0.180 | 0.963 | 0.990 | 0.963 |
| generic_llm | 50 | 0.340 | 1.560 | 0.943 | 0.950 | 0.943 |
| privacy_first_llm | 50 | 0.000 | 0.100 | 0.590 | 0.583 | 0.590 |

