"""Report exact provider usage for the bounded n120 OpenAI expansion."""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from io_utils import read_jsonl


CACHE = Path("data/processed/openai_cache.jsonl")
BUDGET = Path("results/openai_expansion_budget_n120_final.json")
OUT_MD = Path("results/openai_api_usage_n120.md")
OUT_JSON = Path("results/openai_api_usage_n120.json")


def dollar_formula(prompt_tokens: int, completion_tokens: int) -> str:
    return (
        f"({prompt_tokens:,} / 1,000,000 * input_price_per_million) + "
        f"({completion_tokens:,} / 1,000,000 * output_price_per_million)"
    )


def main() -> None:
    cache_rows = read_jsonl(CACHE)
    usage_rows = [
        row
        for row in cache_rows
        if isinstance(row.get("usage"), dict)
        and row.get("usage")
        and row.get("elapsed_ms") is not None
    ]
    by_method: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in usage_rows:
        method = str(row.get("method", "missing"))
        usage = row["usage"]
        by_method[method]["rows"] += 1
        by_method[method]["prompt_tokens"] += int(usage.get("prompt_tokens") or 0)
        by_method[method]["completion_tokens"] += int(usage.get("completion_tokens") or 0)
        by_method[method]["total_tokens"] += int(usage.get("total_tokens") or 0)
        by_method[method]["elapsed_ms"] += float(row.get("elapsed_ms") or 0.0)

    total_prompt = sum(int(row["usage"].get("prompt_tokens") or 0) for row in usage_rows)
    total_completion = sum(int(row["usage"].get("completion_tokens") or 0) for row in usage_rows)
    total_tokens = sum(int(row["usage"].get("total_tokens") or 0) for row in usage_rows)
    total_elapsed_ms = sum(float(row.get("elapsed_ms") or 0.0) for row in usage_rows)
    budget = json.loads(BUDGET.read_text(encoding="utf-8")) if BUDGET.exists() else {}
    payload = {
        "generated": date.today().isoformat(),
        "scope": "Exact provider usage for new cache rows created during the bounded n120 expansion.",
        "usage_rows": len(usage_rows),
        "prompt_tokens": total_prompt,
        "completion_tokens": total_completion,
        "total_tokens": total_tokens,
        "elapsed_ms": total_elapsed_ms,
        "elapsed_seconds": total_elapsed_ms / 1000.0,
        "rate_formula": dollar_formula(total_prompt, total_completion),
        "n120_cache_coverage": {
            "cached_response_slots": budget.get("total_cached_response_slots"),
            "missing_response_slots": budget.get("total_missing_response_slots"),
        },
        "by_method": {
            method: {
                "rows": int(stats["rows"]),
                "prompt_tokens": int(stats["prompt_tokens"]),
                "completion_tokens": int(stats["completion_tokens"]),
                "total_tokens": int(stats["total_tokens"]),
                "elapsed_seconds": float(stats["elapsed_ms"]) / 1000.0,
            }
            for method, stats in sorted(by_method.items())
        },
    }

    lines = ["# OpenAI n120 Expansion API Usage", ""]
    lines.append(f"Generated: {date.today().isoformat()}")
    lines.append("")
    lines.append(
        "This report covers exact provider token usage and wall-clock request latency for the new cache rows created during the bounded n120 expansion. Earlier n100 cache rows did not store provider usage and remain covered by the token-proxy cost report."
    )
    lines.append("")
    lines.append("## Cache Coverage")
    lines.append("")
    lines.append(
        "- n120 required response slots cached: {cached}; missing: {missing}.".format(
            cached=budget.get("total_cached_response_slots", "unknown"),
            missing=budget.get("total_missing_response_slots", "unknown"),
        )
    )
    lines.append(f"- New cache rows with provider usage and elapsed time: {len(usage_rows)}.")
    lines.append("")
    lines.append("## Exact Provider Usage for New Rows")
    lines.append("")
    lines.append("| Method/stage | Rows | Prompt tokens | Completion tokens | Total tokens | Elapsed seconds |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for method, stats in sorted(by_method.items()):
        lines.append(
            "| {method} | {rows} | {prompt:,} | {completion:,} | {total:,} | {elapsed:.1f} |".format(
                method=f"`{method}`",
                rows=int(stats["rows"]),
                prompt=int(stats["prompt_tokens"]),
                completion=int(stats["completion_tokens"]),
                total=int(stats["total_tokens"]),
                elapsed=float(stats["elapsed_ms"]) / 1000.0,
            )
        )
    lines.append(
        "| **Total** | {rows} | {prompt:,} | {completion:,} | {total:,} | {elapsed:.1f} |".format(
            rows=len(usage_rows),
            prompt=total_prompt,
            completion=total_completion,
            total=total_tokens,
            elapsed=total_elapsed_ms / 1000.0,
        )
    )
    lines.append("")
    lines.append(f"- Rate-free dollar formula for the new n120 rows: `{dollar_formula(total_prompt, total_completion)}`.")
    lines.append("- Do not combine these exact usage numbers with the n100 proxy counts as if they came from the same accounting schema.")
    lines.append("")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
