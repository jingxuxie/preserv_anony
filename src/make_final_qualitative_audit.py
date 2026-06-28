"""Build the final paper-facing qualitative audit from current cached outputs."""

from __future__ import annotations

import argparse
from pathlib import Path
from textwrap import shorten

from io_utils import read_jsonl


METHODS = ["generic_llm", "privacy_first_llm", "critical_span_guard_extracted"]

CASES = [
    {
        "id": "clinical_0006",
        "role": "Main clinical utility-loss example",
        "manual_decision": (
            "Use in the main qualitative section. Privacy-first anonymization removes named clinical facts "
            "needed for QA, while CSG preserves them after redacting identifiers."
        ),
        "paper_point": "Privacy-first redaction can anonymize away the clinical answer.",
        "use_in_paper": "Foreground as the clearest clinical example.",
    },
    {
        "id": "legal_0006",
        "role": "Main legal privacy-utility example",
        "manual_decision": (
            "Use in the main qualitative section. Generic prompting leaks the application number and date; "
            "privacy-first prompting hides Article 6; CSG removes identifiers and preserves Article 6 plus the claim."
        ),
        "paper_point": "Generic and privacy-first prompts fail in opposite directions on the same legal row.",
        "use_in_paper": "Foreground as the clearest legal example.",
    },
    {
        "id": "legal_0005",
        "role": "Residual frontier example",
        "manual_decision": (
            "Use in limitations or error analysis. CSG preserves the exact Article 6 / section 42 claim, "
            "but the statute name retains Northern Ireland and 1976 as quasi-identifying text."
        ),
        "paper_point": "Some legal statute specificity is both useful and identifying.",
        "use_in_paper": "Use to explain residual privacy-utility overlap.",
    },
    {
        "id": "legal_0025",
        "role": "Second residual frontier example",
        "manual_decision": (
            "Use as secondary evidence for the residual frontier. CSG preserves Article 4 of Protocol No. 7 "
            "and the same-act acquittal claim, but the offence-description phrase remains a measured QI hit."
        ),
        "paper_point": "Offence-description specificity can be required for legal reasoning but still quasi-identifying.",
        "use_in_paper": "Mention briefly when discussing residual CSG QI rows.",
    },
    {
        "id": "legal_0018",
        "role": "Metric nuance example",
        "manual_decision": (
            "Use only for metric discussion. CSG preserves Article 1 / Protocol No. 1 / Article 8 and the home/possessions "
            "claim, but exact matching misses a wording shift."
        ),
        "paper_point": "Exact TCFR is reproducible but conservative for legal paraphrase.",
        "use_in_paper": "Use if space allows for exact-vs-audited TCFR.",
    },
]

N70_EXTRA_CASES = [
    {
        "id": "legal_0016",
        "role": "Expanded-run strict legal specificity edge case",
        "manual_decision": (
            "Use as strict legal-specificity caveat evidence. CSG preserves the Article 8 contact-with-daughter claim, "
            "but generalizes `Polish authorities` to `authorities`; the current strict legal claim treats that jurisdictional specificity as non-generalizable."
        ),
        "paper_point": "Strict legal-claim labels can make jurisdictional generalization count as utility loss.",
        "use_in_paper": "Use only when discussing strict legal specificity.",
    },
]

N100_EXTRA_CASES = N70_EXTRA_CASES + [
    {
        "id": "legal_0002",
        "role": "Residual legal sensitive-claim overlap",
        "manual_decision": (
            "Use only in residual-risk analysis. CSG preserves the sexuality and Article 8 claim, "
            "but the same sexuality terms remain measured quasi-identifiers because they are central to the legal claim."
        ),
        "paper_point": "Sensitive status can be both legally material and identifying.",
        "use_in_paper": "Mention only in the residual QI caveat if space allows.",
    },
    {
        "id": "legal_0042",
        "role": "Residual legal frontier candidate",
        "manual_decision": (
            "Use as a frontier-policy caveat. CSG preserves the Article 14 / Protocol No. 1 / Article 12 claim; "
            "the retained `Rom` span needs policy review before treating it as unavoidable utility overlap."
        ),
        "paper_point": "Not every residual QI hit should be called unavoidable.",
        "use_in_paper": "Use to keep the limitations section honest about policy gaps.",
    },
    {
        "id": "legal_0046",
        "role": "Residual legal benefits-overlap example",
        "manual_decision": (
            "Use only in residual-risk analysis. CSG preserves the widows-benefits claim, but the term `widows` "
            "remains a measured quasi-identifier inside the annotated legal answer."
        ),
        "paper_point": "Legal benefit categories can be task-critical and quasi-identifying.",
        "use_in_paper": "Mention only as part of the five-row residual audit.",
    },
]

