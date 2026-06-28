# Final Qualitative Audit

Paper-facing manual spot-check of the foreground examples and residual frontier cases from the current 150-example expansion run.

## Summary

| Example | Role | Paper point | Paper use |
|---|---|---|---|
| `clinical_0006` | Main clinical utility-loss example | Privacy-first redaction can anonymize away the clinical answer. | Foreground as the clearest clinical example. |
| `legal_0006` | Main legal privacy-utility example | Generic and privacy-first prompts fail in opposite directions on the same legal row. | Foreground as the clearest legal example. |
| `legal_0005` | Residual frontier example | Some legal statute specificity is both useful and identifying. | Use to explain residual privacy-utility overlap. |
| `legal_0025` | Second residual frontier example | Offence-description specificity can be required for legal reasoning but still quasi-identifying. | Mention briefly when discussing residual CSG QI rows. |
| `legal_0018` | Metric nuance example | Exact TCFR is reproducible but conservative for legal paraphrase. | Use if space allows for exact-vs-audited TCFR. |
| `legal_0016` | Expanded-run strict legal specificity edge case | Strict legal-claim labels can make jurisdictional generalization count as utility loss. | Use only when discussing strict legal specificity. |
| `legal_0002` | Residual legal sensitive-claim overlap | Sensitive status can be both legally material and identifying. | Mention only in the residual QI caveat if space allows. |
| `legal_0042` | Residual legal frontier candidate | Not every residual QI hit should be called unavoidable. | Use to keep the limitations section honest about policy gaps. |
| `legal_0046` | Residual legal benefits-overlap example | Legal benefit categories can be task-critical and quasi-identifying. | Mention only as part of the five-row residual audit. |
| `legal_0053` | Residual legal age-overlap example | Age can be legally material and identifying. | Mention only as part of the expanded residual QI caveat. |
| `legal_0054` | Residual legal frontier candidate | Legal context can preserve relational details that may still identify the case. | Use if a second expanded residual example is needed. |
| `legal_0055` | Residual legal programme-overlap example | Programme details can be both legally relevant and identifying. | Mention only as part of the expanded residual QI caveat. |
| `legal_0056` | Residual legal jurisdiction/date frontier candidate | Jurisdiction and timeline specificity may require policy-sensitive generalization. | Use if discussing release-policy sensitivity. |
| `clinical_0055` | Expanded-run clinical strict utility caveat | Clinical utility scoring can penalize safety-preserving paraphrase of diagnostic evidence. | Use only when discussing strict audited utility labels. |
| `clinical_0059` | Expanded-run clinical symptom-specificity caveat | Some clinical utility losses are strict wording/specificity losses rather than answer failures. | Use only when discussing strict audited utility labels. |
| `legal_0062` | Expanded-run residual nationality frontier case | Nationality may remain when it is embedded in legal procedure context. | Mention only as part of the n150 residual QI caveat. |
| `legal_0063` | Expanded-run residual benefits-category frontier case | Benefits-category specificity can be legally material and identifying. | Mention only as part of the n150 residual QI caveat. |
| `legal_0069` | Expanded-run exact-metric artifact | Exact QA is reproducible but conservative for long legal paraphrases. | Use only if explaining exact-vs-audited utility. |

## Audit Details

### `clinical_0006` - Main clinical utility-loss example

- Domain/source: `clinical` / `synthetic_template`
- Manual decision: Use in the main qualitative section. Privacy-first anonymization removes named clinical facts needed for QA, while CSG preserves them after redacting identifiers.
- Gold task facts: 3 weeks of morning stiffness in both hands; swelling of the MCP joints; anti-CCP was positive; rheumatoid arthritis; methotrexate 15 mg weekly and folic acid 1 mg daily; 66-year-old
- Gold QA: What medication was started? -> methotrexate 15 mg weekly and folic acid 1 mg daily; Which lab result supported the suspected diagnosis? -> anti-CCP was positive
- Gold direct identifiers: Samuel Ortiz; North Ridge Clinic; July 16, 2025; MRN-710006; 202-555-1006; samuel.ortiz6@example.com; Dr. Patel
- Gold quasi-identifiers: 66-year-old; postal worker; Asheville

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | 66-year-old; postal worker | 0.833 | 1.000 | 1.000 | None |
| privacy_first_llm | None | postal worker | 0.000 | 0.333 | 0.000 | swelling of the MCP joints; anti-CCP was positive; rheumatoid arthritis; methotrexate 15 mg weekly and folic acid 1 mg daily |
| critical_span_guard_extracted | None | None | 1.000 | 1.000 | 1.000 | None |

Output snippets:

- `generic_llm` (preserved=6): A 66-year-old postal worker from a city in the southeastern United States visited a clinic on a summer date. He reported three weeks of morning stiffness in both hands, with swelling of the MCP joints. Anti-CCP was positive. The physician diagnosed rheumatoid arthritis and started methotrexate 15 mg weekly and folic acid 1 mg daily.
- `privacy_first_llm` (generalized_retained=1, omitted=4, preserved=1): A middle-aged postal worker from a regional city visited a healthcare clinic on a summer date. They reported three weeks of morning stiffness in both hands, with swelling of the finger joint areas. A specific antibody test was positive. The healthcare provider diagnosed an autoimmune joint condition and initiated treatment with a weekly dose of a disease-modifying medication and daily folic acid supplementation.
- `critical_span_guard_extracted` (generalized_retained=1, preserved=5): [REDACTED NAME], a mid 60s from [REDACTED CITY], visited [REDACTED INSTITUTION] on [REDACTED DATE] (record [REDACTED MRN], phone [REDACTED PHONE], email [REDACTED EMAIL]). He reported 3 weeks of morning stiffness in both hands, with swelling of the MCP joints. anti-CCP was positive. [CLINICIAN] diagnosed rheumatoid arthritis and started methotrexate 15 mg weekly and folic acid 1 mg daily.

