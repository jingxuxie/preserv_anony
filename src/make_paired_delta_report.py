"""Compute paired CSG-vs-baseline effect sizes on the cached OpenAI run."""

from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

from io_utils import read_jsonl, write_json


CSG = "critical_span_guard_extracted"
BASELINES = ["generic_llm", "privacy_first_llm"]

METRICS = [
    ("direct_leak_reduction", "Direct leak reduction", "direct_identifier_leak", "baseline_minus_csg"),
    ("qi_risk_reduction", "QI risk reduction", "quasi_identifier_risk", "baseline_minus_csg"),
    ("exact_tcfr_gain", "Exact TCFR gain", "tcfr", "csg_minus_baseline"),
    ("audited_tcfr_gain", "Audited TCFR gain", "audited_tcfr", "csg_minus_baseline"),
    ("qa_gain", "QA gain", "qa_consistency", "csg_minus_baseline"),
]


def bootstrap_ci(values: list[float], seed: int = 13, reps: int = 5000) -> list[float]:
    if not values:
        return [math.nan, math.nan]
    if len(values) == 1:
        return [values[0], values[0]]
    rng = random.Random(seed)
    draws = []
    for _ in range(reps):
        sample = [values[rng.randrange(len(values))] for _ in values]
        draws.append(sum(sample) / len(sample))
    draws.sort()
    return [draws[int(0.025 * reps)], draws[int(0.975 * reps)]]


def sign_test_p(wins: int, losses: int) -> float:
    n = wins + losses
    if n == 0:
        return 1.0
    tail = min(wins, losses)
    prob = sum(math.comb(n, k) for k in range(tail + 1)) / (2**n)
    return min(1.0, 2.0 * prob)


def fmt(value: float) -> str:
    if math.isnan(value):
        return "NA"
    return f"{value:.3f}"


def load_rows(
    deterministic_path: str,
    audited_path: str,
) -> tuple[dict[tuple[str, str], dict], dict[tuple[str, str], dict]]:
    deterministic = {(row["id"], row["method"]): row for row in read_jsonl(deterministic_path)}
    audited = {(row["id"], row["method"]): row for row in read_jsonl(audited_path)}
    return deterministic, audited


def value_for(
    deterministic: dict[tuple[str, str], dict],
    audited: dict[tuple[str, str], dict],
    example_id: str,
    method: str,
    metric_key: str,
) -> float:
    if metric_key == "audited_tcfr":
        return float(audited[(example_id, method)]["audited_tcfr"])
    return float(deterministic[(example_id, method)][metric_key])


def paired_values(
    deterministic: dict[tuple[str, str], dict],
    audited: dict[tuple[str, str], dict],
    baseline: str,
    metric_key: str,
    direction: str,
    domain: str | None,
) -> list[tuple[str, float]]:
    ids = sorted(
        row_id
        for row_id, method in deterministic
        if method == CSG and (domain is None or deterministic[(row_id, method)]["domain"] == domain)
    )
    out = []
    for example_id in ids:
        if (example_id, baseline) not in deterministic:
            continue
        csg_value = value_for(deterministic, audited, example_id, CSG, metric_key)
        baseline_value = value_for(deterministic, audited, example_id, baseline, metric_key)
        if direction == "baseline_minus_csg":
            delta = baseline_value - csg_value
        elif direction == "csg_minus_baseline":
            delta = csg_value - baseline_value
        else:
            raise ValueError(direction)
        out.append((example_id, delta))
    return out


def summarize_delta(values: list[tuple[str, float]]) -> dict:
    deltas = [delta for _, delta in values]
    wins = sum(1 for delta in deltas if delta > 1e-12)
    ties = sum(1 for delta in deltas if abs(delta) <= 1e-12)
    losses = sum(1 for delta in deltas if delta < -1e-12)
    mean = sum(deltas) / len(deltas) if deltas else math.nan
    ci = bootstrap_ci(deltas)
    return {
        "n": len(deltas),
        "mean": mean,
        "ci95": ci,
        "wins": wins,
        "ties": ties,
        "losses": losses,
        "sign_test_p": sign_test_p(wins, losses),
        "deltas": [{"id": example_id, "delta": delta} for example_id, delta in values],
    }


