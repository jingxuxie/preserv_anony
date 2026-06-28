"""Generate a paper-facing artifact and data statement."""

from __future__ import annotations

from collections import Counter
from datetime import date
from pathlib import Path

from io_utils import read_jsonl


BENCHMARK_PATH = Path("data/processed/benchmark.jsonl")
ROBUSTNESS_PATH = Path("data/processed/robustness_benchmark.jsonl")
OPENAI_OUTPUTS_PATH = Path("data/processed/openai_anonymized_outputs.jsonl")
OPENAI_JUDGMENTS_PATH = Path("data/processed/openai_judgments.jsonl")
OPENAI_FACT_JUDGMENTS_PATH = Path("data/processed/openai_fact_judgments.jsonl")
OPENAI_OUTPUTS_N70_PATH = Path("data/processed/openai_anonymized_outputs_n70.jsonl")
OPENAI_JUDGMENTS_N70_PATH = Path("data/processed/openai_judgments_n70.jsonl")
OPENAI_FACT_JUDGMENTS_N70_PATH = Path("data/processed/openai_fact_judgments_n70.jsonl")
OPENAI_OUTPUTS_N100_PATH = Path("data/processed/openai_anonymized_outputs_n100.jsonl")
OPENAI_JUDGMENTS_N100_PATH = Path("data/processed/openai_judgments_n100.jsonl")
OPENAI_FACT_JUDGMENTS_N100_PATH = Path("data/processed/openai_fact_judgments_n100.jsonl")
OPENAI_CACHE_PATH = Path("data/processed/openai_cache.jsonl")
LOCAL_N200_BENCHMARK_PATH = Path("data/processed/benchmark_n200_local.jsonl")
LOCAL_N200_OUTPUTS_PATH = Path("data/processed/anonymized_outputs_n200_local.jsonl")
LOCAL_N200_JUDGMENTS_PATH = Path("data/processed/judgments_n200_local.jsonl")
OPENAI_N120_BENCHMARK_PATH = Path("data/processed/benchmark_n120_llm.jsonl")
OPENAI_OUTPUTS_N120_PATH = Path("data/processed/openai_anonymized_outputs_n120.jsonl")
OPENAI_JUDGMENTS_N120_PATH = Path("data/processed/openai_judgments_n120.jsonl")
OPENAI_FACT_JUDGMENTS_N120_PATH = Path("data/processed/openai_fact_judgments_n120.jsonl")
OPENAI_N150_BENCHMARK_PATH = Path("data/processed/benchmark_n150_llm.jsonl")
OPENAI_OUTPUTS_N150_PATH = Path("data/processed/openai_anonymized_outputs_n150.jsonl")
OPENAI_JUDGMENTS_N150_PATH = Path("data/processed/openai_judgments_n150.jsonl")
OPENAI_FACT_JUDGMENTS_N150_PATH = Path("data/processed/openai_fact_judgments_n150.jsonl")
TAB_RAW_PATH = Path("data/raw/text-anonymisation-benchmark")
OUT_PATH = Path("results/artifact_data_statement.md")


METHOD_LABELS = {
    "generic_llm": "Generic LLM",
    "privacy_first_llm": "Privacy-first LLM",
    "critical_span_guard_extracted": "Critical Span Guard",
}

METHOD_ORDER = [
    "generic_llm",
    "privacy_first_llm",
    "critical_span_guard_extracted",
]


def count_by(rows: list[dict], key: str) -> Counter[str]:
    return Counter(str(row.get(key, "missing")) for row in rows)


def source_family(source: object) -> str:
    value = str(source)
    if value == "synthetic_template":
        return "synthetic clinical templates"
    if value.startswith("TAB:"):
        parts = value.split(":")
        split = parts[1] if len(parts) > 1 else "unknown"
        return f"TAB ECHR {split} split"
    if value.startswith("stress_"):
        return "handwritten stress slice"
    return value or "missing"


def span_counts(rows: list[dict]) -> tuple[int, int]:
    direct = 0
    quasi = 0
    for row in rows:
        for span in row.get("private_spans", []):
            identifier_type = span.get("identifier_type")
            if identifier_type == "DIRECT":
                direct += 1
            elif identifier_type == "QUASI":
                quasi += 1
    return direct, quasi


