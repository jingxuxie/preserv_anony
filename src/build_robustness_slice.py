"""Build a small handwritten robustness slice for privacy-utility overlaps."""

from __future__ import annotations

import argparse

from io_utils import write_jsonl


def direct(text: str, typ: str, replacement: str) -> dict:
    return {"text": text, "type": typ, "identifier_type": "DIRECT", "replacement": replacement}


def quasi(text: str, typ: str, replacement: str = "[QUASI]") -> dict:
    return {"text": text, "type": typ, "identifier_type": "QUASI", "replacement": replacement}


def fact(
    typ: str,
    value: str,
    generalization_allowed: bool = False,
    acceptable_generalizations: list[str] | None = None,
    answer_aliases: list[str] | None = None,
) -> dict:
    row = {"type": typ, "fact": value, "generalization_allowed": generalization_allowed}
    if acceptable_generalizations:
        row["acceptable_generalizations"] = acceptable_generalizations
    if answer_aliases:
        row["answer_aliases"] = answer_aliases
    return row


def qa(question: str, answer: str, aliases: list[str] | None = None) -> dict:
    answer_aliases = [answer]
    for alias in aliases or []:
        if alias not in answer_aliases:
            answer_aliases.append(alias)
    return {"q": question, "a": answer, "answer_aliases": answer_aliases}


