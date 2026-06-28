# n70 Promotion Readiness

Generated: 2026-06-27

This report documents the promoted 70-example OpenAI headline run and the caveats carried into the manuscript. It is generated from n70 artifacts only and makes no API calls.

Promotion status: **READY WITH CAVEATS**.

- n70 unique examples: 70.
- Required n70 artifacts missing: none.
- CSG direct-leak rows: 0/70.
- CSG residual QI rows: 2/70 (legal_0025, legal_0005).
- CSG audited fact-loss rows: 1/70 (legal_0016).
- CSG privacy span recall: direct 1.000, quasi 0.990, all privacy 0.993.

## n70 Main Metrics

| Method | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|
| Generic LLM | 0.186 | 1.757 | 0.805 | 0.929 | 0.867 |
| Privacy-first LLM | 0.000 | 0.586 | 0.390 | 0.514 | 0.410 |
| Critical Span Guard | 0.000 | 0.057 | 0.893 | 0.993 | 0.981 |

## Paired Effects

- Versus generic prompting: direct-leak reduction 0.186, QI-risk reduction 1.700, audited TCFR gain 0.064, QA gain 0.114.
- Versus privacy-first prompting: QI-risk reduction 0.529, exact TCFR gain 0.502, audited TCFR gain 0.479, QA gain 0.571.

## Caveats Carried In Current Headline

- CSG has 3 exact legal QA misses in n70; all are exact-phrase artifacts under the fact judge.
- `legal_0016` is the only CSG audited fact-loss row: CSG preserves the Article 8 contact-with-daughter claim but generalizes `Polish authorities` to `authorities` under strict legal-claim labeling.
- Residual QI remains concentrated in `legal_0005` and `legal_0025`, both task-critical legal-overlap cases.
- The verification prompt still does not drive the measured ablation gain; the deterministic safety/repair layer does.

## Completed Promotion Steps

- Manuscript main table, paired-delta text, ablation table, surface table, and frontier figure use the n70 artifacts.
- Paper caveats use 70-example wording, including `legal_0016` as the strict-specificity edge case.
- Recompile the paper and rerun `src/verify_submission_package.py` after any future headline change.