N120_EXTRA_CASES = N100_EXTRA_CASES + [
    {
        "id": "legal_0053",
        "role": "Residual legal age-overlap example",
        "manual_decision": (
            "Use only in residual-risk analysis. CSG preserves the Article 8 remedies claim, "
            "but `14 years old` remains as a measured quasi-identifier because it is inside the annotated legal claim."
        ),
        "paper_point": "Age can be legally material and identifying.",
        "use_in_paper": "Mention only as part of the expanded residual QI caveat.",
    },
    {
        "id": "legal_0054",
        "role": "Residual legal frontier candidate",
        "manual_decision": (
            "Use as a frontier-policy caveat. CSG preserves the inheritance-tax claim, "
            "but relationship terms and vote-count detail remain and may be generalizable under a stricter release policy."
        ),
        "paper_point": "Legal context can preserve relational details that may still identify the case.",
        "use_in_paper": "Use if a second expanded residual example is needed.",
    },
    {
        "id": "legal_0055",
        "role": "Residual legal programme-overlap example",
        "manual_decision": (
            "Use only in residual-risk analysis. CSG preserves the access-to-court claim, "
            "but the labour-market-programme phrase remains as a measured quasi-identifier."
        ),
        "paper_point": "Programme details can be both legally relevant and identifying.",
        "use_in_paper": "Mention only as part of the expanded residual QI caveat.",
    },
    {
        "id": "legal_0056",
        "role": "Residual legal jurisdiction/date frontier candidate",
        "manual_decision": (
            "Use as a frontier-policy caveat. CSG preserves the immigration-detention claim, "
            "but nationality and exact dates remain candidates for stricter generalization."
        ),
        "paper_point": "Jurisdiction and timeline specificity may require policy-sensitive generalization.",
        "use_in_paper": "Use if discussing release-policy sensitivity.",
    },
]

N150_EXTRA_CASES = N120_EXTRA_CASES + [
    {
        "id": "clinical_0055",
        "role": "Expanded-run clinical strict utility caveat",
        "manual_decision": (
            "Use only in limitations. CSG removes the age/profession/city quasi-identifiers and keeps the diagnosis "
            "and treatment plan, but the strict audited fact list counts the CT angiography specificity as not fully retained."
        ),
        "paper_point": "Clinical utility scoring can penalize safety-preserving paraphrase of diagnostic evidence.",
        "use_in_paper": "Use only when discussing strict audited utility labels.",
    },
    {
        "id": "clinical_0059",
        "role": "Expanded-run clinical symptom-specificity caveat",
        "manual_decision": (
            "Use only in limitations. CSG removes age/profession/city quasi-identifiers and preserves appendicitis QA, "
            "but the strict audited fact list counts the exact symptom-duration phrase as omitted."
        ),
        "paper_point": "Some clinical utility losses are strict wording/specificity losses rather than answer failures.",
        "use_in_paper": "Use only when discussing strict audited utility labels.",
    },
    {
        "id": "legal_0062",
        "role": "Expanded-run residual nationality frontier case",
        "manual_decision": (
            "Use in residual-risk analysis if n150 is promoted. CSG preserves the Article 2 lethal-force claim, "
            "but the retained nationality term `Irish` remains a measured quasi-identifier."
        ),
        "paper_point": "Nationality may remain when it is embedded in legal procedure context.",
        "use_in_paper": "Mention only as part of the n150 residual QI caveat.",
    },
    {
        "id": "legal_0063",
        "role": "Expanded-run residual benefits-category frontier case",
        "manual_decision": (
            "Use in residual-risk analysis if n150 is promoted. CSG preserves the Article 14 discrimination claim, "
            "but the benefits-category phrase remains a measured quasi-identifier and may need policy-sensitive generalization."
        ),
        "paper_point": "Benefits-category specificity can be legally material and identifying.",
        "use_in_paper": "Mention only as part of the n150 residual QI caveat.",
    },
    {
        "id": "legal_0069",
        "role": "Expanded-run exact-metric artifact",
        "manual_decision": (
            "Use only for metric discussion. CSG has no direct or quasi-identifier hit and the audited judge retains all facts, "
            "but exact QA matching misses a faithful paraphrase of the core claim."
        ),
        "paper_point": "Exact QA is reproducible but conservative for long legal paraphrases.",
        "use_in_paper": "Use only if explaining exact-vs-audited utility.",
    },
]


