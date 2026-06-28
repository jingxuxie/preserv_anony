"""Build a fixed subset audit from existing row-level evidence.

This script does not call any model. It converts deterministic metrics and
cached fact-judge evidence into a transparent, fixed-sample audit packet.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from textwrap import shorten

from io_utils import read_jsonl, write_json


METHODS = ["generic_llm", "privacy_first_llm", "critical_span_guard_extracted"]

TARGET_DOMAIN_COUNTS = {"clinical": 15, "legal": 15}

ESSENTIAL_REASONS = {
    "clinical_0006": "foreground clinical utility-loss example",
    "legal_0006": "foreground legal privacy-utility example",
    "legal_0005": "residual CSG legal QI frontier row",
    "legal_0025": "residual CSG legal QI frontier row",
    "legal_0018": "exact-vs-audited legal metric nuance",
    "legal_0016": "strict legal-specificity audited utility caveat",
    "legal_0002": "residual CSG legal QI frontier row",
    "legal_0042": "residual CSG legal QI frontier row",
    "legal_0046": "residual CSG legal QI frontier row",
    "legal_0053": "residual CSG legal QI frontier row",
    "legal_0054": "residual CSG legal QI frontier row",
    "legal_0055": "residual CSG legal QI frontier row",
    "legal_0056": "residual CSG legal QI frontier row",
}

TAG_LABELS = {
    "generic_direct_leak": "generic direct identifier leak",
    "generic_qi_retention": "generic quasi-identifier retention",
    "privacy_first_utility_loss": "privacy-first utility loss",
    "csg_residual_qi": "CSG residual quasi-identifier",
    "csg_strict_specificity_loss": "CSG strict-specificity audited loss",
    "csg_exact_match_artifact": "CSG exact-match artifact",
    "exact_metric_artifact": "exact metric undercount",
    "csg_clean": "clean CSG row",
}

TAG_WEIGHTS = {
    "generic_direct_leak": 9.0,
    "generic_qi_retention": 4.0,
    "privacy_first_utility_loss": 7.0,
    "csg_residual_qi": 10.0,
    "csg_strict_specificity_loss": 10.0,
    "csg_exact_match_artifact": 5.0,
    "exact_metric_artifact": 4.0,
    "csg_clean": 1.0,
}


def clean(text: object) -> str:
    value = str(text)
    value = value.translate({ord(ch): " " for ch in "\x00\x11\x17\x7f"})
    return "".join(ch for ch in value if ch in "\n\t" or ord(ch) >= 32)


def short(text: object, width: int = 180) -> str:
    return shorten(clean(text).replace("\n", " "), width=width, placeholder=" ...")


def one_line(items: list[object], width: int = 180) -> str:
    if not items:
        return "None"
    return short("; ".join(clean(item) for item in items), width=width)


def retained_status(judgment: dict, gold_fact: dict | None) -> bool:
    status = judgment.get("status")
    if status == "preserved":
        return True
    if status == "generalized_but_acceptable":
        return bool((gold_fact or {}).get("generalization_allowed"))
    return False


def not_retained_facts(fact_row: dict | None, example: dict) -> list[str]:
    if not fact_row:
        return []
    gold_facts = example.get("task_critical_facts", [])
    out = []
    for judgment in fact_row.get("fact_judgments", []):
        try:
            gold_fact = gold_facts[int(judgment.get("fact_index"))]
        except (TypeError, ValueError, IndexError):
            gold_fact = None
        if not retained_status(judgment, gold_fact):
            out.append(clean(judgment.get("gold_fact") or judgment.get("fact") or ""))
    return out


def has_contradiction(fact_row: dict | None) -> bool:
    return any(judgment.get("status") == "contradicted" for judgment in (fact_row or {}).get("fact_judgments", []))


def fact_status_counts(fact_row: dict | None, example: dict) -> Counter:
    counts: Counter = Counter()
    if not fact_row:
        return counts
    gold_facts = example.get("task_critical_facts", [])
    for judgment in fact_row.get("fact_judgments", []):
        status = str(judgment.get("status", "missing"))
        if status == "generalized_but_acceptable":
            try:
                gold_fact = gold_facts[int(judgment.get("fact_index"))]
            except (TypeError, ValueError, IndexError):
                gold_fact = None
            status = "generalized_retained" if retained_status(judgment, gold_fact) else "generalized_not_retained"
        counts[status] += 1
    return counts


def format_counts(counts: Counter) -> str:
    if not counts:
        return "NA"
    order = ["preserved", "generalized_retained", "generalized_not_retained", "omitted", "contradicted"]
    parts = [f"{key}={counts[key]}" for key in order if counts.get(key)]
    parts.extend(f"{key}={value}" for key, value in sorted(counts.items()) if key not in order)
    return ", ".join(parts)


def audited_tcfr(fact_row: dict | None) -> float:
    if not fact_row:
        return 0.0
    return float(fact_row.get("audited_tcfr", 0.0))


def row_labels(score: dict, fact_row: dict | None, example: dict) -> list[str]:
    method = score["method"]
    labels: list[str] = []
    direct = bool(score.get("direct_leaked_spans"))
    quasi = bool(score.get("quasi_leaked_spans"))
    not_retained = bool(not_retained_facts(fact_row, example))
    audited = audited_tcfr(fact_row)
    exact = float(score.get("tcfr", 0.0))
    qa = float(score.get("qa_consistency", 0.0))

    if direct:
        labels.append("direct_identifier_leak")
    if quasi:
        labels.append("quasi_identifier_retained")
    if not_retained:
        labels.append("audited_fact_loss")
    if has_contradiction(fact_row):
        labels.append("audited_contradiction")
    if score.get("omitted_facts"):
        labels.append("exact_fact_omission")
    if score.get("failed_qa"):
        labels.append("exact_qa_failure")
    if fact_row and audited - exact >= 0.15:
        labels.append("exact_match_artifact")
    if method == "privacy_first_llm" and (not_retained or qa < 0.999 or exact < 0.75):
        labels.append("privacy_first_overgeneralization")
    if method == "generic_llm" and (direct or quasi):
        labels.append("generic_privacy_leak")
    if method == "critical_span_guard_extracted" and quasi:
        labels.append("csg_residual_qi_frontier")
    if method == "critical_span_guard_extracted" and not_retained:
        labels.append("csg_strict_specificity_loss")
    return labels or ["clean"]


def example_tags(example_id: str, scored: dict[tuple[str, str], dict], judged: dict[tuple[str, str], dict], example: dict) -> set[str]:
    tags: set[str] = set()
    for method in METHODS:
        score = scored[(example_id, method)]
        fact_row = judged.get((example_id, method))
        labels = set(row_labels(score, fact_row, example))
        if method == "generic_llm":
            if "direct_identifier_leak" in labels:
                tags.add("generic_direct_leak")
            if "quasi_identifier_retained" in labels:
                tags.add("generic_qi_retention")
        if method == "privacy_first_llm" and "privacy_first_overgeneralization" in labels:
            tags.add("privacy_first_utility_loss")
        if method == "critical_span_guard_extracted":
            if "csg_residual_qi_frontier" in labels:
                tags.add("csg_residual_qi")
            if "csg_strict_specificity_loss" in labels:
                tags.add("csg_strict_specificity_loss")
            if "exact_match_artifact" in labels:
                tags.add("csg_exact_match_artifact")
            if labels == {"clean"}:
                tags.add("csg_clean")
        if "exact_match_artifact" in labels:
            tags.add("exact_metric_artifact")
    return tags or {"low_signal_control"}


def severity(example_id: str, scored: dict[tuple[str, str], dict], judged: dict[tuple[str, str], dict], example: dict) -> float:
    total = 0.0
    for method in METHODS:
        score = scored[(example_id, method)]
        fact_row = judged.get((example_id, method))
        total += 2.0 * len(score.get("direct_leaked_spans", []))
        total += 1.0 * len(score.get("quasi_leaked_spans", []))
        total += 6.0 * (1.0 - audited_tcfr(fact_row))
        total += 2.0 * (1.0 - float(score.get("qa_consistency", 0.0)))
        total += 2.0 * max(0.0, audited_tcfr(fact_row) - float(score.get("tcfr", 0.0)))
        if not_retained_facts(fact_row, example):
            total += 1.0
    return total


def select_sample(
    examples: dict[str, dict],
    scored: dict[tuple[str, str], dict],
    judged: dict[tuple[str, str], dict],
) -> list[str]:
    selected: list[str] = []
    selected_set: set[str] = set()

    def add_id(example_id: str) -> None:
        if example_id in examples and example_id not in selected_set:
            selected.append(example_id)
            selected_set.add(example_id)

    for example_id in ESSENTIAL_REASONS:
        add_id(example_id)

    required_caveat_ids = sorted(
        {
            example_id
            for (example_id, method), score in scored.items()
            if method == "critical_span_guard_extracted" and score.get("quasi_leaked_spans")
        }
        | {
            example_id
            for (example_id, method), fact_row in judged.items()
            if method == "critical_span_guard_extracted"
            and example_id in examples
            and not_retained_facts(fact_row, examples[example_id])
        }
    )
    for example_id in required_caveat_ids:
        add_id(example_id)

    for domain, target in TARGET_DOMAIN_COUNTS.items():
        while sum(1 for example_id in selected if examples[example_id]["domain"] == domain) < target:
            chosen_id: str | None = None
            chosen_score: float | None = None
            current_domain_tags = set()
            for example_id in selected:
                if examples[example_id]["domain"] == domain:
                    current_domain_tags.update(example_tags(example_id, scored, judged, examples[example_id]))
            for example_id, example in examples.items():
                if example_id in selected_set or example["domain"] != domain:
                    continue
                tags = example_tags(example_id, scored, judged, example)
                tag_score = sum(TAG_WEIGHTS.get(tag, 0.5) for tag in tags)
                uncovered_bonus = 5.0 * len(tags - current_domain_tags)
                candidate_score = tag_score + uncovered_bonus + severity(example_id, scored, judged, example)
                if chosen_score is None or candidate_score > chosen_score or (
                    candidate_score == chosen_score and example_id < (chosen_id or "")
                ):
                    chosen_id = example_id
                    chosen_score = candidate_score
            if chosen_id is None:
                raise RuntimeError(f"Could not fill fixed sample for domain {domain}")
            add_id(chosen_id)

    return sorted(selected, key=lambda example_id: (examples[example_id]["domain"], example_id))


def method_row(score: dict, fact_row: dict | None, example: dict) -> dict:
    labels = row_labels(score, fact_row, example)
    return {
        "method": score["method"],
        "direct_leaked_spans": score.get("direct_leaked_spans", []),
        "quasi_leaked_spans": score.get("quasi_leaked_spans", []),
        "exact_tcfr": float(score.get("tcfr", 0.0)),
        "audited_tcfr": audited_tcfr(fact_row),
        "qa_consistency": float(score.get("qa_consistency", 0.0)),
        "labels": labels,
        "not_retained_audited_facts": not_retained_facts(fact_row, example),
        "fact_status_counts": dict(fact_status_counts(fact_row, example)),
    }


def build_payload(
    sample_ids: list[str],
    examples: dict[str, dict],
    scored: dict[tuple[str, str], dict],
    judged: dict[tuple[str, str], dict],
    args: argparse.Namespace,
) -> dict:
    rows = []
    domain_counts: Counter = Counter()
    label_counts_by_method: dict[str, Counter] = {method: Counter() for method in METHODS}
    row_summary_by_method: dict[str, Counter] = {method: Counter() for method in METHODS}
    tag_counts: Counter = Counter()

    for example_id in sample_ids:
        example = examples[example_id]
        domain_counts[example["domain"]] += 1
        tags = sorted(example_tags(example_id, scored, judged, example))
        tag_counts.update(tags)
        methods = []
        for method in METHODS:
            row = method_row(scored[(example_id, method)], judged.get((example_id, method)), example)
            methods.append(row)
            label_counts_by_method[method].update(row["labels"])
            row_summary_by_method[method]["rows"] += 1
            if row["direct_leaked_spans"]:
                row_summary_by_method[method]["direct_leak_rows"] += 1
            if row["quasi_leaked_spans"]:
                row_summary_by_method[method]["qi_hit_rows"] += 1
            if row["not_retained_audited_facts"]:
                row_summary_by_method[method]["audited_fact_loss_rows"] += 1
            if "exact_qa_failure" in row["labels"]:
                row_summary_by_method[method]["exact_qa_failure_rows"] += 1
            if "exact_match_artifact" in row["labels"]:
                row_summary_by_method[method]["exact_match_artifact_rows"] += 1
            if row["labels"] == ["clean"]:
                row_summary_by_method[method]["clean_rows"] += 1
        reasons = [ESSENTIAL_REASONS[example_id]] if example_id in ESSENTIAL_REASONS else []
        reasons.extend(TAG_LABELS.get(tag, tag.replace("_", " ")) for tag in tags if TAG_LABELS.get(tag) not in reasons)
        rows.append(
            {
                "id": example_id,
                "domain": example["domain"],
                "source": example.get("source"),
                "selected_because": reasons,
                "tags": tags,
                "methods": methods,
            }
        )

    csg_residual_ids = sorted(
        example_id
        for (example_id, method), score in scored.items()
        if method == "critical_span_guard_extracted" and score.get("quasi_leaked_spans")
    )
    csg_audited_loss_ids = sorted(
        example_id
        for (example_id, method), fact_row in judged.items()
        if method == "critical_span_guard_extracted"
        and not_retained_facts(fact_row, examples[example_id])
    )

    return {
        "metadata": {
            "generated": date.today().isoformat(),
            "sample_version": args.sample_version,
            "sample_label": args.sample_label,
            "no_api_calls": True,
            "examples": len(sample_ids),
            "method_rows": len(sample_ids) * len(METHODS),
            "methods": METHODS,
            "source_files": {
                "benchmark": args.benchmark,
                "deterministic_judgments": args.scored,
                "fact_judgments": args.fact_judgments,
            },
            "audit_scope": (
                "Single-author/manual-style fixed subset audit derived from cached row-level evidence; "
                "not an independent multi-annotator study."
            ),
        },
        "summary": {
            "domain_counts": dict(domain_counts),
            "tag_counts": dict(tag_counts),
            "row_summary_by_method": {method: dict(counts) for method, counts in row_summary_by_method.items()},
            "label_counts_by_method": {method: dict(counts) for method, counts in label_counts_by_method.items()},
            "required_caveat_ids": {
                "strict_specificity": csg_audited_loss_ids,
                "residual_qi": csg_residual_ids,
            },
        },
        "examples": rows,
    }


def write_markdown(payload: dict, examples: dict[str, dict], out_path: str) -> None:
    lines = ["# Fixed Sample Manual Audit", ""]
    meta = payload["metadata"]
    summary = payload["summary"]
    lines.append(f"Generated: {meta['generated']}")
    lines.append("")
    lines.append(
        f"This is a fixed 30-example transparent subset audit for the {meta['sample_label']}. It uses existing deterministic metrics and cached fact-judge evidence only; no new API calls were made."
    )
    lines.append(
        "Scope caveat: this is a single-author/manual-style audit packet, not an independent multi-annotator study or inter-rater agreement result."
    )
    lines.append("")
    lines.append("## Fixed Sample")
    lines.append("")
    domain_text = ", ".join(f"{domain}={count}" for domain, count in sorted(summary["domain_counts"].items()))
    lines.append(
        f"- Fixed sample: {meta['examples']} examples ({domain_text}), all {len(METHODS)} methods per example."
    )
    lines.append(f"- Method rows audited: {meta['method_rows']}.")
    strict_ids = summary["required_caveat_ids"].get("strict_specificity", [])
    residual_ids = summary["required_caveat_ids"].get("residual_qi", [])
    lines.append(
        "- Required caveats included: strict-specificity/audited-loss rows "
        + (", ".join(f"`{example_id}`" for example_id in strict_ids) if strict_ids else "none")
        + "; residual-QI rows "
        + (", ".join(f"`{example_id}`" for example_id in residual_ids) if residual_ids else "none")
        + "."
    )
    lines.append(
        "- Selection rule: include foreground/caveat cases first, then deterministically fill each domain to 15 examples using direct leaks, QI retention, privacy-first utility loss, CSG caveats, exact-metric artifacts, and clean CSG controls."
    )
    lines.append("")
    lines.append("## Method-Row Summary")
    lines.append("")
    lines.append("| Method | Rows | Direct-leak rows | QI-hit rows | Audited fact-loss rows | Exact QA-failure rows | Exact-match artifact rows | Clean rows |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for method in METHODS:
        counts = defaultdict(int, summary["row_summary_by_method"].get(method, {}))
        lines.append(
            "| {method} | {rows} | {direct} | {qi} | {audit_loss} | {qa} | {artifact} | {clean_rows} |".format(
                method=method,
                rows=counts["rows"],
                direct=counts["direct_leak_rows"],
                qi=counts["qi_hit_rows"],
                audit_loss=counts["audited_fact_loss_rows"],
                qa=counts["exact_qa_failure_rows"],
                artifact=counts["exact_match_artifact_rows"],
                clean_rows=counts["clean_rows"],
            )
        )
    lines.append("")
    lines.append("## Selected Examples")
    lines.append("")
    lines.append("| Example | Domain | Selected because | CSG labels |")
    lines.append("|---|---|---|---|")
    for row in payload["examples"]:
        csg = next(method for method in row["methods"] if method["method"] == "critical_span_guard_extracted")
        lines.append(
            f"| `{row['id']}` | {row['domain']} | {one_line(row['selected_because'], width=180)} | {one_line(csg['labels'], width=120)} |"
        )
    lines.append("")
    lines.append("## Row-Level Audit")
    lines.append("")
    for row in payload["examples"]:
        example = examples[row["id"]]
        facts = [fact.get("fact", "") for fact in example.get("task_critical_facts", [])]
        qas = [f"{qa.get('q')} -> {qa.get('a')}" for qa in example.get("qa", [])]
        direct = [span.get("text", "") for span in example.get("private_spans", []) if span.get("identifier_type") == "DIRECT"]
        quasi = [span.get("text", "") for span in example.get("private_spans", []) if span.get("identifier_type") == "QUASI"]
        lines.append(f"### `{row['id']}` ({row['domain']})")
        lines.append("")
        lines.append(f"- Selected because: {one_line(row['selected_because'], width=260)}")
        lines.append(f"- Gold task facts: {one_line(facts, width=260)}")
        lines.append(f"- Gold QA: {one_line(qas, width=220)}")
        lines.append(f"- Gold direct identifiers: {one_line(direct, width=180)}")
        lines.append(f"- Gold quasi-identifiers: {one_line(quasi, width=180)}")
        lines.append("")
        lines.append("| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA | Labels | Not-retained audited facts |")
        lines.append("|---|---|---|---:|---:|---:|---|---|")
        for method in row["methods"]:
            lines.append(
                "| {method_name} | {direct_hits} | {qi_hits} | {exact:.3f} | {audited:.3f} | {qa:.3f} | {labels} | {not_retained} |".format(
                    method_name=method["method"],
                    direct_hits=one_line(method["direct_leaked_spans"], width=90),
                    qi_hits=one_line(method["quasi_leaked_spans"], width=90),
                    exact=method["exact_tcfr"],
                    audited=method["audited_tcfr"],
                    qa=method["qa_consistency"],
                    labels=one_line(method["labels"], width=140),
                    not_retained=one_line(method["not_retained_audited_facts"], width=160),
                )
            )
        lines.append("")
    lines.append("## Paper-Use Notes")
    lines.append("")
    lines.append(f"- This audit closes the plan-level transparent 20-50 example subset requirement for the current {meta['sample_label']} package.")
    lines.append("- For a full top-tier submission, the natural next step is a second independent annotator or adjudicated human labels on this fixed subset.")
    lines.append("- Keep exact cost/latency caveats separate: the n100 cache is complete, but early cache rows did not store provider usage or elapsed time.")
    lines.append("")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/benchmark.jsonl")
    parser.add_argument("--scored", default="data/processed/openai_judgments_n100.jsonl")
    parser.add_argument("--fact-judgments", default="data/processed/openai_fact_judgments_n100.jsonl")
    parser.add_argument("--out-md", default="results/fixed_sample_manual_audit_n100.md")
    parser.add_argument("--out-json", default="results/fixed_sample_manual_audit_n100.json")
    parser.add_argument("--sample-label", default="n100 promoted run")
    parser.add_argument("--sample-version", default="n100_fixed_30_examples_all_3_methods_v1")
    args = parser.parse_args()

    examples = {row["id"]: row for row in read_jsonl(args.benchmark)}
    scored = {(row["id"], row["method"]): row for row in read_jsonl(args.scored)}
    judged = {(row["id"], row["method"]): row for row in read_jsonl(args.fact_judgments)}
    sample_ids = select_sample(examples, scored, judged)
    payload = build_payload(sample_ids, examples, scored, judged, args)
    write_json(args.out_json, payload)
    write_markdown(payload, examples, args.out_md)
    print(f"wrote {args.out_md}")
    print(f"wrote {args.out_json}")


if __name__ == "__main__":
    main()
