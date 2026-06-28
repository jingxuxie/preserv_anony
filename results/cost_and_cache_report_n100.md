# Cost and Cache Report for n100

Generated: 2026-06-28

This report documents reproducibility and approximate cost exposure for the promoted 100-example run. It makes no API calls. Token counts are character/4 proxies because the early cache schema did not store provider token usage or request latency.

## Required Cached Calls

| Stage | Required response slots | Cached | Prompt token proxy | Response token proxy |
|---|---:|---:|---:|---:|
| anonymize | 200 | 200 | 45577 | 22260 |
| csg_extract | 100 | 100 | 59389 | 49664 |
| csg_anonymize | 100 | 100 | 81174 | 11856 |
| csg_verify_repair | 100 | 100 | 89900 | 12787 |
| fact_judge | 300 | 300 | 235962 | 103086 |

- Total required response slots for a cold n100 rebuild: 800.
- Missing required cache entries for n100 cache-only rebuild: 0.
- Current raw cache rows: 1109; unique cache keys: 1108; duplicate/superseded rows: 1.
- Cache rows with provider token usage: 160; stored prompt tokens: 101865; stored completion tokens: 42736.
- Cache rows with elapsed-time fields: 160.
- Total prompt token proxy: 512,002; total response token proxy: 199,653; total token proxy: 711,655.
- Mean per-example token proxy: prompt 5120.0, response 1996.5, total 7116.6.
- Rate-free dollar formula for the n100 token proxy: `(512,002 / 1,000,000 * input_price_per_million) + (199,653 / 1,000,000 * output_price_per_million)`.

## Expansion Budget Projection

These are linear token-proxy projections from the promoted n100 run. They are planning estimates only; actual provider billing depends on the tokenizer, model, pricing, retries, and cache behavior.

| Target examples | Est. response slots | Prompt token proxy | Response token proxy | Total token proxy | Rate-free cost formula |
|---:|---:|---:|---:|---:|---|
| 150 | 1200 | 768,003 | 299,480 | 1,067,483 | `(768,003 / 1,000,000 * input_price_per_million) + (299,480 / 1,000,000 * output_price_per_million)` |
| 200 | 1600 | 1,024,004 | 399,306 | 1,423,310 | `(1,024,004 / 1,000,000 * input_price_per_million) + (399,306 / 1,000,000 * output_price_per_million)` |
| 300 | 2400 | 1,536,006 | 598,959 | 2,134,965 | `(1,536,006 / 1,000,000 * input_price_per_million) + (598,959 / 1,000,000 * output_price_per_million)` |
| 500 | 4000 | 2,560,010 | 998,265 | 3,558,275 | `(2,560,010 / 1,000,000 * input_price_per_million) + (998,265 / 1,000,000 * output_price_per_million)` |

## Raw Cache Inventory

| Cache method key | Rows |
|---|---:|
| `critical_span_guard_extracted:anonymize` | 124 |
| `critical_span_guard_extracted:extract` | 125 |
| `critical_span_guard_extracted:verify_repair` | 124 |
| `critical_span_guard_goldprompt` | 6 |
| `fact_retention_judge` | 484 |
| `generic_llm` | 123 |
| `privacy_first_llm` | 123 |

## Reproducibility Commands

The promoted outputs and fact judgments should rebuild from cache without new API calls:

```bash
conda run -n preserv_anony python src/run_openai_methods.py \
  --model gpt-4.1-nano --max-examples 100 --seed 21 \
  --methods generic_llm privacy_first_llm critical_span_guard_extracted \
  --out data/processed/openai_anonymized_outputs_n100.jsonl --cache-only
conda run -n preserv_anony python src/run_fact_judge.py \
  --model gpt-4.1-nano --outputs data/processed/openai_anonymized_outputs_n100.jsonl \
  --out data/processed/openai_fact_judgments_n100.jsonl \
  --summary results/openai_fact_judge_summary_n100.json \
  --report results/openai_fact_judge_results_n100.md --cache-only
```

## Paper-Safe Interpretation

- The n100 headline is reproducible from the local cache with zero expected new API calls when using the commands above.
- A cold n100 run would require 800 response slots: 200 baseline anonymization calls, 300 CSG extraction/anonymization/verification calls, and 300 fact-judge calls.
- The project should not report exact dollar cost or latency because token usage and request timing were not persisted in the cache schema.
- For budget planning, use the JSON fields in `results/cost_and_cache_report_n100.json` and insert current provider rates into the rate-free formula.
- Future API calls will persist provider `usage`, `elapsed_ms`, prompt character count, and response character count in `data/processed/openai_cache.jsonl`.
- `results/openai_api_usage_n120.md` records exact provider usage and latency for the 160 new bounded n120 expansion calls; do not combine those exact counts with the older n100 proxy-only rows as if they used the same accounting schema.
