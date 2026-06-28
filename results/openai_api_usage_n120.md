# OpenAI n120 Expansion API Usage

Generated: 2026-06-28

This report covers exact provider token usage and wall-clock request latency for the new cache rows created during the bounded n120 expansion. Earlier n100 cache rows did not store provider usage and remain covered by the token-proxy cost report.

## Cache Coverage

- n120 required response slots cached: 960; missing: 0.
- New cache rows with provider usage and elapsed time: 160.

## Exact Provider Usage for New Rows

| Method/stage | Rows | Prompt tokens | Completion tokens | Total tokens | Elapsed seconds |
|---|---:|---:|---:|---:|---:|
| `critical_span_guard_extracted:anonymize` | 20 | 16,468 | 2,467 | 18,935 | 21.5 |
| `critical_span_guard_extracted:extract` | 20 | 10,304 | 10,766 | 21,070 | 58.1 |
| `critical_span_guard_extracted:verify_repair` | 20 | 18,615 | 2,744 | 21,359 | 23.7 |
| `fact_retention_judge` | 60 | 48,030 | 22,776 | 70,806 | 134.5 |
| `generic_llm` | 20 | 4,104 | 2,139 | 6,243 | 20.6 |
| `privacy_first_llm` | 20 | 4,344 | 1,844 | 6,188 | 25.0 |
| **Total** | 160 | 101,865 | 42,736 | 144,601 | 283.4 |

- Rate-free dollar formula for the new n120 rows: `(101,865 / 1,000,000 * input_price_per_million) + (42,736 / 1,000,000 * output_price_per_million)`.
- Do not combine these exact usage numbers with the n100 proxy counts as if they came from the same accounting schema.
