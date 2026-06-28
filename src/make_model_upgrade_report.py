"""Compare a bounded GPT-5.5 anonymization screen against current outputs."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from datetime import date
from pathlib import Path

from io_utils import read_jsonl, write_json
from run_fact_judge import JUDGE_PROMPT
from run_openai_methods import cache_key


METHODS = ["generic_llm", "privacy_first_llm", "critical_span_guard_extracted"]
METHOD_LABELS = {
    "generic_llm": "Generic LLM",
    "privacy_first_llm": "Privacy-first LLM",
    "critical_span_guard_extracted": "Critical Span Guard",
}


def fmt(value: float) -> str:
    if math.isnan(value):
        return "NA"
    return f"{value:.3f}"


def mean(rows: list[dict], key: str) -> float:
    values = [float(row.get(key, math.nan)) for row in rows]
    values = [value for value in values if not math.isnan(value)]
    return sum(values) / len(values) if values else math.nan


def load_ids(path: str) -> list[str]:
    return [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def by_id_method(path: str) -> dict[tuple[str, str], dict]:
    return {(row["id"], row["method"]): row for row in read_jsonl(path)}


def load_jsonl_by_key(path: str) -> dict[str, dict]:
    return {row["cache_key"]: row for row in read_jsonl(path)}


def usage_int(row: dict, key: str) -> int:
    usage = row.get("usage") or {}
    return int(usage.get(key) or 0)


def reasoning_tokens(row: dict) -> int:
    details = ((row.get("usage") or {}).get("completion_tokens_details") or {})
    return int(details.get("reasoning_tokens") or 0)


def summarize_usage(rows: list[dict]) -> dict:
    return {
        "rows": len(rows),
        "prompt_tokens": sum(usage_int(row, "prompt_tokens") for row in rows),
        "completion_tokens": sum(usage_int(row, "completion_tokens") for row in rows),
        "reasoning_tokens": sum(reasoning_tokens(row) for row in rows),
        "total_tokens": sum(usage_int(row, "total_tokens") for row in rows),
        "elapsed_ms": sum(float(row.get("elapsed_ms") or 0.0) for row in rows),
    }


def collect_usage_rows(args: argparse.Namespace, ids: list[str]) -> tuple[dict, list[str]]:
    cache = load_jsonl_by_key(args.cache)
    raw_cache = read_jsonl(args.cache)
    examples = {row["id"]: row for row in read_jsonl(args.benchmark)}
    upgraded_outputs = by_id_method(args.upgraded_outputs)
    missing: list[str] = []
    anonymization_rows: list[dict] = []
    fact_rows: list[dict] = []

    def add_key(key: str) -> None:
        row = cache.get(key)
        if row is None:
            missing.append(f"fact_judge:{key}")
        else:
            fact_rows.append(row)

    def add_anonymization_match(example_id: str, method: str) -> None:
        matches = [
            row
            for row in raw_cache
            if row.get("model") == args.model and row.get("method") == method and row.get("id") == example_id
        ]
        if len(matches) != 1:
            missing.append(f"anonymization:{method}:{example_id}:matches={len(matches)}")
        else:
            anonymization_rows.append(matches[0])

    for example_id in ids:
        for method in [
            "generic_llm",
            "privacy_first_llm",
            "critical_span_guard_extracted:extract",
            "critical_span_guard_extracted:anonymize",
            "critical_span_guard_extracted:verify_repair",
        ]:
            add_anonymization_match(example_id, method)

    for output in upgraded_outputs.values():
        if output["id"] not in set(ids):
            continue
        example = examples[output["id"]]
        facts = []
        for index, fact in enumerate(example.get("task_critical_facts", [])):
            item = dict(fact)
            item["fact_index"] = index
            facts.append(item)
        prompt = JUDGE_PROMPT.format(
            original_text=example["text"],
            anonymized_text=output["anonymized_text"],
            facts_json=json.dumps(facts, ensure_ascii=True),
        )
        add_key(cache_key(args.model, "fact_retention_judge", f"{output['id']}:{output['method']}", prompt))

    total_rows = anonymization_rows + fact_rows
    return {
        "successful_cached_calls": summarize_usage(total_rows),
        "anonymization": summarize_usage(anonymization_rows),
        "upgraded_fact_judge": summarize_usage(fact_rows),
        "uncached_failed_calls": args.uncached_failed_calls,
        "total_call_attempts_including_uncached_failures": len(total_rows) + args.uncached_failed_calls,
    }, missing


def collect_rows(table: dict[tuple[str, str], dict], ids: list[str], method: str) -> list[dict]:
    rows = []
    missing = []
    for example_id in ids:
        row = table.get((example_id, method))
        if row is None:
            missing.append(f"{example_id}:{method}")
        else:
            rows.append(row)
    if missing:
        raise RuntimeError(f"missing rows in comparison input: {missing[:10]}")
    return rows


def summarize_side(
    ids: list[str],
    deterministic: dict[tuple[str, str], dict],
    fact: dict[tuple[str, str], dict],
) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for method in METHODS:
        det_rows = collect_rows(deterministic, ids, method)
        fact_rows = collect_rows(fact, ids, method)
        out[method] = {
            "n": len(det_rows),
            "direct_identifier_leak": mean(det_rows, "direct_identifier_leak"),
            "quasi_identifier_risk": mean(det_rows, "quasi_identifier_risk"),
            "exact_tcfr": mean(det_rows, "tcfr"),
            "qa_consistency": mean(det_rows, "qa_consistency"),
            "audited_tcfr": mean(fact_rows, "audited_tcfr"),
            "audited_ccr": mean(fact_rows, "audited_ccr"),
        }
    return out


def summarize_domains(
    ids: list[str],
    deterministic: dict[tuple[str, str], dict],
    fact: dict[tuple[str, str], dict],
) -> dict[str, dict[str, dict]]:
    ids_by_domain: dict[str, list[str]] = defaultdict(list)
    for example_id in ids:
        row = deterministic.get((example_id, METHODS[0]))
        if row is None:
            raise RuntimeError(f"missing deterministic row for domain lookup: {example_id}")
        ids_by_domain[str(row.get("domain"))].append(example_id)
    return {domain: summarize_side(domain_ids, deterministic, fact) for domain, domain_ids in sorted(ids_by_domain.items())}


def build(args: argparse.Namespace) -> dict:
    ids = load_ids(args.ids_file)
    current_det = by_id_method(args.current_deterministic)
    current_fact = by_id_method(args.current_external_fact)
    upgraded_det = by_id_method(args.upgraded_deterministic)
    upgraded_fact = by_id_method(args.upgraded_fact)
    subset_manifest = read_jsonl(args.subset_manifest)
    usage, missing_usage = collect_usage_rows(args, ids)
    if missing_usage:
        raise RuntimeError(f"missing cache usage rows: {missing_usage[:10]}")

    current = summarize_side(ids, current_det, current_fact)
    upgraded = summarize_side(ids, upgraded_det, upgraded_fact)
    deltas = {}
    for method in METHODS:
        deltas[method] = {
            key: upgraded[method][key] - current[method][key]
            for key in ["direct_identifier_leak", "quasi_identifier_risk", "exact_tcfr", "qa_consistency", "audited_tcfr"]
        }

    return {
        "metadata": {
            "generated": date.today().isoformat(),
            "scope": (
                "Bounded GPT-5.5 anonymization sanity check on a 9-example stress subset. "
                "Not a replacement for the promoted n150 headline or a full 30-example model-upgrade study."
            ),
            "ids_file": args.ids_file,
            "subset_manifest": args.subset_manifest,
            "current_outputs": "gpt-4.1-nano promoted n150 outputs",
            "upgraded_outputs": "gpt-5.5 pilot outputs",
            "fact_judge": "gpt-5.5 for both current and upgraded outputs",
        },
        "subset": {
            "n": len(ids),
            "ids": ids,
            "manifest_rows": subset_manifest,
            "planned_paid_calls_if_cold": {
                "anonymization": len(ids) * 5,
                "upgraded_fact_judge": len(ids) * len(METHODS),
                "total": len(ids) * 5 + len(ids) * len(METHODS),
            },
        },
        "provider_usage": usage,
        "current": current,
        "upgraded": upgraded,
        "delta_upgraded_minus_current": deltas,
        "by_domain": {
            "current": summarize_domains(ids, current_det, current_fact),
            "upgraded": summarize_domains(ids, upgraded_det, upgraded_fact),
        },
        "interpretation": interpret(current, upgraded),
    }


def interpret(current: dict[str, dict], upgraded: dict[str, dict]) -> list[str]:
    notes = []
    if upgraded["generic_llm"]["direct_identifier_leak"] > 0 or upgraded["generic_llm"]["quasi_identifier_risk"] >= 0.5:
        notes.append("Stronger generic prompting still leaves measurable privacy risk on the stress subset.")
    else:
        notes.append("Stronger generic prompting removes measured direct leaks on this subset; larger validation is needed before changing the main claim.")
    if upgraded["privacy_first_llm"]["audited_tcfr"] < upgraded["critical_span_guard_extracted"]["audited_tcfr"]:
        notes.append("Privacy-first prompting still preserves less audited task-critical content than CSG under the GPT-5.5 judge.")
    if (
        upgraded["critical_span_guard_extracted"]["direct_identifier_leak"] == 0.0
        and upgraded["critical_span_guard_extracted"]["audited_tcfr"] >= upgraded["generic_llm"]["audited_tcfr"]
        and upgraded["critical_span_guard_extracted"]["audited_tcfr"] >= upgraded["privacy_first_llm"]["audited_tcfr"]
    ):
        notes.append("CSG remains on the best observed privacy-utility corner for this bounded stronger-model screen.")
    notes.append("Treat this as a speed screen only; the planned full model-upgrade check remains 30 examples.")
    return notes


def write_markdown(payload: dict, out_path: str) -> None:
    lines = ["# GPT-5.5 Model-Upgrade Anonymization Screen", ""]
    lines.append(f"Generated: {payload['metadata']['generated']}")
    lines.append("")
    lines.append(payload["metadata"]["scope"])
    lines.append("")
    calls = payload["subset"]["planned_paid_calls_if_cold"]
    lines.append(
        f"Cold-run API-call guardrail: {calls['anonymization']} anonymization calls plus {calls['upgraded_fact_judge']} upgraded-output fact-judge calls ({calls['total']} total)."
    )
    lines.append("Current-output baseline fact labels reuse the existing GPT-5.5 external fact audit.")
    usage = payload["provider_usage"]
    total_usage = usage["successful_cached_calls"]
    lines.append(
        "Successful cached provider usage for this pilot: {rows} rows, {prompt:,} prompt tokens, {completion:,} completion tokens, {reasoning:,} reasoning tokens, {total:,} total tokens.".format(
            rows=total_usage["rows"],
            prompt=total_usage["prompt_tokens"],
            completion=total_usage["completion_tokens"],
            reasoning=total_usage["reasoning_tokens"],
            total=total_usage["total_tokens"],
        )
    )
    if usage["uncached_failed_calls"]:
        lines.append(
            f"Run note: an earlier too-small completion cap produced {usage['uncached_failed_calls']} uncached failed JSON attempts before the successful rerun."
        )
    lines.append("")
    lines.append("## Overall")
    lines.append("")
    lines.append("| Method | Current direct | Upgraded direct | Current QI | Upgraded QI | Current audited TCFR | Upgraded audited TCFR | Delta audited TCFR |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for method in METHODS:
        cur = payload["current"][method]
        up = payload["upgraded"][method]
        delta = payload["delta_upgraded_minus_current"][method]
        lines.append(
            "| {label} | {cur_direct} | {up_direct} | {cur_qi} | {up_qi} | {cur_audit} | {up_audit} | {delta_audit} |".format(
                label=METHOD_LABELS[method],
                cur_direct=fmt(cur["direct_identifier_leak"]),
                up_direct=fmt(up["direct_identifier_leak"]),
                cur_qi=fmt(cur["quasi_identifier_risk"]),
                up_qi=fmt(up["quasi_identifier_risk"]),
                cur_audit=fmt(cur["audited_tcfr"]),
                up_audit=fmt(up["audited_tcfr"]),
                delta_audit=fmt(delta["audited_tcfr"]),
            )
        )
    lines.append("")
    lines.append("## Exact-Metric Utility")
    lines.append("")
    lines.append("| Method | Current exact TCFR | Upgraded exact TCFR | Current QA | Upgraded QA |")
    lines.append("|---|---:|---:|---:|---:|")
    for method in METHODS:
        cur = payload["current"][method]
        up = payload["upgraded"][method]
        lines.append(
            f"| {METHOD_LABELS[method]} | {fmt(cur['exact_tcfr'])} | {fmt(up['exact_tcfr'])} | {fmt(cur['qa_consistency'])} | {fmt(up['qa_consistency'])} |"
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    for note in payload["interpretation"]:
        lines.append(f"- {note}")
    lines.append("")
    lines.append("## Subset")
    lines.append("")
    lines.append("| Rank | ID | Domain | Screen bucket | Reasons |")
    lines.append("|---:|---|---|---|---|")
    for row in payload["subset"]["manifest_rows"]:
        reasons = "; ".join(row.get("selection_reasons", []))
        lines.append(
            f"| {row.get('model_upgrade_rank')} | `{row['id']}` | {row['domain']} | {row.get('screen_bucket')} | {reasons} |"
        )
    lines.append("")
    lines.append("Caveat: this is a deliberately small stress subset. Do not promote it as a model-scaling result without the planned 30-example follow-up.")
    lines.append("")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids-file", default="data/processed/gpt55_model_upgrade_ids_n9.txt")
    parser.add_argument("--benchmark", default="data/processed/benchmark_n150_llm.jsonl")
    parser.add_argument("--subset-manifest", default="data/processed/gpt55_model_upgrade_subset_n9.jsonl")
    parser.add_argument("--current-deterministic", default="data/processed/openai_judgments_n150.jsonl")
    parser.add_argument("--current-external-fact", default="data/processed/gpt55_fact_judgments_stratified60.jsonl")
    parser.add_argument("--upgraded-outputs", default="data/processed/gpt55_model_upgrade_outputs_n9.jsonl")
    parser.add_argument("--upgraded-deterministic", default="data/processed/gpt55_model_upgrade_judgments_n9.jsonl")
    parser.add_argument("--upgraded-fact", default="data/processed/gpt55_model_upgrade_fact_judgments_n9.jsonl")
    parser.add_argument("--cache", default="data/processed/openai_cache.jsonl")
    parser.add_argument("--model", default="gpt-5.5")
    parser.add_argument("--uncached-failed-calls", type=int, default=3)
    parser.add_argument("--out-json", default="results/gpt55_model_upgrade_report_n9.json")
    parser.add_argument("--out-md", default="results/gpt55_model_upgrade_report_n9.md")
    args = parser.parse_args()

    payload = build(args)
    write_json(args.out_json, payload)
    write_markdown(payload, args.out_md)
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")


if __name__ == "__main__":
    main()
