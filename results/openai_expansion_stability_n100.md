# OpenAI n100 Expansion Audit

Generated: 2026-06-27

This report compares the previous 70-example OpenAI run with the promoted 100-example headline run. The expanded run has matching ablation, manual-audit, paper-table, and verifier support artifacts.

The expansion adds 30 examples to the previous 70: clinical=15, legal=15.

## Previous 70-Example Run

| Method | N | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|---:|
| Generic LLM | 70 | 0.186 | 1.757 | 0.805 | 0.929 | 0.867 |
| Privacy-first LLM | 70 | 0.000 | 0.586 | 0.390 | 0.514 | 0.410 |
| Critical Span Guard | 70 | 0.000 | 0.057 | 0.893 | 0.993 | 0.981 |

## Promoted 100-Example Headline Run

| Method | N | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|---:|
| Generic LLM | 100 | 0.190 | 1.800 | 0.823 | 0.938 | 0.892 |
| Privacy-first LLM | 100 | 0.000 | 0.630 | 0.383 | 0.510 | 0.405 |
| Critical Span Guard | 100 | 0.000 | 0.090 | 0.898 | 0.995 | 0.982 |

## Added 30 Examples Only

| Method | N | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|---:|
| Generic LLM | 30 | 0.200 | 1.900 | 0.867 | 0.961 | 0.950 |
| Privacy-first LLM | 30 | 0.000 | 0.733 | 0.367 | 0.500 | 0.394 |
| Critical Span Guard | 30 | 0.000 | 0.167 | 0.911 | 1.000 | 0.983 |

## Added CSG Edge Cases

| ID | Domain | Deterministic issue | Audited TCFR | Note |
|---|---|---|---:|---|
| `legal_0002` | legal | QI: homosexuality, homosexuals, homosexual; failed exact QA: What core claim was raised? | 1.000 | audited facts retained |
| `legal_0042` | legal | QI: Rom | 1.000 | audited facts retained |
| `legal_0046` | legal | QI: widows | 1.000 | audited facts retained |

## Interpretation

- The expanded run preserves the qualitative result: CSG keeps zero measured direct leaks, much lower QI risk than generic prompting, and much higher utility than privacy-first prompting.
- The added slice is not a cherry-picked win: CSG has 0 direct-leak rows and 3 QI-hit rows on the added slice, with added-slice audited TCFR 1.000 and QA 0.983.
- The promoted headline reduces, but does not eliminate, the small-sample concern; any expansion beyond 100 should rerun the ablation, residual audit, qualitative audit, paper tables, and verifier.
