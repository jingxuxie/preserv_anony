# LLM-Audited Fact Retention

Means over example-method rows. Uses gold facts for evaluation only.

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 70 | 0.993 | 0.000 |
| generic_llm | 70 | 0.929 | 0.000 |
| privacy_first_llm | 70 | 0.514 | 0.000 |

## Clinical

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 35 | 1.000 | 0.000 |
| generic_llm | 35 | 0.914 | 0.000 |
| privacy_first_llm | 35 | 0.433 | 0.000 |

## Legal

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 35 | 0.986 | 0.000 |
| generic_llm | 35 | 0.943 | 0.000 |
| privacy_first_llm | 35 | 0.595 | 0.000 |

