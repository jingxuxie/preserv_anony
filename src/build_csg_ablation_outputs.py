"""Build CSG ablation outputs from cached OpenAI stages.

Stages:
- csg_draft: extracted spans/facts + anonymization prompt only.
- csg_verified: verifier/repair output, without deterministic safety scrub.
- csg_verified_safety: verifier/repair output plus deterministic safety scrub.

This script should not make network calls. It reconstructs current prompt hashes
and reads the matching cached responses from data/processed/openai_cache.jsonl.
"""

from __future__ import annotations

import argparse
import json

from io_utils import read_jsonl, write_jsonl
from run_openai_methods import (
    CSG_EXTRACTED_PROMPT,
    CSG_VERIFY_REPAIR_PROMPT,
    EXTRACT_PRIVACY_AND_FACTS_PROMPT,
    cache_key,
    parse_json_object,
    repair_clinical_medication_placeholders,
    repair_legal_detention_regime_labels,
    repair_legal_case_labels,
    repair_legal_article_placeholders,
    safety_scrub_direct_identifiers,
    select_examples,
)


def load_cache(path: str) -> dict[str, dict]:
    cache = {}
    for row in read_jsonl(path):
        if "text" not in row and "anonymized_text" in row:
            row["text"] = row["anonymized_text"]
        cache[row["cache_key"]] = row
    return cache


def cache_text(cache: dict[str, dict], model: str, method: str, example_id: str, prompt: str) -> str:
    key = cache_key(model, method, example_id, prompt)
    if key not in cache:
        raise KeyError(f"missing cache key for {example_id} {method}: {key}")
    return str(cache[key]["text"])


def build_rows(args: argparse.Namespace) -> list[dict]:
    examples = select_examples(read_jsonl(args.benchmark), args.max_examples, args.seed)
    cache = load_cache(args.cache)
    rows = []
    for example in examples:
        extraction_prompt = EXTRACT_PRIVACY_AND_FACTS_PROMPT.format(text=example["text"])
        extraction_text = cache_text(
            cache,
            args.model,
            "critical_span_guard_extracted:extract",
            example["id"],
            extraction_prompt,
        )
        extraction = parse_json_object(extraction_text)
        privacy_spans = extraction.get("privacy_spans", [])
        task_facts = extraction.get("task_critical_facts", [])

        anonymize_prompt = CSG_EXTRACTED_PROMPT.format(
            text=example["text"],
            privacy_spans=json.dumps(privacy_spans, ensure_ascii=True),
            task_facts=json.dumps(task_facts, ensure_ascii=True),
        )
        draft = cache_text(
            cache,
            args.model,
            "critical_span_guard_extracted:anonymize",
            example["id"],
            anonymize_prompt,
        )

        verify_prompt = CSG_VERIFY_REPAIR_PROMPT.format(
            original_text=example["text"],
            anonymized_text=draft,
            privacy_spans=json.dumps(privacy_spans, ensure_ascii=True),
            task_facts=json.dumps(task_facts, ensure_ascii=True),
        )
        verify_text = cache_text(
            cache,
            args.model,
            "critical_span_guard_extracted:verify_repair",
            example["id"],
            verify_prompt,
        )
        verification = parse_json_object(verify_text)
        verified = str(verification.get("text") or draft).strip()
        final = safety_scrub_direct_identifiers(verified)
        final = repair_legal_article_placeholders(example["text"], final)
        final = repair_legal_case_labels(task_facts, final)
        final = repair_legal_detention_regime_labels(task_facts, final)
        final = repair_clinical_medication_placeholders(task_facts, final)

        base = {
            "id": example["id"],
            "domain": example["domain"],
            "source": example["source"],
            "model": args.model,
            "text": example["text"],
            "extracted_privacy_spans": privacy_spans,
            "extracted_task_critical_facts": task_facts,
            "verification": verification,
        }
        rows.append({**base, "method": "csg_draft", "anonymized_text": draft.strip()})
        rows.append({**base, "method": "csg_verified", "anonymized_text": verified})
        rows.append({**base, "method": "csg_verified_safety", "anonymized_text": final})
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/benchmark.jsonl")
    parser.add_argument("--cache", default="data/processed/openai_cache.jsonl")
    parser.add_argument("--out", default="data/processed/csg_ablation_outputs.jsonl")
    parser.add_argument("--model", default="gpt-4.1-nano")
    parser.add_argument("--max-examples", type=int, default=50)
    parser.add_argument("--seed", type=int, default=21)
    args = parser.parse_args()
    rows = build_rows(args)
    write_jsonl(args.out, rows)
    print(f"wrote {len(rows)} rows to {args.out}")


if __name__ == "__main__":
    main()
