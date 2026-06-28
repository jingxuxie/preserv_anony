# Final Qualitative Audit

Paper-facing manual spot-check of the foreground examples and residual frontier cases from the current 100-example n100 promoted run.

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

## Paper-Safe Wording

- Use `clinical_0006`, `legal_0006`, and `legal_0005` as the compact qualitative set in the main paper.
- Use `legal_0025` only if the residual privacy frontier needs a second legal example.
- Use `legal_0018` only to explain exact TCFR undercounting faithful legal paraphrase.
- Do not claim CSG solves legal anonymization; five residual rows retain quasi-identifying legal-claim text or frontier legal context.
- Carry `legal_0016` as a strict legal-specificity utility caveat, separate from the residual QI rows.
- Do not claim the verifier improved this run; the ablation attributes measured gains to deterministic safety/repair.
