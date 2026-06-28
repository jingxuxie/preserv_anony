"""Create audit and ablation reports from cached experiment outputs."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from textwrap import shorten

from io_utils import read_jsonl


METHOD_ORDER = [
    "generic_llm",
    "privacy_first_llm",
    "critical_span_guard_extracted",
]

ABLATION_ORDER = [
    "csg_draft",
    "csg_verified",
    "csg_verified_safety",
]


def load_json(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def metric(stats: dict, key: str) -> float:
    value = stats[key]
    if isinstance(value, dict):
        return float(value["mean"])
    return float(value)


def clean_text(text: object) -> str:
    """Remove control characters that can corrupt markdown rendering."""

    value = str(text)
    return "".join(ch for ch in value if ch in "\n\t" or ord(ch) >= 32)


def retained_status(judgment: dict, gold_fact: dict | None) -> bool:
    status = judgment.get("status")
    if status == "preserved":
        return True
    if status == "generalized_but_acceptable":
        return bool((gold_fact or {}).get("generalization_allowed"))
    return False


def status_counts(fact_row: dict | None, example: dict | None = None) -> Counter:
    counts: Counter = Counter()
    if not fact_row:
        return counts
    gold_facts = (example or {}).get("task_critical_facts", [])
    for judgment in fact_row.get("fact_judgments", []):
        status = judgment.get("status", "missing_status")
        if status == "generalized_but_acceptable":
            try:
                gold_fact = gold_facts[int(judgment.get("fact_index"))]
            except (IndexError, TypeError, ValueError):
                gold_fact = None
            if retained_status(judgment, gold_fact):
                counts["generalized_retained"] += 1
            else:
                counts["generalized_not_retained"] += 1
        else:
            counts[status] += 1
    return counts


def format_status_counts(counts: Counter) -> str:
    if not counts:
        return "NA"
    parts = []
    for key in ["preserved", "generalized_retained", "generalized_not_retained", "omitted", "contradicted"]:
        if counts.get(key):
            parts.append(f"{key}={counts[key]}")
    for key, value in sorted(counts.items()):
        if key not in {"preserved", "generalized_retained", "generalized_not_retained", "omitted", "contradicted"}:
            parts.append(f"{key}={value}")
    return ", ".join(parts) if parts else "NA"


def method_sort_key(method: str) -> tuple[int, str]:
    if method in METHOD_ORDER:
        return (METHOD_ORDER.index(method), method)
    if method in ABLATION_ORDER:
        return (ABLATION_ORDER.index(method), method)
    return (99, method)


def one_line(items: list[str], limit: int = 220) -> str:
    if not items:
        return "None"
    return shorten("; ".join(clean_text(item) for item in items), width=limit, placeholder=" ...")


def md_quote(text: str) -> list[str]:
    return [f"> {line}" if line else ">" for line in clean_text(text).splitlines()]


def write_ablation_table(summary_path: str, scored_path: str, out_path: str) -> None:
    summary = load_json(summary_path)
    scored = read_jsonl(scored_path)
    n_examples = next(iter(summary["overall"].values()))["n"] if summary.get("overall") else 0
    leak_counts = Counter(row["method"] for row in scored if row.get("direct_leaked_spans"))
    qi_rows = Counter(row["method"] for row in scored if row.get("quasi_leaked_spans"))
    final_qi_ids = sorted(
        row["id"]
        for row in scored
        if row["method"] == "csg_verified_safety" and row.get("quasi_leaked_spans")
    )

    lines = ["# Critical Span Guard Ablation", ""]
    lines.append(f"Cache-only ablation reconstructed from the {n_examples}-example non-oracle CSG run.")
    lines.append("")
    lines.append("| Stage | N | Direct leak | Rows with direct leaks | QI risk | Rows with QI hits | TCFR | QA consistency | Edit rate |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|---:|")
    for method in ABLATION_ORDER:
        stats = summary["overall"][method]
        lines.append(
            "| {method} | {n} | {direct:.3f} | {direct_rows} | {qi:.3f} | {qi_rows} | {tcfr:.3f} | {qa:.3f} | {edit:.3f} |".format(
                method=method,
                n=stats["n"],
                direct=metric(stats, "direct_identifier_leak"),
                direct_rows=leak_counts[method],
                qi=metric(stats, "quasi_identifier_risk"),
                qi_rows=qi_rows[method],
                tcfr=metric(stats, "tcfr"),
                qa=metric(stats, "qa_consistency"),
                edit=metric(stats, "edit_rate"),
            )
        )
    lines.append("")
    lines.append("## Domain split")
    lines.append("")
    lines.append("| Domain | Stage | N | Direct leak | QI risk | TCFR | QA consistency |")
    lines.append("|---|---|---:|---:|---:|---:|---:|")
    for domain in sorted(summary["by_domain"]):
        for method in ABLATION_ORDER:
            stats = summary["by_domain"][domain][method]
            lines.append(
                "| {domain} | {method} | {n} | {direct:.3f} | {qi:.3f} | {tcfr:.3f} | {qa:.3f} |".format(
                    domain=domain,
                    method=method,
                    n=stats["n"],
                    direct=metric(stats, "direct_identifier_leak"),
                    qi=metric(stats, "quasi_identifier_risk"),
                    tcfr=metric(stats, "tcfr"),
                    qa=metric(stats, "qa_consistency"),
                )
            )
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "- The verify/repair pass did not change this cached sample under deterministic scoring; draft and verified rows are numerically identical."
    )
    lines.append(
        "- The deterministic safety scrub plus legal-Article, case-label, detention-regime, and medication repair closes the remaining direct clinical leak, most synthetic clinical quasi-identifier hits, the sampled legal Article over-generalization, the clean quoted case-label leak, and one utility-irrelevant detention-regime label."
    )
    if final_qi_ids:
        ids = ", ".join(f"`{example_id}`" for example_id in final_qi_ids)
        lines.append(
            f"- {len(final_qi_ids)} legal examples remain flagged for quasi-identifiers after safety scrub ({ids}); these are legal statute/jurisdiction or offense-description details that overlap with the claim meaning, so they should be framed as frontier cases rather than blindly scrubbed."
        )
    else:
        lines.append(
            "- No CSG rows remain flagged for quasi-identifiers after safety scrub in this cached sample; this should still not be presented as a formal anonymization guarantee."
        )
    lines.append("")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def any_not_retained(fact_row: dict | None, example: dict | None) -> bool:
    if not fact_row or not example:
        return False
    gold_facts = example.get("task_critical_facts", [])
    for judgment in fact_row.get("fact_judgments", []):
        try:
            gold_fact = gold_facts[int(judgment.get("fact_index"))]
        except (IndexError, TypeError, ValueError):
            gold_fact = None
        if not retained_status(judgment, gold_fact):
            return True
    return False


def not_retained_facts(fact_row: dict | None, example: dict | None) -> list[str]:
    if not fact_row or not example:
        return []
    gold_facts = example.get("task_critical_facts", [])
    facts = []
    for judgment in fact_row.get("fact_judgments", []):
        try:
            gold_fact = gold_facts[int(judgment.get("fact_index"))]
        except (IndexError, TypeError, ValueError):
            gold_fact = None
        if not retained_status(judgment, gold_fact):
            facts.append(clean_text(judgment.get("gold_fact", judgment.get("fact", ""))))
    return facts


def write_error_taxonomy(benchmark_path: str, scored_path: str, fact_path: str, out_path: str) -> None:
    examples = {row["id"]: row for row in read_jsonl(benchmark_path)}
    scored = read_jsonl(scored_path)
    facts = {(row["id"], row["method"]): row for row in read_jsonl(fact_path)}
    methods = sorted({row["method"] for row in scored}, key=method_sort_key)
    n_examples = max(Counter(row["method"] for row in scored).values()) if scored else 0

    categories = [
        (
            "Direct identifier leak",
            "direct_leaked_spans is non-empty",
            lambda row, fact: bool(row.get("direct_leaked_spans")),
        ),
        (
            "Quasi-identifier retained",
            "quasi_leaked_spans is non-empty",
            lambda row, fact: bool(row.get("quasi_leaked_spans")),
        ),
        (
            "Exact critical fact omitted",
            "omitted_facts is non-empty under exact/alias matching",
            lambda row, fact: bool(row.get("omitted_facts")),
        ),
        (
            "QA answer changed",
            "failed_qa is non-empty",
            lambda row, fact: bool(row.get("failed_qa")),
        ),
        (
            "LLM-audited fact not retained",
            "fact judge marks at least one fact not retained after applying gold generalization rules",
            lambda row, fact: any_not_retained(fact, examples.get(row["id"])),
        ),
        (
            "LLM-audited contradiction",
            "fact judge marks at least one fact contradicted",
            lambda row, fact: any(j.get("status") == "contradicted" for j in (fact or {}).get("fact_judgments", [])),
        ),
        (
            "Likely exact-match undercount",
            "audited TCFR exceeds exact TCFR by at least 0.15",
            lambda row, fact: fact is not None and float(fact.get("audited_tcfr", 0.0)) - float(row.get("tcfr", 0.0)) >= 0.15,
        ),
    ]

    counts: dict[str, Counter] = {name: Counter() for name, _, _ in categories}
    domains: dict[str, Counter] = {name: Counter() for name, _, _ in categories}
    for row in scored:
        fact = facts.get((row["id"], row["method"]))
        for name, _, predicate in categories:
            if predicate(row, fact):
                counts[name][row["method"]] += 1
                domains[name][f"{row['method']}:{row['domain']}"] += 1

    lines = ["# Error Taxonomy and Current Counts", ""]
    lines.append(
        f"Counts are row counts over the {n_examples}-example cached LLM run. Treat them as audit triage, not final paper statistics."
    )
    lines.append("")
    header = "| Error type | Operational signal | " + " | ".join(methods) + " |"
    sep = "|---|---|" + "|".join(["---:"] * len(methods)) + "|"
    lines.append(header)
    lines.append(sep)
    for name, signal, _ in categories:
        values = " | ".join(str(counts[name][method]) for method in methods)
        lines.append(f"| {name} | {signal} | {values} |")
    lines.append("")
    lines.append("## Domain notes")
    lines.append("")
    for name, _, _ in categories:
        parts = []
        for method in methods:
            clinical = domains[name][f"{method}:clinical"]
            legal = domains[name][f"{method}:legal"]
            if clinical or legal:
                parts.append(f"{method}: clinical={clinical}, legal={legal}")
        if parts:
            lines.append(f"- {name}: " + "; ".join(parts))
    lines.append("")
    lines.append("## Paper-facing interpretation")
    lines.append("")
    lines.append(
        "- Direct leaks in this run are concentrated in generic LLM legal outputs, especially legal application numbers."
    )
    lines.append(
        "- Privacy-first prompting nearly eliminates direct leaks but frequently removes task-critical clinical and legal facts."
    )
    lines.append(
        "- Critical Span Guard has the best current privacy-utility balance, but remaining legal quasi-identifier cases and exact-match undercounts should be manually audited before submission."
    )
    lines.append(
        "- The exact TCFR scorer is intentionally conservative; use the LLM-audited table and manual examples to avoid overclaiming deterministic-string failures."
    )
    lines.append("")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def selected_examples(scored: list[dict], facts: dict[tuple[str, str], dict]) -> list[tuple[str, str, list[str]]]:
    by_key = {(row["id"], row["method"]): row for row in scored}
    selected: dict[str, tuple[str, list[str]]] = {}

    def add(example_id: str, reason: str) -> None:
        if example_id not in selected:
            selected[example_id] = (reason, [])
        selected[example_id][1].append(reason)

    generic_leaks = [
        row
        for row in scored
        if row["method"] == "generic_llm" and row.get("direct_leaked_spans")
    ]
    for row in sorted(generic_leaks, key=lambda r: (-len(r["direct_leaked_spans"]), r["id"]))[:3]:
        add(row["id"], "generic direct identifier leak")

    for domain in ["clinical", "legal"]:
        privacy_rows = [
            row
            for row in scored
            if row["method"] == "privacy_first_llm"
            and row["domain"] == domain
            and (row.get("omitted_facts") or row.get("failed_qa"))
        ]
        if privacy_rows:
            row = sorted(privacy_rows, key=lambda r: (r["tcfr"], r["qa_consistency"], r["id"]))[0]
            add(row["id"], f"privacy-first {domain} utility loss")

    csg_rows = [row for row in scored if row["method"] == "critical_span_guard_extracted"]
    if csg_rows:
        row = sorted(csg_rows, key=lambda r: (r["tcfr"], r["qa_consistency"], r["id"]))[0]
        add(row["id"], "lowest exact-TCFR CSG case")

    for row in csg_rows:
        fact = facts.get((row["id"], row["method"]))
        if fact and float(fact.get("audited_tcfr", 0.0)) - float(row.get("tcfr", 0.0)) >= 0.15:
            add(row["id"], "CSG exact-match undercount candidate")
            break

    csg_by_id = {row["id"]: row for row in csg_rows}
    privacy_by_id = {row["id"]: row for row in scored if row["method"] == "privacy_first_llm"}
    contrast = []
    for example_id, csg_row in csg_by_id.items():
        privacy_row = privacy_by_id.get(example_id)
        if not privacy_row:
            continue
        contrast.append((csg_row["tcfr"] - privacy_row["tcfr"], csg_row["qa_consistency"] - privacy_row["qa_consistency"], example_id))
    if contrast:
        _, _, example_id = sorted(contrast, reverse=True)[0]
        add(example_id, "largest CSG vs privacy-first utility gap")

    generic_by_id = {row["id"]: row for row in scored if row["method"] == "generic_llm"}
    leak_contrast = []
    for example_id, generic_row in generic_by_id.items():
        csg_row = by_key.get((example_id, "critical_span_guard_extracted"))
        if generic_row.get("direct_leaked_spans") and csg_row and not csg_row.get("direct_leaked_spans"):
            leak_contrast.append((len(generic_row["direct_leaked_spans"]), example_id))
    if leak_contrast:
        _, example_id = sorted(leak_contrast, reverse=True)[0]
        add(example_id, "CSG closes generic direct leak on same example")

    out = []
    for example_id, (_, reasons) in selected.items():
        domain = by_key.get((example_id, METHOD_ORDER[0]), {}).get("domain", "")
        out.append((example_id, domain, sorted(set(reasons))))
    return sorted(out, key=lambda item: (item[1], item[0]))[:12]


def write_manual_audit_package(
    benchmark_path: str,
    outputs_path: str,
    scored_path: str,
    fact_path: str,
    out_path: str,
) -> None:
    examples = {row["id"]: row for row in read_jsonl(benchmark_path)}
    outputs = {(row["id"], row["method"]): row for row in read_jsonl(outputs_path)}
    scored = read_jsonl(scored_path)
    score_by_key = {(row["id"], row["method"]): row for row in scored}
    facts = {(row["id"], row["method"]): row for row in read_jsonl(fact_path)}
    candidates = selected_examples(scored, facts)
    n_examples = max(Counter(row["method"] for row in scored).values()) if scored else 0

    lines = ["# Manual Audit Package", ""]
    lines.append(f"This package selects high-signal rows from the cached {n_examples}-example LLM run for human review.")
    lines.append("")
    lines.append("## Audit checklist")
    lines.append("")
    lines.append("- Privacy: did the output retain a direct identifier, case number, institution, exact age, rare occupation, or other re-identification cue?")
    lines.append("- Utility: are diagnosis/claim, article/statute, dose/value, outcome, chronology, and downstream answer still recoverable?")
    lines.append("- Faithfulness: did anonymization introduce a new fact or contradict a task-critical fact?")
    lines.append("- Scorer disagreement: does deterministic exact matching undercount a faithful paraphrase?")
    lines.append("")
    lines.append("## Candidate index")
    lines.append("")
    lines.append("| Example | Domain | Why selected |")
    lines.append("|---|---|---|")
    for example_id, domain, reasons in candidates:
        lines.append(f"| {example_id} | {domain} | {'; '.join(reasons)} |")
    lines.append("")

    for example_id, domain, reasons in candidates:
        ex = examples[example_id]
        lines.append(f"## {example_id} ({domain})")
        lines.append("")
        lines.append("Selected because: " + "; ".join(reasons))
        lines.append("")
        lines.append("### Original")
        lines.append("")
        lines.extend(md_quote(ex["text"]))
        lines.append("")
        direct_spans = [span["text"] for span in ex["private_spans"] if span.get("identifier_type") == "DIRECT"]
        quasi_spans = [span["text"] for span in ex["private_spans"] if span.get("identifier_type") == "QUASI"]
        critical_facts = [fact["fact"] for fact in ex["task_critical_facts"]]
        qa_pairs = [f"{qa['q']} -> {qa['a']}" for qa in ex.get("qa", [])]
        lines.append(f"- Gold direct/private spans: {one_line(direct_spans)}")
        lines.append(f"- Gold quasi-identifiers: {one_line(quasi_spans)}")
        lines.append(f"- Gold task-critical facts: {one_line(critical_facts, limit=300)}")
        lines.append(f"- Gold QA: {one_line(qa_pairs, limit=260)}")
        lines.append("")

        lines.append("### Method summary")
        lines.append("")
        lines.append("| Method | Direct leaks | QI hits | Exact TCFR | Audited TCFR | QA consistency | Fact-judge statuses |")
        lines.append("|---|---|---|---:|---:|---:|---|")
        for method in METHOD_ORDER:
            score = score_by_key[(example_id, method)]
            fact = facts.get((example_id, method))
            audited = "NA" if not fact else f"{float(fact['audited_tcfr']):.3f}"
            lines.append(
                "| {method} | {direct} | {qi} | {tcfr:.3f} | {audited} | {qa:.3f} | {statuses} |".format(
                    method=method,
                    direct=one_line(score.get("direct_leaked_spans", []), limit=110),
                    qi=one_line(score.get("quasi_leaked_spans", []), limit=130),
                    tcfr=float(score["tcfr"]),
                    audited=audited,
                    qa=float(score["qa_consistency"]),
                    statuses=format_status_counts(status_counts(fact, ex)),
                )
            )
        lines.append("")
        for method in METHOD_ORDER:
            score = score_by_key[(example_id, method)]
            out = outputs[(example_id, method)]
            fact = facts.get((example_id, method))
            lines.append(f"### {method}")
            lines.append("")
            lines.extend(md_quote(out["anonymized_text"]))
            lines.append("")
            lines.append(f"- Omitted facts by exact scorer: {one_line(score.get('omitted_facts', []), limit=260)}")
            lines.append(f"- Contradicted facts by exact scorer: {one_line(score.get('contradicted_facts', []), limit=220)}")
            lines.append(f"- Failed QA by exact scorer: {one_line(score.get('failed_qa', []), limit=220)}")
            if fact:
                omitted = not_retained_facts(fact, ex)
                contradicted = [
                    clean_text(j.get("gold_fact", j.get("fact", "")))
                    for j in fact.get("fact_judgments", [])
                    if j.get("status") == "contradicted"
                ]
                lines.append(f"- Not-retained facts by LLM judge: {one_line(omitted, limit=260)}")
                lines.append(f"- Contradicted facts by LLM judge: {one_line(contradicted, limit=220)}")
            lines.append("")

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    Path(out_path).write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/benchmark.jsonl")
    parser.add_argument("--outputs", default="data/processed/openai_anonymized_outputs.jsonl")
    parser.add_argument("--scored", default="data/processed/openai_judgments.jsonl")
    parser.add_argument("--fact-judgments", default="data/processed/openai_fact_judgments.jsonl")
    parser.add_argument("--ablation-summary", default="results/csg_ablation_summary.json")
    parser.add_argument("--ablation-scored", default="data/processed/csg_ablation_judgments.jsonl")
    parser.add_argument("--audit-out", default="results/manual_audit_package.md")
    parser.add_argument("--taxonomy-out", default="results/error_taxonomy.md")
    parser.add_argument("--ablation-out", default="results/csg_ablation_table.md")
    args = parser.parse_args()

    write_ablation_table(args.ablation_summary, args.ablation_scored, args.ablation_out)
    write_error_taxonomy(args.benchmark, args.scored, args.fact_judgments, args.taxonomy_out)
    write_manual_audit_package(args.benchmark, args.outputs, args.scored, args.fact_judgments, args.audit_out)
    print(f"wrote {args.ablation_out}")
    print(f"wrote {args.taxonomy_out}")
    print(f"wrote {args.audit_out}")


if __name__ == "__main__":
    main()
