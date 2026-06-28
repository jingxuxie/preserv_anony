# Fixed Sample Manual Audit

Generated: 2026-06-28

This is a fixed 30-example transparent subset audit for the n120 bounded OpenAI expansion. It uses existing deterministic metrics and cached fact-judge evidence only; no new API calls were made.
Scope caveat: this is a single-author/manual-style audit packet, not an independent multi-annotator study or inter-rater agreement result.

## Fixed Sample

- Fixed sample: 30 examples (clinical=15, legal=15), all 3 methods per example.
- Method rows audited: 90.
- Required caveats included: strict-specificity/audited-loss rows `clinical_0055`, `clinical_0059`, `legal_0016`; residual-QI rows `legal_0002`, `legal_0005`, `legal_0025`, `legal_0042`, `legal_0046`, `legal_0053`, `legal_0054`, `legal_0055`, `legal_0056`.
- Selection rule: include foreground/caveat cases first, then deterministically fill each domain to 15 examples using direct leaks, QI retention, privacy-first utility loss, CSG caveats, exact-metric artifacts, and clean CSG controls.

## Method-Row Summary

| Method | Rows | Direct-leak rows | QI-hit rows | Audited fact-loss rows | Exact QA-failure rows | Exact-match artifact rows | Clean rows |
|---|---:|---:|---:|---:|---:|---:|---:|
| generic_llm | 30 | 8 | 26 | 14 | 15 | 18 | 1 |
| privacy_first_llm | 30 | 0 | 11 | 26 | 28 | 19 | 0 |
| critical_span_guard_extracted | 30 | 0 | 9 | 3 | 4 | 16 | 6 |

## Selected Examples

| Example | Domain | Selected because | CSG labels |
|---|---|---|---|
| `clinical_0005` | clinical | CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss | exact_fact_omission; exact_match_artifact |
| `clinical_0006` | clinical | foreground clinical utility-loss example; clean CSG row; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss | clean |
| `clinical_0009` | clinical | CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss | exact_fact_omission; exact_match_artifact |
| `clinical_0011` | clinical | CSG exact-match artifact; exact metric undercount; generic direct identifier leak; generic quasi-identifier retention; privacy-first utility loss | exact_fact_omission; exact_match_artifact |
| `clinical_0012` | clinical | CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss | exact_fact_omission; exact_match_artifact |
| `clinical_0017` | clinical | CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss | exact_fact_omission; exact_match_artifact |
| `clinical_0023` | clinical | CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss | exact_fact_omission; exact_match_artifact |
| `clinical_0029` | clinical | CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss | exact_fact_omission; exact_match_artifact |
| `clinical_0031` | clinical | clean CSG row; exact metric undercount; generic direct identifier leak; generic quasi-identifier retention; privacy-first utility loss | clean |
| `clinical_0035` | clinical | CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss | exact_fact_omission; exact_match_artifact |
| `clinical_0040` | clinical | CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss | exact_fact_omission; exact_match_artifact |
| `clinical_0041` | clinical | CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss | exact_fact_omission; exact_match_artifact |
| `clinical_0053` | clinical | CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss | exact_fact_omission; exact_match_artifact |
| `clinical_0055` | clinical | CSG strict-specificity audited loss; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss | audited_fact_loss; exact_fact_omission; csg_strict_specificity_loss |
| `clinical_0059` | clinical | CSG exact-match artifact; CSG strict-specificity audited loss; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss | audited_fact_loss; exact_fact_omission; exact_match_artifact; csg_strict_specificity_loss |
| `legal_0002` | legal | residual CSG legal QI frontier row; CSG exact-match artifact; CSG residual quasi-identifier; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss | quasi_identifier_retained; exact_fact_omission; exact_qa_failure; exact_match_artifact; csg_residual_qi_frontier |
| `legal_0005` | legal | residual CSG legal QI frontier row; CSG residual quasi-identifier; exact metric undercount; privacy-first utility loss | quasi_identifier_retained; csg_residual_qi_frontier |
| `legal_0006` | legal | foreground legal privacy-utility example; clean CSG row; generic direct identifier leak; generic quasi-identifier retention; privacy-first utility loss | clean |
| `legal_0016` | legal | strict legal-specificity audited utility caveat; CSG strict-specificity audited loss; generic quasi-identifier retention; privacy-first utility loss | audited_fact_loss; csg_strict_specificity_loss |
| `legal_0018` | legal | exact-vs-audited legal metric nuance; CSG exact-match artifact; exact metric undercount; privacy-first utility loss | exact_fact_omission; exact_qa_failure; exact_match_artifact |
| `legal_0021` | legal | clean CSG row; generic direct identifier leak; generic quasi-identifier retention; privacy-first utility loss | clean |
| `legal_0025` | legal | residual CSG legal QI frontier row; CSG residual quasi-identifier; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss | quasi_identifier_retained; csg_residual_qi_frontier |
| `legal_0037` | legal | clean CSG row; generic direct identifier leak; generic quasi-identifier retention; privacy-first utility loss | clean |
| `legal_0042` | legal | residual CSG legal QI frontier row; CSG residual quasi-identifier; generic quasi-identifier retention | quasi_identifier_retained; csg_residual_qi_frontier |
| `legal_0043` | legal | clean CSG row; generic direct identifier leak; generic quasi-identifier retention; privacy-first utility loss | clean |
| `legal_0046` | legal | residual CSG legal QI frontier row; CSG residual quasi-identifier; generic quasi-identifier retention; privacy-first utility loss | quasi_identifier_retained; csg_residual_qi_frontier |
| `legal_0053` | legal | residual CSG legal QI frontier row; CSG residual quasi-identifier; generic direct identifier leak; generic quasi-identifier retention; privacy-first utility loss | quasi_identifier_retained; csg_residual_qi_frontier |
| `legal_0054` | legal | residual CSG legal QI frontier row; CSG exact-match artifact; CSG residual quasi-identifier; exact metric undercount; privacy-first utility loss | quasi_identifier_retained; exact_fact_omission; exact_qa_failure; exact_match_artifact; csg_residual_qi_frontier |
| `legal_0055` | legal | residual CSG legal QI frontier row; CSG residual quasi-identifier; generic direct identifier leak; generic quasi-identifier retention | quasi_identifier_retained; csg_residual_qi_frontier |
| `legal_0056` | legal | residual CSG legal QI frontier row; CSG exact-match artifact; CSG residual quasi-identifier; exact metric undercount; privacy-first utility loss | quasi_identifier_retained; exact_fact_omission; exact_qa_failure; exact_match_artifact; csg_residual_qi_frontier |