def build_report(deterministic_path: str, audited_path: str) -> dict:
    deterministic, audited = load_rows(deterministic_path, audited_path)
    report: dict[str, dict] = {"overall": {}, "by_domain": {}}
    for baseline in BASELINES:
        report["overall"][baseline] = {}
        for key, _label, metric_key, direction in METRICS:
            values = paired_values(deterministic, audited, baseline, metric_key, direction, domain=None)
            report["overall"][baseline][key] = summarize_delta(values)
    for domain in ["clinical", "legal"]:
        report["by_domain"][domain] = {}
        for baseline in BASELINES:
            report["by_domain"][domain][baseline] = {}
            for key, _label, metric_key, direction in METRICS:
                values = paired_values(deterministic, audited, baseline, metric_key, direction, domain=domain)
                report["by_domain"][domain][baseline][key] = summarize_delta(values)
    return report


def metric_table(report: dict, section: str, domain: str | None = None) -> list[str]:
    lines = [f"## {section}", ""]
    lines.append("| Baseline | Metric | Mean paired advantage | 95% bootstrap CI | Wins / ties / losses | Sign-test p |")
    lines.append("|---|---|---:|---:|---:|---:|")
    source = report["overall"] if domain is None else report["by_domain"][domain]
    for baseline in BASELINES:
        for key, label, _metric_key, _direction in METRICS:
            stats = source[baseline][key]
            lo, hi = stats["ci95"]
            lines.append(
                "| {baseline} | {label} | {mean} | [{lo}, {hi}] | {wins}/{ties}/{losses} | {p:.4f} |".format(
                    baseline=baseline,
                    label=label,
                    mean=fmt(stats["mean"]),
                    lo=fmt(lo),
                    hi=fmt(hi),
                    wins=stats["wins"],
                    ties=stats["ties"],
                    losses=stats["losses"],
                    p=stats["sign_test_p"],
                )
            )
    lines.append("")
    return lines


def write_markdown(report: dict, out_path: str) -> None:
    lines = ["# Paired CSG Advantage Report", ""]
    n = report["overall"]["generic_llm"]["direct_leak_reduction"]["n"]
    lines.append(
        f"Paired deltas compare `critical_span_guard_extracted` against each baseline on the same {n} examples. Positive values always mean CSG is better: lower privacy risk or higher utility."
    )
    lines.append("")
    lines.extend(metric_table(report, "Overall"))
    lines.extend(metric_table(report, "Clinical", domain="clinical"))
    lines.extend(metric_table(report, "Legal", domain="legal"))
    lines.append("## Paper Takeaways")
    lines.append("")
    gen = report["overall"]["generic_llm"]
    priv = report["overall"]["privacy_first_llm"]
    lines.append(
        "- Relative to generic prompting, CSG reduces direct-leak rate by {direct} and QI risk by {qi} on paired examples, while increasing audited TCFR by {audited}.".format(
            direct=fmt(gen["direct_leak_reduction"]["mean"]),
            qi=fmt(gen["qi_risk_reduction"]["mean"]),
            audited=fmt(gen["audited_tcfr_gain"]["mean"]),
        )
    )
    lines.append(
        "- Relative to privacy-first prompting, CSG increases exact TCFR by {exact}, audited TCFR by {audited}, and QA consistency by {qa}; overall QI risk is still lower by {qi_gain}, though legal-only QI risk is slightly higher for CSG because privacy-first over-generalizes legal facts.".format(
            exact=fmt(priv["exact_tcfr_gain"]["mean"]),
            audited=fmt(priv["audited_tcfr_gain"]["mean"]),
            qa=fmt(priv["qa_gain"]["mean"]),
            qi_gain=fmt(priv["qi_risk_reduction"]["mean"]),
        )
    )
    lines.append(
        "- This paired view supports the paper's tradeoff framing: CSG mainly improves privacy over generic prompting and utility over privacy-first prompting."
    )
    lines.append("")
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scored", default="data/processed/openai_judgments.jsonl")
    parser.add_argument("--fact-judgments", default="data/processed/openai_fact_judgments.jsonl")
    parser.add_argument("--out-json", default="results/paired_delta_report.json")
    parser.add_argument("--out-md", default="results/paired_delta_report.md")
    args = parser.parse_args()

    report = build_report(args.scored, args.fact_judgments)
    write_json(args.out_json, report)
    write_markdown(report, args.out_md)
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")


if __name__ == "__main__":
    main()
