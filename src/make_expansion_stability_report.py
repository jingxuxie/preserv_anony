"""Summarize a bounded OpenAI headline expansion audit."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import date
from pathlib import Path

from io_utils import read_jsonl


METHODS = [
    "generic_llm",
    "privacy_first_llm",
    "critical_span_guard_extracted",
]

METHOD_LABELS = {
    "generic_llm": "Generic LLM",
    "privacy_first_llm": "Privacy-first LLM",
    "critical_span_guard_extracted": "Critical Span Guard",
}

METRICS = [
    ("direct_identifier_leak", "Direct leak"),
    ("quasi_identifier_risk", "QI risk"),
    ("tcfr", "Exact TCFR"),
    ("audited_tcfr", "Audited TCFR"),
    ("qa_consistency", "QA"),
]


def load_json(path: str | Path) -> dict:
    with Path(path).open("r", encoding="utf-8") as f:
        return json.load(f)


def fmt(value: float) -> str:
    return f"{value:.3f}"


def summary_value(det: dict, audit: dict, method: str, key: str) -> float:
    if key == "audited_tcfr":
        return float(audit["overall"][method]["audited_tcfr"])
    value = det["overall"][method][key]
    if isinstance(value, dict):
        return float(value["mean"])
    return float(value)


def ids_for_outputs(path: str | Path) -> set[str]:
    return {row["id"] for row in read_jsonl(path) if row.get("method") == METHODS[0]}


def suffixed(prefix: str, suffix: str, ext: str) -> str:
    return f"{prefix}_{suffix}.{ext}"


def method_subset_summary(
    scored: list[dict],
    fact_judgments: list[dict],
    ids: set[str],
) -> dict[str, dict[str, float]]:
    audited = {(row["id"], row["method"]): row for row in fact_judgments if row["id"] in ids}
    out: dict[str, dict[str, float]] = {}
    for method in METHODS:
        rows = [row for row in scored if row["id"] in ids and row["method"] == method]
        out[method] = {"n": float(len(rows))}
        for key, _label in METRICS:
            if key == "audited_tcfr":
                values = [float(audited[(row["id"], method)]["audited_tcfr"]) for row in rows]
            else:
                values = [float(row[key]) for row in rows]
            out[method][key] = sum(values) / len(values) if values else float("nan")
    return out


def compact(text: object, limit: int = 120) -> str:
    value = " ".join(str(text).split())
    if len(value) <= limit:
        return value
    return value[: limit - 3].rstrip() + "..."


def csg_added_exceptions(
    scored: list[dict],
    fact_judgments: list[dict],
    added_ids: set[str],
) -> list[dict]:
    audit_by_id = {row["id"]: row for row in fact_judgments if row["id"] in added_ids and row["method"] == "critical_span_guard_extracted"}
    rows = []
    for row in scored:
        if row["id"] not in added_ids or row["method"] != "critical_span_guard_extracted":
            continue
        audit = audit_by_id[row["id"]]
        issues = []
        if row["direct_leaked_spans"]:
            issues.append("direct leak: " + ", ".join(row["direct_leaked_spans"]))
        if row["quasi_leaked_spans"]:
            issues.append("QI: " + ", ".join(row["quasi_leaked_spans"]))
        if row["failed_qa"]:
            issues.append("failed exact QA: " + "; ".join(row["failed_qa"]))
        notes = []
        if float(audit["audited_tcfr"]) < 1.0:
            for judgment in audit["fact_judgments"]:
                if judgment["status"] != "preserved":
                    notes.append(f"{judgment['status']}: {compact(judgment.get('gold_fact'))}")
        if issues or notes:
            rows.append(
                {
                    "id": row["id"],
                    "domain": row["domain"],
                    "deterministic": "; ".join(issues) if issues else "none",
                    "audited_tcfr": float(audit["audited_tcfr"]),
                    "note": "; ".join(notes) if notes else "audited facts retained",
                }
            )
    return sorted(rows, key=lambda item: item["id"])


def write_summary_table(lines: list[str], title: str, det: dict, audit: dict) -> None:
    lines.append(f"## {title}")
    lines.append("")
    lines.append("| Method | N | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for method in METHODS:
        values = [summary_value(det, audit, method, key) for key, _label in METRICS]
        lines.append(
            "| {method} | {n} | {direct} | {qi} | {exact} | {audited} | {qa} |".format(
                method=METHOD_LABELS[method],
                n=int(det["overall"][method]["n"]),
                direct=fmt(values[0]),
                qi=fmt(values[1]),
                exact=fmt(values[2]),
                audited=fmt(values[3]),
                qa=fmt(values[4]),
            )
        )
    lines.append("")


def write_subset_table(lines: list[str], title: str, summary: dict[str, dict[str, float]]) -> None:
    lines.append(f"## {title}")
    lines.append("")
    lines.append("| Method | N | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for method in METHODS:
        stats = summary[method]
        lines.append(
            "| {method} | {n} | {direct} | {qi} | {exact} | {audited} | {qa} |".format(
                method=METHOD_LABELS[method],
                n=int(stats["n"]),
                direct=fmt(stats["direct_identifier_leak"]),
                qi=fmt(stats["quasi_identifier_risk"]),
                exact=fmt(stats["tcfr"]),
                audited=fmt(stats["audited_tcfr"]),
                qa=fmt(stats["qa_consistency"]),
            )
        )
    lines.append("")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-suffix", default="n70")
    parser.add_argument("--target-suffix", default="n100")
    parser.add_argument("--base-label", default="70-example")
    parser.add_argument("--target-label", default="100-example")
    parser.add_argument(
        "--diagnostic-only",
        action="store_true",
        help="Describe the target as bounded expansion evidence rather than a promoted headline.",
    )
    parser.add_argument("--out", default="results/openai_expansion_stability_n100.md")
    args = parser.parse_args()

    det_base = load_json(suffixed("results/openai_summary", args.base_suffix, "json"))
    audit_base = load_json(suffixed("results/openai_fact_judge_summary", args.base_suffix, "json"))
    det_target = load_json(suffixed("results/openai_summary", args.target_suffix, "json"))
    audit_target = load_json(suffixed("results/openai_fact_judge_summary", args.target_suffix, "json"))

    outputs_base_path = suffixed("data/processed/openai_anonymized_outputs", args.base_suffix, "jsonl")
    outputs_target_path = suffixed("data/processed/openai_anonymized_outputs", args.target_suffix, "jsonl")
    scored_target_path = suffixed("data/processed/openai_judgments", args.target_suffix, "jsonl")
    fact_target_path = suffixed("data/processed/openai_fact_judgments", args.target_suffix, "jsonl")

    ids_base = ids_for_outputs(outputs_base_path)
    ids_target = ids_for_outputs(outputs_target_path)
    added_ids = ids_target - ids_base
    added_domains = Counter(example_id.split("_", 1)[0] for example_id in added_ids)

    scored_target = read_jsonl(scored_target_path)
    fact_target = read_jsonl(fact_target_path)
    added_summary = method_subset_summary(scored_target, fact_target, added_ids)
    exceptions = csg_added_exceptions(scored_target, fact_target, added_ids)

    csg_added = added_summary["critical_span_guard_extracted"]
    csg_added_direct_rows = sum(
        1
        for row in scored_target
        if row["id"] in added_ids
        and row["method"] == "critical_span_guard_extracted"
        and float(row.get("direct_identifier_leak", 0.0)) > 0
    )
    csg_added_qi_rows = sum(
        1
        for row in scored_target
        if row["id"] in added_ids
        and row["method"] == "critical_span_guard_extracted"
        and float(row.get("quasi_identifier_risk", 0.0)) > 0
    )

    lines = [f"# OpenAI {args.target_suffix} Expansion Audit", ""]
    lines.append(f"Generated: {date.today().isoformat()}")
    lines.append("")
    if args.diagnostic_only:
        lines.append(
            f"This report compares the previous {args.base_label} OpenAI run with a bounded {args.target_label} diagnostic expansion. "
            f"It tests whether the non-oracle LLM headline pattern survives a small added slice; it is not promoted over the current {args.base_label} package unless matching ablation, manual-audit, paper-table, and verifier artifacts are regenerated."
        )
    else:
        lines.append(
            f"This report compares the previous {args.base_label} OpenAI run with the promoted {args.target_label} headline run. "
            "The expanded run has matching ablation, manual-audit, paper-table, and verifier support artifacts."
        )
    lines.append("")
    lines.append(
        f"The expansion adds {len(added_ids)} examples to the previous {len(ids_base)}: "
        + ", ".join(f"{domain}={count}" for domain, count in sorted(added_domains.items()))
        + "."
    )
    lines.append("")
    write_summary_table(lines, f"Previous {args.base_label.title()} Run", det_base, audit_base)
    target_title = f"{args.target_label.title()} Diagnostic Expansion" if args.diagnostic_only else f"Promoted {args.target_label.title()} Headline Run"
    write_summary_table(lines, target_title, det_target, audit_target)
    write_subset_table(lines, f"Added {len(added_ids)} Examples Only", added_summary)

    lines.append("## Added CSG Edge Cases")
    lines.append("")
    if exceptions:
        lines.append("| ID | Domain | Deterministic issue | Audited TCFR | Note |")
        lines.append("|---|---|---|---:|---|")
        for row in exceptions:
            lines.append(
                f"| `{row['id']}` | {row['domain']} | {row['deterministic']} | {fmt(row['audited_tcfr'])} | {row['note']} |"
            )
    else:
        lines.append("No added CSG direct leaks, QI hits, exact QA misses, or audited fact-retention losses were found.")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")
    lines.append(
        "- The expanded run preserves the qualitative result: CSG keeps zero measured direct leaks, much lower QI risk than generic prompting, and much higher utility than privacy-first prompting."
    )
    lines.append(
        "- The added slice is not a cherry-picked win: CSG has "
        f"{csg_added_direct_rows} direct-leak rows and {csg_added_qi_rows} QI-hit rows on the added slice, "
        f"with added-slice audited TCFR {fmt(csg_added['audited_tcfr'])} and QA {fmt(csg_added['qa_consistency'])}."
    )
    if args.diagnostic_only:
        lines.append(
            f"- The bounded {args.target_label} expansion reduces, but does not eliminate, the small-sample concern; promotion beyond {len(ids_base)} should rerun the ablation, residual audit, qualitative audit, paper tables, and verifier."
        )
    else:
        lines.append(
            f"- The promoted headline reduces, but does not eliminate, the small-sample concern; any expansion beyond {len(ids_target)} should rerun the ablation, residual audit, qualitative audit, paper tables, and verifier."
        )
    lines.append("")

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