## Row-Level Audit

### `clinical_0005` (clinical)

- Selected because: CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; CT abdomen showed an enlarged appendix with periappendiceal fat stranding; acute appendicitis; ceftriaxone and metronidazole ...
- Gold QA: What did the CT abdomen show? -> enlarged appendix with periappendiceal fat stranding; What procedure was planned? -> laparoscopic appendectomy
- Gold direct identifiers: Grace Chen; Riverside Family Practice; June 9, 2025; MRN-710005; 202-555-1005; grace.chen5@example.com; Dr. Singh
- Gold quasi-identifiers: 59-year-old; long-haul driver; Boise

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | 59-year-old; long-haul driver | 0.500 | 0.667 | 0.500 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; generic_privacy_leak | rebound tenderness was present at McBurney's point; ceftriaxone and metronidazole before laparoscopic appendectomy |
| privacy_first_llm | None | None | 0.167 | 0.500 | 0.000 | audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; ceftriaxone and metronidazole ... |
| critical_span_guard_extracted | None | None | 0.833 | 1.000 | 1.000 | exact_fact_omission; exact_match_artifact | None |

### `clinical_0006` (clinical)

- Selected because: foreground clinical utility-loss example; clean CSG row; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: 3 weeks of morning stiffness in both hands; swelling of the MCP joints; anti-CCP was positive; rheumatoid arthritis; methotrexate 15 mg weekly and folic acid 1 mg daily; 66-year-old
- Gold QA: What medication was started? -> methotrexate 15 mg weekly and folic acid 1 mg daily; Which lab result supported the suspected diagnosis? -> anti-CCP was positive
- Gold direct identifiers: Samuel Ortiz; North Ridge Clinic; July 16, 2025; MRN-710006; 202-555-1006; samuel.ortiz6@example.com; Dr. Patel
- Gold quasi-identifiers: 66-year-old; postal worker; Asheville

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | 66-year-old; postal worker | 0.833 | 1.000 | 1.000 | quasi_identifier_retained; exact_fact_omission; exact_match_artifact; generic_privacy_leak | None |
| privacy_first_llm | None | postal worker | 0.000 | 0.333 | 0.000 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | swelling of the MCP joints; anti-CCP was positive; rheumatoid arthritis; methotrexate 15 mg weekly and folic acid 1 mg daily |
| critical_span_guard_extracted | None | None | 1.000 | 1.000 | 1.000 | clean | None |

### `clinical_0009` (clinical)

- Selected because: CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: 5 days of fever, productive cough, and right-sided chest pain; oxygen saturation was 88 percent on room air; chest x-ray showed a right lower-lobe infiltrate; community-acquired pneumonia; ceftriaxone 1 g daily and azithromycin 500 mg daily; 87-year-old
- Gold QA: What did the chest x-ray show? -> right lower-lobe infiltrate; Which antibiotics were ordered? -> ceftriaxone 1 g daily and azithromycin 500 mg daily
- Gold direct identifiers: Anthony Reed; Riverside Family Practice; October 10, 2025; MRN-710009; 202-555-1009; anthony.reed9@example.com; Dr. Patel
- Gold quasi-identifiers: 87-year-old; software engineer; Reno

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | software engineer | 0.500 | 0.833 | 1.000 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_match_artifact; generic_privacy_leak | 5 days of fever, productive cough, and right-sided chest pain |
| privacy_first_llm | None | software engineer | 0.167 | 0.333 | 0.000 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | 5 days of fever, productive cough, and right-sided chest pain; oxygen saturation was 88 percent on room air; chest x-ray showed a right lower-lobe ... |
| critical_span_guard_extracted | None | None | 0.833 | 1.000 | 1.000 | exact_fact_omission; exact_match_artifact | None |

