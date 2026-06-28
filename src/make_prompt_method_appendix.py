"""Generate a prompt and method appendix, with drift checks against runner code."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import run_openai_methods


OUT_PATH = Path("results/prompt_method_appendix.md")

PROMPTS = [
    {
        "name": "Generic LLM anonymizer",
        "path": Path("prompts/generic_anonymizer.txt"),
        "constant": "GENERIC_PROMPT",
        "role": "Non-oracle baseline prompt.",
    },
    {
        "name": "Privacy-first LLM anonymizer",
        "path": Path("prompts/privacy_first_anonymizer.txt"),
        "constant": "PRIVACY_FIRST_PROMPT",
        "role": "Conservative non-oracle baseline prompt.",
    },
    {
        "name": "CSG extraction prompt",
        "path": Path("prompts/extract_privacy_and_facts.txt"),
        "constant": "EXTRACT_PRIVACY_AND_FACTS_PROMPT",
        "role": "Non-oracle extraction of privacy spans and task-critical facts.",
    },
    {
        "name": "CSG anonymization prompt",
        "path": Path("prompts/critical_span_guard_extracted.txt"),
        "constant": "CSG_EXTRACTED_PROMPT",
        "role": "Non-oracle anonymization using extracted structures.",
    },
    {
        "name": "CSG verify/repair prompt",
        "path": Path("prompts/verify_repair.txt"),
        "constant": "CSG_VERIFY_REPAIR_PROMPT",
        "role": "Verifier prompt used before deterministic safety/repair.",
    },
    {
        "name": "Gold-prompt CSG diagnostic",
        "path": Path("prompts/critical_span_guard_goldprompt.txt"),
        "constant": "CSG_GOLD_PROMPT",
        "role": "Gold-informed diagnostic prompt, not the headline method.",
    },
]

PLACEHOLDER_NORMALIZATION = {
    "text": "TEXT",
    "TEXT": "TEXT",
    "original_text": "ORIGINAL_TEXT",
    "ORIGINAL_TEXT": "ORIGINAL_TEXT",
    "anonymized_text": "ANONYMIZED_TEXT",
    "ANONYMIZED_TEXT": "ANONYMIZED_TEXT",
    "privacy_spans": "PRIVACY_SPANS_JSON",
    "PRIVACY_SPANS_JSON": "PRIVACY_SPANS_JSON",
    "task_facts": "TASK_CRITICAL_FACTS_JSON",
    "TASK_CRITICAL_FACTS_JSON": "TASK_CRITICAL_FACTS_JSON",
}


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_template(text: str) -> str:
    """Normalize file templates and Python format strings for drift comparison."""

    text = text.replace("{{", "{").replace("}}", "}")

    def replace(match: re.Match[str]) -> str:
        name = match.group(1)
        normalized = PLACEHOLDER_NORMALIZATION.get(name, name)
        return "{" + normalized + "}"

    text = re.sub(r"\{([A-Za-z_][A-Za-z0-9_]*)\}", replace, text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()


def method_boundary_lines() -> list[str]:
    return [
        "- `generic_llm` uses only the source text and the generic anonymizer prompt.",
        "- `privacy_first_llm` uses only the source text and the conservative privacy-first prompt.",
        "- `critical_span_guard_extracted` first extracts privacy spans and task facts from the source text, then anonymizes from those extracted structures, then runs verify/repair, then applies deterministic safety/repair.",
        "- `critical_span_guard_extracted` does not use gold `private_spans`, gold `task_critical_facts`, or gold QA at inference time.",
        "- Gold annotations are used for evaluation, local oracle diagnostics, and fact-judge evaluation prompts, not for the headline non-oracle anonymizer inputs.",
        "- Cache keys are SHA-256 hashes of the model, method, example id, and exact rendered prompt text in `src/run_openai_methods.py`.",
    ]


def deterministic_repair_lines() -> list[str]:
    return [
        "- Direct safety scrub for email, phone, MRN, record IDs, clinic/hospital names, legal application numbers, exact ages, and synthetic occupations.",
        "- Legal Article placeholder repair to restore task-critical Article numbers when over-generalized.",
        "- Legal case-label repair and detention-regime label generalization when the label is not task-critical.",
        "- Clinical medication placeholder repair for task-critical treatment facts.",
    ]


def main() -> int:
    rows = []
    failures = []
    for item in PROMPTS:
        file_text = item["path"].read_text(encoding="utf-8")
        code_text = str(getattr(run_openai_methods, item["constant"]))
        file_norm = normalize_template(file_text)
        code_norm = normalize_template(code_text)
        matches = file_norm == code_norm
        if not matches:
            failures.append(f"{item['path']} differs from {item['constant']}")
        rows.append(
            {
                **item,
                "file_sha": sha256(file_text),
                "code_sha": sha256(code_text),
                "matches": matches,
                "line_count": len(file_text.splitlines()),
            }
        )

    lines = ["# Prompt and Method Appendix", ""]
    lines.append(
        "Generated appendix for exact prompt transparency and implementation drift checks. The runner constants in `src/run_openai_methods.py` are authoritative for cached OpenAI calls."
    )
    lines.append("")
    lines.append("## Prompt Inventory")
    lines.append("")
    lines.append("| Prompt | Role | File | Lines | File SHA-256 | Runner constant | Normalized match |")
    lines.append("|---|---|---|---:|---|---|---|")
    for row in rows:
        lines.append(
            "| {name} | {role} | `{path}` | {line_count} | `{file_sha}` | `{constant}` / `{code_sha}` | {match} |".format(
                name=row["name"],
                role=row["role"],
                path=row["path"],
                line_count=row["line_count"],
                file_sha=row["file_sha"][:16],
                constant=row["constant"],
                code_sha=row["code_sha"][:16],
                match="yes" if row["matches"] else "no",
            )
        )
    lines.append("")
    lines.append("## Non-Oracle Boundary")
    lines.append("")
    lines.extend(method_boundary_lines())
    lines.append("")
    lines.append("## Deterministic Safety/Repair Layer")
    lines.append("")
    lines.extend(deterministic_repair_lines())
    lines.append("")
    lines.append("## Cache-Only Rebuild")
    lines.append("")
    lines.append(
        "`conda run -n preserv_anony python src/run_openai_methods.py --model gpt-4.1-nano --max-examples 50 --methods generic_llm privacy_first_llm critical_span_guard_extracted --cache-only`"
    )
    lines.append("")
    lines.append("## Drift Check")
    lines.append("")
    if failures:
        lines.append(f"Status: FAIL ({len(failures)} prompt drift issue(s)).")
        for failure in failures:
            lines.append(f"- {failure}")
    else:
        lines.append("Status: PASS. Prompt files match the runner constants after normalizing placeholder names and Python-escaped JSON braces.")
    lines.append("")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT_PATH}")
    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
