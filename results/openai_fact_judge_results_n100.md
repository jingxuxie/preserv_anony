# LLM-Audited Fact Retention

Means over example-method rows. Uses gold facts for evaluation only.

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 100 | 0.995 | 0.000 |
| generic_llm | 100 | 0.938 | 0.000 |
| privacy_first_llm | 100 | 0.510 | 0.002 |

## Clinical

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 50 | 1.000 | 0.000 |
| generic_llm | 50 | 0.927 | 0.000 |
| privacy_first_llm | 50 | 0.437 | 0.003 |

## Legal

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 50 | 0.990 | 0.000 |
| generic_llm | 50 | 0.950 | 0.000 |
| privacy_first_llm | 50 | 0.583 | 0.000 |

