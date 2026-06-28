"""Estimate cache misses and token exposure for bounded OpenAI expansions."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from io_utils import read_jsonl
from run_fact_judge import JUDGE_PROMPT
from run_openai_methods import (
    CSG_EXTRACTED_PROMPT,
    CSG_VERIFY_REPAIR_PROMPT,
    EXTRACT_PRIVACY_AND_FACTS_PROMPT,
    cache_key,
    load_cache,
    parse_json_object,
    prompt_for,
)


METHODS = ["generic_llm", "privacy_first_llm", "critical_span_guard_extracted"]


def proxy_tokens(text: str) -> int:
    return max(1, round(len(text) / 4))


def cache_text(cache: dict[str, dict], model: str, method: str, example_id: str, prompt: str) -> str | None:
    row = cache.get(cache_key(model, method, example_id, prompt))
    if not row:
        return None
    return str(row.get("text", ""))


def fact_prompt(example: dict, output: dict) -> str:
    facts = []
    for index, fact in enumerate(example.get("task_critical_facts", [])):
        item = dict(fact)
        item["fact_index"] = index
        facts.append(item)
    return JUDGE_PROMPT.format(
        original_text=example["text"],
        anonymized_text=output["anonymized_text"],
        facts_json=json.dumps(facts, ensure_ascii=True),
    )


def estimate(args: argparse.Namespace) -> None:
    examples = read_jsonl(args.benchmark)
    examples_by_id = {row["id"]: row for row in examples}
    if len(examples) != args.target_examples:
        raise ValueError(f"{args.benchmark} has {len(examples)} rows, expected {args.target_examples}")
    cache = load_cache(args.cache)
    cached_outputs = read_jsonl(args.outputs) if args.outputs and Path(args.outputs).exists() else []
    outputs_by_key = {(row["id"], row["method"]): row for row in cached_outputs}

    missing = Counter()
    cached = Counter()
    prompt_proxy = Counter()
    known_response_proxy = Counter()
    unknown_response_slots = Counter()
    cache_rows_with_usage = 0
    usage_prompt_tokens = 0
    usage_completion_tokens = 0
    elapsed_rows = 0
    elapsed_ms_total = 0.0

    for row in cache.values():
        usage = row.get("usage") or {}
        if usage:
            cache_rows_with_usage += 1
            usage_prompt_tokens += int(usage.get("prompt_tokens") or 0)
            usage_completion_tokens += int(usage.get("completion_tokens") or 0)
        if row.get("elapsed_ms") is not None:
            elapsed_rows += 1
            elapsed_ms_total += float(row.get("elapsed_ms") or 0.0)

    for example in examples:
        for method in METHODS:
            if method != "critical_span_guard_extracted":
                prompt = prompt_for(method, example)
                stage = "anonymize"
                prompt_proxy[stage] += proxy_tokens(prompt)
                text = cache_text(cache, args.model, method, example["id"], prompt)
                if text is None:
                    missing[stage] += 1
                    unknown_response_slots[stage] += 1
                else:
                    cached[stage] += 1
                    known_response_proxy[stage] += proxy_tokens(text)
                continue

            extract_prompt = EXTRACT_PRIVACY_AND_FACTS_PROMPT.format(text=example["text"])
            prompt_proxy["csg_extract"] += proxy_tokens(extract_prompt)
            extraction_text = cache_text(
                cache,
                args.model,
                "critical_span_guard_extracted:extract",
                example["id"],
                extract_prompt,
            )
            if extraction_text is None:
                missing["csg_extract"] += 1
                unknown_response_slots["csg_extract"] += 1
                missing["csg_anonymize"] += 1
                unknown_response_slots["csg_anonymize"] += 1
                missing["csg_verify_repair"] += 1
                unknown_response_slots["csg_verify_repair"] += 1
                continue
            cached["csg_extract"] += 1
            known_response_proxy["csg_extract"] += proxy_tokens(extraction_text)
            extraction = parse_json_object(extraction_text)
            privacy_spans = extraction.get("privacy_spans", [])
            task_facts = extraction.get("task_critical_facts", [])

            anonymize_prompt = CSG_EXTRACTED_PROMPT.format(
                text=example["text"],
                privacy_spans=json.dumps(privacy_spans, ensure_ascii=True),
                task_facts=json.dumps(task_facts, ensure_ascii=True),
            )
            prompt_proxy["csg_anonymize"] += proxy_tokens(anonymize_prompt)
            draft = cache_text(
                cache,
                args.model,
                "critical_span_guard_extracted:anonymize",
                example["id"],
                anonymize_prompt,
            )
            if draft is None:
                missing["csg_anonymize"] += 1
                unknown_response_slots["csg_anonymize"] += 1
                missing["csg_verify_repair"] += 1
                unknown_response_slots["csg_verify_repair"] += 1
                continue
            cached["csg_anonymize"] += 1
            known_response_proxy["csg_anonymize"] += proxy_tokens(draft)

            verify_prompt = CSG_VERIFY_REPAIR_PROMPT.format(
                original_text=example["text"],
                anonymized_text=draft,
                privacy_spans=json.dumps(privacy_spans, ensure_ascii=True),
                task_facts=json.dumps(task_facts, ensure_ascii=True),
            )
            prompt_proxy["csg_verify_repair"] += proxy_tokens(verify_prompt)
            verify = cache_text(
                cache,
                args.model,
                "critical_span_guard_extracted:verify_repair",
                example["id"],
                verify_prompt,
            )
            if verify is None:
                missing["csg_verify_repair"] += 1
                unknown_response_slots["csg_verify_repair"] += 1
            else:
                cached["csg_verify_repair"] += 1
                known_response_proxy["csg_verify_repair"] += proxy_tokens(verify)

    for example in examples:
        for method in METHODS:
            output = outputs_by_key.get((example["id"], method))
            stage = "fact_judge"
            if output is None:
                missing[stage] += 1
                unknown_response_slots[stage] += 1
                continue
            prompt = fact_prompt(example, output)
            prompt_proxy[stage] += proxy_tokens(prompt)
            text = cache_text(cache, args.model, "fact_retention_judge", f"{example['id']}:{method}", prompt)
            if text is None:
                missing[stage] += 1
                unknown_response_slots[stage] += 1
            else:
                cached[stage] += 1
                known_response_proxy[stage] += proxy_tokens(text)

    stages = ["anonymize", "csg_extract", "csg_anonymize", "csg_verify_repair", "fact_judge"]
    total_missing = sum(missing.values())
    total_cached = sum(cached.values())
    total_prompt_proxy = sum(prompt_proxy.values())
    total_known_response_proxy = sum(known_response_proxy.values())
    payload = {
        "benchmark": args.benchmark,
        "target_examples": args.target_examples,
        "model": args.model,
        "cached_response_slots": dict(cached),
        "missing_response_slots": dict(missing),
        "total_cached_response_slots": total_cached,
        "total_missing_response_slots": total_missing,
        "prompt_token_proxy_for_known_prompts": total_prompt_proxy,
        "known_response_token_proxy": total_known_response_proxy,
        "unknown_response_slots": dict(unknown_response_slots),
        "cache_rows_with_provider_usage": cache_rows_with_usage,
        "stored_prompt_tokens": usage_prompt_tokens,
        "stored_completion_tokens": usage_completion_tokens,
        "cache_rows_with_elapsed_ms": elapsed_rows,
        "stored_elapsed_ms_total": elapsed_ms_total,
    }

    print(f"benchmark={args.benchmark} target_examples={args.target_examples} model={args.model}")
    print(f"cached_response_slots={total_cached} missing_response_slots={total_missing}")
    for stage in stages:
        print(
            f"{stage}: cached={cached[stage]} missing={missing[stage]} "
            f"prompt_proxy={prompt_proxy[stage]} known_response_proxy={known_response_proxy[stage]}"
        )
    print(f"cache_usage_rows={cache_rows_with_usage} elapsed_rows={elapsed_rows}")
    if args.out_json:
        out = Path(args.out_json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"wrote {out}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", required=True)
    parser.add_argument("--target-examples", type=int, required=True)
    parser.add_argument("--outputs", default="")
    parser.add_argument("--cache", default="data/processed/openai_cache.jsonl")
    parser.add_argument("--model", default="gpt-4.1-nano")
    parser.add_argument("--out-json", default="")
    estimate(parser.parse_args())


if __name__ == "__main__":
    main()
