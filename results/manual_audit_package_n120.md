# Manual Audit Package

This package selects high-signal rows from the cached 120-example LLM run for human review.

## Audit checklist

- Privacy: did the output retain a direct identifier, case number, institution, exact age, rare occupation, or other re-identification cue?
- Utility: are diagnosis/claim, article/statute, dose/value, outcome, chronology, and downstream answer still recoverable?
- Faithfulness: did anonymization introduce a new fact or contradict a task-critical fact?
- Scorer disagreement: does deterministic exact matching undercount a faithful paraphrase?

## Candidate index

| Example | Domain | Why selected |
|---|---|---|
| clinical_0000 | clinical | privacy-first clinical utility loss |
| clinical_0011 | clinical | generic direct identifier leak; lowest exact-TCFR CSG case |
| clinical_0021 | clinical | CSG exact-match undercount candidate |
| clinical_0031 | clinical | generic direct identifier leak |
| legal_0001 | legal | generic direct identifier leak |
| legal_0002 | legal | privacy-first legal utility loss |
| legal_0043 | legal | largest CSG vs privacy-first utility gap |
| legal_0058 | legal | CSG closes generic direct leak on same example |

## clinical_0000 (clinical)

Selected because: privacy-first clinical utility loss

### Original

> Maria Lopez, a 24-year-old teacher from Santa Fe, visited North Ridge Clinic on January 1, 2025 (record MRN-710000, phone 202-555-1000, email maria.lopez0@example.com). She reported 3 weeks of morning stiffness in both hands, with swelling of the MCP joints. anti-CCP was positive. Dr. O'Connor diagnosed rheumatoid arthritis and started methotrexate 15 mg weekly and folic acid 1 mg daily.

- Gold direct/private spans: Maria Lopez; North Ridge Clinic; January 1, 2025; MRN-710000; 202-555-1000; maria.lopez0@example.com; Dr. O'Connor
- Gold quasi-identifiers: 24-year-old; teacher; Santa Fe
- Gold task-critical facts: 3 weeks of morning stiffness in both hands; swelling of the MCP joints; anti-CCP was positive; rheumatoid arthritis; methotrexate 15 mg weekly and folic acid 1 mg daily; 24-year-old
- Gold QA: What medication was started? -> methotrexate 15 mg weekly and folic acid 1 mg daily; Which lab result supported the suspected diagnosis? -> anti-CCP was positive

### Method summary

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA consistency | Fact-judge statuses |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | 24-year-old; teacher | 0.833 | 0.833 | 1.000 | preserved=5, omitted=1 |
| privacy_first_llm | None | None | 0.000 | 0.500 | 0.000 | preserved=2, generalized_retained=1, omitted=3 |
| critical_span_guard_extracted | None | None | 0.833 | 1.000 | 1.000 | preserved=5, generalized_retained=1 |

### generic_llm

> A 24-year-old teacher from a city in the southwestern region visited a clinic on a specified date. She reported three weeks of morning stiffness in both hands, with swelling of the MCP joints. Anti-CCP was positive. The physician diagnosed rheumatoid arthritis and started methotrexate 15 mg weekly and folic acid 1 mg daily.

- Omitted facts by exact scorer: 3 weeks of morning stiffness in both hands
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: 3 weeks of morning stiffness in both hands
- Contradicted facts by LLM judge: None

### privacy_first_llm

> A young adult patient visited a healthcare clinic on a specific date. She reported several weeks of morning stiffness in both hands, with swelling of the finger joint areas. Laboratory testing showed positive results for a particular antibody. The healthcare provider diagnosed an autoimmune joint condition and initiated treatment with a weekly medication and daily supplement.

- Omitted facts by exact scorer: 3 weeks of morning stiffness in both hands; swelling of the MCP joints; anti-CCP was positive; rheumatoid arthritis; methotrexate 15 mg weekly and folic acid 1 mg daily; 24-year-old
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: What medication was started?; Which lab result supported the suspected diagnosis?
- Not-retained facts by LLM judge: 3 weeks of morning stiffness in both hands; swelling of the MCP joints; methotrexate 15 mg weekly and folic acid 1 mg daily
- Contradicted facts by LLM judge: None

### critical_span_guard_extracted

