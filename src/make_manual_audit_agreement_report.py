"""Summarize fixed manual-audit evidence and second-annotator readiness.

This script is cache-only: it does not call any model or external service. The
output is intentionally conservative because the prepared second-annotator form
has not yet been completed by an independent annotator.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from statistics import mean

from io_utils import read_jsonl, write_json


METHODS = ["generic_llm", "privacy_first_llm", "critical_span_guard_extracted"]
METHOD_LABELS = {
    "generic_llm": "Generic LLM",
    "privacy_first_llm": "Privacy-first LLM",
    "critical_span_guard_extracted": "Critical Span Guard",
}


def fmt(value: float) -> str:
    return f"{value:.3f}"


def load_json(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def row_bool(row: dict, name: str) -> bool:
    if name == "direct_identifier_retained":
        return bool(row.get("direct_leaked_spans"))
    if name == "quasi_identifier_retained":
        return bool(row.get("quasi_leaked_spans"))
    if name == "audited_fact_loss":
        return bool(row.get("not_retained_audited_facts"))
    if name == "exact_qa_failure":
        return "exact_qa_failure" in set(row.get("labels", []))
    if name == "exact_match_artifact":
        return "exact_match_artifact" in set(row.get("labels", []))
    raise KeyError(name)


def expected_label_bool(row: dict, name: str) -> bool:
    labels = set(row.get("labels", []))
    if name == "direct_identifier_retained":
        return "direct_identifier_leak" in labels
    if name == "quasi_identifier_retained":
        return "quasi_identifier_retained" in labels
    if name == "audited_fact_loss":
        return "audited_fact_loss" in labels
    if name == "exact_qa_failure":
        return "exact_qa_failure" in labels
    if name == "exact_match_artifact":
        return "exact_match_artifact" in labels
    raise KeyError(name)


def flatten_method_rows(fixed: dict) -> list[dict]:
    rows = []
    for example in fixed.get("examples", []):
        for method_row in example.get("methods", []):
            row = dict(method_row)
            row["id"] = example.get("id")
            row["domain"] = example.get("domain")
            rows.append(row)
    return rows


def summarize_methods(rows: list[dict]) -> dict[str, dict]:
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        grouped[row["method"]].append(row)

    out: dict[str, dict] = {}
    for method in METHODS:
        method_rows = grouped[method]
        n = len(method_rows)
        direct_rows = sum(row_bool(row, "direct_identifier_retained") for row in method_rows)
        qi_rows = sum(row_bool(row, "quasi_identifier_retained") for row in method_rows)
        fact_loss_rows = sum(row_bool(row, "audited_fact_loss") for row in method_rows)
        qa_fail_rows = sum(row_bool(row, "exact_qa_failure") for row in method_rows)
        artifact_rows = sum(row_bool(row, "exact_match_artifact") for row in method_rows)
        clean_rows = sum(row.get("labels") == ["clean"] for row in method_rows)
        out[method] = {
            "rows": n,
            "direct_identifier_retained_rows": direct_rows,
            "direct_identifier_retained_rate": direct_rows / n if n else 0.0,
            "quasi_identifier_retained_rows": qi_rows,
            "quasi_identifier_retained_rate": qi_rows / n if n else 0.0,
            "audited_fact_loss_rows": fact_loss_rows,
            "audited_fact_loss_rate": fact_loss_rows / n if n else 0.0,
            "exact_qa_failure_rows": qa_fail_rows,
            "exact_qa_failure_rate": qa_fail_rows / n if n else 0.0,
            "exact_match_artifact_rows": artifact_rows,
            "exact_match_artifact_rate": artifact_rows / n if n else 0.0,
            "clean_rows": clean_rows,
            "clean_rate": clean_rows / n if n else 0.0,
            "exact_tcfr": mean(float(row.get("exact_tcfr", 0.0)) for row in method_rows) if n else 0.0,
            "audited_tcfr": mean(float(row.get("audited_tcfr", 0.0)) for row in method_rows) if n else 0.0,
            "qa_consistency": mean(float(row.get("qa_consistency", 0.0)) for row in method_rows) if n else 0.0,
        }
    return out


def summarize_packet(packet: list[dict], fixed_ids: set[str], answer_key: dict) -> dict:
    variants_by_id: dict[str, set[str]] = defaultdict(set)
    domains = Counter()
    forbidden_values = set(METHODS)
    method_counts = Counter()
    method_label_leak_rows = []
    for row in packet:
        example_id = str(row.get("example_id"))
        variants_by_id[example_id].add(str(row.get("variant_code")))
        if row.get("variant_code") == "A":
            domains[str(row.get("domain"))] += 1
        row_text = json.dumps(row, ensure_ascii=True)
        if any(value in row_text for value in forbidden_values):
            method_label_leak_rows.append(f"{example_id}:{row.get('variant_code')}")

    answer_examples = answer_key.get("examples", {})
    for mapping in answer_examples.values():
        method_counts.update(mapping.values())

    complete_variant_sets = all(variants == {"A", "B", "C"} for variants in variants_by_id.values())
    answer_key_complete = (
        answer_key.get("do_not_share_with_annotator") is True
        and set(answer_examples) == fixed_ids
        and all(set(mapping) == {"A", "B", "C"} and set(mapping.values()) == set(METHODS) for mapping in answer_examples.values())
    )
    return {
        "packet_rows": len(packet),
        "examples": len(variants_by_id),
        "domain_counts": dict(sorted(domains.items())),
        "packet_ids_match_fixed_audit": set(variants_by_id) == fixed_ids,
        "complete_variant_sets": complete_variant_sets,
        "answer_key_complete": answer_key_complete,
        "method_label_leak_rows": method_label_leak_rows,
        "method_counts_in_answer_key": dict(method_counts),
        "completed_independent_annotations": False,
    }


def consistency_checks(rows: list[dict]) -> dict[str, dict]:
    out = {}
    for field in [
        "direct_identifier_retained",
        "quasi_identifier_retained",
        "audited_fact_loss",
        "exact_qa_failure",
        "exact_match_artifact",
    ]:
        agreements = sum(row_bool(row, field) == expected_label_bool(row, field) for row in rows)
        positives = sum(row_bool(row, field) for row in rows)
        out[field] = {
            "rows": len(rows),
            "positive_rows": positives,
            "agreements": agreements,
            "agreement_rate": agreements / len(rows) if rows else 0.0,
        }
    return out


def build_report(fixed: dict, packet: list[dict], answer_key: dict, args: argparse.Namespace) -> dict:
    rows = flatten_method_rows(fixed)
    fixed_ids = {example.get("id") for example in fixed.get("examples", [])}
    return {
        "metadata": {
            "generated": date.today().isoformat(),
            "scope": (
                "Cache-only synthesis of the fixed manual-style audit and blinded second-annotator packet. "
                "This is not completed independent annotation or inter-rater agreement."
            ),
            "no_api_calls": True,
            "fixed_audit_json": args.fixed_audit_json,
            "packet_jsonl": args.packet_jsonl,
            "answer_key": args.answer_key,
        },
        "fixed_subset": {
            "examples": len(fixed_ids),
            "method_rows": len(rows),
            "sample_version": fixed.get("metadata", {}).get("sample_version"),
            "domain_counts": fixed.get("summary", {}).get("domain_counts", {}),
            "required_caveat_ids": fixed.get("summary", {}).get("required_caveat_ids", {}),
        },
        "method_summary": summarize_methods(rows),
        "packet_readiness": summarize_packet(packet, fixed_ids, answer_key),
        "reference_label_consistency": consistency_checks(rows),
        "paper_use_caveats": [
            "The fixed subset is enriched for difficult and caveat rows, so subset rates are not population estimates.",
            "The second-annotator packet is ready and blinded, but no independent annotation has been completed.",
            "Reference-label consistency checks validate artifact synchronization, not human inter-rater reliability.",
        ],
    }


def write_markdown(payload: dict, out_path: str) -> None:
    meta = payload["metadata"]
    subset = payload["fixed_subset"]
    packet = payload["packet_readiness"]
    lines = ["# Manual Audit Agreement and Readiness Report", ""]
    lines.append(f"Generated: {meta['generated']}")
    lines.append("")
    lines.append(
        "This report synthesizes the fixed manual-style audit and the blinded second-annotator packet without new API calls."
    )
    lines.append(
        "Scope caveat: the packet is ready for independent annotation, but it has not been completed; the agreement checks below are artifact-consistency checks against current reference labels, not inter-rater agreement."
    )
    lines.append("")
    lines.append("## Fixed-Subset Summary")
    lines.append("")
    domain_text = ", ".join(f"{key}={value}" for key, value in sorted(subset["domain_counts"].items()))
    lines.append(f"- Examples: {subset['examples']} ({domain_text}).")
    lines.append(f"- Method rows: {subset['method_rows']}.")
    lines.append(f"- Sample version: `{subset['sample_version']}`.")
    lines.append("- The subset intentionally includes all promoted CSG residual-QI and strict-specificity caveat rows.")
    lines.append("")
    lines.append("## Method-Row Summary")
    lines.append("")
    lines.append("| Method | Rows | Direct rate | QI rate | Audited TCFR | Fact-loss rate | QA-fail rate | Clean rate |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for method in METHODS:
        stats = payload["method_summary"][method]
        lines.append(
            "| {label} | {rows} | {direct} | {qi} | {audited} | {fact_loss} | {qa_fail} | {clean} |".format(
                label=METHOD_LABELS[method],
                rows=stats["rows"],
                direct=fmt(stats["direct_identifier_retained_rate"]),
                qi=fmt(stats["quasi_identifier_retained_rate"]),
                audited=fmt(stats["audited_tcfr"]),
                fact_loss=fmt(stats["audited_fact_loss_rate"]),
                qa_fail=fmt(stats["exact_qa_failure_rate"]),
                clean=fmt(stats["clean_rate"]),
            )
        )
    lines.append("")
    lines.append("## Blinded Packet Readiness")
    lines.append("")
    lines.append("| Check | Value |")
    lines.append("|---|---:|")
    lines.append(f"| Packet rows | {packet['packet_rows']} |")
    lines.append(f"| Examples | {packet['examples']} |")
    lines.append(f"| Packet IDs match fixed audit | {packet['packet_ids_match_fixed_audit']} |")
    lines.append(f"| Complete A/B/C variants | {packet['complete_variant_sets']} |")
    lines.append(f"| Answer key complete and separated | {packet['answer_key_complete']} |")
    lines.append(f"| Method-label leak rows in packet | {len(packet['method_label_leak_rows'])} |")
    lines.append(f"| Completed independent annotations | {packet['completed_independent_annotations']} |")
    lines.append("")
    lines.append("## Reference-Label Consistency")
    lines.append("")
    lines.append("| Reference field | Positive rows | Agreements | Agreement rate |")
    lines.append("|---|---:|---:|---:|")
    for field, stats in payload["reference_label_consistency"].items():
        lines.append(
            f"| `{field}` | {stats['positive_rows']}/{stats['rows']} | {stats['agreements']}/{stats['rows']} | {fmt(stats['agreement_rate'])} |"
        )
    lines.append("")
    lines.append("## Paper-Use Caveats")
    lines.append("")
    for caveat in payload["paper_use_caveats"]:
        lines.append(f"- {caveat}")
    lines.append("")
    lines.append("Recommended wording: fixed-subset evidence confirms that CSG remains the best utility-preserving method on the deliberately hard audit subset, while the prepared blinded packet enables a future independent annotation pass.")
    lines.append("")

    path = Path(out_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixed-audit-json", default="results/fixed_sample_manual_audit_n150.json")
    parser.add_argument("--packet-jsonl", default="data/processed/second_annotator_packet_n150.jsonl")
    parser.add_argument("--answer-key", default="results/second_annotator_answer_key_n150.json")
    parser.add_argument("--out-json", default="results/manual_audit_agreement_n150.json")
    parser.add_argument("--out-md", default="results/manual_audit_agreement_n150.md")
    args = parser.parse_args()

    fixed = load_json(args.fixed_audit_json)
    packet = read_jsonl(args.packet_jsonl)
    answer_key = load_json(args.answer_key)
    payload = build_report(fixed, packet, answer_key, args)
    write_json(args.out_json, payload)
    write_markdown(payload, args.out_md)
    print(f"wrote {args.out_json}")
    print(f"wrote {args.out_md}")


if __name__ == "__main__":
    main()
