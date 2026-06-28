"""Verify that the paper-facing package matches the current result artifacts."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from io_utils import read_jsonl


OUT_PATH = Path("results/submission_verification.md")
HEADLINE_SUFFIX = "n150"
HEADLINE_N = 150
HEADLINE_DOMAIN_N = 75
HEADLINE_CACHE_SLOTS = 1200
HEADLINE_USAGE_ROWS = 400
HEADLINE_PROMPT_TOKENS = 249340
HEADLINE_COMPLETION_TOKENS = 103847
HEADLINE_TOTAL_TOKENS = 353187
HEADLINE_RESIDUAL_IDS = {
    "legal_0002",
    "legal_0005",
    "legal_0025",
    "legal_0042",
    "legal_0046",
    "legal_0053",
    "legal_0054",
    "legal_0055",
    "legal_0056",
    "legal_0062",
    "legal_0063",
}
HEADLINE_STRICT_IDS = {"clinical_0055", "clinical_0059", "legal_0016"}
GPT55_FACT_ROWS = 180
GPT55_PRIVACY_ROWS = 60
GPT55_AUDIT_IDS = 60
GPT55_PRIVACY_IDS = 20
GPT55_TOTAL_TOKENS = 278291
GPT55_PROMPT_TOKENS = 160845
GPT55_COMPLETION_TOKENS = 117446
GPT55_REASONING_TOKENS = 44335

METHODS = [
    ("generic_llm", "Generic LLM"),
    ("privacy_first_llm", "Privacy-first LLM"),
    ("critical_span_guard_extracted", "Critical Span Guard"),
]

CRITICAL_LATEX_PATTERNS = [
    r"Citation .* undefined",
    r"Reference .* undefined",
    r"Package natbib Error",
    r"There were undefined citations",
    r"Overfull",
    r"LaTeX Error",
    r"Emergency stop",
]

REQUIRED_PATHS = [
    "paper/main.tex",
    "paper/main.pdf",
    "paper/generated_privacy_utility_frontier.tex",
    "paper/references.bib",
    "results/openai_combined_results.md",
    "results/openai_combined_results_n100.md",
    "results/openai_summary_n100.json",
    "results/openai_fact_judge_summary_n100.json",
    "results/openai_expansion_stability_n100.md",
    "results/n100_promotion_readiness.md",
    "results/paired_delta_report_n100.md",
    "results/csg_ablation_table_n100.md",
    "results/privacy_span_recall_audit_n100.md",
    "results/surface_metric_audit_n100.md",
    "results/legal_qa_disagreement_audit_n100.md",
    "results/surface_failure_scatter_n100.json",
    "results/residual_qi_audit_n100.md",
    "results/error_taxonomy_n100.md",
    "results/manual_audit_package_n100.md",
    "results/final_qualitative_audit_n100.md",
    "results/fixed_sample_manual_audit_n100.md",
    "results/fixed_sample_manual_audit_n100.json",
    "data/processed/second_annotator_packet_n100.jsonl",
    "results/second_annotator_form_n100.csv",
    "results/second_annotator_answer_key_n100.json",
    "results/second_annotator_rubric_n100.md",
    "results/paper_ready_tables_n100.md",
    "results/paper_ready_tables_n100.tex",
    "paper/generated_privacy_utility_frontier_n100.tex",
    "paper/generated_surface_failure_scatter.tex",
    "results/benchmark_quality_audit.md",
    "results/prompt_method_appendix.md",
    "results/paired_delta_report.md",
    "results/csg_ablation_table.md",
    "results/surface_metric_audit.md",
    "results/robustness_report.md",
    "results/residual_qi_audit.md",
    "results/frontier_policy_sensitivity.md",
    "results/threat_model_report.md",
    "results/final_qualitative_audit.md",
    "results/baseline_bridge_report.md",
    "results/artifact_data_statement.md",
    "results/reviewer_risk_register.md",
    "results/cost_and_cache_report_n100.md",
    "results/cost_and_cache_report_n100.json",
    "data/processed/benchmark_n200_local.jsonl",
    "data/processed/anonymized_outputs_n200_local.jsonl",
    "data/processed/judgments_n200_local.jsonl",
    "results/summary_n200_local.json",
    "results/main_results_n200_local.md",
    "results/local_n200_diagnostic_report.md",
    "results/local_n200_diagnostic_report.json",
    "data/processed/benchmark_n120_llm.jsonl",
    "data/processed/openai_anonymized_outputs_n120.jsonl",
    "data/processed/openai_judgments_n120.jsonl",
    "data/processed/openai_fact_judgments_n120.jsonl",
    "results/openai_summary_n120.json",
    "results/openai_fact_judge_summary_n120.json",
    "results/openai_combined_results_n120.md",
    "results/openai_expansion_stability_n120.md",
    "results/openai_api_usage_n120.md",
    "results/openai_api_usage_n120.json",
    "results/openai_expansion_budget_n120_final.json",
    "data/processed/csg_ablation_outputs_n120.jsonl",
    "data/processed/csg_ablation_judgments_n120.jsonl",
    "results/csg_ablation_summary_n120.json",
    "results/csg_ablation_results_n120.md",
    "results/csg_ablation_table_n120.md",
    "results/error_taxonomy_n120.md",
    "results/manual_audit_package_n120.md",
    "results/paired_delta_report_n120.json",
    "results/paired_delta_report_n120.md",
    "results/privacy_span_recall_audit_n120.md",
    "results/surface_metric_audit_n120.json",
    "results/surface_metric_audit_n120.md",
    "results/surface_failure_scatter_n120.json",
    "results/legal_qa_disagreement_audit_n120.json",
    "results/legal_qa_disagreement_audit_n120.md",
    "results/residual_qi_audit_n120.md",
    "results/final_qualitative_audit_n120.md",
    "results/paper_ready_tables_n120.md",
    "results/paper_ready_tables_n120.tex",
    "paper/generated_privacy_utility_frontier_n120.tex",
    "results/fixed_sample_manual_audit_n120.md",
    "results/fixed_sample_manual_audit_n120.json",
    "data/processed/second_annotator_packet_n120.jsonl",
    "results/second_annotator_form_n120.csv",
    "results/second_annotator_answer_key_n120.json",
    "results/second_annotator_rubric_n120.md",
    "data/processed/benchmark_n150_llm.jsonl",
    "data/processed/openai_anonymized_outputs_n150.jsonl",
    "data/processed/openai_judgments_n150.jsonl",
    "data/processed/openai_fact_judgments_n150.jsonl",
    "results/openai_summary_n150.json",
    "results/openai_fact_judge_summary_n150.json",
    "results/openai_combined_results_n150.md",
    "results/openai_expansion_stability_n150.md",
    "results/openai_api_usage_n150.md",
    "results/openai_api_usage_n150.json",
    "results/openai_expansion_budget_n150_final.json",
    "data/processed/csg_ablation_outputs_n150.jsonl",
    "data/processed/csg_ablation_judgments_n150.jsonl",
    "results/csg_ablation_summary_n150.json",
    "results/csg_ablation_results_n150.md",
    "results/csg_ablation_table_n150.md",
    "results/error_taxonomy_n150.md",
    "results/manual_audit_package_n150.md",
    "results/paired_delta_report_n150.json",
    "results/paired_delta_report_n150.md",
    "results/privacy_span_recall_audit_n150.md",
    "results/surface_metric_audit_n150.json",
    "results/surface_metric_audit_n150.md",
    "results/surface_failure_scatter_n150.json",
    "results/legal_qa_disagreement_audit_n150.json",
    "results/legal_qa_disagreement_audit_n150.md",
    "results/residual_qi_audit_n150.md",
    "results/final_qualitative_audit_n150.md",
    "results/paper_ready_tables_n150.md",
    "results/paper_ready_tables_n150.tex",
    "paper/generated_privacy_utility_frontier_n150.tex",
    "paper/generated_surface_failure_scatter_n150.tex",
    "results/fixed_sample_manual_audit_n150.md",
    "results/fixed_sample_manual_audit_n150.json",
    "data/processed/second_annotator_packet_n150.jsonl",
    "results/second_annotator_form_n150.csv",
    "results/second_annotator_answer_key_n150.json",
    "results/second_annotator_rubric_n150.md",
    "results/workshop_plan_compliance_audit.md",
    "results/submission_checklist.md",
    "data/processed/gpt55_audit_ids_60.txt",
    "data/processed/gpt55_audit_subset_stratified60.jsonl",
    "data/processed/gpt55_fact_judgments_stratified60.jsonl",
    "data/processed/gpt55_privacy_ids_hard20.txt",
    "data/processed/gpt55_privacy_judgments_hard20.jsonl",
    "results/gpt55_audit_subset_stratified60.json",
    "results/gpt55_audit_subset_stratified60.md",
    "results/gpt55_fact_judge_summary_stratified60.json",
    "results/gpt55_fact_judge_results_stratified60.md",
    "results/gpt55_privacy_judge_summary_hard20.json",
    "results/gpt55_privacy_judge_results_hard20.md",
    "results/gpt55_external_audit_comparison_stratified60.json",
    "results/gpt55_external_audit_comparison_stratified60.md",
    "results/gpt55_external_audit_comparison_fact60_privacyhard20.json",
    "results/gpt55_external_audit_comparison_fact60_privacyhard20.md",
    "results/gpt55_external_audit_usage_report.json",
    "results/gpt55_external_audit_usage_report.md",
    "data/processed/benchmark.jsonl",
    "data/processed/openai_anonymized_outputs.jsonl",
    "data/processed/openai_anonymized_outputs_n70.jsonl",
    "data/processed/openai_anonymized_outputs_n100.jsonl",
    "data/processed/openai_judgments.jsonl",
    "data/processed/openai_judgments_n70.jsonl",
    "data/processed/openai_judgments_n100.jsonl",
    "data/processed/openai_fact_judgments.jsonl",
    "data/processed/openai_fact_judgments_n70.jsonl",
    "data/processed/openai_fact_judgments_n100.jsonl",
    "data/processed/csg_ablation_outputs_n100.jsonl",
    "data/processed/csg_ablation_judgments_n100.jsonl",
]


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


def load_json(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def read(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8")


def mean(summary: dict, method: str, key: str) -> float:
    value = summary["overall"][method][key]
    if isinstance(value, dict):
        return float(value["mean"])
    return float(value)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def add(checks: list[Check], name: str, passed: bool, detail: str) -> None:
    checks.append(Check(name=name, passed=passed, detail=detail))


def pdf_pages(path: str | Path) -> int | None:
    try:
        result = subprocess.run(
            ["pdfinfo", str(path)],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        log = Path("paper/main.log")
        if not log.exists():
            return None
        match = re.search(r"Output written on main\.pdf \((\d+) pages?", log.read_text(encoding="utf-8"))
        return int(match.group(1)) if match else None
    match = re.search(r"^Pages:\s+(\d+)$", result.stdout, flags=re.MULTILINE)
    return int(match.group(1)) if match else None


def verify_required_paths(checks: list[Check]) -> None:
    missing = [path for path in REQUIRED_PATHS if not Path(path).exists()]
    add(
        checks,
        "Required paper artifacts exist",
        not missing,
        "missing: " + ", ".join(missing) if missing else f"{len(REQUIRED_PATHS)} required artifacts present",
    )


def verify_main_numbers(checks: list[Check]) -> None:
    det = load_json(f"results/openai_summary_{HEADLINE_SUFFIX}.json")
    audit = load_json(f"results/openai_fact_judge_summary_{HEADLINE_SUFFIX}.json")
    paper = read("paper/main.tex")
    combined = read(f"results/openai_combined_results_{HEADLINE_SUFFIX}.md")
    missing: list[str] = []
    for method, label in METHODS:
        values = [
            fmt(mean(det, method, "direct_identifier_leak")),
            fmt(mean(det, method, "quasi_identifier_risk")),
            fmt(mean(det, method, "tcfr")),
            fmt(float(audit["overall"][method]["audited_tcfr"])),
            fmt(mean(det, method, "qa_consistency")),
        ]
        for value in values:
            if value not in paper:
                missing.append(f"paper {label} {value}")
            if value not in combined:
                missing.append(f"combined {label} {value}")
    add(
        checks,
        "Main result numbers match JSON summaries",
        not missing,
        "missing values: " + "; ".join(missing) if missing else f"all {HEADLINE_SUFFIX} main table values found in paper and combined table",
    )


def verify_frontier_figure(checks: list[Check]) -> None:
    det = load_json(f"results/openai_summary_{HEADLINE_SUFFIX}.json")
    audit = load_json(f"results/openai_fact_judge_summary_{HEADLINE_SUFFIX}.json")
    figure = read("paper/generated_privacy_utility_frontier.tex")
    paper = read("paper/main.tex")
    missing: list[str] = []
    for method, _label in METHODS:
        qi = mean(det, method, "quasi_identifier_risk")
        audited = float(audit["overall"][method]["audited_tcfr"])
        coordinate = f"({fmt(qi)},{fmt(audited)})"
        if coordinate not in figure:
            missing.append(f"{method} coordinate {coordinate}")
    for phrase in ["\\label{fig:frontier}", "\\input{generated_privacy_utility_frontier}", "Figure~\\ref{fig:frontier}"]:
        if phrase not in figure and phrase not in paper:
            missing.append(phrase)
    add(
        checks,
        "Privacy-utility figure matches JSON summaries",
        not missing,
        "figure coordinates and manuscript reference are synchronized"
        if not missing
        else "missing figure evidence: " + "; ".join(missing),
    )


def verify_expansion_stability(checks: list[Check]) -> None:
    det = load_json("results/openai_summary_n100.json")
    audit = load_json("results/openai_fact_judge_summary_n100.json")
    report = read("results/openai_expansion_stability_n100.md")
    combined = read("results/openai_combined_results_n100.md")
    outputs_70 = {row["id"] for row in read_jsonl("data/processed/openai_anonymized_outputs_n70.jsonl") if row.get("method") == METHODS[0][0]}
    outputs_100 = {row["id"] for row in read_jsonl("data/processed/openai_anonymized_outputs_n100.jsonl") if row.get("method") == METHODS[0][0]}
    added = outputs_100 - outputs_70
    scored = [
        row
        for row in read_jsonl("data/processed/openai_judgments_n100.jsonl")
        if row.get("method") == "critical_span_guard_extracted" and row.get("id") in added
    ]
    added_direct = sum(1 for row in scored if float(row.get("direct_identifier_leak", 0.0)) > 0)
    added_qi = sum(float(row.get("quasi_identifier_risk", 0.0)) for row in scored)
    missing: list[str] = []
    for method, label in METHODS:
        values = [
            fmt(mean(det, method, "direct_identifier_leak")),
            fmt(mean(det, method, "quasi_identifier_risk")),
            fmt(mean(det, method, "tcfr")),
            fmt(float(audit["overall"][method]["audited_tcfr"])),
            fmt(mean(det, method, "qa_consistency")),
        ]
        for value in values:
            if value not in report or value not in combined:
                missing.append(f"{label} n100 {value}")
    required_text = ["The expansion adds 30 examples", "clinical=15, legal=15", "added-slice audited TCFR"]
    missing.extend(text for text in required_text if text not in report)
    passed = len(outputs_70) == 70 and len(outputs_100) == 100 and len(added) == 30 and added_direct == 0 and not missing
    detail = (
        "n100 stability report matches JSON summaries; added CSG direct rows=0"
        if passed
        else f"ids 70={len(outputs_70)} 100={len(outputs_100)} added={len(added)}; added direct={added_direct}; added qi sum={fmt(added_qi)}"
    )
    if missing:
        detail += "; missing text: " + "; ".join(missing)
    add(checks, "n100 expansion stability check is synchronized", passed, detail)


def verify_n100_readiness(checks: list[Check]) -> None:
    report = read("results/n100_promotion_readiness.md")
    det = load_json("results/openai_summary_n100.json")
    audit = load_json("results/openai_fact_judge_summary_n100.json")
    scored = [row for row in read_jsonl("data/processed/openai_judgments_n100.jsonl") if row.get("method") == "critical_span_guard_extracted"]
    fact = [row for row in read_jsonl("data/processed/openai_fact_judgments_n100.jsonl") if row.get("method") == "critical_span_guard_extracted"]
    direct_rows = sum(1 for row in scored if float(row.get("direct_identifier_leak", 0.0)) > 0)
    qi_rows = sum(1 for row in scored if float(row.get("quasi_identifier_risk", 0.0)) > 0)
    audited_loss_rows = sum(1 for row in fact if float(row.get("audited_tcfr", 0.0)) < 0.999)
    missing: list[str] = []
    for method, label in METHODS:
        values = [
            fmt(mean(det, method, "direct_identifier_leak")),
            fmt(mean(det, method, "quasi_identifier_risk")),
            fmt(mean(det, method, "tcfr")),
            fmt(float(audit["overall"][method]["audited_tcfr"])),
            fmt(mean(det, method, "qa_consistency")),
        ]
        for value in values:
            if value not in report:
                missing.append(f"{label} n100 readiness {value}")
    required_text = ["READY WITH CAVEATS", "legal_0016", "legal_0002", "legal_0005", "legal_0025", "legal_0042", "legal_0046", "Promotion Steps"]
    missing.extend(text for text in required_text if text not in report)
    passed = direct_rows == 0 and qi_rows == 5 and audited_loss_rows == 1 and not missing
    detail = (
        "n100 promotion-readiness report matches row-level caveats"
        if passed
        else f"direct={direct_rows}, qi_rows={qi_rows}, audited_loss_rows={audited_loss_rows}"
    )
    if missing:
        detail += "; missing text: " + "; ".join(missing)
    add(checks, "n100 promotion readiness is auditable", passed, detail)


def verify_baseline_bridge(checks: list[Check]) -> None:
    local = load_json("results/summary_n200_local.json")
    paper = read("paper/main.tex")
    report = read("results/local_n200_diagnostic_report.md")
    required_values = [
        fmt(mean(local, "regex_rules", "quasi_identifier_risk")),
        fmt(mean(local, "direct_span_oracle", "quasi_identifier_risk")),
        fmt(mean(local, "privacy_first_oracle", "tcfr")),
    ]
    paper_only_values = [
        fmt(local["by_domain"]["legal"]["presidio_baseline"]["direct_identifier_leak"]["mean"]),
        fmt(local["by_domain"]["clinical"]["presidio_baseline"]["tcfr"]["mean"]),
    ]
    missing = [value for value in required_values if value not in paper or value not in report]
    missing.extend(value for value in paper_only_values if value not in paper)
    add(
        checks,
        "Baseline bridge values are visible",
        not missing,
        "missing values: " + ", ".join(missing) if missing else "n200 diagnostic baseline values found in paper and diagnostic report",
    )


def verify_surface_metric_audit(checks: list[Check]) -> None:
    surface = load_json(f"results/surface_metric_audit_{HEADLINE_SUFFIX}.json")
    scatter = load_json(f"results/surface_failure_scatter_{HEADLINE_SUFFIX}.json")
    report = read(f"results/surface_metric_audit_{HEADLINE_SUFFIX}.md")
    figure = read("paper/generated_surface_failure_scatter.tex")
    paper = read("paper/main.tex")
    generic = surface["by_method"]["generic_llm"]
    csg = surface["by_method"]["critical_span_guard_extracted"]
    tfidf_high = next(item for item in surface["high_similarity"] if item["metric"] == "tfidf_cosine")
    expected = [
        fmt(float(generic["tfidf_cosine"])),
        fmt(float(csg["tfidf_cosine"])),
        str(tfidf_high["rows_with_privacy_failure"]),
        str(tfidf_high["rows_with_audited_fact_failure"]),
        str(scatter["high_similarity_privacy_failure_rows"]),
        str(scatter["high_similarity_audited_fact_loss_rows"]),
        "TF-IDF cosine",
        "\\input{generated_surface_failure_scatter}",
    ]
    missing = [value for value in expected if value not in report and value not in paper]
    missing.extend(value for value in ["\\label{fig:surface-scatter}", fmt(float(scatter["tfidf_median_threshold"]))] if value not in figure)
    passed = (
        float(generic["tfidf_cosine"]) > float(csg["tfidf_cosine"])
        and tfidf_high["rows_with_privacy_failure"] > 0
        and scatter["high_similarity_rows"] == tfidf_high["n"]
        and scatter["high_similarity_privacy_failure_rows"] == tfidf_high["rows_with_privacy_failure"]
        and scatter["high_similarity_audited_fact_loss_rows"] == tfidf_high["rows_with_audited_fact_failure"]
        and not missing
    )
    add(
        checks,
        "Surface metric audit includes TF-IDF foil",
        passed,
        "TF-IDF cosine and generated surface-failure scatter are synchronized"
        if passed
        else "missing or inconsistent surface evidence: " + "; ".join(missing),
    )


def verify_residual_privacy(checks: list[Check]) -> None:
    scored = read_jsonl(f"data/processed/openai_judgments_{HEADLINE_SUFFIX}.jsonl")
    csg = [row for row in scored if row.get("method") == "critical_span_guard_extracted"]
    direct_rows = sum(1 for row in csg if float(row.get("direct_identifier_leak", 0.0)) > 0)
    qi_rows = sum(1 for row in csg if float(row.get("quasi_identifier_risk", 0.0)) > 0)
    residual = read(f"results/residual_qi_audit_{HEADLINE_SUFFIX}.md")
    expected = [f"Residual rows: {qi_rows}/{len(csg)}", f"Direct identifier leaks: {direct_rows}/{len(csg)}"]
    missing = [item for item in expected if item not in residual]
    add(
        checks,
        "Residual CSG privacy counts match row-level judgments",
        direct_rows == 0 and qi_rows == len(HEADLINE_RESIDUAL_IDS) and len(csg) == HEADLINE_N and not missing,
        f"direct rows={direct_rows}/{len(csg)}, qi rows={qi_rows}/{len(csg)}"
        + ("" if not missing else "; missing text: " + "; ".join(missing)),
    )


def verify_privacy_span_recall(checks: list[Check]) -> None:
    summary = load_json(f"results/openai_summary_{HEADLINE_SUFFIX}.json")
    scored = read_jsonl(f"data/processed/openai_judgments_{HEADLINE_SUFFIX}.jsonl")
    report = read(f"results/privacy_span_recall_audit_{HEADLINE_SUFFIX}.md")
    paper = read("paper/main.tex")
    missing: list[str] = []
    for method, label in METHODS:
        values = [
            fmt(mean(summary, method, "direct_span_recall")),
            fmt(mean(summary, method, "quasi_span_recall")),
            fmt(mean(summary, method, "pii_span_recall")),
        ]
        for value in values:
            if value not in report:
                missing.append(f"{label} span recall {value}")
    csg = [row for row in scored if row.get("method") == "critical_span_guard_extracted"]
    csg_direct_rows = sum(1 for row in csg if row.get("direct_leaked_spans"))
    csg_quasi_rows = sum(1 for row in csg if row.get("quasi_leaked_spans"))
    required_text = [
        "Direct span recall",
        "All privacy span recall",
        "Critical Span Guard | 1.000 | 0.972 | 0.982",
        "all privacy-span recall of 0.982",
    ]
    missing.extend(text for text in required_text if text not in report and text not in paper)
    passed = csg_direct_rows == 0 and csg_quasi_rows == len(HEADLINE_RESIDUAL_IDS) and len(csg) == HEADLINE_N and not missing
    add(
        checks,
        "Privacy span recall audit matches row-level judgments",
        passed,
        f"CSG direct span leaks=0 and quasi-leak rows={len(HEADLINE_RESIDUAL_IDS)}; report values match {HEADLINE_SUFFIX} summary"
        if passed
        else f"CSG direct rows={csg_direct_rows}, quasi rows={csg_quasi_rows}; missing: " + "; ".join(missing),
    )


def verify_page_count(checks: list[Check]) -> None:
    pages = pdf_pages("paper/main.pdf")
    docs = {
        "README.md": read("README.md"),
        "results/submission_checklist.md": read("results/submission_checklist.md"),
        "results/experiment_note.md": read("results/experiment_note.md"),
        "results/paper_claim_package.md": read("results/paper_claim_package.md"),
    }
    if pages is None:
        add(checks, "PDF page count is documented", False, "could not determine page count")
        return
    expected_forms = [f"{pages} pages", f"{pages}-page"]
    missing = [path for path, text in docs.items() if not any(form in text for form in expected_forms)]
    add(
        checks,
        "PDF page count is documented",
        not missing,
        f"paper/main.pdf has {pages} pages" + ("" if not missing else "; stale docs: " + ", ".join(missing)),
    )


def verify_latex_log(checks: list[Check]) -> None:
    log_path = Path("paper/main.log")
    if not log_path.exists():
        add(checks, "LaTeX log has no critical errors", False, "paper/main.log missing")
        return
    log = log_path.read_text(encoding="utf-8")
    hits = []
    for pattern in CRITICAL_LATEX_PATTERNS:
        if re.search(pattern, log):
            hits.append(pattern)
    add(
        checks,
        "LaTeX log has no critical errors",
        not hits,
        "no critical patterns found" if not hits else "matched patterns: " + ", ".join(hits),
    )


def verify_claim_boundaries(checks: list[Check]) -> None:
    risk = read("results/reviewer_risk_register.md")
    checklist = read("results/submission_checklist.md")
    required = [
        "The verifier prompt caused the measured CSG gain. | Unsupported; avoid",
        "The clinical results demonstrate real clinical-note de-identification. | Unsupported; avoid",
        "formal anonymization",
        "Do not report oracle methods as deployable systems",
        "Do not present the local n200 diagnostic as a non-oracle LLM result",
    ]
    missing = [phrase for phrase in required if phrase not in risk and phrase not in checklist]
    add(
        checks,
        "Reviewer-sensitive caveats are present",
        not missing,
        "all required caveats found" if not missing else "missing caveats: " + "; ".join(missing),
    )


def verify_benchmark_quality(checks: list[Check]) -> None:
    quality = read("results/benchmark_quality_audit.md")
    required = [
        "Status: PASS.",
        "Every row has at least one direct identifier",
        "Private span texts are found in the source text",
        "Task facts or their aliases are found in the source text",
        "QA answers or their aliases are found in the source text",
    ]
    missing = [phrase for phrase in required if phrase not in quality]
    add(
        checks,
        "Benchmark quality audit passes",
        not missing,
        "schema and containment checks passed" if not missing else "missing quality evidence: " + "; ".join(missing),
    )


def verify_prompt_appendix(checks: list[Check]) -> None:
    appendix = read("results/prompt_method_appendix.md")
    required = [
        "Status: PASS.",
        "critical_span_guard_extracted` does not use gold `private_spans`",
        "Cache keys are SHA-256 hashes",
        "Deterministic Safety/Repair Layer",
        "Normalized match",
    ]
    missing = [phrase for phrase in required if phrase not in appendix]
    add(
        checks,
        "Prompt appendix drift check passes",
        not missing,
        "prompt files match runner constants and method boundary is documented"
        if not missing
        else "missing prompt evidence: " + "; ".join(missing),
    )


def verify_threat_model(checks: list[Check]) -> None:
    threat = read("results/threat_model_report.md")
    paper = read("paper/main.tex")
    required_report = [
        "Status: PASS.",
        "Motivated adversary with external databases",
        "no k-anonymity, differential privacy, or adversarial re-identification guarantee",
        "CSG residual QI rows: legal_0002, legal_0005, legal_0025, legal_0042, legal_0046, legal_0053, legal_0054, legal_0055, legal_0056, legal_0062, legal_0063",
        "Direct leak rows: 0/150",
    ]
    required_paper = [
        r"\paragraph{Threat model.}",
        "linkage attacks by an adversary with external databases",
        "residual-risk notes",
    ]
    missing = [phrase for phrase in required_report if phrase not in threat]
    missing.extend(phrase for phrase in required_paper if phrase not in paper)
    add(
        checks,
        "Threat model is explicit and bounded",
        not missing,
        "threat model and out-of-scope privacy claims are documented"
        if not missing
        else "missing threat-model evidence: " + "; ".join(missing),
    )


def verify_cost_and_plan_audits(checks: list[Check]) -> None:
    cost = read("results/cost_and_cache_report_n100.md")
    cost_json = load_json("results/cost_and_cache_report_n100.json")
    compliance = read("results/workshop_plan_compliance_audit.md")
    required_cost = [
        "Total required response slots for a cold n100 rebuild: 800",
        "Missing required cache entries for n100 cache-only rebuild: 0",
        "Total prompt token proxy: 512,002; total response token proxy: 199,653; total token proxy: 711,655",
        "Expansion Budget Projection",
        "results/cost_and_cache_report_n100.json",
        "input_price_per_million",
        "Future API calls will persist provider `usage`, `elapsed_ms`",
    ]
    required_compliance = [
        "100-200 example benchmark with clinical and legal splits | PASS",
        "benchmark_n200_local.jsonl",
        "benchmark_n150_llm.jsonl",
        "promoted non-oracle rows",
        "openai_anonymized_outputs_n150.jsonl",
        "promoted n150 non-oracle headline",
        "Manual audit on 20-50 examples or transparent subset audit | PASS",
        "fixed_sample_manual_audit_n150.md",
        "results/openai_api_usage_n150.md",
        "400 n100-to-n150 expansion/cache rows",
        "Cost and latency table | PARTIAL",
        "Highest-Impact Remaining Gaps",
    ]
    missing = [phrase for phrase in required_cost if phrase not in cost]
    missing.extend(phrase for phrase in required_compliance if phrase not in compliance)
    projected_targets = {item.get("target_examples") for item in cost_json.get("expansion_projections", [])}
    cost_json_ok = (
        cost_json.get("required_response_slots") == 800
        and cost_json.get("missing_required_cache_entries") == 0
        and cost_json.get("prompt_tokens_proxy") == 512002
        and cost_json.get("response_tokens_proxy") == 199653
        and cost_json.get("total_tokens_proxy") == 711655
        and {150, 200, 300, 500}.issubset(projected_targets)
    )
    add(
        checks,
        "Plan compliance and cache-cost audits are current",
        not missing and cost_json_ok,
        "cost/cache report includes cache coverage, token-proxy budget, expansion projections, and remaining gaps"
        if not missing and cost_json_ok
        else "missing audit evidence: " + "; ".join(missing) + ("" if cost_json_ok else "; cost JSON values are inconsistent"),
    )


def verify_local_n200_diagnostic(checks: list[Check]) -> None:
    report = read("results/local_n200_diagnostic_report.md")
    diagnostic = load_json("results/local_n200_diagnostic_report.json")
    summary = load_json("results/summary_n200_local.json")
    benchmark = read_jsonl("data/processed/benchmark_n200_local.jsonl")
    outputs = read_jsonl("data/processed/anonymized_outputs_n200_local.jsonl")
    judgments = read_jsonl("data/processed/judgments_n200_local.jsonl")

    required_methods = {
        "regex_rules",
        "presidio_baseline",
        "direct_span_oracle",
        "privacy_first_oracle",
        "critical_span_guard_oracle",
    }
    expected_method_counts = {method: 200 for method in required_methods}
    csg = diagnostic["n200_overall"]["critical_span_guard_oracle"]
    direct_span = diagnostic["n200_overall"]["direct_span_oracle"]
    privacy_first = diagnostic["n200_overall"]["privacy_first_oracle"]
    legal_presidio = diagnostic["n200_by_domain"]["legal"]["presidio_baseline"]
    summary_csg_qi = mean(summary, "critical_span_guard_oracle", "quasi_identifier_risk")
    required_text = [
        "no-API local diagnostic expansion",
        "not a replacement for the promoted n150 non-oracle LLM headline",
        "Do not mix this local/oracle diagnostic",
        "0.225",
        "2.810",
        "0.448",
    ]
    missing = [text for text in required_text if text not in report]
    counts_ok = (
        diagnostic.get("benchmark_rows") == 200
        and diagnostic.get("domain_counts", {}).get("clinical") == 100
        and diagnostic.get("domain_counts", {}).get("legal") == 100
        and diagnostic.get("output_rows") == 1000
        and diagnostic.get("judgment_rows") == 1000
        and diagnostic.get("output_methods") == expected_method_counts
        and diagnostic.get("judgment_methods") == expected_method_counts
        and len(benchmark) == 200
        and len(outputs) == 1000
        and len(judgments) == 1000
    )
    metrics_ok = (
        diagnostic.get("all_directional_checks_pass") is True
        and diagnostic.get("scope") == "No-API local/oracle diagnostic expansion; not the non-oracle LLM headline."
        and set(diagnostic.get("directional_checks", {})) == {
            "direct_span_oracle_high_qi",
            "privacy_first_oracle_utility_loss",
            "csg_oracle_frontier",
            "presidio_legal_direct_leak_failure",
        }
        and all(diagnostic["directional_checks"].values())
        and csg["direct_identifier_leak"] == 0.0
        and csg["tcfr"] >= 0.999
        and csg["qa_consistency"] >= 0.999
        and csg["quasi_identifier_risk"] < direct_span["quasi_identifier_risk"]
        and direct_span["quasi_identifier_risk"] >= 2.5
        and privacy_first["tcfr"] <= 0.5
        and privacy_first["qa_consistency"] <= 0.4
        and legal_presidio["direct_identifier_leak"] >= 0.9
        and abs(summary_csg_qi - csg["quasi_identifier_risk"]) < 1e-9
    )
    add(
        checks,
        "Local n200 diagnostic expansion is bounded and synchronized",
        counts_ok and metrics_ok and not missing,
        "n200 no-API diagnostic has 200 examples, 1000 method rows, stable local/oracle frontier, and explicit n150-headline boundary"
        if counts_ok and metrics_ok and not missing
        else (
            f"counts_ok={counts_ok}, metrics_ok={metrics_ok}"
            + ("" if not missing else "; missing report text: " + "; ".join(missing))
        ),
    )


def verify_openai_headline_expansion(checks: list[Check]) -> None:
    benchmark = read_jsonl(f"data/processed/benchmark_{HEADLINE_SUFFIX}_llm.jsonl")
    outputs = read_jsonl(f"data/processed/openai_anonymized_outputs_{HEADLINE_SUFFIX}.jsonl")
    scored = read_jsonl(f"data/processed/openai_judgments_{HEADLINE_SUFFIX}.jsonl")
    fact = read_jsonl(f"data/processed/openai_fact_judgments_{HEADLINE_SUFFIX}.jsonl")
    det = load_json(f"results/openai_summary_{HEADLINE_SUFFIX}.json")
    audit = load_json(f"results/openai_fact_judge_summary_{HEADLINE_SUFFIX}.json")
    usage = load_json(f"results/openai_api_usage_{HEADLINE_SUFFIX}.json")
    budget = load_json(f"results/openai_expansion_budget_{HEADLINE_SUFFIX}_final.json")
    expansion = read(f"results/openai_expansion_stability_{HEADLINE_SUFFIX}.md")
    combined = read(f"results/openai_combined_results_{HEADLINE_SUFFIX}.md")

    domains = defaultdict(int)
    for row in benchmark:
        domains[row.get("domain", "missing")] += 1
    output_methods = defaultdict(int)
    scored_methods = defaultdict(int)
    fact_methods = defaultdict(int)
    for row in outputs:
        output_methods[row["method"]] += 1
    for row in scored:
        scored_methods[row["method"]] += 1
    for row in fact:
        fact_methods[row["method"]] += 1

    csg = det["overall"]["critical_span_guard_extracted"]
    generic = det["overall"]["generic_llm"]
    privacy_first = det["overall"]["privacy_first_llm"]
    csg_audit = audit["overall"]["critical_span_guard_extracted"]
    added_ids = {f"clinical_{index:04d}" for index in range(60, 75)}
    added_ids.update({f"legal_{index:04d}" for index in range(60, 75)})
    added_csg = [row for row in scored if row["method"] == "critical_span_guard_extracted" and row["id"] in added_ids]
    added_csg_direct = sum(1 for row in added_csg if float(row.get("direct_identifier_leak", 0.0)) > 0)
    added_csg_qi = sum(1 for row in added_csg if float(row.get("quasi_identifier_risk", 0.0)) > 0)
    expected_values = [
        "0.180",
        "1.733",
        "0.938",
        "0.127",
        "0.994",
        "0.974",
        "150-example",
        "The expansion adds 30 examples",
        "0 direct-leak rows and 2 QI-hit rows",
    ]
    missing = [value for value in expected_values if value not in expansion and value not in combined]
    counts_ok = (
        len(benchmark) == HEADLINE_N
        and domains["clinical"] == HEADLINE_DOMAIN_N
        and domains["legal"] == HEADLINE_DOMAIN_N
        and len(outputs) == HEADLINE_N * len(METHODS)
        and len(scored) == HEADLINE_N * len(METHODS)
        and len(fact) == HEADLINE_N * len(METHODS)
        and all(output_methods[method] == HEADLINE_N for method, _label in METHODS)
        and all(scored_methods[method] == HEADLINE_N for method, _label in METHODS)
        and all(fact_methods[method] == HEADLINE_N for method, _label in METHODS)
    )
    metrics_ok = (
        csg["n"] == HEADLINE_N
        and float(csg["direct_identifier_leak"]["mean"]) == 0.0
        and float(csg["quasi_identifier_risk"]["mean"]) <= 0.15
        and float(csg["tcfr"]["mean"]) >= 0.88
        and float(csg["qa_consistency"]["mean"]) >= 0.97
        and float(csg_audit["audited_tcfr"]) >= 0.99
        and float(generic["direct_identifier_leak"]["mean"]) >= 0.15
        and float(generic["quasi_identifier_risk"]["mean"]) >= 1.5
        and float(privacy_first["tcfr"]["mean"]) <= 0.55
        and added_csg_direct == 0
        and added_csg_qi == 2
    )
    usage_ok = (
        usage.get("usage_rows") == HEADLINE_USAGE_ROWS
        and usage.get("prompt_tokens") == HEADLINE_PROMPT_TOKENS
        and usage.get("completion_tokens") == HEADLINE_COMPLETION_TOKENS
        and usage.get("total_tokens") == HEADLINE_TOTAL_TOKENS
        and usage.get("cache_coverage", {}).get("cached_response_slots") == HEADLINE_CACHE_SLOTS
        and usage.get("cache_coverage", {}).get("missing_response_slots") == 0
        and budget.get("total_cached_response_slots") == HEADLINE_CACHE_SLOTS
        and budget.get("total_missing_response_slots") == 0
        and budget.get("cache_rows_with_provider_usage") == HEADLINE_USAGE_ROWS
        and budget.get("cache_rows_with_elapsed_ms") == HEADLINE_USAGE_ROWS
    )
    add(
        checks,
        "OpenAI n150 headline expansion is bounded and cached",
        counts_ok and metrics_ok and usage_ok and not missing,
        f"{HEADLINE_SUFFIX} headline has {HEADLINE_N} examples, stable non-oracle pattern, {HEADLINE_CACHE_SLOTS}/{HEADLINE_CACHE_SLOTS} cached slots, and exact usage for {HEADLINE_USAGE_ROWS} n100-to-n150 cache rows"
        if counts_ok and metrics_ok and usage_ok and not missing
        else (
            f"counts_ok={counts_ok}, metrics_ok={metrics_ok}, usage_ok={usage_ok}, "
            f"added_csg_direct={added_csg_direct}, added_csg_qi={added_csg_qi}"
            + ("" if not missing else "; missing report text: " + "; ".join(missing))
        ),
    )


def verify_headline_full_audit_bundle(checks: list[Check]) -> None:
    residual_ids = HEADLINE_RESIDUAL_IDS
    strict_ids = HEADLINE_STRICT_IDS
    ablation = load_json(f"results/csg_ablation_summary_{HEADLINE_SUFFIX}.json")
    ablation_report = read(f"results/csg_ablation_table_{HEADLINE_SUFFIX}.md")
    residual = read(f"results/residual_qi_audit_{HEADLINE_SUFFIX}.md")
    span = read(f"results/privacy_span_recall_audit_{HEADLINE_SUFFIX}.md")
    paired = load_json(f"results/paired_delta_report_{HEADLINE_SUFFIX}.json")
    paired_report = read(f"results/paired_delta_report_{HEADLINE_SUFFIX}.md")
    fixed = load_json(f"results/fixed_sample_manual_audit_{HEADLINE_SUFFIX}.json")
    packet = read_jsonl(f"data/processed/second_annotator_packet_{HEADLINE_SUFFIX}.jsonl")
    answer_key = load_json(f"results/second_annotator_answer_key_{HEADLINE_SUFFIX}.json")

    final = ablation["overall"]["csg_verified_safety"]
    fixed_meta = fixed.get("metadata", {})
    fixed_summary = fixed.get("summary", {})
    fixed_ids = {row.get("id") for row in fixed.get("examples", [])}
    csg_fixed = defaultdict(int, fixed_summary.get("row_summary_by_method", {}).get("critical_span_guard_extracted", {}))
    packet_ids = {row.get("example_id") for row in packet}

    missing: list[str] = []
    required_text = [
        "Rows with direct leaks |",
        "verify/repair pass did not change",
        "Residual rows: 11/150. Direct identifier leaks: 0/150.",
        "Critical Span Guard | 1.000 | 0.972 | 0.982 | 0/150 | 11/150",
        "QI risk reduction | 1.607",
        "Audited TCFR gain | 0.466",
    ]
    haystacks = [ablation_report, residual, span, paired_report]
    for text in required_text:
        if not any(text in haystack for haystack in haystacks):
            missing.append(text)
    missing.extend(example_id for example_id in sorted(residual_ids | strict_ids) if example_id not in residual + ablation_report + json.dumps(fixed, ensure_ascii=True))

    ablation_ok = (
        int(final["n"]) == HEADLINE_N
        and float(final["direct_identifier_leak"]["mean"]) == 0.0
        and abs(float(final["quasi_identifier_risk"]["mean"]) - 0.12666666666666668) < 1e-9
        and abs(float(final["tcfr"]["mean"]) - 0.8844444444444446) < 1e-9
    )
    paired_ok = (
        abs(float(paired["overall"]["generic_llm"]["qi_risk_reduction"]["mean"]) - 1.6066666666666667) < 1e-9
        and abs(float(paired["overall"]["privacy_first_llm"]["audited_tcfr_gain"]["mean"]) - 0.46555555555555567) < 1e-9
    )
    fixed_ok = (
        fixed_meta.get("examples") == 30
        and fixed_meta.get("method_rows") == 90
        and fixed_meta.get("no_api_calls") is True
        and fixed_summary.get("domain_counts", {}).get("clinical") == 15
        and fixed_summary.get("domain_counts", {}).get("legal") == 15
        and residual_ids.issubset(fixed_ids)
        and strict_ids.issubset(fixed_ids)
        and csg_fixed["direct_leak_rows"] == 0
        and csg_fixed["qi_hit_rows"] == len(HEADLINE_RESIDUAL_IDS)
        and csg_fixed["audited_fact_loss_rows"] == 3
    )
    packet_ok = (
        len(packet) == 90
        and len(packet_ids) == 30
        and packet_ids == fixed_ids
        and answer_key.get("do_not_share_with_annotator") is True
        and set(answer_key.get("examples", {})) == fixed_ids
    )
    passed = ablation_ok and paired_ok and fixed_ok and packet_ok and not missing
    add(
        checks,
        "n150 full audit bundle is promotable with caveats",
        passed,
        "n150 ablation, residual-QI audit, span recall, paired deltas, fixed audit, and blinded packet are synchronized"
        if passed
        else (
            f"ablation_ok={ablation_ok}, paired_ok={paired_ok}, fixed_ok={fixed_ok}, packet_ok={packet_ok}"
            + ("" if not missing else "; missing: " + "; ".join(missing[:10]))
        ),
    )


def verify_gpt55_external_audit(checks: list[Check]) -> None:
    ids = [line.strip() for line in Path("data/processed/gpt55_audit_ids_60.txt").read_text(encoding="utf-8").splitlines() if line.strip()]
    privacy_ids = [
        line.strip()
        for line in Path("data/processed/gpt55_privacy_ids_hard20.txt").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    manifest = read_jsonl("data/processed/gpt55_audit_subset_stratified60.jsonl")
    fact_rows = read_jsonl("data/processed/gpt55_fact_judgments_stratified60.jsonl")
    privacy_rows = read_jsonl("data/processed/gpt55_privacy_judgments_hard20.jsonl")
    fact_summary = load_json("results/gpt55_fact_judge_summary_stratified60.json")
    privacy_summary = load_json("results/gpt55_privacy_judge_summary_hard20.json")
    comparison = load_json("results/gpt55_external_audit_comparison_fact60_privacyhard20.json")
    usage = load_json("results/gpt55_external_audit_usage_report.json")
    paper = read("paper/main.tex")
    claim = read("results/paper_claim_package.md")
    report = read("results/gpt55_external_audit_comparison_fact60_privacyhard20.md")
    usage_report = read("results/gpt55_external_audit_usage_report.md")

    fact_counts: dict[str, int] = defaultdict(int)
    privacy_counts: dict[str, int] = defaultdict(int)
    for row in fact_rows:
        fact_counts[row["method"]] += 1
    for row in privacy_rows:
        privacy_counts[row["method"]] += 1
    manifest_ids = {row["id"] for row in manifest}
    hard_ids = {row["id"] for row in manifest if row.get("bucket") == "hard"}

    counts_ok = (
        len(ids) == GPT55_AUDIT_IDS
        and len(set(ids)) == GPT55_AUDIT_IDS
        and len(manifest) == GPT55_AUDIT_IDS
        and set(ids) == manifest_ids
        and HEADLINE_RESIDUAL_IDS.issubset(manifest_ids)
        and HEADLINE_STRICT_IDS.issubset(manifest_ids)
        and len(privacy_ids) == GPT55_PRIVACY_IDS
        and len(set(privacy_ids)) == GPT55_PRIVACY_IDS
        and set(privacy_ids) == hard_ids
        and len(fact_rows) == GPT55_FACT_ROWS
        and len(privacy_rows) == GPT55_PRIVACY_ROWS
        and all(fact_counts[method] == GPT55_AUDIT_IDS for method, _label in METHODS)
        and all(privacy_counts[method] == GPT55_PRIVACY_IDS for method, _label in METHODS)
    )

    fact = comparison["fact_retention"]["overall"]
    privacy = comparison["privacy"]
    fact_ok = (
        abs(float(fact_summary["overall"]["critical_span_guard_extracted"]["audited_tcfr"]) - 0.9166666666666665) < 1e-9
        and abs(float(fact_summary["overall"]["generic_llm"]["audited_tcfr"]) - 0.8749999999999999) < 1e-9
        and abs(float(fact_summary["overall"]["privacy_first_llm"]["audited_tcfr"]) - 0.4833333333333334) < 1e-9
        and float(fact["critical_span_guard_extracted"]["external_audited_tcfr"]) > float(fact["generic_llm"]["external_audited_tcfr"])
        and float(fact["generic_llm"]["external_audited_tcfr"]) > float(fact["privacy_first_llm"]["external_audited_tcfr"])
        and abs(float(fact["critical_span_guard_extracted"]["fact_label_agreement"]) - 0.9120370370370371) < 1e-9
    )
    privacy_ok = (
        abs(float(privacy_summary["overall"]["critical_span_guard_extracted"]["direct_flag_rate"]) - 0.05) < 1e-9
        and abs(float(privacy_summary["overall"]["generic_llm"]["direct_flag_rate"]) - 0.6) < 1e-9
        and float(privacy_summary["overall"]["privacy_first_llm"]["direct_flag_rate"]) == 0.0
        and abs(float(privacy["critical_span_guard_extracted"]["severe_flag_rate"]) - 0.9) < 1e-9
        and float(privacy["generic_llm"]["severe_flag_rate"]) == 1.0
        and abs(float(privacy["privacy_first_llm"]["severe_flag_rate"]) - 0.7) < 1e-9
    )
    usage_ok = (
        not usage.get("missing_fact_cache_rows")
        and not usage.get("missing_privacy_cache_rows")
        and usage["fact_audit"]["rows"] == GPT55_FACT_ROWS
        and usage["privacy_audit"]["rows"] == GPT55_PRIVACY_ROWS
        and usage["total"]["rows"] == GPT55_FACT_ROWS + GPT55_PRIVACY_ROWS
        and usage["total"]["prompt_tokens"] == GPT55_PROMPT_TOKENS
        and usage["total"]["completion_tokens"] == GPT55_COMPLETION_TOKENS
        and usage["total"]["reasoning_tokens"] == GPT55_REASONING_TOKENS
        and usage["total"]["total_tokens"] == GPT55_TOTAL_TOKENS
    )
    required_text = [
        "0.917",
        "0.875",
        "0.483",
        "0.912",
        "60\\%",
        "5\\%",
        "0\\%",
        "model-assisted evidence, not expert annotation",
        "278,291",
    ]
    haystacks = [paper, claim, report, usage_report]
    missing = [text for text in required_text if not any(text in haystack for haystack in haystacks)]
    passed = counts_ok and fact_ok and privacy_ok and usage_ok and not missing
    add(
        checks,
        "GPT-5.5 external audit bundle is synchronized",
        passed,
        "60-id fact audit, hard20 privacy audit, comparison report, usage report, and manuscript/claim text are synchronized"
        if passed
        else (
            f"counts_ok={counts_ok}, fact_ok={fact_ok}, privacy_ok={privacy_ok}, usage_ok={usage_ok}"
            + ("" if not missing else "; missing: " + "; ".join(missing))
        ),
    )


def verify_fixed_sample_manual_audit(checks: list[Check]) -> None:
    payload = load_json(f"results/fixed_sample_manual_audit_{HEADLINE_SUFFIX}.json")
    report = read(f"results/fixed_sample_manual_audit_{HEADLINE_SUFFIX}.md")
    meta = payload.get("metadata", {})
    summary = payload.get("summary", {})
    examples = payload.get("examples", [])
    ids = {row.get("id") for row in examples}
    domains = summary.get("domain_counts", {})
    csg = defaultdict(int, summary.get("row_summary_by_method", {}).get("critical_span_guard_extracted", {}))
    required_ids = HEADLINE_RESIDUAL_IDS | HEADLINE_STRICT_IDS
    rows_have_three_methods = all(len(row.get("methods", [])) == 3 for row in examples)
    missing: list[str] = []
    expected_text = [
        "Fixed sample: 30 examples (clinical=15, legal=15)",
        "Method rows audited: 90",
        "no new API calls were made",
        "not an independent multi-annotator study",
    ]
    missing.extend(text for text in expected_text if text not in report)
    missing.extend(example_id for example_id in sorted(required_ids) if example_id not in ids or example_id not in report)
    passed = (
        meta.get("examples") == 30
        and meta.get("method_rows") == 90
        and meta.get("no_api_calls") is True
        and domains.get("clinical") == 15
        and domains.get("legal") == 15
        and required_ids.issubset(ids)
        and rows_have_three_methods
        and csg["direct_leak_rows"] == 0
        and csg["qi_hit_rows"] == len(HEADLINE_RESIDUAL_IDS)
        and csg["audited_fact_loss_rows"] == 3
        and not missing
    )
    detail = (
        "fixed 30-example audit covers 90 method rows, all caveat ids, and expected CSG caveat counts"
        if passed
        else (
            f"examples={meta.get('examples')}, rows={meta.get('method_rows')}, domains={domains}, "
            f"csg_direct={csg['direct_leak_rows']}, csg_qi={csg['qi_hit_rows']}, csg_audited_loss={csg['audited_fact_loss_rows']}"
        )
    )
    if missing:
        detail += "; missing audit evidence: " + "; ".join(missing)
    add(checks, "Fixed-sample manual audit covers planned subset", passed, detail)


def verify_second_annotator_packet(checks: list[Check]) -> None:
    packet = read_jsonl(f"data/processed/second_annotator_packet_{HEADLINE_SUFFIX}.jsonl")
    form = read(f"results/second_annotator_form_{HEADLINE_SUFFIX}.csv")
    answer_key = load_json(f"results/second_annotator_answer_key_{HEADLINE_SUFFIX}.json")
    rubric = read(f"results/second_annotator_rubric_{HEADLINE_SUFFIX}.md")
    fixed = load_json(f"results/fixed_sample_manual_audit_{HEADLINE_SUFFIX}.json")
    fixed_ids = {row.get("id") for row in fixed.get("examples", [])}
    packet_ids = {row.get("example_id") for row in packet}
    variants_by_id: dict[str, set[str]] = defaultdict(set)
    forbidden_keys = {"method", "exact_tcfr", "audited_tcfr", "qa_consistency", "labels", "fact_status_counts"}
    forbidden_values = ["generic_llm", "privacy_first_llm", "critical_span_guard_extracted"]
    missing: list[str] = []
    for row in packet:
        variants_by_id[str(row.get("example_id"))].add(str(row.get("variant_code")))
        if forbidden_keys.intersection(row):
            missing.append(f"forbidden packet keys in {row.get('example_id')}:{row.get('variant_code')}")
        row_text = json.dumps(row, ensure_ascii=True)
        if any(value in row_text for value in forbidden_values):
            missing.append(f"method label leaked in packet row {row.get('example_id')}:{row.get('variant_code')}")
    answer_examples = answer_key.get("examples", {})
    answer_key_ok = (
        answer_key.get("do_not_share_with_annotator") is True
        and set(answer_examples) == fixed_ids
        and all(set(mapping) == {"A", "B", "C"} and set(mapping.values()) == {method for method, _label in METHODS} for mapping in answer_examples.values())
    )
    form_lines = [line for line in form.splitlines() if line.strip()]
    rubric_required = [
        "Method names, existing metric scores, fact-judge labels, and prior manual decisions are intentionally excluded",
        "Do not claim inter-rater agreement until this form is completed by a second annotator",
        "direct_identifier_retained",
        "privacy_utility_overlap",
    ]
    missing.extend(text for text in rubric_required if text not in rubric)
    passed = (
        len(packet) == 90
        and len(packet_ids) == 30
        and packet_ids == fixed_ids
        and all(variants == {"A", "B", "C"} for variants in variants_by_id.values())
        and len(form_lines) == 91
        and answer_key_ok
        and not missing
    )
    detail = (
        "blinded second-annotator packet has 30 examples, 90 variant rows, complete answer key, and no method-label leakage"
        if passed
        else (
            f"packet_rows={len(packet)}, examples={len(packet_ids)}, form_lines={len(form_lines)}, "
            f"answer_key_ok={answer_key_ok}; issues: " + "; ".join(missing[:5])
        )
    )
    add(checks, "Second-annotator packet is blinded and complete", passed, detail)


def write_report(checks: list[Check]) -> None:
    passed = sum(1 for check in checks if check.passed)
    lines = ["# Submission Verification", ""]
    lines.append(f"Generated: {date.today().isoformat()}")
    lines.append("")
    lines.append(f"Passed {passed}/{len(checks)} checks.")
    lines.append("")
    lines.append("| Check | Status | Detail |")
    lines.append("|---|---|---|")
    for check in checks:
        status = "PASS" if check.passed else "FAIL"
        lines.append(f"| {check.name} | {status} | {check.detail} |")
    lines.append("")
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    checks: list[Check] = []
    verify_required_paths(checks)
    verify_main_numbers(checks)
    verify_frontier_figure(checks)
    verify_expansion_stability(checks)
    verify_n100_readiness(checks)
    verify_baseline_bridge(checks)
    verify_surface_metric_audit(checks)
    verify_residual_privacy(checks)
    verify_privacy_span_recall(checks)
    verify_page_count(checks)
    verify_latex_log(checks)
    verify_claim_boundaries(checks)
    verify_benchmark_quality(checks)
    verify_prompt_appendix(checks)
    verify_threat_model(checks)
    verify_local_n200_diagnostic(checks)
    verify_openai_headline_expansion(checks)
    verify_headline_full_audit_bundle(checks)
    verify_gpt55_external_audit(checks)
    verify_fixed_sample_manual_audit(checks)
    verify_second_annotator_packet(checks)
    verify_cost_and_plan_audits(checks)
    write_report(checks)
    print(f"wrote {OUT_PATH}")
    failed = [check for check in checks if not check.passed]
    if failed:
        for check in failed:
            print(f"FAIL: {check.name}: {check.detail}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
