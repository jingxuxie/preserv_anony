# LLM-Audited Fact Retention

Means over example-method rows. Uses gold facts for evaluation only.

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 150 | 0.994 | 0.000 |
| generic_llm | 150 | 0.938 | 0.000 |
| privacy_first_llm | 150 | 0.529 | 0.001 |

## Clinical

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 75 | 0.996 | 0.000 |
| generic_llm | 75 | 0.933 | 0.000 |
| privacy_first_llm | 75 | 0.458 | 0.002 |

## Legal

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 75 | 0.993 | 0.000 |
| generic_llm | 75 | 0.942 | 0.000 |
| privacy_first_llm | 75 | 0.600 | 0.000 |

