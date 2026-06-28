"""Write paper-ready result tables from current summary JSON files."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


METHOD_LABELS = {
    "regex_rules": "Regex",
    "presidio_baseline": "Presidio",
    "direct_span_oracle": "Direct-span oracle",
    "privacy_first_oracle": "Privacy-first oracle",
    "critical_span_guard_oracle": "CSG oracle",
    "generic_llm": "Generic LLM",
    "privacy_first_llm": "Privacy-first LLM",
    "critical_span_guard_extracted": "Critical Span Guard",
    "csg_draft": "CSG draft",
    "csg_verified": "CSG verified",
    "csg_verified_safety": "CSG + safety/repair",
}


def load(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def mean(stats: dict, key: str) -> float:
    value = stats[key]
    if isinstance(value, dict):
        return float(value["mean"])
    return float(value)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def main_table(det: dict, audit: dict) -> list[list[str]]:
    rows = [["Method", "Direct leak", "QI risk", "Exact TCFR", "Audited TCFR", "QA"]]
    for method in ["generic_llm", "privacy_first_llm", "critical_span_guard_extracted"]:
        stats = det["overall"][method]
        audit_stats = audit["overall"][method]
        rows.append(
            [
                METHOD_LABELS[method],
                fmt(mean(stats, "direct_identifier_leak")),
                fmt(mean(stats, "quasi_identifier_risk")),
                fmt(mean(stats, "tcfr")),
                fmt(float(audit_stats["audited_tcfr"])),
                fmt(mean(stats, "qa_consistency")),
            ]
        )
    return rows


def domain_table(det: dict, audit: dict) -> list[list[str]]:
    rows = [["Domain", "Method", "Direct leak", "QI risk", "Exact TCFR", "Audited TCFR", "QA"]]
    for domain in ["clinical", "legal"]:
        for method in ["generic_llm", "privacy_first_llm", "critical_span_guard_extracted"]:
            stats = det["by_domain"][domain][method]
            audit_stats = audit["by_domain"][domain][method]
            rows.append(
                [
                    domain.capitalize(),
                    METHOD_LABELS[method],
                    fmt(mean(stats, "direct_identifier_leak")),
                    fmt(mean(stats, "quasi_identifier_risk")),
                    fmt(mean(stats, "tcfr")),
                    fmt(float(audit_stats["audited_tcfr"])),
                    fmt(mean(stats, "qa_consistency")),
                ]
            )
    return rows


def ablation_table(summary: dict) -> list[list[str]]:
    rows = [["Stage", "Direct leak", "QI risk", "Exact TCFR", "QA"]]
    for method in ["csg_draft", "csg_verified", "csg_verified_safety"]:
        stats = summary["overall"][method]
        rows.append(
            [
                METHOD_LABELS[method],
                fmt(mean(stats, "direct_identifier_leak")),
                fmt(mean(stats, "quasi_identifier_risk")),
                fmt(mean(stats, "tcfr")),
                fmt(mean(stats, "qa_consistency")),
            ]
        )
    return rows


def surface_table(summary: dict) -> list[list[str]]:
    rows = [["Method", "Token F1", "Edit rate", "Audited fact-fail rate", "Privacy-fail rate"]]
    for method in ["generic_llm", "privacy_first_llm", "critical_span_guard_extracted"]:
        stats = summary["by_method"][method]
        rows.append(
            [
                METHOD_LABELS[method],
                fmt(float(stats["token_f1"])),
                fmt(float(stats["token_edit_rate"])),
                fmt(float(stats["audited_fact_failure_rate"])),
                fmt(float(stats["privacy_failure_rate"])),
            ]
        )
    return rows


def robustness_table(summary: dict) -> list[list[str]]:
    rows = [["Method", "Direct leak", "QI risk", "Exact TCFR", "QA"]]
    for method in [
        "regex_rules",
        "presidio_baseline",
        "direct_span_oracle",
        "privacy_first_oracle",
        "critical_span_guard_oracle",
    ]:
        stats = summary["overall"][method]
        rows.append(
            [
                METHOD_LABELS[method],
                fmt(mean(stats, "direct_identifier_leak")),
                fmt(mean(stats, "quasi_identifier_risk")),
                fmt(mean(stats, "tcfr")),
                fmt(mean(stats, "qa_consistency")),
            ]
        )
    return rows


def markdown(rows: list[list[str]]) -> str:
    header = rows[0]
    lines = ["| " + " | ".join(header) + " |"]
    lines.append("|" + "|".join(["---"] * len(header)) + "|")
    for row in rows[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def latex(tabular_name: str, rows: list[list[str]]) -> str:
    cols = "l" * len(rows[0])
    lines = [f"\\begin{{table}}[t]", "\\centering", f"\\begin{{tabular}}{{{cols}}}", "\\toprule"]
    lines.append(" & ".join(rows[0]) + r" \\")
    lines.append("\\midrule")
    for row in rows[1:]:
        lines.append(" & ".join(row) + r" \\")
    lines.extend(
        [
            "\\bottomrule",
            "\\end{tabular}",
            f"\\caption{{{tabular_name}}}",
            "\\end{table}",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--det-summary", default="results/openai_summary.json")
    parser.add_argument("--audit-summary", default="results/openai_fact_judge_summary.json")
    parser.add_argument("--ablation-summary", default="results/csg_ablation_summary.json")
    parser.add_argument("--surface-summary", default="results/surface_metric_audit.json")
    parser.add_argument("--robustness-summary", default="results/robustness_summary.json")
    parser.add_argument("--out-md", default="results/paper_ready_tables.md")
    parser.add_argument("--out-tex", default="results/paper_ready_tables.tex")
    parser.add_argument("--sample-label", default="50-example")
    args = parser.parse_args()

    det = load(args.det_summary)
    audit = load(args.audit_summary)
    ablation = load(args.ablation_summary)
    surface = load(args.surface_summary)
    robustness = load(args.robustness_summary)
    tables = [
        (f"Main {args.sample_label} non-oracle results.", main_table(det, audit)),
        (f"Domain split for the {args.sample_label} non-oracle run.", domain_table(det, audit)),
        ("Critical Span Guard ablation.", ablation_table(ablation)),
        ("Surface similarity audit for generic utility metrics.", surface_table(surface)),
        ("Handwritten robustness stress slice.", robustness_table(robustness)),
    ]

    md_parts = ["# Paper-Ready Tables", ""]
    tex_parts = []
    for title, rows in tables:
        md_parts.extend([f"## {title}", "", markdown(rows), ""])
        tex_parts.append(latex(title, rows))
        tex_parts.append("")

    Path(args.out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_tex).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_md).write_text("\n".join(md_parts), encoding="utf-8")
    Path(args.out_tex).write_text("\n".join(tex_parts), encoding="utf-8")
    print(f"wrote {args.out_md}")
    print(f"wrote {args.out_tex}")


if __name__ == "__main__":
    main()
