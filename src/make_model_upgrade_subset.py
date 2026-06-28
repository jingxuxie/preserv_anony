"""Select a small stronger-model anonymization sanity-check subset.

The subset is drawn from the existing GPT-5.5 external-audit manifest so the
current low-cost outputs already have GPT-5.5 fact-judge labels. This keeps the
model-upgrade screen bounded and avoids extra baseline judge calls.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from io_utils import read_jsonl, write_json, write_jsonl


def add_rows(rows: list[dict], selected: list[dict], selected_ids: set[str], count: int, bucket: str) -> None:
    for row in rows:
        if len([item for item in selected if item["screen_bucket"] == bucket]) >= count:
            return
        if row["id"] in selected_ids:
            continue
        item = dict(row)
        item["screen_bucket"] = bucket
        selected.append(item)
        selected_ids.add(row["id"])


def has_reason(row: dict, reason: str) -> bool:
    return reason in set(row.get("selection_reasons", []))


def select_hard_rows(rows: list[dict], count: int) -> list[dict]:
    """Force coverage of CSG privacy, CSG utility, and generic stress cases."""

    selected: list[dict] = []
    selected_ids: set[str] = set()

    def add_first(candidates: list[dict]) -> None:
        for row in candidates:
            if row["id"] not in selected_ids:
                selected.append(row)
                selected_ids.add(row["id"])
                return

    csg_loss = [row for row in rows if has_reason(row, "CSG audited fact loss")]
    csg_residual = [row for row in rows if has_reason(row, "residual CSG QI risk")]
    generic_stress = [
        row
        for row in rows
        if has_reason(row, "high privacy-utility stress score") or has_reason(row, "generic direct identifier leak")
    ]
    for bucket in [csg_loss, csg_residual, generic_stress]:
        add_first(bucket)
        if len(selected) >= count:
            return selected

    for row in rows:
        if len(selected) >= count:
            break
        if row["id"] not in selected_ids:
            selected.append(row)
            selected_ids.add(row["id"])
    return selected


def build(args: argparse.Namespace) -> None:
    manifest = read_jsonl(args.audit_manifest)
    hard = sorted(
        [row for row in manifest if row.get("bucket") == "hard"],
        key=lambda row: (-float(row.get("hard_score", 0.0)), row["id"]),
    )
    clinical = sorted(
        [row for row in manifest if row.get("domain") == "clinical" and row.get("bucket") != "hard"],
        key=lambda row: (-float(row.get("hard_score", 0.0)), row["id"]),
    )
    legal = sorted(
        [row for row in manifest if row.get("domain") == "legal" and row.get("bucket") != "hard"],
        key=lambda row: (-float(row.get("hard_score", 0.0)), row["id"]),
    )

    selected: list[dict] = []
    selected_ids: set[str] = set()
    for row in select_hard_rows(hard, args.hard_count):
        item = dict(row)
        item["screen_bucket"] = "hard"
        selected.append(item)
        selected_ids.add(row["id"])
    add_rows(clinical, selected, selected_ids, args.clinical_count, "clinical")
    add_rows(legal, selected, selected_ids, args.legal_count, "legal")
    if len(selected) != args.total_count:
        raise RuntimeError(f"selected {len(selected)} rows, expected {args.total_count}")

    for rank, row in enumerate(selected, start=1):
        row["model_upgrade_rank"] = rank
        row["selection_note"] = (
            "Selected from the existing GPT-5.5 external-audit subset for a bounded stronger-model anonymization screen."
        )

    with Path(args.ids_out).open("w", encoding="utf-8") as f:
        for row in selected:
            f.write(row["id"] + "\n")
    write_jsonl(args.manifest_out, selected)
    summary = summarize(selected)
    write_json(args.summary_out, summary)
    Path(args.report_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report_out).write_text(markdown_report(selected, summary), encoding="utf-8")
    print(f"wrote {len(selected)} ids to {args.ids_out}")
    print(f"wrote {args.report_out}")


def summarize(rows: list[dict]) -> dict:
    by_domain = Counter(row.get("domain") for row in rows)
    by_bucket = Counter(row.get("screen_bucket") for row in rows)
    reasons = Counter()
    for row in rows:
        reasons.update(row.get("selection_reasons", []))
    return {
        "n": len(rows),
        "by_domain": dict(sorted(by_domain.items())),
        "by_screen_bucket": dict(sorted(by_bucket.items())),
        "reason_counts": dict(sorted(reasons.items(), key=lambda item: (-item[1], item[0]))),
        "mean_hard_score": sum(float(row.get("hard_score", 0.0)) for row in rows) / len(rows) if rows else 0.0,
    }


def markdown_report(rows: list[dict], summary: dict) -> str:
    lines = ["# Model-Upgrade Sanity-Check Subset", ""]
    lines.append("This is a bounded subset for the optional GPT-5.5 anonymization screen.")
    lines.append("It is drawn from the existing GPT-5.5 external-audit subset so current low-cost outputs already have GPT-5.5 fact-judge labels.")
    lines.append("")
    lines.append("## Composition")
    lines.append("")
    lines.append(f"- Examples: {summary['n']}.")
    lines.append(f"- Mean hard score: {summary['mean_hard_score']:.3f}.")
    lines.append("")
    lines.append("| Group | Count |")
    lines.append("|---|---:|")
    for key, value in summary["by_screen_bucket"].items():
        lines.append(f"| screen_bucket={key} | {value} |")
    for key, value in summary["by_domain"].items():
        lines.append(f"| domain={key} | {value} |")
    lines.append("")
    lines.append("## Selection Reasons")
    lines.append("")
    lines.append("| Reason | Count |")
    lines.append("|---|---:|")
    for key, value in summary["reason_counts"].items():
        lines.append(f"| {key} | {value} |")
    lines.append("")
    lines.append("## IDs")
    lines.append("")
    lines.append("| Rank | ID | Domain | Screen bucket | Audit bucket | Reasons |")
    lines.append("|---:|---|---|---|---|---|")
    for row in rows:
        reasons = "; ".join(row.get("selection_reasons", []))
        lines.append(
            f"| {row['model_upgrade_rank']} | `{row['id']}` | {row['domain']} | {row['screen_bucket']} | {row.get('bucket')} | {reasons} |"
        )
    lines.append("")
    lines.append("Scope caveat: this subset is a fast screen, not a replacement for the promoted n150 headline or a full 30-example model-upgrade study.")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-manifest", default="data/processed/gpt55_audit_subset_stratified60.jsonl")
    parser.add_argument("--ids-out", default="data/processed/gpt55_model_upgrade_ids_n9.txt")
    parser.add_argument("--manifest-out", default="data/processed/gpt55_model_upgrade_subset_n9.jsonl")
    parser.add_argument("--summary-out", default="results/gpt55_model_upgrade_subset_n9.json")
    parser.add_argument("--report-out", default="results/gpt55_model_upgrade_subset_n9.md")
    parser.add_argument("--clinical-count", type=int, default=3)
    parser.add_argument("--legal-count", type=int, default=3)
    parser.add_argument("--hard-count", type=int, default=3)
    parser.add_argument("--total-count", type=int, default=9)
    args = parser.parse_args()
    build(args)


if __name__ == "__main__":
    main()