### `clinical_0011` (clinical)

- Selected because: CSG exact-match artifact; exact metric undercount; generic direct identifier leak; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; CT abdomen showed an enlarged appendix with periappendiceal fat stranding; acute appendicitis; ceftriaxone and metronidazole ...
- Gold QA: What did the CT abdomen show? -> enlarged appendix with periappendiceal fat stranding; What procedure was planned? -> laparoscopic appendectomy
- Gold direct identifiers: Elena Petrova; Riverside Family Practice; December 24, 2025; MRN-710011; 202-555-1011; elena.petrova11@example.com; Dr. Singh
- Gold quasi-identifiers: 33-year-old; farm manager; Tucson

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | December 24, 2025 | 33-year-old; farm manager | 0.500 | 0.833 | 1.000 | direct_identifier_leak; quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_match_artifact; generic_privacy_leak | ceftriaxone and metronidazole before laparoscopic appendectomy |
| privacy_first_llm | None | None | 0.167 | 0.500 | 0.000 | audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; ceftriaxone and metronidazole ... |
| critical_span_guard_extracted | None | None | 0.333 | 1.000 | 1.000 | exact_fact_omission; exact_match_artifact | None |

### `clinical_0012` (clinical)

- Selected because: CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: 3 weeks of morning stiffness in both hands; swelling of the MCP joints; anti-CCP was positive; rheumatoid arthritis; methotrexate 15 mg weekly and folic acid 1 mg daily; 40-year-old
- Gold QA: What medication was started? -> methotrexate 15 mg weekly and folic acid 1 mg daily; Which lab result supported the suspected diagnosis? -> anti-CCP was positive
- Gold direct identifiers: James Walker; North Ridge Clinic; January 4, 2025; MRN-710012; 202-555-1012; james.walker12@example.com; Dr. Patel
- Gold quasi-identifiers: 40-year-old; retired judge; Madison

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | 40-year-old; retired judge | 0.833 | 1.000 | 1.000 | quasi_identifier_retained; exact_fact_omission; exact_match_artifact; generic_privacy_leak | None |
| privacy_first_llm | None | retired judge | 0.000 | 0.167 | 0.000 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | 3 weeks of morning stiffness in both hands; swelling of the MCP joints; anti-CCP was positive; rheumatoid arthritis; methotrexate 15 mg weekly and folic ... |
| critical_span_guard_extracted | None | None | 0.833 | 1.000 | 1.000 | exact_fact_omission; exact_match_artifact | None |

### `clinical_0017` (clinical)

- Selected because: CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; CT abdomen showed an enlarged appendix with periappendiceal fat stranding; acute appendicitis; ceftriaxone and metronidazole ...
- Gold QA: What did the CT abdomen show? -> enlarged appendix with periappendiceal fat stranding; What procedure was planned? -> laparoscopic appendectomy
- Gold direct identifiers: Anthony Reed; Riverside Family Practice; June 12, 2025; MRN-710017; 202-555-1017; anthony.reed17@example.com; Dr. Singh
- Gold quasi-identifiers: 75-year-old; software engineer; Reno

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | 75-year-old; software engineer | 0.500 | 0.833 | 0.500 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; generic_privacy_leak | rebound tenderness was present at McBurney's point |
| privacy_first_llm | None | None | 0.167 | 0.500 | 0.000 | audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; ceftriaxone and metronidazole ... |
| critical_span_guard_extracted | None | None | 0.667 | 1.000 | 1.000 | exact_fact_omission; exact_match_artifact | None |

### `clinical_0023` (clinical)

- Selected because: CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; CT abdomen showed an enlarged appendix with periappendiceal fat stranding; acute appendicitis; ceftriaxone and metronidazole ...
- Gold QA: What did the CT abdomen show? -> enlarged appendix with periappendiceal fat stranding; What procedure was planned? -> laparoscopic appendectomy
- Gold direct identifiers: Nadia Hassan; Riverside Family Practice; December 27, 2025; MRN-710023; 202-555-1023; nadia.hassan23@example.com; Dr. Rivera
- Gold quasi-identifiers: 49-year-old; violin maker; Flagstaff

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | 49-year-old; violin maker | 0.500 | 0.667 | 0.500 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; generic_privacy_leak | rebound tenderness was present at McBurney's point; ceftriaxone and metronidazole before laparoscopic appendectomy |
| privacy_first_llm | None | None | 0.167 | 0.500 | 0.000 | audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; ceftriaxone and metronidazole ... |
| critical_span_guard_extracted | None | None | 0.833 | 1.000 | 1.000 | exact_fact_omission; exact_match_artifact | None |

### `clinical_0029` (clinical)

