"""Deterministic anonymizers for fast local experiments.

These are intentionally simple. The oracle variants use benchmark annotations
to estimate upper-bound behavior and to debug metrics before API runs.
"""

from __future__ import annotations

import re
import os
from pathlib import Path


METHODS = [
    "regex_rules",
    "presidio_baseline",
    "direct_span_oracle",
    "privacy_first_oracle",
    "critical_span_guard_oracle",
]


def anonymize(example: dict, method: str) -> str:
    if method == "regex_rules":
        return regex_rules(example["text"])
    if method == "presidio_baseline":
        return presidio_baseline(example["text"])
    if method == "direct_span_oracle":
        return direct_span_oracle(example)
    if method == "privacy_first_oracle":
        return privacy_first_oracle(example)
    if method == "critical_span_guard_oracle":
        return critical_span_guard_oracle(example)
    raise ValueError(f"unknown method: {method}")


def regex_rules(text: str) -> str:
    """Pattern-only baseline that does not use gold annotations."""

    out = text
    out = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[EMAIL]", out)
    out = re.sub(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{2,4}[-.\s]\d{4}\b", "[PHONE]", out)
    out = re.sub(r"\b\d{3}[-.]\d{4}\b", "[PHONE]", out)
    out = re.sub(r"\bMRN[-\s]?\d+\b", "[ID]", out, flags=re.IGNORECASE)
    out = re.sub(r"\brecord\s+[A-Z]{2,5}-?\d+\b", "record [ID]", out, flags=re.IGNORECASE)
    out = re.sub(r"\bno\.\s*\d+/\d+\b", "no. [ID]", out, flags=re.IGNORECASE)
    out = re.sub(
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",
        "[DATE]",
        out,
    )
    out = re.sub(r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b", "[DATE]", out)
    out = re.sub(r"\b(?:Mr|Mrs|Ms|Miss|Dr)\.?\s+[A-Z][A-Za-z'.-]+(?:\s+[A-Z][A-Za-z'.-]+)?", "[PERSON]", out)
    out = re.sub(r"^([A-Z][A-Za-z'.-]+\s+[A-Z][A-Za-z'.-]+),", "[PERSON],", out)
    out = re.sub(
        r"\b[A-Z][A-Za-z'.-]+(?:\s+[A-Z][A-Za-z'.-]+){0,3}\s+(?:Clinic|Hospital|Medical Center|Family Practice)\b",
        "[INSTITUTION]",
        out,
    )
    out = re.sub(r"\bfrom\s+[A-Z][A-Za-z'.-]+(?:\s+[A-Z][A-Za-z'.-]+)?\b", "from [LOCATION]", out)
    return _clean(out)


_PRESIDIO_ANALYZER = None
_PRESIDIO_ANONYMIZER = None


def presidio_baseline(text: str) -> str:
    """Microsoft Presidio baseline with typed replacement placeholders."""

    analyzer, anonymizer, operator_config = _get_presidio()
    results = analyzer.analyze(text=text, language="en")
    anonymized = anonymizer.anonymize(
        text=text,
        analyzer_results=results,
        operators={
            "PERSON": operator_config("replace", {"new_value": "[PERSON]"}),
            "LOCATION": operator_config("replace", {"new_value": "[LOCATION]"}),
            "DATE_TIME": operator_config("replace", {"new_value": "[DATE]"}),
            "EMAIL_ADDRESS": operator_config("replace", {"new_value": "[EMAIL]"}),
            "PHONE_NUMBER": operator_config("replace", {"new_value": "[PHONE]"}),
            "US_SSN": operator_config("replace", {"new_value": "[ID]"}),
            "IBAN_CODE": operator_config("replace", {"new_value": "[ID]"}),
            "CREDIT_CARD": operator_config("replace", {"new_value": "[ID]"}),
            "DEFAULT": operator_config("replace", {"new_value": "[PII]"}),
        },
    )
    return _clean(anonymized.text)


def _get_presidio():
    global _PRESIDIO_ANALYZER, _PRESIDIO_ANONYMIZER
    if _PRESIDIO_ANALYZER is None or _PRESIDIO_ANONYMIZER is None:
        cache_dir = Path("data/processed/.cache/tldextract").resolve()
        cache_dir.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("TLDEXTRACT_CACHE", str(cache_dir))

        from presidio_analyzer import AnalyzerEngine
        from presidio_analyzer.nlp_engine import NlpEngineProvider
        from presidio_anonymizer import AnonymizerEngine
        from presidio_anonymizer.entities import OperatorConfig

        config = {
            "nlp_engine_name": "spacy",
            "models": [{"lang_code": "en", "model_name": "en_core_web_sm"}],
        }
        nlp_engine = NlpEngineProvider(nlp_configuration=config).create_engine()
        _PRESIDIO_ANALYZER = AnalyzerEngine(nlp_engine=nlp_engine, supported_languages=["en"])
        _PRESIDIO_ANONYMIZER = AnonymizerEngine()
        return _PRESIDIO_ANALYZER, _PRESIDIO_ANONYMIZER, OperatorConfig
    from presidio_anonymizer.entities import OperatorConfig

    return _PRESIDIO_ANALYZER, _PRESIDIO_ANONYMIZER, OperatorConfig


def direct_span_oracle(example: dict) -> str:
    spans = [s for s in example["private_spans"] if s["identifier_type"] == "DIRECT"]
    return replace_spans(example["text"], spans)


def privacy_first_oracle(example: dict) -> str:
    """Aggressively redact gold privacy spans and sensitive-looking values."""

    out = replace_spans(example["text"], example["private_spans"])
    # Conservative policies often over-generalize values that are also utility.
    out = re.sub(r"\bArticle\s+\d+[A-Za-z]?\b", "Article [NUMBER]", out)
    out = re.sub(r"\b\d+(?:\.\d+)?\s*(?:mg|g|mcg|units|mL|mmHg|percent|%)\b", "[VALUE]", out, flags=re.IGNORECASE)
    out = re.sub(r"\b\d+/\d+\s*mmHg\b", "[VALUE]", out, flags=re.IGNORECASE)
    out = re.sub(r"\b\d+(?:\.\d+)?\s*mg/dL\b", "[VALUE]", out, flags=re.IGNORECASE)
    out = re.sub(r"\bpH\s+(?:was\s+)?\d+(?:\.\d+)?\b", "pH [VALUE]", out, flags=re.IGNORECASE)
    out = re.sub(r"\b\d+\s+(?:minutes?|hours?|days?|weeks?|months?|years?)\b", "[DURATION]", out, flags=re.IGNORECASE)
    out = re.sub(r"\b(?:right|left)\s+lower-lobe\b", "[LOCATION]", out, flags=re.IGNORECASE)
    out = re.sub(r"\b(?:peanuts|anti-CCP|McBurney's point)\b", "[SPECIFIC_DETAIL]", out, flags=re.IGNORECASE)
    return _clean(out)


def critical_span_guard_oracle(example: dict) -> str:
    """Gold-informed CSG approximation: redact privacy spans unless protected."""

    protected = protected_strings(example)
    out = example["text"]
    spans = sorted(example["private_spans"], key=lambda s: len(s["text"]), reverse=True)
    for span in spans:
        text = span["text"]
        identifier_type = span["identifier_type"]
        if identifier_type == "QUASI" and _is_protected(text, protected):
            replacement = protected_replacement(span, example)
        else:
            replacement = span.get("replacement") or default_replacement(span)
        out = replace_literal(out, text, replacement)
    return _clean(out)


def protected_strings(example: dict) -> list[str]:
    protected: list[str] = []
    for fact in example.get("task_critical_facts", []):
        protected.append(str(fact.get("fact", "")))
        for alias in fact.get("acceptable_generalizations", []):
            protected.append(str(alias))
    for qa in example.get("qa", []):
        protected.append(str(qa.get("a", "")))
        protected.extend(str(a) for a in qa.get("answer_aliases", []))
    return [p for p in protected if p]


def _is_protected(text: str, protected: list[str]) -> bool:
    low = text.lower()
    return any(low in item.lower() for item in protected)


def protected_replacement(span: dict, example: dict) -> str:
    """Use the least identifying allowed form for protected quasi-identifiers."""

    span_text = span["text"]
    for fact in example.get("task_critical_facts", []):
        if span_text.lower() not in str(fact.get("fact", "")).lower():
            continue
        if fact.get("generalization_allowed") and fact.get("acceptable_generalizations"):
            return str(fact["acceptable_generalizations"][0])
        return span_text
    return span.get("replacement") or span_text


def replace_spans(text: str, spans: list[dict]) -> str:
    out = text
    for span in sorted(spans, key=lambda s: len(s["text"]), reverse=True):
        out = replace_literal(out, span["text"], span.get("replacement") or default_replacement(span))
    return _clean(out)


def replace_literal(text: str, old: str, new: str) -> str:
    if not old:
        return text
    return re.sub(re.escape(old), new, text)


def default_replacement(span: dict) -> str:
    identifier_type = span.get("identifier_type")
    typ = str(span.get("type", "IDENTIFIER")).upper()
    if identifier_type == "QUASI":
        return "[QUASI]"
    if "PERSON" in typ:
        return "[PERSON]"
    if typ in {"DATE", "DATETIME"}:
        return "[DATE]"
    if typ in {"PHONE"}:
        return "[PHONE]"
    if typ in {"EMAIL"}:
        return "[EMAIL]"
    if typ in {"ID", "CODE"}:
        return "[ID]"
    if typ in {"ORG"}:
        return "[ORGANIZATION]"
    if typ in {"LOC", "LOCATION"}:
        return "[LOCATION]"
    return "[IDENTIFIER]"


def _clean(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:)])", r"\1", text)
    text = re.sub(r"([(])\s+", r"\1", text)
    return text.strip()
