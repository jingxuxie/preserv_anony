"""Generate a cache and API-call reproducibility report for the promoted run."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from io_utils import read_jsonl
from run_fact_judge import JUDGE_PROMPT
from run_openai_methods import (
    CSG_EXTRACTED_PROMPT,
    CSG_VERIFY_REPAIR_PROMPT,
    EXTRACT_PRIVACY_AND_FACTS_PROMPT,
    cache_key,
    load_cache,
    parse_json_object,
    prompt_for,
    select_examples,
)


MODEL = "gpt-4.1-nano"
BENCHMARK = Path("data/processed/benchmark.jsonl")
CACHE = Path("data/processed/openai_cache.jsonl")
OUTPUTS = Path("data/processed/openai_anonymized_outputs_n100.jsonl")
OUT_PATH = Path("results/cost_and_cache_report_n100.md")
OUT_JSON = Path("results/cost_and_cache_report_n100.json")
N120_USAGE_REPORT = Path("results/openai_api_usage_n120.md")

STAGE_ORDER = ["anonymize", "csg_extract", "csg_anonymize", "csg_verify_repair", "fact_judge"]


def approx_tokens(text: str) -> int:
    # Transparent rough proxy for budget reporting only. API invoices should use
    # provider usage fields, which were not stored in the early cache schema.
    return max(1, round(len(text) / 4))


def cache_rows(path: Path) -> list[dict]:
    return read_jsonl(path) if path.exists() else []


def cache_text(cache: dict[str, dict], key: str) -> str:
    row = cache[key]
    return str(row.get("text") or row.get("anonymized_text") or "")


def dollar_formula(prompt_tokens: int, response_tokens: int) -> str:
    return (
        f"({prompt_tokens:,} / 1,000,000 * input_price_per_million) + "
        f"({response_tokens:,} / 1,000,000 * output_price_per_million)"
    )


def facts_json(example: dict) -> str:
    indexed = []
    for index, fact in enumerate(example.get("task_critical_facts", [])):
        item = dict(fact)
        item["fact_index"] = index
        indexed.append(item)
    return json.dumps(indexed, ensure_ascii=True)


def main() -> None:
    examples = select_examples(read_jsonl(BENCHMARK), max_examples=100, seed=21)
    examples_by_id = {row["id"]: row for row in examples}
    outputs = read_jsonl(OUTPUTS)
    outputs_by_key = {(row["id"], row["method"]): row for row in outputs}
    cache = load_cache(str(CACHE))
    raw_cache = cache_rows(CACHE)

    required: list[dict] = []

    def add_call(stage: str, method: str, example_id: str, prompt: str, response_key: str | None = None) -> str:
        key = cache_key(MODEL, method, example_id, prompt)
        text = cache_text(cache, key) if key in cache else ""
        required.append(
            {
                "stage": stage,
                "method": method,
                "example_id": example_id,
                "cache_key": key,
                "cached": key in cache,
                "prompt_chars": len(prompt),
                "prompt_tokens_proxy": approx_tokens(prompt),
                "response_chars": len(text),
                "response_tokens_proxy": approx_tokens(text) if text else 0,
                "response_key": response_key or "text",
            }
        )
        return key

    for example in examples:
        add_call("anonymize", "generic_llm", example["id"], prompt_for("generic_llm", example))
        add_call("anonymize", "privacy_first_llm", example["id"], prompt_for("privacy_first_llm", example))

        extraction_prompt = EXTRACT_PRIVACY_AND_FACTS_PROMPT.format(text=example["text"])
        extraction_key = add_call(
            "csg_extract",
            "critical_span_guard_extracted:extract",
            example["id"],
            extraction_prompt,
        )
        extraction = parse_json_object(cache_text(cache, extraction_key))
        privacy_spans = extraction.get("privacy_spans", [])
        task_facts = extraction.get("task_critical_facts", [])
        anonymize_prompt = CSG_EXTRACTED_PROMPT.format(
            text=example["text"],
            privacy_spans=json.dumps(privacy_spans, ensure_ascii=True),
            task_facts=json.dumps(task_facts, ensure_ascii=True),
        )
        draft_key = add_call(
            "csg_anonymize",
            "critical_span_guard_extracted:anonymize",
            example["id"],
            anonymize_prompt,
        )
        verify_prompt = CSG_VERIFY_REPAIR_PROMPT.format(
            original_text=example["text"],
            anonymized_text=cache_text(cache, draft_key),
            privacy_spans=json.dumps(privacy_spans, ensure_ascii=True),
            task_facts=json.dumps(task_facts, ensure_ascii=True),
        )
        add_call(
            "csg_verify_repair",
            "critical_span_guard_extracted:verify_repair",
            example["id"],
            verify_prompt,
        )

    for output in outputs:
        example = examples_by_id[output["id"]]
        prompt = JUDGE_PROMPT.format(
            original_text=example["text"],
            anonymized_text=output["anonymized_text"],
            facts_json=facts_json(example),
        )
        add_call(
            "fact_judge",
            "fact_retention_judge",
            f"{output['id']}:{output['method']}",
            prompt,
        )

    stage_counts = Counter(row["stage"] for row in required)
    missing = [row for row in required if not row["cached"]]
    by_stage: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for row in required:
        by_stage[row["stage"]]["calls"] += 1
        by_stage[row["stage"]]["prompt_tokens_proxy"] += int(row["prompt_tokens_proxy"])
        by_stage[row["stage"]]["response_tokens_proxy"] += int(row["response_tokens_proxy"])

    raw_by_method = Counter(str(row.get("method", "missing")) for row in raw_cache)
    unique_keys = {str(row.get("cache_key")) for row in raw_cache if row.get("cache_key")}
    duplicate_rows = len(raw_cache) - len(unique_keys)
    usage_rows = [row for row in raw_cache if isinstance(row.get("usage"), dict) and row.get("usage")]
    elapsed_rows = [row for row in raw_cache if row.get("elapsed_ms") is not None]
    total_prompt_tokens = sum(int(row.get("usage", {}).get("prompt_tokens", 0)) for row in usage_rows)
    total_completion_tokens = sum(int(row.get("usage", {}).get("completion_tokens", 0)) for row in usage_rows)
    proxy_prompt_total = sum(int(row["prompt_tokens_proxy"]) for row in required)
    proxy_response_total = sum(int(row["response_tokens_proxy"]) for row in required)
    proxy_total = proxy_prompt_total + proxy_response_total
    per_example_prompt = proxy_prompt_total / len(examples)
    per_example_response = proxy_response_total / len(examples)
    projections = []
    for target_examples in [150, 200, 300, 500]:
        scale = target_examples / len(examples)
        prompt = round(proxy_prompt_total * scale)
        response = round(proxy_response_total * scale)
        projections.append(
            {
                "target_examples": target_examples,
                "estimated_response_slots": round(len(required) * scale),
                "prompt_tokens_proxy": prompt,
                "response_tokens_proxy": response,
                "total_tokens_proxy": prompt + response,
                "rate_formula": dollar_formula(prompt, response),
            }
        )
    report_json = {
        "generated": date.today().isoformat(),
        "model": MODEL,
        "examples": len(examples),
        "required_response_slots": len(required),
        "missing_required_cache_entries": len(missing),
        "raw_cache_rows": len(raw_cache),
        "unique_cache_keys": len(unique_keys),
        "duplicate_or_superseded_rows": duplicate_rows,
        "provider_usage_rows": len(usage_rows),
        "elapsed_rows": len(elapsed_rows),
        "token_proxy_method": "round(characters / 4); approximate planning proxy, not provider usage",
        "prompt_tokens_proxy": proxy_prompt_total,
        "response_tokens_proxy": proxy_response_total,
        "total_tokens_proxy": proxy_total,
        "per_example_prompt_tokens_proxy": per_example_prompt,
        "per_example_response_tokens_proxy": per_example_response,
        "stage_summary": {
            stage: {
                "calls": int(by_stage[stage]["calls"]),
                "cached": sum(1 for row in required if row["stage"] == stage and row["cached"]),
                "prompt_tokens_proxy": int(by_stage[stage]["prompt_tokens_proxy"]),
                "response_tokens_proxy": int(by_stage[stage]["response_tokens_proxy"]),
                "average_prompt_tokens_proxy": (
                    int(by_stage[stage]["prompt_tokens_proxy"]) / int(by_stage[stage]["calls"])
                    if by_stage[stage]["calls"]
                    else 0.0
                ),
                "average_response_tokens_proxy": (
                    int(by_stage[stage]["response_tokens_proxy"]) / int(by_stage[stage]["calls"])
                    if by_stage[stage]["calls"]
                    else 0.0
                ),
            }
            for stage in STAGE_ORDER
        },
        "expansion_projections": projections,
        "exact_usage_reports": [
            {
                "path": str(N120_USAGE_REPORT),
                "scope": "Exact provider usage and elapsed time for new bounded n120 expansion calls only.",
                "present": N120_USAGE_REPORT.exists(),
            }
        ],
        "cost_formula": dollar_formula(proxy_prompt_total, proxy_response_total),
        "interpretation": (
            "Use token-proxy counts for budget planning only. Exact dollar cost and latency require provider usage "
            "and elapsed_ms fields, which early cache rows did not store."
        ),
    }

    lines = ["# Cost and Cache Report for n100", ""]
    lines.append(f"Generated: {date.today().isoformat()}")
    lines.append("")
    lines.append(
        "This report documents reproducibility and approximate cost exposure for the promoted 100-example run. "
        "It makes no API calls. Token counts are character/4 proxies because the early cache schema did not store provider token usage or request latency."
    )
    lines.append("")
    lines.append("## Required Cached Calls")
    lines.append("")
    lines.append("| Stage | Required response slots | Cached | Prompt token proxy | Response token proxy |")
    lines.append("|---|---:|---:|---:|---:|")
    for stage in STAGE_ORDER:
        stats = by_stage[stage]
        cached = sum(1 for row in required if row["stage"] == stage and row["cached"])
        lines.append(
            f"| {stage} | {stats['calls']} | {cached} | {stats['prompt_tokens_proxy']} | {stats['response_tokens_proxy']} |"
        )
    lines.append("")
    lines.append(f"- Total required response slots for a cold n100 rebuild: {len(required)}.")
    lines.append(f"- Missing required cache entries for n100 cache-only rebuild: {len(missing)}.")
    lines.append(f"- Current raw cache rows: {len(raw_cache)}; unique cache keys: {len(unique_keys)}; duplicate/superseded rows: {duplicate_rows}.")
    lines.append(
        f"- Cache rows with provider token usage: {len(usage_rows)}; stored prompt tokens: {total_prompt_tokens}; stored completion tokens: {total_completion_tokens}."
    )
    lines.append(f"- Cache rows with elapsed-time fields: {len(elapsed_rows)}.")
    lines.append(f"- Total prompt token proxy: {proxy_prompt_total:,}; total response token proxy: {proxy_response_total:,}; total token proxy: {proxy_total:,}.")
    lines.append(f"- Mean per-example token proxy: prompt {per_example_prompt:.1f}, response {per_example_response:.1f}, total {per_example_prompt + per_example_response:.1f}.")
    lines.append(f"- Rate-free dollar formula for the n100 token proxy: `{dollar_formula(proxy_prompt_total, proxy_response_total)}`.")
    lines.append("")
    lines.append("## Expansion Budget Projection")
    lines.append("")
    lines.append(
        "These are linear token-proxy projections from the promoted n100 run. They are planning estimates only; actual provider billing depends on the tokenizer, model, pricing, retries, and cache behavior."
    )
    lines.append("")
    lines.append("| Target examples | Est. response slots | Prompt token proxy | Response token proxy | Total token proxy | Rate-free cost formula |")
    lines.append("|---:|---:|---:|---:|---:|---|")
    for item in projections:
        lines.append(
            "| {target} | {slots} | {prompt} | {response} | {total} | `{formula}` |".format(
                target=item["target_examples"],
                slots=item["estimated_response_slots"],
                prompt=f"{item['prompt_tokens_proxy']:,}",
                response=f"{item['response_tokens_proxy']:,}",
                total=f"{item['total_tokens_proxy']:,}",
                formula=item["rate_formula"],
            )
        )
    lines.append("")
    lines.append("## Raw Cache Inventory")
    lines.append("")
    lines.append("| Cache method key | Rows |")
    lines.append("|---|---:|")
    for method, count in sorted(raw_by_method.items()):
        lines.append(f"| `{method}` | {count} |")
    lines.append("")
    lines.append("## Reproducibility Commands")
    lines.append("")
    lines.append("The promoted outputs and fact judgments should rebuild from cache without new API calls:")
    lines.append("")
    lines.append("```bash")
    lines.append("conda run -n preserv_anony python src/run_openai_methods.py \\")
    lines.append("  --model gpt-4.1-nano --max-examples 100 --seed 21 \\")
    lines.append("  --methods generic_llm privacy_first_llm critical_span_guard_extracted \\")
    lines.append("  --out data/processed/openai_anonymized_outputs_n100.jsonl --cache-only")
    lines.append("conda run -n preserv_anony python src/run_fact_judge.py \\")
    lines.append("  --model gpt-4.1-nano --outputs data/processed/openai_anonymized_outputs_n100.jsonl \\")
    lines.append("  --out data/processed/openai_fact_judgments_n100.jsonl \\")
    lines.append("  --summary results/openai_fact_judge_summary_n100.json \\")
    lines.append("  --report results/openai_fact_judge_results_n100.md --cache-only")
    lines.append("```")
    lines.append("")
    lines.append("## Paper-Safe Interpretation")
    lines.append("")
    lines.append(
        "- The n100 headline is reproducible from the local cache with zero expected new API calls when using the commands above."
    )
    lines.append(
        "- A cold n100 run would require 800 response slots: 200 baseline anonymization calls, 300 CSG extraction/anonymization/verification calls, and 300 fact-judge calls."
    )
    lines.append(
        "- The project should not report exact dollar cost or latency because token usage and request timing were not persisted in the cache schema."
    )
    lines.append(
        "- For budget planning, use the JSON fields in `results/cost_and_cache_report_n100.json` and insert current provider rates into the rate-free formula."
    )
    lines.append(
        "- Future API calls will persist provider `usage`, `elapsed_ms`, prompt character count, and response character count in `data/processed/openai_cache.jsonl`."
    )
    lines.append(
        "- `results/openai_api_usage_n120.md` records exact provider usage and latency for the 160 new bounded n120 expansion calls; do not combine those exact counts with the older n100 proxy-only rows as if they used the same accounting schema."
    )
    lines.append("")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report_json, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT_PATH}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
