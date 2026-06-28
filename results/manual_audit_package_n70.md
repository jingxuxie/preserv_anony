# Manual Audit Package

This package selects high-signal rows from the cached 70-example LLM run for human review.

## Audit checklist

- Privacy: did the output retain a direct identifier, case number, institution, exact age, rare occupation, or other re-identification cue?
- Utility: are diagnosis/claim, article/statute, dose/value, outcome, chronology, and downstream answer still recoverable?
- Faithfulness: did anonymization introduce a new fact or contradict a task-critical fact?
- Scorer disagreement: does deterministic exact matching undercount a faithful paraphrase?

## Candidate index

| Example | Domain | Why selected |
|---|---|---|
| clinical_0006 | clinical | privacy-first clinical utility loss |
| clinical_0029 | clinical | CSG exact-match undercount candidate |
| clinical_0031 | clinical | generic direct identifier leak |
| legal_0001 | legal | generic direct identifier leak |
| legal_0006 | legal | generic direct identifier leak |
| legal_0018 | legal | lowest exact-TCFR CSG case; privacy-first legal utility loss |
| legal_0043 | legal | largest CSG vs privacy-first utility gap |
| legal_0049 | legal | CSG closes generic direct leak on same example |

## clinical_0006 (clinical)

Selected because: privacy-first clinical utility loss

### Original

> Samuel Ortiz, a 66-year-old postal worker from Asheville, visited North Ridge Clinic on July 16, 2025 (record MRN-710006, phone 202-555-1006, email samuel.ortiz6@example.com). He reported 3 weeks of morning stiffness in both hands, with swelling of the MCP joints. anti-CCP was positive. Dr. Patel diagnosed rheumatoid arthritis and started methotrexate 15 mg weekly and folic acid 1 mg daily.

- Gold direct/private spans: Samuel Ortiz; North Ridge Clinic; July 16, 2025; MRN-710006; 202-555-1006; samuel.ortiz6@example.com; Dr. Patel
- Gold quasi-identifiers: 66-year-old; postal worker; Asheville
- Gold task-critical facts: 3 weeks of morning stiffness in both hands; swelling of the MCP joints; anti-CCP was positive; rheumatoid arthritis; methotrexate 15 mg weekly and folic acid 1 mg daily; 66-year-old
- Gold QA: What medication was started? -> methotrexate 15 mg weekly and folic acid 1 mg daily; Which lab result supported the suspected diagnosis? -> anti-CCP was positive

### Method summary

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA consistency | Fact-judge statuses |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | 66-year-old; postal worker | 0.833 | 1.000 | 1.000 | preserved=6 |
| privacy_first_llm | None | postal worker | 0.000 | 0.333 | 0.000 | preserved=1, generalized_retained=1, omitted=4 |
| critical_span_guard_extracted | None | None | 1.000 | 1.000 | 1.000 | preserved=5, generalized_retained=1 |

### generic_llm

> A 66-year-old postal worker from a city in the southeastern United States visited a clinic on a summer date. He reported three weeks of morning stiffness in both hands, with swelling of the MCP joints. Anti-CCP was positive. The physician diagnosed rheumatoid arthritis and started methotrexate 15 mg weekly and folic acid 1 mg daily.

- Omitted facts by exact scorer: 3 weeks of morning stiffness in both hands
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

### privacy_first_llm

> A middle-aged postal worker from a regional city visited a healthcare clinic on a summer date. They reported three weeks of morning stiffness in both hands, with swelling of the finger joint areas. A specific antibody test was positive. The healthcare provider diagnosed an autoimmune joint condition and initiated treatment with a weekly dose of a disease-modifying medication and daily folic acid supplementation.

- Omitted facts by exact scorer: 3 weeks of morning stiffness in both hands; swelling of the MCP joints; anti-CCP was positive; rheumatoid arthritis; methotrexate 15 mg weekly and folic acid 1 mg daily; 66-year-old
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: What medication was started?; Which lab result supported the suspected diagnosis?
- Not-retained facts by LLM judge: swelling of the MCP joints; anti-CCP was positive; rheumatoid arthritis; methotrexate 15 mg weekly and folic acid 1 mg daily
- Contradicted facts by LLM judge: None

