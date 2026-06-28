# OpenAI n120 Expansion Audit

Generated: 2026-06-28

This report compares the previous 100-example OpenAI run with the promoted 120-example headline run. The expanded run has matching ablation, manual-audit, paper-table, and verifier support artifacts.

The expansion adds 20 examples to the previous 100: clinical=10, legal=10.

## Previous 100-Example Run

| Method | N | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|---:|
| Generic LLM | 100 | 0.190 | 1.800 | 0.823 | 0.938 | 0.892 |
| Privacy-first LLM | 100 | 0.000 | 0.630 | 0.383 | 0.510 | 0.405 |
| Critical Span Guard | 100 | 0.000 | 0.090 | 0.898 | 0.995 | 0.982 |

## Promoted 120-Example Headline Run

| Method | N | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|---:|
| Generic LLM | 120 | 0.183 | 1.742 | 0.818 | 0.939 | 0.892 |
| Privacy-first LLM | 120 | 0.000 | 0.600 | 0.406 | 0.542 | 0.422 |
| Critical Span Guard | 120 | 0.000 | 0.142 | 0.889 | 0.993 | 0.979 |

## Added 20 Examples Only

| Method | N | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|---:|
| Generic LLM | 20 | 0.150 | 1.450 | 0.792 | 0.942 | 0.892 |
| Privacy-first LLM | 20 | 0.000 | 0.450 | 0.517 | 0.700 | 0.508 |
| Critical Span Guard | 20 | 0.000 | 0.400 | 0.842 | 0.983 | 0.967 |

## Added CSG Edge Cases

| ID | Domain | Deterministic issue | Audited TCFR | Note |
|---|---|---|---:|---|
| `clinical_0055` | clinical | none | 0.833 | generalized_but_acceptable: CT angiography showed a segmental pulmonary embolism; generalized_but_acceptable: 69-year-old |
| `clinical_0059` | clinical | none | 0.833 | omitted: 18 hours of periumbilical pain that migrated to the right lower quadrant; generalized_but_acceptable: 29-year-old |
| `legal_0053` | legal | QI: 14 years old | 1.000 | audited facts retained |
| `legal_0054` | legal | QI: sister, sister’s, sister’, four votes to three; failed exact QA: What core claim was raised? | 1.000 | audited facts retained |
| `legal_0055` | legal | QI: participate in a labour market policy programme. | 1.000 | audited facts retained |
| `legal_0056` | legal | QI: British, 10 September 2009, 14 May 2009; failed exact QA: What core claim was raised? | 1.000 | audited facts retained |

## Interpretation

- The expanded run preserves the qualitative result: CSG keeps zero measured direct leaks, much lower QI risk than generic prompting, and much higher utility than privacy-first prompting.
- The added slice is not a cherry-picked win: CSG has 0 direct-leak rows and 4 QI-hit rows on the added slice, with added-slice audited TCFR 0.983 and QA 0.967.
- The promoted headline reduces, but does not eliminate, the small-sample concern; any expansion beyond 120 should rerun the ablation, residual audit, qualitative audit, paper tables, and verifier.
