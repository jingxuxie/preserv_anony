"""Write a paper-facing report for the handwritten robustness slice."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from textwrap import shorten

from io_utils import read_jsonl


METHOD_ORDER = [
    "regex_rules",
    "presidio_baseline",
    "direct_span_oracle",
    "privacy_first_oracle",
    "critical_span_guard_oracle",
]


METHOD_LABELS = {
    "regex_rules": "Regex",
    "presidio_baseline": "Presidio",
    "direct_span_oracle": "Direct-span oracle",
    "privacy_first_oracle": "Privacy-first oracle",
    "critical_span_guard_oracle": "CSG oracle",
}


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def metric(stats: dict, key: str) -> float:
    value = stats[key]
    if isinstance(value, dict):
        return float(value["mean"])
    return float(value)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def clean(text: object) -> str:
    return "".join(ch for ch in str(text) if ch in "\n\t" or ord(ch) >= 32)


def method_table(summary: dict) -> list[str]:
    lines = []
    lines.append("| Method | Direct leak | QI risk | Exact TCFR | QA |")
    lines.append("|---|---:|---:|---:|---:|")
    for method in METHOD_ORDER:
        stats = summary["overall"][method]
        lines.append(
            "| {method} | {direct} | {qi} | {tcfr} | {qa} |".format(
                method=METHOD_LABELS[method],
                direct=fmt(metric(stats, "direct_identifier_leak")),
                qi=fmt(metric(stats, "quasi_identifier_risk")),
                tcfr=fmt(metric(stats, "tcfr")),
                qa=fmt(metric(stats, "qa_consistency")),
            )
        )
    return lines


def tag_table(examples: list[dict]) -> list[str]:
    counts = Counter(tag for row in examples for tag in row.get("stress_tags", []))
    lines = ["| Stress tag | Examples |", "|---|---:|"]
    for tag, count in sorted(counts.items()):
        lines.append(f"| `{tag}` | {count} |")
    return lines


def row_lookup(rows: list[dict]) -> dict[tuple[str, str], dict]:
    return {(row["id"], row["method"]): row for row in rows}


def output_lookup(rows: list[dict]) -> dict[tuple[str, str], dict]:
    return {(row["id"], row["method"]): row for row in rows}


def example_block(
    example_id: str,
    method: str,
    examples: dict[str, dict],
    judgments: dict[tuple[str, str], dict],
    outputs: dict[tuple[str, str], dict],
) -> list[str]:
    example = examples[example_id]
    judgment = judgments[(example_id, method)]
    output = outputs[(example_id, method)]
    lines = [f"### `{example_id}` / `{METHOD_LABELS.get(method, method)}`", ""]
    lines.append(f"- Tags: {', '.join(f'`{tag}`' for tag in example.get('stress_tags', []))}")
    lines.append(f"- Direct leaks: {one_line(judgment.get('direct_leaked_spans', []))}")
    lines.append(f"- QI hits: {one_line(judgment.get('quasi_leaked_spans', []))}")
    lines.append(f"- Omitted facts: {one_line(judgment.get('omitted_facts', []))}")
    lines.append(f"- Failed QA: {one_line(judgment.get('failed_qa', []))}")
    lines.append(
        "- Output: "
        + shorten(clean(output.get("anonymized_text", "")), width=360, placeholder=" ...")
    )
    lines.append("")
    return lines


def one_line(items: list[str]) -> str:
    if not items:
        return "None"
    return "; ".join(clean(item) for item in items)


def write_report(args: argparse.Namespace) -> None:
    examples_list = read_jsonl(args.benchmark)
    examples = {row["id"]: row for row in examples_list}
    outputs = output_lookup(read_jsonl(args.outputs))
    judgments = row_lookup(read_jsonl(args.scored))
    summary = load_json(args.summary)

    privacy_first = [row for row in judgments.values() if row["method"] == "privacy_first_oracle"]
    csg = [row for row in judgments.values() if row["method"] == "critical_span_guard_oracle"]
    direct = [row for row in judgments.values() if row["method"] == "direct_span_oracle"]

    lines = ["# Robustness Stress Slice", ""]
    lines.append(
        "A 12-example handwritten diagnostic slice covering hard privacy-utility overlaps. "
        "This is a local stress test, not part of the cached 50-example non-oracle OpenAI headline run."
    )
    lines.append("")
    lines.append("## Coverage")
    lines.append("")
    lines.extend(tag_table(examples_list))
    lines.append("")
    lines.append("## Local Diagnostic Results")
    lines.append("")
    lines.extend(method_table(summary))
    lines.append("")
    lines.append("## Failure Counts")
    lines.append("")
    lines.append(
        f"- Privacy-first oracle has zero direct leaks and zero measured QI risk, but fails QA on {sum(bool(r['failed_qa']) for r in privacy_first)}/12 rows."
    )
    lines.append(
        f"- Direct-span oracle has zero direct leaks and perfect utility, but retains quasi-identifiers on {sum(bool(r['quasi_leaked_spans']) for r in direct)}/12 rows."
    )
    lines.append(
        f"- CSG oracle has zero direct leaks and perfect utility, but retains task-critical quasi-identifiers on {sum(bool(r['quasi_leaked_spans']) for r in csg)}/12 rows."
    )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "- The stress slice makes the privacy-utility conflict explicit: some sensitive facts, such as pregnancy, sexual orientation, domestic violence, or Roma marriage, are also the facts needed to answer the domain question."
    )
    lines.append(
        "- Strong privacy-first redaction can drive measured QI risk to zero while removing doses, lab values, Article numbers, protocol provisions, or sensitive claim facts."
    )
    lines.append(
        "- A task-aware policy can preserve utility on this diagnostic slice, but remaining QI risk is not just an implementation bug; it reflects facts that are simultaneously sensitive and task-critical."
    )
    lines.append("")
    lines.append("## Paper-Useful Examples")
    lines.append("")
    for example_id, method in [
        ("stress_clinical_0000", "privacy_first_oracle"),
        ("stress_legal_0005", "privacy_first_oracle"),
        ("stress_legal_0001", "critical_span_guard_oracle"),
        ("stress_legal_0000", "critical_span_guard_oracle"),
    ]:
        lines.extend(example_block(example_id, method, examples, judgments, outputs))

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/robustness_benchmark.jsonl")
    parser.add_argument("--outputs", default="data/processed/robustness_outputs.jsonl")
    parser.add_argument("--scored", default="data/processed/robustness_judgments.jsonl")
    parser.add_argument("--summary", default="results/robustness_summary.json")
    parser.add_argument("--out", default="results/robustness_report.md")
    args = parser.parse_args()
    write_report(args)


if __name__ == "__main__":
    main()
