# Residual CSG QI Audit

Manual-style audit of the remaining Critical Span Guard quasi-identifier rows after deterministic safety, legal-Article, medication, case-label, and detention-regime repair.

Residual rows: 9/120. Direct identifier leaks: 0/120.

## Summary

| Example | QI risk | QI spans | Audit class | Paper interpretation |
|---|---:|---|---|---|
| `legal_0002` | 3 | homosexuality; homosexuals; homosexual | task-critical overlap | The retained quasi-identifier text is inside the current gold task-critical fact, so removing it would change the annotated answer unless a domain-aware generalization is added. |
| `legal_0005` | 3 | Northern Ireland; 1976 | task-critical overlap | The retained quasi-identifier text is inside the current gold task-critical fact, so removing it would change the annotated answer unless a domain-aware generalization is added. |
| `legal_0054` | 3 | sister; sister’s; sister’; four votes to three | frontier candidate | The retained quasi-identifier appears related to legal claim context; manual review is needed before deciding whether to generalize it. |
| `legal_0056` | 3 | British; 10 September 2009; 14 May 2009 | frontier candidate | The retained quasi-identifier appears related to legal claim context; manual review is needed before deciding whether to generalize it. |
| `legal_0025` | 1 | resisting the exercise of official authority | task-critical overlap | The retained quasi-identifier text is inside the current gold task-critical fact, so removing it would change the annotated answer unless a domain-aware generalization is added. |
| `legal_0042` | 1 | Rom | frontier candidate | The retained quasi-identifier appears related to legal claim context; manual review is needed before deciding whether to generalize it. |
| `legal_0046` | 1 | widows | task-critical overlap | The retained quasi-identifier text is inside the current gold task-critical fact, so removing it would change the annotated answer unless a domain-aware generalization is added. |
| `legal_0053` | 1 | 14 years old | task-critical overlap | The retained quasi-identifier text is inside the current gold task-critical fact, so removing it would change the annotated answer unless a domain-aware generalization is added. |
| `legal_0055` | 1 | participate in a labour market policy programme. | frontier candidate | The retained quasi-identifier appears related to legal claim context; manual review is needed before deciding whether to generalize it. |

## Method Comparison

