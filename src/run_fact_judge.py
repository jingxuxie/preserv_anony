"""LLM-assisted fact-retention audit for anonymized outputs.

This supplements the exact-string TCFR metric with a paraphrase-aware judge.
It uses gold facts only for evaluation, not for anonymization.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from collections import defaultdict

from io_utils import read_jsonl, write_json, write_jsonl
from run_openai_methods import (
    cached_completion,
    choose_model,
    load_cache,
    load_key,
    parse_json_object,
)


JUDGE_PROMPT = """You are auditing whether anonymized text preserves task-critical facts.

Original text:
{original_text}

Anonymized text:
{anonymized_text}

Gold task-critical facts:
{facts_json}

For each fact, decide whether the anonymized text preserves the fact at the intended specificity.

Status definitions:
- preserved: the anonymized text entails the fact, including faithful paraphrases.
- generalized_but_acceptable: the fact is generalized, but the gold item allows generalization and the downstream answer would remain correct.
- omitted: the anonymized text does not contain enough information to recover the fact.
- contradicted: the anonymized text states an incompatible fact.
- unclear: cannot decide.

Be strict about numeric values, medication names, doses, lab values, imaging findings, legal Article numbers, outcomes, and legal claims. Do not require exact wording when a faithful paraphrase preserves the same meaning.

Important specificity rules:
- "antibiotic therapy" does not preserve "ceftriaxone and metronidazole".
- "a medication" or "disease-modifying medication" does not preserve a named drug and dose.
- "low pH" does not preserve "pH 7.21".
- "high blood glucose" does not preserve "blood glucose 482 mg/dL".
- "a procedural article" does not preserve "Article 6".
- "violation" and "no violation" are contradictory.

