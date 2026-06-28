# OpenAI n70 Expansion Audit

Generated: 2026-06-27

This report compares the earlier 50-example OpenAI run with the promoted 70-example headline run. The expanded run now has matching ablation, manual-audit, paper-table, and verifier support artifacts.

The expansion adds 20 examples to the original 50: clinical=10, legal=10.

## Earlier 50-Example Run

| Method | N | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|---:|
| Generic LLM | 50 | 0.160 | 1.740 | 0.817 | 0.940 | 0.890 |
| Privacy-first LLM | 50 | 0.000 | 0.660 | 0.430 | 0.567 | 0.440 |
| Critical Span Guard | 50 | 0.000 | 0.080 | 0.897 | 1.000 | 0.990 |

## Promoted 70-Example Headline Run

| Method | N | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|---:|
| Generic LLM | 70 | 0.186 | 1.757 | 0.805 | 0.929 | 0.867 |
| Privacy-first LLM | 70 | 0.000 | 0.586 | 0.390 | 0.514 | 0.410 |
| Critical Span Guard | 70 | 0.000 | 0.057 | 0.893 | 0.993 | 0.981 |

## Added 20 Examples Only

| Method | N | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---:|---:|---:|---:|---:|---:|
| Generic LLM | 20 | 0.250 | 1.800 | 0.775 | 0.900 | 0.808 |
| Privacy-first LLM | 20 | 0.000 | 0.400 | 0.292 | 0.383 | 0.333 |
| Critical Span Guard | 20 | 0.000 | 0.000 | 0.883 | 0.975 | 0.958 |

## Added CSG Edge Cases

| ID | Domain | Deterministic issue | Audited TCFR | Note |
|---|---|---|---:|---|
| `legal_0014` | legal | failed exact QA: What core claim was raised? | 1.000 | audited facts retained |
| `legal_0016` | legal | none | 0.500 | generalized_but_acceptable: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which ha... |
| `legal_0026` | legal | failed exact QA: What core claim was raised? | 1.000 | audited facts retained |

## Interpretation

- The expanded run preserves the qualitative result: CSG keeps zero measured direct leaks, much lower QI risk than generic prompting, and much higher utility than privacy-first prompting.
- The added 20 examples are not cherry-picked wins: CSG has zero direct leaks and zero QI hits on the added slice, while exact QA misses remain concentrated in legal wording shifts.
- The one added audited CSG loss is `legal_0016`, where the output preserves the Article 8 contact-with-daughter claim but generalizes `Polish authorities` to `authorities`; the strict gold legal claim currently marks that specificity as non-generalizable.
- The promoted headline reduces, but does not eliminate, the small-sample concern; any expansion beyond 70 should rerun the ablation, residual audit, qualitative audit, paper tables, and verifier.
