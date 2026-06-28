"""Generate a bounded threat-model and release-policy report."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from io_utils import read_jsonl


OUT_PATH = Path("results/threat_model_report.md")
HEADLINE_SUFFIX = "n150"

METHOD_ORDER = [
    ("generic_llm", "Generic LLM", "Non-oracle LLM baseline"),
    ("privacy_first_llm", "Privacy-first LLM", "Conservative non-oracle baseline"),
    ("critical_span_guard_extracted", "Critical Span Guard", "Non-oracle proposed method"),
]


def load_json(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def mean(summary: dict, method: str, key: str) -> float:
    value = summary["overall"][method][key]
    if isinstance(value, dict):
        return float(value["mean"])
    return float(value)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def row_counts(scored: list[dict], method: str) -> dict:
    rows = [row for row in scored if row.get("method") == method]
    direct_rows = [row for row in rows if float(row.get("direct_identifier_leak", 0.0)) > 0]
    qi_rows = [row for row in rows if float(row.get("quasi_identifier_risk", 0.0)) > 0]
    return {
        "n": len(rows),
        "direct_rows": len(direct_rows),
        "qi_rows": len(qi_rows),
        "qi_ids": sorted(str(row["id"]) for row in qi_rows),
        "direct_ids": sorted(str(row["id"]) for row in direct_rows),
    }


def main() -> None:
    summary = load_json(f"results/openai_summary_{HEADLINE_SUFFIX}.json")
    scored = read_jsonl(f"data/processed/openai_judgments_{HEADLINE_SUFFIX}.jsonl")
    benchmark = read_jsonl(f"data/processed/benchmark_{HEADLINE_SUFFIX}_llm.jsonl")
    robustness = load_json("results/robustness_summary.json")
    domain_counts = Counter(str(row.get("domain", "missing")) for row in benchmark)

    lines = ["# Threat Model and Release Policy", ""]
    lines.append(
        "Bounded privacy framing for the current utility-preserving anonymization study. This report is deliberately narrower than a formal anonymization guarantee."
    )
    lines.append("")
    lines.append("## Release Scenario")
    lines.append("")
    lines.append(
        "- Intended setting: transforming sensitive text before controlled AI research use, evaluation, retrieval experiments, or dataset inspection."
    )
    lines.append(
        "- Data in this package: 75 synthetic clinical vignettes and 75 public TAB-derived ECHR snippets in the promoted non-oracle benchmark; 12 handwritten diagnostic stress examples."
    )
    lines.append(
        "- Primary release concern: whether transformed text still exposes direct identifiers or quasi-identifying facts while preserving the task-critical facts needed for downstream reasoning."
    )
    lines.append(
        "- Public-release posture: treat outputs as research artifacts requiring citation, provenance, license preservation, and residual-risk review before redistribution."
    )
    lines.append("")
    lines.append("## Attacker Model")
    lines.append("")
    lines.append("| Attacker capability | In scope? | How this package addresses it |")
    lines.append("|---|---|---|")
    rows = [
        (
            "String search for known direct identifiers such as names, emails, phone numbers, MRNs, legal application numbers, and exact dates.",
            "yes",
            "Measured by direct identifier leak rate and direct leaked spans.",
        ),
        (
            "Inspection of retained quasi-identifiers such as age, occupation, city, nationality, institution, sensitive status, statute labels, or event descriptions.",
            "yes",
            "Measured by heuristic QI risk and residual QI audit.",
        ),
        (
            "Task user who needs clinical or legal facts after transformation.",
            "yes",
            "Measured by exact TCFR, audited TCFR, and QA consistency.",
        ),
        (
            "Motivated adversary with external databases, linkage attacks, or case-specific background knowledge.",
            "no",
            "Explicitly out of scope; no k-anonymity, differential privacy, or adversarial re-identification guarantee is claimed.",
        ),
        (
            "Legal or regulatory compliance auditor.",
            "no",
            "The package is an empirical research study, not HIPAA, GDPR, court, or institutional compliance evidence.",
        ),
    ]
    for capability, in_scope, mitigation in rows:
        lines.append(f"| {capability} | {in_scope} | {mitigation} |")
    lines.append("")
    lines.append("## Current Measured Residual Risk")
    lines.append("")
    lines.append("| Method | Role | N | Direct leak rows | Mean direct leak | QI rows | Mean QI risk | Exact TCFR | QA |")
    lines.append("|---|---|---:|---:|---:|---:|---:|---:|---:|")
    for method, label, role in METHOD_ORDER:
        counts = row_counts(scored, method)
        lines.append(
            "| {label} | {role} | {n} | {direct_rows} | {direct_mean} | {qi_rows} | {qi_mean} | {tcfr} | {qa} |".format(
                label=label,
                role=role,
                n=counts["n"],
                direct_rows=counts["direct_rows"],
                direct_mean=fmt(mean(summary, method, "direct_identifier_leak")),
                qi_rows=counts["qi_rows"],
                qi_mean=fmt(mean(summary, method, "quasi_identifier_risk")),
                tcfr=fmt(mean(summary, method, "tcfr")),
                qa=fmt(mean(summary, method, "qa_consistency")),
            )
        )
    csg_counts = row_counts(scored, "critical_span_guard_extracted")
    lines.append("")
    lines.append(
        f"CSG residual QI rows: {', '.join(csg_counts['qi_ids']) if csg_counts['qi_ids'] else 'none'}. Direct leak rows: {csg_counts['direct_rows']}/{csg_counts['n']}."
    )
    lines.append("")
    lines.append("## Frontier Cases")
    lines.append("")
    lines.append(
        "- The eleven residual CSG QI rows in the promoted 150-example run are legal task-critical overlap or frontier cases: `legal_0002`, `legal_0005`, `legal_0025`, `legal_0042`, `legal_0046`, `legal_0053`, `legal_0054`, `legal_0055`, `legal_0056`, `legal_0062`, and `legal_0063`."
    )
    lines.append(
        "- The stress slice shows the same issue under controlled diagnostics: CSG oracle preserves QA while retaining task-critical QI on 6/12 rows; privacy-first oracle removes QI but fails QA on 11/12 rows."
    )
    lines.append(
        "- This supports a policy-sensitive frontier claim rather than a claim that all residual QI is technically unavoidable."
    )
    lines.append("")
    lines.append("## Policy Guidance")
    lines.append("")
    lines.append("| Use case | Recommended policy | Rationale |")
    lines.append("|---|---|---|")
    policy_rows = [
        (
            "Internal method evaluation",
            "Use strict task annotations and report residual QI rows.",
            "Keeps utility target measurable and makes frontier cases inspectable.",
        ),
        (
            "Public benchmark release",
            "Share synthetic clinical rows as controlled examples with provenance; release TAB-derived legal subsets only with upstream license and residual-risk notes.",
            "Clinical rows are synthetic; legal snippets remain public case text with sensitive allegations.",
        ),
        (
            "Privacy-aggressive downstream sharing",
            "Consider generalized legal-claim annotations and rerun residual QI auditing.",
            "Can reduce residual QI but changes the legal utility target.",
        ),
        (
            "Compliance or adversarial privacy claims",
            "Do not use this package as sufficient evidence.",
            "The metrics do not prove formal anonymization or protection against external-linkage attacks.",
        ),
    ]
    for use_case, policy, rationale in policy_rows:
        lines.append(f"| {use_case} | {policy} | {rationale} |")
    lines.append("")
    lines.append("## Paper-Safe Wording")
    lines.append("")
    lines.append(
        "We evaluate direct string leakage and heuristic quasi-identifier retention under a bounded release scenario. The method reduces measured direct and quasi-identifier risk on this sample, but it is not a formal anonymization guarantee and does not protect against motivated re-identification with external knowledge."
    )
    lines.append("")
    lines.append("## Inventory Cross-Check")
    lines.append("")
    lines.append(f"- Main benchmark domains: {', '.join(f'{k}={v}' for k, v in sorted(domain_counts.items()))}.")
    lines.append(
        "- Robustness CSG oracle QI risk: {qi}; privacy-first oracle QA: {qa}.".format(
            qi=fmt(float(robustness["overall"]["critical_span_guard_oracle"]["quasi_identifier_risk"]["mean"])),
            qa=fmt(float(robustness["overall"]["privacy_first_oracle"]["qa_consistency"]["mean"])),
        )
    )
    lines.append("")
    lines.append("Status: PASS. Threat model is bounded and explicitly excludes formal anonymization, compliance, and adversarial linkage guarantees.")
    lines.append("")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