def clean(text: object) -> str:
    value = str(text)
    value = value.translate({ord(ch): " § " for ch in "\x00\x11\x17\x7f"})
    return "".join(ch for ch in value if ch in "\n\t" or ord(ch) >= 32)


def short(text: object, width: int = 220) -> str:
    return shorten(clean(text).replace("\n", " "), width=width, placeholder=" ...")


def one_line(items: list[object], width: int = 220) -> str:
    if not items:
        return "None"
    return short("; ".join(clean(item) for item in items), width=width)


def retained_by_judge(judgment: dict, gold_fact: dict | None) -> bool:
    status = judgment.get("status")
    if status == "preserved":
        return True
    if status == "generalized_but_acceptable":
        return bool((gold_fact or {}).get("generalization_allowed"))
    return False


def not_retained_by_judge(fact_row: dict | None, example: dict) -> list[str]:
    if not fact_row:
        return []
    gold_facts = example.get("task_critical_facts", [])
    out = []
    for judgment in fact_row.get("fact_judgments", []):
        try:
            gold_fact = gold_facts[int(judgment.get("fact_index"))]
        except (TypeError, ValueError, IndexError):
            gold_fact = None
        if not retained_by_judge(judgment, gold_fact):
            out.append(clean(judgment.get("gold_fact") or judgment.get("fact") or ""))
    return out


