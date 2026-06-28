# Combined LLM Results

Deterministic privacy metrics plus exact-string and LLM-audited utility metrics.

| Method | N | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA consistency ↑ |
|---|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 70 | 0.000 | 0.057 | 0.893 | 0.993 | 0.981 |
| generic_llm | 70 | 0.186 | 1.757 | 0.805 | 0.929 | 0.867 |
| privacy_first_llm | 70 | 0.000 | 0.586 | 0.390 | 0.514 | 0.410 |

## Clinical

| Method | N | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA consistency ↑ |
|---|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 35 | 0.000 | 0.000 | 0.824 | 1.000 | 1.000 |
| generic_llm | 35 | 0.029 | 2.029 | 0.676 | 0.914 | 0.800 |
| privacy_first_llm | 35 | 0.000 | 1.143 | 0.190 | 0.433 | 0.229 |

## Legal

| Method | N | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA consistency ↑ |
|---|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 35 | 0.000 | 0.114 | 0.962 | 0.986 | 0.962 |
| generic_llm | 35 | 0.343 | 1.486 | 0.933 | 0.943 | 0.933 |
| privacy_first_llm | 35 | 0.000 | 0.029 | 0.590 | 0.595 | 0.590 |

