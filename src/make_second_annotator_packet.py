"""Create a blinded second-annotator packet for a fixed audit subset.

The packet hides method names and excludes existing scores/labels. It is meant
for independent human annotation, not as completed annotation evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

from io_utils import read_jsonl, write_json, write_jsonl


METHODS = ["generic_llm", "privacy_first_llm", "critical_span_guard_extracted"]
VARIANT_CODES = ["A", "B", "C"]
DEFAULT_SAMPLE_VERSION = "n100_fixed_30_second_annotator_v1"


def method_order(example_id: str, sample_version: str) -> list[str]:
    return sorted(
        METHODS,
        key=lambda method: hashlib.sha256(f"{sample_version}:{example_id}:{method}".encode("utf-8")).hexdigest(),
    )


def clean(text: object) -> str:
    value = str(text)
    value = value.translate({ord(ch): " " for ch in "\x00\x11\x17\x7f"})
    return "".join(ch for ch in value if ch in "\n\t" or ord(ch) >= 32)


def private_span_texts(example: dict, identifier_type: str) -> list[str]:
    return [
        clean(span.get("text", ""))
        for span in example.get("private_spans", [])
        if span.get("identifier_type") == identifier_type
    ]


def task_facts(example: dict) -> list[dict]:
    facts = []
    for index, fact in enumerate(example.get("task_critical_facts", [])):
        facts.append(
            {
                "fact_index": index,
                "fact": clean(fact.get("fact", "")),
                "type": fact.get("type", ""),
                "generalization_allowed": bool(fact.get("generalization_allowed", False)),
                "acceptable_generalizations": fact.get("acceptable_generalizations", []),
            }
        )
    return facts


def qa_pairs(example: dict) -> list[dict]:
    return [
        {
            "question": clean(qa.get("q", "")),
            "answer": clean(qa.get("a", "")),
            "answer_aliases": [clean(alias) for alias in qa.get("answer_aliases", [])],
        }
        for qa in example.get("qa", [])
    ]


def build_packet_rows(
    sample: dict,
    examples: dict[str, dict],
    outputs: dict[tuple[str, str], dict],
    sample_version: str,
) -> tuple[list[dict], dict]:
    rows: list[dict] = []
    answer_key: dict[str, object] = {
        "sample_version": sample_version,
        "do_not_share_with_annotator": True,
        "description": "Maps blinded variant codes to method names for reconciliation after annotation.",
        "examples": {},
    }
    for sample_row in sample["examples"]:
        example_id = sample_row["id"]
        example = examples[example_id]
        mapping = dict(zip(VARIANT_CODES, method_order(example_id, sample_version)))
        answer_key["examples"][example_id] = mapping
        for code in VARIANT_CODES:
            method = mapping[code]
            output = outputs[(example_id, method)]
            rows.append(
                {
                    "sample_version": sample_version,
                    "example_id": example_id,
                    "domain": example.get("domain"),
                    "source": example.get("source"),
                    "variant_code": code,
                    "original_text": clean(example.get("text", "")),
                    "transformed_text": clean(output.get("anonymized_text", "")),
                    "gold_direct_identifiers": private_span_texts(example, "DIRECT"),
                    "gold_quasi_identifiers": private_span_texts(example, "QUASI"),
                    "gold_task_facts": task_facts(example),
                    "gold_qa_pairs": qa_pairs(example),
                    "annotation_fields": {
                        "direct_identifier_retained": "blank",
                        "quasi_identifier_retained": "blank",
                        "task_fact_retention": "blank",
                        "qa_answerability": "blank",
                        "contradiction_or_hallucination": "blank",
                        "privacy_utility_overlap": "blank",
                        "notes": "blank",
                    },
                }
            )
    return rows, answer_key


def write_form(rows: list[dict], out_csv: str) -> None:
    fieldnames = [
        "example_id",
        "domain",
        "variant_code",
        "direct_identifier_retained",
        "quasi_identifier_retained",
        "task_fact_retention",
        "qa_answerability",
        "contradiction_or_hallucination",
        "privacy_utility_overlap",
        "notes",
    ]
    path = Path(out_csv)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "example_id": row["example_id"],
                    "domain": row["domain"],
                    "variant_code": row["variant_code"],
                    "direct_identifier_retained": "",
                    "quasi_identifier_retained": "",
                    "task_fact_retention": "",
                    "qa_answerability": "",
                    "contradiction_or_hallucination": "",
                    "privacy_utility_overlap": "",
                    "notes": "",
                }
            )


def write_rubric(rows: list[dict], answer_key: dict, out_md: str, sample_label: str, packet_jsonl: str, form_csv: str, answer_key_path: str) -> None:
    domains = Counter(row["domain"] for row in rows if row["variant_code"] == "A")
    examples = sorted({row["example_id"] for row in rows})
    lines = [f"# Second-Annotator Packet for Fixed {sample_label} Audit", ""]
    lines.append(f"This packet is prepared for an independent annotation pass on the fixed {sample_label} audit subset.")
    lines.append("")
    lines.append("## Scope")
    lines.append("")
    lines.append(f"- Sample version: `{answer_key['sample_version']}`.")
    lines.append(f"- Examples: {len(examples)} ({', '.join(f'{k}={v}' for k, v in sorted(domains.items()))}).")
    lines.append(f"- Variant rows: {len(rows)}; each example has blinded variants `A`, `B`, and `C`.")
    lines.append("- Method names, existing metric scores, fact-judge labels, and prior manual decisions are intentionally excluded from the annotator packet.")
    lines.append("- The answer key is separate and should not be shared until annotation is complete.")
    lines.append("")
    lines.append("## Files")
    lines.append("")
    lines.append(f"- `{packet_jsonl}`: full blinded packet with original text, transformed text, gold spans, task facts, and QA.")
    lines.append(f"- `{form_csv}`: blank row-level annotation form.")
    lines.append(f"- `{answer_key_path}`: method mapping for post-annotation reconciliation only.")
    lines.append("")
    lines.append("## Annotation Rubric")
    lines.append("")
    lines.append("For each row, compare `transformed_text` against `original_text`, gold privacy spans, task facts, and QA pairs.")
    lines.append("")
    lines.append("| Field | Allowed values | Guidance |")
    lines.append("|---|---|---|")
    lines.append("| `direct_identifier_retained` | `no`, `yes`, `uncertain` | Mark `yes` if a listed direct identifier or obvious direct alias remains. |")
    lines.append("| `quasi_identifier_retained` | `no`, `yes`, `uncertain` | Mark `yes` if a listed quasi-identifier, rare occupation/location/attribute, exact date, or close equivalent remains. |")
    lines.append("| `task_fact_retention` | `all`, `minor_loss`, `major_loss`, `uncertain` | `all` means all task facts are recoverable, including accepted generalizations. `major_loss` means at least one answer-critical fact is not recoverable. |")
    lines.append("| `qa_answerability` | `all`, `some`, `none`, `uncertain` | Decide whether the provided questions can still be answered from the transformed text. |")
    lines.append("| `contradiction_or_hallucination` | `no`, `yes`, `uncertain` | Mark `yes` if the transformed text changes a fact or introduces unsupported task-relevant content. |")
    lines.append("| `privacy_utility_overlap` | `no`, `yes`, `uncertain` | Mark `yes` when a retained privacy-sensitive detail appears necessary for the task fact or QA target. |")
    lines.append("| `notes` | free text | Briefly cite the retained/leaked span or lost fact. |")
    lines.append("")
    lines.append("## Reconciliation Plan")
    lines.append("")
    lines.append(f"After annotation, join the completed CSV with `{answer_key_path}` by `example_id` and `variant_code`. Report agreement against the current single-author/manual-style labels separately from deterministic metrics. Do not claim inter-rater agreement until this form is completed by a second annotator.")
    lines.append("")
    lines.append("## Blinded Variant Index")
    lines.append("")
    lines.append("| Example | Domain | Variants |")
    lines.append("|---|---|---|")
    for example_id in examples:
        domain = next(row["domain"] for row in rows if row["example_id"] == example_id)
        variants = ", ".join(sorted(answer_key["examples"][example_id]))
        lines.append(f"| `{example_id}` | {domain} | {variants} |")
    lines.append("")
    Path(out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(out_md).write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/benchmark.jsonl")
    parser.add_argument("--outputs", default="data/processed/openai_anonymized_outputs_n100.jsonl")
    parser.add_argument("--fixed-audit-json", default="results/fixed_sample_manual_audit_n100.json")
    parser.add_argument("--packet-jsonl", default="data/processed/second_annotator_packet_n100.jsonl")
    parser.add_argument("--form-csv", default="results/second_annotator_form_n100.csv")
    parser.add_argument("--answer-key", default="results/second_annotator_answer_key_n100.json")
    parser.add_argument("--rubric-md", default="results/second_annotator_rubric_n100.md")
    parser.add_argument("--sample-label", default="n100")
    parser.add_argument("--sample-version", default=DEFAULT_SAMPLE_VERSION)
    args = parser.parse_args()

    with open(args.fixed_audit_json, encoding="utf-8") as f:
        sample = json.load(f)
    examples = {row["id"]: row for row in read_jsonl(args.benchmark)}
    outputs = {(row["id"], row["method"]): row for row in read_jsonl(args.outputs)}
    rows, answer_key = build_packet_rows(sample, examples, outputs, args.sample_version)

    write_jsonl(args.packet_jsonl, rows)
    write_form(rows, args.form_csv)
    write_json(args.answer_key, answer_key)
    write_rubric(rows, answer_key, args.rubric_md, args.sample_label, args.packet_jsonl, args.form_csv, args.answer_key)
    print(f"wrote {args.packet_jsonl}")
    print(f"wrote {args.form_csv}")
    print(f"wrote {args.answer_key}")
    print(f"wrote {args.rubric_md}")


if __name__ == "__main__":
    main()
