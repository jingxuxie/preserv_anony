"""Report exact provider usage for an incremental OpenAI expansion slice."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from io_utils import read_jsonl


def dollar_formula(prompt_tokens: int, completion_tokens: int) -> str:
    return (
        f"({prompt_tokens:,} / 1,000,000 * input_price_per_million) + "
        f"({completion_tokens:,} / 1,000,000 * output_price_per_million)"
    )


def cache_example_id(row: dict) -> str:
    value = str(row.get("id", ""))
    if ":" in value:
        return value.split(":", 1)[0]
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", default="data/processed/openai_cache.jsonl")
    parser.add_argument("--base-benchmark", required=True)
    parser.add_argument("--target-benchmark", required=True)
    parser.add_argument("--budget-json", required=True)
    parser.add_argument("--out-md", required=True)
    parser.add_argument("--out-json", required=True)
    parser.add_argument("--label", required=True)
    args = parser.parse_args()

    base_ids = {row["id"] for row in read_jsonl(args.base_benchmark)}
    target_ids = {row["id"] for row in read_jsonl(args.target_benchmark)}
    added_ids = target_ids - base_ids
    cache_rows = read_jsonl(args.cache)
    usage_rows = [
        row
        for row in cache_rows
        if cache_example_id(row) in added_ids
        and isinstance(row.get("usage"), dict)
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
    budget = json.loads(Path(args.budget_json).read_text(encoding="utf-8"))

    payload = {
        "generated": date.today().isoformat(),
        "label": args.label,
        "base_examples": len(base_ids),
        "target_examples": len(target_ids),
        "added_examples": len(added_ids),
        "added_ids": sorted(added_ids),
        "usage_rows": len(usage_rows),
        "prompt_tokens": total_prompt,
        "completion_tokens": total_completion,
        "total_tokens": total_tokens,
        "elapsed_ms": total_elapsed_ms,
        "elapsed_seconds": total_elapsed_ms / 1000.0,
        "rate_formula": dollar_formula(total_prompt, total_completion),
        "cache_coverage": {
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

    lines = [f"# OpenAI {args.label} Incremental API Usage", ""]
    lines.append(f"Generated: {payload['generated']}")
    lines.append("")
    lines.append(
        f"This report covers exact provider token usage and request latency for the {payload['added_examples']} examples added from {payload['base_examples']} to {payload['target_examples']} examples."
    )
    lines.append("")
    lines.append("## Cache Coverage")
    lines.append("")
    lines.append(
        "- Target required response slots cached: {cached}; missing: {missing}.".format(
            cached=budget.get("total_cached_response_slots", "unknown"),
            missing=budget.get("total_missing_response_slots", "unknown"),
        )
    )
    lines.append(f"- Incremental cache rows with provider usage and elapsed time: {len(usage_rows)}.")
    lines.append("")
    lines.append("## Exact Provider Usage for Incremental Rows")
    lines.append("")
    lines.append("| Method/stage | Rows | Prompt tokens | Completion tokens | Total tokens | Elapsed seconds |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for method, stats in sorted(by_method.items()):
        lines.append(
            "| `{method}` | {rows} | {prompt:,} | {completion:,} | {total:,} | {elapsed:.1f} |".format(
                method=method,
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
    lines.append(f"- Rate-free dollar formula: `{dollar_formula(total_prompt, total_completion)}`.")
    lines.append("- Keep these exact incremental counts separate from proxy-only early cache rows.")
    lines.append("")

    out_md = Path(args.out_md)
    out_json = Path(args.out_json)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("\n".join(lines), encoding="utf-8")
    out_json.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {out_md}")
    print(f"wrote {out_json}")


if __name__ == "__main__":
    main()
