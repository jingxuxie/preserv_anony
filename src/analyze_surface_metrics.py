"""Audit whether surface similarity metrics capture privacy and utility failures."""

from __future__ import annotations

import argparse
import difflib
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

from io_utils import read_jsonl, write_json


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def word_tokens(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+(?:[-'][a-zA-Z0-9]+)?", text.lower())


def char_similarity(original: str, anonymized: str) -> float:
    return difflib.SequenceMatcher(a=normalize(original), b=normalize(anonymized)).ratio()


def multiset_token_f1(original: str, anonymized: str) -> float:
    orig = Counter(word_tokens(original))
    anon = Counter(word_tokens(anonymized))
    if not orig and not anon:
        return 1.0
    if not orig or not anon:
        return 0.0
    overlap = sum((orig & anon).values())
    precision = overlap / sum(anon.values()) if anon else 0.0
    recall = overlap / sum(orig.values()) if orig else 0.0
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def token_jaccard(original: str, anonymized: str) -> float:
    orig = set(word_tokens(original))
    anon = set(word_tokens(anonymized))
    if not orig and not anon:
        return 1.0
    if not orig or not anon:
        return 0.0
    return len(orig & anon) / len(orig | anon)


def build_idf(texts: list[str]) -> dict[str, float]:
    doc_count = len(texts)
    df = Counter()
    for text in texts:
        df.update(set(word_tokens(text)))
    return {token: math.log((1 + doc_count) / (1 + count)) + 1.0 for token, count in df.items()}


def tfidf_cosine(original: str, anonymized: str, idf: dict[str, float]) -> float:
    orig_tf = Counter(word_tokens(original))
    anon_tf = Counter(word_tokens(anonymized))
    if not orig_tf and not anon_tf:
        return 1.0
    if not orig_tf or not anon_tf:
        return 0.0
    vocab = set(orig_tf) | set(anon_tf)
    dot = sum(orig_tf[token] * anon_tf[token] * idf.get(token, 1.0) ** 2 for token in vocab)
    orig_norm = math.sqrt(sum((orig_tf[token] * idf.get(token, 1.0)) ** 2 for token in orig_tf))
    anon_norm = math.sqrt(sum((anon_tf[token] * idf.get(token, 1.0)) ** 2 for token in anon_tf))
    if orig_norm == 0 or anon_norm == 0:
        return 0.0
    return dot / (orig_norm * anon_norm)


def length_ratio(original: str, anonymized: str) -> float:
    orig_len = len(word_tokens(original))
    anon_len = len(word_tokens(anonymized))
    if orig_len == 0:
        return 1.0 if anon_len == 0 else math.inf
    return anon_len / orig_len


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else math.nan


def median(values: list[float]) -> float:
    if not values:
        return math.nan
    sorted_values = sorted(values)
    mid = len(sorted_values) // 2
    if len(sorted_values) % 2:
        return sorted_values[mid]
    return (sorted_values[mid - 1] + sorted_values[mid]) / 2


def pearson(xs: list[float], ys: list[float]) -> float:
    pairs = [(x, y) for x, y in zip(xs, ys) if not math.isnan(x) and not math.isnan(y)]
    if len(pairs) < 2:
        return math.nan
    xs, ys = [p[0] for p in pairs], [p[1] for p in pairs]
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    den_x = math.sqrt(sum((x - mx) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - my) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return math.nan
    return num / (den_x * den_y)


def rank_values(values: list[float]) -> list[float]:
    indexed = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    i = 0
    while i < len(indexed):
        j = i
        while j + 1 < len(indexed) and indexed[j + 1][1] == indexed[i][1]:
            j += 1
        rank = (i + j) / 2 + 1
        for k in range(i, j + 1):
            ranks[indexed[k][0]] = rank
        i = j + 1
    return ranks


def spearman(xs: list[float], ys: list[float]) -> float:
    pairs = [(x, y) for x, y in zip(xs, ys) if not math.isnan(x) and not math.isnan(y)]
    if len(pairs) < 2:
        return math.nan
    ranked_x = rank_values([p[0] for p in pairs])
    ranked_y = rank_values([p[1] for p in pairs])
    return pearson(ranked_x, ranked_y)


def fmt(value: float, digits: int = 3) -> str:
    if math.isnan(value):
        return "NA"
    return f"{value:.{digits}f}"


def load_by_key(path: str) -> dict[tuple[str, str], dict]:
    return {(row["id"], row["method"]): row for row in read_jsonl(path)}


def retained_by_gold_policy(judgment: dict, fact: dict | None) -> bool:
    status = judgment.get("status")
    if status == "preserved":
        return True
    if status == "generalized_but_acceptable":
        return bool((fact or {}).get("generalization_allowed"))
    return False


def sentence_snippet(text: str, limit: int = 190) -> str:
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def build_rows(args: argparse.Namespace) -> list[dict]:
    examples = {row["id"]: row for row in read_jsonl(args.benchmark)}
    outputs = read_jsonl(args.outputs)
    det = load_by_key(args.scored)
    fact = load_by_key(args.fact_judgments)
    idf = build_idf(
        [examples[output["id"]]["text"] for output in outputs]
        + [output["anonymized_text"] for output in outputs]
    )

    rows: list[dict] = []
    for output in outputs:
        key = (output["id"], output["method"])
        example = examples[output["id"]]
        det_row = det[key]
        fact_row = fact.get(key, {})
        gold_facts = example.get("task_critical_facts", [])
        fact_judgments = fact_row.get("fact_judgments", [])
        audited_problem_facts = []
        for judgment in fact_judgments:
            try:
                fact_index = int(judgment.get("fact_index"))
            except (TypeError, ValueError):
                fact_index = -1
            gold_fact = gold_facts[fact_index] if 0 <= fact_index < len(gold_facts) else None
            if not retained_by_gold_policy(judgment, gold_fact):
                audited_problem_facts.append(str(judgment.get("gold_fact") or judgment.get("fact")))
        original = example["text"]
        anonymized = output["anonymized_text"]
        audited_tcfr = float(fact_row.get("audited_tcfr", math.nan))
        audited_ccr = float(fact_row.get("audited_ccr", math.nan))
        qa = float(det_row["qa_consistency"])
        direct = int(det_row["direct_identifier_leak"])
        qi = float(det_row["quasi_identifier_risk"])
        audited_fact_failure = audited_tcfr < 0.999
        qa_failure = qa < 0.999
        utility_failure = audited_fact_failure or qa_failure
        privacy_failure = direct > 0 or qi >= args.high_qi_threshold
        rows.append(
            {
                "id": output["id"],
                "domain": example["domain"],
                "method": output["method"],
                "char_similarity": char_similarity(original, anonymized),
                "token_f1": multiset_token_f1(original, anonymized),
                "token_jaccard": token_jaccard(original, anonymized),
                "tfidf_cosine": tfidf_cosine(original, anonymized, idf),
                "token_edit_rate": float(det_row["edit_rate"]),
                "length_ratio": length_ratio(original, anonymized),
                "direct_identifier_leak": direct,
                "quasi_identifier_risk": qi,
                "audited_tcfr": audited_tcfr,
                "audited_ccr": audited_ccr,
                "qa_consistency": qa,
                "audited_fact_failure": audited_fact_failure,
                "qa_failure": qa_failure,
                "utility_failure": utility_failure,
                "privacy_failure": privacy_failure,
                "any_failure": utility_failure or privacy_failure,
                "failed_qa": det_row.get("failed_qa", []),
                "omitted_facts": det_row.get("omitted_facts", []),
                "audited_problem_facts": audited_problem_facts,
                "direct_leaked_spans": det_row.get("direct_leaked_spans", []),
                "quasi_leaked_spans": det_row.get("quasi_leaked_spans", []),
                "original_snippet": sentence_snippet(original),
                "anonymized_snippet": sentence_snippet(anonymized),
            }
        )
    return rows


def summarize_by_method(rows: list[dict]) -> dict[str, dict]:
    by_method: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_method[row["method"]].append(row)

    summary: dict[str, dict] = {}
    for method, method_rows in sorted(by_method.items()):
        summary[method] = {
            "n": len(method_rows),
            "char_similarity": mean([r["char_similarity"] for r in method_rows]),
            "token_f1": mean([r["token_f1"] for r in method_rows]),
            "token_jaccard": mean([r["token_jaccard"] for r in method_rows]),
            "tfidf_cosine": mean([r["tfidf_cosine"] for r in method_rows]),
            "token_edit_rate": mean([r["token_edit_rate"] for r in method_rows]),
            "length_ratio": mean([r["length_ratio"] for r in method_rows]),
            "audited_tcfr": mean([r["audited_tcfr"] for r in method_rows]),
            "qa_consistency": mean([r["qa_consistency"] for r in method_rows]),
            "direct_identifier_leak": mean([r["direct_identifier_leak"] for r in method_rows]),
            "quasi_identifier_risk": mean([r["quasi_identifier_risk"] for r in method_rows]),
            "audited_fact_failure_rate": mean(
                [1.0 if r["audited_fact_failure"] else 0.0 for r in method_rows]
            ),
            "qa_failure_rate": mean([1.0 if r["qa_failure"] else 0.0 for r in method_rows]),
            "utility_failure_rate": mean([1.0 if r["utility_failure"] else 0.0 for r in method_rows]),
            "privacy_failure_rate": mean([1.0 if r["privacy_failure"] else 0.0 for r in method_rows]),
        }
    return summary


def summarize_high_similarity(rows: list[dict], metric: str) -> dict:
    threshold = median([row[metric] for row in rows])
    high = [row for row in rows if row[metric] >= threshold]
    return {
        "metric": metric,
        "threshold": threshold,
        "n": len(high),
        "audited_fact_failure_rate": mean([1.0 if r["audited_fact_failure"] else 0.0 for r in high]),
        "qa_failure_rate": mean([1.0 if r["qa_failure"] else 0.0 for r in high]),
        "utility_failure_rate": mean([1.0 if r["utility_failure"] else 0.0 for r in high]),
        "privacy_failure_rate": mean([1.0 if r["privacy_failure"] else 0.0 for r in high]),
        "any_failure_rate": mean([1.0 if r["any_failure"] else 0.0 for r in high]),
        "rows_with_audited_fact_failure": sum(1 for r in high if r["audited_fact_failure"]),
        "rows_with_qa_failure": sum(1 for r in high if r["qa_failure"]),
        "rows_with_utility_failure": sum(1 for r in high if r["utility_failure"]),
        "rows_with_privacy_failure": sum(1 for r in high if r["privacy_failure"]),
        "rows_with_any_failure": sum(1 for r in high if r["any_failure"]),
    }


def correlations(rows: list[dict]) -> dict[str, dict[str, float]]:
    surface_metrics = ["char_similarity", "token_f1", "token_jaccard", "tfidf_cosine", "token_edit_rate"]
    targets = ["audited_tcfr", "qa_consistency", "direct_identifier_leak", "quasi_identifier_risk"]
    out: dict[str, dict[str, float]] = {}
    for metric in surface_metrics:
        out[metric] = {}
        xs = [row[metric] for row in rows]
        for target in targets:
            ys = [row[target] for row in rows]
            out[metric][f"pearson_{target}"] = pearson(xs, ys)
            out[metric][f"spearman_{target}"] = spearman(xs, ys)
    return out


def select_examples(rows: list[dict]) -> dict[str, list[dict]]:
    high_audited_fact_misses = [
        row
        for row in rows
        if row["audited_fact_failure"] and row["token_f1"] >= 0.55
    ]
    high_qa_misses = [
        row
        for row in rows
        if row["qa_failure"] and row["token_f1"] >= 0.55
    ]
    high_privacy_misses = [
        row
        for row in rows
        if row["privacy_failure"] and row["token_f1"] >= 0.55
    ]
    return {
        "high_similarity_audited_fact_failures": sorted(
            high_audited_fact_misses,
            key=lambda row: (row["token_f1"], row["char_similarity"]),
            reverse=True,
        )[:8],
        "high_similarity_qa_failures": sorted(
            high_qa_misses,
            key=lambda row: (row["token_f1"], row["char_similarity"]),
            reverse=True,
        )[:8],
        "high_similarity_privacy_failures": sorted(
            high_privacy_misses,
            key=lambda row: (row["token_f1"], row["char_similarity"]),
            reverse=True,
        )[:8],
    }


def compact_example(row: dict) -> dict:
    keys = [
        "id",
        "domain",
        "method",
        "char_similarity",
        "token_f1",
        "tfidf_cosine",
        "audited_tcfr",
        "qa_consistency",
        "direct_identifier_leak",
        "quasi_identifier_risk",
        "failed_qa",
        "omitted_facts",
        "audited_problem_facts",
        "direct_leaked_spans",
        "quasi_leaked_spans",
        "original_snippet",
        "anonymized_snippet",
    ]
    return {key: row[key] for key in keys}


def markdown_report(summary: dict) -> str:
    lines: list[str] = []
    lines.append("# Surface Metric Audit")
    lines.append("")
    lines.append(
        "This audit tests whether generic text-overlap metrics are sufficient proxies for "
        f"privacy-safe task utility on the {summary['by_method'][next(iter(summary['by_method']))]['n']}-example OpenAI run. No new API calls are used."
    )
    lines.append("")
    lines.append("## Method Means")
    lines.append("")
    lines.append(
        "| Method | N | Char sim | Token F1 | Token Jaccard | TF-IDF cosine | Edit rate | Audited TCFR | QA | Direct leak | QI risk |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for method, stats in summary["by_method"].items():
        lines.append(
            "| {method} | {n} | {char} | {f1} | {jac} | {tfidf} | {edit} | {tcfr} | {qa} | {direct} | {qi} |".format(
                method=method,
                n=stats["n"],
                char=fmt(stats["char_similarity"]),
                f1=fmt(stats["token_f1"]),
                jac=fmt(stats["token_jaccard"]),
                tfidf=fmt(stats["tfidf_cosine"]),
                edit=fmt(stats["token_edit_rate"]),
                tcfr=fmt(stats["audited_tcfr"]),
                qa=fmt(stats["qa_consistency"]),
                direct=fmt(stats["direct_identifier_leak"]),
                qi=fmt(stats["quasi_identifier_risk"]),
            )
        )
    lines.append("")
    lines.append("## High-Similarity Failures")
    lines.append("")
    lines.append(
        "Rows at or above the median surface score still often fail audited fact, exact QA, or privacy checks."
    )
    lines.append("")
    lines.append(
        "| Surface metric | Median threshold | Rows | Audited fact-loss rows | QA-failure rows | Privacy failure rows | Any failure rows |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for item in summary["high_similarity"]:
        lines.append(
            "| {metric} | {threshold} | {n} | {aff} ({aff_rate}) | {qaf} ({qaf_rate}) | {pf} ({pf_rate}) | {af} ({af_rate}) |".format(
                metric=item["metric"],
                threshold=fmt(item["threshold"]),
                n=item["n"],
                aff=item["rows_with_audited_fact_failure"],
                aff_rate=fmt(item["audited_fact_failure_rate"]),
                qaf=item["rows_with_qa_failure"],
                qaf_rate=fmt(item["qa_failure_rate"]),
                pf=item["rows_with_privacy_failure"],
                pf_rate=fmt(item["privacy_failure_rate"]),
                af=item["rows_with_any_failure"],
                af_rate=fmt(item["any_failure_rate"]),
            )
        )
    lines.append("")
    lines.append("## Correlations")
    lines.append("")
    lines.append(
        "Pearson and Spearman correlations are computed over all method-example rows. "
        "A strong surface metric would need to track both retained facts and privacy failures, but these metrics do not."
    )
    lines.append("")
    lines.append("| Surface metric | Pearson vs audited TCFR | Spearman vs audited TCFR | Pearson vs QA | Pearson vs direct leak | Pearson vs QI risk |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for metric, stats in summary["correlations"].items():
        lines.append(
            "| {metric} | {pt} | {st} | {qa} | {direct} | {qi} |".format(
                metric=metric,
                pt=fmt(stats["pearson_audited_tcfr"]),
                st=fmt(stats["spearman_audited_tcfr"]),
                qa=fmt(stats["pearson_qa_consistency"]),
                direct=fmt(stats["pearson_direct_identifier_leak"]),
                qi=fmt(stats["pearson_quasi_identifier_risk"]),
            )
        )
    lines.append("")
    lines.append("## Paper-Useful Examples")
    lines.append("")
    lines.append("### High Similarity But Audited Fact Loss")
    lines.append("")
    append_examples(lines, summary["examples"]["high_similarity_audited_fact_failures"])
    lines.append("")
    lines.append("### High Similarity But Exact QA Failure")
    lines.append("")
    append_examples(lines, summary["examples"]["high_similarity_qa_failures"])
    lines.append("")
    lines.append("### High Similarity But Privacy Failure")
    lines.append("")
    append_examples(lines, summary["examples"]["high_similarity_privacy_failures"])
    lines.append("")
    lines.append("## Takeaway")
    lines.append("")
    lines.append(
        "Surface overlap can reward outputs that retain original identifiers and quasi-identifiers, "
        "and it can miss exact QA failures or audited fact losses. The paper should therefore treat "
        "edit rate and generic similarity as diagnostic foils, not headline privacy or utility metrics."
    )
    return "\n".join(lines)


def append_examples(lines: list[str], examples: list[dict]) -> None:
    if not examples:
        lines.append("No examples met the configured threshold.")
        return
    lines.append("| ID | Method | Token F1 | Audited TCFR | QA | Privacy flags | Failure signal |")
    lines.append("|---|---|---:|---:|---:|---|---|")
    for row in examples:
        privacy = []
        if row["direct_identifier_leak"]:
            privacy.append("direct leak")
        if row["quasi_identifier_risk"] >= 2:
            privacy.append(f"QI {row['quasi_identifier_risk']:.0f}")
        if not privacy:
            privacy.append("none")
        failures = []
        if row["failed_qa"]:
            failures.append("QA: " + "; ".join(row["failed_qa"][:2]))
        if row["audited_problem_facts"]:
            failures.append("audited: " + "; ".join(str(f) for f in row["audited_problem_facts"][:2]))
        if row["omitted_facts"]:
            failures.append("omitted: " + "; ".join(str(f) for f in row["omitted_facts"][:2]))
        if row["direct_leaked_spans"]:
            failures.append("leaked: " + "; ".join(str(s) for s in row["direct_leaked_spans"][:2]))
        if row["quasi_leaked_spans"]:
            failures.append("QI spans: " + "; ".join(str(s) for s in row["quasi_leaked_spans"][:2]))
        lines.append(
            "| {id} | {method} | {f1} | {tcfr} | {qa} | {privacy} | {failure} |".format(
                id=row["id"],
                method=row["method"],
                f1=fmt(row["token_f1"]),
                tcfr=fmt(row["audited_tcfr"]),
                qa=fmt(row["qa_consistency"]),
                privacy=", ".join(privacy),
                failure=escape_table("; ".join(failures) if failures else "none"),
            )
        )


def escape_table(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def run(args: argparse.Namespace) -> None:
    rows = build_rows(args)
    examples = select_examples(rows)
    summary = {
        "n": len(rows),
        "by_method": summarize_by_method(rows),
        "high_similarity": [
            summarize_high_similarity(rows, "char_similarity"),
            summarize_high_similarity(rows, "token_f1"),
            summarize_high_similarity(rows, "token_jaccard"),
            summarize_high_similarity(rows, "tfidf_cosine"),
        ],
        "correlations": correlations(rows),
        "examples": {
            key: [compact_example(row) for row in value]
            for key, value in examples.items()
        },
    }
    write_json(args.out_json, summary)
    out_md = Path(args.out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    with out_md.open("w", encoding="utf-8") as f:
        f.write(markdown_report(summary))
        f.write("\n")
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/benchmark.jsonl")
    parser.add_argument("--outputs", default="data/processed/openai_anonymized_outputs.jsonl")
    parser.add_argument("--scored", default="data/processed/openai_judgments.jsonl")
    parser.add_argument("--fact-judgments", default="data/processed/openai_fact_judgments.jsonl")
    parser.add_argument("--out-json", default="results/surface_metric_audit.json")
    parser.add_argument("--out-md", default="results/surface_metric_audit.md")
    parser.add_argument("--high-qi-threshold", type=float, default=2.0)
    args = parser.parse_args()
    run(args)


if __name__ == "__main__":
    main()
