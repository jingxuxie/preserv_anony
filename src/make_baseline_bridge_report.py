"""Generate a bridge report between local baselines, oracles, and LLM methods."""

from __future__ import annotations

import json
from pathlib import Path


OUT_PATH = Path("results/baseline_bridge_report.md")


METHOD_LABELS = {
    "regex_rules": "Regex rules",
    "presidio_baseline": "Presidio baseline",
    "direct_span_oracle": "Direct-span oracle",
    "privacy_first_oracle": "Privacy-first oracle",
    "critical_span_guard_oracle": "CSG oracle",
    "generic_llm": "Generic LLM",
    "privacy_first_llm": "Privacy-first LLM",
    "critical_span_guard_extracted": "Critical Span Guard",
}

LOCAL_METHOD_ORDER = [
    "regex_rules",
    "presidio_baseline",
    "direct_span_oracle",
    "privacy_first_oracle",
    "critical_span_guard_oracle",
]

LLM_METHOD_ORDER = [
    "generic_llm",
    "privacy_first_llm",
    "critical_span_guard_extracted",
]

METHOD_CLASS = {
    "regex_rules": "Deployable local baseline",
    "presidio_baseline": "Deployable local baseline",
    "direct_span_oracle": "Gold-informed diagnostic",
    "privacy_first_oracle": "Gold-informed diagnostic",
    "critical_span_guard_oracle": "Gold-informed diagnostic",
    "generic_llm": "Non-oracle LLM baseline",
    "privacy_first_llm": "Non-oracle LLM baseline",
    "critical_span_guard_extracted": "Non-oracle proposed method",
}


def load(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def metric(stats: dict, key: str) -> float:
    value = stats[key]
    if isinstance(value, dict):
        return float(value["mean"])
    return float(value)


def ci(stats: dict, key: str) -> str:
    value = stats[key]
    if not isinstance(value, dict) or "ci95" not in value:
        return ""
    low, high = value["ci95"]
    return f" [{float(low):.3f}, {float(high):.3f}]"


def fmt(value: float) -> str:
    return f"{value:.3f}"


def method_rows(summary: dict, methods: list[str], audited: dict | None = None) -> list[str]:
    lines = [
        "| Method | Comparison role | N | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |",
        "|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for method in methods:
        stats = summary["overall"][method]
        audited_value = "NA"
        if audited is not None and method in audited["overall"]:
            audited_value = fmt(float(audited["overall"][method]["audited_tcfr"]))
        lines.append(
            "| {label} | {role} | {n} | {direct} | {qi} | {tcfr} | {audited} | {qa} |".format(
                label=METHOD_LABELS[method],
                role=METHOD_CLASS[method],
                n=int(stats["n"]),
                direct=fmt(metric(stats, "direct_identifier_leak")),
                qi=fmt(metric(stats, "quasi_identifier_risk")),
                tcfr=fmt(metric(stats, "tcfr")),
                audited=audited_value,
                qa=fmt(metric(stats, "qa_consistency")),
            )
        )
    return lines


def domain_rows(summary: dict, methods: list[str]) -> list[str]:
    lines = [
        "| Domain | Method | Direct leak | QI risk | Exact TCFR | QA |",
        "|---|---|---:|---:|---:|---:|",
    ]
    for domain in ["clinical", "legal"]:
        for method in methods:
            stats = summary["by_domain"][domain][method]
            lines.append(
                "| {domain} | {label} | {direct} | {qi} | {tcfr} | {qa} |".format(
                    domain=domain.capitalize(),
                    label=METHOD_LABELS[method],
                    direct=fmt(metric(stats, "direct_identifier_leak")),
                    qi=fmt(metric(stats, "quasi_identifier_risk")),
                    tcfr=fmt(metric(stats, "tcfr")),
                    qa=fmt(metric(stats, "qa_consistency")),
                )
            )
    return lines


def main() -> None:
    local = load("results/summary.json")
    llm = load("results/openai_summary.json")
    audited = load("results/openai_fact_judge_summary.json")

    lines = ["# Baseline Bridge Report", ""]
    lines.append(
        "This report separates deployable local baselines, gold-informed diagnostics, and the 50-example non-oracle LLM headline run. It is meant to prevent unfair comparisons between oracle rows and deployable systems."
    )
    lines.append("")
    lines.append("## Full 100-Example Local Baselines and Oracles")
    lines.append("")
    lines.extend(method_rows(local, LOCAL_METHOD_ORDER))
    lines.append("")
    lines.append("## Full 100-Example Domain Split")
    lines.append("")
    lines.extend(domain_rows(local, LOCAL_METHOD_ORDER))
    lines.append("")
    lines.append("## 50-Example Non-Oracle LLM Run")
    lines.append("")
    lines.extend(method_rows(llm, LLM_METHOD_ORDER, audited=audited))
    lines.append("")
    lines.append("## Bridge Interpretation")
    lines.append("")
    lines.append(
        "- Regex and direct-span oracle rows show why direct identifier removal is incomplete: they preserve task facts but retain high quasi-identifier risk."
    )
    lines.append(
        "- Presidio is a useful off-the-shelf baseline, but in this setup it misses many legal application identifiers and over-redacts some clinical task facts."
    )
    lines.append(
        "- Privacy-first oracle redaction is the opposite corner of the frontier: it nearly eliminates measured QI risk but removes many facts needed for downstream QA."
    )
    lines.append(
        "- CSG oracle is not deployable because it uses gold annotations, but it shows the target tradeoff is feasible when privacy spans and task facts are separated correctly."
    )
    lines.append(
        "- The non-oracle CSG result is the fair headline method comparison: it uses extracted structures rather than gold spans/facts at inference time."
    )
    lines.append("")
    lines.append("## Paper-Safe Wording")
    lines.append("")
    lines.append(
        "Use the 100-example local table as a diagnostic baseline anchor, not as the main headline. The main deployable-method claim should come from the 50-example non-oracle LLM run, while the oracle rows should be described as upper-bound or frontier diagnostics."
    )
    lines.append("")
    lines.append("## Compact Manuscript Sentence")
    lines.append("")
    lines.append(
        "A 100-example local diagnostic run gives the same qualitative frontier: regex and direct-span replacement preserve TCFR but leave high QI risk, Presidio misses many legal identifiers and loses clinical facts, and privacy-first oracle redaction protects privacy at large utility cost."
    )
    lines.append("")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