- Selected because: CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; CT abdomen showed an enlarged appendix with periappendiceal fat stranding; acute appendicitis; ceftriaxone and metronidazole ...
- Gold QA: What did the CT abdomen show? -> enlarged appendix with periappendiceal fat stranding; What procedure was planned? -> laparoscopic appendectomy
- Gold direct identifiers: Grace Chen; Riverside Family Practice; June 15, 2025; MRN-710029; 202-555-1029; grace.chen29@example.com; Dr. Kim
- Gold quasi-identifiers: 91-year-old; long-haul driver; Boise

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | 91-year-old; long-haul driver | 0.500 | 0.833 | 0.500 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; generic_privacy_leak | rebound tenderness was present at McBurney's point |
| privacy_first_llm | None | long-haul driver | 0.167 | 0.500 | 0.000 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; ceftriaxone and metronidazole ... |
| critical_span_guard_extracted | None | None | 0.833 | 1.000 | 1.000 | exact_fact_omission; exact_match_artifact | None |

### `clinical_0031` (clinical)

- Selected because: clean CSG row; exact metric undercount; generic direct identifier leak; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: sudden pleuritic chest pain and shortness of breath; oxygen saturation was 89 percent on room air; CT angiography showed a segmental pulmonary embolism; pulmonary embolism; apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily; 37-year-old
- Gold QA: What condition was diagnosed? -> pulmonary embolism; What anticoagulation plan was started? -> apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily
- Gold direct identifiers: Nadia Hassan; Riverside Family Practice; August 2, 2025; MRN-710031; 202-555-1031; nadia.hassan31@example.com; Dr. Kim
- Gold quasi-identifiers: 37-year-old; violin maker; Flagstaff

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | August 2, 2025 | 37-year-old; violin maker | 0.667 | 1.000 | 0.500 | direct_identifier_leak; quasi_identifier_retained; exact_fact_omission; exact_qa_failure; exact_match_artifact; generic_privacy_leak | None |
| privacy_first_llm | None | None | 0.167 | 0.333 | 0.500 | audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | sudden pleuritic chest pain and shortness of breath; oxygen saturation was 89 percent on room air; CT angiography showed a segmental pulmonary embolism; ... |
| critical_span_guard_extracted | None | None | 1.000 | 1.000 | 1.000 | clean | None |

### `clinical_0035` (clinical)

- Selected because: CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; CT abdomen showed an enlarged appendix with periappendiceal fat stranding; acute appendicitis; ceftriaxone and metronidazole ...
- Gold QA: What did the CT abdomen show? -> enlarged appendix with periappendiceal fat stranding; What procedure was planned? -> laparoscopic appendectomy
- Gold direct identifiers: Elena Petrova; Riverside Family Practice; December 3, 2025; MRN-710035; 202-555-1035; elena.petrova35@example.com; Dr. Patel
- Gold quasi-identifiers: 65-year-old; farm manager; Tucson

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | 65-year-old; farm manager | 0.500 | 0.833 | 0.500 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; generic_privacy_leak | ceftriaxone and metronidazole before laparoscopic appendectomy |
| privacy_first_llm | None | None | 0.167 | 0.500 | 0.000 | audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; ceftriaxone and metronidazole ... |
| critical_span_guard_extracted | None | None | 0.667 | 1.000 | 1.000 | exact_fact_omission; exact_match_artifact | None |

### `clinical_0040` (clinical)

- Selected because: CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: diffuse hives, wheezing, and throat tightness within 20 minutes of eating peanuts; blood pressure fell to 82/48 mmHg; symptoms improved after epinephrine; anaphylaxis; intramuscular epinephrine 0.3 mg and observation for 4 hours; 32-year-old
- Gold QA: What exposure preceded the reaction? -> eating peanuts; What emergency treatment was given? -> intramuscular epinephrine 0.3 mg
- Gold direct identifiers: Maria Lopez; North Ridge Clinic; May 11, 2025; MRN-710040; 202-555-1040; maria.lopez40@example.com; Dr. Singh
- Gold quasi-identifiers: 32-year-old; teacher; Santa Fe

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | 32-year-old; teacher | 0.667 | 0.833 | 1.000 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_match_artifact; generic_privacy_leak | blood pressure fell to 82/48 mmHg |
| privacy_first_llm | None | teacher | 0.167 | 0.500 | 0.000 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | diffuse hives, wheezing, and throat tightness within 20 minutes of eating peanuts; blood pressure fell to 82/48 mmHg; intramuscular epinephrine 0.3 mg and ... |
| critical_span_guard_extracted | None | None | 0.833 | 1.000 | 1.000 | exact_fact_omission; exact_match_artifact | None |

### `clinical_0041` (clinical)

- Selected because: CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; CT abdomen showed an enlarged appendix with periappendiceal fat stranding; acute appendicitis; ceftriaxone and metronidazole ...
- Gold QA: What did the CT abdomen show? -> enlarged appendix with periappendiceal fat stranding; What procedure was planned? -> laparoscopic appendectomy
- Gold direct identifiers: Anthony Reed; Riverside Family Practice; June 18, 2025; MRN-710041; 202-555-1041; anthony.reed41@example.com; Dr. O'Connor
- Gold quasi-identifiers: 39-year-old; software engineer; Reno

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | 39-year-old; software engineer | 0.500 | 0.667 | 0.500 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; generic_privacy_leak | rebound tenderness was present at McBurney's point; ceftriaxone and metronidazole before laparoscopic appendectomy |
| privacy_first_llm | None | software engineer | 0.167 | 0.333 | 0.000 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; CT abdomen showed an enlarged ... |
| critical_span_guard_extracted | None | None | 0.667 | 1.000 | 1.000 | exact_fact_omission; exact_match_artifact | None |

