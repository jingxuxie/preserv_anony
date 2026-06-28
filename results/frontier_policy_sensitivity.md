# Frontier Policy Sensitivity

Date: 2026-06-28

This note records the current policy boundary for the eleven residual Critical Span Guard quasi-identifier rows in the promoted n150 run: `legal_0002`, `legal_0005`, `legal_0025`, `legal_0042`, `legal_0046`, `legal_0053`, `legal_0054`, `legal_0055`, `legal_0056`, `legal_0062`, and `legal_0063`.

## Current Strict Policy

The benchmark treats exact legal claim, statute, offence, protected-status, age, relationship, and jurisdictional specificity as task-critical unless the annotation explicitly allows generalization.

| Example | Audit class | Residual QI span(s) | Current interpretation |
|---|---|---|---|
| `legal_0002` | task-critical overlap | `homosexuality`; `homosexuals`; `homosexual` | The protected-status terms are central to the Article 8 / Article 14 discharge claim. |
| `legal_0005` | task-critical overlap | `Northern Ireland`; `1976` | The spans are inside the section 42 Fair Employment statute name. |
| `legal_0025` | task-critical overlap | `resisting the exercise of official authority` | The offence description is part of the same-act acquittal claim. |
| `legal_0046` | task-critical overlap | `widows` | The benefit category is inside the annotated benefits-discrimination claim. |
| `legal_0053` | task-critical overlap | `14 years old` | The age is part of the Article 8 claim about personal-integrity remedies. |
| `legal_0063` | task-critical overlap | `Widow's Bereavement Allowance` | The benefits category is inside the annotated Article 14 discrimination claim. |
| `legal_0042` | frontier candidate | `Rom` | Manual policy review is needed before deciding whether to generalize protected-status context. |
| `legal_0054` | frontier candidate | `sister`; `four votes to three` | Relationship and vote-count detail may be useful legal context but may be generalized under a stricter release policy. |
| `legal_0055` | frontier candidate | `participate in a labour market policy programme` | The programme detail overlaps with the access-to-court claim but could be generalized. |
| `legal_0056` | frontier candidate | `British`; exact dates | Jurisdiction and dates may be generalized if the utility target tolerates less specificity. |
| `legal_0062` | frontier candidate | `Irish` | Nationality remains in procedure context and may be generalized under a stricter release policy. |

Strict-policy headline:

- CSG has zero direct leaks and residual QI risk on 11/150 rows.
- Six residual cases are clear task-critical overlaps; five are frontier candidates requiring policy review.
- This supports a privacy-utility frontier claim, not a claim that every residual QI hit is technically unavoidable.

## Generalized-Claim Alternative

A more privacy-aggressive legal release policy could allow domain-aware generalized claim annotations. That would likely lower measured QI risk, but it would also change the utility target by removing statute, jurisdiction, protected-status, relationship, age, or event-detail specificity.

## Recommendation

Keep the strict annotations for the headline result and use `legal_0005` plus one added-row candidate such as `legal_0062`, `legal_0054`, or `legal_0056` to illustrate the frontier. Mention the 11/150 residual audit in limitations and avoid presenting residual QI as solved.

Paper-safe wording:

- "The remaining CSG QI hits are not direct-identifier failures. They occur where protected-status, statute, offence, relationship, age, jurisdiction, or event-detail specificity overlaps with the annotated legal claim."
- "A more privacy-aggressive release policy could generalize these claims, but that changes the downstream utility target."
- "We therefore report the strict-policy result and treat the eleven residual rows as audit targets that expose the privacy-utility frontier."

Avoid:

- "CSG reaches zero quasi-identifier risk." It does not under the strict current benchmark.
- "The residual QI hits are unavoidable." Some are avoidable under a more generalized task definition, but at a utility cost.
- "Legal specificity should always be preserved." The right policy depends on the downstream legal task and release risk.
