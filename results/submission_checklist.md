# Submission Checklist

Date: 2026-06-28

## Current Headline

Promoted non-oracle 120-example result:

| Method | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|
| Generic LLM | 0.183 | 1.742 | 0.818 | 0.939 | 0.892 |
| Privacy-first LLM | 0.000 | 0.600 | 0.406 | 0.542 | 0.422 |
| Critical Span Guard | 0.000 | 0.142 | 0.889 | 0.993 | 0.979 |

Best concise claim: CSG improves the observed privacy-utility tradeoff in this controlled 120-example clinical/legal run, mainly by reducing privacy risk relative to generic prompting and preserving utility relative to privacy-first prompting. The caveats are three strict-specificity audited-loss rows (`clinical_0055`, `clinical_0059`, `legal_0016`) and nine residual legal QI rows.

The current manuscript is `paper/main.tex`; `paper/main.pdf` compiles to 6 pages.

## Claim-to-Artifact Map

| Claim | Primary artifact | Supporting artifact |
|---|---|---|
| CSG gives the best current privacy-utility tradeoff | `results/openai_combined_results_n120.md` | `results/paper_ready_tables_n120.md` |
| n100-to-n120 expansion preserves the qualitative pattern | `results/openai_expansion_stability_n120.md` | `results/openai_api_usage_n120.md` |
| Privacy-utility frontier figure is synchronized | `paper/generated_privacy_utility_frontier.tex` | `results/openai_summary_n120.json` |
| Safety/repair layer accounts for measured CSG gains | `results/csg_ablation_table_n120.md` | `data/processed/csg_ablation_judgments_n120.jsonl` |
| Paired examples show privacy gains over generic and utility gains over privacy-first | `results/paired_delta_report_n120.md` | `results/paired_delta_report_n120.json` |
| Span-level privacy recall supports the privacy claim | `results/privacy_span_recall_audit_n120.md` | `data/processed/openai_judgments_n120.jsonl` |
| Surface overlap is an inadequate utility/privacy proxy | `results/surface_metric_audit_n120.md` | `paper/generated_surface_failure_scatter.tex` |
| Remaining CSG privacy risk is small and inspectable | `results/residual_qi_audit_n120.md` | `results/fixed_sample_manual_audit_n120.md` |
| Blinded packet is ready for a second annotator | `results/second_annotator_rubric_n120.md` | `data/processed/second_annotator_packet_n120.jsonl` |
| No-API local n200 diagnostic preserves the local/oracle frontier | `results/local_n200_diagnostic_report.md` | `results/local_n200_diagnostic_report.json` |
| Threat model and release policy are bounded explicitly | `results/threat_model_report.md` | `results/artifact_data_statement.md` |
| Paper package consistency is machine-checked | `results/submission_verification.md` | `src/verify_submission_package.py` |

## Rebuild Commands

Promoted n120 cache-only rebuild:

```bash
conda run -n preserv_anony python src/run_openai_methods.py \
  --benchmark data/processed/benchmark_n120_llm.jsonl \
  --model gpt-4.1-nano \
  --max-examples 120 \
  --seed 21 \
  --methods generic_llm privacy_first_llm critical_span_guard_extracted \
  --out data/processed/openai_anonymized_outputs_n120.jsonl \
  --cache-only
conda run -n preserv_anony python src/compute_metrics.py \
  --benchmark data/processed/benchmark_n120_llm.jsonl \
  --outputs data/processed/openai_anonymized_outputs_n120.jsonl \
  --scored data/processed/openai_judgments_n120.jsonl \
  --summary results/openai_summary_n120.json \
  --report results/openai_results_n120.md
conda run -n preserv_anony python src/run_fact_judge.py \
  --benchmark data/processed/benchmark_n120_llm.jsonl \
  --model gpt-4.1-nano \
  --outputs data/processed/openai_anonymized_outputs_n120.jsonl \
  --out data/processed/openai_fact_judgments_n120.jsonl \
  --summary results/openai_fact_judge_summary_n120.json \
  --report results/openai_fact_judge_results_n120.md \
  --cache-only
conda run -n preserv_anony python src/verify_submission_package.py
```

Paper compile:

```bash
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

## Claims To Avoid

- Do not claim real clinical-note coverage.
- Do not claim formal anonymization or regulatory compliance.
- Do not claim the verifier prompt caused the gains.
- Do not report oracle methods as deployable systems.
- Do not present the local n200 diagnostic as a non-oracle LLM result.
- Do not present the fixed audit as completed independent annotation.
