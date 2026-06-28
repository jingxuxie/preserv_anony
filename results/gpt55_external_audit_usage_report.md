# GPT-5.5 External Audit API Usage

Generated: 2026-06-28

This report uses exact provider `usage` fields stored in the OpenAI cache. It makes no API calls and does not hard-code model prices.

| Scope | Rows | Prompt tokens | Completion tokens | Reasoning tokens | Total tokens | Elapsed seconds |
|---|---:|---:|---:|---:|---:|---:|
| fact_audit | 180 | 136,709 | 74,441 | 23,548 | 211,150 | 967.4 |
| privacy_audit | 60 | 24,136 | 43,005 | 20,787 | 67,141 | 657.1 |
| total | 240 | 160,845 | 117,446 | 44,335 | 278,291 | 1624.5 |

- Rate-free dollar formula: `(160,845 / 1,000,000 * input_price_per_million) + (117,446 / 1,000,000 * output_price_per_million)`.
- Use the billing dashboard or current pricing table to fill in the per-million token rates.

## By Stage

| Group | Rows | Prompt tokens | Completion tokens | Reasoning tokens | Total tokens | Elapsed seconds |
|---|---:|---:|---:|---:|---:|---:|
| `adversarial_privacy_judge` | 60 | 24,136 | 43,005 | 20,787 | 67,141 | 657.1 |
| `fact_retention_judge` | 180 | 136,709 | 74,441 | 23,548 | 211,150 | 967.4 |

## By Output Method

| Group | Rows | Prompt tokens | Completion tokens | Reasoning tokens | Total tokens | Elapsed seconds |
|---|---:|---:|---:|---:|---:|---:|
| `critical_span_guard_extracted` | 80 | 54,876 | 38,549 | 14,491 | 93,425 | 542.4 |
| `generic_llm` | 80 | 53,759 | 37,780 | 12,415 | 91,539 | 514.1 |
| `privacy_first_llm` | 80 | 52,210 | 41,117 | 17,429 | 93,327 | 568.0 |

