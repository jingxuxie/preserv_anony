# Workshop Paper Draft

This directory contains a COLM 2026 submission-shell LaTeX draft built from the current fast-iteration evidence.

Main file:

```bash
paper/main.tex
```

Compile from this directory:

```bash
cd paper
latexmk -pdf main.tex
```

Evidence sources:

- `results/openai_combined_results.md`
- `results/openai_combined_results_n70.md`
- `results/openai_expansion_stability_n70.md`
- `results/n70_promotion_readiness.md`
- `results/paper_ready_tables_n70.md`
- `paper/generated_privacy_utility_frontier_n70.tex`
- `results/benchmark_quality_audit.md`
- `paper/generated_privacy_utility_frontier.tex`
- `results/prompt_method_appendix.md`
- `results/csg_ablation_table.md`
- `results/surface_metric_audit.md`
- `results/paired_delta_report.md`
- `results/privacy_span_recall_audit_n70.md`
- `results/robustness_report.md`
- `results/baseline_bridge_report.md`
- `results/residual_qi_audit.md`
- `results/frontier_policy_sensitivity.md`
- `results/threat_model_report.md`
- `results/manual_audit_decisions.md`
- `results/manual_audit_package.md`
- `results/final_qualitative_audit.md`
- `results/artifact_data_statement.md`
- `results/reviewer_risk_register.md`
- `results/submission_verification.md`

Template support:

- `colm2026_conference.sty`
- `inconsolata.sty`
- `references.bib`

Claim discipline:

- The clinical split is synthetic.
- The promoted 70-example LLM run is non-oracle and cached.
- The earlier 50-example OpenAI run is retained as an audit trail.
- The n70 ablation, residual audit, surface audit, legal QA audit, qualitative audit, paper-ready tables, and promotion-readiness report are the current headline support artifacts; the manuscript carries the `legal_0016` caveat.
- The robustness slice is diagnostic, not the headline result.
- Local regex, Presidio, and oracle baselines are diagnostic anchors, not the main non-oracle LLM comparison.
- The verifier prompt did not improve deterministic metrics in the cached ablation; the measured CSG gain comes from the deterministic safety/repair layer.
- Data provenance and release caveats are summarized in `results/artifact_data_statement.md`.
- Threat-model and release-policy boundaries are summarized in `results/threat_model_report.md`.
- Span-level privacy recall is summarized in `results/privacy_span_recall_audit_n70.md`.
- Benchmark schema and integrity checks are summarized in `results/benchmark_quality_audit.md`.
- Prompt templates and the non-oracle method boundary are summarized in `results/prompt_method_appendix.md`.
- Reviewer-facing claim boundaries are summarized in `results/reviewer_risk_register.md`.
- Package consistency checks are summarized in `results/submission_verification.md`.
- No formal anonymization, legal compliance, k-anonymity, or differential-privacy claim is made.
