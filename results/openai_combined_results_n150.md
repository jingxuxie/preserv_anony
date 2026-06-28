# Combined LLM Results

Deterministic privacy metrics plus exact-string and LLM-audited utility metrics.

| Method | N | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA consistency ↑ |
|---|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 150 | 0.000 | 0.127 | 0.884 | 0.994 | 0.974 |
| generic_llm | 150 | 0.180 | 1.733 | 0.813 | 0.938 | 0.888 |
| privacy_first_llm | 150 | 0.000 | 0.573 | 0.398 | 0.529 | 0.414 |

## Clinical

| Method | N | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA consistency ↑ |
|---|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 75 | 0.000 | 0.000 | 0.820 | 0.996 | 1.000 |
| generic_llm | 75 | 0.027 | 2.027 | 0.704 | 0.933 | 0.853 |
| privacy_first_llm | 75 | 0.000 | 1.067 | 0.193 | 0.458 | 0.227 |

## Legal

| Method | N | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA consistency ↑ |
|---|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 75 | 0.000 | 0.253 | 0.949 | 0.993 | 0.949 |
| generic_llm | 75 | 0.333 | 1.440 | 0.922 | 0.942 | 0.922 |
| privacy_first_llm | 75 | 0.000 | 0.080 | 0.602 | 0.600 | 0.602 |

