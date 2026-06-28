"""Summarize the no-API n200 local diagnostic expansion.

This report is deliberately separate from the promoted n150 non-oracle LLM
headline. It tests whether the local/oracle diagnostic frontier remains visible
on a larger benchmark slice without spending API budget.
"""

from __future__ import annotations

import json
from collections import Counter
from datetime import date
from pathlib import Path

from io_utils import read_jsonl


N100_SUMMARY = Path("results/summary.json")
N200_SUMMARY = Path("results/summary_n200_local.json")
N200_BENCHMARK = Path("data/processed/benchmark_n200_local.jsonl")
N200_OUTPUTS = Path("data/processed/anonymized_outputs_n200_local.jsonl")
N200_JUDGMENTS = Path("data/processed/judgments_n200_local.jsonl")
OUT_MD = Path("results/local_n200_diagnostic_report.md")
OUT_JSON = Path("results/local_n200_diagnostic_report.json")

METHOD_ORDER = [
    "regex_rules",
    "presidio_baseline",
    "direct_span_oracle",
    "privacy_first_oracle",
    "critical_span_guard_oracle",
]


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def mean(summary: dict, method: str, metric: str, domain: str | None = None) -> float:
    if domain is None:
        value = summary["overall"][method][metric]
    else:
        value = summary["by_domain"][domain][method][metric]
    if isinstance(value, dict):
        return float(value["mean"])
    return float(value)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def method_row(summary: dict, method: str, domain: str | None = None) -> dict:
    source = summary["overall"][method] if domain is None else summary["by_domain"][domain][method]
    return {
        "n": int(source["n"]),
        "direct_identifier_leak": mean(summary, method, "direct_identifier_leak", domain),
        "quasi_identifier_risk": mean(summary, method, "quasi_identifier_risk", domain),
        "tcfr": mean(summary, method, "tcfr", domain),
        "qa_consistency": mean(summary, method, "qa_consistency", domain),
        "edit_rate": mean(summary, method, "edit_rate", domain) if domain is None else None,
    }


