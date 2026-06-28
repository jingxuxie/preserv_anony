# Combined LLM Results

Deterministic privacy metrics plus exact-string and LLM-audited utility metrics.

| Method | N | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA consistency ↑ |
|---|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 120 | 0.000 | 0.142 | 0.889 | 0.993 | 0.979 |
| generic_llm | 120 | 0.183 | 1.742 | 0.818 | 0.939 | 0.892 |
| privacy_first_llm | 120 | 0.000 | 0.600 | 0.406 | 0.542 | 0.422 |

## Clinical

| Method | N | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA consistency ↑ |
|---|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 60 | 0.000 | 0.000 | 0.819 | 0.994 | 1.000 |
| generic_llm | 60 | 0.033 | 2.033 | 0.703 | 0.928 | 0.850 |
| privacy_first_llm | 60 | 0.000 | 1.100 | 0.183 | 0.450 | 0.217 |

## Legal

| Method | N | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA consistency ↑ |
|---|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 60 | 0.000 | 0.283 | 0.958 | 0.992 | 0.958 |
| generic_llm | 60 | 0.333 | 1.450 | 0.933 | 0.950 | 0.933 |
| privacy_first_llm | 60 | 0.000 | 0.100 | 0.628 | 0.633 | 0.628 |

