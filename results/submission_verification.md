# Submission Verification

Generated: 2026-06-28

Passed 22/22 checks.

| Check | Status | Detail |
|---|---|---|
| Required paper artifacts exist | PASS | 158 required artifacts present |
| Main result numbers match JSON summaries | PASS | all n150 main table values found in paper and combined table |
| Privacy-utility figure matches JSON summaries | PASS | figure coordinates and manuscript reference are synchronized |
| n100 expansion stability check is synchronized | PASS | n100 stability report matches JSON summaries; added CSG direct rows=0 |
| n100 promotion readiness is auditable | PASS | n100 promotion-readiness report matches row-level caveats |
| Baseline bridge values are visible | PASS | n200 diagnostic baseline values found in paper and diagnostic report |
| Surface metric audit includes TF-IDF foil | PASS | TF-IDF cosine and generated surface-failure scatter are synchronized |
| Residual CSG privacy counts match row-level judgments | PASS | direct rows=0/150, qi rows=11/150 |
| Privacy span recall audit matches row-level judgments | PASS | CSG direct span leaks=0 and quasi-leak rows=11; report values match n150 summary |
| PDF page count is documented | PASS | paper/main.pdf has 10 pages |
| LaTeX log has no critical errors | PASS | no critical patterns found |
| Reviewer-sensitive caveats are present | PASS | all required caveats found |
| Benchmark quality audit passes | PASS | schema and containment checks passed |
| Prompt appendix drift check passes | PASS | prompt files match runner constants and method boundary is documented |
| Threat model is explicit and bounded | PASS | threat model and out-of-scope privacy claims are documented |
| Local n200 diagnostic expansion is bounded and synchronized | PASS | n200 no-API diagnostic has 200 examples, 1000 method rows, stable local/oracle frontier, and explicit n150-headline boundary |
| OpenAI n150 headline expansion is bounded and cached | PASS | n150 headline has 150 examples, stable non-oracle pattern, 1200/1200 cached slots, and exact usage for 400 n100-to-n150 cache rows |
| n150 full audit bundle is promotable with caveats | PASS | n150 ablation, residual-QI audit, span recall, paired deltas, fixed audit, and blinded packet are synchronized |
| GPT-5.5 external audit bundle is synchronized | PASS | 60-id fact audit, hard20 privacy audit, comparison report, usage report, and manuscript/claim text are synchronized |
| Fixed-sample manual audit covers planned subset | PASS | fixed 30-example audit covers 90 method rows, all caveat ids, and expected CSG caveat counts |
| Second-annotator packet is blinded and complete | PASS | blinded second-annotator packet has 30 examples, 90 variant rows, complete answer key, and no method-label leakage |
| Plan compliance and cache-cost audits are current | PASS | cost/cache report includes cache coverage, token-proxy budget, expansion projections, and remaining gaps |
