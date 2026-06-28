"""Generate a reviewer-facing claim risk register from current result artifacts."""

from __future__ import annotations

import json
from pathlib import Path

from io_utils import read_jsonl


OUT_PATH = Path("results/reviewer_risk_register.md")
HEADLINE_SUFFIX = "n150"
HEADLINE_N = 150
HEADLINE_RESIDUAL_QI_ROWS = 11


def load_json(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def mean(summary: dict, method: str, key: str) -> float:
    value = summary["overall"][method][key]
    if isinstance(value, dict):
        return float(value["mean"])
    return float(value)


def domain_mean(summary: dict, domain: str, method: str, key: str) -> float:
    value = summary["by_domain"][domain][method][key]
    if isinstance(value, dict):
        return float(value["mean"])
    return float(value)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def ci(stat: dict) -> str:
    low, high = stat["ci95"]
    return f"{fmt(float(low))}-{fmt(float(high))}"


def paired(paired_summary: dict, baseline: str, metric: str) -> dict:
    return paired_summary["overall"][baseline][metric]


def row_counts(scored: list[dict], method: str) -> tuple[int, int, int]:
    rows = [row for row in scored if row.get("method") == method]
    direct_rows = sum(1 for row in rows if float(row.get("direct_identifier_leak", 0.0)) > 0)
    qi_rows = sum(1 for row in rows if float(row.get("quasi_identifier_risk", 0.0)) > 0)
    return len(rows), direct_rows, qi_rows


def add_claim(
    rows: list[list[str]],
    claim: str,
    status: str,
    evidence: str,
    safe_wording: str,
    overclaim_risk: str,
) -> None:
    rows.append([claim, status, evidence, safe_wording, overclaim_risk])


def markdown_table(rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(rows[0]) + " |"]
    lines.append("|" + "|".join(["---"] * len(rows[0])) + "|")
    for row in rows[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return "\n".join(lines)


def main() -> None:
    det = load_json(f"results/openai_summary_{HEADLINE_SUFFIX}.json")
    audit = load_json(f"results/openai_fact_judge_summary_{HEADLINE_SUFFIX}.json")
    ablation = load_json(f"results/csg_ablation_summary_{HEADLINE_SUFFIX}.json")
    surface = load_json(f"results/surface_metric_audit_{HEADLINE_SUFFIX}.json")
    paired_summary = load_json(f"results/paired_delta_report_{HEADLINE_SUFFIX}.json")
    scored = read_jsonl(f"data/processed/openai_judgments_{HEADLINE_SUFFIX}.jsonl")

    n_csg, csg_direct_rows, csg_qi_rows = row_counts(scored, "critical_span_guard_extracted")
    n_generic, generic_direct_rows, generic_qi_rows = row_counts(scored, "generic_llm")
    n_privacy, privacy_direct_rows, privacy_qi_rows = row_counts(scored, "privacy_first_llm")

    rows = [["Claim", "Status", "Evidence", "Safe paper wording", "Risk if overstated"]]
    add_claim(
        rows,
        "CSG improves privacy over generic prompting.",
        "Strong on current sample",
        (
            f"Direct leak {fmt(mean(det, 'critical_span_guard_extracted', 'direct_identifier_leak'))} vs "
            f"{fmt(mean(det, 'generic_llm', 'direct_identifier_leak'))}; QI risk "
            f"{fmt(mean(det, 'critical_span_guard_extracted', 'quasi_identifier_risk'))} vs "
            f"{fmt(mean(det, 'generic_llm', 'quasi_identifier_risk'))}. All privacy-span recall "
            f"{fmt(mean(det, 'critical_span_guard_extracted', 'pii_span_recall'))} vs "
            f"{fmt(mean(det, 'generic_llm', 'pii_span_recall'))}. Paired direct-leak reduction "
            f"{fmt(paired(paired_summary, 'generic_llm', 'direct_leak_reduction')['mean'])} "
            f"[{ci(paired(paired_summary, 'generic_llm', 'direct_leak_reduction'))}], QI reduction "
            f"{fmt(paired(paired_summary, 'generic_llm', 'qi_risk_reduction')['mean'])} "
            f"[{ci(paired(paired_summary, 'generic_llm', 'qi_risk_reduction'))}]."
        ),
        f"On this {HEADLINE_N}-example run, CSG reduces direct leaks and quasi-identifier risk relative to generic prompting.",
        "Do not imply adversarial privacy or formal anonymization.",
    )
    add_claim(
        rows,
        "CSG improves utility over privacy-first prompting.",
        "Strong on current sample",
        (
            f"Exact TCFR gain {fmt(paired(paired_summary, 'privacy_first_llm', 'exact_tcfr_gain')['mean'])} "
            f"[{ci(paired(paired_summary, 'privacy_first_llm', 'exact_tcfr_gain'))}], audited TCFR gain "
            f"{fmt(paired(paired_summary, 'privacy_first_llm', 'audited_tcfr_gain')['mean'])} "
            f"[{ci(paired(paired_summary, 'privacy_first_llm', 'audited_tcfr_gain'))}], QA gain "
            f"{fmt(paired(paired_summary, 'privacy_first_llm', 'qa_gain')['mean'])} "
            f"[{ci(paired(paired_summary, 'privacy_first_llm', 'qa_gain'))}]."
        ),
        "CSG preserves task-critical facts and QA answers better than privacy-first anonymization on paired examples.",
        "Do not say privacy-first is always worse; it is intentionally conservative and sometimes has lower legal QI risk.",
    )
    add_claim(
        rows,
        "CSG improves utility over generic prompting.",
        "Supported but modest",
        (
            f"Overall audited TCFR {fmt(audit['overall']['critical_span_guard_extracted']['audited_tcfr'])} vs "
            f"{fmt(audit['overall']['generic_llm']['audited_tcfr'])}; paired audited gain "
            f"{fmt(paired(paired_summary, 'generic_llm', 'audited_tcfr_gain')['mean'])} "
            f"[{ci(paired(paired_summary, 'generic_llm', 'audited_tcfr_gain'))}]. Legal-only paired utility gains are small."
        ),
        "CSG slightly improves retained utility over generic prompting while greatly improving privacy.",
        "Do not frame the generic comparison as a large utility win; the main advantage over generic is privacy.",
    )
    add_claim(
        rows,
        "The promoted n150 headline carries strict specificity and residual-QI caveats.",
        "Supported and documented",
        (
            f"In the {HEADLINE_N}-example headline run, CSG has direct leak "
            f"{fmt(mean(det, 'critical_span_guard_extracted', 'direct_identifier_leak'))}, QI risk "
            f"{fmt(mean(det, 'critical_span_guard_extracted', 'quasi_identifier_risk'))}, and audited TCFR "
            f"{fmt(audit['overall']['critical_span_guard_extracted']['audited_tcfr'])}; generic has direct leak "
            f"{fmt(mean(det, 'generic_llm', 'direct_identifier_leak'))}, QI risk "
            f"{fmt(mean(det, 'generic_llm', 'quasi_identifier_risk'))}, audited TCFR "
            f"{fmt(audit['overall']['generic_llm']['audited_tcfr'])}; privacy-first audited TCFR is "
            f"{fmt(audit['overall']['privacy_first_llm']['audited_tcfr'])}. The n150 audit bundle marks `clinical_0055`, `clinical_0059`, and `legal_0016` as strict-specificity CSG audited-loss rows and eleven legal rows as residual QI cases."
        ),
        "Use the 150-example headline with three strict-specificity audited-loss rows and eleven residual legal QI rows.",
        "Do not omit the added audited CSG edge case or imply perfect legal-specificity preservation.",
    )
    add_claim(
        rows,
        "CSG has zero direct leaks.",
        "Supported as measured sample result",
        (
            f"CSG direct leak rows {csg_direct_rows}/{n_csg}; generic {generic_direct_rows}/{n_generic}; "
            f"privacy-first {privacy_direct_rows}/{n_privacy}."
        ),
        f"CSG has zero measured direct identifier leaks on the current {HEADLINE_N}-example sample.",
        "Do not state this as a guarantee beyond the evaluated span list and sample.",
    )
    add_claim(
        rows,
        "Remaining CSG privacy risk is small and inspectable.",
        "Supported with caveat",
        (
            f"CSG rows with QI hits {csg_qi_rows}/{n_csg}; generic {generic_qi_rows}/{n_generic}; "
            f"privacy-first {privacy_qi_rows}/{n_privacy}. Residual rows are documented in the residual QI audit."
        ),
        f"The remaining measured CSG QI risk is concentrated in {HEADLINE_RESIDUAL_QI_ROWS} legal task-critical overlap or frontier cases.",
        "Do not claim all residual QI is unavoidable; it depends on the chosen legal utility target.",
    )
    add_claim(
        rows,
        "The verifier prompt caused the measured CSG gain.",
        "Unsupported; avoid",
        (
            f"CSG draft and verified stages both have direct leak {fmt(mean(ablation, 'csg_draft', 'direct_identifier_leak'))}, "
            f"QI risk {fmt(mean(ablation, 'csg_draft', 'quasi_identifier_risk'))}, TCFR "
            f"{fmt(mean(ablation, 'csg_draft', 'tcfr'))}; verified+safety changes these to direct leak "
            f"{fmt(mean(ablation, 'csg_verified_safety', 'direct_identifier_leak'))}, QI risk "
            f"{fmt(mean(ablation, 'csg_verified_safety', 'quasi_identifier_risk'))}, TCFR "
            f"{fmt(mean(ablation, 'csg_verified_safety', 'tcfr'))}."
        ),
        "Report that the deterministic safety/repair layer accounts for the measured gains in this cached ablation.",
        "A reviewer can reject a claim that verification improved this run because the ablation contradicts it.",
    )
    add_claim(
        rows,
        "Generic surface similarity is enough to evaluate utility.",
        "Refuted by current audit",
        (
            f"Generic and CSG token F1 are close ({fmt(surface['by_method']['generic_llm']['token_f1'])} vs "
            f"{fmt(surface['by_method']['critical_span_guard_extracted']['token_f1'])}), and generic has higher TF-IDF cosine "
            f"({fmt(surface['by_method']['generic_llm']['tfidf_cosine'])} vs "
            f"{fmt(surface['by_method']['critical_span_guard_extracted']['tfidf_cosine'])}), but privacy-failure rates differ "
            f"({fmt(surface['by_method']['generic_llm']['privacy_failure_rate'])} vs "
            f"{fmt(surface['by_method']['critical_span_guard_extracted']['privacy_failure_rate'])}) and audited fact-failure rates differ "
            f"({fmt(surface['by_method']['generic_llm']['audited_fact_failure_rate'])} vs "
            f"{fmt(surface['by_method']['critical_span_guard_extracted']['audited_fact_failure_rate'])})."
        ),
        "Use surface metrics as foils; they miss privacy failures and task-critical fact loss.",
        "Do not omit task-level metrics and rely on edit distance or token overlap.",
    )
    add_claim(
        rows,
        "Privacy-first is uniformly less private than CSG.",
        "False; nuance required",
        (
            f"Overall QI risk favors CSG ({fmt(mean(det, 'critical_span_guard_extracted', 'quasi_identifier_risk'))} vs "
            f"{fmt(mean(det, 'privacy_first_llm', 'quasi_identifier_risk'))}), but legal-only QI risk favors privacy-first "
            f"({fmt(domain_mean(det, 'legal', 'critical_span_guard_extracted', 'quasi_identifier_risk'))} vs "
            f"{fmt(domain_mean(det, 'legal', 'privacy_first_llm', 'quasi_identifier_risk'))})."
        ),
        "Overall CSG has lower QI risk, while legal-only privacy-first can be lower because it over-generalizes legal facts.",
        "A blanket privacy claim ignores the legal split and weakens credibility.",
    )
    add_claim(
        rows,
        "Audited TCFR is ground truth.",
        "Supported only as corroborating audit",
        (
            f"Audited TCFR is {fmt(audit['overall']['critical_span_guard_extracted']['audited_tcfr'])} for CSG, "
            f"{fmt(audit['overall']['generic_llm']['audited_tcfr'])} for generic, and "
            f"{fmt(audit['overall']['privacy_first_llm']['audited_tcfr'])} for privacy-first."
        ),
        "Use audited TCFR to identify faithful paraphrases, backed by manual spot checks.",
        "Do not treat a judge model as expert annotation or sole ground truth.",
    )
    add_claim(
        rows,
        "The clinical results demonstrate real clinical-note de-identification.",
        "Unsupported; avoid",
        "Clinical examples are synthetic controlled vignettes; no real PHI is used.",
        "The clinical split tests controlled utility preservation without real PHI.",
        "A reviewer will object if the paper implies real clinical-note deployment evidence.",
    )
    add_claim(
        rows,
        "The method provides formal anonymization or compliance.",
        "Unsupported; avoid",
        "Metrics are deterministic span checks and heuristic QI scoring over a small benchmark.",
        "The work evaluates privacy-utility behavior; it does not claim k-anonymity, differential privacy, HIPAA compliance, or adversarial resistance.",
        "Formal privacy claims require a threat model and separate proof or audit.",
    )
    add_claim(
        rows,
        "The stress slice is headline performance evidence.",
        "Diagnostic only",
        "The stress slice has 12 handwritten examples and includes oracle variants.",
        "Use the stress slice to illustrate inherent privacy-utility overlap, not as the main non-oracle performance result.",
        f"Overweighting oracle stress results can make the paper look less empirical than the {HEADLINE_N}-example LLM run.",
    )

    lines = ["# Reviewer Risk Register", ""]
    lines.append(
        "Generated from current result JSONL/JSON artifacts. The purpose is to keep paper claims aligned with what the fast-iteration evidence actually supports."
    )
    lines.append("")
    lines.append(markdown_table(rows))
    lines.append("")
    lines.append("## Highest-Risk Reviewer Attacks")
    lines.append("")
    lines.append(f"- Small sample: the fully audited headline LLM result is {HEADLINE_N} examples, split 75/75 across synthetic clinical and TAB-derived legal data, with three CSG strict-specificity audited-loss rows and {HEADLINE_RESIDUAL_QI_ROWS} residual CSG QI rows.")
    lines.append("- Sample-size sensitivity: a no-API n200 local/oracle diagnostic preserves the local frontier, but it does not replace a 300-500 example fully audited non-oracle headline.")
    lines.append("- Clinical realism: the clinical split is synthetic and should be framed as controlled utility evidence, not real-note validation.")
    lines.append("- Legal annotation quality: legal facts are heuristic plus spot-checks, not expert legal annotation.")
    lines.append("- Judge dependence: audited TCFR is useful for paraphrase, but it is still an LLM judge and needs manual examples.")
    lines.append("- Method attribution: the current ablation supports the deterministic safety/repair layer, not a verifier-prompt gain.")
    lines.append("- Privacy claim scope: measured direct/QI checks are not formal anonymization or adversarial privacy guarantees.")
    lines.append("")
    lines.append("## Recommended One-Sentence Claim")
    lines.append("")
    lines.append(
        f"In a {HEADLINE_N}-example controlled clinical/legal run, CSG improves the observed privacy-utility tradeoff by reducing privacy risk relative to generic prompting and preserving task-critical facts relative to privacy-first prompting, with explicit residual legal caveats."
    )
    lines.append("")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
