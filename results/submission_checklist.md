# Submission Checklist

Date: 2026-06-28

## Current Headline

Promoted non-oracle 150-example result:

| Method | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|
| Generic LLM | 0.180 | 1.733 | 0.813 | 0.938 | 0.888 |
| Privacy-first LLM | 0.000 | 0.573 | 0.398 | 0.529 | 0.414 |
| Critical Span Guard | 0.000 | 0.127 | 0.884 | 0.994 | 0.974 |

Best concise claim: CSG improves the observed privacy-utility tradeoff in this controlled 150-example clinical/legal run, mainly by reducing privacy risk relative to generic prompting and preserving utility relative to privacy-first prompting. The caveats are three strict-specificity audited-loss rows (`clinical_0055`, `clinical_0059`, `legal_0016`) and eleven residual legal QI rows.

External audit addendum: GPT-5.5 is stricter on a 60-example stratified subset but preserves the utility ranking (`critical_span_guard_extracted` 0.917 audited TCFR, `generic_llm` 0.875, `privacy_first_llm` 0.483). On the 20 hardest rows, GPT-5.5 adversarial privacy flags show the residual frontier: generic has many direct flags, privacy-first has lower privacy severity but much lower utility, and CSG has one direct-flagged exact-date row plus many task-overlap linkage flags.

The current manuscript is `paper/main.tex`; `paper/main.pdf` compiles to 10 pages.

## Claim-to-Artifact Map

| Claim | Primary artifact | Supporting artifact |
|---|---|---|
| CSG gives the best current privacy-utility tradeoff | `results/openai_combined_results_n150.md` | `results/paper_ready_tables_n150.md` |
| n100-to-n150 expansion preserves the qualitative pattern | `results/openai_expansion_stability_n150.md` | `results/openai_api_usage_n150.md` |
| GPT-5.5 fact audit preserves the utility ranking under a stricter judge | `results/gpt55_external_audit_comparison_fact60_privacyhard20.md` | `data/processed/gpt55_fact_judgments_stratified60.jsonl` |
| GPT-5.5 adversarial privacy audit exposes the residual frontier | `results/gpt55_privacy_judge_results_hard20.md` | `data/processed/gpt55_privacy_judgments_hard20.jsonl` |
| Privacy-utility frontier figure is synchronized | `paper/generated_privacy_utility_frontier.tex` | `results/openai_summary_n150.json` |
| Safety/repair layer accounts for measured CSG gains | `results/csg_ablation_table_n150.md` | `data/processed/csg_ablation_judgments_n150.jsonl` |
| Paired examples show privacy gains over generic and utility gains over privacy-first | `results/paired_delta_report_n150.md` | `results/paired_delta_report_n150.json` |
| Span-level privacy recall supports the privacy claim | `results/privacy_span_recall_audit_n150.md` | `data/processed/openai_judgments_n150.jsonl` |
| Surface overlap is an inadequate utility/privacy proxy | `results/surface_metric_audit_n150.md` | `paper/generated_surface_failure_scatter_n150.tex` |
| Remaining CSG privacy risk is small and inspectable | `results/residual_qi_audit_n150.md` | `results/fixed_sample_manual_audit_n150.md` |
| Fixed-subset audit and blinded-packet readiness are synchronized | `results/manual_audit_agreement_n150.md` | `results/manual_audit_agreement_n150.json` |
| Blinded packet is ready for a second annotator | `results/second_annotator_rubric_n150.md` | `data/processed/second_annotator_packet_n150.jsonl` |
| No-API local n200 diagnostic preserves the local/oracle frontier | `results/local_n200_diagnostic_report.md` | `results/local_n200_diagnostic_report.json` |
| Threat model and release policy are bounded explicitly | `results/threat_model_report.md` | `results/artifact_data_statement.md` |
| Paper package consistency is machine-checked | `results/submission_verification.md` | `src/verify_submission_package.py` |

## Rebuild Commands

Promoted n150 cache-only rebuild:

```bash
conda run -n preserv_anony python src/run_openai_methods.py \
  --benchmark data/processed/benchmark_n150_llm.jsonl \
  --model gpt-4.1-nano \
  --max-examples 150 \
  --seed 21 \
  --methods generic_llm privacy_first_llm critical_span_guard_extracted \
  --out data/processed/openai_anonymized_outputs_n150.jsonl \
  --cache-only
conda run -n preserv_anony python src/compute_metrics.py \
  --benchmark data/processed/benchmark_n150_llm.jsonl \
  --outputs data/processed/openai_anonymized_outputs_n150.jsonl \
  --scored data/processed/openai_judgments_n150.jsonl \
  --summary results/openai_summary_n150.json \
  --report results/openai_results_n150.md
conda run -n preserv_anony python src/run_fact_judge.py \
  --benchmark data/processed/benchmark_n150_llm.jsonl \
  --model gpt-4.1-nano \
  --outputs data/processed/openai_anonymized_outputs_n150.jsonl \
  --out data/processed/openai_fact_judgments_n150.jsonl \
  --summary results/openai_fact_judge_summary_n150.json \
  --report results/openai_fact_judge_results_n150.md \
  --cache-only
conda run -n preserv_anony python src/run_fact_judge.py \
  --benchmark data/processed/benchmark_n150_llm.jsonl \
  --model gpt-5.5 \
  --outputs data/processed/openai_anonymized_outputs_n150.jsonl \
  --ids-file data/processed/gpt55_audit_ids_60.txt \
  --out data/processed/gpt55_fact_judgments_stratified60.jsonl \
  --summary results/gpt55_fact_judge_summary_stratified60.json \
  --report results/gpt55_fact_judge_results_stratified60.md \
  --max-tokens 1600 \
  --cache-only
conda run -n preserv_anony python src/run_privacy_judge.py \
  --model gpt-5.5 \
  --ids-file data/processed/gpt55_privacy_ids_hard20.txt \
  --out data/processed/gpt55_privacy_judgments_hard20.jsonl \
  --summary results/gpt55_privacy_judge_summary_hard20.json \
  --report results/gpt55_privacy_judge_results_hard20.md \
  --max-tokens 1800 \
  --cache-only
conda run -n preserv_anony python src/make_external_audit_report.py \
  --privacy-judgments data/processed/gpt55_privacy_judgments_hard20.jsonl \
  --summary results/gpt55_external_audit_comparison_fact60_privacyhard20.json \
  --report results/gpt55_external_audit_comparison_fact60_privacyhard20.md \
  --model gpt-5.5
conda run -n preserv_anony python src/make_external_audit_usage_report.py
conda run -n preserv_anony python src/make_manual_audit_agreement_report.py
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
