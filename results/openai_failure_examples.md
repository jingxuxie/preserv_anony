# Qualitative Failure Candidates

Generated from deterministic scoring; manually audit before using in the paper.

## critical_span_guard_extracted

### clinical_0008 (clinical)

- Direct leaks: []
- Quasi leaks: []
- Omitted facts: ['blood glucose was 482 mg/dL with large serum ketones', '80-year-old']

Original:

> Maria Lopez, a 80-year-old teacher from Santa Fe, visited North Ridge Clinic on September 3, 2025 (record MRN-710008, phone 202-555-1008, email maria.lopez8@example.com). She reported two days of vomiting, thirst, and abdominal pain, with blood glucose was 482 mg/dL with large serum ketones. venous pH was 7.21. Dr. Patel diagnosed diabetic ketoacidosis and started intravenous insulin and potassium replacement.

Anonymized:

> [REDACTED_NAME], an elderly individual from [REDACTED_CITY], visited [CLINIC] on [REDACTED_DATE] (record [REDACTED_MRN], phone [REDACTED_PHONE], email [REDACTED_EMAIL]). They reported two days of vomiting, thirst, and abdominal pain, with blood glucose of 482 mg/dL with large serum ketones. Venous pH was 7.21. [CLINICIAN] diagnosed diabetic ketoacidosis and started intravenous insulin and potassium replacement.

### clinical_0041 (clinical)

- Direct leaks: []
- Quasi leaks: []
- Omitted facts: ['18 hours of periumbilical pain that migrated to the right lower quadrant', "rebound tenderness was present at McBurney's point"]

Original:

> Anthony Reed, a 39-year-old software engineer from Reno, visited Riverside Family Practice on June 18, 2025 (record MRN-710041, phone 202-555-1041, email anthony.reed41@example.com). He reported 18 hours of periumbilical pain that migrated to the right lower quadrant, with rebound tenderness was present at McBurney's point. CT abdomen showed an enlarged appendix with periappendiceal fat stranding. Dr. O'Connor diagnosed acute appendicitis and started ceftriaxone and metronidazole before laparoscopic appendectomy.

Anonymized:

> [REDACTED_NAME], a late 30s worker from [REDACTED_CITY], visited [CLINIC] on [REDACTED_DATE] (record [REDACTED_MRN], phone [REDACTED_PHONE], email [REDACTED_EMAIL]). He reported 18 hours of periumbilical pain migrating to the right lower quadrant, with rebound tenderness at McBurney's point. CT abdomen showed an enlarged appendix with periappendiceal fat stranding. [CLINICIAN] diagnosed acute appendicitis and started ceftriaxone and metronidazole before laparoscopic appendectomy.

### clinical_0046 (clinical)

- Direct leaks: []
- Quasi leaks: []
- Omitted facts: ['blood pressure fell to 82/48 mmHg', '74-year-old']

Original:

> Samuel Ortiz, a 74-year-old postal worker from Asheville, visited North Ridge Clinic on November 26, 2025 (record MRN-710046, phone 202-555-1046, email samuel.ortiz46@example.com). He reported diffuse hives, wheezing, and throat tightness within 20 minutes of eating peanuts, with blood pressure fell to 82/48 mmHg. symptoms improved after epinephrine. Dr. Nguyen diagnosed anaphylaxis and started intramuscular epinephrine 0.3 mg and observation for 4 hours.

Anonymized:

> [PERSON], an elderly worker from a city, visited a clinic on a date (record [ID]], phone number, email address). He reported diffuse hives, wheezing, and throat tightness within 20 minutes of eating peanuts, with blood pressure falling to 82/48 mmHg. Symptoms improved after epinephrine. The clinician diagnosed anaphylaxis and started intramuscular epinephrine 0.3 mg and observation for 4 hours.

### clinical_0002 (clinical)

- Direct leaks: []
- Quasi leaks: []
- Omitted facts: ['blood glucose was 482 mg/dL with large serum ketones', '38-year-old']

Original:

> Priya Shah, a 38-year-old dental hygienist from Burlington, visited North Ridge Clinic on March 15, 2025 (record MRN-710002, phone 202-555-1002, email priya.shah2@example.com). She reported two days of vomiting, thirst, and abdominal pain, with blood glucose was 482 mg/dL with large serum ketones. venous pH was 7.21. Dr. Singh diagnosed diabetic ketoacidosis and started intravenous insulin and potassium replacement.

Anonymized:

> [PATIENT], an adult worker from [REDACTED_CITY], visited [REDACTED_CLINIC] on [REDACTED_DATE] (record [REDACTED_MRN], phone [REDACTED_PHONE], email [REDACTED_EMAIL]). She reported two days of vomiting, thirst, and abdominal pain, with blood glucose being 482 mg/dL with large serum ketones. venous pH was 7.21. [CLINICIAN] diagnosed diabetic ketoacidosis and started intravenous insulin and potassium replacement.