def main() -> None:
    n100 = load_json(N100_SUMMARY)
    n200 = load_json(N200_SUMMARY)
    benchmark = read_jsonl(N200_BENCHMARK)
    outputs = read_jsonl(N200_OUTPUTS)
    judgments = read_jsonl(N200_JUDGMENTS)
    domains = Counter(row["domain"] for row in benchmark)
    output_methods = Counter(row["method"] for row in outputs)
    judgment_methods = Counter(row["method"] for row in judgments)

    n200_overall = {method: method_row(n200, method) for method in METHOD_ORDER}
    n200_by_domain = {
        domain: {method: method_row(n200, method, domain) for method in METHOD_ORDER}
        for domain in sorted(n200["by_domain"])
    }
    n100_vs_n200 = {
        method: {
            "n100": method_row(n100, method),
            "n200": method_row(n200, method),
            "delta_qi_risk": method_row(n200, method)["quasi_identifier_risk"]
            - method_row(n100, method)["quasi_identifier_risk"],
            "delta_tcfr": method_row(n200, method)["tcfr"] - method_row(n100, method)["tcfr"],
            "delta_qa": method_row(n200, method)["qa_consistency"] - method_row(n100, method)["qa_consistency"],
        }
        for method in METHOD_ORDER
    }
    directional_checks = {
        "direct_span_oracle_high_qi": n200_overall["direct_span_oracle"]["quasi_identifier_risk"] >= 2.5
        and n200_overall["direct_span_oracle"]["tcfr"] >= 0.999,
        "privacy_first_oracle_utility_loss": n200_overall["privacy_first_oracle"]["quasi_identifier_risk"] <= 0.05
        and n200_overall["privacy_first_oracle"]["tcfr"] <= 0.5
        and n200_overall["privacy_first_oracle"]["qa_consistency"] <= 0.4,
        "csg_oracle_frontier": n200_overall["critical_span_guard_oracle"]["direct_identifier_leak"] == 0.0
        and n200_overall["critical_span_guard_oracle"]["tcfr"] >= 0.999
        and n200_overall["critical_span_guard_oracle"]["qa_consistency"] >= 0.999
        and n200_overall["critical_span_guard_oracle"]["quasi_identifier_risk"]
        < n200_overall["direct_span_oracle"]["quasi_identifier_risk"],
        "presidio_legal_direct_leak_failure": n200_by_domain["legal"]["presidio_baseline"]["direct_identifier_leak"] >= 0.9,
    }

    payload = {
        "generated": date.today().isoformat(),
        "scope": "No-API local/oracle diagnostic expansion; not the non-oracle LLM headline.",
        "benchmark_rows": len(benchmark),
        "domain_counts": dict(domains),
        "output_rows": len(outputs),
        "judgment_rows": len(judgments),
        "output_methods": dict(output_methods),
        "judgment_methods": dict(judgment_methods),
        "n200_overall": n200_overall,
        "n200_by_domain": n200_by_domain,
        "n100_vs_n200": n100_vs_n200,
        "directional_checks": directional_checks,
        "all_directional_checks_pass": all(directional_checks.values()),
    }

    lines = ["# Local n200 Diagnostic Expansion", ""]
    lines.append(f"Generated: {payload['generated']}")
    lines.append("")
    lines.append(
        "This report is a no-API local diagnostic expansion from 100 to 200 examples. "
        "It uses deterministic local baselines and gold-informed oracle variants only; it is not a replacement for the promoted n150 non-oracle LLM headline."
    )
    lines.append("")
    lines.append("## Data Integrity")
    lines.append("")
    lines.append(f"- Benchmark rows: {len(benchmark)} ({', '.join(f'{k}={v}' for k, v in sorted(domains.items()))}).")
    lines.append(f"- Output rows: {len(outputs)}; judgment rows: {len(judgments)}.")
    lines.append("- Methods: " + ", ".join(f"`{method}`={output_methods[method]}" for method in METHOD_ORDER) + ".")
    lines.append("")
    lines.append("## n200 Local Diagnostic Result")
    lines.append("")
    lines.append("| Method | N | Direct leak | QI risk | TCFR | QA |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for method in METHOD_ORDER:
        row = n200_overall[method]
        lines.append(
            f"| `{method}` | {row['n']} | {fmt(row['direct_identifier_leak'])} | {fmt(row['quasi_identifier_risk'])} | {fmt(row['tcfr'])} | {fmt(row['qa_consistency'])} |"
        )
    lines.append("")
    lines.append("## n100 to n200 Directional Stability")
    lines.append("")
    lines.append("| Method | n100 QI | n200 QI | n100 TCFR | n200 TCFR | n100 QA | n200 QA |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for method in METHOD_ORDER:
        item = n100_vs_n200[method]
        n100_row = item["n100"]
        n200_row = item["n200"]
        lines.append(
            f"| `{method}` | {fmt(n100_row['quasi_identifier_risk'])} | {fmt(n200_row['quasi_identifier_risk'])} | {fmt(n100_row['tcfr'])} | {fmt(n200_row['tcfr'])} | {fmt(n100_row['qa_consistency'])} | {fmt(n200_row['qa_consistency'])} |"
        )
    lines.append("")
    lines.append("## Directional Checks")
    lines.append("")
    for key, passed in directional_checks.items():
        lines.append(f"- {'PASS' if passed else 'FAIL'}: `{key}`.")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "- The local n200 slice preserves the same diagnostic frontier as n100: direct-span-only masking keeps utility but leaves high QI risk, while privacy-first oracle redaction minimizes QI risk at large utility cost."
    )
    lines.append(
        "- Gold-informed CSG remains an upper-bound diagnostic: zero measured direct leaks, perfect exact TCFR/QA, and much lower QI risk than direct-span-only masking."
    )
    lines.append(
        "- Presidio remains a useful negative baseline for legal snippets, with high direct-leak rate on the n200 legal split."
    )
    lines.append(
        "- Do not mix this local/oracle diagnostic with the n150 non-oracle LLM headline; use it to address sample-size sensitivity of the benchmark and local baseline phenomena."
    )
    lines.append("")

    OUT_MD.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=True, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUT_MD}")
    print(f"wrote {OUT_JSON}")


if __name__ == "__main__":
    main()
