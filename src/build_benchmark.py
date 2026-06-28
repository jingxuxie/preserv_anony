"""Build a small utility-preserving anonymization benchmark.

The clinical split is synthetic and controlled. The legal split samples short
snippets from the public Text Anonymization Benchmark (TAB) ECHR corpus.
"""

from __future__ import annotations

import argparse
import json
import random
import re
from pathlib import Path

from io_utils import write_jsonl


TAB_DIR = Path("data/raw/text-anonymisation-benchmark")


NAMES = [
    ("Maria Lopez", "she", "her"),
    ("Anthony Reed", "he", "his"),
    ("Priya Shah", "she", "her"),
    ("Elena Petrova", "she", "her"),
    ("James Walker", "he", "his"),
    ("Grace Chen", "she", "her"),
    ("Samuel Ortiz", "he", "his"),
    ("Nadia Hassan", "she", "her"),
]

CLINICS = [
    "North Ridge Clinic",
    "Cedar Valley Hospital",
    "Lakeview Medical Center",
    "Riverside Family Practice",
    "Pine Hollow Clinic",
    "Summit Regional Hospital",
]

CITIES = [
    "Santa Fe",
    "Boise",
    "Burlington",
    "Flagstaff",
    "Madison",
    "Reno",
    "Asheville",
    "Tucson",
]

OCCUPATIONS = [
    "teacher",
    "violin maker",
    "postal worker",
    "long-haul driver",
    "retired judge",
    "farm manager",
    "dental hygienist",
    "software engineer",
]

CLINICAL_SCENARIOS = [
    {
        "diagnosis": "rheumatoid arthritis",
        "symptom": "3 weeks of morning stiffness in both hands",
        "finding": "swelling of the MCP joints",
        "test": "anti-CCP was positive",
        "medication": "methotrexate 15 mg weekly and folic acid 1 mg daily",
        "qa": [
            ("What medication was started?", "methotrexate 15 mg weekly and folic acid 1 mg daily"),
            ("Which lab result supported the suspected diagnosis?", "anti-CCP was positive"),
        ],
    },
    {
        "diagnosis": "pulmonary embolism",
        "symptom": "sudden pleuritic chest pain and shortness of breath",
        "finding": "oxygen saturation was 89 percent on room air",
        "test": "CT angiography showed a segmental pulmonary embolism",
        "medication": "apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily",
        "qa": [
            ("What condition was diagnosed?", "pulmonary embolism"),
            ("What anticoagulation plan was started?", "apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily"),
        ],
    },
    {
        "diagnosis": "diabetic ketoacidosis",
        "symptom": "two days of vomiting, thirst, and abdominal pain",
        "finding": "blood glucose was 482 mg/dL with large serum ketones",
        "test": "venous pH was 7.21",
        "medication": "intravenous insulin and potassium replacement",
        "qa": [
            ("Which acid-base result was reported?", "venous pH was 7.21"),
            ("What treatment was started?", "intravenous insulin and potassium replacement"),
        ],
    },
    {
        "diagnosis": "community-acquired pneumonia",
        "symptom": "5 days of fever, productive cough, and right-sided chest pain",
        "finding": "oxygen saturation was 88 percent on room air",
        "test": "chest x-ray showed a right lower-lobe infiltrate",
        "medication": "ceftriaxone 1 g daily and azithromycin 500 mg daily",
        "qa": [
            ("What did the chest x-ray show?", "right lower-lobe infiltrate"),
            ("Which antibiotics were ordered?", "ceftriaxone 1 g daily and azithromycin 500 mg daily"),
        ],
    },
    {
        "diagnosis": "anaphylaxis",
        "symptom": "diffuse hives, wheezing, and throat tightness within 20 minutes of eating peanuts",
        "finding": "blood pressure fell to 82/48 mmHg",
        "test": "symptoms improved after epinephrine",
        "medication": "intramuscular epinephrine 0.3 mg and observation for 4 hours",
        "qa": [
            ("What exposure preceded the reaction?", "eating peanuts"),
            ("What emergency treatment was given?", "intramuscular epinephrine 0.3 mg"),
        ],
    },
    {
        "diagnosis": "acute appendicitis",
        "symptom": "18 hours of periumbilical pain that migrated to the right lower quadrant",
        "finding": "rebound tenderness was present at McBurney's point",
        "test": "CT abdomen showed an enlarged appendix with periappendiceal fat stranding",
        "medication": "ceftriaxone and metronidazole before laparoscopic appendectomy",
        "qa": [
            ("What did the CT abdomen show?", "enlarged appendix with periappendiceal fat stranding"),
            ("What procedure was planned?", "laparoscopic appendectomy"),
        ],
    },
]