### `clinical_0053` (clinical)

- Selected because: CSG exact-match artifact; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; CT abdomen showed an enlarged appendix with periappendiceal fat stranding; acute appendicitis; ceftriaxone and metronidazole ...
- Gold QA: What did the CT abdomen show? -> enlarged appendix with periappendiceal fat stranding; What procedure was planned? -> laparoscopic appendectomy
- Gold direct identifiers: Grace Chen; Riverside Family Practice; June 21, 2025; MRN-710053; 202-555-1053; grace.chen53@example.com; Dr. Rivera
- Gold quasi-identifiers: 55-year-old; long-haul driver; Boise

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | 55-year-old; long-haul driver | 0.500 | 0.833 | 1.000 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_match_artifact; generic_privacy_leak | ceftriaxone and metronidazole before laparoscopic appendectomy |
| privacy_first_llm | None | None | 0.167 | 0.500 | 0.000 | audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; ceftriaxone and metronidazole ... |
| critical_span_guard_extracted | None | None | 0.333 | 1.000 | 1.000 | exact_fact_omission; exact_match_artifact | None |

### `clinical_0055` (clinical)

- Selected because: CSG strict-specificity audited loss; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: sudden pleuritic chest pain and shortness of breath; oxygen saturation was 89 percent on room air; CT angiography showed a segmental pulmonary embolism; pulmonary embolism; apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily; 69-year-old
- Gold QA: What condition was diagnosed? -> pulmonary embolism; What anticoagulation plan was started? -> apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily
- Gold direct identifiers: Nadia Hassan; Riverside Family Practice; August 8, 2025; MRN-710055; 202-555-1055; nadia.hassan55@example.com; Dr. Singh
- Gold quasi-identifiers: 69-year-old; violin maker; Flagstaff

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | 69-year-old; violin maker | 0.667 | 1.000 | 0.500 | quasi_identifier_retained; exact_fact_omission; exact_qa_failure; exact_match_artifact; generic_privacy_leak | None |
| privacy_first_llm | None | None | 0.167 | 0.333 | 0.500 | audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | sudden pleuritic chest pain and shortness of breath; oxygen saturation was 89 percent on room air; CT angiography showed a segmental pulmonary embolism; ... |
| critical_span_guard_extracted | None | None | 0.833 | 0.833 | 1.000 | audited_fact_loss; exact_fact_omission; csg_strict_specificity_loss | CT angiography showed a segmental pulmonary embolism |

### `clinical_0059` (clinical)

- Selected because: CSG exact-match artifact; CSG strict-specificity audited loss; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; CT abdomen showed an enlarged appendix with periappendiceal fat stranding; acute appendicitis; ceftriaxone and metronidazole ...
- Gold QA: What did the CT abdomen show? -> enlarged appendix with periappendiceal fat stranding; What procedure was planned? -> laparoscopic appendectomy
- Gold direct identifiers: Elena Petrova; Riverside Family Practice; December 9, 2025; MRN-710059; 202-555-1059; elena.petrova59@example.com; Dr. Singh
- Gold quasi-identifiers: 29-year-old; farm manager; Tucson

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | 29-year-old; farm manager | 0.500 | 0.833 | 0.500 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; generic_privacy_leak | ceftriaxone and metronidazole before laparoscopic appendectomy |
| privacy_first_llm | None | None | 0.167 | 0.500 | 0.000 | audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | 18 hours of periumbilical pain that migrated to the right lower quadrant; rebound tenderness was present at McBurney's point; ceftriaxone and metronidazole ... |
| critical_span_guard_extracted | None | None | 0.500 | 0.833 | 1.000 | audited_fact_loss; exact_fact_omission; exact_match_artifact; csg_strict_specificity_loss | 18 hours of periumbilical pain that migrated to the right lower quadrant |

### `legal_0002` (legal)

- Selected because: residual CSG legal QI frontier row; CSG exact-match artifact; CSG residual quasi-identifier; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: Article 8; an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces that existed at the time violated their ...
- Gold QA: Which substantive Article was invoked? -> Article 8; What core claim was raised? -> an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the ...
- Gold direct identifiers: 43208/98; 44875/98; Mr Terence Perkins
- Gold quasi-identifiers: Ms R.; homosexuality; homosexuals; homosexual

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | homosexuality; homosexuals; homosexual | 0.500 | 1.000 | 0.500 | quasi_identifier_retained; exact_fact_omission; exact_qa_failure; exact_match_artifact; generic_privacy_leak | None |
| privacy_first_llm | None | homosexuality; homosexual | 0.000 | 0.500 | 0.000 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against ... |
| critical_span_guard_extracted | None | homosexuality; homosexuals; homosexual | 0.500 | 1.000 | 0.500 | quasi_identifier_retained; exact_fact_omission; exact_qa_failure; exact_match_artifact; csg_residual_qi_frontier | None |

### `legal_0005` (legal)