def average_count(rows: list[dict], key: str) -> float:
    if not rows:
        return 0.0
    return sum(len(row.get(key, [])) for row in rows) / len(rows)


def method_table(outputs: list[dict], judgments: list[dict], fact_judgments: list[dict]) -> list[str]:
    output_counts = count_by(outputs, "method")
    judgment_counts = count_by(judgments, "method")
    fact_counts = count_by(fact_judgments, "method")
    models_by_method: dict[str, Counter[str]] = {}
    for row in outputs:
        models_by_method.setdefault(str(row.get("method", "missing")), Counter())[str(row.get("model", "missing"))] += 1

    lines = [
        "| Method | Output rows | Deterministic judgment rows | Fact-judge rows | Model(s) |",
        "|---|---:|---:|---:|---|",
    ]
    ordered_methods = [method for method in METHOD_ORDER if method in output_counts]
    ordered_methods.extend(method for method in sorted(output_counts) if method not in set(ordered_methods))
    for method in ordered_methods:
        model_counts = models_by_method.get(method, Counter())
        models = ", ".join(f"{model} ({count})" for model, count in sorted(model_counts.items()))
        lines.append(
            "| {method} | {outputs} | {judgments} | {facts} | {models} |".format(
                method=METHOD_LABELS.get(method, method),
                outputs=output_counts[method],
                judgments=judgment_counts.get(method, 0),
                facts=fact_counts.get(method, 0),
                models=models or "missing",
            )
        )
    return lines


def count_rows(path: Path) -> int:
    if not path.exists():
        return 0
    return len(read_jsonl(path))


def yes_no(value: bool) -> str:
    return "yes" if value else "no"