def _phone(i: int) -> str:
    return f"202-555-{1000 + i % 9000:04d}"


def _mrn(i: int) -> str:
    return f"MRN-{710000 + i}"


def _date(i: int) -> str:
    months = [
        "January",
        "February",
        "March",
        "April",
        "May",
        "June",
        "July",
        "August",
        "September",
        "October",
        "November",
        "December",
    ]
    return f"{months[i % 12]} {(i * 7) % 27 + 1}, 2025"


def _age(i: int) -> int:
    return 24 + (i * 7) % 68


def _email(name: str, i: int) -> str:
    base = name.lower().replace(" ", ".")
    return f"{base}{i}@example.com"


def build_clinical(n: int, seed: int) -> list[dict]:
    rng = random.Random(seed)
    rows: list[dict] = []
    for i in range(n):
        name, subj, poss = NAMES[i % len(NAMES)]
        scenario = CLINICAL_SCENARIOS[i % len(CLINICAL_SCENARIOS)]
        clinic = CLINICS[(i * 3) % len(CLINICS)]
        city = CITIES[(i * 5) % len(CITIES)]
        occupation = OCCUPATIONS[(i * 7) % len(OCCUPATIONS)]
        clinician = rng.choice(["Nguyen", "Patel", "O'Connor", "Kim", "Rivera", "Singh"])
        age = _age(i)
        date = _date(i)
        mrn = _mrn(i)
        phone = _phone(i)
        email = _email(name, i)
        text = (
            f"{name}, a {age}-year-old {occupation} from {city}, visited {clinic} "
            f"on {date} (record {mrn}, phone {phone}, email {email}). "
            f"{subj.capitalize()} reported {scenario['symptom']}, with {scenario['finding']}. "
            f"{scenario['test']}. Dr. {clinician} diagnosed {scenario['diagnosis']} "
            f"and started {scenario['medication']}."
        )
        facts = [
            {"type": "symptom", "fact": scenario["symptom"], "generalization_allowed": False},
            {"type": "finding", "fact": scenario["finding"], "generalization_allowed": False},
            {"type": "test", "fact": scenario["test"], "generalization_allowed": False},
            {"type": "diagnosis", "fact": scenario["diagnosis"], "generalization_allowed": False},
            {"type": "treatment", "fact": scenario["medication"], "generalization_allowed": False},
            {
                "type": "age",
                "fact": f"{age}-year-old",
                "generalization_allowed": True,
                "acceptable_generalizations": [age_band(age)],
            },
        ]
        private_spans = [
            {"text": name, "type": "PERSON", "identifier_type": "DIRECT", "replacement": "[PATIENT]"},
            {"text": clinic, "type": "ORG", "identifier_type": "DIRECT", "replacement": "[CLINIC]"},
            {"text": date, "type": "DATE", "identifier_type": "DIRECT", "replacement": "[DATE]"},
            {"text": mrn, "type": "ID", "identifier_type": "DIRECT", "replacement": "[ID]"},
            {"text": phone, "type": "PHONE", "identifier_type": "DIRECT", "replacement": "[PHONE]"},
            {"text": email, "type": "EMAIL", "identifier_type": "DIRECT", "replacement": "[EMAIL]"},
            {"text": f"Dr. {clinician}", "type": "PERSON", "identifier_type": "DIRECT", "replacement": "[CLINICIAN]"},
            {"text": f"{age}-year-old", "type": "AGE", "identifier_type": "QUASI", "replacement": age_band(age)},
            {"text": occupation, "type": "OCCUPATION", "identifier_type": "QUASI", "replacement": "worker"},
            {"text": city, "type": "LOCATION", "identifier_type": "QUASI", "replacement": "[LOCATION]"},
        ]
        qa = [{"q": q, "a": a, "answer_aliases": [a]} for q, a in scenario["qa"]]
        rows.append(
            {
                "id": f"clinical_{i:04d}",
                "domain": "clinical",
                "source": "synthetic_template",
                "text": text,
                "private_spans": private_spans,
                "task_critical_facts": facts,
                "qa": qa,
            }
        )
    return rows