### critical_span_guard_extracted

> [REDACTED NAME], a mid 60s from [REDACTED CITY], visited [REDACTED INSTITUTION] on [REDACTED DATE] (record [REDACTED MRN], phone [REDACTED PHONE], email [REDACTED EMAIL]). He reported 3 weeks of morning stiffness in both hands, with swelling of the MCP joints. anti-CCP was positive. [CLINICIAN] diagnosed rheumatoid arthritis and started methotrexate 15 mg weekly and folic acid 1 mg daily.

- Omitted facts by exact scorer: None
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

## clinical_0029 (clinical)

Selected because: CSG exact-match undercount candidate

### Original

> Grace Chen, a 91-year-old long-haul driver from Boise, visited Riverside Family Practice on June 15, 2025 (record MRN-710029, phone 202-555-1029, email grace.chen29@example.com). She reported 18 hours of periumbilical pain that migrated to the right lower quadrant, with rebound tenderness was present at McBurney's point. CT abdomen showed an enlarged appendix with periappendiceal fat stranding. Dr. Kim diagnosed acute appendicitis and started ceftriaxone and metronidazole before laparoscopic appendectomy.

- Gold direct/private spans: Grace Chen; Riverside Family Practice; June 15, 2025; MRN-710029; 202-555-1029; grace.chen29@example.com; Dr. Kim
- Gold quasi-identifiers: 91-year-old; long-haul driver; Boise
- Gold task-critical facts: 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; CT abdomen showed an enlarged appendix with periappendiceal fat stranding; acute appendicitis; ceftriaxone and metronidazole before laparoscopic appendectomy; 91-year-old
- Gold QA: What did the CT abdomen show? -> enlarged appendix with periappendiceal fat stranding; What procedure was planned? -> laparoscopic appendectomy

### Method summary

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA consistency | Fact-judge statuses |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | 91-year-old; long-haul driver | 0.500 | 0.833 | 0.500 | preserved=5, omitted=1 |
| privacy_first_llm | None | long-haul driver | 0.167 | 0.500 | 0.000 | preserved=2, generalized_retained=1, omitted=3 |
| critical_span_guard_extracted | None | None | 0.833 | 1.000 | 1.000 | preserved=5, generalized_retained=1 |

### generic_llm

> A 91-year-old long-haul driver from a specific city visited a family practice clinic on a date in mid-2025. She reported 18 hours of periumbilical pain that migrated to the right lower quadrant, with rebound tenderness at a specific point. Imaging of the abdomen showed an enlarged appendix with surrounding fat stranding. A physician diagnosed acute appendicitis and initiated antibiotic therapy before laparoscopic appendectomy.

- Omitted facts by exact scorer: rebound tenderness was present at McBurney's point; CT abdomen showed an enlarged appendix with periappendiceal fat stranding; ceftriaxone and metronidazole before laparoscopic appendectomy
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: What did the CT abdomen show?
- Not-retained facts by LLM judge: rebound tenderness was present at McBurney's point
- Contradicted facts by LLM judge: None

### privacy_first_llm

> A senior long-haul driver visited a healthcare facility on a specific date. They reported several hours of abdominal pain that migrated to the lower right area, with rebound tenderness at a specific point. Imaging revealed an enlarged appendix with surrounding fat changes. A healthcare provider diagnosed acute appendicitis and initiated antibiotic treatment before surgical removal of the appendix.

- Omitted facts by exact scorer: 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; CT abdomen showed an enlarged appendix with periappendiceal fat stranding; ceftriaxone and metronidazole before laparoscopic ...
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: What did the CT abdomen show?; What procedure was planned?
- Not-retained facts by LLM judge: 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; ceftriaxone and metronidazole before laparoscopic appendectomy
- Contradicted facts by LLM judge: None

