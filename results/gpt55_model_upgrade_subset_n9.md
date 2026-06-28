# Model-Upgrade Sanity-Check Subset

This is a bounded subset for the optional GPT-5.5 anonymization screen.
It is drawn from the existing GPT-5.5 external-audit subset so current low-cost outputs already have GPT-5.5 fact-judge labels.

## Composition

- Examples: 9.
- Mean hard score: 9.765.

| Group | Count |
|---|---:|
| screen_bucket=clinical | 3 |
| screen_bucket=hard | 3 |
| screen_bucket=legal | 3 |
| domain=clinical | 3 |
| domain=legal | 6 |

## Selection Reasons

| Reason | Count |
|---|---:|
| generic direct identifier leak | 6 |
| clinical stratified sample | 2 |
| CSG audited fact loss | 1 |
| high privacy-utility stress score | 1 |
| residual CSG QI risk | 1 |

## IDs

| Rank | ID | Domain | Screen bucket | Audit bucket | Reasons |
|---:|---|---|---|---|---|
| 1 | `legal_0016` | legal | hard | hard | CSG audited fact loss |
| 2 | `legal_0053` | legal | hard | hard | generic direct identifier leak; residual CSG QI risk |
| 3 | `legal_0037` | legal | hard | hard | generic direct identifier leak; high privacy-utility stress score |
| 4 | `clinical_0011` | clinical | clinical | clinical | generic direct identifier leak |
| 5 | `clinical_0030` | clinical | clinical | clinical | clinical stratified sample |
| 6 | `clinical_0060` | clinical | clinical | clinical | clinical stratified sample |
| 7 | `legal_0004` | legal | legal | legal | generic direct identifier leak |
| 8 | `legal_0022` | legal | legal | legal | generic direct identifier leak |
| 9 | `legal_0029` | legal | legal | legal | generic direct identifier leak |

Scope caveat: this subset is a fast screen, not a replacement for the promoted n150 headline or a full 30-example model-upgrade study.
