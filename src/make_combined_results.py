"""Combine deterministic privacy metrics with LLM-audited utility metrics."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_json(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def metric(stats: dict, key: str) -> float:
    value = stats[key]
    if isinstance(value, dict):
        return float(value["mean"])
    return float(value)


def write_section(lines: list[str], title: str, det_methods: dict, audit_methods: dict) -> None:
    if title:
        lines.append(f"## {title}")
        lines.append("")
    lines.append("| Method | N | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA consistency ↑ |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for method, det in sorted(det_methods.items()):
        audit = audit_methods.get(method, {})
        audited_tcfr = audit.get("audited_tcfr")
        audited = "NA" if audited_tcfr is None else f"{audited_tcfr:.3f}"
        lines.append(
            "| {method} | {n} | {direct:.3f} | {qi:.3f} | {tcfr:.3f} | {audited} | {qa:.3f} |".format(
                method=method,
                n=det["n"],
                direct=metric(det, "direct_identifier_leak"),
                qi=metric(det, "quasi_identifier_risk"),
                tcfr=metric(det, "tcfr"),
                audited=audited,
                qa=metric(det, "qa_consistency"),
            )
        )
    lines.append("")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--det-summary", default="results/openai_summary.json")
    parser.add_argument("--audit-summary", default="results/openai_fact_judge_summary.json")
    parser.add_argument("--out", default="results/openai_combined_results.md")
    args = parser.parse_args()

    det = load_json(args.det_summary)
    audit = load_json(args.audit_summary)
    lines = ["# Combined LLM Results", ""]
    lines.append("Deterministic privacy metrics plus exact-string and LLM-audited utility metrics.")
    lines.append("")
    write_section(lines, "", det["overall"], audit["overall"])
    for domain in sorted(det["by_domain"]):
        write_section(
            lines,
            domain.capitalize(),
            det["by_domain"][domain],
            audit.get("by_domain", {}).get(domain, {}),
        )
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        f.write("\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