### `legal_0006` - Main legal privacy-utility example

- Domain/source: `legal` / `TAB:train:001-60653`
- Manual decision: Use in the main qualitative section. Generic prompting leaks the application number and date; privacy-first prompting hides Article 6; CSG removes identifiers and preserves Article 6 plus the claim.
- Gold task facts: Article 6; the civil proceedings in her case exceeded a reasonable time, contrary to Article 6 § 1 of the Convention
- Gold QA: Which substantive Article was invoked? -> Article 6; What core claim was raised? -> the civil proceedings in her case exceeded a reasonable time, contrary to Article 6 § 1 of the Convention
- Gold direct identifiers: 37645/97; Mrs Helena Sawicka
- Gold quasi-identifiers: 10 March 1997

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | 37645/97 | 10 March 1997 | 1.000 | 1.000 | 1.000 | None |
| privacy_first_llm | None | None | 0.500 | 0.000 | 0.500 | Article 6; the civil proceedings in her case exceeded a reasonable time, contrary to Article 6 § 1 of the Convention |
| critical_span_guard_extracted | None | None | 1.000 | 1.000 | 1.000 | None |

Output snippets:

- `generic_llm` (preserved=2): PROCEDURE The case originated in an application (no. 37645/97) against a State party lodged with the European Court of Human Rights (“the Court”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, a woman (“the applicant”), on 10 March 1997. The applicant alleged, in particular, that the civil proceedings in her case ...
- `privacy_first_llm` (generalized_not_retained=1, omitted=1): PROCEDURE The case originated in an application against a country lodged with the European human rights body under former provisions of a human rights treaty by a national of that country, on a specific date. The applicant alleged, in particular, that the civil proceedings in her case exceeded a reasonable time, contrary to a specified article of the treaty.
- `critical_span_guard_extracted` (preserved=2): PROCEDURE The case originated in an application ([ID]) against [COUNTRY] lodged with [INSTITUTION] under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a [NATIONALITY] national, [NAME], on [DATE]. The applicant alleged, in particular, that the civil proceedings in her case exceeded a reasonable time, contrary to Article 6 § 1 of the Convention.

### `legal_0005` - Residual frontier example

- Domain/source: `legal` / `TAB:test:001-60309`
- Manual decision: Use in limitations or error analysis. CSG preserves the exact Article 6 / section 42 claim, but the statute name retains Northern Ireland and 1976 as quasi-identifying text.
- Gold task facts: Article 6; violation; the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976
- Gold QA: Which substantive Article was invoked? -> Article 6; What outcome did the Court state? -> violation; What core claim was raised? -> the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976
- Gold direct identifiers: 24265/94; Mr Liam Devenney
- Gold quasi-identifiers: Irish; 12 April 1994; Northern Ireland; 1976; United Kingdom

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | None | 0.667 | 0.667 | 0.667 | the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976 |
| privacy_first_llm | None | None | 0.333 | 0.667 | 0.333 | the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976 |
| critical_span_guard_extracted | None | Northern Ireland; 1976 | 1.000 | 1.000 | 1.000 | None |

Output snippets:

- `generic_llm` (generalized_not_retained=1, preserved=2): PROCEDURE The case originated in an application against a country lodged with the European Commission of Human Rights (“the Commission”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by an individual, on a specified date. The applicant alleged that the issue of a certificate issued by a government official, under relevant legislation, which was ...
- `privacy_first_llm` (omitted=1, preserved=2): PROCEDURE The case originated in an application against a country in Europe lodged with the European Court of Human Rights under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms by an individual from Ireland, on a specific date in 1994. The applicant alleged that a certificate issued by a government official, under a particular national law, which was considered conclusive ...
- `critical_span_guard_extracted` (preserved=3): PROCEDURE The case originated in an application [ID] against the Country lodged with the European Commission of Human Rights (“the Commission”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by an individual, [PERSON], on [DATE]. He alleged that the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment ...

### `legal_0025` - Second residual frontier example

- Domain/source: `legal` / `TAB:train:001-81922`
- Manual decision: Use as secondary evidence for the residual frontier. CSG preserves Article 4 of Protocol No. 7 and the same-act acquittal claim, but the offence-description phrase remains a measured QI hit.
- Gold task facts: Article 4; the conduct of proceedings for the said traffic offence violated Article 4 of Protocol No. 7, given that he had been acquitted of the offence of resisting the exercise of official authority in respect of the same act
- Gold QA: Which substantive Article was invoked? -> Article 4; What core claim was raised? -> the conduct of proceedings for the said traffic offence violated Article 4 of Protocol No. 7, given that he had been acquitted of the offence of resisting the exercise of official authority in ...
- Gold direct identifiers: 18015/03; Mr Roland Schutte
- Gold quasi-identifiers: 23 May 2003; resisting the exercise of official authority; 4 February 1998

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | 23 May 2003; resisting the exercise of official authority; 4 February 1998 | 1.000 | 1.000 | 1.000 | None |
| privacy_first_llm | None | resisting the exercise of official authority | 0.500 | 1.000 | 0.500 | None |
| critical_span_guard_extracted | None | resisting the exercise of official authority | 1.000 | 1.000 | 1.000 | None |

Output snippets:

- `generic_llm` (preserved=2): PROCEDURE The case originated in an application against a State party lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, the applicant, on 23 May 2003. The applicant submitted his defence on 4 February 1998, asserting in particular that the conduct of proceedings for the said traffic offence violated Article ...
- `privacy_first_llm` (preserved=2): PROCEDURE The case originated in an application against a European country lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, an individual (“the applicant”), on a specified date. The applicant submitted his defence on a previous date, asserting in particular that the conduct of proceedings for a traffic ...
- `critical_span_guard_extracted` (preserved=2): PROCEDURE The case originated in an application [ID] against [REDACTED_COUNTRY] lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by an [REDACTED_COUNTRY] national, [REDACTED_NAME], on [REDACTED_DATE]. The applicant submitted his defence on [REDACTED_DATE], asserting in particular that the conduct of proceedings for the said traffic ...

### `legal_0018` - Metric nuance example

- Domain/source: `legal` / `TAB:train:001-61164`
- Manual decision: Use only for metric discussion. CSG preserves Article 1 / Protocol No. 1 / Article 8 and the home/possessions claim, but exact matching misses a wording shift.
- Gold task facts: Article 1; the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively
- Gold QA: Which substantive Article was invoked? -> Article 1; What core claim was raised? -> the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention ...
- Gold direct identifiers: 35179/97; Ms Inga Allard
- Gold quasi-identifiers: 27 November 1996

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | None | 1.000 | 1.000 | 1.000 | None |
| privacy_first_llm | None | None | 0.000 | 0.000 | 0.000 | Article 1; the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively |
| critical_span_guard_extracted | None | None | 0.500 | 1.000 | 0.500 | None |

Output snippets:

- `generic_llm` (preserved=2): PROCEDURE The case originated in an application against a Member State lodged with the European Court of Human Rights (“the Court”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, a female applicant, on a specified date. The applicant alleged, in particular, that the demolition of a house had violated her rights to the ...
- `privacy_first_llm` (omitted=2): PROCEDURE The case originated in an application against a European country lodged with the European human rights body under a former article of a human rights convention by a national of that country, on a specific date. The applicant alleged that the demolition of a house had violated her rights to peaceful enjoyment of possessions and to respect for her home under relevant articles of the convention.
- `critical_span_guard_extracted` (preserved=2): PROCEDURE The case originated in an application [ID] against the Kingdom of Sweden lodged with the European human rights body under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national, [PERSON], on [DATE]. The applicant alleged, in particular, that the demolition of a house had violated her rights to peaceful enjoyment of her possessions and to ...

### `legal_0016` - Expanded-run strict legal specificity edge case

- Domain/source: `legal` / `TAB:test:001-90250`
- Manual decision: Use as strict legal-specificity caveat evidence. CSG preserves the Article 8 contact-with-daughter claim, but generalizes `Polish authorities` to `authorities`; the current strict legal claim treats that jurisdictional specificity as non-generalizable.
- Gold task facts: Article 8; the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention
- Gold QA: Which substantive Article was invoked? -> Article 8; What core claim was raised? -> the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention
- Gold direct identifiers: 11375/02; Mr Anton Kaleta
- Gold quasi-identifiers: German; 1 June 2001; 12 July 2006; 2001

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | 1 June 2001; 12 July 2006; 2001 | 0.500 | 0.500 | 0.500 | the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention |
| privacy_first_llm | None | None | 0.500 | 0.500 | 0.500 | the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention |
| critical_span_guard_extracted | None | None | 1.000 | 0.500 | 1.000 | the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention |

Output snippets:

- `generic_llm` (generalized_not_retained=1, preserved=1): PROCEDURE The case originated in an application against a State Party lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of a member state, the applicant, on 1 June 2001. The applicant alleged that the authorities had failed to take effective steps to enforce his right of contact with his child, which had violated his rights ...
- `privacy_first_llm` (generalized_not_retained=1, preserved=1): PROCEDURE The case originated in an application against a country lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of a member state, an individual, on a specific date. The applicant alleged that the authorities had failed to take effective steps to enforce their right of contact with a family member, which had violated ...
- `critical_span_guard_extracted` (generalized_not_retained=1, preserved=1): PROCEDURE The case originated in an application ([ID]) against [REDACTED_COUNTRY] lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national, [REDACTED_NAME], on [REDACTED_DATE]. The applicant alleged that the authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his ...

### `legal_0002` - Residual legal sensitive-claim overlap

- Domain/source: `legal` / `TAB:train:001-60695`
- Manual decision: Use only in residual-risk analysis. CSG preserves the sexuality and Article 8 claim, but the same sexuality terms remain measured quasi-identifiers because they are central to the legal claim.
- Gold task facts: Article 8; an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces that existed at the time violated their rights under Article 8, alone and in conjunction with ...
- Gold QA: Which substantive Article was invoked? -> Article 8; What core claim was raised? -> an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the ...
- Gold direct identifiers: 43208/98; 44875/98; Mr Terence Perkins
- Gold quasi-identifiers: Ms R.; homosexuality; homosexuals; homosexual

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | homosexuality; homosexuals; homosexual | 0.500 | 1.000 | 0.500 | None |
| privacy_first_llm | None | homosexuality; homosexual | 0.000 | 0.500 | 0.000 | an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces that ... |
| critical_span_guard_extracted | None | homosexuality; homosexuals; homosexual | 0.500 | 1.000 | 0.500 | None |

Output snippets:

- `generic_llm` (preserved=2): PROCEDURE The case originated in two applications against a member state lodged with the European Commission of Human Rights (“the Commission”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by two nationals of that country. The applicants alleged that an investigation into their sexuality and their discharge from the military service on the basis of ...
- `privacy_first_llm` (generalized_not_retained=1, preserved=1): PROCEDURE The case originated in two applications against a European country lodged with a human rights commission under a former human rights treaty by two nationals of that country. The applicants alleged that an investigation into their sexuality and their discharge from a military service on the basis of their homosexuality, due to a policy against the presence of individuals with same-sex orientation in the armed ...
- `critical_span_guard_extracted` (preserved=2): PROCEDURE The case originated in two applications [ID] against [LOCATION] lodged with the European Commission of Human Rights (“the Commission”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by two [COUNTRY] nationals, [PERSON_NAME_1] and [PERSON_NAME_2]. The applicants alleged that an investigation into their sexuality and their discharge from the ...

### `legal_0042` - Residual legal frontier candidate

- Domain/source: `legal` / `TAB:train:001-96100`
- Manual decision: Use as a frontier-policy caveat. CSG preserves the Article 14 / Protocol No. 1 / Article 12 claim; the retained `Rom` span needs policy review before treating it as unavoidable utility overlap.
- Gold task facts: Article 14; no violation; there had been a violation of Article 14 of the Convention taken in conjunction with Article 1 of Protocol No. 1 and Article 12 of the Convention
- Gold QA: Which substantive Article was invoked? -> Article 14; What outcome did the Court state? -> no violation; What core claim was raised? -> there had been a violation of Article 14 of the Convention taken in conjunction with Article 1 of Protocol No. 1 and Article 12 of the ...
- Gold direct identifiers: 49151/07; Mrs María Luisa Muñoz Díaz
- Gold quasi-identifiers: 29 October 2007; Rom

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | Rom | 1.000 | 1.000 | 1.000 | None |
| privacy_first_llm | None | Rom | 1.000 | 1.000 | 1.000 | None |
| critical_span_guard_extracted | None | Rom | 1.000 | 1.000 | 1.000 | None |

Output snippets:

- `generic_llm` (preserved=3): PROCEDURE The case originated in an application against a Member State lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, referred to as “the applicant,” on a specified date. She alleged that there had been a violation of Article 14 of the Convention taken in conjunction with Article 1 of Protocol No. 1 and ...
- `privacy_first_llm` (preserved=3): PROCEDURE The case originated in an application against a European country lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, a woman, on a specific date. She alleged that there had been a violation of Article 14 of the Convention taken in conjunction with Article 1 of Protocol No. 1 and Article 12 of the ...
- `critical_span_guard_extracted` (preserved=3): PROCEDURE The case originated in an application [ID] against the country lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national, [PERSON], on [DATE]. She alleged that there had been a violation of Article 14 of the Convention taken in conjunction with Article 1 of Protocol No. 1 and Article 12 of the Convention. No violation of ...

### `legal_0046` - Residual legal benefits-overlap example

- Domain/source: `legal` / `TAB:test:001-91096`
- Manual decision: Use only in residual-risk analysis. CSG preserves the widows-benefits claim, but the term `widows` remains a measured quasi-identifier inside the annotated legal answer.
- Gold task facts: Article 1; inadmissible; because he was a man, he was denied social security benefits equivalent to those received by widows
- Gold QA: Which substantive Article was invoked? -> Article 1; What outcome did the Court state? -> inadmissible; What core claim was raised? -> because he was a man, he was denied social security benefits equivalent to those received by widows
- Gold direct identifiers: 28095/02; Mr Dennis Twomey
- Gold quasi-identifiers: British; 1 March 2001; widows; 4 November 2003; British national

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | widows | 1.000 | 1.000 | 1.000 | None |
| privacy_first_llm | None | widows | 0.333 | 0.333 | 0.333 | Article 1; because he was a man, he was denied social security benefits equivalent to those received by widows |
| critical_span_guard_extracted | None | widows | 1.000 | 1.000 | 1.000 | None |

Output snippets:

- `generic_llm` (preserved=3): PROCEDURE The case originated in an application against a member state lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, on a specified date. The applicant complained under Articles 8 and 14 of the Convention and Article 1 of Protocol No. 1 that, because he was a man, he was denied social security benefits ...
- `privacy_first_llm` (generalized_not_retained=2, preserved=1): PROCEDURE The case originated in an application against a European country lodged with the Court under a human rights treaty by a national of that country, on a specific date. The applicant complained under certain articles of the treaty that, because he was a man, he was denied social security benefits typically provided to widows. The Court decided to communicate the complaints related to benefits for widows concerning a ...
- `critical_span_guard_extracted` (preserved=3): PROCEDURE The case originated in an application [ID] against [LOCATION] lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national, [PERSON], on [DATE]. The applicant complained under Articles 8 and 14 of the Convention and Article 1 of Protocol No. 1 that, because he was a man, he was denied social security benefits equivalent to ...

### `legal_0053` - Residual legal age-overlap example

- Domain/source: `legal` / `TAB:train:001-128043`
- Manual decision: Use only in residual-risk analysis. CSG preserves the Article 8 remedies claim, but `14 years old` remains as a measured quasi-identifier because it is inside the annotated legal claim.
- Gold task facts: Article 8; the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he had attempted secretly to film her naked in their bathroom when she was 14 years old
- Gold QA: Which substantive Article was invoked? -> Article 8; What core claim was raised? -> the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he ...
- Gold direct identifiers: 5786/08; Ms Eliza Söderman
- Gold quasi-identifiers: 21 January 2008; 14 years old

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | 5786/08 | 21 January 2008; 14 years old | 0.500 | 0.500 | 0.500 | the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he had attempted secretly to ... |
| privacy_first_llm | None | None | 0.500 | 0.500 | 0.500 | the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he had attempted secretly to ... |
| critical_span_guard_extracted | None | 14 years old | 1.000 | 1.000 | 1.000 | None |

Output snippets:

- `generic_llm` (generalized_not_retained=1, preserved=1): PROCEDURE The case originated in an application (no. 5786/08) against a State party lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, a woman, on 21 January 2008. The applicant alleged that the State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies ...
- `privacy_first_llm` (generalized_not_retained=1, preserved=1): PROCEDURE The case originated in an application against a European country lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, a woman, on a specific date. The applicant alleged that the State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against a ...
- `critical_span_guard_extracted` (preserved=2): PROCEDURE The case originated in an application [ID] against the Kingdom of Sweden lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a Swedish national, [PERSON], on [DATE]. The applicant alleged that the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her ...

### `legal_0054` - Residual legal frontier candidate

- Domain/source: `legal` / `TAB:dev:001-86146`
- Manual decision: Use as a frontier-policy caveat. CSG preserves the inheritance-tax claim, but relationship terms and vote-count detail remain and may be generalizable under a stricter release policy.
- Gold task facts: Article 14; no violation; when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas the survivor of a married couple or a homosexual relationship registered under the Civil Partnership Act 2004 would be exempt from paying inheritance ...
- Gold QA: Which substantive Article was invoked? -> Article 14; What outcome did the Court state? -> no violation; What core claim was raised? -> when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas ...
- Gold direct identifiers: 13378/05
- Gold quasi-identifiers: sister; 12 December 2006; sister’s; United Kingdom of Great Britain and Northern Ireland; British nationals; British; sister’; four votes to three

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | None | 0.667 | 1.000 | 0.667 | None |
| privacy_first_llm | None | None | 0.667 | 0.667 | 0.667 | when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas the survivor of a married couple or a homosexual relationship registered under ... |
| critical_span_guard_extracted | None | sister; sister’s; sister’; four votes to three | 0.667 | 1.000 | 0.667 | None |

Output snippets:

- `generic_llm` (preserved=3): PROCEDURE The case originated in an application against a member state lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by two individuals. The applicants complained under Article 14 of the Convention taken in conjunction with Article 1 of Protocol No. 1 that, when the first of them died, the survivor would be required to pay inheritance ...
- `privacy_first_llm` (generalized_not_retained=1, preserved=2): PROCEDURE The case originated in an application against a country in Europe lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by two individuals. The applicants complained under Article 14 of the Convention taken in conjunction with Article 1 of Protocol No. 1 that, when one of them died, the survivor would be required to pay inheritance ...
- `critical_span_guard_extracted` (preserved=3): PROCEDURE The case originated in an application [ID] against [COUNTRY] lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by two [NATIONALITY] nationals, [PartyName]. The applicants complained under Article 14 of the Convention taken in conjunction with Article 1 of Protocol No. 1 that, when the first of them died, the survivor would be ...

### `legal_0055` - Residual legal programme-overlap example

- Domain/source: `legal` / `TAB:test:001-92090`
- Manual decision: Use only in residual-risk analysis. CSG preserves the access-to-court claim, but the labour-market-programme phrase remains as a measured quasi-identifier.
- Gold task facts: Article 6; her right to access to a court according to Article 6 § 1 of the Convention had been violated since she had not been able to appeal to a court against a decision by an authority to withdraw permission for her to participate in a labour market policy programme
- Gold QA: Which substantive Article was invoked? -> Article 6; What core claim was raised? -> her right to access to a court according to Article 6 § 1 of the Convention had been violated since she had not been able to appeal to a court against a decision by an authority to withdraw ...
- Gold direct identifiers: 28426/06; Ms Sonja Mendel
- Gold quasi-identifiers: 28 June 2006; participate in a labour market policy programme.; Kingdom of Sweden; Swedish

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | 28426/06 | 28 June 2006; participate in a labour market policy programme. | 1.000 | 1.000 | 1.000 | None |
| privacy_first_llm | None | participate in a labour market policy programme. | 1.000 | 1.000 | 1.000 | None |
| critical_span_guard_extracted | None | participate in a labour market policy programme. | 1.000 | 1.000 | 1.000 | None |

Output snippets:

- `generic_llm` (preserved=2): PROCEDURE The case originated in an application (no. 28426/06) against a State party lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, a female applicant, on 28 June 2006. The applicant alleged that her right of access to a court according to Article 6 § 1 of the Convention had been violated since she had ...
- `privacy_first_llm` (preserved=2): PROCEDURE The case originated in an application against a European country lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, the applicant, on a specific date. The applicant alleged that her right to access to a court according to Article 6 § 1 of the Convention had been violated since she had not been able ...
- `critical_span_guard_extracted` (preserved=2): PROCEDURE The case originated in an application [ID] against the country lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national, [PERSON], on [DATE]. The applicant alleged that her right to access to a court according to Article 6 § 1 of the Convention had been violated since she had not been able to appeal to a court against a ...

### `legal_0056` - Residual legal jurisdiction/date frontier candidate

- Domain/source: `legal` / `TAB:train:001-144123`
- Manual decision: Use as a frontier-policy caveat. CSG preserves the immigration-detention claim, but nationality and exact dates remain candidates for stricter generalization.
- Gold task facts: Article 1; inadmissible; shortcomings in the British health system in connection with the recruitment of locum doctors and supervision of out-of-hours locum services had led to their father’s death as a consequence of medical malpractice by German locum doctor U
- Gold QA: Which substantive Article was invoked? -> Article 1; What outcome did the Court state? -> inadmissible; What core claim was raised? -> shortcomings in the British health system in connection with the recruitment of locum doctors and supervision of out-of-hours locum services ...
- Gold direct identifiers: 49278/09; Mr Stuart Gray
- Gold quasi-identifiers: United Kingdom; British; Mr Rory Gray; 10 September 2009; Hamm General Prosecution Authorities; Hamm; Hamm General Prosecution; Hamm Higher Regional Court; 14 May 2009

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | None | 0.667 | 1.000 | 0.667 | None |
| privacy_first_llm | None | None | 0.667 | 1.000 | 0.667 | None |
| critical_span_guard_extracted | None | British; 10 September 2009; 14 May 2009 | 0.667 | 1.000 | 0.667 | None |

Output snippets:

- `generic_llm` (preserved=3): PROCEDURE The case originated in an application against a Member State and another country lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by two individuals, identified as Mr. Gray and Mr. Gray, on a specified date. The applicants, relying on the Member State’s general duty under Article 1 of the Convention to secure to everyone within ...
- `privacy_first_llm` (preserved=3): PROCEDURE The case originated in an application against a European country and a Western European country lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by two nationals of an unspecified country, referred to here as the Applicants, on a specific date. The Applicants, relying on the Member State’s general duty under Article 1 of the ...
- `critical_span_guard_extracted` (preserved=3): PROCEDURE The case originated in an application [ID] against the [LOCATION] and the [LOCATION] lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by two [PERSON]s, [PERSON] and [PERSON], on 10 September 2009. The applicants, relying on the Member State’s general duty under Article 1 of the Convention to secure to everyone within their ...

### `clinical_0055` - Expanded-run clinical strict utility caveat

- Domain/source: `clinical` / `synthetic_template`
- Manual decision: Use only in limitations. CSG removes the age/profession/city quasi-identifiers and keeps the diagnosis and treatment plan, but the strict audited fact list counts the CT angiography specificity as not fully retained.
- Gold task facts: sudden pleuritic chest pain and shortness of breath; oxygen saturation was 89 percent on room air; CT angiography showed a segmental pulmonary embolism; pulmonary embolism; apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily; 69-year-old
- Gold QA: What condition was diagnosed? -> pulmonary embolism; What anticoagulation plan was started? -> apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily
- Gold direct identifiers: Nadia Hassan; Riverside Family Practice; August 8, 2025; MRN-710055; 202-555-1055; nadia.hassan55@example.com; Dr. Singh
- Gold quasi-identifiers: 69-year-old; violin maker; Flagstaff

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | 69-year-old; violin maker | 0.667 | 1.000 | 0.500 | None |
| privacy_first_llm | None | None | 0.167 | 0.333 | 0.500 | sudden pleuritic chest pain and shortness of breath; oxygen saturation was 89 percent on room air; CT angiography showed a segmental pulmonary embolism; apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily |
| critical_span_guard_extracted | None | None | 0.833 | 0.833 | 1.000 | CT angiography showed a segmental pulmonary embolism |

Output snippets:

- `generic_llm` (preserved=6): A 69-year-old violin maker from a northern city visited a local family practice clinic on a recent date. She reported sudden pleuritic chest pain and shortness of breath, with oxygen saturation of 89 percent on room air. CT angiography showed a segmental pulmonary embolism. The physician diagnosed pulmonary embolism and started anticoagulant therapy with apixaban 10 mg twice daily for 7 days, followed by 5 mg twice daily.
- `privacy_first_llm` (generalized_retained=1, omitted=4, preserved=1): A middle-aged individual specializing in string instrument craftsmanship visited a healthcare facility on a recent date. They reported sudden chest pain and shortness of breath, with oxygen saturation below normal levels. Imaging tests indicated a pulmonary embolism. A healthcare provider diagnosed the condition and initiated anticoagulant therapy.
- `critical_span_guard_extracted` (generalized_not_retained=1, generalized_retained=1, preserved=4): [REDACTED_NAME], a late 60s individual, visited [CLINIC] on [REDACTED_DATE] (record [REDACTED_MRN], phone [REDACTED_PHONE], email [REDACTED_EMAIL]). They reported sudden pleuritic chest pain and shortness of breath, with oxygen saturation was 89 percent on room air. Imaging showed a segmental pulmonary embolism. [CLINICIAN] diagnosed pulmonary embolism and started medication with apixaban 10 mg twice daily for 7 days ...

### `clinical_0059` - Expanded-run clinical symptom-specificity caveat

- Domain/source: `clinical` / `synthetic_template`
- Manual decision: Use only in limitations. CSG removes age/profession/city quasi-identifiers and preserves appendicitis QA, but the strict audited fact list counts the exact symptom-duration phrase as omitted.
- Gold task facts: 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; CT abdomen showed an enlarged appendix with periappendiceal fat stranding; acute appendicitis; ceftriaxone and metronidazole before laparoscopic appendectomy; 29-year-old
- Gold QA: What did the CT abdomen show? -> enlarged appendix with periappendiceal fat stranding; What procedure was planned? -> laparoscopic appendectomy
- Gold direct identifiers: Elena Petrova; Riverside Family Practice; December 9, 2025; MRN-710059; 202-555-1059; elena.petrova59@example.com; Dr. Singh
- Gold quasi-identifiers: 29-year-old; farm manager; Tucson

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | 29-year-old; farm manager | 0.500 | 0.833 | 0.500 | ceftriaxone and metronidazole before laparoscopic appendectomy |
| privacy_first_llm | None | None | 0.167 | 0.500 | 0.000 | 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; ceftriaxone and metronidazole before laparoscopic appendectomy |
| critical_span_guard_extracted | None | None | 0.500 | 0.833 | 1.000 | 18 hours of periumbilical pain that migrated to the right lower quadrant |

Output snippets:

- `generic_llm` (omitted=1, preserved=5): A 29-year-old farm manager from a southwestern city visited a local family practice on a specific date in late 2025. She reported 18 hours of periumbilical pain that migrated to the right lower quadrant, with rebound tenderness at a specific point. Imaging of the abdomen showed an enlarged appendix with surrounding fat stranding. The physician diagnosed acute appendicitis and initiated antibiotic treatment before ...
- `privacy_first_llm` (generalized_retained=1, omitted=3, preserved=2): A female patient in her late twenties visited a healthcare facility on a specified date. She reported several hours of abdominal pain that migrated to the lower right area, with rebound tenderness noted at a common clinical point. Imaging revealed an enlarged appendix with surrounding fat changes. The clinician diagnosed acute appendicitis and initiated antibiotic therapy before surgical removal of the appendix.
- `critical_span_guard_extracted` (generalized_retained=1, omitted=1, preserved=4): [REDACTED_NAME], an adolescent adult worker from [REDACTED_CITY], visited [REDACTED_CLINIC] on [REDACTED_DATE] (record [REDACTED_MRN], phone [REDACTED_PHONE], email [REDACTED_EMAIL]). They reported 18 hours of periumbilical pain migrating to the right lower quadrant, with rebound tenderness at McBurney's point. CT abdomen showed an enlarged appendix with periappendiceal fat stranding. [CLINICIAN] diagnosed acute ...

### `legal_0062` - Expanded-run residual nationality frontier case

- Domain/source: `legal` / `TAB:train:001-122371`
- Manual decision: Use in residual-risk analysis if n150 is promoted. CSG preserves the Article 2 lethal-force claim, but the retained nationality term `Irish` remains a measured quasi-identifier.
- Gold task facts: Article 2; there had been an unlawful use of lethal force against the deceased, Mr John Hemsworth
- Gold QA: Which substantive Article was invoked? -> Article 2; What core claim was raised? -> there had been an unlawful use of lethal force against the deceased, Mr John Hemsworth
- Gold direct identifiers: 58559/09; Mrs Collette Hemsworth
- Gold quasi-identifiers: Irish; Mr Michael Hemsworth; 12 October 2009; Mr John Hemsworth; John Hemsworth; Northern Ireland; October 2009

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | 58559/09 | 12 October 2009; Northern Ireland; October 2009 | 0.500 | 0.500 | 0.500 | there had been an unlawful use of lethal force against the deceased, Mr John Hemsworth |
| privacy_first_llm | None | None | 0.500 | 0.500 | 0.500 | there had been an unlawful use of lethal force against the deceased, Mr John Hemsworth |
| critical_span_guard_extracted | None | Irish | 0.500 | 1.000 | 0.500 | None |

Output snippets:

- `generic_llm` (generalized_not_retained=1, preserved=1): PROCEDURE The case originated in an application (no. 58559/09) against a country in the United Kingdom of Great Britain and Northern Ireland lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by two individuals, a woman and a man (“the first and second applicants”), on 12 October 2009. The applicants mainly complained under Article 2 that ...
- `privacy_first_llm` (generalized_not_retained=1, preserved=1): PROCEDURE The case originated in an application against a European country lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by two individuals of a certain nationality, hereafter referred to as the first and second applicants, on a specific date. The applicants mainly complained under Article 2 that there had been an unlawful use of ...
- `critical_span_guard_extracted` (preserved=2): PROCEDURE The case originated in an application [ID] against [REDACTED] lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by two Irish nationals, [REDACTED] and [REDACTED] (“the first and second applicants”), on [REDACTED]. The applicants mainly complained under Article 2 that there had been an unlawful use of lethal force against the ...

### `legal_0063` - Expanded-run residual benefits-category frontier case

- Domain/source: `legal` / `TAB:test:001-83404`
- Manual decision: Use in residual-risk analysis if n150 is promoted. CSG preserves the Article 14 discrimination claim, but the benefits-category phrase remains a measured quasi-identifier and may need policy-sensitive generalization.
- Gold task facts: Article 14; inadmissible; the United Kingdom authorities' refusal to grant him Widow's Bereavement Allowance or equivalent constituted discrimination on grounds of sex contrary to Article 14 of the Convention in conjunction with Article 1 of Protocol No. 1
- Gold QA: Which substantive Article was invoked? -> Article 14; What outcome did the Court state? -> inadmissible; What core claim was raised? -> the United Kingdom authorities' refusal to grant him Widow's Bereavement Allowance or equivalent constituted discrimination on grounds of ...
- Gold direct identifiers: 12895/02; Mr William Crilly
- Gold quasi-identifiers: 26 September 2000; 30 April 2002; Widow's Bereavement Allowance

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | None | 0.667 | 0.667 | 0.667 | the United Kingdom authorities' refusal to grant him Widow's Bereavement Allowance or equivalent constituted discrimination on grounds of sex contrary to Article 14 of the Convention in conjunction with Article 1 of ... |
| privacy_first_llm | None | None | 0.667 | 0.667 | 0.667 | the United Kingdom authorities' refusal to grant him Widow's Bereavement Allowance or equivalent constituted discrimination on grounds of sex contrary to Article 14 of the Convention in conjunction with Article 1 of ... |
| critical_span_guard_extracted | None | Widow's Bereavement Allowance | 0.667 | 1.000 | 0.667 | None |

Output snippets:

- `generic_llm` (omitted=1, preserved=2): PROCEDURE The case originated in an application against a member state lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by an individual on a specified date. The applicant complained that the authorities' refusal to grant a certain type of bereavement allowance or its equivalent constituted discrimination on grounds of sex contrary to ...
- `privacy_first_llm` (generalized_not_retained=1, preserved=2): PROCEDURE The case originated in an application against a European country lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by an individual on a specified date. The applicant complained that the authorities' refusal to grant a certain social benefit or its equivalent constituted discrimination on grounds of sex contrary to Article 14 of ...
- `critical_span_guard_extracted` (preserved=3): PROCEDURE The case originated in an application [ID] against the country lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by [PERSON] on [DATE]. The applicant complained that the authorities' refusal to grant [PATIENT]'s Widow's Bereavement Allowance or equivalent constituted discrimination on grounds of sex contrary to Article 14 of the ...

### `legal_0069` - Expanded-run exact-metric artifact

- Domain/source: `legal` / `TAB:train:001-79486`
- Manual decision: Use only for metric discussion. CSG has no direct or quasi-identifier hit and the audited judge retains all facts, but exact QA matching misses a faithful paraphrase of the core claim.
- Gold task facts: Article 1; State security forces had destroyed his home and possessions and had forced him to leave his place of residence with no possibility of return and that he had been denied an effective remedy in domestic law in violation of Articles 3, 6, 8, 13 and 14 of the Convention and Article 1 of Protocol No. 1
- Gold QA: Which substantive Article was invoked? -> Article 1; What core claim was raised? -> State security forces had destroyed his home and possessions and had forced him to leave his place of residence with no possibility of return and that he had been denied an effective remedy in ...
- Gold direct identifiers: 37850/97; Mr Halis Aksakal
- Gold quasi-identifiers: 3 November 1995; Turkey; 1995; Halis Aksakal

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | None | 0.500 | 1.000 | 0.500 | None |
| privacy_first_llm | None | None | 0.000 | 0.000 | 0.000 | Article 1; State security forces had destroyed his home and possessions and had forced him to leave his place of residence with no possibility of return and that he had been denied an effective remedy in domestic law ... |
| critical_span_guard_extracted | None | None | 0.500 | 1.000 | 0.500 | None |

Output snippets:

- `generic_llm` (preserved=2): PROCEDURE The case originated in an application against a State party lodged with the European Commission of Human Rights (“the Commission”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, the applicant, on a specified date. The applicant alleged that security forces had destroyed his home and possessions and had forced ...
- `privacy_first_llm` (generalized_not_retained=2): PROCEDURE The case originated in an application against a national government lodged with an international human rights body under a former human rights treaty provision. The applicant alleged that security forces had destroyed his home and possessions and had forced him to leave his residence with no possibility of return, and that he had been denied an effective remedy in domestic law in violation of several articles of ...
- `critical_span_guard_extracted` (preserved=2): PROCEDURE The case originated in an application [ID] against the country lodged with the European Commission of Human Rights (“the Commission”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national, [PERSON], on [DATE]. The applicant alleged that institution had destroyed [HIS/HER] home and possessions and had forced [HIM/HER] to leave ...

## Paper-Safe Wording

- Use `clinical_0006`, `legal_0006`, and `legal_0005` as the compact qualitative set in the main paper.
- Use `legal_0025` only if the residual privacy frontier needs a second legal example.
- Use `legal_0018` only to explain exact TCFR undercounting faithful legal paraphrase.
- Do not claim CSG solves legal anonymization; 11 residual rows retain quasi-identifying legal-claim text or frontier legal context.
- Carry `legal_0016` as a strict legal-specificity utility caveat, separate from the residual QI rows.
- Carry `clinical_0055` and `clinical_0059` as strict clinical utility caveats, separate from the residual QI rows.
- Do not claim the verifier improved this run; the ablation attributes measured gains to deterministic safety/repair.