- Selected because: residual CSG legal QI frontier row; CSG residual quasi-identifier; exact metric undercount; privacy-first utility loss
- Gold task facts: Article 6; violation; the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976
- Gold QA: Which substantive Article was invoked? -> Article 6; What outcome did the Court state? -> violation; What core claim was raised? -> the issue of a certificate emanating from the Secretary of State, under section 42 ...
- Gold direct identifiers: 24265/94; Mr Liam Devenney
- Gold quasi-identifiers: Irish; 12 April 1994; Northern Ireland; 1976; United Kingdom

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | None | 0.667 | 0.667 | 0.667 | audited_fact_loss; exact_fact_omission; exact_qa_failure | the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976 |
| privacy_first_llm | None | None | 0.333 | 0.667 | 0.333 | audited_fact_loss; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976 |
| critical_span_guard_extracted | None | Northern Ireland; 1976 | 1.000 | 1.000 | 1.000 | quasi_identifier_retained; csg_residual_qi_frontier | None |

### `legal_0006` (legal)

- Selected because: foreground legal privacy-utility example; clean CSG row; generic direct identifier leak; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: Article 6; the civil proceedings in her case exceeded a reasonable time, contrary to Article 6 § 1 of the Convention
- Gold QA: Which substantive Article was invoked? -> Article 6; What core claim was raised? -> the civil proceedings in her case exceeded a reasonable time, contrary to Article 6 § 1 of the Convention
- Gold direct identifiers: 37645/97; Mrs Helena Sawicka
- Gold quasi-identifiers: 10 March 1997

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | 37645/97 | 10 March 1997 | 1.000 | 1.000 | 1.000 | direct_identifier_leak; quasi_identifier_retained; generic_privacy_leak | None |
| privacy_first_llm | None | None | 0.500 | 0.000 | 0.500 | audited_fact_loss; exact_fact_omission; exact_qa_failure; privacy_first_overgeneralization | Article 6; the civil proceedings in her case exceeded a reasonable time, contrary to Article 6 § 1 of the Convention |
| critical_span_guard_extracted | None | None | 1.000 | 1.000 | 1.000 | clean | None |

### `legal_0016` (legal)

- Selected because: strict legal-specificity audited utility caveat; CSG strict-specificity audited loss; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: Article 8; the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention
- Gold QA: Which substantive Article was invoked? -> Article 8; What core claim was raised? -> the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his ...
- Gold direct identifiers: 11375/02; Mr Anton Kaleta
- Gold quasi-identifiers: German; 1 June 2001; 12 July 2006; 2001

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | 1 June 2001; 12 July 2006; 2001 | 0.500 | 0.500 | 0.500 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_qa_failure; generic_privacy_leak | the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 ... |
| privacy_first_llm | None | None | 0.500 | 0.500 | 0.500 | audited_fact_loss; exact_fact_omission; exact_qa_failure; privacy_first_overgeneralization | the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 ... |
| critical_span_guard_extracted | None | None | 1.000 | 0.500 | 1.000 | audited_fact_loss; csg_strict_specificity_loss | the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 ... |

### `legal_0018` (legal)

- Selected because: exact-vs-audited legal metric nuance; CSG exact-match artifact; exact metric undercount; privacy-first utility loss
- Gold task facts: Article 1; the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively
- Gold QA: Which substantive Article was invoked? -> Article 1; What core claim was raised? -> the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under ...
- Gold direct identifiers: 35179/97; Ms Inga Allard
- Gold quasi-identifiers: 27 November 1996

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | None | 1.000 | 1.000 | 1.000 | clean | None |
| privacy_first_llm | None | None | 0.000 | 0.000 | 0.000 | audited_fact_loss; exact_fact_omission; exact_qa_failure; privacy_first_overgeneralization | Article 1; the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of ... |
| critical_span_guard_extracted | None | None | 0.500 | 1.000 | 0.500 | exact_fact_omission; exact_qa_failure; exact_match_artifact | None |

### `legal_0021` (legal)

- Selected because: clean CSG row; generic direct identifier leak; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: Article 8
- Gold QA: Which substantive Article was invoked? -> Article 8
- Gold direct identifiers: 29865/96; Mrs Ayten Ünal Tekeli; Ayten Ünal Tekeli; Ünal
- Gold quasi-identifiers: 20 December 1995

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | 29865/96 | 20 December 1995 | 1.000 | 1.000 | 1.000 | direct_identifier_leak; quasi_identifier_retained; generic_privacy_leak | None |
| privacy_first_llm | None | None | 0.000 | 0.000 | 0.000 | audited_fact_loss; exact_fact_omission; exact_qa_failure; privacy_first_overgeneralization | Article 8 |
| critical_span_guard_extracted | None | None | 1.000 | 1.000 | 1.000 | clean | None |

### `legal_0025` (legal)

