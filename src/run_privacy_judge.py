"""LLM adversarial privacy audit for anonymized outputs."""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict

from io_utils import read_jsonl, write_json, write_jsonl
from run_openai_methods import (
    cached_completion,
    choose_model,
    load_cache,
    load_key,
    parse_json_object,
)


PRIVACY_AUDIT_PROMPT = """You are a privacy auditor for anonymized clinical or legal text.

Anonymized text:
{anonymized_text}

Task: identify residual privacy risks visible in the anonymized text. Look for:
1. direct identifiers, including names, exact dates, application/case numbers, record numbers, contact details, and named institutions tied to a person;
2. quasi-identifiers, including rare occupation, specific location, age, nationality, family relation, rare event, exact statute/jurisdiction detail, sensitive attribute, or unusual combination of details;
3. facts that might be both task-critical and privacy-relevant.

Return only valid JSON:
{{
  "findings": [
    {{
      "type": "direct_identifier|quasi_identifier|sensitive_attribute|linkage_combination|none",
      "severity": 0,
      "span": "exact text span or empty string",
      "reason": "brief explanation",
      "task_critical_overlap": true
    }}
  ],
  "overall_severity": 0,
  "summary": "brief summary"
}}

Severity scale:
- 0: no visible privacy risk.
- 1: low-risk generic or common detail.
- 2: meaningful quasi-identifier or linkage clue.
- 3: direct identifier or highly distinctive linkage combination.

Do not infer beyond the text. If there are no visible privacy risks, return an empty findings list and severity 0.
"""


def load_ids(path: str | None) -> set[str] | None:
    if not path:
        return None
    keep: set[str] = set()
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            value = line.strip()
            if value:
                keep.add(value)
    return keep


def deterministic_map(path: str | None) -> dict[tuple[str, str], dict]:
    if not path:
        return {}
    return {(row["id"], row["method"]): row for row in read_jsonl(path)}


def clamp_severity(value: object) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, min(3, number))


def normalize_finding(finding: dict) -> dict:
    risk_type = str(finding.get("type", "none")).strip().lower()
    allowed = {"direct_identifier", "quasi_identifier", "sensitive_attribute", "linkage_combination", "none"}
    if risk_type not in allowed:
        risk_type = "quasi_identifier"
    return {
        "type": risk_type,
        "severity": clamp_severity(finding.get("severity", 0)),
        "span": str(finding.get("span", "")).strip(),
        "reason": str(finding.get("reason", "")).strip(),
        "task_critical_overlap": bool(finding.get("task_critical_overlap", False)),
    }


def judge_row(
    api_key: str,
    model: str,
    cache: dict[str, dict],
    cache_path: str,
    output: dict,
    deterministic: dict[tuple[str, str], dict],
    max_tokens: int,
    cache_only: bool,
) -> tuple[dict, int]:
    prompt = PRIVACY_AUDIT_PROMPT.format(anonymized_text=output["anonymized_text"])
    text, calls = cached_completion(
        api_key,
        model,
        cache,
        cache_path,
        "adversarial_privacy_judge",
        f"{output['id']}:{output['method']}",
        prompt,
        max_tokens,
        json_mode=True,
        cache_only=cache_only,
    )
    parsed = parse_json_object(text)
    findings = [
        normalize_finding(finding)
        for finding in parsed.get("findings", [])
        if isinstance(finding, dict)
    ]
    max_severity = max([clamp_severity(parsed.get("overall_severity", 0))] + [row["severity"] for row in findings])
    direct_flag = any(row["type"] == "direct_identifier" and row["severity"] >= 2 for row in findings)
    qi_flag = any(
        row["type"] in {"quasi_identifier", "sensitive_attribute", "linkage_combination"} and row["severity"] >= 2
        for row in findings
    )
    det = deterministic.get((output["id"], output["method"]), {})
    deterministic_direct = int(det.get("direct_identifier_leak", 0) or 0)
    deterministic_qi = int(det.get("quasi_identifier_risk", 0) or 0)
    row = {
        "id": output["id"],
        "domain": output["domain"],
        "method": output["method"],
        "model": model,
        "privacy_findings": findings,
        "max_severity": max_severity,
        "has_severe_flag": max_severity >= 2,
        "llm_direct_flag": direct_flag,
        "llm_qi_flag": qi_flag,
        "deterministic_direct_identifier_leak": deterministic_direct,
        "deterministic_qi_risk": deterministic_qi,
        "new_severe_beyond_deterministic": max_severity >= 2 and not deterministic_direct and deterministic_qi < 2,
        "summary": str(parsed.get("summary", "")).strip(),
    }
    return row, calls


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else math.nan


