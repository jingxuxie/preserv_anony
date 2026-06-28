# LLM-Audited Fact Retention

Means over example-method rows. Uses gold facts for evaluation only.

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 50 | 1.000 | 0.000 |
| generic_llm | 50 | 0.940 | 0.000 |
| privacy_first_llm | 50 | 0.567 | 0.000 |

## Clinical

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 25 | 1.000 | 0.000 |
| generic_llm | 25 | 0.920 | 0.000 |
| privacy_first_llm | 25 | 0.433 | 0.000 |

## Legal

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 25 | 1.000 | 0.000 |
| generic_llm | 25 | 0.960 | 0.000 |
| privacy_first_llm | 25 | 0.700 | 0.000 |

