"""Create lightweight paper-facing tables and qualitative examples."""

from __future__ import annotations

import argparse
import csv
import html
import json
from collections import defaultdict
from pathlib import Path

from io_utils import read_jsonl


def load_summary(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_frontier_csv(summary: dict, path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["method", "direct_identifier_leak", "quasi_identifier_risk", "tcfr", "qa_consistency"])
        for method, stats in sorted(summary["overall"].items()):
            writer.writerow(
                [
                    method,
                    stats["direct_identifier_leak"]["mean"],
                    stats["quasi_identifier_risk"]["mean"],
                    stats["tcfr"]["mean"],
                    stats["qa_consistency"]["mean"],
                ]
            )


def write_frontier_svg(summary: dict, path: str) -> None:
    width, height = 720, 460
    margin_left, margin_right, margin_top, margin_bottom = 78, 24, 34, 68
    plot_w = width - margin_left - margin_right
    plot_h = height - margin_top - margin_bottom

    def x(qi: float) -> float:
        return margin_left + (qi / 3.0) * plot_w

    def y(tcfr: float) -> float:
        return margin_top + (1.0 - tcfr) * plot_h

    colors = {
        "regex_rules": "#4c78a8",
        "direct_span_oracle": "#f58518",
        "privacy_first_oracle": "#e45756",
        "critical_span_guard_oracle": "#54a24b",
    }
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="white"/>',
        f'<line x1="{margin_left}" y1="{margin_top + plot_h}" x2="{margin_left + plot_w}" y2="{margin_top + plot_h}" stroke="#333"/>',
        f'<line x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_h}" stroke="#333"/>',
        f'<text x="{width / 2}" y="{height - 18}" text-anchor="middle" font-family="Arial" font-size="15">Quasi-identifier risk (lower is better)</text>',
        f'<text x="18" y="{height / 2}" text-anchor="middle" transform="rotate(-90 18 {height / 2})" font-family="Arial" font-size="15">TCFR (higher is better)</text>',
        f'<text x="{width / 2}" y="22" text-anchor="middle" font-family="Arial" font-size="17" font-weight="bold">Privacy-Utility Frontier, Quick Local Run</text>',
    ]
    for tick in [0, 1, 2, 3]:
        tx = x(tick)
        parts.append(f'<line x1="{tx:.1f}" y1="{margin_top + plot_h}" x2="{tx:.1f}" y2="{margin_top + plot_h + 5}" stroke="#333"/>')
        parts.append(f'<text x="{tx:.1f}" y="{margin_top + plot_h + 22}" text-anchor="middle" font-family="Arial" font-size="12">{tick}</text>')
    for tick in [0.0, 0.25, 0.5, 0.75, 1.0]:
        ty = y(tick)
        parts.append(f'<line x1="{margin_left - 5}" y1="{ty:.1f}" x2="{margin_left}" y2="{ty:.1f}" stroke="#333"/>')
        parts.append(f'<text x="{margin_left - 10}" y="{ty + 4:.1f}" text-anchor="end" font-family="Arial" font-size="12">{tick:.2f}</text>')
    for method, stats in sorted(summary["overall"].items()):
        qi = stats["quasi_identifier_risk"]["mean"]
        tcfr = stats["tcfr"]["mean"]
        cx, cy = x(qi), y(tcfr)
        color = colors.get(method, "#777")
        label = method.replace("_oracle", "").replace("_", " ")
        parts.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="7" fill="{color}" stroke="#222"/>')
        parts.append(f'<text x="{cx + 10:.1f}" y="{cy - 9:.1f}" font-family="Arial" font-size="12">{html.escape(label)}</text>')
    parts.append("</svg>")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
        f.write("\n")


def write_failure_examples(benchmark_path: str, outputs_path: str, scored_path: str, path: str) -> None:
    examples = {row["id"]: row for row in read_jsonl(benchmark_path)}
    outputs = {(row["id"], row["method"]): row for row in read_jsonl(outputs_path)}
    scored = read_jsonl(scored_path)
    by_method = defaultdict(list)
    for row in scored:
        if row["omitted_facts"] or row["direct_leaked_spans"] or row["quasi_leaked_spans"]:
            by_method[row["method"]].append(row)

    lines = ["# Qualitative Failure Candidates", ""]
    lines.append("Generated from deterministic scoring; manually audit before using in the paper.")
    lines.append("")
    for method in sorted(by_method):
        lines.append(f"## {method}")
        lines.append("")
        rows = sorted(
            by_method[method],
            key=lambda r: (len(r["omitted_facts"]), len(r["direct_leaked_spans"]), len(r["quasi_leaked_spans"])),
            reverse=True,
        )[:4]
        for row in rows:
            ex = examples[row["id"]]
            out = outputs[(row["id"], method)]
            lines.append(f"### {row['id']} ({row['domain']})")
            lines.append("")
            lines.append(f"- Direct leaks: {row['direct_leaked_spans']}")
            lines.append(f"- Quasi leaks: {row['quasi_leaked_spans']}")
            lines.append(f"- Omitted facts: {row['omitted_facts']}")
            lines.append("")
            lines.append("Original:")
            lines.append("")
            lines.append(f"> {ex['text']}")
            lines.append("")
            lines.append("Anonymized:")
            lines.append("")
            lines.append(f"> {out['anonymized_text']}")
            lines.append("")
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        f.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/benchmark.jsonl")
    parser.add_argument("--outputs", default="data/processed/anonymized_outputs.jsonl")
    parser.add_argument("--scored", default="data/processed/judgments.jsonl")
    parser.add_argument("--summary", default="results/summary.json")
    parser.add_argument("--frontier-csv", default="results/privacy_utility_frontier.csv")
    parser.add_argument("--frontier-svg", default="results/privacy_utility_frontier.svg")
    parser.add_argument("--failures", default="results/failure_examples.md")
    args = parser.parse_args()

    summary = load_summary(args.summary)
    write_frontier_csv(summary, args.frontier_csv)
    write_frontier_svg(summary, args.frontier_svg)
    write_failure_examples(args.benchmark, args.outputs, args.scored, args.failures)
    print(f"wrote {args.frontier_csv}")
    print(f"wrote {args.frontier_svg}")
    print(f"wrote {args.failures}")


if __name__ == "__main__":
    main()
