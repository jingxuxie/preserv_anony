# Utility-Preserving Anonymization Experiments

Fast scaffold and paper artifacts for `utility_preserving_anonymization_workshop_plan.md`.

## Current Headline

The promoted non-oracle OpenAI run is `n150`: 75 synthetic clinical vignettes and 75 TAB-derived legal snippets.

| Method | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|
| Generic LLM | 0.180 | 1.733 | 0.813 | 0.938 | 0.888 |
| Privacy-first LLM | 0.000 | 0.573 | 0.398 | 0.529 | 0.414 |
| Critical Span Guard | 0.000 | 0.127 | 0.884 | 0.994 | 0.974 |

The compiled draft is `paper/main.pdf` and is 10 pages. The package is machine-checked by `src/verify_submission_package.py`.

## Key Artifacts

- `paper/main.tex`, `paper/main.pdf`
- `results/openai_combined_results_n150.md`
- `results/csg_ablation_table_n150.md`
- `results/paired_delta_report_n150.md`
- `results/privacy_span_recall_audit_n150.md`
- `results/residual_qi_audit_n150.md`
- `results/surface_metric_audit_n150.md`
- `results/fixed_sample_manual_audit_n150.md`
- `results/manual_audit_agreement_n150.md`
- `data/processed/second_annotator_packet_n150.jsonl`
- `results/openai_api_usage_n150.md`
- `results/gpt55_external_audit_comparison_fact60_privacyhard20.md`
- `results/gpt55_fact_judge_results_stratified60.md`
- `results/gpt55_privacy_judge_results_hard20.md`
- `results/gpt55_external_audit_usage_report.md`
- `results/local_n200_diagnostic_report.md`
- `results/submission_verification.md`
- `results/paper_claim_package.md`
- `results/submission_checklist.md`

## Cache-Only Rebuild

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
conda run -n preserv_anony python src/make_manual_audit_agreement_report.py
conda run -n preserv_anony python src/verify_submission_package.py
```

## Paper Compile

```bash
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

## Claim Boundaries

- Clinical rows are synthetic controlled vignettes, not real clinical-note evidence.
- TAB-derived legal facts are heuristic and spot-checked, not expert legal annotation.
- The n200 local run is a no-API local/oracle diagnostic, not a non-oracle LLM result.
- Audited TCFR is judge-assisted evidence, not ground truth.
- This is not a formal anonymization, compliance, or adversarial privacy guarantee.
