# Robustness Stress Slice

A 12-example handwritten diagnostic slice covering hard privacy-utility overlaps. This is a local stress test, not part of the cached 50-example non-oracle OpenAI headline run.

## Coverage

| Stress tag | Examples |
|---|---:|
| `article_specificity` | 5 |
| `case_label` | 1 |
| `detention_status` | 1 |
| `device_failure` | 1 |
| `diagnosis_sensitive` | 1 |
| `domestic_violence` | 1 |
| `dose_preservation` | 1 |
| `exact_age` | 1 |
| `family_relationship` | 1 |
| `immunosuppression` | 1 |
| `location_is_private` | 1 |
| `minority_status_is_claim` | 1 |
| `numeric_lab` | 3 |
| `occupation_is_causal` | 1 |
| `pediatric_age` | 1 |
| `pregnancy` | 1 |
| `protocol_specificity` | 1 |
| `rare_condition` | 1 |
| `rare_occupation` | 1 |
| `role_is_claim` | 1 |
| `secret_evidence` | 1 |
| `sensitive_attribute_is_claim` | 1 |
| `small_institution` | 1 |
| `small_location` | 1 |
| `trigger_is_sensitive` | 1 |
| `utility_critical_sensitive_attribute` | 1 |

## Local Diagnostic Results

| Method | Direct leak | QI risk | Exact TCFR | QA |
|---|---:|---:|---:|---:|
| Regex | 0.083 | 2.167 | 1.000 | 1.000 |
| Presidio | 0.667 | 2.667 | 0.817 | 0.833 |
| Direct-span oracle | 0.000 | 2.500 | 1.000 | 1.000 |
| Privacy-first oracle | 0.000 | 0.000 | 0.608 | 0.528 |
| CSG oracle | 0.000 | 0.667 | 1.000 | 1.000 |

## Failure Counts

- Privacy-first oracle has zero direct leaks and zero measured QI risk, but fails QA on 11/12 rows.
- Direct-span oracle has zero direct leaks and perfect utility, but retains quasi-identifiers on 12/12 rows.
- CSG oracle has zero direct leaks and perfect utility, but retains task-critical quasi-identifiers on 6/12 rows.

## Interpretation

- The stress slice makes the privacy-utility conflict explicit: some sensitive facts, such as pregnancy, sexual orientation, domestic violence, or Roma marriage, are also the facts needed to answer the domain question.
- Strong privacy-first redaction can drive measured QI risk to zero while removing doses, lab values, Article numbers, protocol provisions, or sensitive claim facts.
- A task-aware policy can preserve utility on this diagnostic slice, but remaining QI risk is not just an implementation bug; it reflects facts that are simultaneously sensitive and task-critical.

## Paper-Useful Examples

### `stress_clinical_0000` / `Privacy-first oracle`

- Tags: `exact_age`, `pregnancy`, `utility_critical_sensitive_attribute`
- Direct leaks: None
- QI hits: None
- Omitted facts: pregnant; blood pressure 168/112 mmHg; magnesium sulfate 4 g IV loading dose followed by 1 g per hour
- Failed QA: What treatment was started?
- Output: [PATIENT], a adolescent [PREGNANCY_STATUS] performer from [LOCATION], arrived at [CLINIC] on [DATE] (record [ID], phone [PHONE]). She had a generalized seizure, blood pressure 168/[VALUE], and 3+ proteinuria. [CLINICIAN] diagnosed eclampsia and started magnesium sulfate [VALUE] IV loading dose followed by [VALUE] per hour.

### `stress_legal_0005` / `Privacy-first oracle`

- Tags: `minority_status_is_claim`, `protocol_specificity`
- Direct leaks: None
- QI hits: None
- Omitted facts: Article 14; Article 1 of Protocol No. 1
- Failed QA: Which substantive Article was invoked?; What protocol provision was invoked?
- Output: In application no. [ID], [PERSON] complained under Article [NUMBER] taken with Article [NUMBER] of Protocol No. 1 that survivor benefits were denied because her [MINORITY_STATUS] had not been registered in a civil ceremony. The Court found a violation.

### `stress_legal_0001` / `CSG oracle`

- Tags: `case_label`, `secret_evidence`, `article_specificity`
- Direct leaks: None
- QI hits: None
- Omitted facts: None
- Failed QA: None
- Output: Application no. [ID] was lodged by [PERSON] in the [CASE_LABEL] disciplinary proceedings. She complained under Article 6 that the tribunal relied on secret evidence without letting her lawyer inspect it. The Court found a violation.

### `stress_legal_0000` / `CSG oracle`

- Tags: `sensitive_attribute_is_claim`, `article_specificity`
- Direct leaks: None
- QI hits: sexual orientation; Royal Navy
- Omitted facts: None
- Failed QA: None
- Output: The case originated in application no. [ID] against the [COUNTRY] by [PERSON] on [DATE]. The applicant complained under Article 8 that an investigation into his sexual orientation and discharge from the Royal Navy had violated his right to private life.