def main() -> None:
    benchmark = read_jsonl(BENCHMARK_PATH)
    robustness = read_jsonl(ROBUSTNESS_PATH)
    local_n200 = read_jsonl(LOCAL_N200_BENCHMARK_PATH)
    openai_n150 = read_jsonl(OPENAI_N150_BENCHMARK_PATH)
    outputs = read_jsonl(OPENAI_OUTPUTS_N150_PATH)
    judgments = read_jsonl(OPENAI_JUDGMENTS_N150_PATH)
    fact_judgments = read_jsonl(OPENAI_FACT_JUDGMENTS_N150_PATH)
    cache_rows = count_rows(OPENAI_CACHE_PATH)

    benchmark_domains = count_by(benchmark, "domain")
    benchmark_sources = Counter(source_family(row.get("source")) for row in benchmark)
    robustness_domains = count_by(robustness, "domain")
    local_n200_domains = count_by(local_n200, "domain")
    local_n200_sources = Counter(source_family(row.get("source")) for row in local_n200)
    openai_n150_domains = count_by(openai_n150, "domain")
    openai_n150_sources = Counter(source_family(row.get("source")) for row in openai_n150)
    direct_spans, quasi_spans = span_counts(benchmark)
    robustness_direct_spans, robustness_quasi_spans = span_counts(robustness)
    local_n200_direct_spans, local_n200_quasi_spans = span_counts(local_n200)
    openai_n150_direct_spans, openai_n150_quasi_spans = span_counts(openai_n150)

    lines = ["# Artifact and Data Statement", ""]
    lines.append(f"Generated: {date.today().isoformat()}")
    lines.append("")
    lines.append(
        "This statement summarizes the current data provenance, cached model artifacts, and release caveats for the utility-preserving anonymization workshop package."
    )
    lines.append("")
    lines.append("## Data Inventory")
    lines.append("")
    lines.append("| Split | Rows | Domains | Sources | Direct spans | Quasi spans | Avg task facts | Avg QA pairs |")
    lines.append("|---|---:|---|---|---:|---:|---:|---:|")
    lines.append(
        "| Main benchmark | {rows} | {domains} | {sources} | {direct} | {quasi} | {facts:.2f} | {qa:.2f} |".format(
            rows=len(benchmark),
            domains=", ".join(f"{key}={value}" for key, value in sorted(benchmark_domains.items())),
            sources=", ".join(f"{key}={value}" for key, value in sorted(benchmark_sources.items())),
            direct=direct_spans,
            quasi=quasi_spans,
            facts=average_count(benchmark, "task_critical_facts"),
            qa=average_count(benchmark, "qa"),
        )
    )
    lines.append(
        "| Robustness stress slice | {rows} | {domains} | handwritten diagnostics | {direct} | {quasi} | {facts:.2f} | {qa:.2f} |".format(
            rows=len(robustness),
            domains=", ".join(f"{key}={value}" for key, value in sorted(robustness_domains.items())),
            direct=robustness_direct_spans,
            quasi=robustness_quasi_spans,
            facts=average_count(robustness, "task_critical_facts"),
            qa=average_count(robustness, "qa"),
        )
    )
    lines.append(
        "| Local n200 diagnostic benchmark | {rows} | {domains} | {sources} | {direct} | {quasi} | {facts:.2f} | {qa:.2f} |".format(
            rows=len(local_n200),
            domains=", ".join(f"{key}={value}" for key, value in sorted(local_n200_domains.items())),
            sources=", ".join(f"{key}={value}" for key, value in sorted(local_n200_sources.items())),
            direct=local_n200_direct_spans,
            quasi=local_n200_quasi_spans,
            facts=average_count(local_n200, "task_critical_facts"),
            qa=average_count(local_n200, "qa"),
        )
    )
    lines.append(
        "| OpenAI n150 promoted benchmark | {rows} | {domains} | {sources} | {direct} | {quasi} | {facts:.2f} | {qa:.2f} |".format(
            rows=len(openai_n150),
            domains=", ".join(f"{key}={value}" for key, value in sorted(openai_n150_domains.items())),
            sources=", ".join(f"{key}={value}" for key, value in sorted(openai_n150_sources.items())),
            direct=openai_n150_direct_spans,
            quasi=openai_n150_quasi_spans,
            facts=average_count(openai_n150, "task_critical_facts"),
            qa=average_count(openai_n150, "qa"),
        )
    )
    lines.append("")
    lines.append("## Provenance")
    lines.append("")
    lines.append(
        "- Clinical examples are synthetic vignettes generated from local templates. They are designed to contain controlled direct identifiers, quasi-identifiers, task-critical clinical facts, and QA targets; they are not real clinical notes and should not be described as real PHI."
    )
    lines.append(
        "- Legal examples are public ECHR snippets sampled from the Text Anonymization Benchmark clone at `data/raw/text-anonymisation-benchmark`. The local raw clone is present: `{present}`; license file present: `{license_present}`.".format(
            present=yes_no(TAB_RAW_PATH.exists()),
            license_present=yes_no((TAB_RAW_PATH / "LICENSE.txt").exists()),
        )
    )
    lines.append(
        "- The robustness slice is handwritten and diagnostic. It intentionally includes cases where sensitive or quasi-identifying content is also downstream-task-critical."
    )
    lines.append("")
    lines.append("## Cached Model Artifacts")
    lines.append("")
    lines.extend(method_table(outputs, judgments, fact_judgments))
    lines.append("")
    lines.append(
        "- Promoted 150-example headline run: {outputs} output rows, {judgments} deterministic judgment rows, and {facts} fact-judge rows.".format(
            outputs=count_rows(OPENAI_OUTPUTS_N150_PATH),
            judgments=count_rows(OPENAI_JUDGMENTS_N150_PATH),
            facts=count_rows(OPENAI_FACT_JUDGMENTS_N150_PATH),
        )
    )
    lines.append(
        "- Earlier 100-example run retained for audit trail: {outputs} output rows, {judgments} deterministic judgment rows, and {facts} fact-judge rows.".format(
            outputs=count_rows(OPENAI_OUTPUTS_N100_PATH),
            judgments=count_rows(OPENAI_JUDGMENTS_N100_PATH),
            facts=count_rows(OPENAI_FACT_JUDGMENTS_N100_PATH),
        )
    )
    lines.append(
        "- Earlier 70-example run retained for audit trail: {outputs} output rows, {judgments} deterministic judgment rows, and {facts} fact-judge rows.".format(
            outputs=count_rows(OPENAI_OUTPUTS_N70_PATH),
            judgments=count_rows(OPENAI_JUDGMENTS_N70_PATH),
            facts=count_rows(OPENAI_FACT_JUDGMENTS_N70_PATH),
        )
    )
    lines.append(
        "- Earlier 50-example run retained for audit trail: {outputs} output rows, {judgments} deterministic judgment rows, and {facts} fact-judge rows.".format(
            outputs=count_rows(OPENAI_OUTPUTS_PATH),
            judgments=count_rows(OPENAI_JUDGMENTS_PATH),
            facts=count_rows(OPENAI_FACT_JUDGMENTS_PATH),
        )
    )
    lines.append(f"- OpenAI cache rows: {cache_rows} in `{OPENAI_CACHE_PATH}`.")
    lines.append(
        "- The current promoted 150-example non-oracle LLM run uses `gpt-4.1-nano` and three methods: generic prompting, privacy-first prompting, and Critical Span Guard with extracted privacy/fact structures."
    )
    lines.append(
        "- Separate no-API local n200 diagnostic: {benchmark} benchmark rows, {outputs} deterministic local/oracle output rows, and {judgments} deterministic judgment rows. It is not the promoted non-oracle LLM headline.".format(
            benchmark=count_rows(LOCAL_N200_BENCHMARK_PATH),
            outputs=count_rows(LOCAL_N200_OUTPUTS_PATH),
            judgments=count_rows(LOCAL_N200_JUDGMENTS_PATH),
        )
    )
    lines.append(
        "- Bounded OpenAI n150 expansion usage: {outputs} output rows, {judgments} deterministic judgment rows, and {facts} fact-judge rows. The n100-to-n150 provider/cache rows with exact usage and latency are in `results/openai_api_usage_n150.md`.".format(
            outputs=count_rows(OPENAI_OUTPUTS_N150_PATH),
            judgments=count_rows(OPENAI_JUDGMENTS_N150_PATH),
            facts=count_rows(OPENAI_FACT_JUDGMENTS_N150_PATH),
        )
    )
    lines.append(
        "- Current OpenAI outputs can be rebuilt from cache without new API calls with `conda run -n preserv_anony python src/run_openai_methods.py --benchmark data/processed/benchmark_n150_llm.jsonl --model gpt-4.1-nano --max-examples 150 --seed 21 --methods generic_llm privacy_first_llm critical_span_guard_extracted --out data/processed/openai_anonymized_outputs_n150.jsonl --cache-only`."
    )
    lines.append(
        "- Fact-judge rows use gold task facts for evaluation only. They are not inputs to the non-oracle anonymizer."
    )
    lines.append("")
    lines.append("## Artifact Map")
    lines.append("")
    lines.append("| Artifact | Role |")
    lines.append("|---|---|")
    artifact_rows = [
        ("`data/processed/benchmark.jsonl`", "Main controlled benchmark with text, spans, facts, and QA."),
        ("`data/processed/openai_anonymized_outputs.jsonl`", "Cached earlier 50-example non-oracle anonymizer outputs."),
        ("`data/processed/openai_judgments.jsonl`", "Deterministic scoring for the earlier 50-example run."),
        ("`data/processed/openai_fact_judgments.jsonl`", "Fact-judge rows for the earlier 50-example run."),
        ("`data/processed/openai_anonymized_outputs_n100.jsonl`", "Cached earlier 100-example anonymizer outputs retained as audit trail."),
        ("`data/processed/openai_judgments_n100.jsonl`", "Deterministic scoring for the earlier 100-example run."),
        ("`data/processed/openai_fact_judgments_n100.jsonl`", "Fact-judge rows for the earlier 100-example run."),
        ("`results/openai_combined_results_n100.md`", "Combined deterministic and audited utility for the earlier 100-example run."),
        ("`results/openai_expansion_stability_n100.md`", "Bounded expansion report comparing the 70-example run with the then-promoted 100-example run."),
        ("`results/n100_promotion_readiness.md`", "Synthesis report documenting n100 promotion readiness and caveats."),
        ("`results/paired_delta_report_n100.md`", "Paired CSG-vs-baseline effect sizes for the 100-example run."),
        ("`results/csg_ablation_table_n100.md`", "Critical Span Guard stage ablation for the 100-example run."),
        ("`results/privacy_span_recall_audit_n100.md`", "Span-level direct, quasi, and all-privacy recall audit for the 100-example run."),
        ("`results/surface_metric_audit_n100.md`", "Surface-metric audit for the 100-example run."),
        ("`results/surface_failure_scatter_n100.json`", "Summary counts backing the generated surface-failure scatter."),
        ("`paper/generated_surface_failure_scatter.tex`", "Generated RQ2 scatter showing surface similarity failures."),
        ("`results/legal_qa_disagreement_audit_n100.md`", "Legal QA exact-match audit for the 100-example run."),
        ("`results/residual_qi_audit_n100.md`", "Residual CSG quasi-identifier audit for the 100-example run."),
        ("`results/final_qualitative_audit_n100.md`", "Foreground and n100-edge qualitative audit for paper claims."),
        ("`results/fixed_sample_manual_audit_n100.md`", "Fixed 30-example transparent subset audit across all non-oracle methods."),
        ("`results/fixed_sample_manual_audit_n100.json`", "Structured labels and sample metadata for the fixed subset audit."),
        ("`data/processed/second_annotator_packet_n100.jsonl`", "Blinded second-annotator packet for the fixed subset."),
        ("`results/second_annotator_rubric_n100.md`", "Rubric and reconciliation plan for independent annotation."),
        ("`results/second_annotator_form_n100.csv`", "Blank row-level form for a second annotator."),
        ("`results/second_annotator_answer_key_n100.json`", "Separate method-code answer key for post-annotation reconciliation."),
        ("`results/paper_ready_tables_n100.md`", "Paper-ready tables for the 100-example run."),
        ("`paper/generated_privacy_utility_frontier_n100.tex`", "Generated PGFPlots frontier for the 100-example run."),
        ("`results/cost_and_cache_report_n100.md`", "Cache-only reproducibility and response-slot accounting for the promoted run."),
        ("`results/cost_and_cache_report_n100.json`", "Structured token-proxy budget and expansion projections for API planning."),
        ("`data/processed/benchmark_n200_local.jsonl`", "No-API 200-example local/oracle diagnostic benchmark."),
        ("`data/processed/anonymized_outputs_n200_local.jsonl`", "No-API local/oracle anonymizer outputs for the n200 diagnostic."),
        ("`data/processed/judgments_n200_local.jsonl`", "Deterministic scoring rows for the n200 local/oracle diagnostic."),
        ("`results/summary_n200_local.json`", "Structured local/oracle metrics for the n200 diagnostic."),
        ("`results/main_results_n200_local.md`", "Readable local/oracle metric table for the n200 diagnostic."),
        ("`results/local_n200_diagnostic_report.md`", "Bounded n100-to-n200 local/oracle diagnostic stability report."),
        ("`results/local_n200_diagnostic_report.json`", "Structured n200 diagnostic counts and directional checks."),
        ("`data/processed/benchmark_n120_llm.jsonl`", "Controlled 120-example benchmark for bounded non-oracle OpenAI expansion."),
        ("`data/processed/openai_anonymized_outputs_n120.jsonl`", "Cached n120 non-oracle anonymizer outputs."),
        ("`data/processed/openai_judgments_n120.jsonl`", "Deterministic scoring for the n120 non-oracle expansion."),
        ("`data/processed/openai_fact_judgments_n120.jsonl`", "Fact-judge rows for the n120 non-oracle expansion."),
        ("`results/openai_combined_results_n120.md`", "Prior 120-example combined deterministic and audited utility table retained as audit trail."),
        ("`results/openai_expansion_stability_n120.md`", "n100-to-n120 expansion stability report retained as audit trail."),
        ("`results/openai_api_usage_n120.md`", "Exact provider usage and latency for new n120 cache rows."),
        ("`results/openai_api_usage_n120.json`", "Structured provider usage and cache-coverage data for new n120 rows."),
        ("`data/processed/benchmark_n150_llm.jsonl`", "Controlled 150-example benchmark for the promoted non-oracle OpenAI headline."),
        ("`data/processed/openai_anonymized_outputs_n150.jsonl`", "Cached n150 non-oracle anonymizer outputs."),
        ("`data/processed/openai_judgments_n150.jsonl`", "Deterministic scoring for the promoted n150 non-oracle headline."),
        ("`data/processed/openai_fact_judgments_n150.jsonl`", "Fact-judge rows for the promoted n150 non-oracle headline."),
        ("`results/openai_combined_results_n150.md`", "Headline paper table combining deterministic and audited utility for the promoted 150-example run."),
        ("`results/openai_expansion_stability_n150.md`", "n120-to-n150 promoted expansion stability report."),
        ("`results/openai_api_usage_n150.md`", "Exact provider usage and latency for n100-to-n150 cache rows with stored usage."),
        ("`results/openai_api_usage_n150.json`", "Structured provider usage and cache-coverage data for n100-to-n150 rows."),
        ("`results/workshop_plan_compliance_audit.md`", "Mapping from the original workshop plan to current evidence and remaining gaps."),
        ("`data/processed/openai_anonymized_outputs_n70.jsonl`", "Cached earlier 70-example anonymizer outputs retained as audit trail."),
        ("`results/openai_combined_results_n70.md`", "Earlier 70-example combined table retained as audit trail."),
        ("`results/benchmark_quality_audit.md`", "Schema and integrity audit for benchmark annotations."),
        ("`results/prompt_method_appendix.md`", "Prompt hashes, non-oracle method boundary, and deterministic repair summary."),
        ("`paper/generated_privacy_utility_frontier.tex`", "Generated PGFPlots figure for the promoted non-oracle privacy-utility frontier."),
        ("`results/openai_combined_results.md`", "Earlier 50-example paper table retained for audit trail."),
        ("`results/baseline_bridge_report.md`", "Diagnostic bridge between local baselines, oracles, and non-oracle LLM methods."),
        ("`results/csg_ablation_table.md`", "Critical Span Guard stage ablation."),
        ("`results/residual_qi_audit.md`", "Manual-style audit of remaining CSG quasi-identifier rows."),
        ("`results/final_qualitative_audit.md`", "Foreground example audit for paper writing."),
        ("`results/frontier_policy_sensitivity.md`", "Policy note for strict vs. generalized legal-claim handling."),
        ("`results/threat_model_report.md`", "Bounded threat model, residual-risk table, and release-policy guidance."),
        ("`results/reviewer_risk_register.md`", "Reviewer-facing claim-strength and overclaiming audit."),
        ("`results/submission_verification.md`", "Machine-readable consistency check for the paper package."),
        ("`paper/main.tex` and `paper/main.pdf`", "Current COLM-style manuscript draft and compiled PDF."),
    ]
    for artifact, role in artifact_rows:
        lines.append(f"| {artifact} | {role} |")
    lines.append("")
    lines.append("## Release and Claim Caveats")
    lines.append("")
    lines.append(
        "- This package supports a controlled empirical claim about a privacy-utility tradeoff. It does not establish formal anonymization, HIPAA compliance, k-anonymity, differential privacy, or resistance to motivated re-identification."
    )
    lines.append(
        "- Public legal snippets may still contain sensitive allegations and case facts. Any public release should preserve the upstream license, cite TAB, and avoid representing the derived subset as newly anonymized legal data."
    )
    lines.append(
        "- The clinical split is safe to describe as synthetic controlled data, but its findings should not be generalized to real clinical-note deployment without additional real-note or expert-annotated evaluation."
    )
    lines.append(
        "- The stress slice and oracle methods are diagnostics, not headline deployed systems."
    )
    lines.append(
        "- The local n200 expansion is a no-API local/oracle diagnostic. Do not combine it with the promoted n150 non-oracle LLM headline table."
    )
    lines.append(
        "- The n150 OpenAI expansion is now the promoted non-oracle headline because the matching ablation, qualitative audit, paper tables, fixed audit, and verifier coverage have been regenerated; larger non-oracle runs remain future work."
    )
    lines.append("")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
