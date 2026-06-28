# Artifact and Data Statement

Generated: 2026-06-28

This statement summarizes the current data provenance, cached model artifacts, and release caveats for the utility-preserving anonymization workshop package.

## Data Inventory

| Split | Rows | Domains | Sources | Direct spans | Quasi spans | Avg task facts | Avg QA pairs |
|---|---:|---|---|---:|---:|---:|---:|
| Main benchmark | 100 | clinical=50, legal=50 | TAB ECHR dev split=6, TAB ECHR test split=6, TAB ECHR train split=38, synthetic clinical templates=50 | 459 | 291 | 4.09 | 2.09 |
| Robustness stress slice | 12 | clinical=6, legal=6 | handwritten diagnostics | 45 | 32 | 4.17 | 2.50 |
| Local n200 diagnostic benchmark | 200 | clinical=100, legal=100 | TAB ECHR dev split=11, TAB ECHR test split=16, TAB ECHR train split=73, synthetic clinical templates=100 | 913 | 634 | 4.09 | 2.09 |
| OpenAI n150 promoted benchmark | 150 | clinical=75, legal=75 | TAB ECHR dev split=8, TAB ECHR test split=9, TAB ECHR train split=58, synthetic clinical templates=75 | 684 | 444 | 4.10 | 2.10 |

## Provenance

- Clinical examples are synthetic vignettes generated from local templates. They are designed to contain controlled direct identifiers, quasi-identifiers, task-critical clinical facts, and QA targets; they are not real clinical notes and should not be described as real PHI.
- Legal examples are public ECHR snippets sampled from the Text Anonymization Benchmark clone at `data/raw/text-anonymisation-benchmark`. The local raw clone is present: `yes`; license file present: `yes`.
- The robustness slice is handwritten and diagnostic. It intentionally includes cases where sensitive or quasi-identifying content is also downstream-task-critical.

## Cached Model Artifacts

| Method | Output rows | Deterministic judgment rows | Fact-judge rows | Model(s) |
|---|---:|---:|---:|---|
| Generic LLM | 150 | 150 | 150 | gpt-4.1-nano (150) |
| Privacy-first LLM | 150 | 150 | 150 | gpt-4.1-nano (150) |
| Critical Span Guard | 150 | 150 | 150 | gpt-4.1-nano (150) |

- Promoted 150-example headline run: 450 output rows, 450 deterministic judgment rows, and 450 fact-judge rows.
- Earlier 100-example run retained for audit trail: 300 output rows, 300 deterministic judgment rows, and 300 fact-judge rows.
- Earlier 70-example run retained for audit trail: 210 output rows, 210 deterministic judgment rows, and 210 fact-judge rows.
- Earlier 50-example run retained for audit trail: 150 output rows, 150 deterministic judgment rows, and 150 fact-judge rows.
- OpenAI cache rows: 1349 in `data/processed/openai_cache.jsonl`.
- The current promoted 150-example non-oracle LLM run uses `gpt-4.1-nano` and three methods: generic prompting, privacy-first prompting, and Critical Span Guard with extracted privacy/fact structures.
- Separate no-API local n200 diagnostic: 200 benchmark rows, 1000 deterministic local/oracle output rows, and 1000 deterministic judgment rows. It is not the promoted non-oracle LLM headline.
- Bounded OpenAI n150 expansion usage: 450 output rows, 450 deterministic judgment rows, and 450 fact-judge rows. The n100-to-n150 provider/cache rows with exact usage and latency are in `results/openai_api_usage_n150.md`.
- Current OpenAI outputs can be rebuilt from cache without new API calls with `conda run -n preserv_anony python src/run_openai_methods.py --benchmark data/processed/benchmark_n150_llm.jsonl --model gpt-4.1-nano --max-examples 150 --seed 21 --methods generic_llm privacy_first_llm critical_span_guard_extracted --out data/processed/openai_anonymized_outputs_n150.jsonl --cache-only`.
- Fact-judge rows use gold task facts for evaluation only. They are not inputs to the non-oracle anonymizer.

## Artifact Map

