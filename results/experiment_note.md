# Fast Iteration Note: Utility-Preserving Anonymization

Date: 2026-06-28

## Current State

The promoted paper package is now the 150-example non-oracle OpenAI run: 75 synthetic clinical vignettes and 75 TAB-derived legal snippets. The earlier 50-, 70-, 100-, and 120-example OpenAI runs remain audit trail; the 200-example run is a no-API local/oracle diagnostic only.

`paper/main.pdf` compiles to 10 pages under the local COLM submission style.

## Main Non-Oracle Result

From `results/openai_combined_results_n150.md`:

| Method | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA consistency |
|---|---:|---:|---:|---:|---:|
| `generic_llm` | 0.180 | 1.733 | 0.813 | 0.938 | 0.888 |
| `privacy_first_llm` | 0.000 | 0.573 | 0.398 | 0.529 | 0.414 |
| `critical_span_guard_extracted` | 0.000 | 0.127 | 0.884 | 0.994 | 0.974 |

CSG has zero measured direct leaks and much lower QI risk than generic prompting, while preserving much more task-critical utility than privacy-first prompting. Caveats: three strict-specificity audited-loss rows (`clinical_0055`, `clinical_0059`, `legal_0016`) and eleven residual legal QI rows.

## Support Artifacts

- n150 ablation: `results/csg_ablation_table_n150.md`
- n150 paired deltas: `results/paired_delta_report_n150.md`
- n150 privacy span recall: `results/privacy_span_recall_audit_n150.md`
- n150 residual-QI audit: `results/residual_qi_audit_n150.md`
- n150 surface metric foil: `results/surface_metric_audit_n150.md`
- n150 fixed 30-example audit: `results/fixed_sample_manual_audit_n150.md`
- n150 manual-audit agreement/readiness synthesis: `results/manual_audit_agreement_n150.md`
- n150 blinded second-annotator packet: `data/processed/second_annotator_packet_n150.jsonl`
- GPT-5.5 external audit: `results/gpt55_external_audit_comparison_fact60_privacyhard20.md`
- Exact provider usage for n100-to-n150 cache rows: `results/openai_api_usage_n150.md`
- Plan/verifier status: `results/workshop_plan_compliance_audit.md`, `results/submission_verification.md`

The promoted n150 cache has exact provider usage for the 400 n100-to-n150 cache rows: 249,340 prompt tokens, 103,847 completion tokens, 353,187 total tokens, and 687.4 elapsed request seconds. The original n100 cache rows remain proxy-only because early calls did not store provider usage.

## Local Diagnostic

From `results/local_n200_diagnostic_report.md`:

| Method | Direct leak | QI risk | TCFR | QA consistency |
|---|---:|---:|---:|---:|
| `direct_span_oracle` | 0.000 | 2.810 | 1.000 | 1.000 |
| `privacy_first_oracle` | 0.000 | 0.005 | 0.448 | 0.336 |
| `critical_span_guard_oracle` | 0.000 | 0.225 | 1.000 | 1.000 |

This preserves the local/oracle frontier but is not a non-oracle LLM result.

## Conservative Claims

- Clinical examples are synthetic, not real clinical-note evidence.
- TAB-derived legal facts are heuristic and spot-checked, not expert legal annotation.
- Audited TCFR uses an LLM judge; the fixed audit and GPT-5.5 audit are supporting checks, not ground truth.
- The deterministic safety/repair layer accounts for the measured CSG ablation gains.
- The method is not formal anonymization, k-anonymity, differential privacy, or compliance proof.
- The fixed audit and manual-agreement report are single-author/manual-style evidence; the second-annotator packet is prepared but not completed.

## Next Steps

1. Have a second annotator complete `results/second_annotator_form_n150.csv`.
2. If expanding beyond n150, rerun all n150 support artifacts and the verifier.
3. If changing legal policy from strict to generalized claims, rerun the residual-QI audit and update the paper caveats.