def clinical_rows() -> list[dict]:
    return [
        {
            "id": "stress_clinical_0000",
            "domain": "clinical",
            "source": "handwritten_stress",
            "stress_tags": ["exact_age", "pregnancy", "utility_critical_sensitive_attribute"],
            "text": (
                "Lena Ortiz, a 17-year-old pregnant ballet dancer from Nome, arrived at Aurora Teen Clinic "
                "on April 2, 2025 (record MRN-990100, phone 202-555-2100). She had a generalized seizure, "
                "blood pressure 168/112 mmHg, and 3+ proteinuria. Dr. Avery diagnosed eclampsia and started "
                "magnesium sulfate 4 g IV loading dose followed by 1 g per hour."
            ),
            "private_spans": [
                direct("Lena Ortiz", "PERSON", "[PATIENT]"),
                direct("Aurora Teen Clinic", "ORG", "[CLINIC]"),
                direct("April 2, 2025", "DATE", "[DATE]"),
                direct("MRN-990100", "ID", "[ID]"),
                direct("202-555-2100", "PHONE", "[PHONE]"),
                direct("Dr. Avery", "PERSON", "[CLINICIAN]"),
                quasi("17-year-old", "AGE", "adolescent"),
                quasi("pregnant", "SENSITIVE_ATTRIBUTE", "[PREGNANCY_STATUS]"),
                quasi("ballet dancer", "OCCUPATION", "performer"),
                quasi("Nome", "LOCATION", "[LOCATION]"),
            ],
            "task_critical_facts": [
                fact("age", "17-year-old", True, ["adolescent"]),
                fact("pregnancy", "pregnant"),
                fact("finding", "blood pressure 168/112 mmHg"),
                fact("finding", "3+ proteinuria"),
                fact("diagnosis", "eclampsia"),
                fact("treatment", "magnesium sulfate 4 g IV loading dose followed by 1 g per hour"),
            ],
            "qa": [
                qa("What diagnosis was made?", "eclampsia"),
                qa(
                    "What treatment was started?",
                    "magnesium sulfate 4 g IV loading dose followed by 1 g per hour",
                ),
            ],
        },
        {
            "id": "stress_clinical_0001",
            "domain": "clinical",
            "source": "handwritten_stress",
            "stress_tags": ["rare_occupation", "small_location", "numeric_lab"],
            "text": (
                "Noah Kim, a 72-year-old retired judge from Marfa, was seen at Cedar Valley Hospital on "
                "May 9, 2025 (record MRN-990101, email noah.kim@example.com). He had tremor, ataxia, and "
                "confusion after dehydration. Lithium level was 1.8 mmol/L. Dr. Singh diagnosed lithium "
                "toxicity, held lithium, and started IV fluids."
            ),
            "private_spans": [
                direct("Noah Kim", "PERSON", "[PATIENT]"),
                direct("Cedar Valley Hospital", "ORG", "[CLINIC]"),
                direct("May 9, 2025", "DATE", "[DATE]"),
                direct("MRN-990101", "ID", "[ID]"),
                direct("noah.kim@example.com", "EMAIL", "[EMAIL]"),
                direct("Dr. Singh", "PERSON", "[CLINICIAN]"),
                quasi("72-year-old", "AGE", "early 70s"),
                quasi("retired judge", "OCCUPATION", "retired professional"),
                quasi("Marfa", "LOCATION", "[LOCATION]"),
            ],
            "task_critical_facts": [
                fact("symptom", "tremor, ataxia, and confusion"),
                fact("lab", "Lithium level was 1.8 mmol/L"),
                fact("diagnosis", "lithium toxicity"),
                fact("treatment", "held lithium and started IV fluids", answer_aliases=["held lithium", "IV fluids"]),
                fact("age", "72-year-old", True, ["early 70s"]),
            ],
            "qa": [
                qa("Which level was abnormal?", "Lithium level was 1.8 mmol/L"),
                qa("What treatment change was made?", "held lithium and started IV fluids", ["held lithium", "IV fluids"]),
            ],
        },
        {
            "id": "stress_clinical_0002",
            "domain": "clinical",
            "source": "handwritten_stress",
            "stress_tags": ["trigger_is_sensitive", "dose_preservation"],
            "text": (
                "Omar Rahman, a 44-year-old beekeeper from Taos, visited Pine Hollow Clinic on June 18, 2025 "
                "(record MRN-990102). He developed diffuse hives, wheezing, and throat tightness 12 minutes "
                "after a bee sting. Dr. Rivera diagnosed anaphylaxis and gave intramuscular epinephrine 0.3 mg."
            ),
            "private_spans": [
                direct("Omar Rahman", "PERSON", "[PATIENT]"),
                direct("Pine Hollow Clinic", "ORG", "[CLINIC]"),
                direct("June 18, 2025", "DATE", "[DATE]"),
                direct("MRN-990102", "ID", "[ID]"),
                direct("Dr. Rivera", "PERSON", "[CLINICIAN]"),
                quasi("44-year-old", "AGE", "mid 40s"),
                quasi("beekeeper", "OCCUPATION", "outdoor worker"),
                quasi("Taos", "LOCATION", "[LOCATION]"),
                quasi("bee sting", "SENSITIVE_EVENT", "[TRIGGER]"),
            ],
            "task_critical_facts": [
                fact("trigger", "bee sting"),
                fact("timeline", "12 minutes after a bee sting"),
                fact("diagnosis", "anaphylaxis"),
                fact("treatment", "intramuscular epinephrine 0.3 mg"),
                fact("age", "44-year-old", True, ["mid 40s"]),
            ],
            "qa": [
                qa("What triggered the reaction?", "bee sting"),
                qa("What treatment was given?", "intramuscular epinephrine 0.3 mg"),
            ],
        },
        {
            "id": "stress_clinical_0003",
            "domain": "clinical",
            "source": "handwritten_stress",
            "stress_tags": ["pediatric_age", "device_failure", "numeric_lab"],
            "text": (
                "Maya Chen, a 9-year-old student from Ely, came to Lakeview Medical Center on July 1, 2025 "
                "(record MRN-990103). Her insulin pump had stopped overnight. Blood glucose was 510 mg/dL, "
                "serum ketones were large, and venous pH was 7.18. Dr. Patel diagnosed diabetic ketoacidosis "
                "from insulin pump failure and started IV insulin and potassium replacement."
            ),
            "private_spans": [
                direct("Maya Chen", "PERSON", "[PATIENT]"),
                direct("Lakeview Medical Center", "ORG", "[CLINIC]"),
                direct("July 1, 2025", "DATE", "[DATE]"),
                direct("MRN-990103", "ID", "[ID]"),
                direct("Dr. Patel", "PERSON", "[CLINICIAN]"),
                quasi("9-year-old", "AGE", "child under 10"),
                quasi("student", "OCCUPATION", "child"),
                quasi("Ely", "LOCATION", "[LOCATION]"),
            ],
            "task_critical_facts": [
                fact("age", "9-year-old", True, ["child under 10"]),
                fact("cause", "insulin pump had stopped overnight"),
                fact("lab", "Blood glucose was 510 mg/dL"),
                fact("lab", "venous pH was 7.18"),
                fact("diagnosis", "diabetic ketoacidosis from insulin pump failure"),
                fact("treatment", "IV insulin and potassium replacement"),
            ],
            "qa": [
                qa("What caused the DKA?", "insulin pump failure", ["insulin pump had stopped overnight"]),
                qa("Which acid-base result was reported?", "venous pH was 7.18"),
            ],
        },
        {
            "id": "stress_clinical_0004",
            "domain": "clinical",
            "source": "handwritten_stress",
            "stress_tags": ["rare_condition", "numeric_lab", "immunosuppression"],
            "text": (
                "Elena Petrova, a 58-year-old kidney-transplant recipient from Sitka, was evaluated at Summit "
                "Regional Hospital on August 3, 2025 (record MRN-990104). She had tremor and rising creatinine. "
                "Tacrolimus trough was 18 ng/mL. Dr. Kim diagnosed tacrolimus toxicity and reduced tacrolimus "
                "from 4 mg twice daily to 2 mg twice daily."
            ),
            "private_spans": [
                direct("Elena Petrova", "PERSON", "[PATIENT]"),
                direct("Summit Regional Hospital", "ORG", "[CLINIC]"),
                direct("August 3, 2025", "DATE", "[DATE]"),
                direct("MRN-990104", "ID", "[ID]"),
                direct("Dr. Kim", "PERSON", "[CLINICIAN]"),
                quasi("58-year-old", "AGE", "late 50s"),
                quasi("kidney-transplant recipient", "SENSITIVE_ATTRIBUTE", "[TRANSPLANT_STATUS]"),
                quasi("Sitka", "LOCATION", "[LOCATION]"),
            ],
            "task_critical_facts": [
                fact("condition", "kidney-transplant recipient"),
                fact("lab", "Tacrolimus trough was 18 ng/mL"),
                fact("diagnosis", "tacrolimus toxicity"),
                fact("treatment", "reduced tacrolimus from 4 mg twice daily to 2 mg twice daily"),
                fact("age", "58-year-old", True, ["late 50s"]),
            ],
            "qa": [
                qa("Which drug level was elevated?", "Tacrolimus trough was 18 ng/mL"),
                qa("How was the tacrolimus dose changed?", "reduced tacrolimus from 4 mg twice daily to 2 mg twice daily"),
            ],
        },
        {
            "id": "stress_clinical_0005",
            "domain": "clinical",
            "source": "handwritten_stress",
            "stress_tags": ["occupation_is_causal", "location_is_private"],
            "text": (
                "Caleb Price, a 34-year-old underground miner from Silverton, visited North Ridge Clinic on "
                "September 12, 2025 (record MRN-990105). He reported progressive dyspnea after 12 years of "
                "silica dust exposure. Chest CT showed upper-lobe nodules and eggshell hilar calcifications. "
                "Dr. Nguyen diagnosed chronic silicosis and advised removal from further silica exposure."
            ),
            "private_spans": [
                direct("Caleb Price", "PERSON", "[PATIENT]"),
                direct("North Ridge Clinic", "ORG", "[CLINIC]"),
                direct("September 12, 2025", "DATE", "[DATE]"),
                direct("MRN-990105", "ID", "[ID]"),
                direct("Dr. Nguyen", "PERSON", "[CLINICIAN]"),
                quasi("34-year-old", "AGE", "early 30s"),
                quasi("underground miner", "OCCUPATION", "dust-exposed worker"),
                quasi("Silverton", "LOCATION", "[LOCATION]"),
            ],
            "task_critical_facts": [
                fact("occupation", "underground miner", True, ["dust-exposed worker"]),
                fact("exposure", "12 years of silica dust exposure"),
                fact("imaging", "upper-lobe nodules and eggshell hilar calcifications"),
                fact("diagnosis", "chronic silicosis"),
                fact("plan", "removal from further silica exposure"),
            ],
            "qa": [
                qa("What exposure explained the lung disease?", "12 years of silica dust exposure"),
                qa("What diagnosis was made?", "chronic silicosis"),
            ],
        },
    ]