> [PATIENT], an adolescent adult worker from [REDACTED_CITY], visited [REDACTED_CLINIC] on [REDACTED_DATE] (record [REDACTED_MRN], phone [REDACTED_PHONE], email [REDACTED_EMAIL]). She reported 3 weeks of morning stiffness in both hands, with swelling of the MCP joints. anti-CCP was positive. [CLINICIAN] diagnosed rheumatoid arthritis and started methotrexate 15 mg weekly and folic acid 1 mg daily.

- Omitted facts by exact scorer: 24-year-old
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

## clinical_0011 (clinical)

Selected because: generic direct identifier leak; lowest exact-TCFR CSG case

### Original

> Elena Petrova, a 33-year-old farm manager from Tucson, visited Riverside Family Practice on December 24, 2025 (record MRN-710011, phone 202-555-1011, email elena.petrova11@example.com). She reported 18 hours of periumbilical pain that migrated to the right lower quadrant, with rebound tenderness was present at McBurney's point. CT abdomen showed an enlarged appendix with periappendiceal fat stranding. Dr. Singh diagnosed acute appendicitis and started ceftriaxone and metronidazole before laparoscopic appendectomy.

- Gold direct/private spans: Elena Petrova; Riverside Family Practice; December 24, 2025; MRN-710011; 202-555-1011; elena.petrova11@example.com; Dr. Singh
- Gold quasi-identifiers: 33-year-old; farm manager; Tucson
- Gold task-critical facts: 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; CT abdomen showed an enlarged appendix with periappendiceal fat stranding; acute appendicitis; ceftriaxone and metronidazole before laparoscopic appendectomy; 33-year-old
- Gold QA: What did the CT abdomen show? -> enlarged appendix with periappendiceal fat stranding; What procedure was planned? -> laparoscopic appendectomy

### Method summary

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA consistency | Fact-judge statuses |
|---|---|---|---:|---:|---:|---|
| generic_llm | December 24, 2025 | 33-year-old; farm manager | 0.500 | 0.833 | 1.000 | preserved=5, omitted=1 |
| privacy_first_llm | None | None | 0.167 | 0.500 | 0.000 | preserved=2, generalized_retained=1, omitted=3 |
| critical_span_guard_extracted | None | None | 0.333 | 1.000 | 1.000 | preserved=5, generalized_retained=1 |

### generic_llm

> A 33-year-old farm manager from a southwestern city visited a local family practice clinic on December 24, 2025. She reported 18 hours of periumbilical pain that migrated to the right lower quadrant, with rebound tenderness present at McBurney's point. Imaging of the abdomen showed an enlarged appendix with periappendiceal fat stranding. The physician diagnosed acute appendicitis and initiated antibiotic therapy before laparoscopic appendectomy.

- Omitted facts by exact scorer: rebound tenderness was present at McBurney's point; CT abdomen showed an enlarged appendix with periappendiceal fat stranding; ceftriaxone and metronidazole before laparoscopic appendectomy
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: ceftriaxone and metronidazole before laparoscopic appendectomy
- Contradicted facts by LLM judge: None

### privacy_first_llm

> A patient in their early thirties visited a healthcare facility on a specific date. They reported several hours of abdominal pain that migrated to the lower right area, with rebound tenderness at a specific point. Imaging studies indicated an enlarged appendix with surrounding fat changes. The healthcare provider diagnosed acute appendicitis and initiated antibiotic treatment before surgical removal of the appendix.

- Omitted facts by exact scorer: 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; CT abdomen showed an enlarged appendix with periappendiceal fat stranding; ceftriaxone and metronidazole before laparoscopic ...
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: What did the CT abdomen show?; What procedure was planned?
- Not-retained facts by LLM judge: 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; ceftriaxone and metronidazole before laparoscopic appendectomy
- Contradicted facts by LLM judge: None

### critical_span_guard_extracted

> [PERSON], a [AGE]-year-old from [LOCATION], visited [CLINIC] on [DATE] (record [ID]], phone [PHONE], email [EMAIL]). She reported 18 hours of periumbilical pain migrating to the right lower quadrant, with rebound tenderness at McBurney's point. CT abdomen showed an enlarged appendix with periappendiceal fat stranding. [CLINICIAN] diagnosed acute appendicitis and started [MEDICATIONS] before laparoscopic appendectomy.

- Omitted facts by exact scorer: 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; ceftriaxone and metronidazole before laparoscopic appendectomy; 33-year-old
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

## clinical_0021 (clinical)

Selected because: CSG exact-match undercount candidate

### Original