### critical_span_guard_extracted

> [PERSON], a adult over 80 worker from [LOCATION], visited [CLINIC] on [DATE] (record [ID]], phone [ID], email [ID]). She reported 18 hours of periumbilical pain that migrated to the right lower quadrant, with rebound tenderness at McBurney's point. CT abdomen showed an enlarged appendix with periappendiceal fat stranding. [CLINICIAN] diagnosed acute appendicitis and started ceftriaxone and metronidazole before laparoscopic appendectomy.

- Omitted facts by exact scorer: rebound tenderness was present at McBurney's point
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

## clinical_0031 (clinical)

Selected because: generic direct identifier leak

### Original

> Nadia Hassan, a 37-year-old violin maker from Flagstaff, visited Riverside Family Practice on August 2, 2025 (record MRN-710031, phone 202-555-1031, email nadia.hassan31@example.com). She reported sudden pleuritic chest pain and shortness of breath, with oxygen saturation was 89 percent on room air. CT angiography showed a segmental pulmonary embolism. Dr. Kim diagnosed pulmonary embolism and started apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily.

- Gold direct/private spans: Nadia Hassan; Riverside Family Practice; August 2, 2025; MRN-710031; 202-555-1031; nadia.hassan31@example.com; Dr. Kim
- Gold quasi-identifiers: 37-year-old; violin maker; Flagstaff
- Gold task-critical facts: sudden pleuritic chest pain and shortness of breath; oxygen saturation was 89 percent on room air; CT angiography showed a segmental pulmonary embolism; pulmonary embolism; apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily; 37-year-old
- Gold QA: What condition was diagnosed? -> pulmonary embolism; What anticoagulation plan was started? -> apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily

### Method summary

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA consistency | Fact-judge statuses |
|---|---|---|---:|---:|---:|---|
| generic_llm | August 2, 2025 | 37-year-old; violin maker | 0.667 | 1.000 | 0.500 | preserved=6 |
| privacy_first_llm | None | None | 0.167 | 0.333 | 0.500 | preserved=1, generalized_retained=1, omitted=4 |
| critical_span_guard_extracted | None | None | 1.000 | 1.000 | 1.000 | preserved=5, generalized_retained=1 |

### generic_llm

> A 37-year-old violin maker visited a healthcare facility on August 2, 2025. She reported sudden pleuritic chest pain and shortness of breath, with oxygen saturation at 89 percent on room air. CT angiography showed a segmental pulmonary embolism. The physician diagnosed pulmonary embolism and started anticoagulant therapy with apixaban 10 mg twice daily for 7 days, followed by 5 mg twice daily.

- Omitted facts by exact scorer: oxygen saturation was 89 percent on room air; apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: What anticoagulation plan was started?
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

### privacy_first_llm

> A middle-aged individual visited a healthcare facility on a specific date. They reported sudden chest pain and shortness of breath, with low oxygen saturation. Imaging revealed a pulmonary embolism. A healthcare provider diagnosed the condition and initiated anticoagulant therapy.

- Omitted facts by exact scorer: sudden pleuritic chest pain and shortness of breath; oxygen saturation was 89 percent on room air; CT angiography showed a segmental pulmonary embolism; apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily; 37-year-old
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: What anticoagulation plan was started?
- Not-retained facts by LLM judge: sudden pleuritic chest pain and shortness of breath; oxygen saturation was 89 percent on room air; CT angiography showed a segmental pulmonary embolism; apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily
- Contradicted facts by LLM judge: None

### critical_span_guard_extracted

> [PERSON], a late 30s worker from [LOCATION], visited [CLINIC] on [DATE] (record [ID]], phone [PHONE], email [EMAIL]). She reported sudden pleuritic chest pain and shortness of breath, with oxygen saturation was 89 percent on room air. CT angiography showed a segmental pulmonary embolism. [CLINICIAN] diagnosed pulmonary embolism and started apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily.

