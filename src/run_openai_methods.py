"""Run a tiny cached OpenAI anonymization smoke test.

This script is intentionally conservative: it defaults to a small balanced
subset and caches every response by prompt hash to avoid repeat spend.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import time
import urllib.error
import urllib.request
import re
from pathlib import Path

from io_utils import read_jsonl, write_jsonl


MODEL_PREFERENCES = [
    "gpt-4.1-nano",
    "gpt-4.1-mini",
    "gpt-4o-mini",
]


GENERIC_PROMPT = """You are de-identifying sensitive text before it is used for AI research.
Remove or replace personally identifying information, including names, addresses, exact dates, contact information, IDs, institutions, and other details that could identify a person.
Preserve the meaning of the document as much as possible.
Return only the anonymized text.

Text:
{text}
"""


PRIVACY_FIRST_PROMPT = """You are de-identifying sensitive text before it is used for AI research.
Your priority is privacy protection.
Remove, replace, or generalize any information that could identify a person, including direct identifiers, rare locations, exact dates, named institutions, rare occupations, unique events, and combinations of details.
When uncertain, generalize or remove the information.
Return only the anonymized text.

Text:
{text}
"""


CSG_GOLD_PROMPT = """You are anonymizing sensitive text for AI research.
You must protect privacy while preserving task-critical domain meaning.

Privacy spans to remove or generalize:
{privacy_spans}

Task-critical facts to preserve:
{task_facts}

Rules:
1. Replace direct identifiers with typed placeholders such as [PATIENT], [PERSON], [CLINICIAN], [COURT], [LOCATION], [DATE], [ID].
2. Generalize quasi-identifiers when possible instead of deleting them.
3. Preserve task-critical facts needed for clinical or legal reasoning.
4. If a span is both privacy-relevant and task-critical, preserve the least identifying version that keeps the downstream meaning.
5. Do not invent new facts.
6. Return only the anonymized text.

Original text:
{text}
"""


EXTRACT_PRIVACY_AND_FACTS_PROMPT = """You are preparing sensitive text for utility-preserving anonymization.

Extract two things:
1. privacy spans that should be removed or generalized,
2. task-critical domain facts that must be preserved for downstream reasoning.

For clinical-style text, task-critical facts include symptoms, diagnosis, medication, dose, allergy, lab result, imaging result, temporal sequence, severity, and clinically relevant age.
For legal text, task-critical facts include party roles, legal basis, claim, procedure, court reasoning, outcome, chronology, and statute/article references.
Clinical medications, doses, lab values, imaging findings, diagnoses, procedures, and clinically meaningful timelines should usually have "generalization_allowed": false. Age may be generalized to a clinically meaningful band. Non-clinical occupations and cities should not be task-critical unless the text makes them clinically relevant.
Legal Article/statute numbers, claims, procedure, court outcomes, and reasoning should usually have "generalization_allowed": false. Legal case/application numbers are privacy spans, not task-critical legal bases.

Direct identifiers include names, contact details, addresses, exact dates, IDs, account numbers, medical record numbers, legal case/application numbers, and named institutions tied to a person.
Quasi-identifiers include age, occupation, city, rare disease/event, family relation, sensitive attribute, nationality, and combinations of details that may enable re-identification.

Return only valid JSON with this schema:
{{
  "domain": "clinical" or "legal",
  "privacy_spans": [
    {{"span": "...", "type": "...", "identifier_type": "DIRECT" or "QUASI", "risk": 0-3, "replacement": "..."}}
  ],
  "task_critical_facts": [
    {{"type": "...", "fact": "...", "generalization_allowed": true or false, "reason": "..."}}
  ]
}}

Text:
{text}
"""


CSG_EXTRACTED_PROMPT = """You are anonymizing sensitive text for AI research.
You must protect privacy while preserving task-critical domain meaning.

Privacy spans to remove or generalize:
{privacy_spans}

Task-critical facts to preserve:
{task_facts}

Rules:
1. Replace direct identifiers with typed placeholders such as [PATIENT], [PERSON], [CLINICIAN], [COURT], [LOCATION], [DATE], [ID].
2. Generalize quasi-identifiers when possible instead of deleting them.
3. Preserve task-critical facts needed for clinical or legal reasoning.
4. If a span is both privacy-relevant and task-critical, preserve the least identifying version that keeps downstream meaning.
5. Preserve specific clinical medications, doses, lab values, diagnoses, symptoms, imaging findings, and medically meaningful timelines unless they are direct identifiers.
6. Preserve legal article/statute numbers, claims, procedural posture, court outcomes, and reasoning unless they are direct identifiers.
7. Legal case/application numbers such as "no. 12345/06" or "nos. 12345/06 and 67890/07" are direct identifiers and must be replaced with [ID], while legal Article numbers must be preserved.
8. Do not invent new facts.
9. Return only the anonymized text.

