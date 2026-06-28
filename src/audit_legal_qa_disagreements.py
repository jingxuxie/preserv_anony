"""Audit legal QA failures against paraphrase-aware fact judgments."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from pathlib import Path
from textwrap import shorten

from io_utils import read_jsonl, write_json


QUESTION_TO_FACT_TYPE = {
    "Which substantive Article was invoked?": "legal_basis",
    "What outcome did the Court state?": "outcome",
    "What core claim was raised?": "claim",
}


METHOD_ORDER = [
    "generic_llm",
    "privacy_first_llm",
    "critical_span_guard_extracted",
]


def clean_text(text: object) -> str:
    return "".join(ch for ch in str(text) if ch in "\n\t" or ord(ch) >= 32)


def retained_by_gold_policy(judgment: dict | None, fact: dict | None) -> bool:
    if not judgment:
        return False
    status = judgment.get("status")
    if status == "preserved":
        return True
    if status == "generalized_but_acceptable":
        return bool((fact or {}).get("generalization_allowed"))
    return False


def related_fact(example: dict, question: str) -> tuple[int | None, dict | None]:
    fact_type = QUESTION_TO_FACT_TYPE.get(question)
    if not fact_type:
        return None, None
    for index, fact in enumerate(example.get("task_critical_facts", [])):
        if fact.get("type") == fact_type:
            return index, fact
    return None, None


def fact_judgment(fact_row: dict | None, fact_index: int | None) -> dict | None:
    if fact_row is None or fact_index is None:
        return None
    for judgment in fact_row.get("fact_judgments", []):
        try:
            if int(judgment.get("fact_index")) == fact_index:
                return judgment
        except (TypeError, ValueError):
            continue
    return None


def classify(question: str, retained: bool) -> str:
    if retained:
        return "exact_phrase_artifact"
    if question == "Which substantive Article was invoked?":
        return "article_specificity_loss"
    return "audited_utility_loss"


def method_sort(method: str) -> tuple[int, str]:
    if method in METHOD_ORDER:
        return (METHOD_ORDER.index(method), method)
    return (99, method)


def build_rows(args: argparse.Namespace) -> list[dict]:
    examples = {row["id"]: row for row in read_jsonl(args.benchmark)}
    outputs = {(row["id"], row["method"]): row for row in read_jsonl(args.outputs)}
    facts = {(row["id"], row["method"]): row for row in read_jsonl(args.fact_judgments)}
    rows = []
    for scored in read_jsonl(args.scored):
        if scored.get("domain") != "legal" or not scored.get("failed_qa"):
            continue
        example = examples[scored["id"]]
        fact_row = facts.get((scored["id"], scored["method"]))
        output = outputs.get((scored["id"], scored["method"]), {})
        qa_by_question = {qa["q"]: qa for qa in example.get("qa", [])}
        for question in scored.get("failed_qa", []):
            fact_index, gold_fact = related_fact(example, question)
            judgment = fact_judgment(fact_row, fact_index)
            retained = retained_by_gold_policy(judgment, gold_fact)
            category = classify(question, retained)
            rows.append(
                {
                    "id": scored["id"],
                    "method": scored["method"],
                    "question": question,
                    "category": category,
                    "audited_related_fact_retained": retained,
                    "fact_type": (gold_fact or {}).get("type"),
                    "gold_answer": qa_by_question.get(question, {}).get("a", ""),
                    "gold_fact": (gold_fact or {}).get("fact", ""),
                    "judge_status": (judgment or {}).get("status", "missing"),
                    "judge_evidence": clean_text((judgment or {}).get("evidence", "")),
                    "qa_consistency": scored.get("qa_consistency"),
                    "audited_tcfr": None if fact_row is None else fact_row.get("audited_tcfr"),
                    "direct_identifier_leak": scored.get("direct_identifier_leak"),
                    "quasi_identifier_risk": scored.get("quasi_identifier_risk"),
                    "anonymized_snippet": shorten(
                        clean_text(output.get("anonymized_text", "")),
                        width=260,
                        placeholder=" ...",
                    ),
                }
            )
    return rows


def summarize(rows: list[dict]) -> dict:
    by_method: dict[str, Counter] = defaultdict(Counter)
    by_question: dict[str, Counter] = defaultdict(Counter)
    for row in rows:
        by_method[row["method"]][row["category"]] += 1
        by_method[row["method"]]["total"] += 1
        by_question[row["question"]][row["category"]] += 1
        by_question[row["question"]]["total"] += 1
    return {
        "n_failed_questions": len(rows),
        "by_method": {method: dict(counts) for method, counts in sorted(by_method.items(), key=lambda item: method_sort(item[0]))},
        "by_question": {question: dict(counts) for question, counts in sorted(by_question.items())},
    }


def markdown(rows: list[dict], summary: dict) -> str:
    lines: list[str] = []
    lines.append("# Legal QA Disagreement Audit")
    lines.append("")
    lines.append(
        "This audit classifies exact legal QA failures using the paraphrase-aware fact judge. "
        "It does not make API calls. Article-number failures are counted as specificity losses when "
        "the related Article fact is not retained, because legal Article numbers are non-generalizable "
        "task-critical facts in this benchmark."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Method | Failed legal QA items | Article specificity loss | Audited utility loss | Exact-phrase artifact |")
    lines.append("|---|---:|---:|---:|---:|")
    for method, counts in summary["by_method"].items():
        lines.append(
            "| {method} | {total} | {article} | {utility} | {artifact} |".format(
                method=method,
                total=counts.get("total", 0),
                article=counts.get("article_specificity_loss", 0),
                utility=counts.get("audited_utility_loss", 0),
                artifact=counts.get("exact_phrase_artifact", 0),
            )
        )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    csg_counts = summary["by_method"].get("critical_span_guard_extracted", {})
    csg_total = csg_counts.get("total", 0)
    csg_artifacts = csg_counts.get("exact_phrase_artifact", 0)
    csg_utility = csg_counts.get("audited_utility_loss", 0)
    csg_articles = csg_counts.get("article_specificity_loss", 0)
    privacy_counts = summary["by_method"].get("privacy_first_llm", {})
    item_word = "item" if csg_total == 1 else "items"
    artifact_word = "is" if csg_artifacts == 1 else "are"
    lines.append(
        f"- CSG has {csg_total} failed legal QA {item_word}; {csg_artifacts} {artifact_word} exact-phrase artifacts, "
        f"{csg_utility} are audited utility losses, and {csg_articles} are Article-specificity losses."
    )
    lines.append(
        "- Most privacy-first legal failures are true utility or Article-specificity losses: the model often replaces Article numbers or concrete claims with generic legal wording. "
        f"In this run, privacy-first has {privacy_counts.get('article_specificity_loss', 0)} Article-specificity losses and {privacy_counts.get('audited_utility_loss', 0)} audited utility losses."
    )
    lines.append(
        "- Generic prompting has fewer QA failures, but some high-overlap outputs still lose legal specificity or leak privacy elsewhere; use this audit alongside the privacy table."
    )
    lines.append("")
    lines.append("## Failed QA Items")
    lines.append("")
    lines.append("| ID | Method | Question | Category | Judge status | Gold answer / fact |")
    lines.append("|---|---|---|---|---|---|")
    for row in sorted(rows, key=lambda r: (method_sort(r["method"]), r["id"], r["question"])):
        answer = row["gold_answer"] or row["gold_fact"]
        lines.append(
            "| {id} | {method} | {question} | {category} | {status} | {answer} |".format(
                id=row["id"],
                method=row["method"],
                question=escape(row["question"]),
                category=row["category"],
                status=escape(str(row["judge_status"])),
                answer=escape(shorten(clean_text(answer), width=190, placeholder=" ...")),
            )
        )
    lines.append("")
    lines.append("## Paper-Useful Cases")
    lines.append("")
    append_case(lines, rows, "legal_0018", "critical_span_guard_extracted")
    append_case(lines, rows, "legal_0023", "privacy_first_llm")
    append_case(lines, rows, "legal_0005", "generic_llm")
    return "\n".join(lines)


def append_case(lines: list[str], rows: list[dict], example_id: str, method: str) -> None:
    selected = [row for row in rows if row["id"] == example_id and row["method"] == method]
    if not selected:
        return
    lines.append(f"### `{example_id}` / `{method}`")
    lines.append("")
    for row in selected:
        lines.append(f"- Category: `{row['category']}`")
        lines.append(f"- Failed question: {row['question']}")
        lines.append(f"- Gold answer: {clean_text(row['gold_answer'])}")
        if row["judge_evidence"]:
            lines.append(f"- Judge evidence: {clean_text(row['judge_evidence'])}")
        lines.append(f"- Output snippet: {clean_text(row['anonymized_snippet'])}")
    lines.append("")


def escape(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def run(args: argparse.Namespace) -> None:
    rows = build_rows(args)
    summary = summarize(rows)
    write_json(args.out_json, {"summary": summary, "rows": rows})
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(markdown(rows, summary) + "\n", encoding="utf-8")
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/benchmark.jsonl")
    parser.add_argument("--outputs", default="data/processed/openai_anonymized_outputs.jsonl")
    parser.add_argument("--scored", default="data/processed/openai_judgments.jsonl")
    parser.add_argument("--fact-judgments", default="data/processed/openai_fact_judgments.jsonl")
    parser.add_argument("--out-json", default="results/legal_qa_disagreement_audit.json")
    parser.add_argument("--out-md", default="results/legal_qa_disagreement_audit.md")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
