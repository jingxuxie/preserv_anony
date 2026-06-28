# LLM-Audited Fact Retention

Means over example-method rows. Uses gold facts for evaluation only.

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 30 | 1.000 | 0.000 |
| generic_llm | 30 | 0.933 | 0.000 |
| privacy_first_llm | 30 | 0.550 | 0.000 |

## Clinical

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 15 | 1.000 | 0.000 |
| generic_llm | 15 | 0.889 | 0.000 |
| privacy_first_llm | 15 | 0.478 | 0.000 |

## Legal

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 15 | 1.000 | 0.000 |
| generic_llm | 15 | 0.978 | 0.000 |
| privacy_first_llm | 15 | 0.622 | 0.000 |

