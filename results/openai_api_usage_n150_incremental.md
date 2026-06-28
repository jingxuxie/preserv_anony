# OpenAI n120-to-n150 Incremental API Usage

Generated: 2026-06-28

This report covers exact provider token usage and request latency for the 30 examples added from 120 to 150 examples.

## Cache Coverage

- Target required response slots cached: 1200; missing: 0.
- Incremental cache rows with provider usage and elapsed time: 240.

## Exact Provider Usage for Incremental Rows

| Method/stage | Rows | Prompt tokens | Completion tokens | Total tokens | Elapsed seconds |
|---|---:|---:|---:|---:|---:|
| `critical_span_guard_extracted:anonymize` | 30 | 24,107 | 3,416 | 27,523 | 33.0 |
| `critical_span_guard_extracted:extract` | 30 | 15,175 | 15,813 | 30,988 | 81.1 |
| `critical_span_guard_extracted:verify_repair` | 30 | 27,043 | 3,811 | 30,854 | 31.1 |
| `fact_retention_judge` | 90 | 69,040 | 32,785 | 101,825 | 207.6 |
| `generic_llm` | 30 | 5,875 | 2,932 | 8,807 | 26.2 |
| `privacy_first_llm` | 30 | 6,235 | 2,354 | 8,589 | 25.0 |
| **Total** | 240 | 147,475 | 61,111 | 208,586 | 404.0 |

- Rate-free dollar formula: `(147,475 / 1,000,000 * input_price_per_million) + (61,111 / 1,000,000 * output_price_per_million)`.
- Keep these exact incremental counts separate from proxy-only early cache rows.