def fact_statuses(fact_row: dict | None, example: dict) -> str:
    if not fact_row:
        return "NA"
    gold_facts = example.get("task_critical_facts", [])
    counts: dict[str, int] = {}
    for judgment in fact_row.get("fact_judgments", []):
        status = str(judgment.get("status", "missing"))
        if status == "generalized_but_acceptable":
            try:
                gold_fact = gold_facts[int(judgment.get("fact_index"))]
            except (TypeError, ValueError, IndexError):
                gold_fact = None
            status = "generalized_retained" if retained_by_judge(judgment, gold_fact) else "generalized_not_retained"
        counts[status] = counts.get(status, 0) + 1
    return ", ".join(f"{key}={counts[key]}" for key in sorted(counts)) or "NA"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/benchmark.jsonl")
    parser.add_argument("--outputs", default="data/processed/openai_anonymized_outputs.jsonl")
    parser.add_argument("--scored", default="data/processed/openai_judgments.jsonl")
    parser.add_argument("--fact-judgments", default="data/processed/openai_fact_judgments.jsonl")
    parser.add_argument("--out", default="results/final_qualitative_audit.md")
    parser.add_argument("--case-set", choices=["main", "n70", "n100", "n120", "n150"], default="main")
    args = parser.parse_args()

    benchmark = {row["id"]: row for row in read_jsonl(args.benchmark)}
    outputs = {(row["id"], row["method"]): row for row in read_jsonl(args.outputs)}
    scored = {(row["id"], row["method"]): row for row in read_jsonl(args.scored)}
    judged = {(row["id"], row["method"]): row for row in read_jsonl(args.fact_judgments)}
    if args.case_set == "n150":
        cases = CASES + N150_EXTRA_CASES
    elif args.case_set == "n120":
        cases = CASES + N120_EXTRA_CASES
    elif args.case_set == "n100":
        cases = CASES + N100_EXTRA_CASES
    elif args.case_set == "n70":
        cases = CASES + N70_EXTRA_CASES
    else:
        cases = CASES

    lines = ["# Final Qualitative Audit", ""]
    sample_labels = {
        "main": "50-example OpenAI run",
        "n70": "70-example n70 stability run",
        "n100": "100-example n100 promoted run",
        "n120": "120-example promoted run",
        "n150": "150-example expansion run",
    }
    sample_label = sample_labels[args.case_set]
    lines.append(
        f"Paper-facing manual spot-check of the foreground examples and residual frontier cases from the current {sample_label}."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append("| Example | Role | Paper point | Paper use |")
    lines.append("|---|---|---|---|")
    for case in cases:
        lines.append(
            f"| `{case['id']}` | {case['role']} | {case['paper_point']} | {case['use_in_paper']} |"
        )
    lines.append("")
    lines.append("## Audit Details")
    lines.append("")

    for case in cases:
        example = benchmark[case["id"]]
        facts = [fact.get("fact", "") for fact in example.get("task_critical_facts", [])]
        qas = [f"{qa.get('q')} -> {qa.get('a')}" for qa in example.get("qa", [])]
        direct = [span.get("text", "") for span in example.get("private_spans", []) if span.get("identifier_type") == "DIRECT"]
        quasi = [span.get("text", "") for span in example.get("private_spans", []) if span.get("identifier_type") == "QUASI"]

        lines.append(f"### `{case['id']}` - {case['role']}")
        lines.append("")
        lines.append(f"- Domain/source: `{example.get('domain')}` / `{example.get('source')}`")
        lines.append(f"- Manual decision: {case['manual_decision']}")
        lines.append(f"- Gold task facts: {one_line(facts, width=320)}")
        lines.append(f"- Gold QA: {one_line(qas, width=280)}")
        lines.append(f"- Gold direct identifiers: {one_line(direct, width=220)}")
        lines.append(f"- Gold quasi-identifiers: {one_line(quasi, width=220)}")
        lines.append("")
        lines.append("| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |")
        lines.append("|---|---|---|---:|---:|---:|---|")
        for method in METHODS:
            score = scored[(case["id"], method)]
            fact_row = judged.get((case["id"], method))
            audited_tcfr = "NA" if fact_row is None else f"{float(fact_row.get('audited_tcfr', 0.0)):.3f}"
            lines.append(
                "| {method} | {direct_leaks} | {qi_hits} | {tcfr:.3f} | {audited_tcfr} | {qa:.3f} | {not_retained} |".format(
                    method=method,
                    direct_leaks=one_line(score.get("direct_leaked_spans", []), width=100),
                    qi_hits=one_line(score.get("quasi_leaked_spans", []), width=120),
                    tcfr=float(score.get("tcfr", 0.0)),
                    audited_tcfr=audited_tcfr,
                    qa=float(score.get("qa_consistency", 0.0)),
                    not_retained=one_line(not_retained_by_judge(fact_row, example), width=220),
                )
            )
        lines.append("")
        lines.append("Output snippets:")
        lines.append("")
        for method in METHODS:
            output = outputs[(case["id"], method)]["anonymized_text"]
            fact_row = judged.get((case["id"], method))
            lines.append(f"- `{method}` ({fact_statuses(fact_row, example)}): {short(output, width=430)}")
        lines.append("")

    lines.append("## Paper-Safe Wording")
    lines.append("")
    lines.append("- Use `clinical_0006`, `legal_0006`, and `legal_0005` as the compact qualitative set in the main paper.")
    lines.append("- Use `legal_0025` only if the residual privacy frontier needs a second legal example.")
    lines.append("- Use `legal_0018` only to explain exact TCFR undercounting faithful legal paraphrase.")
    residual_counts = {"n100": 5, "n120": 9, "n150": 11}
    if args.case_set in residual_counts:
        lines.append(
            f"- Do not claim CSG solves legal anonymization; {residual_counts[args.case_set]} residual rows retain quasi-identifying legal-claim text or frontier legal context."
        )
        lines.append("- Carry `legal_0016` as a strict legal-specificity utility caveat, separate from the residual QI rows.")
        if args.case_set == "n150":
            lines.append("- Carry `clinical_0055` and `clinical_0059` as strict clinical utility caveats, separate from the residual QI rows.")
    else:
        lines.append("- Do not claim CSG solves legal anonymization; residual rows retain quasi-identifying legal-claim text.")
    lines.append("- Do not claim the verifier improved this run; the ablation attributes measured gains to deterministic safety/repair.")
    lines.append("")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
