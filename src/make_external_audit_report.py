"""Compare current and independent audit judgments on the stratified subset."""

from __future__ import annotations

import argparse
import math
import re
from collections import Counter, defaultdict

from io_utils import read_jsonl, write_json


def load_ids(path: str) -> list[str]:
    with open(path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def retained(status: str, fact: dict) -> bool:
    if status == "preserved":
        return True
    if status == "generalized_but_acceptable":
        return bool(fact.get("generalization_allowed"))
    return False


def fact_map(row: dict) -> dict[int, dict]:
    out = {}
    for judgment in row.get("fact_judgments", []):
        try:
            out[int(judgment.get("fact_index"))] = judgment
        except (TypeError, ValueError):
            continue
    return out


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else math.nan


def categorize_disagreement(domain: str, fact_text: str, current: dict, external: dict) -> str:
    text = " ".join(
        [
            domain,
            fact_text,
            str(current.get("status", "")),
            str(current.get("evidence", "")),
            str(external.get("status", "")),
            str(external.get("evidence", "")),
        ]
    ).lower()
    if re.search(r"\b(homosexual|sexuality|widow|ethnic|rom|nationality|irish|british)\b", text):
        return "sensitive attribute overlap"
    if domain == "clinical" and re.search(r"\b(\d+|mg|ml|mmol|ph|percent|dose|lab|oxygen|glucose|ct|mri)\b", text):
        return "clinical numeric/specificity"
    if domain == "legal" and re.search(
        r"\b(article|protocol|section|act|convention|jurisdiction|authorit|state|court|violation|inadmissible)\b",
        text,
    ):
        return "legal specificity"
    if "general" in text or "paraphrase" in text:
        return "generalization/paraphrase"
    if "missing judgment" in text or "unclear" in text:
        return "judge uncertainty"
    return "other"


def compare_fact_rows(examples: dict[str, dict], current_rows: list[dict], external_rows: list[dict]) -> dict:
    current = {(row["id"], row["method"]): row for row in current_rows}
    external = {(row["id"], row["method"]): row for row in external_rows}
    by_method: dict[str, dict] = defaultdict(lambda: {"rows": [], "agreements": [], "categories": Counter()})
    disagreements = []
    for key, external_row in sorted(external.items()):
        example_id, method = key
        current_row = current.get(key)
        if current_row is None:
            continue
        by_method[method]["rows"].append(
            {
                "current_tcfr": float(current_row.get("audited_tcfr", math.nan)),
                "external_tcfr": float(external_row.get("audited_tcfr", math.nan)),
            }
        )
        facts = examples[example_id].get("task_critical_facts", [])
        current_by_index = fact_map(current_row)
        external_by_index = fact_map(external_row)
        for index, fact in enumerate(facts):
            cur = current_by_index.get(index, {})
            ext = external_by_index.get(index, {})
            cur_retained = retained(str(cur.get("status", "")), fact)
            ext_retained = retained(str(ext.get("status", "")), fact)
            by_method[method]["agreements"].append(cur_retained == ext_retained)
            if cur_retained != ext_retained:
                category = categorize_disagreement(examples[example_id]["domain"], str(fact.get("fact", "")), cur, ext)
                by_method[method]["categories"][category] += 1
                disagreements.append(
                    {
                        "id": example_id,
                        "domain": examples[example_id]["domain"],
                        "method": method,
                        "fact_index": index,
                        "fact": fact.get("fact", ""),
                        "current_status": cur.get("status", "missing"),
                        "external_status": ext.get("status", "missing"),
                        "category": category,
                    }
                )
    summary = {"overall": {}, "disagreements": disagreements}
    for method, data in sorted(by_method.items()):
        rows = data["rows"]
        categories = data["categories"]
        main_category = categories.most_common(1)[0][0] if categories else "none"
        summary["overall"][method] = {
            "n": len(rows),
            "current_audited_tcfr": mean([row["current_tcfr"] for row in rows]),
            "external_audited_tcfr": mean([row["external_tcfr"] for row in rows]),
            "absolute_delta": mean([row["external_tcfr"] - row["current_tcfr"] for row in rows]),
            "fact_label_agreement": mean([1.0 if item else 0.0 for item in data["agreements"]]),
            "main_disagreement_type": main_category,
            "disagreement_counts": dict(categories),
        }
    return summary


def privacy_summary(rows: list[dict]) -> dict[str, dict]:
    by_method: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_method[row["method"]].append(row)
    out = {}
    for method, method_rows in sorted(by_method.items()):
        out[method] = {
            "n": len(method_rows),
            "mean_max_severity": mean([float(row["max_severity"]) for row in method_rows]),
            "severe_flag_rate": mean([1.0 if row.get("has_severe_flag") else 0.0 for row in method_rows]),
            "new_severe_beyond_deterministic_rate": mean(
                [1.0 if row.get("new_severe_beyond_deterministic") else 0.0 for row in method_rows]
            ),
        }
    return out


def fmt(value: float) -> str:
    if math.isnan(value):
        return "NA"
    return f"{value:.3f}"


def markdown_report(fact_summary: dict, privacy: dict[str, dict], model: str) -> str:
    lines = ["# External Audit Comparison", ""]
    lines.append(f"External auditor model: `{model}`")
    lines.append("")
    lines.append("## Fact Retention")
    lines.append("")
    lines.append(
        "| Method | N | Current audited TCFR | External audited TCFR | Delta | Fact-label agreement | Main disagreement type |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---|")
    for method, stats in sorted(fact_summary["overall"].items()):
        lines.append(
            "| {method} | {n} | {cur} | {ext} | {delta} | {agree} | {kind} |".format(
                method=method,
                n=stats["n"],
                cur=fmt(stats["current_audited_tcfr"]),
                ext=fmt(stats["external_audited_tcfr"]),
                delta=fmt(stats["absolute_delta"]),
                agree=fmt(stats["fact_label_agreement"]),
                kind=stats["main_disagreement_type"],
            )
        )
    if privacy:
        lines.append("")
        lines.append("## Privacy Audit")
        lines.append("")
        lines.append("| Method | N | Mean max severity | Severe >=2 | New severe beyond deterministic |")
        lines.append("|---|---:|---:|---:|---:|")
        for method, stats in sorted(privacy.items()):
            lines.append(
                "| {method} | {n} | {sev} | {severe} | {new} |".format(
                    method=method,
                    n=stats["n"],
                    sev=fmt(stats["mean_max_severity"]),
                    severe=fmt(stats["severe_flag_rate"]),
                    new=fmt(stats["new_severe_beyond_deterministic_rate"]),
                )
            )
    lines.append("")
    lines.append("## Disagreement Counts")
    lines.append("")
    lines.append("| Method | Category | Count |")
    lines.append("|---|---|---:|")
    for method, stats in sorted(fact_summary["overall"].items()):
        counts = stats.get("disagreement_counts", {})
        if not counts:
            lines.append(f"| {method} | none | 0 |")
        for category, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
            lines.append(f"| {method} | {category} | {count} |")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> None:
    ids = set(load_ids(args.ids_file))
    examples = {row["id"]: row for row in read_jsonl(args.benchmark) if row["id"] in ids}
    current_rows = [row for row in read_jsonl(args.current_fact_judgments) if row["id"] in ids]
    external_rows = read_jsonl(args.external_fact_judgments)
    fact_summary = compare_fact_rows(examples, current_rows, external_rows)
    privacy = privacy_summary(read_jsonl(args.privacy_judgments)) if args.privacy_judgments else {}
    out = {
        "model": args.model,
        "ids_file": args.ids_file,
        "fact_retention": fact_summary,
        "privacy": privacy,
    }
    write_json(args.summary, out)
    with open(args.report, "w", encoding="utf-8") as f:
        f.write(markdown_report(fact_summary, privacy, args.model))
        f.write("\n")
    print(f"wrote {args.summary}")
    print(f"wrote {args.report}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/benchmark_n150_llm.jsonl")
    parser.add_argument("--ids-file", default="data/processed/gpt55_audit_ids_60.txt")
    parser.add_argument("--current-fact-judgments", default="data/processed/openai_fact_judgments_n150.jsonl")
    parser.add_argument("--external-fact-judgments", default="data/processed/gpt55_fact_judgments_stratified60.jsonl")
    parser.add_argument("--privacy-judgments", default="data/processed/gpt55_privacy_judgments_stratified60.jsonl")
    parser.add_argument("--summary", default="results/gpt55_external_audit_comparison_stratified60.json")
    parser.add_argument("--report", default="results/gpt55_external_audit_comparison_stratified60.md")
    parser.add_argument("--model", default="gpt-5.5")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
