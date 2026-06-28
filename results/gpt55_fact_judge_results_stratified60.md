# LLM-Audited Fact Retention

Means over example-method rows. Uses gold facts for evaluation only.

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 60 | 0.917 | 0.000 |
| generic_llm | 60 | 0.875 | 0.000 |
| privacy_first_llm | 60 | 0.483 | 0.014 |

## Clinical

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 22 | 0.894 | 0.000 |
| generic_llm | 22 | 0.833 | 0.000 |
| privacy_first_llm | 22 | 0.356 | 0.038 |

## Legal

| Method | N | Audited TCFR ↑ | Audited CCR ↓ |
|---|---:|---:|---:|
| critical_span_guard_extracted | 38 | 0.930 | 0.000 |
| generic_llm | 38 | 0.899 | 0.000 |
| privacy_first_llm | 38 | 0.557 | 0.000 |