| Example | Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Fact judge | Not-retained audited facts |
|---|---|---|---|---:|---:|---:|---|---|
| `legal_0002` | `generic_llm` | None | homosexuality; homosexuals; homosexual | 0.500 | 1.000 | 0.500 | preserved=2 | None |
| `legal_0002` | `privacy_first_llm` | None | homosexuality; homosexual | 0.000 | 0.500 | 0.000 | generalized_not_retained=1, preserved=1 | an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result ... |
| `legal_0002` | `critical_span_guard_extracted` | None | homosexuality; homosexuals; homosexual | 0.500 | 1.000 | 0.500 | preserved=2 | None |
| `legal_0005` | `generic_llm` | None | None | 0.667 | 0.667 | 0.667 | generalized_not_retained=1, preserved=2 | the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) ... |
| `legal_0005` | `privacy_first_llm` | None | None | 0.333 | 0.667 | 0.333 | omitted=1, preserved=2 | the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) ... |
| `legal_0005` | `critical_span_guard_extracted` | None | Northern Ireland; 1976 | 1.000 | 1.000 | 1.000 | preserved=3 | None |
| `legal_0054` | `generic_llm` | None | None | 0.667 | 1.000 | 0.667 | preserved=3 | None |
| `legal_0054` | `privacy_first_llm` | None | None | 0.667 | 0.667 | 0.667 | generalized_not_retained=1, preserved=2 | when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family ... |
| `legal_0054` | `critical_span_guard_extracted` | None | sister; sister’s; sister’; four votes to three | 0.667 | 1.000 | 0.667 | preserved=3 | None |
| `legal_0056` | `generic_llm` | None | None | 0.667 | 1.000 | 0.667 | preserved=3 | None |
| `legal_0056` | `privacy_first_llm` | None | None | 0.667 | 1.000 | 0.667 | preserved=3 | None |
| `legal_0056` | `critical_span_guard_extracted` | None | British; 10 September 2009; 14 May 2009 | 0.667 | 1.000 | 0.667 | preserved=3 | None |
| `legal_0025` | `generic_llm` | None | 23 May 2003; resisting the exercise of official authority; 4 February 1998 | 1.000 | 1.000 | 1.000 | preserved=2 | None |
| `legal_0025` | `privacy_first_llm` | None | resisting the exercise of official authority | 0.500 | 1.000 | 0.500 | preserved=2 | None |
| `legal_0025` | `critical_span_guard_extracted` | None | resisting the exercise of official authority | 1.000 | 1.000 | 1.000 | preserved=2 | None |
| `legal_0042` | `generic_llm` | None | Rom | 1.000 | 1.000 | 1.000 | preserved=3 | None |
| `legal_0042` | `privacy_first_llm` | None | Rom | 1.000 | 1.000 | 1.000 | preserved=3 | None |
| `legal_0042` | `critical_span_guard_extracted` | None | Rom | 1.000 | 1.000 | 1.000 | preserved=3 | None |
| `legal_0046` | `generic_llm` | None | widows | 1.000 | 1.000 | 1.000 | preserved=3 | None |
| `legal_0046` | `privacy_first_llm` | None | widows | 0.333 | 0.333 | 0.333 | generalized_not_retained=2, preserved=1 | Article 1; because he was a man, he was denied social security benefits equivalent to those received by widows |
| `legal_0046` | `critical_span_guard_extracted` | None | widows | 1.000 | 1.000 | 1.000 | preserved=3 | None |
| `legal_0053` | `generic_llm` | 5786/08 | 21 January 2008; 14 years old | 0.500 | 0.500 | 0.500 | generalized_not_retained=1, preserved=1 | the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies ... |
| `legal_0053` | `privacy_first_llm` | None | None | 0.500 | 0.500 | 0.500 | generalized_not_retained=1, preserved=1 | the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies ... |
| `legal_0053` | `critical_span_guard_extracted` | None | 14 years old | 1.000 | 1.000 | 1.000 | preserved=2 | None |
| `legal_0055` | `generic_llm` | 28426/06 | 28 June 2006; participate in a labour market policy programme. | 1.000 | 1.000 | 1.000 | preserved=2 | None |
| `legal_0055` | `privacy_first_llm` | None | participate in a labour market policy programme. | 1.000 | 1.000 | 1.000 | preserved=2 | None |
| `legal_0055` | `critical_span_guard_extracted` | None | participate in a labour market policy programme. | 1.000 | 1.000 | 1.000 | preserved=2 | None |

## Row Notes

### `legal_0002` - task-critical overlap

- Source: `TAB:train:001-60695`
- CSG QI spans: homosexuality; homosexuals; homosexual
- Gold task facts: Article 8; an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces that existed at the time violated their ...
- QA answers: Article 8; an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces ...
- Audit interpretation: The retained quasi-identifier text is inside the current gold task-critical fact, so removing it would change the annotated answer unless a domain-aware generalization is added.

CSG output:

