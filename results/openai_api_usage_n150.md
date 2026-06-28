# OpenAI n100-to-n150 Incremental API Usage

Generated: 2026-06-28

This report covers exact provider token usage and request latency for the 50 examples added from 100 to 150 examples.

## Cache Coverage

- Target required response slots cached: 1200; missing: 0.
- Incremental cache rows with provider usage and elapsed time: 400.

## Exact Provider Usage for Incremental Rows

| Method/stage | Rows | Prompt tokens | Completion tokens | Total tokens | Elapsed seconds |
|---|---:|---:|---:|---:|---:|
| `critical_span_guard_extracted:anonymize` | 50 | 40,575 | 5,883 | 46,458 | 54.5 |
| `critical_span_guard_extracted:extract` | 50 | 25,479 | 26,579 | 52,058 | 139.3 |
| `critical_span_guard_extracted:verify_repair` | 50 | 45,658 | 6,555 | 52,213 | 54.8 |
| `fact_retention_judge` | 150 | 117,070 | 55,561 | 172,631 | 342.1 |
| `generic_llm` | 50 | 9,979 | 5,071 | 15,050 | 46.8 |
| `privacy_first_llm` | 50 | 10,579 | 4,198 | 14,777 | 50.0 |
| **Total** | 400 | 249,340 | 103,847 | 353,187 | 687.4 |

- Rate-free dollar formula: `(249,340 / 1,000,000 * input_price_per_million) + (103,847 / 1,000,000 * output_price_per_million)`.
- Keep these exact incremental counts separate from proxy-only early cache rows.