def summarize(rows: list[dict]) -> dict:
    summary = {"overall": {}, "by_domain": {}}
    by_method: dict[str, list[dict]] = defaultdict(list)
    by_domain_method: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        by_method[row["method"]].append(row)
        by_domain_method[(row["domain"], row["method"])].append(row)
    for method, method_rows in sorted(by_method.items()):
        summary["overall"][method] = summarize_rows(method_rows)
    for (domain, method), method_rows in sorted(by_domain_method.items()):
        summary["by_domain"].setdefault(domain, {})[method] = summarize_rows(method_rows)
    return summary


def rate(rows: list[dict], key: str) -> float:
    return mean([1.0 if row.get(key) else 0.0 for row in rows])


def summarize_rows(rows: list[dict]) -> dict:
    return {
        "n": len(rows),
        "mean_max_severity": mean([float(row["max_severity"]) for row in rows]),
        "severe_flag_rate": rate(rows, "has_severe_flag"),
        "direct_flag_rate": rate(rows, "llm_direct_flag"),
        "qi_flag_rate": rate(rows, "llm_qi_flag"),
        "new_severe_beyond_deterministic_rate": rate(rows, "new_severe_beyond_deterministic"),
    }


def fmt(value: float) -> str:
    if math.isnan(value):
        return "NA"
    return f"{value:.3f}"


def markdown_report(summary: dict) -> str:
    lines = ["# LLM Adversarial Privacy Audit", ""]
    lines.append("The auditor sees only anonymized text. It does not receive gold privacy spans or the original text.")
    lines.append("")
    lines.append("| Method | N | Mean severity | Severe >=2 | Direct flag | QI/linkage flag | New severe beyond deterministic |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for method, stats in sorted(summary["overall"].items()):
        lines.append(
            "| {method} | {n} | {sev} | {severe} | {direct} | {qi} | {new} |".format(
                method=method,
                n=stats["n"],
                sev=fmt(stats["mean_max_severity"]),
                severe=fmt(stats["severe_flag_rate"]),
                direct=fmt(stats["direct_flag_rate"]),
                qi=fmt(stats["qi_flag_rate"]),
                new=fmt(stats["new_severe_beyond_deterministic_rate"]),
            )
        )
    lines.append("")
    for domain, methods in sorted(summary["by_domain"].items()):
        lines.append(f"## {domain.capitalize()}")
        lines.append("")
        lines.append("| Method | N | Mean severity | Severe >=2 | Direct flag | QI/linkage flag |")
        lines.append("|---|---:|---:|---:|---:|---:|")
        for method, stats in sorted(methods.items()):
            lines.append(
                "| {method} | {n} | {sev} | {severe} | {direct} | {qi} |".format(
                    method=method,
                    n=stats["n"],
                    sev=fmt(stats["mean_max_severity"]),
                    severe=fmt(stats["severe_flag_rate"]),
                    direct=fmt(stats["direct_flag_rate"]),
                    qi=fmt(stats["qi_flag_rate"]),
                )
            )
        lines.append("")
    return "\n".join(lines)


def run(args: argparse.Namespace) -> None:
    if args.cache_only and args.model == "auto":
        raise ValueError("--cache-only requires an explicit --model so no model-list request is needed")
    api_key = "" if args.cache_only else load_key(args.api_key_file)
    model = args.model if args.cache_only else choose_model(api_key, args.model)
    outputs = read_jsonl(args.outputs)
    keep_ids = load_ids(args.ids_file)
    if keep_ids is not None:
        outputs = [row for row in outputs if row["id"] in keep_ids]
    if args.methods:
        methods = set(args.methods)
        outputs = [row for row in outputs if row["method"] in methods]
    deterministic = deterministic_map(args.deterministic_judgments)
    cache = load_cache(args.cache)
    rows = []
    calls = 0
    for output in outputs:
        row, new_calls = judge_row(
            api_key,
            model,
            cache,
            args.cache,
            output,
            deterministic,
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
    parser.add_argument("--outputs", default="data/processed/openai_anonymized_outputs_n150.jsonl")
    parser.add_argument("--deterministic-judgments", default="data/processed/openai_judgments_n150.jsonl")
    parser.add_argument("--out", default="data/processed/gpt55_privacy_judgments_stratified60.jsonl")
    parser.add_argument("--summary", default="results/gpt55_privacy_judge_summary_stratified60.json")
    parser.add_argument("--report", default="results/gpt55_privacy_judge_results_stratified60.md")
    parser.add_argument("--cache", default="data/processed/openai_cache.jsonl")
    parser.add_argument("--api-key-file", default="/home/eston/colm_workshop/apikey.txt")
    parser.add_argument("--model", default="auto")
    parser.add_argument("--max-tokens", type=int, default=700)
    parser.add_argument("--methods", nargs="*", default=None)
    parser.add_argument("--ids-file", default=None, help="optional newline-delimited example ids to audit")
    parser.add_argument("--cache-only", action="store_true", help="rebuild from cache and fail instead of making API calls")
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