def age_band(age: int) -> str:
    decade = (age // 10) * 10
    if age < 30:
        return "adult under 30"
    if age >= 80:
        return "adult over 80"
    prefix = "early" if age % 10 <= 3 else "mid" if age % 10 <= 6 else "late"
    return f"{prefix} {decade}s"


def _normal_space(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _sentences(text: str) -> list[str]:
    text = _normal_space(text)
    parts = re.split(r"(?<=[.!?])\s+(?=[A-Z\"(])", text)
    return [p.strip() for p in parts if len(p.strip()) > 25]


def _iter_mentions(doc: dict) -> list[dict]:
    mentions: list[dict] = []
    annotations = doc.get("annotations", {})
    annotators = annotations.values() if isinstance(annotations, dict) else annotations
    seen = set()
    for ann in annotators:
        for mention in ann.get("entity_mentions", []):
            key = (
                mention.get("start_offset"),
                mention.get("end_offset"),
                mention.get("span_text"),
                mention.get("identifier_type"),
            )
            if key in seen:
                continue
            seen.add(key)
            mentions.append(mention)
    return mentions


def _find_sentence(sentences: list[str], patterns: list[str]) -> str | None:
    for pattern in patterns:
        rx = re.compile(pattern, re.IGNORECASE)
        for sent in sentences:
            if rx.search(sent):
                return sent
    return None


def _legal_outcome(sentence: str | None) -> str | None:
    if not sentence:
        return None
    lower = sentence.lower()
    if "no violation" in lower:
        return "no violation"
    if "not been a violation" in lower:
        return "no violation"
    if "violation" in lower:
        return "violation"
    if "inadmissible" in lower:
        return "inadmissible"
    return None


def _article_candidates(text: str) -> list[str]:
    allowed = {
        "Article 1",
        "Article 2",
        "Article 3",
        "Article 4",
        "Article 5",
        "Article 6",
        "Article 7",
        "Article 8",
        "Article 9",
        "Article 10",
        "Article 11",
        "Article 12",
        "Article 13",
        "Article 14",
        "Article 15",
        "Article 17",
        "Article 18",
    }
    articles = []
    for article in re.findall(r"\bArticle\s+\d+[A-Za-z]?\b", text):
        if article not in allowed:
            continue
        if article not in articles:
            articles.append(article)
    return articles


def _find_complaint_sentence(sentences: list[str]) -> str | None:
    for sent in sentences:
        low = sent.lower()
        if not any(token in low for token in ["complain", "allege", "submitted", "relied"]):
            continue
        if _article_candidates(sent):
            return sent
    return None


def _claim_phrase(sentence: str) -> str | None:
    patterns = [
        r"\bcomplained\s+under\b.*?\bthat\b,?\s+(.+)",
        r"\b(?:complained|alleged|submitted)\b.*?\bthat\b,?\s+(.+)",
        r"\bcomplained\s+of\s+(.+)",
        r"\bcomplained\s+under\s+Article[^.]{0,160}?\babout\s+(.+)",
        r"\bcomplained\s+under\s+Article[^.]{0,160}?\bof\s+(.+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, sentence, flags=re.IGNORECASE)
        if not match:
            continue
        phrase = _clean_claim_phrase(match.group(1))
        if phrase:
            return phrase
    return None


def _clean_claim_phrase(phrase: str) -> str | None:
    phrase = _normal_space(phrase)
    protected = re.sub(
        r"\b(Protocol No|Art|art|No)\.\s+",
        lambda match: f"{match.group(1)}<DOT> ",
        phrase,
    )
    phrase = re.split(r";|(?<!<DOT>)\.\s|,\s+and\s+", protected)[0]
    phrase = phrase.replace("<DOT>", ".")
    phrase = re.sub(r"\s+On\s+\d{1,2}\s+[A-Z].*$", "", phrase)
    phrase = phrase.strip(" .")
    if not phrase:
        return None
    if re.fullmatch(r"(?:the Convention and )?Article \d+ of Protocol No\.?\s*$", phrase, flags=re.IGNORECASE):
        return None
    if re.fullmatch(r"Protocol No\.?\s*\d*", phrase, flags=re.IGNORECASE):
        return None
    if len(phrase) <= 360:
        return phrase
    cut = phrase[:360]
    for marker in [", which ", ", as ", ", because ", " and ", " in which "]:
        idx = cut.rfind(marker)
        if idx >= 80 and not re.search(r"\b(?:Protocol No|art|Art)\.?\s*$", cut[:idx], flags=re.IGNORECASE):
            return cut[:idx].strip(" ,.")
    truncated = cut.rsplit(" ", 1)[0].strip(" ,.")
    if re.search(r"\b(?:Protocol No|art|Art)\.?\s*$", truncated, flags=re.IGNORECASE):
        return None
    if re.search(r"\b(?:under|of|and|or|with|to|the|a|an)\s*$", truncated, flags=re.IGNORECASE):
        return None
    return truncated


def _claim_aliases(claim: str) -> list[str]:
    aliases = []
    patterns = [
        r"\bfreedom of expression\b",
        r"\bright to [^,;.]+",
        r"\breasonable time\b",
        r"\blength of [^,;.]+",
        r"\bpre-trial detention\b",
        r"\bsearch and seizure\b",
        r"\bunfairness of [^,;.]+",
        r"\bfair trials?\b",
        r"\bprivate and family life\b",
        r"\baccess to a court\b",
        r"\bcontact with (?:his|her) (?:son|daughter)\b",
        r"\bdetention\b",
        r"\bdischarge from [^,;.]+",
        r"\bincitement of offences\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, claim, flags=re.IGNORECASE)
        if not match:
            continue
        alias = _normal_space(match.group(0)).strip(" .")
        if len(alias) >= 8 and alias.lower() not in {a.lower() for a in aliases}:
            aliases.append(alias)
    return aliases


def _application_numbers(snippet: str) -> list[str]:
    numbers = []
    for match in re.finditer(r"\b\d{2,6}/\d{2,4}\b", snippet):
        value = match.group(0)
        if value not in numbers:
            numbers.append(value)
    return numbers


def _upsert_direct_legal_id(private_spans: list[dict], span: str) -> None:
    key = span.lower()
    for item in private_spans:
        if str(item.get("text", "")).lower() == key:
            item["identifier_type"] = "DIRECT"
            item["type"] = "CODE"
            item["replacement"] = "[ID]"
            return
    private_spans.append(
        {
            "text": span,
            "type": "CODE",
            "identifier_type": "DIRECT",
            "replacement": "[ID]",
        }
    )


def build_legal(n: int, seed: int, tab_dir: Path = TAB_DIR) -> list[dict]:
    rng = random.Random(seed)
    docs: list[dict] = []
    for name in ["echr_dev.json", "echr_test.json", "echr_train.json"]:
        path = tab_dir / name
        if path.exists():
            with path.open("r", encoding="utf-8") as f:
                docs.extend(json.load(f))
    rng.shuffle(docs)

    rows: list[dict] = []
    for doc in docs:
        sentences = _sentences(doc.get("text", ""))
        if not sentences:
            continue
        applicant = doc.get("meta", {}).get("applicant")
        intro = None
        if applicant:
            intro = _find_sentence(sentences[:15], [re.escape(str(applicant).split()[0])])
        intro = intro or _find_sentence(sentences[:15], [r"\bapplication\b", r"\bapplicant\b"])
        complaint = _find_complaint_sentence(sentences)
        outcome_sent = _find_sentence(
            list(reversed(sentences)),
            [r"\bno violation\b.*\bArticle\b", r"\bviolation of Article\b", r"\binadmissible\b"],
        )
        if not complaint:
            continue
        selected = []
        for sent in [intro, complaint, outcome_sent]:
            if sent and sent not in selected:
                selected.append(sent)
        snippet = _normal_space(" ".join(selected))
        articles = _article_candidates(snippet)
        if len(snippet) < 120 or not articles:
            continue
        if len(snippet) > 1400:
            snippet = snippet[:1400].rsplit(" ", 1)[0] + "."

        private_spans = []
        seen_spans = set()
        for mention in _iter_mentions(doc):
            span = _normal_space(str(mention.get("span_text", "")))
            identifier_type = mention.get("identifier_type")
            if identifier_type not in {"DIRECT", "QUASI"}:
                continue
            if len(span) < 2 or span.lower() not in snippet.lower():
                continue
            key = span.lower()
            if key in seen_spans:
                continue
            seen_spans.add(key)
            private_spans.append(
                {
                    "text": span,
                    "type": mention.get("entity_type", "UNKNOWN"),
                    "identifier_type": identifier_type,
                    "replacement": replacement_for_legal(mention.get("entity_type", "UNKNOWN"), identifier_type),
                }
            )
        if not any(s["identifier_type"] == "DIRECT" for s in private_spans):
            continue
        for number in _application_numbers(snippet):
            _upsert_direct_legal_id(private_spans, number)

        outcome = _legal_outcome(outcome_sent)
        country = doc.get("meta", {}).get("countries")
        facts = [
            {
                "type": "legal_basis",
                "fact": articles[0],
                "generalization_allowed": False,
            }
        ]
        if outcome:
            facts.append({"type": "outcome", "fact": outcome, "generalization_allowed": False})
        claim = _claim_phrase(complaint)
        if claim:
            claim_fact = {
                "type": "claim",
                "fact": claim,
                "generalization_allowed": False,
            }
            aliases = _claim_aliases(claim)
            if aliases:
                claim_fact["answer_aliases"] = aliases
            facts.append(
                claim_fact
            )
        if country and country in snippet:
            facts.append({"type": "state", "fact": country, "generalization_allowed": False})

        qa = [{"q": "Which substantive Article was invoked?", "a": articles[0], "answer_aliases": [articles[0]]}]
        if outcome:
            qa.append({"q": "What outcome did the Court state?", "a": outcome, "answer_aliases": [outcome]})
        if claim:
            qa.append({"q": "What core claim was raised?", "a": claim, "answer_aliases": [claim, *_claim_aliases(claim)]})

        rows.append(
            {
                "id": f"legal_{len(rows):04d}",
                "domain": "legal",
                "source": f"TAB:{doc.get('dataset_type')}:{doc.get('doc_id')}",
                "text": snippet,
                "private_spans": private_spans,
                "task_critical_facts": facts,
                "qa": qa,
            }
        )
        if len(rows) >= n:
            break
    return rows


def replacement_for_legal(entity_type: str, identifier_type: str) -> str:
    if identifier_type == "QUASI":
        if entity_type == "DATETIME":
            return "[DATE]"
        if entity_type == "QUANTITY":
            return "[QUANTITY]"
        if entity_type == "LOC":
            return "[LOCATION]"
        if entity_type == "ORG":
            return "[ORGANIZATION]"
        return "[QUASI]"
    if entity_type == "PERSON":
        return "[PERSON]"
    if entity_type == "CODE":
        return "[ID]"
    if entity_type == "LOC":
        return "[LOCATION]"
    if entity_type == "ORG":
        return "[ORGANIZATION]"
    return "[IDENTIFIER]"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clinical-n", type=int, default=50)
    parser.add_argument("--legal-n", type=int, default=50)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--out", default="data/processed/benchmark.jsonl")
    args = parser.parse_args()

    clinical = build_clinical(args.clinical_n, args.seed)
    legal = build_legal(args.legal_n, args.seed)
    rows = clinical + legal
    write_jsonl(args.out, rows)
    print(f"wrote {len(rows)} examples to {args.out}")
    print(f"clinical={len(clinical)} legal={len(legal)}")


if __name__ == "__main__":
    main()