def legal_rows() -> list[dict]:
    return [
        {
            "id": "stress_legal_0000",
            "domain": "legal",
            "source": "handwritten_stress",
            "stress_tags": ["sensitive_attribute_is_claim", "article_specificity"],
            "text": (
                "The case originated in application no. 70001/22 against the United Kingdom by Mr Alan Reed "
                "on 4 January 2022. The applicant complained under Article 8 that an investigation into his "
                "sexual orientation and discharge from the Royal Navy had violated his right to private life."
            ),
            "private_spans": [
                direct("70001/22", "CODE", "[ID]"),
                direct("Mr Alan Reed", "PERSON", "[PERSON]"),
                direct("4 January 2022", "DATE", "[DATE]"),
                quasi("United Kingdom", "LOC", "[COUNTRY]"),
                quasi("sexual orientation", "SENSITIVE_ATTRIBUTE", "[SENSITIVE_ATTRIBUTE]"),
                quasi("Royal Navy", "ORG", "armed forces"),
            ],
            "task_critical_facts": [
                fact("legal_basis", "Article 8"),
                fact("claim", "investigation into his sexual orientation and discharge from the Royal Navy had violated his right to private life", answer_aliases=["sexual orientation", "right to private life"]),
            ],
            "qa": [
                qa("Which substantive Article was invoked?", "Article 8"),
                qa("What core claim was raised?", "investigation into his sexual orientation and discharge from the Royal Navy had violated his right to private life", ["sexual orientation", "right to private life"]),
            ],
        },
        {
            "id": "stress_legal_0001",
            "domain": "legal",
            "source": "handwritten_stress",
            "stress_tags": ["case_label", "secret_evidence", "article_specificity"],
            "text": (
                "Application no. 11820/08 was lodged by Ms K. in the Blackspur disciplinary proceedings. "
                "She complained under Article 6 that the tribunal relied on secret evidence without letting "
                "her lawyer inspect it. The Court found a violation."
            ),
            "private_spans": [
                direct("11820/08", "CODE", "[ID]"),
                direct("Ms K.", "PERSON", "[PERSON]"),
                quasi("Blackspur", "CASE_LABEL", "[CASE_LABEL]"),
            ],
            "task_critical_facts": [
                fact("legal_basis", "Article 6"),
                fact("claim", "tribunal relied on secret evidence without letting her lawyer inspect it", answer_aliases=["secret evidence"]),
                fact("outcome", "violation", answer_aliases=["violated"]),
            ],
            "qa": [
                qa("Which substantive Article was invoked?", "Article 6"),
                qa("What core claim was raised?", "tribunal relied on secret evidence without letting her lawyer inspect it", ["secret evidence"]),
                qa("What outcome did the Court state?", "violation", ["violation", "violated"]),
            ],
        },
        {
            "id": "stress_legal_0002",
            "domain": "legal",
            "source": "handwritten_stress",
            "stress_tags": ["role_is_claim", "small_institution", "article_specificity"],
            "text": (
                "In application no. 45510/19, nurse Priya S. complained under Article 10 that she was dismissed "
                "from St. Agnes Oncology Ward after disclosing unsafe staffing levels to a newspaper. The Court "
                "held that the dismissal violated her freedom of expression."
            ),
            "private_spans": [
                direct("45510/19", "CODE", "[ID]"),
                direct("Priya S.", "PERSON", "[PERSON]"),
                quasi("nurse", "ROLE", "healthcare worker"),
                quasi("St. Agnes Oncology Ward", "ORG", "[INSTITUTION]"),
            ],
            "task_critical_facts": [
                fact("legal_basis", "Article 10"),
                fact("claim", "dismissed after disclosing unsafe staffing levels to a newspaper", answer_aliases=["unsafe staffing", "freedom of expression"]),
                fact("outcome", "violation", answer_aliases=["violated"]),
            ],
            "qa": [
                qa("Which substantive Article was invoked?", "Article 10"),
                qa("What core claim was raised?", "dismissed after disclosing unsafe staffing levels to a newspaper", ["unsafe staffing"]),
                qa("What outcome did the Court state?", "violation", ["violation", "violated"]),
            ],
        },
        {
            "id": "stress_legal_0003",
            "domain": "legal",
            "source": "handwritten_stress",
            "stress_tags": ["family_relationship", "domestic_violence", "article_specificity"],
            "text": (
                "Application no. 33440/17 was brought by Ms D. from Lviv. She complained under Article 3 that "
                "police ignored repeated threats from her former partner and failed to protect her from domestic "
                "violence. The Court found a violation."
            ),
            "private_spans": [
                direct("33440/17", "CODE", "[ID]"),
                direct("Ms D.", "PERSON", "[PERSON]"),
                quasi("Lviv", "LOC", "[LOCATION]"),
                quasi("former partner", "RELATION", "[RELATION]"),
                quasi("domestic violence", "SENSITIVE_EVENT", "[SENSITIVE_EVENT]"),
            ],
            "task_critical_facts": [
                fact("legal_basis", "Article 3"),
                fact("claim", "police ignored repeated threats from her former partner and failed to protect her from domestic violence", answer_aliases=["failed to protect her from domestic violence"]),
                fact("outcome", "violation", answer_aliases=["violated"]),
            ],
            "qa": [
                qa("Which substantive Article was invoked?", "Article 3"),
                qa("What core claim was raised?", "police ignored repeated threats from her former partner and failed to protect her from domestic violence", ["domestic violence"]),
                qa("What outcome did the Court state?", "violation", ["violation", "violated"]),
            ],
        },
        {
            "id": "stress_legal_0004",
            "domain": "legal",
            "source": "handwritten_stress",
            "stress_tags": ["detention_status", "diagnosis_sensitive", "article_specificity"],
            "text": (
                "The applicant in no. 22991/16, Mr J., was detained in the Ravenhill secure psychiatric unit. "
                "He complained under Article 5 that he did not receive a speedy review of the lawfulness of his "
                "detention after a diagnosis of schizoaffective disorder. The Court found no violation."
            ),
            "private_spans": [
                direct("22991/16", "CODE", "[ID]"),
                direct("Mr J.", "PERSON", "[PERSON]"),
                quasi("Ravenhill secure psychiatric unit", "ORG", "[INSTITUTION]"),
                quasi("schizoaffective disorder", "SENSITIVE_ATTRIBUTE", "mental health diagnosis"),
            ],
            "task_critical_facts": [
                fact("legal_basis", "Article 5"),
                fact("claim", "did not receive a speedy review of the lawfulness of his detention", answer_aliases=["speedy review of the lawfulness of his detention"]),
                fact("outcome", "no violation"),
            ],
            "qa": [
                qa("Which substantive Article was invoked?", "Article 5"),
                qa("What core claim was raised?", "did not receive a speedy review of the lawfulness of his detention", ["speedy review of the lawfulness of his detention"]),
                qa("What outcome did the Court state?", "no violation"),
            ],
        },
        {
            "id": "stress_legal_0005",
            "domain": "legal",
            "source": "handwritten_stress",
            "stress_tags": ["minority_status_is_claim", "protocol_specificity"],
            "text": (
                "In application no. 78110/20, Mrs Mira B. complained under Article 14 taken with Article 1 of "
                "Protocol No. 1 that survivor benefits were denied because her Roma marriage had not been "
                "registered in a civil ceremony. The Court found a violation."
            ),
            "private_spans": [
                direct("78110/20", "CODE", "[ID]"),
                direct("Mrs Mira B.", "PERSON", "[PERSON]"),
                quasi("Roma marriage", "SENSITIVE_ATTRIBUTE", "[MINORITY_STATUS]"),
            ],
            "task_critical_facts": [
                fact("legal_basis", "Article 14"),
                fact("legal_basis", "Article 1 of Protocol No. 1"),
                fact("claim", "survivor benefits were denied because her Roma marriage had not been registered in a civil ceremony", answer_aliases=["survivor benefits", "Roma marriage"]),
                fact("outcome", "violation"),
            ],
            "qa": [
                qa("Which substantive Article was invoked?", "Article 14"),
                qa("What protocol provision was invoked?", "Article 1 of Protocol No. 1"),
                qa("What core claim was raised?", "survivor benefits were denied because her Roma marriage had not been registered in a civil ceremony", ["survivor benefits", "Roma marriage"]),
                qa("What outcome did the Court state?", "violation"),
            ],
        },
    ]


def build_rows() -> list[dict]:
    return clinical_rows() + legal_rows()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="data/processed/robustness_benchmark.jsonl")
    args = parser.parse_args()
    rows = build_rows()
    write_jsonl(args.out, rows)
    print(f"wrote {len(rows)} stress examples to {args.out}")
    print(f"clinical={sum(1 for r in rows if r['domain'] == 'clinical')} legal={sum(1 for r in rows if r['domain'] == 'legal')}")


if __name__ == "__main__":
    main()
