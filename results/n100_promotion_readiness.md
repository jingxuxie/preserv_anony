# n100 Promotion Readiness

Generated: 2026-06-27

This report documents the promoted 100-example OpenAI headline run and the caveats carried into the manuscript. It is generated from n100 artifacts only and makes no API calls.

Promotion status: **READY WITH CAVEATS**.

- n100 unique examples: 100.
- Required n100 artifacts missing: none.
- CSG direct-leak rows: 0/100.
- CSG residual QI rows: 5/100 (legal_0025, legal_0005, legal_0046, legal_0002, legal_0042).
- CSG audited fact-loss rows: 1/100 (legal_0016).
- CSG privacy span recall: direct 1.000, quasi 0.978, all privacy 0.987.

## n100 Main Metrics

| Method | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|
| Generic LLM | 0.190 | 1.800 | 0.823 | 0.938 | 0.892 |
| Privacy-first LLM | 0.000 | 0.630 | 0.383 | 0.510 | 0.405 |
| Critical Span Guard | 0.000 | 0.090 | 0.898 | 0.995 | 0.982 |

## Paired Effects

- Versus generic prompting: direct-leak reduction 0.190 [0.110-0.270], QI-risk reduction 1.710 [1.470-1.930], audited TCFR gain 0.057 [0.035-0.082], QA gain 0.090 [0.050-0.130].
- Versus privacy-first prompting: QI-risk reduction 0.540 [0.350-0.740], exact TCFR gain 0.515 [0.453-0.578], audited TCFR gain 0.485 [0.425-0.545], QA gain 0.577 [0.505-0.650].

## Caveats Carried In Current Headline

- CSG has 4 exact legal QA misses in n100; all are exact-phrase artifacts under the fact judge.
- `legal_0016` is the only CSG audited fact-loss row: CSG preserves the Article 8 contact-with-daughter claim but generalizes `Polish authorities` to `authorities` under strict legal-claim labeling.
- Residual QI remains concentrated in five legal rows: `legal_0002`, `legal_0005`, `legal_0025`, `legal_0042`, and `legal_0046`.
- The verification prompt still does not drive the measured ablation gain; the deterministic safety/repair layer does.

## Completed Promotion Steps

- Manuscript main table, paired-delta text, ablation table, surface table, and frontier figure use the n100 artifacts.
- Paper caveats use 100-example wording, including `legal_0016` as the strict-specificity edge case and five residual CSG QI rows.
- Recompile the paper and rerun `src/verify_submission_package.py` after any future headline change.