- Omitted facts by exact scorer: None
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

## legal_0001 (legal)

Selected because: generic direct identifier leak

### Original

> PROCEDURE The case originated in an application (no. 52363/11) against the French Republic lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a French national, Mr Philippe Bidart (“the applicant”), on 16 August 2011. The applicant alleged, in particular, that the restriction on freedom of expression imposed on him in the framework of his release on licence was contrary to Article 10 of the Convention.

- Gold direct/private spans: 52363/11; Mr Philippe Bidart; Philippe Bidart
- Gold quasi-identifiers: 16 August 2011
- Gold task-critical facts: Article 10; the restriction on freedom of expression imposed on him in the framework of his release on licence was contrary to Article 10 of the Convention
- Gold QA: Which substantive Article was invoked? -> Article 10; What core claim was raised? -> the restriction on freedom of expression imposed on him in the framework of his release on licence was contrary to Article 10 of the Convention

### Method summary

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA consistency | Fact-judge statuses |
|---|---|---|---:|---:|---:|---|
| generic_llm | 52363/11 | 16 August 2011 | 1.000 | 1.000 | 1.000 | preserved=2 |
| privacy_first_llm | None | None | 1.000 | 1.000 | 1.000 | preserved=2 |
| critical_span_guard_extracted | None | None | 1.000 | 1.000 | 1.000 | preserved=2 |

### generic_llm

> PROCEDURE The case originated in an application (no. 52363/11) against a State party lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, a named individual (“the applicant”), on 16 August 2011. The applicant alleged, in particular, that the restriction on freedom of expression imposed on him in the framework of his release on licence was contrary to Article 10 of the Convention.

- Omitted facts by exact scorer: None
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

### privacy_first_llm

> PROCEDURE The case originated in an application against a national government lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by an individual, on a specified date. The applicant alleged, in particular, that the restriction on freedom of expression imposed on them in the framework of their release on licence was contrary to Article 10 of the Convention.

- Omitted facts by exact scorer: None
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

### critical_span_guard_extracted

> PROCEDURE The case originated in an application [ID] against the Country lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a person, [PERSON], on [DATE]. The applicant alleged, in particular, that the restriction on freedom of expression imposed on him in the framework of his release on licence was contrary to Article 10 of the Convention.

- Omitted facts by exact scorer: None
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

## legal_0006 (legal)

Selected because: generic direct identifier leak

### Original