> Grace Chen, a 35-year-old long-haul driver from Boise, visited Riverside Family Practice on October 13, 2025 (record MRN-710021, phone 202-555-1021, email grace.chen21@example.com). She reported 5 days of fever, productive cough, and right-sided chest pain, with oxygen saturation was 88 percent on room air. chest x-ray showed a right lower-lobe infiltrate. Dr. Patel diagnosed community-acquired pneumonia and started ceftriaxone 1 g daily and azithromycin 500 mg daily.

- Gold direct/private spans: Grace Chen; Riverside Family Practice; October 13, 2025; MRN-710021; 202-555-1021; grace.chen21@example.com; Dr. Patel
- Gold quasi-identifiers: 35-year-old; long-haul driver; Boise
- Gold task-critical facts: 5 days of fever, productive cough, and right-sided chest pain; oxygen saturation was 88 percent on room air; chest x-ray showed a right lower-lobe infiltrate; community-acquired pneumonia; ceftriaxone 1 g daily and azithromycin 500 mg daily; 35-year-old
- Gold QA: What did the chest x-ray show? -> right lower-lobe infiltrate; Which antibiotics were ordered? -> ceftriaxone 1 g daily and azithromycin 500 mg daily

### Method summary

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA consistency | Fact-judge statuses |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | 35-year-old; long-haul driver | 0.833 | 1.000 | 1.000 | preserved=6 |
| privacy_first_llm | None | None | 0.167 | 0.333 | 0.000 | preserved=1, generalized_retained=1, omitted=4 |
| critical_span_guard_extracted | None | None | 0.833 | 1.000 | 1.000 | preserved=5, generalized_retained=1 |

### generic_llm

> A 35-year-old long-haul driver from a city visited a family practice clinic on a specified date. She reported 5 days of fever, productive cough, and right-sided chest pain, with oxygen saturation at 88 percent on room air. Chest x-ray showed a right lower-lobe infiltrate. The healthcare provider diagnosed community-acquired pneumonia and started ceftriaxone 1 g daily and azithromycin 500 mg daily.

- Omitted facts by exact scorer: oxygen saturation was 88 percent on room air
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

### privacy_first_llm

> A middle-aged individual from a metropolitan area visited a healthcare facility on a recent date. They reported several days of fever, productive cough, and chest pain, with oxygen saturation below normal levels. Imaging showed a lung infiltrate. A healthcare provider diagnosed community-acquired pneumonia and initiated antibiotic treatment.

- Omitted facts by exact scorer: 5 days of fever, productive cough, and right-sided chest pain; oxygen saturation was 88 percent on room air; chest x-ray showed a right lower-lobe infiltrate; ceftriaxone 1 g daily and azithromycin 500 mg daily; 35-year-old
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: What did the chest x-ray show?; Which antibiotics were ordered?
- Not-retained facts by LLM judge: 5 days of fever, productive cough, and right-sided chest pain; oxygen saturation was 88 percent on room air; chest x-ray showed a right lower-lobe infiltrate; ceftriaxone 1 g daily and azithromycin 500 mg daily
- Contradicted facts by LLM judge: None

### critical_span_guard_extracted

> [REDACTED_NAME], an adult worker from [REDACTED_CITY], visited [REDACTED_CLINIC] on [REDACTED_DATE] (record [REDACTED_MRN], phone [REDACTED_PHONE], email [REDACTED_EMAIL]). She reported 5 days of fever, productive cough, and right-sided chest pain, with oxygen saturation was 88 percent on room air. chest x-ray showed a right lower-lobe infiltrate. [CLINICIAN] diagnosed community-acquired pneumonia and started ceftriaxone 1 g daily and azithromycin 500 mg daily.

- Omitted facts by exact scorer: 35-year-old
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

## legal_0002 (legal)

Selected because: privacy-first legal utility loss

### Original