## generic_llm

### clinical_0047 (clinical)

- Direct leaks: []
- Quasi leaks: ['violin maker']
- Omitted facts: ["rebound tenderness was present at McBurney's point", 'CT abdomen showed an enlarged appendix with periappendiceal fat stranding', 'ceftriaxone and metronidazole before laparoscopic appendectomy', '81-year-old']

Original:

> Nadia Hassan, a 81-year-old violin maker from Flagstaff, visited Riverside Family Practice on December 6, 2025 (record MRN-710047, phone 202-555-1047, email nadia.hassan47@example.com). She reported 18 hours of periumbilical pain that migrated to the right lower quadrant, with rebound tenderness was present at McBurney's point. CT abdomen showed an enlarged appendix with periappendiceal fat stranding. Dr. O'Connor diagnosed acute appendicitis and started ceftriaxone and metronidazole before laparoscopic appendectomy.

Anonymized:

> A patient in their early 80s, a violin maker from a city in the southwestern United States, visited a local family practice clinic. The visit occurred in early December of a recent year. The patient reported 18 hours of periumbilical pain that migrated to the right lower quadrant, with rebound tenderness present at a specific point on the abdomen. Imaging studies showed an enlarged appendix with surrounding fat stranding. The healthcare provider diagnosed acute appendicitis and initiated antibiotic treatment with ceftriaxone and metronidazole before performing a laparoscopic appendectomy.

### clinical_0028 (clinical)

- Direct leaks: []
- Quasi leaks: ['retired judge']
- Omitted facts: ['blood pressure fell to 82/48 mmHg', 'symptoms improved after epinephrine', 'intramuscular epinephrine 0.3 mg and observation for 4 hours', '84-year-old']

Original:

> James Walker, a 84-year-old retired judge from Madison, visited North Ridge Clinic on May 8, 2025 (record MRN-710028, phone 202-555-1028, email james.walker28@example.com). He reported diffuse hives, wheezing, and throat tightness within 20 minutes of eating peanuts, with blood pressure fell to 82/48 mmHg. symptoms improved after epinephrine. Dr. O'Connor diagnosed anaphylaxis and started intramuscular epinephrine 0.3 mg and observation for 4 hours.

Anonymized:

> A retired judge, aged 84, from a city in the Midwest, visited a local clinic on a specified date. He reported diffuse hives, wheezing, and throat tightness within 20 minutes of eating peanuts, with blood pressure falling to a low level. Symptoms improved after administration of epinephrine. The physician diagnosed anaphylaxis and initiated intramuscular epinephrine 0.3 mg, with observation for 4 hours.

### clinical_0019 (clinical)

- Direct leaks: []
- Quasi leaks: ['farm manager']
- Omitted facts: ['oxygen saturation was 89 percent on room air', 'CT angiography showed a segmental pulmonary embolism', 'apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily', '89-year-old']

Original:

> Elena Petrova, a 89-year-old farm manager from Tucson, visited Riverside Family Practice on August 26, 2025 (record MRN-710019, phone 202-555-1019, email elena.petrova19@example.com). She reported sudden pleuritic chest pain and shortness of breath, with oxygen saturation was 89 percent on room air. CT angiography showed a segmental pulmonary embolism. Dr. Nguyen diagnosed pulmonary embolism and started apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily.

Anonymized:

> A female patient in her late 80s, a farm manager, visited a healthcare facility on a recent date. She reported sudden pleuritic chest pain and shortness of breath, with oxygen saturation of 89 percent on room air. Imaging studies revealed a segmental pulmonary embolism. The physician diagnosed pulmonary embolism and initiated anticoagulant therapy with apixaban, starting with 10 mg twice daily for 7 days, followed by 5 mg twice daily.

### clinical_0029 (clinical)

- Direct leaks: []
- Quasi leaks: ['91-year-old', 'long-haul driver']
- Omitted facts: ["rebound tenderness was present at McBurney's point", 'CT abdomen showed an enlarged appendix with periappendiceal fat stranding', 'ceftriaxone and metronidazole before laparoscopic appendectomy']

Original:

> Grace Chen, a 91-year-old long-haul driver from Boise, visited Riverside Family Practice on June 15, 2025 (record MRN-710029, phone 202-555-1029, email grace.chen29@example.com). She reported 18 hours of periumbilical pain that migrated to the right lower quadrant, with rebound tenderness was present at McBurney's point. CT abdomen showed an enlarged appendix with periappendiceal fat stranding. Dr. Kim diagnosed acute appendicitis and started ceftriaxone and metronidazole before laparoscopic appendectomy.

Anonymized:

> A 91-year-old long-haul driver from a specific city visited a family practice clinic on a date in mid-2025. She reported 18 hours of periumbilical pain that migrated to the right lower quadrant, with rebound tenderness at a specific point. Imaging of the abdomen showed an enlarged appendix with surrounding fat stranding. A physician diagnosed acute appendicitis and initiated antibiotic therapy before laparoscopic appendectomy.

## privacy_first_llm

### clinical_0006 (clinical)

- Direct leaks: []
- Quasi leaks: ['postal worker']
- Omitted facts: ['3 weeks of morning stiffness in both hands', 'swelling of the MCP joints', 'anti-CCP was positive', 'rheumatoid arthritis', 'methotrexate 15 mg weekly and folic acid 1 mg daily', '66-year-old']

Original:

> Samuel Ortiz, a 66-year-old postal worker from Asheville, visited North Ridge Clinic on July 16, 2025 (record MRN-710006, phone 202-555-1006, email samuel.ortiz6@example.com). He reported 3 weeks of morning stiffness in both hands, with swelling of the MCP joints. anti-CCP was positive. Dr. Patel diagnosed rheumatoid arthritis and started methotrexate 15 mg weekly and folic acid 1 mg daily.

Anonymized:

> A middle-aged postal worker from a regional city visited a healthcare clinic on a summer date. They reported three weeks of morning stiffness in both hands, with swelling of the finger joint areas. A specific antibody test was positive. The healthcare provider diagnosed an autoimmune joint condition and initiated treatment with a weekly dose of a disease-modifying medication and daily folic acid supplementation.

### clinical_0012 (clinical)

- Direct leaks: []
- Quasi leaks: ['retired judge']
- Omitted facts: ['3 weeks of morning stiffness in both hands', 'swelling of the MCP joints', 'anti-CCP was positive', 'rheumatoid arthritis', 'methotrexate 15 mg weekly and folic acid 1 mg daily', '40-year-old']

Original:

> James Walker, a 40-year-old retired judge from Madison, visited North Ridge Clinic on January 4, 2025 (record MRN-710012, phone 202-555-1012, email james.walker12@example.com). He reported 3 weeks of morning stiffness in both hands, with swelling of the MCP joints. anti-CCP was positive. Dr. Patel diagnosed rheumatoid arthritis and started methotrexate 15 mg weekly and folic acid 1 mg daily.

Anonymized:

> A middle-aged individual, a retired judge, visited a medical clinic on a specific date. They reported several weeks of morning stiffness in both hands, with swelling of the finger joint areas. A positive antibody test was noted. A healthcare professional diagnosed an autoimmune joint condition and initiated treatment with a weekly dose of a disease-modifying medication and daily folic acid supplementation.

### clinical_0036 (clinical)

- Direct leaks: []
- Quasi leaks: ['retired judge']
- Omitted facts: ['3 weeks of morning stiffness in both hands', 'swelling of the MCP joints', 'anti-CCP was positive', 'rheumatoid arthritis', 'methotrexate 15 mg weekly and folic acid 1 mg daily', '72-year-old']

Original:

> James Walker, a 72-year-old retired judge from Madison, visited North Ridge Clinic on January 10, 2025 (record MRN-710036, phone 202-555-1036, email james.walker36@example.com). He reported 3 weeks of morning stiffness in both hands, with swelling of the MCP joints. anti-CCP was positive. Dr. Kim diagnosed rheumatoid arthritis and started methotrexate 15 mg weekly and folic acid 1 mg daily.

Anonymized:

> A retired judge in their early seventies visited a medical clinic on a specific date. They reported several weeks of morning stiffness in both hands, with swelling of the finger joint areas. A positive antibody test was noted. The healthcare provider diagnosed a form of inflammatory joint disease and initiated treatment with a weekly dose of a disease-modifying medication and daily folic acid supplementation.

### clinical_0042 (clinical)

- Direct leaks: []
- Quasi leaks: ['dental hygienist']
- Omitted facts: ['3 weeks of morning stiffness in both hands', 'swelling of the MCP joints', 'anti-CCP was positive', 'rheumatoid arthritis', 'methotrexate 15 mg weekly and folic acid 1 mg daily', '46-year-old']

Original:

> Priya Shah, a 46-year-old dental hygienist from Burlington, visited North Ridge Clinic on July 25, 2025 (record MRN-710042, phone 202-555-1042, email priya.shah42@example.com). She reported 3 weeks of morning stiffness in both hands, with swelling of the MCP joints. anti-CCP was positive. Dr. Kim diagnosed rheumatoid arthritis and started methotrexate 15 mg weekly and folic acid 1 mg daily.

Anonymized:

> A middle-aged dental hygienist from a suburban area visited a healthcare clinic. She reported several weeks of morning stiffness in both hands, with swelling of the finger joints. A specific antibody test was positive. The healthcare provider diagnosed an autoimmune joint condition and initiated treatment with a disease-modifying medication and folic acid.