Original text:
{text}
"""


CSG_VERIFY_REPAIR_PROMPT = """You are verifying anonymized text.
Compare the original and anonymized text using the task-critical facts and privacy spans below.

Original text:
{original_text}

Anonymized text:
{anonymized_text}

Task-critical facts:
{task_facts}

Known privacy spans:
{privacy_spans}

Check for:
1. leaked direct identifiers,
2. high-risk quasi-identifiers that can be generalized without harming task-critical meaning,
3. omitted task-critical facts,
4. contradicted task-critical facts,
5. invented facts.

If the anonymized text is acceptable, return only valid JSON:
{{"status": "accept", "text": "..."}}

If not, return only valid JSON:
{{"status": "repair", "issues": ["..."], "text": "REPAIRED_ANONYMIZED_TEXT"}}

The repaired text must not reintroduce direct identifiers.
Legal case/application numbers such as "no. 12345/06" or "nos. 12345/06 and 67890/07" are direct identifiers and must be replaced with [ID], while legal Article numbers must be preserved.
Specific clinical medications, doses, lab values, imaging findings, diagnoses, procedures, and meaningful timelines must remain specific unless they are direct identifiers.
"""


def load_key(path: str) -> str:
    key = Path(path).read_text(encoding="utf-8").strip()
    if not key:
        raise RuntimeError(f"empty API key file: {path}")
    return key


def request_json(url: str, api_key: str, payload: dict | None = None, timeout: int = 60) -> dict:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data)
    req.add_header("Authorization", f"Bearer {api_key}")
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def choose_model(api_key: str, requested: str) -> str:
    if requested != "auto":
        return requested
    data = request_json("https://api.openai.com/v1/models", api_key, None, timeout=30)
    available = {item["id"] for item in data.get("data", [])}
    for model in MODEL_PREFERENCES:
        if model in available:
            return model
    for item in sorted(available):
        if "mini" in item or "nano" in item:
            return item
    raise RuntimeError("could not find a preferred low-cost model in /v1/models")


def uses_max_completion_tokens(model: str) -> bool:
    model_name = model.lower()
    return model_name.startswith("gpt-5") or model_name.startswith("o")


def chat_completion(api_key: str, model: str, prompt: str, max_tokens: int, json_mode: bool = False) -> tuple[str, dict, float]:
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
    }
    if not uses_max_completion_tokens(model):
        payload["temperature"] = 0
    token_key = "max_completion_tokens" if uses_max_completion_tokens(model) else "max_tokens"
    payload[token_key] = max_tokens
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
    last_error = None
    for attempt in range(4):
        try:
            start = time.perf_counter()
            data = request_json("https://api.openai.com/v1/chat/completions", api_key, payload)
            elapsed_ms = (time.perf_counter() - start) * 1000.0
            return data["choices"][0]["message"]["content"].strip(), data.get("usage", {}), elapsed_ms
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            last_error = f"HTTP {exc.code}: {body[:500]}"
            if exc.code not in {429, 500, 502, 503, 504}:
                raise RuntimeError(last_error) from exc
        except urllib.error.URLError as exc:
            last_error = str(exc)
        time.sleep(2**attempt)
    raise RuntimeError(f"OpenAI request failed after retries: {last_error}")


def load_cache(path: str) -> dict[str, dict]:
    cache: dict[str, dict] = {}
    p = Path(path)
    if not p.exists():
        return cache
    for row in read_jsonl(p):
        if "text" not in row and "anonymized_text" in row:
            row["text"] = row["anonymized_text"]
        cache[row["cache_key"]] = row
    return cache


def append_cache(path: str, row: dict) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=True, sort_keys=True) + "\n")


def cache_key(model: str, method: str, example_id: str, prompt: str) -> str:
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return f"{model}:{method}:{example_id}:{digest}"


def cached_completion(
    api_key: str,
    model: str,
    cache: dict[str, dict],
    cache_path: str,
    method: str,
    example_id: str,
    prompt: str,
    max_tokens: int,
    json_mode: bool = False,
    cache_only: bool = False,
) -> tuple[str, int]:
    key = cache_key(model, method, example_id, prompt)
    if key in cache:
        cached_text = cache[key]["text"]
        if json_mode:
            try:
                parse_json_object(cached_text)
                return cached_text, 0
            except (json.JSONDecodeError, ValueError):
                if cache_only:
                    raise
        else:
            return cached_text, 0
    if cache_only:
        raise KeyError(f"missing cache key for {example_id} {method}: {key}")
    last_json_error = None
    usage: dict = {}
    elapsed_ms = 0.0
    last_text = ""
    for _ in range(3 if json_mode else 1):
        text, usage, elapsed_ms = chat_completion(api_key, model, prompt, max_tokens, json_mode=json_mode)
        last_text = text
        if not json_mode:
            break
        try:
            parse_json_object(text)
            break
        except (json.JSONDecodeError, ValueError) as exc:
            last_json_error = exc
    else:
        excerpt = repr(last_text[:300])
        raise RuntimeError(
            f"OpenAI returned invalid JSON for {example_id} {method}: {last_json_error}; response_excerpt={excerpt}"
        )
    row = {
        "cache_key": key,
        "model": model,
        "method": method,
        "id": example_id,
        "text": text,
        "usage": usage,
        "elapsed_ms": elapsed_ms,
        "prompt_chars": len(prompt),
        "response_chars": len(text),
    }
    append_cache(cache_path, row)
    cache[key] = row
    return text, 1


def select_examples(examples: list[dict], max_examples: int, seed: int) -> list[dict]:
    by_domain: dict[str, list[dict]] = {}
    for example in examples:
        by_domain.setdefault(example["domain"], []).append(example)
    rng = random.Random(seed)
    selected = []
    per_domain = max(1, max_examples // max(1, len(by_domain)))
    for domain in sorted(by_domain):
        rows = by_domain[domain][:]
        rng.shuffle(rows)
        selected.extend(rows[:per_domain])
    return selected[:max_examples]


def prompt_for(method: str, example: dict) -> str:
    if method == "generic_llm":
        return GENERIC_PROMPT.format(text=example["text"])
    if method == "privacy_first_llm":
        return PRIVACY_FIRST_PROMPT.format(text=example["text"])
    if method == "critical_span_guard_goldprompt":
        privacy_spans = json.dumps(example["private_spans"], ensure_ascii=True)
        task_facts = json.dumps(example["task_critical_facts"], ensure_ascii=True)
        return CSG_GOLD_PROMPT.format(
            text=example["text"],
            privacy_spans=privacy_spans,
            task_facts=task_facts,
        )
    raise ValueError(f"unknown OpenAI method: {method}")


def parse_json_object(text: str) -> dict:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            return json.loads(text[start : end + 1])
        raise


def safety_scrub_direct_identifiers(text: str) -> str:
    """Final deterministic safety net for obvious direct identifiers."""

    out = text
    out = re.sub(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b", "[EMAIL]", out)
    out = re.sub(r"\b(?:\+?1[-.\s]?)?\(?\d{3}\)?[-.\s]\d{2,4}[-.\s]\d{4}\b", "[PHONE]", out)
    out = re.sub(r"\bMRN[-\s]?\d+\b", "[ID]", out, flags=re.IGNORECASE)
    out = re.sub(r"\brecord\s+\[?ID\]?[-\s]?\d*\b", "record [ID]", out, flags=re.IGNORECASE)
    out = re.sub(
        r"\b[A-Z][A-Za-z'.-]+(?:\s+[A-Z][A-Za-z'.-]+){0,3}\s+(?:Clinic|Hospital|Medical Center|Family Practice)\b",
        "[CLINIC]",
        out,
    )
    out = re.sub(
        r"\b(no\.|nos\.)\s+\d{2,6}/\d{2,4}(?:\s*(?:,|and)\s*\d{2,6}/\d{2,4})*",
        r"\1 [ID]",
        out,
        flags=re.IGNORECASE,
    )
    out = re.sub(r"\b(\d{1,3})-year-old\b", lambda m: age_band(int(m.group(1))), out)
    out = re.sub(
        r"\b(?:teacher|violin maker|postal worker|long-haul driver|retired judge|farm manager|dental hygienist|software engineer)\b",
        "worker",
        out,
        flags=re.IGNORECASE,
    )
    return re.sub(r"\s+", " ", out).strip()


def extract_substantive_legal_articles(text: str) -> list[str]:
    """Return legal Article references, preferring non-procedural Articles."""

    matches = []
    for match in re.finditer(r"\bArticle\s+(\d+)(?:\s*[§\u00a7]\s*[\d and,]+)?", text, flags=re.IGNORECASE):
        number = match.group(1)
        matches.append((number, f"Article {number}"))
    if not matches:
        return []

    substantive = [article for number, article in matches if number not in {"25", "34"}]
    candidates = substantive or [article for _, article in matches]
    out = []
    seen = set()
    for article in candidates:
        key = article.lower()
        if key not in seen:
            out.append(article)
            seen.add(key)
    return out


def repair_legal_article_placeholders(original_text: str, anonymized_text: str) -> str:
    """Restore non-identifying legal Article numbers in over-generalized CSG text."""

    articles = extract_substantive_legal_articles(original_text)
    if not articles:
        return anonymized_text
    article = articles[0]
    out = anonymized_text
    one_group_contexts = [
        r"(Relying on\s+)Legal basis",
        r"(relied on\s+)Legal basis",
        r"(contrary to\s+)Legal basis",
        r"(secured by\s+)Legal basis",
        r"(violation of\s+)Legal basis",
        r"(violated\s+)Legal basis",
        r"(complained under\s+)Legal basis",
    ]
    for pattern in one_group_contexts:
        out = re.sub(pattern, rf"\1{article}", out, flags=re.IGNORECASE)
    out = re.sub(r"(under\s+)Legal basis(\s+to a fair hearing)", rf"\1{article}\2", out, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", out).strip()


def repair_legal_case_labels(task_facts: list[dict], anonymized_text: str) -> str:
    """Replace quoted case/proceeding labels unless they are task-critical facts."""

    fact_text = " ".join(str(fact.get("fact", "")) for fact in task_facts).lower()

    def replace(match: re.Match[str]) -> str:
        label = match.group("label")
        noun = match.group("noun")
        if label.lower() in fact_text:
            return match.group(0)
        return f"[CASE_LABEL] {noun}"

    out = re.sub(
        r"[\u201c\"](?P<label>[A-Z][A-Za-z0-9-]{3,})[\u201d\"]\s+(?P<noun>proceedings|case|investigation|inquiry|operation)",
        replace,
        anonymized_text,
    )
    return re.sub(r"\s+", " ", out).strip()


def repair_legal_detention_regime_labels(task_facts: list[dict], anonymized_text: str) -> str:
    """Generalize quoted detention-regime labels unless they are task-critical."""

    fact_text = " ".join(str(fact.get("fact", "")) for fact in task_facts).lower()

    def replace(match: re.Match[str]) -> str:
        label = match.group("label")
        if label.lower() in fact_text:
            return match.group(0)
        if re.search(r"\b(?:detainee|detention|prisoner|custod)\w*\b", label, flags=re.IGNORECASE):
            return "the restrictive detention regime" if match.group("article") else "a restrictive detention regime"
        return match.group(0)

    out = re.sub(
        r"\b(?P<article>the\s+)?[\u201c\"](?P<label>[A-Za-z][A-Za-z -]{3,})[\u201d\"]\s+regime",
        replace,
        anonymized_text,
    )
    return re.sub(r"\s+", " ", out).strip()


def medication_name_from_fact(fact: str) -> str | None:
    text = str(fact).strip()
    if not text:
        return None
    text = re.split(r"\s+before\s+|\s+after\s+|\s+for\s+\d", text, maxsplit=1, flags=re.IGNORECASE)[0]
    text = re.split(r"\s+\d", text, maxsplit=1)[0].strip(" .,")
    if len(text) < 3:
        return None
    return text


def repair_clinical_medication_placeholders(task_facts: list[dict], anonymized_text: str) -> str:
    """Restore non-identifying medication names that CSG over-redacted."""

    out = anonymized_text
    medication_facts = [
        str(fact.get("fact", ""))
        for fact in task_facts
        if any(token in str(fact.get("type", "")).lower() for token in ["medication", "treatment"])
    ]
    for fact in medication_facts:
        name = medication_name_from_fact(fact)
        if not name:
            continue
        out = re.sub(r"\[(?:MEDICATION|TREATMENT|DRUG)\]", name, out, count=1, flags=re.IGNORECASE)
    return re.sub(r"\s+", " ", out).strip()


def age_band(age: int) -> str:
    decade = (age // 10) * 10
    if age < 30:
        return "adult under 30"
    if age >= 80:
        return "adult over 80"
    prefix = "early" if age % 10 <= 3 else "mid" if age % 10 <= 6 else "late"
    return f"{prefix} {decade}s"


def run_csg_extracted(
    api_key: str,
    model: str,
    example: dict,
    cache: dict[str, dict],
    cache_path: str,
    max_tokens: int,
    cache_only: bool,
) -> tuple[str, int, dict]:
    calls = 0
    extraction_prompt = EXTRACT_PRIVACY_AND_FACTS_PROMPT.format(text=example["text"])
    extraction_text, new_calls = cached_completion(
        api_key,
        model,
        cache,
        cache_path,
        "critical_span_guard_extracted:extract",
        example["id"],
        extraction_prompt,
        max_tokens,
        json_mode=True,
        cache_only=cache_only,
    )
    calls += new_calls
    extraction = parse_json_object(extraction_text)
    privacy_spans = extraction.get("privacy_spans", [])
    task_facts = extraction.get("task_critical_facts", [])

    anonymize_prompt = CSG_EXTRACTED_PROMPT.format(
        text=example["text"],
        privacy_spans=json.dumps(privacy_spans, ensure_ascii=True),
        task_facts=json.dumps(task_facts, ensure_ascii=True),
    )
    draft, new_calls = cached_completion(
        api_key,
        model,
        cache,
        cache_path,
        "critical_span_guard_extracted:anonymize",
        example["id"],
        anonymize_prompt,
        max_tokens,
        cache_only=cache_only,
    )
    calls += new_calls

    verify_prompt = CSG_VERIFY_REPAIR_PROMPT.format(
        original_text=example["text"],
        anonymized_text=draft,
        privacy_spans=json.dumps(privacy_spans, ensure_ascii=True),
        task_facts=json.dumps(task_facts, ensure_ascii=True),
    )
    verify_text, new_calls = cached_completion(
        api_key,
        model,
        cache,
        cache_path,
        "critical_span_guard_extracted:verify_repair",
        example["id"],
        verify_prompt,
        max_tokens,
        json_mode=True,
        cache_only=cache_only,
    )
    calls += new_calls
    verification = parse_json_object(verify_text)
    final_text = safety_scrub_direct_identifiers(str(verification.get("text") or draft))
    final_text = repair_legal_article_placeholders(example["text"], final_text)
    final_text = repair_legal_case_labels(task_facts, final_text)
    final_text = repair_legal_detention_regime_labels(task_facts, final_text)
    final_text = repair_clinical_medication_placeholders(task_facts, final_text)
    metadata = {
        "extracted_privacy_spans": privacy_spans,
        "extracted_task_critical_facts": task_facts,
        "verification": verification,
    }
    return str(final_text).strip(), calls, metadata


def run(args: argparse.Namespace) -> None:
    if args.cache_only and args.model == "auto":
        raise ValueError("--cache-only requires an explicit --model so no model-list request is needed")
    api_key = "" if args.cache_only else load_key(args.api_key_file)
    model = args.model if args.cache_only else choose_model(api_key, args.model)
    examples = read_jsonl(args.benchmark)
    examples = select_examples(examples, args.max_examples, args.seed)
    cache = load_cache(args.cache)
    rows = []
    calls = 0
    for example in examples:
        for method in args.methods:
            metadata = {}
            if method == "critical_span_guard_extracted":
                text, new_calls, metadata = run_csg_extracted(
                    api_key,
                    model,
                    example,
                    cache,
                    args.cache,
                    args.max_tokens,
                    args.cache_only,
                )
                calls += new_calls
            else:
                prompt = prompt_for(method, example)
                text, new_calls = cached_completion(
                    api_key,
                    model,
                    cache,
                    args.cache,
                    method,
                    example["id"],
                    prompt,
                    args.max_tokens,
                    cache_only=args.cache_only,
                )
                calls += new_calls
            row = {
                "id": example["id"],
                "domain": example["domain"],
                "source": example["source"],
                "method": method,
                "model": model,
                "text": example["text"],
                "anonymized_text": text,
            }
            row.update(metadata)
            rows.append(row)
    write_jsonl(args.out, rows)
    print(f"model={model}")
    print(f"examples={len(examples)} methods={len(args.methods)} new_api_calls={calls}")
    print(f"wrote {len(rows)} rows to {args.out}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/benchmark.jsonl")
    parser.add_argument("--out", default="data/processed/openai_anonymized_outputs.jsonl")
    parser.add_argument("--cache", default="data/processed/openai_cache.jsonl")
    parser.add_argument("--api-key-file", default="/home/eston/colm_workshop/apikey.txt")
    parser.add_argument("--model", default="auto")
    parser.add_argument("--max-examples", type=int, default=8)
    parser.add_argument("--seed", type=int, default=21)
    parser.add_argument("--max-tokens", type=int, default=700)
    parser.add_argument("--cache-only", action="store_true", help="rebuild from cache and fail instead of making API calls")
    parser.add_argument(
        "--methods",
        nargs="+",
        default=["generic_llm", "privacy_first_llm", "critical_span_guard_extracted"],
    )
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
