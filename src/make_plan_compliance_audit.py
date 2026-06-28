"""Map the workshop plan requirements to current artifacts."""

from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from datetime import date
from pathlib import Path

from io_utils import read_jsonl


OUT_PATH = Path("results/workshop_plan_compliance_audit.md")
HEADLINE_SUFFIX = "n150"
HEADLINE_EXAMPLES = 150
HEADLINE_DOMAIN_EXAMPLES = 75


def load_json(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def exists(path: str) -> bool:
    return Path(path).exists()


def read(path: str) -> str:
    return Path(path).read_text(encoding="utf-8") if exists(path) else ""


def count_unique_examples(path: str) -> int:
    return len({row["id"] for row in read_jsonl(path) if row.get("method") == "generic_llm"})


def status(ok: bool, partial: bool = False) -> str:
    if ok:
        return "PASS"
    if partial:
        return "PARTIAL"
    return "GAP"


def add(rows: list[list[str]], item: str, state: str, evidence: str, next_step: str) -> None:
    rows.append([item, state, evidence, next_step])


def table(rows: list[list[str]]) -> list[str]:
    lines = ["| Plan item | Status | Evidence | Next action |", "|---|---|---|---|"]
    for row in rows:
        lines.append("| " + " | ".join(cell.replace("\n", " ") for cell in row) + " |")
    return lines


def pdf_pages(path: str = "paper/main.pdf") -> int | None:
    try:
        result = subprocess.run(["pdfinfo", path], check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError):
        log = read("paper/main.log")
        match = re.search(r"Output written on main\.pdf \((\d+) pages?", log)
        return int(match.group(1)) if match else None
    match = re.search(r"^Pages:\s+(\d+)$", result.stdout, flags=re.MULTILINE)
    return int(match.group(1)) if match else None


def main() -> None:
    benchmark = read_jsonl("data/processed/benchmark.jsonl")
    benchmark_headline = read_jsonl(f"data/processed/benchmark_{HEADLINE_SUFFIX}_llm.jsonl")
    domains = Counter(row.get("domain", "missing") for row in benchmark)
    domains_headline = Counter(row.get("domain", "missing") for row in benchmark_headline)
    outputs_n100 = read_jsonl("data/processed/openai_anonymized_outputs_n100.jsonl")
    outputs_headline = read_jsonl(f"data/processed/openai_anonymized_outputs_{HEADLINE_SUFFIX}.jsonl") if exists(f"data/processed/openai_anonymized_outputs_{HEADLINE_SUFFIX}.jsonl") else []
    output_methods = sorted({row.get("method", "missing") for row in outputs_headline})
    det = load_json(f"results/openai_summary_{HEADLINE_SUFFIX}.json")
    audit = load_json(f"results/openai_fact_judge_summary_{HEADLINE_SUFFIX}.json")
    local = load_json("results/summary.json")
    local_n200 = load_json("results/local_n200_diagnostic_report.json") if exists("results/local_n200_diagnostic_report.json") else {}
    final_qual = read(f"results/final_qualitative_audit_{HEADLINE_SUFFIX}.md")
    manual_case_count = len(re.findall(r"^### `", final_qual, flags=re.MULTILINE))
    fixed_audit = load_json(f"results/fixed_sample_manual_audit_{HEADLINE_SUFFIX}.json") if exists(f"results/fixed_sample_manual_audit_{HEADLINE_SUFFIX}.json") else {}
    fixed_meta = fixed_audit.get("metadata", {})
    fixed_summary = fixed_audit.get("summary", {})
    fixed_examples = int(fixed_meta.get("examples", 0))
    fixed_rows = int(fixed_meta.get("method_rows", 0))
    fixed_domains = fixed_summary.get("domain_counts", {})
    second_packet_exists = (
        exists(f"data/processed/second_annotator_packet_{HEADLINE_SUFFIX}.jsonl")
        and exists(f"results/second_annotator_rubric_{HEADLINE_SUFFIX}.md")
        and exists(f"results/second_annotator_form_{HEADLINE_SUFFIX}.csv")
        and exists(f"results/second_annotator_answer_key_{HEADLINE_SUFFIX}.json")
    )
    fixed_audit_ok = (
        fixed_examples >= 20
        and fixed_rows >= fixed_examples * 3
        and fixed_meta.get("no_api_calls") is True
        and fixed_domains.get("clinical") == 15
        and fixed_domains.get("legal") == 15
    )
    verification = read("results/submission_verification.md")
    verification_match = re.search(r"Passed\s+(\d+/\d+)\s+checks", verification)
    verification_status = verification_match.group(1) if verification_match else "unknown"
    pages = pdf_pages()
    pages_text = f"{pages} pages" if pages is not None else "unknown pages"
    local_n200_ok = (
        local_n200.get("benchmark_rows") == 200
        and local_n200.get("domain_counts", {}).get("clinical") == 100
        and local_n200.get("domain_counts", {}).get("legal") == 100
        and local_n200.get("all_directional_checks_pass") is True
    )
    headline_usage = load_json(f"results/openai_api_usage_{HEADLINE_SUFFIX}.json") if exists(f"results/openai_api_usage_{HEADLINE_SUFFIX}.json") else {}
    headline_ids = {row.get("id") for row in outputs_headline if row.get("method") == "generic_llm"}
    headline_ok = (
        len(headline_ids) == HEADLINE_EXAMPLES
        and exists(f"results/openai_expansion_stability_{HEADLINE_SUFFIX}.md")
        and exists(f"results/openai_combined_results_{HEADLINE_SUFFIX}.md")
        and headline_usage.get("usage_rows") == 400
        and headline_usage.get("cache_coverage", {}).get("missing_response_slots") == 0
    )

    rows: list[list[str]] = []
    add(
        rows,
        "100-200 example benchmark with clinical and legal splits",
        status(
            len(benchmark_headline) == HEADLINE_EXAMPLES
            and domains_headline.get("clinical") == HEADLINE_DOMAIN_EXAMPLES
            and domains_headline.get("legal") == HEADLINE_DOMAIN_EXAMPLES
            and local_n200_ok
        ),
        (
            f"`data/processed/benchmark_{HEADLINE_SUFFIX}_llm.jsonl` has {len(benchmark_headline)} promoted non-oracle rows: "
            + ", ".join(f"{k}={v}" for k, v in sorted(domains_headline.items()))
            + "; `data/processed/benchmark.jsonl` retains the original 100-row audit trail: "
            + ", ".join(f"{k}={v}" for k, v in sorted(domains.items()))
            + "; `data/processed/benchmark_n200_local.jsonl` has a no-API local diagnostic expansion with 200 rows "
            + f"(clinical={local_n200.get('domain_counts', {}).get('clinical', 'missing')}, legal={local_n200.get('domain_counts', {}).get('legal', 'missing')})."
        ),
        "For a long paper, expand the non-oracle LLM headline toward 300-500 examples; the local n200 diagnostic supports sample-size sensitivity but does not replace a larger non-oracle run.",
    )
    add(
        rows,
        "Methods include regex, Presidio, generic LLM, privacy-first LLM, and Critical Span Guard",
        status(
            {"regex_rules", "presidio_baseline"}.issubset(local["overall"])
            and {"generic_llm", "privacy_first_llm", "critical_span_guard_extracted"}.issubset(output_methods)
        ),
        f"`results/summary.json` and `results/local_n200_diagnostic_report.md` cover local baselines/oracles; `data/processed/openai_anonymized_outputs_{HEADLINE_SUFFIX}.jsonl` covers the promoted non-oracle LLM methods; `results/openai_expansion_stability_{HEADLINE_SUFFIX}.md` documents the n120-to-n150 expansion.",
        "Keep local baselines framed as diagnostic because the promoted headline compares non-oracle LLM prompting methods.",
    )
    add(
        rows,
        "Privacy metrics: direct leak, PII/span recall, QI risk",
        status(
            "direct_identifier_leak" in det["overall"]["critical_span_guard_extracted"]
            and "pii_span_recall" in det["overall"]["critical_span_guard_extracted"]
            and exists(f"results/privacy_span_recall_audit_{HEADLINE_SUFFIX}.md")
        ),
        f"`results/openai_summary_{HEADLINE_SUFFIX}.json` and `results/privacy_span_recall_audit_{HEADLINE_SUFFIX}.md` report row and span privacy metrics.",
        "Do not claim formal anonymization; keep threat model bounded.",
    )
    add(
        rows,
        "Utility metrics: TCFR, CCR, QA consistency, edit rate",
        status(
            "tcfr" in det["overall"]["critical_span_guard_extracted"]
            and "qa_consistency" in det["overall"]["critical_span_guard_extracted"]
            and "audited_ccr" in audit["overall"]["critical_span_guard_extracted"]
        ),
        f"`results/openai_results_{HEADLINE_SUFFIX}.md` covers exact metrics; `results/openai_fact_judge_results_{HEADLINE_SUFFIX}.md` covers audited TCFR/CCR.",
        "Keep audited TCFR as judge-assisted evidence, not ground truth.",
    )
    add(
        rows,
        "Paired statistics and effect sizes",
        status(exists(f"results/paired_delta_report_{HEADLINE_SUFFIX}.md") and exists(f"results/paired_delta_report_{HEADLINE_SUFFIX}.json")),
        f"`results/paired_delta_report_{HEADLINE_SUFFIX}.md` reports paired advantages, bootstrap CIs, wins/ties/losses, and sign-test p-values.",
        "If moving to a long paper, add a brief methods note explaining bootstrap/sign-test choices.",
    )
    add(
        rows,
        "Surface/semantic similarity foil for RQ2",
        status(exists(f"results/surface_metric_audit_{HEADLINE_SUFFIX}.md") and exists("paper/generated_surface_failure_scatter.tex")),
        f"`results/surface_metric_audit_{HEADLINE_SUFFIX}.md` reports token, edit, Jaccard, and TF-IDF analyses; `paper/generated_surface_failure_scatter.tex` visualizes high-similarity privacy and utility failures.",
        "Keep surface metrics framed as foils rather than headline utility metrics.",
    )
    add(
        rows,
        "Ablation of CSG draft, verified, and safety/repair stages",
        status(exists(f"results/csg_ablation_table_{HEADLINE_SUFFIX}.md")),
        f"`results/csg_ablation_table_{HEADLINE_SUFFIX}.md` shows verifier prompt did not change deterministic metrics; safety/repair layer closed measured leaks.",
        "Do not claim verifier-prompt gains unless a future run supports it.",
    )
    add(
        rows,
        "Manual audit on 20-50 examples or transparent subset audit",
        status(fixed_audit_ok or manual_case_count >= 20, partial=manual_case_count > 0),
        (
            f"`results/fixed_sample_manual_audit_{HEADLINE_SUFFIX}.md` covers {fixed_examples} fixed examples "
            f"and {fixed_rows} method rows ({', '.join(f'{k}={v}' for k, v in sorted(fixed_domains.items()))}); "
            f"`results/final_qualitative_audit_{HEADLINE_SUFFIX}.md` spot-checks {manual_case_count} foreground/frontier cases; "
            f"`data/processed/second_annotator_packet_{HEADLINE_SUFFIX}.jsonl` is ready for a blinded second pass."
        )
        if fixed_audit_ok and second_packet_exists
        else (
            f"`results/fixed_sample_manual_audit_{HEADLINE_SUFFIX}.md` covers {fixed_examples} fixed examples "
            f"and {fixed_rows} method rows ({', '.join(f'{k}={v}' for k, v in sorted(fixed_domains.items()))}); "
            f"`results/final_qualitative_audit_{HEADLINE_SUFFIX}.md` spot-checks {manual_case_count} foreground/frontier cases."
        )
        if fixed_audit_ok
        else f"`results/final_qualitative_audit_{HEADLINE_SUFFIX}.md` spot-checks {manual_case_count} foreground/frontier cases; `results/manual_audit_package_{HEADLINE_SUFFIX}.md` is a larger generated review packet.",
        "For a full submission, have a second annotator complete the blinded packet and report agreement/adjudication.",
    )
    add(
        rows,
        "Failure taxonomy",
        status(exists(f"results/error_taxonomy_{HEADLINE_SUFFIX}.md")),
        f"`results/error_taxonomy_{HEADLINE_SUFFIX}.md`, `results/legal_qa_disagreement_audit_{HEADLINE_SUFFIX}.md`, and `results/residual_qi_audit_{HEADLINE_SUFFIX}.md` classify major failure modes.",
        "For a long paper, convert this into a concise table with representative clinical/legal examples.",
    )
    add(
        rows,
        "Cost and latency table",
        status(False, partial=exists("results/cost_and_cache_report_n100.md") and headline_ok),
        (
            "`results/cost_and_cache_report_n100.md` and `.json` document older n100 required cached response slots, token-proxy budget, and n150/n200/n300/n500 expansion projections; "
            f"`results/openai_api_usage_{HEADLINE_SUFFIX}.md` records exact provider usage and latency for 400 n100-to-n150 expansion/cache rows and cache coverage for the promoted n150 package."
        ),
        "Continue persisting provider usage and elapsed time for future API calls; do not mix exact n100-to-n150 expansion usage rows with older n100 proxy-only cache rows.",
    )
    add(
        rows,
        "Paper draft, figure, references, and verification",
        status(exists("paper/main.pdf") and exists("results/submission_verification.md")),
        f"`paper/main.pdf` compiles to {pages_text}; `results/submission_verification.md` passes {verification_status} checks.",
        "Before submission, decide whether to target short-paper concision or expand evidence for an 8-page version.",
    )

    lines = ["# Workshop Plan Compliance Audit", ""]
    lines.append(f"Generated: {date.today().isoformat()}")
    lines.append("")
    lines.append(
        "This audit maps the original workshop plan to current artifacts. PASS means the current evidence directly supports the item; PARTIAL means the paper can discuss it with caveats; GAP means more work is needed."
    )
    lines.append("")
    lines.extend(table(rows))
    lines.append("")
    lines.append("## Highest-Impact Remaining Gaps")
    lines.append("")
    if fixed_audit_ok:
        if second_packet_exists:
            lines.append("1. Manual audit coverage now meets the workshop-plan transparent-subset target, and a blinded second-annotator packet is prepared; completed independent annotation or adjudication is still future work.")
        else:
            lines.append("1. Manual audit coverage now meets the workshop-plan transparent-subset target, but it is single-author/manual-style evidence rather than independent multi-annotator agreement.")
        lines.append("2. Exact cost/latency accounting is now available for the 400 n100-to-n150 expansion/cache rows, but remains partial for the older n100 cache rows because early calls did not persist provider usage or elapsed time.")
        lines.append("3. The promoted n150 non-oracle headline and local n200 diagnostic improve sample-size sensitivity, but the non-oracle headline is still below the 300-500 example stronger-study target.")
        lines.append("4. The surface-similarity scatter now strengthens RQ2; if page pressure increases, move it to an appendix rather than dropping the underlying audit.")
    else:
        lines.append("1. Manual audit coverage is the main remaining weakness: the current n150 qualitative audit is high-signal but still single-author/manual-style evidence.")
        lines.append("2. Exact cost/latency accounting is now available for the 400 n100-to-n150 expansion/cache rows, but remains partial for the older n100 cache rows because early calls did not persist provider usage or elapsed time.")
        lines.append("3. The promoted n150 non-oracle headline and local n200 diagnostic improve sample-size sensitivity, but the non-oracle headline is still below the 300-500 example stronger-study target.")
        lines.append("4. A separate semantic-similarity scatter figure is optional but would strengthen RQ2 if page space allows.")
    lines.append("")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
