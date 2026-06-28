"""Build a stratified subset for independent fact and privacy audits."""

from __future__ import annotations

import argparse
import json
import random
from collections import defaultdict

from io_utils import read_jsonl, write_json, write_jsonl


CSG_METHOD = "critical_span_guard_extracted"


def row_map(rows: list[dict]) -> dict[tuple[str, str], dict]:
    return {(row["id"], row["method"]): row for row in rows}


def mean(values: list[float]) -> float:
    return sum(values) / len(values) if values else 0.0


def hard_score(example_id: str, deterministic: dict[tuple[str, str], dict], audited: dict[tuple[str, str], dict]) -> float:
    det_rows = [row for (row_id, _), row in deterministic.items() if row_id == example_id]
    audit_rows = [row for (row_id, _), row in audited.items() if row_id == example_id]
    direct = max((row.get("direct_identifier_leak", 0) for row in det_rows), default=0)
    qi = max((row.get("quasi_identifier_risk", 0) for row in det_rows), default=0)
    semantic = max((row.get("semantic_similarity_proxy", 0.0) for row in det_rows), default=0.0)
    tcfr_gap = 0.0
    if audit_rows:
        tcfr_values = [float(row.get("audited_tcfr", 0.0)) for row in audit_rows]
        tcfr_gap = max(tcfr_values) - min(tcfr_values)
    privacy_first_loss = 0.0
    privacy_row = audited.get((example_id, "privacy_first_llm"))
    if privacy_row is not None:
        privacy_first_loss = 1.0 - float(privacy_row.get("audited_tcfr", 0.0))
    return 5.0 * direct + 1.5 * qi + 2.0 * tcfr_gap + privacy_first_loss + semantic


def select_hard_ids(
    examples: list[dict],
    deterministic: dict[tuple[str, str], dict],
    audited: dict[tuple[str, str], dict],
    n_hard: int,
) -> tuple[list[str], dict[str, list[str]]]:
    example_ids = [row["id"] for row in examples]
    reasons: dict[str, list[str]] = defaultdict(list)
    required_ids: set[str] = set()

    for (example_id, method), row in deterministic.items():
        if method == CSG_METHOD and row.get("quasi_identifier_risk", 0) > 0:
            reasons[example_id].append("residual CSG QI risk")
            required_ids.add(example_id)

    for (example_id, method), row in audited.items():
        if method == CSG_METHOD and float(row.get("audited_tcfr", 0.0)) < 0.999:
            reasons[example_id].append("CSG audited fact loss")
            required_ids.add(example_id)

    for (example_id, method), row in deterministic.items():
        if method == "generic_llm" and row.get("direct_identifier_leak", 0) > 0:
            reasons[example_id].append("generic direct identifier leak")

    selected = sorted(
        required_ids,
        key=lambda example_id: (-hard_score(example_id, deterministic, audited), example_id),
    )
    selected_set = set(selected)
    if len(selected) < n_hard:
        ranked = sorted(
            example_ids,
            key=lambda example_id: (-hard_score(example_id, deterministic, audited), example_id),
        )
        for example_id in ranked:
            if example_id not in selected_set:
                reasons[example_id].append("high privacy-utility stress score")
                selected.append(example_id)
                selected_set.add(example_id)
            if len(selected) >= n_hard:
                break
    return selected, reasons