- Selected because: residual CSG legal QI frontier row; CSG residual quasi-identifier; exact metric undercount; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: Article 4; the conduct of proceedings for the said traffic offence violated Article 4 of Protocol No. 7, given that he had been acquitted of the offence of resisting the exercise of official authority in respect of the same act
- Gold QA: Which substantive Article was invoked? -> Article 4; What core claim was raised? -> the conduct of proceedings for the said traffic offence violated Article 4 of Protocol No. 7, given that he had been acquitted of ...
- Gold direct identifiers: 18015/03; Mr Roland Schutte
- Gold quasi-identifiers: 23 May 2003; resisting the exercise of official authority; 4 February 1998

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | 23 May 2003; resisting the exercise of official authority; 4 February 1998 | 1.000 | 1.000 | 1.000 | quasi_identifier_retained; generic_privacy_leak | None |
| privacy_first_llm | None | resisting the exercise of official authority | 0.500 | 1.000 | 0.500 | quasi_identifier_retained; exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | None |
| critical_span_guard_extracted | None | resisting the exercise of official authority | 1.000 | 1.000 | 1.000 | quasi_identifier_retained; csg_residual_qi_frontier | None |

### `legal_0037` (legal)

- Selected because: clean CSG row; generic direct identifier leak; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: Article 5
- Gold QA: Which substantive Article was invoked? -> Article 5
- Gold direct identifiers: 41478/98; Ms Nuray Şen
- Gold quasi-identifiers: 25 April 1996; 30 April 2002

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | Ms Nuray Şen | 25 April 1996; 30 April 2002 | 1.000 | 1.000 | 1.000 | direct_identifier_leak; quasi_identifier_retained; generic_privacy_leak | None |
| privacy_first_llm | None | None | 0.000 | 0.000 | 0.000 | audited_fact_loss; exact_fact_omission; exact_qa_failure; privacy_first_overgeneralization | Article 5 |
| critical_span_guard_extracted | None | None | 1.000 | 1.000 | 1.000 | clean | None |

### `legal_0042` (legal)

- Selected because: residual CSG legal QI frontier row; CSG residual quasi-identifier; generic quasi-identifier retention
- Gold task facts: Article 14; no violation; there had been a violation of Article 14 of the Convention taken in conjunction with Article 1 of Protocol No. 1 and Article 12 of the Convention
- Gold QA: Which substantive Article was invoked? -> Article 14; What outcome did the Court state? -> no violation; What core claim was raised? -> there had been a violation of Article 14 of the Convention taken in conjunction ...
- Gold direct identifiers: 49151/07; Mrs María Luisa Muñoz Díaz
- Gold quasi-identifiers: 29 October 2007; Rom

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | Rom | 1.000 | 1.000 | 1.000 | quasi_identifier_retained; generic_privacy_leak | None |
| privacy_first_llm | None | Rom | 1.000 | 1.000 | 1.000 | quasi_identifier_retained | None |
| critical_span_guard_extracted | None | Rom | 1.000 | 1.000 | 1.000 | quasi_identifier_retained; csg_residual_qi_frontier | None |

### `legal_0043` (legal)

- Selected because: clean CSG row; generic direct identifier leak; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: Article 6
- Gold QA: Which substantive Article was invoked? -> Article 6
- Gold direct identifiers: 37770/97; Andrzej Krzewicki
- Gold quasi-identifiers: Polish; 19 July 1997; Łódź Regional Court; 20 April 1996

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | 37770/97 | 19 July 1997; 20 April 1996 | 1.000 | 1.000 | 1.000 | direct_identifier_leak; quasi_identifier_retained; generic_privacy_leak | None |
| privacy_first_llm | None | None | 0.000 | 0.000 | 0.000 | audited_fact_loss; exact_fact_omission; exact_qa_failure; privacy_first_overgeneralization | Article 6 |
| critical_span_guard_extracted | None | None | 1.000 | 1.000 | 1.000 | clean | None |

### `legal_0046` (legal)

- Selected because: residual CSG legal QI frontier row; CSG residual quasi-identifier; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: Article 1; inadmissible; because he was a man, he was denied social security benefits equivalent to those received by widows
- Gold QA: Which substantive Article was invoked? -> Article 1; What outcome did the Court state? -> inadmissible; What core claim was raised? -> because he was a man, he was denied social security benefits equivalent to those ...
- Gold direct identifiers: 28095/02; Mr Dennis Twomey
- Gold quasi-identifiers: British; 1 March 2001; widows; 4 November 2003; British national

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | widows | 1.000 | 1.000 | 1.000 | quasi_identifier_retained; generic_privacy_leak | None |
| privacy_first_llm | None | widows | 0.333 | 0.333 | 0.333 | quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_qa_failure; privacy_first_overgeneralization | Article 1; because he was a man, he was denied social security benefits equivalent to those received by widows |
| critical_span_guard_extracted | None | widows | 1.000 | 1.000 | 1.000 | quasi_identifier_retained; csg_residual_qi_frontier | None |

### `legal_0053` (legal)

