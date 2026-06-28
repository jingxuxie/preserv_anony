# Combined LLM Results

Deterministic privacy metrics plus exact-string and LLM-audited utility metrics.

| Method | N | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA consistency ↑ |
|---|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 30 | 0.000 | 0.100 | 0.894 | 1.000 | 1.000 |
| generic_llm | 30 | 0.167 | 1.867 | 0.817 | 0.933 | 0.911 |
| privacy_first_llm | 30 | 0.000 | 0.633 | 0.422 | 0.550 | 0.394 |

## Clinical

| Method | N | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA consistency ↑ |
|---|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 15 | 0.000 | 0.000 | 0.789 | 1.000 | 1.000 |
| generic_llm | 15 | 0.000 | 2.000 | 0.678 | 0.889 | 0.867 |
| privacy_first_llm | 15 | 0.000 | 1.200 | 0.222 | 0.478 | 0.167 |

## Legal

| Method | N | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA consistency ↑ |
|---|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 15 | 0.000 | 0.200 | 1.000 | 1.000 | 1.000 |
| generic_llm | 15 | 0.333 | 1.733 | 0.956 | 0.978 | 0.956 |
| privacy_first_llm | 15 | 0.000 | 0.067 | 0.622 | 0.622 | 0.622 |