| Artifact | Role |
|---|---|
| `data/processed/benchmark.jsonl` | Main controlled benchmark with text, spans, facts, and QA. |
| `data/processed/openai_anonymized_outputs.jsonl` | Cached earlier 50-example non-oracle anonymizer outputs. |
| `data/processed/openai_judgments.jsonl` | Deterministic scoring for the earlier 50-example run. |
| `data/processed/openai_fact_judgments.jsonl` | Fact-judge rows for the earlier 50-example run. |
| `data/processed/openai_anonymized_outputs_n100.jsonl` | Cached earlier 100-example anonymizer outputs retained as audit trail. |
| `data/processed/openai_judgments_n100.jsonl` | Deterministic scoring for the earlier 100-example run. |
| `data/processed/openai_fact_judgments_n100.jsonl` | Fact-judge rows for the earlier 100-example run. |
| `results/openai_combined_results_n100.md` | Combined deterministic and audited utility for the earlier 100-example run. |
| `results/openai_expansion_stability_n100.md` | Bounded expansion report comparing the 70-example run with the then-promoted 100-example run. |
| `results/n100_promotion_readiness.md` | Synthesis report documenting n100 promotion readiness and caveats. |
| `results/paired_delta_report_n100.md` | Paired CSG-vs-baseline effect sizes for the 100-example run. |
| `results/csg_ablation_table_n100.md` | Critical Span Guard stage ablation for the 100-example run. |
| `results/privacy_span_recall_audit_n100.md` | Span-level direct, quasi, and all-privacy recall audit for the 100-example run. |
| `results/surface_metric_audit_n100.md` | Surface-metric audit for the 100-example run. |
| `results/surface_failure_scatter_n100.json` | Summary counts backing the generated surface-failure scatter. |
| `paper/generated_surface_failure_scatter.tex` | Generated RQ2 scatter showing surface similarity failures. |
| `results/legal_qa_disagreement_audit_n100.md` | Legal QA exact-match audit for the 100-example run. |
| `results/residual_qi_audit_n100.md` | Residual CSG quasi-identifier audit for the 100-example run. |
| `results/final_qualitative_audit_n100.md` | Foreground and n100-edge qualitative audit for paper claims. |
| `results/fixed_sample_manual_audit_n100.md` | Fixed 30-example transparent subset audit across all non-oracle methods. |
| `results/fixed_sample_manual_audit_n100.json` | Structured labels and sample metadata for the fixed subset audit. |
| `data/processed/second_annotator_packet_n100.jsonl` | Blinded second-annotator packet for the fixed subset. |
| `results/second_annotator_rubric_n100.md` | Rubric and reconciliation plan for independent annotation. |
| `results/second_annotator_form_n100.csv` | Blank row-level form for a second annotator. |
| `results/second_annotator_answer_key_n100.json` | Separate method-code answer key for post-annotation reconciliation. |
| `results/paper_ready_tables_n100.md` | Paper-ready tables for the 100-example run. |
| `paper/generated_privacy_utility_frontier_n100.tex` | Generated PGFPlots frontier for the 100-example run. |
| `results/cost_and_cache_report_n100.md` | Cache-only reproducibility and response-slot accounting for the promoted run. |
| `results/cost_and_cache_report_n100.json` | Structured token-proxy budget and expansion projections for API planning. |
| `data/processed/benchmark_n200_local.jsonl` | No-API 200-example local/oracle diagnostic benchmark. |
| `data/processed/anonymized_outputs_n200_local.jsonl` | No-API local/oracle anonymizer outputs for the n200 diagnostic. |
| `data/processed/judgments_n200_local.jsonl` | Deterministic scoring rows for the n200 local/oracle diagnostic. |
| `results/summary_n200_local.json` | Structured local/oracle metrics for the n200 diagnostic. |
| `results/main_results_n200_local.md` | Readable local/oracle metric table for the n200 diagnostic. |
| `results/local_n200_diagnostic_report.md` | Bounded n100-to-n200 local/oracle diagnostic stability report. |
| `results/local_n200_diagnostic_report.json` | Structured n200 diagnostic counts and directional checks. |
| `data/processed/benchmark_n120_llm.jsonl` | Controlled 120-example benchmark for bounded non-oracle OpenAI expansion. |
| `data/processed/openai_anonymized_outputs_n120.jsonl` | Cached n120 non-oracle anonymizer outputs. |
| `data/processed/openai_judgments_n120.jsonl` | Deterministic scoring for the n120 non-oracle expansion. |
| `data/processed/openai_fact_judgments_n120.jsonl` | Fact-judge rows for the n120 non-oracle expansion. |
| `results/openai_combined_results_n120.md` | Prior 120-example combined deterministic and audited utility table retained as audit trail. |
| `results/openai_expansion_stability_n120.md` | n100-to-n120 expansion stability report retained as audit trail. |
| `results/openai_api_usage_n120.md` | Exact provider usage and latency for new n120 cache rows. |
| `results/openai_api_usage_n120.json` | Structured provider usage and cache-coverage data for new n120 rows. |
| `data/processed/benchmark_n150_llm.jsonl` | Controlled 150-example benchmark for the promoted non-oracle OpenAI headline. |
| `data/processed/openai_anonymized_outputs_n150.jsonl` | Cached n150 non-oracle anonymizer outputs. |
| `data/processed/openai_judgments_n150.jsonl` | Deterministic scoring for the promoted n150 non-oracle headline. |
| `data/processed/openai_fact_judgments_n150.jsonl` | Fact-judge rows for the promoted n150 non-oracle headline. |
| `results/openai_combined_results_n150.md` | Headline paper table combining deterministic and audited utility for the promoted 150-example run. |
| `results/openai_expansion_stability_n150.md` | n120-to-n150 promoted expansion stability report. |
| `results/openai_api_usage_n150.md` | Exact provider usage and latency for n100-to-n150 cache rows with stored usage. |
| `results/openai_api_usage_n150.json` | Structured provider usage and cache-coverage data for n100-to-n150 rows. |
| `results/workshop_plan_compliance_audit.md` | Mapping from the original workshop plan to current evidence and remaining gaps. |
| `data/processed/openai_anonymized_outputs_n70.jsonl` | Cached earlier 70-example anonymizer outputs retained as audit trail. |
| `results/openai_combined_results_n70.md` | Earlier 70-example combined table retained as audit trail. |
| `results/benchmark_quality_audit.md` | Schema and integrity audit for benchmark annotations. |
| `results/prompt_method_appendix.md` | Prompt hashes, non-oracle method boundary, and deterministic repair summary. |
| `paper/generated_privacy_utility_frontier.tex` | Generated PGFPlots figure for the promoted non-oracle privacy-utility frontier. |
| `results/openai_combined_results.md` | Earlier 50-example paper table retained for audit trail. |
| `results/baseline_bridge_report.md` | Diagnostic bridge between local baselines, oracles, and non-oracle LLM methods. |
| `results/csg_ablation_table.md` | Critical Span Guard stage ablation. |
| `results/residual_qi_audit.md` | Manual-style audit of remaining CSG quasi-identifier rows. |
| `results/final_qualitative_audit.md` | Foreground example audit for paper writing. |
| `results/frontier_policy_sensitivity.md` | Policy note for strict vs. generalized legal-claim handling. |
| `results/threat_model_report.md` | Bounded threat model, residual-risk table, and release-policy guidance. |
| `results/reviewer_risk_register.md` | Reviewer-facing claim-strength and overclaiming audit. |
| `results/submission_verification.md` | Machine-readable consistency check for the paper package. |
| `paper/main.tex` and `paper/main.pdf` | Current COLM-style manuscript draft and compiled PDF. |

## Release and Claim Caveats

- This package supports a controlled empirical claim about a privacy-utility tradeoff. It does not establish formal anonymization, HIPAA compliance, k-anonymity, differential privacy, or resistance to motivated re-identification.
- Public legal snippets may still contain sensitive allegations and case facts. Any public release should preserve the upstream license, cite TAB, and avoid representing the derived subset as newly anonymized legal data.
- The clinical split is safe to describe as synthetic controlled data, but its findings should not be generalized to real clinical-note deployment without additional real-note or expert-annotated evaluation.
- The stress slice and oracle methods are diagnostics, not headline deployed systems.
- The local n200 expansion is a no-API local/oracle diagnostic. Do not combine it with the promoted n150 non-oracle LLM headline table.
- The n150 OpenAI expansion is now the promoted non-oracle headline because the matching ablation, qualitative audit, paper tables, fixed audit, and verifier coverage have been regenerated; larger non-oracle runs remain future work.