- Selected because: residual CSG legal QI frontier row; CSG residual quasi-identifier; generic direct identifier leak; generic quasi-identifier retention; privacy-first utility loss
- Gold task facts: Article 8; the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he had attempted secretly to film her naked in their ...
- Gold QA: Which substantive Article was invoked? -> Article 8; What core claim was raised? -> the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against ...
- Gold direct identifiers: 5786/08; Ms Eliza Söderman
- Gold quasi-identifiers: 21 January 2008; 14 years old

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | 5786/08 | 21 January 2008; 14 years old | 0.500 | 0.500 | 0.500 | direct_identifier_leak; quasi_identifier_retained; audited_fact_loss; exact_fact_omission; exact_qa_failure; generic_privacy_leak | the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation ... |
| privacy_first_llm | None | None | 0.500 | 0.500 | 0.500 | audited_fact_loss; exact_fact_omission; exact_qa_failure; privacy_first_overgeneralization | the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation ... |
| critical_span_guard_extracted | None | 14 years old | 1.000 | 1.000 | 1.000 | quasi_identifier_retained; csg_residual_qi_frontier | None |

### `legal_0054` (legal)

- Selected because: residual CSG legal QI frontier row; CSG exact-match artifact; CSG residual quasi-identifier; exact metric undercount; privacy-first utility loss
- Gold task facts: Article 14; no violation; when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas the survivor of a married couple or a homosexual relationship registered under the Civil ...
- Gold QA: Which substantive Article was invoked? -> Article 14; What outcome did the Court state? -> no violation; What core claim was raised? -> when the first of them died, the survivor would be required to pay inheritance ...
- Gold direct identifiers: 13378/05
- Gold quasi-identifiers: sister; 12 December 2006; sister’s; United Kingdom of Great Britain and Northern Ireland; British nationals; British; sister’; four votes to three

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | None | 0.667 | 1.000 | 0.667 | exact_fact_omission; exact_qa_failure; exact_match_artifact | None |
| privacy_first_llm | None | None | 0.667 | 0.667 | 0.667 | audited_fact_loss; exact_fact_omission; exact_qa_failure; privacy_first_overgeneralization | when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas the survivor of a ... |
| critical_span_guard_extracted | None | sister; sister’s; sister’; four votes to three | 0.667 | 1.000 | 0.667 | quasi_identifier_retained; exact_fact_omission; exact_qa_failure; exact_match_artifact; csg_residual_qi_frontier | None |

### `legal_0055` (legal)

- Selected because: residual CSG legal QI frontier row; CSG residual quasi-identifier; generic direct identifier leak; generic quasi-identifier retention
- Gold task facts: Article 6; her right to access to a court according to Article 6 § 1 of the Convention had been violated since she had not been able to appeal to a court against a decision by an authority to withdraw permission for her to participate in a labour market ...
- Gold QA: Which substantive Article was invoked? -> Article 6; What core claim was raised? -> her right to access to a court according to Article 6 § 1 of the Convention had been violated since she had not been able to appeal ...
- Gold direct identifiers: 28426/06; Ms Sonja Mendel
- Gold quasi-identifiers: 28 June 2006; participate in a labour market policy programme.; Kingdom of Sweden; Swedish

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | 28426/06 | 28 June 2006; participate in a labour market policy programme. | 1.000 | 1.000 | 1.000 | direct_identifier_leak; quasi_identifier_retained; generic_privacy_leak | None |
| privacy_first_llm | None | participate in a labour market policy programme. | 1.000 | 1.000 | 1.000 | quasi_identifier_retained | None |
| critical_span_guard_extracted | None | participate in a labour market policy programme. | 1.000 | 1.000 | 1.000 | quasi_identifier_retained; csg_residual_qi_frontier | None |

### `legal_0056` (legal)

- Selected because: residual CSG legal QI frontier row; CSG exact-match artifact; CSG residual quasi-identifier; exact metric undercount; privacy-first utility loss
- Gold task facts: Article 1; inadmissible; shortcomings in the British health system in connection with the recruitment of locum doctors and supervision of out-of-hours locum services had led to their father’s death as a consequence of medical malpractice by German locum ...
- Gold QA: Which substantive Article was invoked? -> Article 1; What outcome did the Court state? -> inadmissible; What core claim was raised? -> shortcomings in the British health system in connection with the recruitment of ...
- Gold direct identifiers: 49278/09; Mr Stuart Gray
- Gold quasi-identifiers: United Kingdom; British; Mr Rory Gray; 10 September 2009; Hamm General Prosecution Authorities; Hamm; Hamm General Prosecution; Hamm Higher Regional Court; 14 May 2009

| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |
|---|---|---|---:|---:|---:|---|---|
| generic_llm | None | None | 0.667 | 1.000 | 0.667 | exact_fact_omission; exact_qa_failure; exact_match_artifact | None |
| privacy_first_llm | None | None | 0.667 | 1.000 | 0.667 | exact_fact_omission; exact_qa_failure; exact_match_artifact; privacy_first_overgeneralization | None |
| critical_span_guard_extracted | None | British; 10 September 2009; 14 May 2009 | 0.667 | 1.000 | 0.667 | quasi_identifier_retained; exact_fact_omission; exact_qa_failure; exact_match_artifact; csg_residual_qi_frontier | None |

## Paper-Use Notes

- This audit closes the plan-level transparent 20-50 example subset requirement for the current n120 bounded OpenAI expansion package.
- For a full top-tier submission, the natural next step is a second independent annotator or adjudicated human labels on this fixed subset.
- Keep exact cost/latency caveats separate: the n100 cache is complete, but early cache rows did not store provider usage or elapsed time.
