"""Audit residual CSG quasi-identifier rows after deterministic repair."""

from __future__ import annotations

import argparse
from pathlib import Path
from textwrap import shorten

from io_utils import read_jsonl


METHOD_ORDER = ["generic_llm", "privacy_first_llm", "critical_span_guard_extracted"]


def one_line(items: list[str], limit: int = 180) -> str:
    if not items:
        return "None"
    return shorten("; ".join(str(item) for item in items), width=limit, placeholder=" ...")


def retained_by_judge(judgment: dict, gold_fact: dict | None) -> bool:
    status = judgment.get("status")
    if status == "preserved":
        return True
    if status == "generalized_but_acceptable":
        return bool((gold_fact or {}).get("generalization_allowed"))
    return False


def fact_status_summary(row: dict | None, example: dict | None) -> str:
    if not row:
        return "NA"
    counts: dict[str, int] = {}
    gold_facts = (example or {}).get("task_critical_facts", [])
    for judgment in row.get("fact_judgments", []):
        status = str(judgment.get("status", "missing"))
        if status == "generalized_but_acceptable":
            try:
                gold_fact = gold_facts[int(judgment.get("fact_index"))]
            except (IndexError, TypeError, ValueError):
                gold_fact = None
            status = "generalized_retained" if retained_by_judge(judgment, gold_fact) else "generalized_not_retained"
        counts[status] = counts.get(status, 0) + 1
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts)) or "NA"


def not_retained_facts(row: dict | None, example: dict | None) -> list[str]:
    if not row:
        return []
    gold_facts = (example or {}).get("task_critical_facts", [])
    out = []
    for judgment in row.get("fact_judgments", []):
        try:
            gold_fact = gold_facts[int(judgment.get("fact_index"))]
        except (IndexError, TypeError, ValueError):
            gold_fact = None
        if not retained_by_judge(judgment, gold_fact):
            out.append(str(judgment.get("gold_fact") or judgment.get("fact") or ""))
    return out


