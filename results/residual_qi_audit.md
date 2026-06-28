# Residual CSG QI Audit

Manual-style audit of the remaining Critical Span Guard quasi-identifier rows after deterministic safety, legal-Article, medication, case-label, and detention-regime repair.

Residual rows: 2/50. Direct identifier leaks: 0/50.

## Summary

| Example | QI risk | QI spans | Audit class | Paper interpretation |
|---|---:|---|---|---|
| `legal_0005` | 3 | Northern Ireland; 1976 | task-critical overlap | The retained quasi-identifier text is inside the current gold task-critical fact, so removing it would change the annotated answer unless a domain-aware generalization is added. |
| `legal_0025` | 1 | resisting the exercise of official authority | task-critical overlap | The retained quasi-identifier text is inside the current gold task-critical fact, so removing it would change the annotated answer unless a domain-aware generalization is added. |

## Method Comparison

| Example | Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Fact judge | Not-retained audited facts |
|---|---|---|---|---:|---:|---:|---|---|
| `legal_0005` | `generic_llm` | None | None | 0.667 | 0.667 | 0.667 | generalized_not_retained=1, preserved=2 | the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) ... |
| `legal_0005` | `privacy_first_llm` | None | None | 0.333 | 0.667 | 0.333 | omitted=1, preserved=2 | the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) ... |
| `legal_0005` | `critical_span_guard_extracted` | None | Northern Ireland; 1976 | 1.000 | 1.000 | 1.000 | preserved=3 | None |
| `legal_0025` | `generic_llm` | None | 23 May 2003; resisting the exercise of official authority; 4 February 1998 | 1.000 | 1.000 | 1.000 | preserved=2 | None |
| `legal_0025` | `privacy_first_llm` | None | resisting the exercise of official authority | 0.500 | 1.000 | 0.500 | preserved=2 | None |
| `legal_0025` | `critical_span_guard_extracted` | None | resisting the exercise of official authority | 1.000 | 1.000 | 1.000 | preserved=2 | None |

## Row Notes

### `legal_0005` - task-critical overlap

- Source: `TAB:test:001-60309`
- CSG QI spans: Northern Ireland; 1976
- Gold task facts: Article 6; violation; the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976
- QA answers: Article 6; violation; the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976
- Audit interpretation: The retained quasi-identifier text is inside the current gold task-critical fact, so removing it would change the annotated answer unless a domain-aware generalization is added.

CSG output:

> PROCEDURE The case originated in an application [ID] against the Country lodged with the European Commission of Human Rights (“the Commission”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by an individual, [PERSON], on [DATE]. He alleged that the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976, which was deemed conclusive evidence that the applicant’s employment was terminated for the purpose of protecting public safety and public order, operated under the terms of the 1976 Act to deny him access to a court or tribunal, in violation of Article 6 § 1.

### `legal_0025` - task-critical overlap

- Source: `TAB:train:001-81922`
- CSG QI spans: resisting the exercise of official authority
- Gold task facts: Article 4; the conduct of proceedings for the said traffic offence violated Article 4 of Protocol No. 7, given that he had been acquitted of the offence of resisting the exercise of official authority in respect of the same act
- QA answers: Article 4; the conduct of proceedings for the said traffic offence violated Article 4 of Protocol No. 7, given that he had been acquitted of the offence of resisting the exercise of official authority in respect of ...
- Audit interpretation: The retained quasi-identifier text is inside the current gold task-critical fact, so removing it would change the annotated answer unless a domain-aware generalization is added.

CSG output:

> PROCEDURE The case originated in an application [ID] against [REDACTED_COUNTRY] lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by an [REDACTED_COUNTRY] national, [REDACTED_NAME], on [REDACTED_DATE]. The applicant submitted his defence on [REDACTED_DATE], asserting in particular that the conduct of proceedings for the said traffic offence violated Article 4 of Protocol No. 7, given that he had been acquitted of the offence of resisting the exercise of official authority in respect of the same act.

## Paper Wording

Use this as evidence that the remaining CSG privacy risk is small and inspectable: 2 rows retain measured quasi-identifiers after the deterministic repair layer.
The remaining task-critical overlap cases (`legal_0005`, `legal_0025`) preserve quasi-identifying text inside the annotated legal claim itself, so removing it would change the current benchmark answer unless a domain-aware generalization is added.
Avoid claiming that every residual QI hit is inherently unavoidable. The stronger claim is that task-aware anonymization makes residual cases inspectable and separates true utility-overlap cases from policy gaps.
