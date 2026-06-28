# OpenAI n150 Expansion Audit

Generated: 2026-06-28

This report compares the previous 120-example OpenAI run with the promoted 150-example headline run. The expanded run has matching ablation, manual-audit, paper-table, and verifier support artifacts.

The expansion adds 30 examples to the previous 120: clinical=15, legal=15.

## Previous 120-Example Run

| Method | N | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|---:|
| Generic LLM | 120 | 0.183 | 1.742 | 0.818 | 0.939 | 0.892 |
| Privacy-first LLM | 120 | 0.000 | 0.600 | 0.406 | 0.542 | 0.422 |
| Critical Span Guard | 120 | 0.000 | 0.142 | 0.889 | 0.993 | 0.979 |

## Promoted 150-Example Headline Run

| Method | N | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|---:|
| Generic LLM | 150 | 0.180 | 1.733 | 0.813 | 0.938 | 0.888 |
| Privacy-first LLM | 150 | 0.000 | 0.573 | 0.398 | 0.529 | 0.414 |
| Critical Span Guard | 150 | 0.000 | 0.127 | 0.884 | 0.994 | 0.974 |

## Added 30 Examples Only

| Method | N | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|---:|
| Generic LLM | 30 | 0.167 | 1.700 | 0.794 | 0.933 | 0.872 |
| Privacy-first LLM | 30 | 0.000 | 0.467 | 0.367 | 0.478 | 0.383 |
| Critical Span Guard | 30 | 0.000 | 0.067 | 0.867 | 1.000 | 0.956 |

## Added CSG Edge Cases

| ID | Domain | Deterministic issue | Audited TCFR | Note |
|---|---|---|---:|---|
| `legal_0062` | legal | QI: Irish; failed exact QA: What core claim was raised? | 1.000 | audited facts retained |
| `legal_0063` | legal | QI: Widow's Bereavement Allowance; failed exact QA: What core claim was raised? | 1.000 | audited facts retained |
| `legal_0069` | legal | failed exact QA: What core claim was raised? | 1.000 | audited facts retained |

## Interpretation

- The expanded run preserves the qualitative result: CSG keeps zero measured direct leaks, much lower QI risk than generic prompting, and much higher utility than privacy-first prompting.
- The added slice is not a cherry-picked win: CSG has 0 direct-leak rows and 2 QI-hit rows on the added slice, with added-slice audited TCFR 1.000 and QA 0.956.
- The promoted headline reduces, but does not eliminate, the small-sample concern; any expansion beyond 150 should rerun the ablation, residual audit, qualitative audit, paper tables, and verifier.
