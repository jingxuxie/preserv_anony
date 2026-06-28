# LLM-Audited Fact Retention

Means over example-method rows. Uses gold facts for evaluation only.

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 120 | 0.993 | 0.000 |
| generic_llm | 120 | 0.939 | 0.000 |
| privacy_first_llm | 120 | 0.542 | 0.001 |

## Clinical

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 60 | 0.994 | 0.000 |
| generic_llm | 60 | 0.928 | 0.000 |
| privacy_first_llm | 60 | 0.450 | 0.003 |

## Legal

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 60 | 0.992 | 0.000 |
| generic_llm | 60 | 0.950 | 0.000 |
| privacy_first_llm | 60 | 0.633 | 0.000 |

