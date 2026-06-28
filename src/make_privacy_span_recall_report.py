"""Generate a paper-facing privacy span recall audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

from io_utils import read_jsonl


METHODS = [
    ("generic_llm", "Generic LLM"),
    ("privacy_first_llm", "Privacy-first LLM"),
    ("critical_span_guard_extracted", "Critical Span Guard"),
]


def load_json(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def mean(summary: dict, method: str, key: str) -> float:
    value = summary["overall"][method][key]
    if isinstance(value, dict):
        return float(value["mean"])
    return float(value)


def domain_mean(summary: dict, domain: str, method: str, key: str) -> float:
    value = summary["by_domain"][domain][method][key]
    if isinstance(value, dict):
        return float(value["mean"])
    return float(value)


def leak_counts(rows: list[dict], method: str) -> dict:
    method_rows = [row for row in rows if row.get("method") == method]
    direct_spans = Counter()
    quasi_spans = Counter()
    for row in method_rows:
        direct_spans.update(str(span) for span in row.get("direct_leaked_spans", []))
        quasi_spans.update(str(span) for span in row.get("quasi_leaked_spans", []))
    return {
        "rows": len(method_rows),
        "direct_leak_rows": sum(1 for row in method_rows if row.get("direct_leaked_spans")),
        "quasi_leak_rows": sum(1 for row in method_rows if row.get("quasi_leaked_spans")),
        "direct_span_instances": sum(direct_spans.values()),
        "quasi_span_instances": sum(quasi_spans.values()),
        "top_direct": direct_spans.most_common(6),
        "top_quasi": quasi_spans.most_common(6),
    }


def gold_span_counts(benchmark_rows: list[dict], scored_rows: list[dict]) -> dict[str, dict[str, int]]:
    ids_by_domain: dict[str, set[str]] = defaultdict(set)
    for row in scored_rows:
        ids_by_domain[str(row.get("domain"))].add(str(row.get("id")))
    benchmark_by_id = {str(row["id"]): row for row in benchmark_rows}
    out: dict[str, dict[str, int]] = {}
    for domain, ids in sorted(ids_by_domain.items()):
        direct = 0
        quasi = 0
        for example_id in ids:
            for span in benchmark_by_id[example_id].get("private_spans", []):
                if span.get("identifier_type") == "DIRECT":
                    direct += 1
                elif span.get("identifier_type") == "QUASI":
                    quasi += 1
        out[domain] = {"direct": direct, "quasi": quasi, "total": direct + quasi, "rows": len(ids)}
    direct_all = sum(value["direct"] for value in out.values())
    quasi_all = sum(value["quasi"] for value in out.values())
    rows_all = sum(value["rows"] for value in out.values())
    out["overall"] = {"direct": direct_all, "quasi": quasi_all, "total": direct_all + quasi_all, "rows": rows_all}
    return out


def span_list(items: list[tuple[str, int]]) -> str:
    if not items:
        return "none"
    return "; ".join(f"`{span}` ({count})" for span, count in items)


def write_report(
    benchmark_path: str,
    scored_path: str,
    summary_path: str,
    out_path: str,
) -> None:
    benchmark = read_jsonl(benchmark_path)
    scored = read_jsonl(scored_path)
    summary = load_json(summary_path)
    gold = gold_span_counts(benchmark, scored)

    lines = ["# Privacy Span Recall Audit", ""]
    lines.append(f"Generated: {date.today().isoformat()}")
    lines.append("")
    lines.append(
        "This report surfaces the span-level privacy metrics already computed by `src/compute_metrics.py` for the promoted non-oracle run. "
        "Direct and quasi span recall measure the fraction of gold privacy spans not found verbatim in each anonymized output; they complement row-level direct-leak rate and QI-risk scoring."
    )
    lines.append("")
    lines.append("## Gold Span Inventory")
    lines.append("")
    lines.append("| Split | Rows | Direct spans | Quasi spans | Total privacy spans |")
    lines.append("|---|---:|---:|---:|---:|")
    for split in ["overall", *sorted(k for k in gold if k != "overall")]:
        counts = gold[split]
        lines.append(
            f"| {split} | {counts['rows']} | {counts['direct']} | {counts['quasi']} | {counts['total']} |"
        )
    lines.append("")
    lines.append("## Span Recall")
    lines.append("")
    lines.append("| Method | Direct span recall | Quasi span recall | All privacy span recall | Direct leak rows | Quasi leak rows |")
    lines.append("|---|---:|---:|---:|---:|---:|")
    for method, label in METHODS:
        counts = leak_counts(scored, method)
        lines.append(
            "| {label} | {direct} | {quasi} | {pii} | {direct_rows}/{rows} | {quasi_rows}/{rows} |".format(
                label=label,
                direct=fmt(mean(summary, method, "direct_span_recall")),
                quasi=fmt(mean(summary, method, "quasi_span_recall")),
                pii=fmt(mean(summary, method, "pii_span_recall")),
                direct_rows=counts["direct_leak_rows"],
                quasi_rows=counts["quasi_leak_rows"],
                rows=counts["rows"],
            )
        )
    lines.append("")
    lines.append("## Domain Split")
    lines.append("")
    lines.append("| Domain | Method | Direct span recall | Quasi span recall | All privacy span recall |")
    lines.append("|---|---|---:|---:|---:|")
    for domain in sorted(summary["by_domain"]):
        for method, label in METHODS:
            lines.append(
                "| {domain} | {label} | {direct} | {quasi} | {pii} |".format(
                    domain=domain,
                    label=label,
                    direct=fmt(domain_mean(summary, domain, method, "direct_span_recall")),
                    quasi=fmt(domain_mean(summary, domain, method, "quasi_span_recall")),
                    pii=fmt(domain_mean(summary, domain, method, "pii_span_recall")),
                )
            )
    lines.append("")
    lines.append("## Leaked Span Inventory")
    lines.append("")
    lines.append("| Method | Direct leaked span instances | Top direct leaks | Quasi leaked span instances | Top quasi leaks |")
    lines.append("|---|---:|---|---:|---|")
    for method, label in METHODS:
        counts = leak_counts(scored, method)
        lines.append(
            "| {label} | {direct_count} | {direct} | {quasi_count} | {quasi} |".format(
                label=label,
                direct_count=counts["direct_span_instances"],
                direct=span_list(counts["top_direct"]),
                quasi_count=counts["quasi_span_instances"],
                quasi=span_list(counts["top_quasi"]),
            )
        )
    lines.append("")
    lines.append("## Paper-Safe Interpretation")
    lines.append("")
    lines.append(
        "- CSG has perfect measured direct span recall on the promoted run and the strongest all-span recall, but it is still a deterministic string audit rather than a formal privacy guarantee."
    )
    lines.append(
        "- Generic prompting removes many obvious direct spans but leaves enough legal identifiers and quasi-identifiers to fail both row-level and span-level privacy checks."
    )
    lines.append(
        "- Privacy-first prompting reaches perfect direct span recall but still retains some quasi-identifying clinical or legal details while losing much more task-critical utility."
    )
    lines.append("")

    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/benchmark.jsonl")
    parser.add_argument("--scored", default="data/processed/openai_judgments_n100.jsonl")
    parser.add_argument("--summary", default="results/openai_summary_n100.json")
    parser.add_argument("--out", default="results/privacy_span_recall_audit_n100.md")
    args = parser.parse_args()
    write_report(args.benchmark, args.scored, args.summary, args.out)


if __name__ == "__main__":
    main()