def select_domain_ids(
    examples: list[dict],
    deterministic: dict[tuple[str, str], dict],
    audited: dict[tuple[str, str], dict],
    domain: str,
    count: int,
    exclude: set[str],
    seed: int,
) -> list[str]:
    candidates = [row["id"] for row in examples if row["domain"] == domain and row["id"] not in exclude]
    rng = random.Random(seed + sum(ord(ch) for ch in domain))
    buckets: dict[int, list[str]] = defaultdict(list)
    for example_id in candidates:
        score = hard_score(example_id, deterministic, audited)
        bucket = 2 if score >= 4.0 else 1 if score >= 2.0 else 0
        buckets[bucket].append(example_id)
    selected: list[str] = []
    per_bucket = max(1, count // 3)
    for bucket in [2, 1, 0]:
        rows = buckets[bucket]
        rng.shuffle(rows)
        selected.extend(sorted(rows[:per_bucket]))
    if len(selected) < count:
        rest = [example_id for example_id in candidates if example_id not in set(selected)]
        rng.shuffle(rest)
        selected.extend(rest[: count - len(selected)])
    return selected[:count]


def build(args: argparse.Namespace) -> None:
    examples = read_jsonl(args.benchmark)
    deterministic = row_map(read_jsonl(args.deterministic_judgments))
    audited = row_map(read_jsonl(args.fact_judgments))
    by_id = {row["id"]: row for row in examples}

    hard_ids, reasons = select_hard_ids(examples, deterministic, audited, args.hard_count)
    selected: list[tuple[str, str]] = [(example_id, "hard") for example_id in hard_ids]
    selected_ids = {example_id for example_id, _ in selected}

    for domain, count in [("clinical", args.clinical_count), ("legal", args.legal_count)]:
        domain_ids = select_domain_ids(
            examples,
            deterministic,
            audited,
            domain,
            count,
            selected_ids,
            args.seed,
        )
        selected.extend((example_id, domain) for example_id in domain_ids)
        selected_ids.update(domain_ids)

    selected = selected[: args.total_count]
    selected_ids = {example_id for example_id, _ in selected}
    if len(selected_ids) != len(selected):
        raise RuntimeError("subset selection produced duplicate ids")

    manifest = []
    for rank, (example_id, bucket) in enumerate(selected, start=1):
        example = by_id[example_id]
        manifest.append(
            {
                "rank": rank,
                "id": example_id,
                "domain": example["domain"],
                "bucket": bucket,
                "selection_reasons": sorted(set(reasons.get(example_id, [f"{bucket} stratified sample"]))),
                "hard_score": hard_score(example_id, deterministic, audited),
            }
        )

    with open(args.ids_out, "w", encoding="utf-8") as f:
        for row in manifest:
            f.write(row["id"] + "\n")
    write_jsonl(args.manifest_out, manifest)
    summary = summarize_manifest(manifest)
    write_json(args.summary_out, summary)
    with open(args.report_out, "w", encoding="utf-8") as f:
        f.write(markdown_report(manifest, summary))
        f.write("\n")
    print(f"wrote {len(manifest)} ids to {args.ids_out}")
    print(f"wrote {args.report_out}")


def summarize_manifest(manifest: list[dict]) -> dict:
    out = {"n": len(manifest), "by_bucket": {}, "by_domain": {}, "reason_counts": {}}
    for row in manifest:
        out["by_bucket"][row["bucket"]] = out["by_bucket"].get(row["bucket"], 0) + 1
        out["by_domain"][row["domain"]] = out["by_domain"].get(row["domain"], 0) + 1
        for reason in row["selection_reasons"]:
            out["reason_counts"][reason] = out["reason_counts"].get(reason, 0) + 1
    out["mean_hard_score"] = mean([float(row["hard_score"]) for row in manifest])
    return out


def markdown_report(manifest: list[dict], summary: dict) -> str:
    lines = ["# External Audit Stratified Subset", ""]
    lines.append(f"Rows: {summary['n']}")
    lines.append("")
    lines.append("## Composition")
    lines.append("")
    lines.append("| Group | Count |")
    lines.append("|---|---:|")
    for key, value in sorted(summary["by_bucket"].items()):
        lines.append(f"| bucket={key} | {value} |")
    for key, value in sorted(summary["by_domain"].items()):
        lines.append(f"| domain={key} | {value} |")
    lines.append("")
    lines.append("## Selection Reasons")
    lines.append("")
    lines.append("| Reason | Count |")
    lines.append("|---|---:|")
    for key, value in sorted(summary["reason_counts"].items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"| {key} | {value} |")
    lines.append("")
    lines.append("## IDs")
    lines.append("")
    lines.append("| Rank | ID | Domain | Bucket | Reasons |")
    lines.append("|---:|---|---|---|---|")
    for row in manifest:
        reasons = "; ".join(row["selection_reasons"])
        lines.append(f"| {row['rank']} | `{row['id']}` | {row['domain']} | {row['bucket']} | {reasons} |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/benchmark_n150_llm.jsonl")
    parser.add_argument("--deterministic-judgments", default="data/processed/openai_judgments_n150.jsonl")
    parser.add_argument("--fact-judgments", default="data/processed/openai_fact_judgments_n150.jsonl")
    parser.add_argument("--ids-out", default="data/processed/gpt55_audit_ids_60.txt")
    parser.add_argument("--manifest-out", default="data/processed/gpt55_audit_subset_stratified60.jsonl")
    parser.add_argument("--summary-out", default="results/gpt55_audit_subset_stratified60.json")
    parser.add_argument("--report-out", default="results/gpt55_audit_subset_stratified60.md")
    parser.add_argument("--clinical-count", type=int, default=20)
    parser.add_argument("--legal-count", type=int, default=20)
    parser.add_argument("--hard-count", type=int, default=20)
    parser.add_argument("--total-count", type=int, default=60)
    parser.add_argument("--seed", type=int, default=55)
    args = parser.parse_args()
    build(args)


if __name__ == "__main__":
    main()
