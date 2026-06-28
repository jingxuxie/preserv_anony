# Paper Claim Package

Date: 2026-06-28

This is a paper-facing claim checklist for the current promoted n150 package, not final prose.

## Current Strongest Claim

In a controlled 150-example clinical/legal non-oracle LLM run, Critical Span Guard (CSG) improves the observed privacy-utility tradeoff over generic and privacy-first prompting. The claim is empirical and bounded: CSG has zero measured direct identifier leaks, mean QI risk 0.127, exact TCFR 0.884, audited TCFR 0.994, and QA consistency 0.974. It still has three strict-specificity audited-loss rows (`clinical_0055`, `clinical_0059`, `legal_0016`) and eleven residual legal QI rows.

Core support:

- Main n150 table: `results/openai_combined_results_n150.md`
- n120-to-n150 stability and usage: `results/openai_expansion_stability_n150.md`, `results/openai_api_usage_n150.md`
- n150 ablation: `results/csg_ablation_table_n150.md`
- n150 paired effects: `results/paired_delta_report_n150.md`
- n150 residual/privacy audits: `results/residual_qi_audit_n150.md`, `results/privacy_span_recall_audit_n150.md`
- GPT-5.5 external audits: `results/gpt55_external_audit_comparison_fact60_privacyhard20.md`, `results/gpt55_fact_judge_results_stratified60.md`, `results/gpt55_privacy_judge_results_hard20.md`
- n150 fixed subset audit and blinded packet: `results/fixed_sample_manual_audit_n150.md`, `data/processed/second_annotator_packet_n150.jsonl`
- Local n200 diagnostic: `results/local_n200_diagnostic_report.md`
- Claim boundaries: `results/threat_model_report.md`, `results/reviewer_risk_register.md`
- Paper/verifier: `paper/main.tex`, `paper/main.pdf`, `results/submission_verification.md`

The compiled paper is `paper/main.pdf` and is 10 pages under the local COLM submission style.

## Headline Result

| Method | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|
| `generic_llm` | 0.180 | 1.733 | 0.813 | 0.938 | 0.888 |
| `privacy_first_llm` | 0.000 | 0.573 | 0.398 | 0.529 | 0.414 |
| `critical_span_guard_extracted` | 0.000 | 0.127 | 0.884 | 0.994 | 0.974 |

Paired effects:

- Versus generic prompting, CSG reduces direct-leak rate by 0.180 and QI risk by 1.607.
- Versus privacy-first prompting, CSG improves exact TCFR by 0.487, audited TCFR by 0.466, and QA by 0.560.
- Legal-only QI risk is the main nuance: privacy-first has lower legal QI risk because it over-generalizes legal facts.

## GPT-5.5 External Audit Result

Use this as a robustness check, not as a replacement for expert annotation. On a stratified 60-example subset containing all residual CSG QI rows, all strict CSG audited-loss rows, and additional high-stress cases, GPT-5.5 is stricter than the original `gpt-4.1-nano` fact judge but preserves the method ranking.

| Method | Current audited TCFR | GPT-5.5 audited TCFR | Delta | Fact-label agreement |
|---|---:|---:|---:|---:|
| `generic_llm` | 0.925 | 0.875 | -0.050 | 0.935 |
| `privacy_first_llm` | 0.594 | 0.483 | -0.111 | 0.833 |
| `critical_span_guard_extracted` | 0.986 | 0.917 | -0.069 | 0.912 |

On the 20 hardest rows, the GPT-5.5 adversarial privacy audit is conservative. Generic prompting has severe flags on 1.000 of rows and direct flags on 0.600; privacy-first has severe flags on 0.700 and direct flags on 0.000, but has much lower GPT-5.5 TCFR; CSG has severe flags on 0.900 and direct flags on 0.050. This supports the privacy-utility frontier claim rather than a claim that CSG has no residual linkage risk.

External audit usage: `results/gpt55_external_audit_usage_report.md` records 240 rows, 278,291 total provider tokens, and zero missing cache rows for the GPT-5.5 audit artifacts.

## Caveats To Keep

- Clinical rows are synthetic controlled vignettes, not real clinical-note validation.
- TAB-derived legal facts are heuristic and spot-checked, not expert legal annotation.
- Audited TCFR is judge-assisted evidence, not ground truth.
- The GPT-5.5 external audit is still model-assisted evidence, not expert annotation; it should be framed as judge-sensitivity and adversarial-audit stress testing.
- CSG’s deterministic safety/repair layer accounts for the measured ablation gains; do not claim the verifier prompt caused them.
- The local n200 run is a no-API local/oracle diagnostic, not a 200-example non-oracle LLM result.
- This work does not claim formal anonymization, k-anonymity, differential privacy, HIPAA/GDPR compliance, or adversarial linkage resistance.
- The fixed 30-example audit is single-author/manual-style evidence. The second-annotator packet is prepared but not completed.

## Next Validation

1. For a full submission, have a second annotator complete `results/second_annotator_form_n150.csv` using `data/processed/second_annotator_packet_n150.jsonl`.
2. If expanding beyond n150, rerun the ablation, residual audit, fixed audit, paper tables, generated figures, risk register, and verifier.
3. If changing the legal policy from strict to generalized claims, rerun residual-QI auditing and update the caveat language.