> PROCEDURE The case originated in an application (no. 37645/97) against the Republic of Poland lodged with the European Commission of Human Rights (“the Commission”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a Polish national, Mrs Helena Sawicka (“the applicant”), on 10 March 1997. The applicant alleged, in particular, that the civil proceedings in her case exceeded a reasonable time, contrary to Article 6 § 1 of the Convention. .

- Gold direct/private spans: 37645/97; Mrs Helena Sawicka
- Gold quasi-identifiers: 10 March 1997
- Gold task-critical facts: Article 6; the civil proceedings in her case exceeded a reasonable time, contrary to Article 6 § 1 of the Convention
- Gold QA: Which substantive Article was invoked? -> Article 6; What core claim was raised? -> the civil proceedings in her case exceeded a reasonable time, contrary to Article 6 § 1 of the Convention

### Method summary

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA consistency | Fact-judge statuses |
|---|---|---|---:|---:|---:|---|
| generic_llm | 37645/97 | 10 March 1997 | 1.000 | 1.000 | 1.000 | preserved=2 |
| privacy_first_llm | None | None | 0.500 | 0.000 | 0.500 | generalized_not_retained=1, omitted=1 |
| critical_span_guard_extracted | None | None | 1.000 | 1.000 | 1.000 | preserved=2 |

### generic_llm

> PROCEDURE The case originated in an application (no. 37645/97) against a State party lodged with the European Court of Human Rights (“the Court”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, a woman (“the applicant”), on 10 March 1997. The applicant alleged, in particular, that the civil proceedings in her case exceeded a reasonable time, contrary to Article 6 § 1 of the Convention.

- Omitted facts by exact scorer: None
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

### privacy_first_llm

> PROCEDURE The case originated in an application against a country lodged with the European human rights body under former provisions of a human rights treaty by a national of that country, on a specific date. The applicant alleged, in particular, that the civil proceedings in her case exceeded a reasonable time, contrary to a specified article of the treaty.

- Omitted facts by exact scorer: Article 6
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: Which substantive Article was invoked?
- Not-retained facts by LLM judge: Article 6; the civil proceedings in her case exceeded a reasonable time, contrary to Article 6 § 1 of the Convention
- Contradicted facts by LLM judge: None

### critical_span_guard_extracted

> PROCEDURE The case originated in an application ([ID]) against [COUNTRY] lodged with [INSTITUTION] under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a [NATIONALITY] national, [NAME], on [DATE]. The applicant alleged, in particular, that the civil proceedings in her case exceeded a reasonable time, contrary to Article 6  1 of the Convention.

- Omitted facts by exact scorer: None
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

## legal_0018 (legal)

Selected because: lowest exact-TCFR CSG case; privacy-first legal utility loss

### Original

> PROCEDURE The case originated in an application (no. 35179/97) against the Kingdom of Sweden lodged with the European Commission of Human Rights (“the Commission”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a Swedish national, Ms Inga Allard (“the applicant”), on 27 November 1996. The applicant alleged, in particular, that the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively.

- Gold direct/private spans: 35179/97; Ms Inga Allard
- Gold quasi-identifiers: 27 November 1996
- Gold task-critical facts: Article 1; the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively
- Gold QA: Which substantive Article was invoked? -> Article 1; What core claim was raised? -> the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 ...

### Method summary

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA consistency | Fact-judge statuses |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | None | 1.000 | 1.000 | 1.000 | preserved=2 |
| privacy_first_llm | None | None | 0.000 | 0.000 | 0.000 | omitted=2 |
| critical_span_guard_extracted | None | None | 0.500 | 1.000 | 0.500 | preserved=2 |

### generic_llm

> PROCEDURE The case originated in an application against a Member State lodged with the European Court of Human Rights (“the Court”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, a female applicant, on a specified date. The applicant alleged, in particular, that the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively.

- Omitted facts by exact scorer: None
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

### privacy_first_llm

> PROCEDURE The case originated in an application against a European country lodged with the European human rights body under a former article of a human rights convention by a national of that country, on a specific date. The applicant alleged that the demolition of a house had violated her rights to peaceful enjoyment of possessions and to respect for her home under relevant articles of the convention.

- Omitted facts by exact scorer: Article 1; the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: Which substantive Article was invoked?; What core claim was raised?
- Not-retained facts by LLM judge: Article 1; the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively
- Contradicted facts by LLM judge: None

### critical_span_guard_extracted

> PROCEDURE The case originated in an application [ID] against the Kingdom of Sweden lodged with the European human rights body under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national, [PERSON], on [DATE]. The applicant alleged, in particular, that the demolition of a house had violated her rights to peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively.

- Omitted facts by exact scorer: the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: What core claim was raised?
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

## legal_0043 (legal)

Selected because: largest CSG vs privacy-first utility gap

### Original

> PROCEDURE The case originated in an application (no. 37770/97) against the Republic of Poland lodged with the European Commission of Human Rights (“the Commission”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a Polish national, Andrzej Krzewicki (“the applicant”), on 19 July 1997. On 20 April 1996 the applicant complained, invoking Article 6 of the Convention, about the length of the proceedings to the President of the Łódź Regional Court.

- Gold direct/private spans: 37770/97; Andrzej Krzewicki
- Gold quasi-identifiers: Polish; 19 July 1997; Łódź Regional Court; 20 April 1996
- Gold task-critical facts: Article 6
- Gold QA: Which substantive Article was invoked? -> Article 6

### Method summary

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA consistency | Fact-judge statuses |
|---|---|---|---:|---:|---:|---|
| generic_llm | 37770/97 | 19 July 1997; 20 April 1996 | 1.000 | 1.000 | 1.000 | preserved=1 |
| privacy_first_llm | None | None | 0.000 | 0.000 | 0.000 | omitted=1 |
| critical_span_guard_extracted | None | None | 1.000 | 1.000 | 1.000 | preserved=1 |

### generic_llm

> PROCEDURE The case originated in an application (no. 37770/97) against a country lodged with the European Commission of Human Rights (“the Commission”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, a person, on 19 July 1997. On 20 April 1996 the applicant complained, invoking Article 6 of the Convention, about the length of the proceedings to the President of a regional court.

- Omitted facts by exact scorer: None
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

### privacy_first_llm

> PROCEDURE The case originated in an application against a national government lodged with an international human rights body under a former human rights treaty by an individual, on a specific date. The applicant had previously complained about the length of legal proceedings to a regional court authority.

- Omitted facts by exact scorer: Article 6
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: Which substantive Article was invoked?
- Not-retained facts by LLM judge: Article 6
- Contradicted facts by LLM judge: None

### critical_span_guard_extracted

> PROCEDURE The case originated in an application [ID] against [REDACTED_COUNTRY] lodged with [REDACTED_INSTITUTION] under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a [REDACTED_PERSON], on [REDACTED_DATE]. On [REDACTED_DATE], the applicant complained, invoking Article 6 of the Convention, about the length of the proceedings to the President of the [REDACTED_COURT].

- Omitted facts by exact scorer: None
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

## legal_0049 (legal)

Selected because: CSG closes generic direct leak on same example

### Original

> PROCEDURE The case originated in an application (no. 33176/06) against the Republic of Poland lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a Polish national, Mr Sebastian Gulczyński (“the applicant”), on 8 August 2006. The applicant alleged, in particular, that his detention on remand had exceeded a “reasonable time” within the meaning of Article 5 § 3 of the Convention.

- Gold direct/private spans: 33176/06; Mr Sebastian Gulczyński
- Gold quasi-identifiers: 8 August 2006
- Gold task-critical facts: Article 5; his detention on remand had exceeded a “reasonable time” within the meaning of Article 5 § 3 of the Convention
- Gold QA: Which substantive Article was invoked? -> Article 5; What core claim was raised? -> his detention on remand had exceeded a “reasonable time” within the meaning of Article 5 § 3 of the Convention

### Method summary

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA consistency | Fact-judge statuses |
|---|---|---|---:|---:|---:|---|
| generic_llm | 33176/06 | 8 August 2006 | 1.000 | 1.000 | 1.000 | preserved=2 |
| privacy_first_llm | None | None | 1.000 | 1.000 | 1.000 | preserved=2 |
| critical_span_guard_extracted | None | None | 1.000 | 1.000 | 1.000 | preserved=2 |

### generic_llm

> PROCEDURE The case originated in an application (no. 33176/06) against a State Party lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, a male individual (“the applicant”), on 8 August 2006. The applicant alleged, in particular, that his detention on remand had exceeded a “reasonable time” within the meaning of Article 5 § 3 of the Convention.

- Omitted facts by exact scorer: None
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

### privacy_first_llm

> PROCEDURE The case originated in an application against a national government lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, the applicant, on a specified date. The applicant alleged, in particular, that his detention on remand had exceeded a “reasonable time” within the meaning of Article 5 § 3 of the Convention.

- Omitted facts by exact scorer: None
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

### critical_span_guard_extracted

> PROCEDURE The case originated in an application [ID] against the [REDACTED_COUNTRY] lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a [REDACTED_COUNTRY] national, [REDACTED_NAME], on [REDACTED_DATE]. The applicant alleged, in particular, that his detention on remand had exceeded a “reasonable time” within the meaning of Article 5 § 3 of the Convention.

- Omitted facts by exact scorer: None
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

