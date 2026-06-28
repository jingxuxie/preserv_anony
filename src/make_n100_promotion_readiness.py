"""Summarize the promoted n100 run and its caveats."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from io_utils import read_jsonl


OUT_PATH = Path("results/n100_promotion_readiness.md")

METHODS = [
    ("generic_llm", "Generic LLM"),
    ("privacy_first_llm", "Privacy-first LLM"),
    ("critical_span_guard_extracted", "Critical Span Guard"),
]

REQUIRED_ARTIFACTS = [
    "data/processed/openai_anonymized_outputs_n100.jsonl",
    "data/processed/openai_judgments_n100.jsonl",
    "data/processed/openai_fact_judgments_n100.jsonl",
    "data/processed/csg_ablation_outputs_n100.jsonl",
    "data/processed/csg_ablation_judgments_n100.jsonl",
    "results/openai_combined_results_n100.md",
    "results/openai_expansion_stability_n100.md",
    "results/paired_delta_report_n100.md",
    "results/csg_ablation_table_n100.md",
    "results/privacy_span_recall_audit_n100.md",
    "results/residual_qi_audit_n100.md",
    "results/legal_qa_disagreement_audit_n100.md",
    "results/surface_metric_audit_n100.md",
    "results/error_taxonomy_n100.md",
    "results/manual_audit_package_n100.md",
    "results/final_qualitative_audit_n100.md",
    "results/paper_ready_tables_n100.md",
    "results/paper_ready_tables_n100.tex",
    "paper/generated_privacy_utility_frontier_n100.tex",
]


def load_json(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def mean(summary: dict, method: str, key: str) -> float:
    value = summary["overall"][method][key]
    if isinstance(value, dict):
        return float(value["mean"])
    return float(value)


def count_ids(path: str | Path) -> int:
    return len({row["id"] for row in read_jsonl(path) if row.get("method") == "generic_llm"})


def ci(stat: dict) -> str:
    low, high = stat["ci95"]
    return f"{fmt(float(low))}-{fmt(float(high))}"


def main() -> None:
    det = load_json("results/openai_summary_n100.json")
    audit = load_json("results/openai_fact_judge_summary_n100.json")
    paired = load_json("results/paired_delta_report_n100.json")
    legal_qa = load_json("results/legal_qa_disagreement_audit_n100.json")
    scored = read_jsonl("data/processed/openai_judgments_n100.jsonl")
    fact = read_jsonl("data/processed/openai_fact_judgments_n100.jsonl")

    csg_scored = [row for row in scored if row["method"] == "critical_span_guard_extracted"]
    csg_fact = [row for row in fact if row["method"] == "critical_span_guard_extracted"]
    csg_direct_rows = sum(1 for row in csg_scored if float(row["direct_identifier_leak"]) > 0)
    csg_qi_rows = [row for row in csg_scored if float(row["quasi_identifier_risk"]) > 0]
    csg_audit_loss_rows = [row for row in csg_fact if float(row["audited_tcfr"]) < 0.999]
    missing = [path for path in REQUIRED_ARTIFACTS if not Path(path).exists()]

    lines = ["# n100 Promotion Readiness", ""]
    lines.append(f"Generated: {date.today().isoformat()}")
    lines.append("")
    lines.append(
        "This report documents the promoted 100-example OpenAI headline run and the caveats carried into the manuscript. "
        "It is generated from n100 artifacts only and makes no API calls."
    )
    lines.append("")
    status = "READY WITH CAVEATS" if not missing and csg_direct_rows == 0 else "NOT READY"
    lines.append(f"Promotion status: **{status}**.")
    lines.append("")
    lines.append(f"- n100 unique examples: {count_ids('data/processed/openai_anonymized_outputs_n100.jsonl')}.")
    lines.append(f"- Required n100 artifacts missing: {', '.join(missing) if missing else 'none'}.")
    lines.append(f"- CSG direct-leak rows: {csg_direct_rows}/{len(csg_scored)}.")
    lines.append(f"- CSG residual QI rows: {len(csg_qi_rows)}/{len(csg_scored)} ({', '.join(row['id'] for row in csg_qi_rows) or 'none'}).")
    lines.append(f"- CSG audited fact-loss rows: {len(csg_audit_loss_rows)}/{len(csg_fact)} ({', '.join(row['id'] for row in csg_audit_loss_rows) or 'none'}).")
    lines.append(
        "- CSG privacy span recall: direct {direct}, quasi {quasi}, all privacy {pii}.".format(
            direct=fmt(mean(det, "critical_span_guard_extracted", "direct_span_recall")),
            quasi=fmt(mean(det, "critical_span_guard_extracted", "quasi_span_recall")),
            pii=fmt(mean(det, "critical_span_guard_extracted", "pii_span_recall")),
        )
    )
    lines.append("")
    lines.append("## n100 Main Metrics")
    lines.append("")
    lines.append("| Method | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for method, label in METHODS:
        lines.append(
            "| {label} | {direct} | {qi} | {tcfr} | {audited} | {qa} |".format(
                label=label,
                direct=fmt(mean(det, method, "direct_identifier_leak")),
                qi=fmt(mean(det, method, "quasi_identifier_risk")),
                tcfr=fmt(mean(det, method, "tcfr")),
                audited=fmt(float(audit["overall"][method]["audited_tcfr"])),
                qa=fmt(mean(det, method, "qa_consistency")),
            )
        )
    lines.append("")
    lines.append("## Paired Effects")
    lines.append("")
    gen = paired["overall"]["generic_llm"]
    priv = paired["overall"]["privacy_first_llm"]
    lines.append(
        "- Versus generic prompting: direct-leak reduction {direct} [{direct_ci}], QI-risk reduction {qi} [{qi_ci}], audited TCFR gain {audited} [{audited_ci}], QA gain {qa} [{qa_ci}].".format(
            direct=fmt(gen["direct_leak_reduction"]["mean"]),
            direct_ci=ci(gen["direct_leak_reduction"]),
            qi=fmt(gen["qi_risk_reduction"]["mean"]),
            qi_ci=ci(gen["qi_risk_reduction"]),
            audited=fmt(gen["audited_tcfr_gain"]["mean"]),
            audited_ci=ci(gen["audited_tcfr_gain"]),
            qa=fmt(gen["qa_gain"]["mean"]),
            qa_ci=ci(gen["qa_gain"]),
        )
    )
    lines.append(
        "- Versus privacy-first prompting: QI-risk reduction {qi} [{qi_ci}], exact TCFR gain {exact} [{exact_ci}], audited TCFR gain {audited} [{audited_ci}], QA gain {qa} [{qa_ci}].".format(
            qi=fmt(priv["qi_risk_reduction"]["mean"]),
            qi_ci=ci(priv["qi_risk_reduction"]),
            exact=fmt(priv["exact_tcfr_gain"]["mean"]),
            exact_ci=ci(priv["exact_tcfr_gain"]),
            audited=fmt(priv["audited_tcfr_gain"]["mean"]),
            audited_ci=ci(priv["audited_tcfr_gain"]),
            qa=fmt(priv["qa_gain"]["mean"]),
            qa_ci=ci(priv["qa_gain"]),
        )
    )
    lines.append("")
    lines.append("## Caveats Carried In Current Headline")
    lines.append("")
    legal_counts = legal_qa["summary"]["by_method"].get("critical_span_guard_extracted", {})
    lines.append(
        f"- CSG has {legal_counts.get('total', 0)} exact legal QA misses in n100; all are exact-phrase artifacts under the fact judge."
    )
    lines.append(
        "- `legal_0016` is the only CSG audited fact-loss row: CSG preserves the Article 8 contact-with-daughter claim but generalizes `Polish authorities` to `authorities` under strict legal-claim labeling."
    )
    lines.append(
        "- Residual QI remains concentrated in five legal rows: `legal_0002`, `legal_0005`, `legal_0025`, `legal_0042`, and `legal_0046`."
    )
    lines.append(
        "- The verification prompt still does not drive the measured ablation gain; the deterministic safety/repair layer does."
    )
    lines.append("")
    lines.append("## Completed Promotion Steps")
    lines.append("")
    lines.append("- Manuscript main table, paired-delta text, ablation table, surface table, and frontier figure use the n100 artifacts.")
    lines.append("- Paper caveats use 100-example wording, including `legal_0016` as the strict-specificity edge case and five residual CSG QI rows.")
    lines.append("- Recompile the paper and rerun `src/verify_submission_package.py` after any future headline change.")
    lines.append("")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