Return only valid JSON with this schema:
{{
  "fact_judgments": [
    {{"fact_index": 0, "fact": "...", "status": "preserved|generalized_but_acceptable|omitted|contradicted|unclear", "evidence": "..."}}
  ],
  "summary": {{"preserved": 0, "generalized_but_acceptable": 0, "omitted": 0, "contradicted": 0, "unclear": 0}}
}}
"""


def retained_by_judge(judgment: dict, fact: dict) -> bool:
    status = judgment.get("status")
    if status == "preserved":
        return True
    if status == "generalized_but_acceptable":
        return bool(fact.get("generalization_allowed"))
    return False


def contradicted_by_judge(judgment: dict) -> bool:
    return judgment.get("status") == "contradicted"


def normalize_for_match(text: object) -> str:
    value = "".join(ch if ch in "\t\n" or ord(ch) >= 32 else " " for ch in str(text).lower())
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def norm_contains(haystack: str, needle: str) -> bool:
    if not needle:
        return False
    return re.search(rf"(^| ){re.escape(needle)}($| )", haystack) is not None


def exact_fact_present_without_obvious_contradiction(norm_fact: str, norm_anon: str) -> bool:
    if not norm_contains(norm_anon, norm_fact):
        return False
    if norm_fact == "violation" and norm_contains(norm_anon, "no violation"):
        return False
    return True


def normalize_judgment(judgment: dict, fact: dict | None = None, anonymized_text: str = "") -> dict:
    """Repair obvious status/evidence inconsistencies from the judge."""

    status = judgment.get("status")
    evidence = str(judgment.get("evidence", "")).lower()
    fact_text = str((fact or {}).get("fact", ""))
    norm_fact = normalize_for_match(fact_text)
    norm_anon = normalize_for_match(anonymized_text)
    if status in {None, "unclear"}:
        if exact_fact_present_without_obvious_contradiction(norm_fact, norm_anon):
            judgment["status"] = "preserved"
        elif fact and fact.get("generalization_allowed"):
            for alias in fact.get("acceptable_generalizations", []):
                norm_alias = normalize_for_match(alias)
                if norm_alias and norm_contains(norm_anon, norm_alias):
                    judgment["status"] = "generalized_but_acceptable"
                    break
    if status == "contradicted":
        if "not contradicted" in evidence or "not a contradiction" in evidence:
            judgment["status"] = "preserved"
        elif any(
            phrase in evidence
            for phrase in [
                "does not specify",
                "does not preserve",
                "do not specify",
                "omits",
                "omitted",
                "without specifying",
                "instead of",
            ]
        ) and not any(
            phrase in evidence
            for phrase in ["opposite", "incompatible", "different article number", "no violation", "violation instead"]
        ):
            judgment["status"] = "omitted"
    elif status == "omitted":
        positive = any(
            phrase in evidence
            for phrase in [
                "is preserved",
                "fact is preserved",
                "faithfully preserves",
                "directly preserves",
                "faithfully paraphrases",
                "matches the original",
                "matches the original fact exactly",
            ]
        )
        negative = any(
            phrase in evidence
            for phrase in [
                "does not preserve",
                "does not specify",
                "not specify",
                "omitted",
                "omits",
                "not preserved",
            ]
        )
        if positive and not negative:
            judgment["status"] = "preserved"
    elif status == "generalized_but_acceptable":
        if exact_fact_present_without_obvious_contradiction(norm_fact, norm_anon):
            judgment["status"] = "preserved"
    if judgment.get("status") in {"omitted", "contradicted"} and exact_fact_present_without_obvious_contradiction(
        norm_fact, norm_anon
    ):
        judgment["status"] = "preserved"
    return judgment


def judge_row(
    api_key: str,
    model: str,
    cache: dict[str, dict],
    cache_path: str,
    example: dict,
    output: dict,
    max_tokens: int,
    cache_only: bool,
) -> tuple[dict, int]:
    facts = example.get("task_critical_facts", [])
    indexed_facts = []
    for index, fact in enumerate(facts):
        item = dict(fact)
        item["fact_index"] = index
        indexed_facts.append(item)
    prompt = JUDGE_PROMPT.format(
        original_text=example["text"],
        anonymized_text=output["anonymized_text"],
        facts_json=json.dumps(indexed_facts, ensure_ascii=True),
    )
    text, calls = cached_completion(
        api_key,
        model,
        cache,
        cache_path,
        "fact_retention_judge",
        f"{output['id']}:{output['method']}",
        prompt,
        max_tokens,
        json_mode=True,
        cache_only=cache_only,
    )
    parsed = parse_json_object(text)
    raw_judgments = parsed.get("fact_judgments", [])
    judgments = [judgment for judgment in raw_judgments if isinstance(judgment, dict)]
    by_index = {}
    for judgment in judgments:
        try:
            by_index[int(judgment.get("fact_index"))] = judgment
        except (TypeError, ValueError):
            continue

    retained = 0
    contradicted = 0
    judged = []
    for index, fact in enumerate(facts):
        fact_text = str(fact.get("fact", ""))
        judgment = by_index.get(index)
        if judgment is None and len(judgments) == len(facts):
            candidate = judgments[index]
            if isinstance(candidate, dict) and candidate.get("fact_index") is None:
                judgment = candidate
        judgment = judgment or {"fact": fact_text, "status": "unclear", "evidence": "missing judgment"}
        judgment["fact_index"] = index
        judgment["gold_fact"] = fact_text
        judgment = normalize_judgment(judgment, fact, output["anonymized_text"])
        if retained_by_judge(judgment, fact):
            retained += 1
        if contradicted_by_judge(judgment):
            contradicted += 1
        judged.append(judgment)

    total = len(facts)
    row = {
        "id": output["id"],
        "domain": output["domain"],
        "method": output["method"],
        "model": model,
        "audited_tcfr": retained / total if total else math.nan,
        "audited_ccr": contradicted / total if total else 0.0,
        "fact_judgments": judged,
    }
    return row, calls


def mean(rows: list[dict], key: str) -> float:
    vals = [r[key] for r in rows if not math.isnan(r[key])]
    return sum(vals) / len(vals) if vals else math.nan


def summarize(rows: list[dict]) -> dict:
    summary = {"overall": {}, "by_domain": {}}
    by_method: dict[str, list[dict]] = defaultdict(list)
    by_domain_method: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        by_method[row["method"]].append(row)
        by_domain_method[(row["domain"], row["method"])].append(row)
    for method, method_rows in sorted(by_method.items()):
        summary["overall"][method] = {
            "n": len(method_rows),
            "audited_tcfr": mean(method_rows, "audited_tcfr"),
            "audited_ccr": mean(method_rows, "audited_ccr"),
        }
    for (domain, method), method_rows in sorted(by_domain_method.items()):
        summary["by_domain"].setdefault(domain, {})[method] = {
            "n": len(method_rows),
            "audited_tcfr": mean(method_rows, "audited_tcfr"),
            "audited_ccr": mean(method_rows, "audited_ccr"),
        }
    return summary


def markdown_report(summary: dict) -> str:
    lines = ["# LLM-Audited Fact Retention", ""]
    lines.append("Means over example-method rows. Uses gold facts for evaluation only.")
    lines.append("")
    lines.append("| Method | N | Audited TCFR ↑ | Audited CCR ↓ |")
    lines.append("|---|---:|---:|---:|")
    for method, stats in sorted(summary["overall"].items()):
        lines.append(
            f"| {method} | {stats['n']} | {stats['audited_tcfr']:.3f} | {stats['audited_ccr']:.3f} |"
        )
    lines.append("")
    for domain, methods in sorted(summary["by_domain"].items()):
        lines.append(f"## {domain.capitalize()}")
        lines.append("")
        lines.append("| Method | N | Audited TCFR ↑ | Audited CCR ↓ |")
        lines.append("|---|---:|---:|---:|")
        for method, stats in sorted(methods.items()):
            lines.append(
                f"| {method} | {stats['n']} | {stats['audited_tcfr']:.3f} | {stats['audited_ccr']:.3f} |"
            )
        lines.append("")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> None:
    if args.cache_only and args.model == "auto":
        raise ValueError("--cache-only requires an explicit --model so no model-list request is needed")
    api_key = "" if args.cache_only else load_key(args.api_key_file)
    model = args.model if args.cache_only else choose_model(api_key, args.model)
    examples = {row["id"]: row for row in read_jsonl(args.benchmark)}
    outputs = read_jsonl(args.outputs)
    if args.methods:
        methods = set(args.methods)
        outputs = [row for row in outputs if row["method"] in methods]
    cache = load_cache(args.cache)
    rows = []
    calls = 0
    for output in outputs:
        row, new_calls = judge_row(
            api_key,
            model,
            cache,
            args.cache,
            examples[output["id"]],
            output,
            args.max_tokens,
            args.cache_only,
        )
        rows.append(row)
        calls += new_calls
    summary = summarize(rows)
    write_jsonl(args.out, rows)
    write_json(args.summary, summary)
    with open(args.report, "w", encoding="utf-8") as f:
        f.write(markdown_report(summary))
        f.write("\n")
    print(f"model={model}")
    print(f"rows={len(rows)} new_api_calls={calls}")
    print(f"wrote {args.out}")
    print(f"wrote {args.report}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/benchmark.jsonl")
    parser.add_argument("--outputs", default="data/processed/openai_anonymized_outputs.jsonl")
    parser.add_argument("--out", default="data/processed/openai_fact_judgments.jsonl")
    parser.add_argument("--summary", default="results/openai_fact_judge_summary.json")
    parser.add_argument("--report", default="results/openai_fact_judge_results.md")
    parser.add_argument("--cache", default="data/processed/openai_cache.jsonl")
    parser.add_argument("--api-key-file", default="/home/eston/colm_workshop/apikey.txt")
    parser.add_argument("--model", default="auto")
    parser.add_argument("--max-tokens", type=int, default=1200)
    parser.add_argument("--methods", nargs="*", default=None)
    parser.add_argument("--cache-only", action="store_true", help="rebuild from cache and fail instead of making API calls")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