def classify(example: dict, csg_score: dict) -> tuple[str, str]:
    facts = " ".join(str(fact.get("fact", "")) for fact in example.get("task_critical_facts", [])).lower()
    hits = [str(hit) for hit in csg_score.get("quasi_leaked_spans", [])]
    hit_text = " ".join(hits).lower()
    if all(hit.lower() in facts for hit in hits):
        return (
            "task-critical overlap",
            "The retained quasi-identifier text is inside the current gold task-critical fact, so removing it would change the annotated answer unless a domain-aware generalization is added.",
        )
    if "dangerous detainee" in hit_text:
        return (
            "annotation/policy gap",
            "The retained detention-regime label is legally meaningful, but the current gold QA only asks for Article/outcome. This should be generalized or explicitly annotated depending on the intended legal task.",
        )
    return (
        "frontier candidate",
        "The retained quasi-identifier appears related to legal claim context; manual review is needed before deciding whether to generalize it.",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/benchmark.jsonl")
    parser.add_argument("--outputs", default="data/processed/openai_anonymized_outputs.jsonl")
    parser.add_argument("--scored", default="data/processed/openai_judgments.jsonl")
    parser.add_argument("--fact-judgments", default="data/processed/openai_fact_judgments.jsonl")
    parser.add_argument("--out", default="results/residual_qi_audit.md")
    args = parser.parse_args()

    benchmark = {row["id"]: row for row in read_jsonl(args.benchmark)}
    outputs = {(row["id"], row["method"]): row for row in read_jsonl(args.outputs)}
    scored = {(row["id"], row["method"]): row for row in read_jsonl(args.scored)}
    facts = {(row["id"], row["method"]): row for row in read_jsonl(args.fact_judgments)}

    csg_rows = [row for row in scored.values() if row["method"] == "critical_span_guard_extracted"]
    residual = [row for row in csg_rows if row.get("quasi_identifier_risk", 0) > 0]
    residual.sort(key=lambda row: (-int(row["quasi_identifier_risk"]), row["id"]))
    direct_leak_rows = sum(1 for row in csg_rows if row.get("direct_identifier_leak", 0) > 0)

    lines = ["# Residual CSG QI Audit", ""]
    lines.append(
        "Manual-style audit of the remaining Critical Span Guard quasi-identifier rows after deterministic safety, legal-Article, medication, case-label, and detention-regime repair."
    )
    lines.append("")
    lines.append(f"Residual rows: {len(residual)}/{len(csg_rows)}. Direct identifier leaks: {direct_leak_rows}/{len(csg_rows)}.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Example | QI risk | QI spans | Audit class | Paper interpretation |")
    lines.append("|---|---:|---|---|---|")
    classifications: dict[str, tuple[str, str]] = {}
    for row in residual:
        example = benchmark[row["id"]]
        label, interpretation = classify(example, row)
        classifications[row["id"]] = (label, interpretation)
        lines.append(
            f"| `{row['id']}` | {row['quasi_identifier_risk']} | {one_line(row.get('quasi_leaked_spans', []), 110)} | {label} | {interpretation} |"
        )
    lines.append("")
    lines.append("## Method Comparison")
    lines.append("")
    lines.append("| Example | Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Fact judge | Not-retained audited facts |")
    lines.append("|---|---|---|---|---:|---:|---:|---|---|")
    for csg_row in residual:
        example_id = csg_row["id"]
        for method in METHOD_ORDER:
            score = scored[(example_id, method)]
            fact = facts.get((example_id, method))
            example = benchmark[example_id]
            audited = "NA" if fact is None else f"{float(fact.get('audited_tcfr', 0.0)):.3f}"
            lines.append(
                "| `{example}` | `{method}` | {direct} | {qi} | {tcfr:.3f} | {audited} | {qa:.3f} | {statuses} | {not_retained} |".format(
                    example=example_id,
                    method=method,
                    direct=one_line(score.get("direct_leaked_spans", []), 80),
                    qi=one_line(score.get("quasi_leaked_spans", []), 100),
                    tcfr=float(score.get("tcfr", 0.0)),
                    audited=audited,
                    qa=float(score.get("qa_consistency", 0.0)),
                    statuses=fact_status_summary(fact, example),
                    not_retained=one_line(not_retained_facts(fact, example), 130),
                )
            )
    lines.append("")
    lines.append("## Row Notes")
    lines.append("")
    for row in residual:
        example = benchmark[row["id"]]
        label, interpretation = classifications[row["id"]]
        lines.append(f"### `{row['id']}` - {label}")
        lines.append("")
        lines.append(f"- Source: `{example.get('source')}`")
        lines.append(f"- CSG QI spans: {one_line(row.get('quasi_leaked_spans', []), 180)}")
        lines.append(f"- Gold task facts: {one_line([fact.get('fact', '') for fact in example.get('task_critical_facts', [])], 260)}")
        lines.append(f"- QA answers: {one_line([qa.get('a', '') for qa in example.get('qa', [])], 220)}")
        lines.append(f"- Audit interpretation: {interpretation}")
        lines.append("")
        lines.append("CSG output:")
        lines.append("")
        lines.append("> " + outputs[(row["id"], "critical_span_guard_extracted")]["anonymized_text"])
        lines.append("")
    lines.append("## Paper Wording")
    lines.append("")
    overlap_ids = [
        example_id
        for example_id, (label, _interpretation) in classifications.items()
        if label == "task-critical overlap"
    ]
    policy_ids = [
        example_id
        for example_id, (label, _interpretation) in classifications.items()
        if label == "annotation/policy gap"
    ]
    if not residual:
        lines.append(
            "Use this as evidence that the current deterministic repair layer removes all measured residual CSG quasi-identifiers on this sample. Do not generalize this to formal anonymization or adversarial privacy guarantees."
        )
    else:
        lines.append(
            f"Use this as evidence that the remaining CSG privacy risk is small and inspectable: {len(residual)} rows retain measured quasi-identifiers after the deterministic repair layer."
        )
        if overlap_ids:
            quoted_ids = ", ".join(f"`{example_id}`" for example_id in overlap_ids)
            lines.append(
                f"The remaining task-critical overlap cases ({quoted_ids}) preserve quasi-identifying text inside the annotated legal claim itself, so removing it would change the current benchmark answer unless a domain-aware generalization is added."
            )
        if policy_ids:
            quoted_ids = ", ".join(f"`{example_id}`" for example_id in policy_ids)
            lines.append(
                f"The policy-gap cases ({quoted_ids}) should be either generalized by policy or promoted to richer task annotations before stronger claims."
            )
        lines.append(
            "Avoid claiming that every residual QI hit is inherently unavoidable. The stronger claim is that task-aware anonymization makes residual cases inspectable and separates true utility-overlap cases from policy gaps."
        )
    lines.append("")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
