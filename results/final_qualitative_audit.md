# Final Qualitative Audit

Paper-facing manual spot-check of the foreground examples and residual frontier cases from the current 50-example OpenAI run.

## Summary

| Example | Role | Paper point | Paper use |
|---|---|---|---|
| `clinical_0006` | Main clinical utility-loss example | Privacy-first redaction can anonymize away the clinical answer. | Foreground as the clearest clinical example. |
| `legal_0006` | Main legal privacy-utility example | Generic and privacy-first prompts fail in opposite directions on the same legal row. | Foreground as the clearest legal example. |
| `legal_0005` | Residual frontier example | Some legal statute specificity is both useful and identifying. | Use to explain residual privacy-utility overlap. |
| `legal_0025` | Second residual frontier example | Offence-description specificity can be required for legal reasoning but still quasi-identifying. | Mention briefly if discussing both residual CSG QI rows. |
| `legal_0018` | Metric nuance example | Exact TCFR is reproducible but conservative for legal paraphrase. | Use if space allows for exact-vs-audited TCFR. |

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

## Paper-Safe Wording

- Use `clinical_0006`, `legal_0006`, and `legal_0005` as the compact qualitative set in the main paper.
- Use `legal_0025` only if the residual privacy frontier needs a second legal example.
- Use `legal_0018` only to explain exact TCFR undercounting faithful legal paraphrase.
- Do not claim CSG solves legal anonymization; two residual rows retain quasi-identifying legal-claim text.
- Do not claim the verifier improved this run; the ablation attributes measured gains to deterministic safety/repair.