> PROCEDURE The case originated in two applications [ID] against [LOCATION] lodged with the European Commission of Human Rights (“the Commission”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by two [COUNTRY] nationals, [PERSON_NAME_1] and [PERSON_NAME_2]. The applicants alleged that an investigation into their sexuality and their discharge from the [MILITARY_BRANCH] on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces that existed at the time violated their rights under Article 8, alone and in conjunction with Article 14 of the Convention.

### `legal_0005` - task-critical overlap

- Source: `TAB:test:001-60309`
- CSG QI spans: Northern Ireland; 1976
- Gold task facts: Article 6; violation; the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976
- QA answers: Article 6; violation; the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976
- Audit interpretation: The retained quasi-identifier text is inside the current gold task-critical fact, so removing it would change the annotated answer unless a domain-aware generalization is added.

CSG output:

> PROCEDURE The case originated in an application [ID] against the Country lodged with the European Commission of Human Rights (“the Commission”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by an individual, [PERSON], on [DATE]. He alleged that the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976, which was deemed conclusive evidence that the applicant’s employment was terminated for the purpose of protecting public safety and public order, operated under the terms of the 1976 Act to deny him access to a court or tribunal, in violation of Article 6 § 1.

### `legal_0054` - frontier candidate

- Source: `TAB:dev:001-86146`
- CSG QI spans: sister; sister’s; sister’; four votes to three
- Gold task facts: Article 14; no violation; when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas the survivor of a married couple or a homosexual relationship registered under the Civil ...
- QA answers: Article 14; no violation; when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas the survivor of a married couple or a homosexual ...
- Audit interpretation: The retained quasi-identifier appears related to legal claim context; manual review is needed before deciding whether to generalize it.

CSG output:

> PROCEDURE The case originated in an application [ID] against [COUNTRY] lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by two [NATIONALITY] nationals, [PartyName]. The applicants complained under Article 14 of the Convention taken in conjunction with Article 1 of Protocol No. 1 that, when the first of them died, the survivor would be required to pay inheritance tax on the deceased sister’s share of the family home, whereas the survivor of a married couple or a homosexual relationship registered under the Civil Partnership Act 2004 would be exempt from paying inheritance tax in these circumstances. On [Date], the Chamber unanimously declared the application admissible and delivered a judgment in which it held, by four votes to three, that there had been no violation of Article 14 of the Convention taken in conjunction with Article 1 of Protocol No. 1.

### `legal_0056` - frontier candidate

- Source: `TAB:train:001-144123`
- CSG QI spans: British; 10 September 2009; 14 May 2009
- Gold task facts: Article 1; inadmissible; shortcomings in the British health system in connection with the recruitment of locum doctors and supervision of out-of-hours locum services had led to their father’s death as a consequence of medical malpractice by German locum ...
- QA answers: Article 1; inadmissible; shortcomings in the British health system in connection with the recruitment of locum doctors and supervision of out-of-hours locum services had led to their father’s death as a consequence ...
- Audit interpretation: The retained quasi-identifier appears related to legal claim context; manual review is needed before deciding whether to generalize it.

CSG output:

> PROCEDURE The case originated in an application [ID] against the [LOCATION] and the [LOCATION] lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by two [PERSON]s, [PERSON] and [PERSON], on 10 September 2009. The applicants, relying on the Member State’s general duty under Article 1 of the Convention to secure to everyone within their jurisdiction the rights and freedoms defined in its Section I, complained, inter alia, under the substantive aspect of Article 2 that shortcomings in the British health system in connection with the recruitment of locum doctors and supervision of out-of-hours locum services had led to their father’s death as a consequence of medical malpractice by German locum doctor [ID]. By a decision of 14 May 2009 the [COURT] declared [PERSON]’s extradition inadmissible.

### `legal_0025` - task-critical overlap

- Source: `TAB:train:001-81922`
- CSG QI spans: resisting the exercise of official authority
- Gold task facts: Article 4; the conduct of proceedings for the said traffic offence violated Article 4 of Protocol No. 7, given that he had been acquitted of the offence of resisting the exercise of official authority in respect of the same act
- QA answers: Article 4; the conduct of proceedings for the said traffic offence violated Article 4 of Protocol No. 7, given that he had been acquitted of the offence of resisting the exercise of official authority in respect of ...
- Audit interpretation: The retained quasi-identifier text is inside the current gold task-critical fact, so removing it would change the annotated answer unless a domain-aware generalization is added.

CSG output:

> PROCEDURE The case originated in an application [ID] against [REDACTED_COUNTRY] lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by an [REDACTED_COUNTRY] national, [REDACTED_NAME], on [REDACTED_DATE]. The applicant submitted his defence on [REDACTED_DATE], asserting in particular that the conduct of proceedings for the said traffic offence violated Article 4 of Protocol No. 7, given that he had been acquitted of the offence of resisting the exercise of official authority in respect of the same act.

### `legal_0042` - frontier candidate

- Source: `TAB:train:001-96100`
- CSG QI spans: Rom
- Gold task facts: Article 14; no violation; there had been a violation of Article 14 of the Convention taken in conjunction with Article 1 of Protocol No. 1 and Article 12 of the Convention
- QA answers: Article 14; no violation; there had been a violation of Article 14 of the Convention taken in conjunction with Article 1 of Protocol No. 1 and Article 12 of the Convention
- Audit interpretation: The retained quasi-identifier appears related to legal claim context; manual review is needed before deciding whether to generalize it.

CSG output:

> PROCEDURE The case originated in an application [ID] against the country lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national, [PERSON], on [DATE]. She alleged that there had been a violation of Article 14 of the Convention taken in conjunction with Article 1 of Protocol No. 1 and Article 12 of the Convention. No violation of Article 14 arises from the fact of limiting the survivor’s pension in practice to married couples.

### `legal_0046` - task-critical overlap

- Source: `TAB:test:001-91096`
- CSG QI spans: widows
- Gold task facts: Article 1; inadmissible; because he was a man, he was denied social security benefits equivalent to those received by widows
- QA answers: Article 1; inadmissible; because he was a man, he was denied social security benefits equivalent to those received by widows
- Audit interpretation: The retained quasi-identifier text is inside the current gold task-critical fact, so removing it would change the annotated answer unless a domain-aware generalization is added.

CSG output:

> PROCEDURE The case originated in an application [ID] against [LOCATION] lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national, [PERSON], on [DATE]. The applicant complained under Articles 8 and 14 of the Convention and Article 1 of Protocol No. 1 that, because he was a man, he was denied social security benefits equivalent to those received by widows. On [DATE] the Court decided to communicate the complaints concerning widows’ benefits relating to the period after the date on which the applicant lodged his relevant claim and declared the remainder of the application inadmissible.

### `legal_0053` - task-critical overlap

- Source: `TAB:train:001-128043`
- CSG QI spans: 14 years old
- Gold task facts: Article 8; the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he had attempted secretly to film her naked in their ...
- QA answers: Article 8; the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he had attempted ...
- Audit interpretation: The retained quasi-identifier text is inside the current gold task-critical fact, so removing it would change the annotated answer unless a domain-aware generalization is added.

CSG output:

> PROCEDURE The case originated in an application [ID] against the Kingdom of Sweden lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a Swedish national, [PERSON], on [DATE]. The applicant alleged that the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he had attempted secretly to film her naked in their bathroom when she was 14 years old.

### `legal_0055` - frontier candidate

- Source: `TAB:test:001-92090`
- CSG QI spans: participate in a labour market policy programme.
- Gold task facts: Article 6; her right to access to a court according to Article 6 § 1 of the Convention had been violated since she had not been able to appeal to a court against a decision by an authority to withdraw permission for her to participate in a labour market ...
- QA answers: Article 6; her right to access to a court according to Article 6 § 1 of the Convention had been violated since she had not been able to appeal to a court against a decision by an authority to withdraw permission for ...
- Audit interpretation: The retained quasi-identifier appears related to legal claim context; manual review is needed before deciding whether to generalize it.

CSG output:

> PROCEDURE The case originated in an application [ID] against the country lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national, [PERSON], on [DATE]. The applicant alleged that her right to access to a court according to Article 6 § 1 of the Convention had been violated since she had not been able to appeal to a court against a decision by an authority to withdraw permission for her to participate in a labour market policy programme.

## Paper Wording

Use this as evidence that the remaining CSG privacy risk is small and inspectable: 9 rows retain measured quasi-identifiers after the deterministic repair layer.
The remaining task-critical overlap cases (`legal_0002`, `legal_0005`, `legal_0025`, `legal_0046`, `legal_0053`) preserve quasi-identifying text inside the annotated legal claim itself, so removing it would change the current benchmark answer unless a domain-aware generalization is added.
Avoid claiming that every residual QI hit is inherently unavoidable. The stronger claim is that task-aware anonymization makes residual cases inspectable and separates true utility-overlap cases from policy gaps.
