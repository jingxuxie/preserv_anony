"""Report exact provider usage for GPT-5.5 external audit runs."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date

from io_utils import read_jsonl, write_json


def dollar_formula(prompt_tokens: int, completion_tokens: int) -> str:
    return (
        f"({prompt_tokens:,} / 1,000,000 * input_price_per_million) + "
        f"({completion_tokens:,} / 1,000,000 * output_price_per_million)"
    )


def cache_ids_for_rows(rows: list[dict]) -> set[str]:
    return {f"{row['id']}:{row['method']}" for row in rows}


def usage_int(row: dict, key: str) -> int:
    usage = row.get("usage") or {}
    return int(usage.get(key) or 0)


def reasoning_tokens(row: dict) -> int:
    details = (row.get("usage") or {}).get("completion_tokens_details") or {}
    return int(details.get("reasoning_tokens") or 0)


def summarize(rows: list[dict]) -> dict:
    by_stage: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    by_output_method: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
    for row in rows:
        stage = str(row.get("method", "missing"))
        output_method = str(row.get("id", "")).split(":", 1)[1] if ":" in str(row.get("id", "")) else "unknown"
        for table, key in [(by_stage, stage), (by_output_method, output_method)]:
            table[key]["rows"] += 1
            table[key]["prompt_tokens"] += usage_int(row, "prompt_tokens")
            table[key]["completion_tokens"] += usage_int(row, "completion_tokens")
            table[key]["total_tokens"] += usage_int(row, "total_tokens")
            table[key]["reasoning_tokens"] += reasoning_tokens(row)
            table[key]["elapsed_ms"] += float(row.get("elapsed_ms") or 0.0)
    return {
        "rows": len(rows),
        "prompt_tokens": sum(usage_int(row, "prompt_tokens") for row in rows),
        "completion_tokens": sum(usage_int(row, "completion_tokens") for row in rows),
        "total_tokens": sum(usage_int(row, "total_tokens") for row in rows),
        "reasoning_tokens": sum(reasoning_tokens(row) for row in rows),
        "elapsed_ms": sum(float(row.get("elapsed_ms") or 0.0) for row in rows),
        "by_stage": materialize(by_stage),
        "by_output_method": materialize(by_output_method),
    }


def materialize(table: dict[str, dict[str, float]]) -> dict[str, dict[str, float]]:
    return {
        key: {
            "rows": int(stats["rows"]),
            "prompt_tokens": int(stats["prompt_tokens"]),
            "completion_tokens": int(stats["completion_tokens"]),
            "total_tokens": int(stats["total_tokens"]),
            "reasoning_tokens": int(stats["reasoning_tokens"]),
            "elapsed_seconds": float(stats["elapsed_ms"]) / 1000.0,
        }
        for key, stats in sorted(table.items())
    }


def table_lines(title: str, table: dict[str, dict[str, float]]) -> list[str]:
    lines = [f"## {title}", ""]
    lines.append("| Group | Rows | Prompt tokens | Completion tokens | Reasoning tokens | Total tokens | Elapsed seconds |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for key, stats in sorted(table.items()):
        lines.append(
            "| `{key}` | {rows} | {prompt:,} | {completion:,} | {reasoning:,} | {total:,} | {elapsed:.1f} |".format(
                key=key,
                rows=stats["rows"],
                prompt=stats["prompt_tokens"],
                completion=stats["completion_tokens"],
                reasoning=stats["reasoning_tokens"],
                total=stats["total_tokens"],
                elapsed=stats["elapsed_seconds"],
            )
        )
    lines.append("")
    return lines


def markdown(payload: dict) -> str:
    total = payload["total"]
    lines = ["# GPT-5.5 External Audit API Usage", ""]
    lines.append(f"Generated: {payload['generated']}")
    lines.append("")
    lines.append(
        "This report uses exact provider `usage` fields stored in the OpenAI cache. "
        "It makes no API calls and does not hard-code model prices."
    )
    lines.append("")
    lines.append("| Scope | Rows | Prompt tokens | Completion tokens | Reasoning tokens | Total tokens | Elapsed seconds |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for key in ["fact_audit", "privacy_audit", "total"]:
        stats = payload[key]
        lines.append(
            "| {key} | {rows} | {prompt:,} | {completion:,} | {reasoning:,} | {total:,} | {elapsed:.1f} |".format(
                key=key,
                rows=stats["rows"],
                prompt=stats["prompt_tokens"],
                completion=stats["completion_tokens"],
                reasoning=stats["reasoning_tokens"],
                total=stats["total_tokens"],
                elapsed=stats["elapsed_ms"] / 1000.0,
            )
        )
    lines.append("")
    lines.append(f"- Rate-free dollar formula: `{dollar_formula(total['prompt_tokens'], total['completion_tokens'])}`.")
    lines.append("- Use the billing dashboard or current pricing table to fill in the per-million token rates.")
    lines.append("")
    lines.extend(table_lines("By Stage", total["by_stage"]))
    lines.extend(table_lines("By Output Method", total["by_output_method"]))
    return "\n".join(lines)


def run(args: argparse.Namespace) -> None:
    fact_ids = cache_ids_for_rows(read_jsonl(args.fact_judgments))
    privacy_ids = cache_ids_for_rows(read_jsonl(args.privacy_judgments))
    cache_rows = [row for row in read_jsonl(args.cache) if row.get("model") == args.model]
    fact_rows = [
        row
        for row in cache_rows
        if row.get("method") == "fact_retention_judge" and row.get("id") in fact_ids and row.get("usage")
    ]
    privacy_rows = [
        row
        for row in cache_rows
        if row.get("method") == "adversarial_privacy_judge" and row.get("id") in privacy_ids and row.get("usage")
    ]
    missing_fact = sorted(fact_ids - {row["id"] for row in fact_rows})
    missing_privacy = sorted(privacy_ids - {row["id"] for row in privacy_rows})
    total_rows = fact_rows + privacy_rows
    payload = {
        "generated": date.today().isoformat(),
        "model": args.model,
        "fact_judgments": args.fact_judgments,
        "privacy_judgments": args.privacy_judgments,
        "missing_fact_cache_rows": missing_fact,
        "missing_privacy_cache_rows": missing_privacy,
        "fact_audit": summarize(fact_rows),
        "privacy_audit": summarize(privacy_rows),
        "total": summarize(total_rows),
    }
    write_json(args.out_json, payload)
    with open(args.out_md, "w", encoding="utf-8") as f:
        f.write(markdown(payload))
        f.write("\n")
    print(f"wrote {args.out_md}")
    print(f"wrote {args.out_json}")
    if missing_fact or missing_privacy:
        raise RuntimeError("missing usage rows; see JSON report")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", default="data/processed/openai_cache.jsonl")
    parser.add_argument("--fact-judgments", default="data/processed/gpt55_fact_judgments_stratified60.jsonl")
    parser.add_argument("--privacy-judgments", default="data/processed/gpt55_privacy_judgments_hard20.jsonl")
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--out-md", default="results/gpt55_external_audit_usage_report.md")
    parser.add_argument("--out-json", default="results/gpt55_external_audit_usage_report.json")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