> PROCEDURE The case originated in two applications (nos. 43208/98 and 44875/98) against the United Kingdom lodged with the European Commission of Human Rights (“the Commission”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by two United Kingdom nationals, Mr Terence Perkins and Ms R. The applicants alleged that an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces that existed at the time violated their rights under Article 8, alone and in conjunction with Article 14 of the Convention.

- Gold direct/private spans: 43208/98; 44875/98; Mr Terence Perkins
- Gold quasi-identifiers: Ms R.; homosexuality; homosexuals; homosexual
- Gold task-critical facts: Article 8; an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces that existed at the time violated their rights under Article 8, alone and in ...
- Gold QA: Which substantive Article was invoked? -> Article 8; What core claim was raised? -> an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of ...

### Method summary

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA consistency | Fact-judge statuses |
|---|---|---|---:|---:|---:|---|
| generic_llm | None | homosexuality; homosexuals; homosexual | 0.500 | 1.000 | 0.500 | preserved=2 |
| privacy_first_llm | None | homosexuality; homosexual | 0.000 | 0.500 | 0.000 | preserved=1, generalized_not_retained=1 |
| critical_span_guard_extracted | None | homosexuality; homosexuals; homosexual | 0.500 | 1.000 | 0.500 | preserved=2 |

### generic_llm

> PROCEDURE The case originated in two applications against a member state lodged with the European Commission of Human Rights (“the Commission”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by two nationals of that country. The applicants alleged that an investigation into their sexuality and their discharge from the military service on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces that existed at the time violated their rights under Article 8, alone and in conjunction with Article 14 of the Convention.

- Omitted facts by exact scorer: an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces that existed at the time violated their rights ...
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: What core claim was raised?
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

### privacy_first_llm

> PROCEDURE The case originated in two applications against a European country lodged with a human rights commission under a former human rights treaty by two nationals of that country. The applicants alleged that an investigation into their sexuality and their discharge from a military service on the basis of their homosexuality, due to a policy against the presence of individuals with same-sex orientation in the armed forces at the time, violated their rights under a privacy provision, alone and in conjunction with a non-discrimination provision of the treaty.

- Omitted facts by exact scorer: Article 8; an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces that existed at the time violated their ...
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: Which substantive Article was invoked?; What core claim was raised?
- Not-retained facts by LLM judge: an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces that existed at the time violated their rights ...
- Contradicted facts by LLM judge: None

### critical_span_guard_extracted

> PROCEDURE The case originated in two applications [ID] against [LOCATION] lodged with the European Commission of Human Rights (“the Commission”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by two [COUNTRY] nationals, [PERSON_NAME_1] and [PERSON_NAME_2]. The applicants alleged that an investigation into their sexuality and their discharge from the [MILITARY_BRANCH] on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces that existed at the time violated their rights under Article 8, alone and in conjunction with Article 14 of the Convention.

- Omitted facts by exact scorer: an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces that existed at the time violated their rights ...
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

## legal_0058 (legal)

Selected because: CSG closes generic direct leak on same example

### Original

> PROCEDURE The case originated in an application (no. 31881/02) against the Republic of Turkey lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a Turkish national, Mr Bedran Gencer (“the applicant”), on 22 July 2002. He relied on Articles 6, 13, 14 and 18 of the Convention and Article 1 of Protocol No. 1.

- Gold direct/private spans: 31881/02; Mr Bedran Gencer
- Gold quasi-identifiers: 22 July 2002
- Gold task-critical facts: Article 1
- Gold QA: Which substantive Article was invoked? -> Article 1

### Method summary

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA consistency | Fact-judge statuses |
|---|---|---|---:|---:|---:|---|
| generic_llm | 31881/02 | 22 July 2002 | 1.000 | 1.000 | 1.000 | preserved=1 |
| privacy_first_llm | None | None | 1.000 | 1.000 | 1.000 | preserved=1 |
| critical_span_guard_extracted | None | None | 1.000 | 1.000 | 1.000 | preserved=1 |

### generic_llm

> PROCEDURE The case originated in an application (no. 31881/02) against a country, lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a national of that country, a person, on 22 July 2002. The applicant relied on Articles 6, 13, 14, and 18 of the Convention and Article 1 of Protocol No. 1.

- Omitted facts by exact scorer: None
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

### privacy_first_llm

> PROCEDURE The case originated in an application against a national government lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by an individual, on a specified date. The applicant relied on Articles 6, 13, 14, and 18 of the Convention and Article 1 of Protocol No. 1.

- Omitted facts by exact scorer: None
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

### critical_span_guard_extracted

> PROCEDURE The case originated in an application [ID] against [REDACTED_COUNTRY] lodged with the Court under Article 34 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a [REDACTED_COUNTRY] national, [REDACTED_NAME] (“the applicant”), on [REDACTED_DATE]. He relied on Articles 6, 13, 14 and 18 of the Convention and Article 1 of Protocol No. 1.

- Omitted facts by exact scorer: None
- Contradicted facts by exact scorer: None
- Failed QA by exact scorer: None
- Not-retained facts by LLM judge: None
- Contradicted facts by LLM judge: None

