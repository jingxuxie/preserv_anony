"""Compute privacy and utility metrics for anonymized outputs."""

from __future__ import annotations

import argparse
import difflib
import math
import random
import re
from collections import defaultdict

from io_utils import read_jsonl, write_json, write_jsonl


def norm(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def contains(text: str, needle: str) -> bool:
    return norm(needle) in norm(text)


def fact_retained(output: str, fact: dict) -> bool:
    aliases = [fact.get("fact", "")]
    aliases.extend(fact.get("answer_aliases", []))
    if fact.get("generalization_allowed"):
        aliases.extend(fact.get("acceptable_generalizations", []))
    return any(alias and contains(output, str(alias)) for alias in aliases)


def fact_contradicted(output: str, fact: dict) -> bool:
    fact_text = norm(str(fact.get("fact", "")))
    out = norm(output)
    if "no violation" in fact_text:
        return "violation" in out and "no violation" not in out
    if fact_text == "violation":
        return "no violation" in out
    if "positive" in fact_text:
        anchor = fact_text.replace("positive", "").strip()
        return bool(anchor and anchor in out and "negative" in out)
    if "negative" in fact_text:
        anchor = fact_text.replace("negative", "").strip()
        return bool(anchor and anchor in out and "positive" in out)
    return False


def qa_consistent(output: str, qa: dict) -> bool:
    aliases = [qa.get("a", "")]
    aliases.extend(qa.get("answer_aliases", []))
    return any(alias and contains(output, str(alias)) for alias in aliases)


def token_edit_rate(original: str, output: str) -> float:
    orig = re.findall(r"\w+|\S", original.lower())
    anon = re.findall(r"\w+|\S", output.lower())
    if not orig:
        return 0.0
    ratio = difflib.SequenceMatcher(a=orig, b=anon).ratio()
    return 1.0 - ratio


def semantic_similarity_proxy(original: str, output: str) -> float:
    orig = set(re.findall(r"[a-zA-Z][a-zA-Z0-9'-]+", original.lower()))
    anon = set(re.findall(r"[a-zA-Z][a-zA-Z0-9'-]+", output.lower()))
    if not orig and not anon:
        return 1.0
    if not orig or not anon:
        return 0.0
    return len(orig & anon) / len(orig | anon)


def qi_risk_score(output: str, spans: list[dict], direct_leaks: int) -> int:
    if direct_leaks:
        return 3
    retained = [
        s
        for s in spans
        if s.get("identifier_type") == "QUASI" and contains(output, str(s.get("text", "")))
    ]
    if not retained:
        return 0
    high_types = {"LOCATION", "LOC", "OCCUPATION", "ORG", "DATETIME", "DATE"}
    high = sum(1 for s in retained if str(s.get("type", "")).upper() in high_types)
    if len(retained) >= 3 or high >= 2:
        return 3
    if len(retained) >= 2 or high == 1:
        return 2
    return 1


def score_row(example: dict, output: dict) -> dict:
    anonymized = output["anonymized_text"]
    direct = [s for s in example["private_spans"] if s.get("identifier_type") == "DIRECT"]
    quasi = [s for s in example["private_spans"] if s.get("identifier_type") == "QUASI"]
    direct_leaked = [s["text"] for s in direct if contains(anonymized, s["text"])]
    quasi_leaked = [s["text"] for s in quasi if contains(anonymized, s["text"])]
    private_leaked = [s["text"] for s in example["private_spans"] if contains(anonymized, s["text"])]

    facts = example.get("task_critical_facts", [])
    preserved = [f for f in facts if fact_retained(anonymized, f)]
    contradicted = [f for f in facts if fact_contradicted(anonymized, f)]
    qas = example.get("qa", [])
    qa_ok = [q for q in qas if qa_consistent(anonymized, q)]

    return {
        "id": example["id"],
        "domain": example["domain"],
        "method": output["method"],
        "direct_identifier_leak": 1 if direct_leaked else 0,
        "direct_span_recall": 1.0 - len(direct_leaked) / len(direct) if direct else 1.0,
        "quasi_span_recall": 1.0 - len(quasi_leaked) / len(quasi) if quasi else 1.0,
        "pii_span_recall": 1.0 - len(private_leaked) / len(example["private_spans"]) if example["private_spans"] else 1.0,
        "quasi_identifier_risk": qi_risk_score(anonymized, example["private_spans"], len(direct_leaked)),
        "tcfr": len(preserved) / len(facts) if facts else math.nan,
        "ccr": len(contradicted) / len(facts) if facts else 0.0,
        "qa_consistency": len(qa_ok) / len(qas) if qas else math.nan,
        "edit_rate": token_edit_rate(example["text"], anonymized),
        "semantic_similarity_proxy": semantic_similarity_proxy(example["text"], anonymized),
        "direct_leaked_spans": direct_leaked,
        "quasi_leaked_spans": quasi_leaked,
        "omitted_facts": [f.get("fact") for f in facts if not fact_retained(anonymized, f)],
        "contradicted_facts": [f.get("fact") for f in contradicted],
        "failed_qa": [q.get("q") for q in qas if not qa_consistent(anonymized, q)],
    }


def mean(rows: list[dict], key: str) -> float:
    vals = [r[key] for r in rows if not math.isnan(r[key])]
    return sum(vals) / len(vals) if vals else math.nan


def bootstrap_ci(rows: list[dict], key: str, seed: int = 7, reps: int = 1000) -> list[float]:
    vals = [r[key] for r in rows if not math.isnan(r[key])]
    if not vals:
        return [math.nan, math.nan]
    if len(vals) == 1:
        return [vals[0], vals[0]]
    rng = random.Random(seed)
    draws = []
    for _ in range(reps):
        sample = [vals[rng.randrange(len(vals))] for _ in vals]
        draws.append(sum(sample) / len(sample))
    draws.sort()
    return [draws[int(0.025 * reps)], draws[int(0.975 * reps)]]


def summarize(scored: list[dict]) -> dict:
    metrics = [
        "direct_identifier_leak",
        "direct_span_recall",
        "quasi_span_recall",
        "pii_span_recall",
        "quasi_identifier_risk",
        "tcfr",
        "ccr",
        "qa_consistency",
        "edit_rate",
        "semantic_similarity_proxy",
    ]
    summary: dict[str, dict] = {"overall": {}, "by_domain": {}}
    by_method: dict[str, list[dict]] = defaultdict(list)
    by_domain_method: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in scored:
        by_method[row["method"]].append(row)
        by_domain_method[(row["domain"], row["method"])].append(row)

    for method, rows in sorted(by_method.items()):
        summary["overall"][method] = summarize_rows(rows, metrics)
    for (domain, method), rows in sorted(by_domain_method.items()):
        summary["by_domain"].setdefault(domain, {})[method] = summarize_rows(rows, metrics)
    return summary


def summarize_rows(rows: list[dict], metrics: list[str]) -> dict:
    out = {"n": len(rows)}
    for metric in metrics:
        out[metric] = {
            "mean": mean(rows, metric),
            "ci95": bootstrap_ci(rows, metric),
        }
    return out


def markdown_table(summary: dict) -> str:
    lines = []
    lines.append("# Quick Experiment Results")
    lines.append("")
    lines.append("Means with bootstrap 95% CIs over examples.")
    lines.append("")
    lines.append(
        "| Method | N | Direct leak ↓ | QI risk ↓ | TCFR ↑ | CCR ↓ | QA consistency ↑ | Edit rate |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for method, stats in sorted(summary["overall"].items()):
        lines.append(
            "| {method} | {n} | {direct} | {qi} | {tcfr} | {ccr} | {qa} | {edit} |".format(
                method=method,
                n=stats["n"],
                direct=fmt(stats["direct_identifier_leak"]),
                qi=fmt(stats["quasi_identifier_risk"]),
                tcfr=fmt(stats["tcfr"]),
                ccr=fmt(stats["ccr"]),
                qa=fmt(stats["qa_consistency"]),
                edit=fmt(stats["edit_rate"]),
            )
        )
    lines.append("")
    for domain, methods in sorted(summary["by_domain"].items()):
        lines.append(f"## {domain.capitalize()}")
        lines.append("")
        lines.append("| Method | N | Direct leak ↓ | QI risk ↓ | TCFR ↑ | QA consistency ↑ |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for method, stats in sorted(methods.items()):
            lines.append(
                "| {method} | {n} | {direct} | {qi} | {tcfr} | {qa} |".format(
                    method=method,
                    n=stats["n"],
                    direct=fmt(stats["direct_identifier_leak"]),
                    qi=fmt(stats["quasi_identifier_risk"]),
                    tcfr=fmt(stats["tcfr"]),
                    qa=fmt(stats["qa_consistency"]),
                )
            )
        lines.append("")
    return "\n".join(lines)


def fmt(metric: dict) -> str:
    mean_value = metric["mean"]
    lo, hi = metric["ci95"]
    if math.isnan(mean_value):
        return "NA"
    return f"{mean_value:.3f} [{lo:.3f}, {hi:.3f}]"


def run(benchmark_path: str, outputs_path: str, scored_path: str, summary_path: str, report_path: str) -> None:
    examples = {row["id"]: row for row in read_jsonl(benchmark_path)}
    outputs = read_jsonl(outputs_path)
    scored = [score_row(examples[row["id"]], row) for row in outputs]
    summary = summarize(scored)
    write_jsonl(scored_path, scored)
    write_json(summary_path, summary)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(markdown_table(summary))
        f.write("\n")
    print(f"wrote scored rows to {scored_path}")
    print(f"wrote summary to {summary_path}")
    print(f"wrote report to {report_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/benchmark.jsonl")
    parser.add_argument("--outputs", default="data/processed/anonymized_outputs.jsonl")
    parser.add_argument("--scored", default="data/processed/judgments.jsonl")
    parser.add_argument("--summary", default="results/summary.json")
    parser.add_argument("--report", default="results/main_results.md")
    args = parser.parse_args()
    run(args.benchmark, args.outputs, args.scored, args.summary, args.report)


if __name__ == "__main__":
    main()
