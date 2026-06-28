# GPT-5.5 Model-Upgrade Anonymization Screen

Generated: 2026-06-28

Bounded GPT-5.5 anonymization sanity check on a 9-example stress subset. Not a replacement for the promoted n150 headline or a full 30-example model-upgrade study.

Cold-run API-call guardrail: 45 anonymization calls plus 27 upgraded-output fact-judge calls (72 total).
Current-output baseline fact labels reuse the existing GPT-5.5 external fact audit.
Successful cached provider usage for this pilot: 72 rows, 48,289 prompt tokens, 33,979 completion tokens, 14,742 reasoning tokens, 82,268 total tokens.
Run note: an earlier too-small completion cap produced 3 uncached failed JSON attempts before the successful rerun.

## Overall

| Method | Current direct | Upgraded direct | Current QI | Upgraded QI | Current audited TCFR | Upgraded audited TCFR | Delta audited TCFR |
|---|---:|---:|---:|---:|---:|---:|---:|
| Generic LLM | 0.667 | 0.000 | 2.778 | 0.222 | 0.852 | 0.815 | -0.037 |
| Privacy-first LLM | 0.000 | 0.000 | 0.222 | 0.000 | 0.389 | 0.333 | -0.056 |
| Critical Span Guard | 0.000 | 0.000 | 0.111 | 0.556 | 0.870 | 0.852 | -0.019 |

## Exact-Metric Utility

| Method | Current exact TCFR | Upgraded exact TCFR | Current QA | Upgraded QA |
|---|---:|---:|---:|---:|
| Generic LLM | 0.796 | 0.833 | 0.889 | 0.907 |
| Privacy-first LLM | 0.389 | 0.333 | 0.370 | 0.463 |
| Critical Span Guard | 0.889 | 0.833 | 1.000 | 0.889 |

## Interpretation

- Stronger generic prompting removes measured direct leaks on this subset; larger validation is needed before changing the main claim.
- Privacy-first prompting still preserves less audited task-critical content than CSG under the GPT-5.5 judge.
- CSG remains on the best observed privacy-utility corner for this bounded stronger-model screen.
- Treat this as a speed screen only; the planned full model-upgrade check remains 30 examples.

## Subset

| Rank | ID | Domain | Screen bucket | Reasons |
|---:|---|---|---|---|
| 1 | `legal_0016` | legal | hard | CSG audited fact loss |
| 2 | `legal_0053` | legal | hard | generic direct identifier leak; residual CSG QI risk |
| 3 | `legal_0037` | legal | hard | generic direct identifier leak; high privacy-utility stress score |
| 4 | `clinical_0011` | clinical | clinical | generic direct identifier leak |
| 5 | `clinical_0030` | clinical | clinical | clinical stratified sample |
| 6 | `clinical_0060` | clinical | clinical | clinical stratified sample |
| 7 | `legal_0004` | legal | legal | generic direct identifier leak |
| 8 | `legal_0022` | legal | legal | generic direct identifier leak |
| 9 | `legal_0029` | legal | legal | generic direct identifier leak |

Caveat: this is a deliberately small stress subset. Do not promote it as a model-scaling result without the planned 30-example follow-up.
