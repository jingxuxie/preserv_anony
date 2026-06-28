"""Generate a schema and quality audit for the benchmark JSONL files."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

from io_utils import read_jsonl


BENCHMARK_PATH = Path("data/processed/benchmark.jsonl")
BENCHMARK_N120_PATH = Path("data/processed/benchmark_n120_llm.jsonl")
ROBUSTNESS_PATH = Path("data/processed/robustness_benchmark.jsonl")
OUT_PATH = Path("results/benchmark_quality_audit.md")

REQUIRED_ROW_KEYS = {"id", "domain", "source", "text", "private_spans", "task_critical_facts", "qa"}
REQUIRED_SPAN_KEYS = {"text", "type", "identifier_type", "replacement"}
REQUIRED_FACT_KEYS = {"type", "fact", "generalization_allowed"}
REQUIRED_QA_KEYS = {"q", "a", "answer_aliases"}


def source_family(source: object) -> str:
    value = str(source)
    if value == "synthetic_template":
        return "synthetic clinical template"
    if value.startswith("TAB:"):
        parts = value.split(":")
        split = parts[1] if len(parts) > 1 else "unknown"
        return f"TAB ECHR {split}"
    if value == "handwritten_stress" or value.startswith("stress_"):
        return "handwritten stress slice"
    return value or "missing"


def counter_text(counter: Counter[str]) -> str:
    if not counter:
        return "none"
    return ", ".join(f"{key}={value}" for key, value in sorted(counter.items()))


def avg(rows: list[dict], key: str) -> float:
    if not rows:
        return 0.0
    return mean(len(row.get(key, [])) for row in rows)


def contains(text: str, needle: object) -> bool:
    value = str(needle).strip()
    return bool(value) and value.lower() in text.lower()


def validate_rows(rows: list[dict], name: str) -> list[str]:
    failures: list[str] = []
    ids = [str(row.get("id", "")) for row in rows]
    duplicate_ids = sorted(item for item, count in Counter(ids).items() if count > 1)
    if duplicate_ids:
        failures.append(f"{name}: duplicate ids: {', '.join(duplicate_ids[:10])}")

    for row in rows:
        row_id = str(row.get("id", "missing-id"))
        missing_row_keys = sorted(REQUIRED_ROW_KEYS - set(row.keys()))
        if missing_row_keys:
            failures.append(f"{name}/{row_id}: missing row keys {missing_row_keys}")
            continue
        text = str(row.get("text", ""))
        if len(text.strip()) < 20:
            failures.append(f"{name}/{row_id}: text is empty or too short")
        if row.get("domain") not in {"clinical", "legal"}:
            failures.append(f"{name}/{row_id}: unsupported domain {row.get('domain')}")

        spans = row.get("private_spans", [])
        facts = row.get("task_critical_facts", [])
        qas = row.get("qa", [])
        if not spans:
            failures.append(f"{name}/{row_id}: no private spans")
        if not any(span.get("identifier_type") == "DIRECT" for span in spans):
            failures.append(f"{name}/{row_id}: no direct identifier span")
        if not facts:
            failures.append(f"{name}/{row_id}: no task-critical facts")
        if not qas:
            failures.append(f"{name}/{row_id}: no QA pairs")

        for index, span in enumerate(spans):
            missing_span_keys = sorted(REQUIRED_SPAN_KEYS - set(span.keys()))
            if missing_span_keys:
                failures.append(f"{name}/{row_id}/span{index}: missing keys {missing_span_keys}")
            if span.get("identifier_type") not in {"DIRECT", "QUASI"}:
                failures.append(f"{name}/{row_id}/span{index}: bad identifier_type {span.get('identifier_type')}")
            if not contains(text, span.get("text", "")):
                failures.append(f"{name}/{row_id}/span{index}: span text not found in source text")

        for index, fact in enumerate(facts):
            missing_fact_keys = sorted(REQUIRED_FACT_KEYS - set(fact.keys()))
            if missing_fact_keys:
                failures.append(f"{name}/{row_id}/fact{index}: missing keys {missing_fact_keys}")
            if not isinstance(fact.get("generalization_allowed"), bool):
                failures.append(f"{name}/{row_id}/fact{index}: generalization_allowed is not bool")
            fact_text = str(fact.get("fact", "")).strip()
            aliases = [str(alias) for alias in fact.get("answer_aliases", [])]
            if fact_text and not contains(text, fact_text) and not any(contains(text, alias) for alias in aliases):
                failures.append(f"{name}/{row_id}/fact{index}: fact or alias not found in source text")

        for index, qa in enumerate(qas):
            missing_qa_keys = sorted(REQUIRED_QA_KEYS - set(qa.keys()))
            if missing_qa_keys:
                failures.append(f"{name}/{row_id}/qa{index}: missing keys {missing_qa_keys}")
            answer = str(qa.get("a", "")).strip()
            aliases = [str(alias) for alias in qa.get("answer_aliases", [])]
            if answer and answer not in aliases:
                failures.append(f"{name}/{row_id}/qa{index}: answer is not listed as an alias")
            if answer and not contains(text, answer) and not any(contains(text, alias) for alias in aliases):
                failures.append(f"{name}/{row_id}/qa{index}: answer or alias not found in source text")
    return failures


def inventory(rows: list[dict]) -> dict:
    by_domain: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_domain[str(row.get("domain", "missing"))].append(row)

    span_types: Counter[str] = Counter()
    identifier_types: Counter[str] = Counter()
    fact_types: Counter[str] = Counter()
    qa_counts: Counter[str] = Counter()
    generalizable_facts = 0
    for row in rows:
        qa_counts[str(len(row.get("qa", [])))] += 1
        for span in row.get("private_spans", []):
            identifier_type = str(span.get("identifier_type", "missing"))
            identifier_types[identifier_type] += 1
            span_types[f"{identifier_type}:{span.get('type', 'missing')}"] += 1
        for fact in row.get("task_critical_facts", []):
            fact_types[f"{row.get('domain')}:{fact.get('type', 'missing')}"] += 1
            if fact.get("generalization_allowed"):
                generalizable_facts += 1

    return {
        "by_domain": Counter({domain: len(items) for domain, items in by_domain.items()}),
        "sources": Counter(source_family(row.get("source")) for row in rows),
        "identifier_types": identifier_types,
        "span_types": span_types,
        "fact_types": fact_types,
        "qa_counts": qa_counts,
        "generalizable_facts": generalizable_facts,
        "avg_spans": avg(rows, "private_spans"),
        "avg_facts": avg(rows, "task_critical_facts"),
        "avg_qa": avg(rows, "qa"),
    }


def write_report(benchmark: list[dict], benchmark_n120: list[dict], robustness: list[dict], failures: list[str]) -> None:
    bench = inventory(benchmark)
    bench_n120 = inventory(benchmark_n120)
    stress = inventory(robustness)
    lines = ["# Benchmark Quality Audit", ""]
    lines.append(
        "Generated schema and integrity audit for the controlled benchmarks and handwritten stress slice."
    )
    lines.append("")
    lines.append("## Schema Contract")
    lines.append("")
    lines.append("- Each row has `id`, `domain`, `source`, `text`, `private_spans`, `task_critical_facts`, and `qa`.")
    lines.append("- Each private span has `text`, `type`, `identifier_type`, and `replacement`; `identifier_type` is `DIRECT` or `QUASI`.")
    lines.append("- Each task-critical fact has `type`, `fact`, and boolean `generalization_allowed`.")
    lines.append("- Each QA item has `q`, `a`, and `answer_aliases`, with the canonical answer included in aliases.")
    lines.append("")
    lines.append("## Inventory")
    lines.append("")
    lines.append("| Split | Rows | Domains | Sources | Avg spans | Avg facts | Avg QA | Generalizable facts |")
    lines.append("|---|---:|---|---|---:|---:|---:|---:|")
    lines.append(
        "| Main benchmark | {rows} | {domains} | {sources} | {avg_spans:.2f} | {avg_facts:.2f} | {avg_qa:.2f} | {generalizable} |".format(
            rows=len(benchmark),
            domains=counter_text(bench["by_domain"]),
            sources=counter_text(bench["sources"]),
            avg_spans=bench["avg_spans"],
            avg_facts=bench["avg_facts"],
            avg_qa=bench["avg_qa"],
            generalizable=bench["generalizable_facts"],
        )
    )
    lines.append(
        "| Promoted n120 benchmark | {rows} | {domains} | {sources} | {avg_spans:.2f} | {avg_facts:.2f} | {avg_qa:.2f} | {generalizable} |".format(
            rows=len(benchmark_n120),
            domains=counter_text(bench_n120["by_domain"]),
            sources=counter_text(bench_n120["sources"]),
            avg_spans=bench_n120["avg_spans"],
            avg_facts=bench_n120["avg_facts"],
            avg_qa=bench_n120["avg_qa"],
            generalizable=bench_n120["generalizable_facts"],
        )
    )
    lines.append(
        "| Stress slice | {rows} | {domains} | {sources} | {avg_spans:.2f} | {avg_facts:.2f} | {avg_qa:.2f} | {generalizable} |".format(
            rows=len(robustness),
            domains=counter_text(stress["by_domain"]),
            sources=counter_text(stress["sources"]),
            avg_spans=stress["avg_spans"],
            avg_facts=stress["avg_facts"],
            avg_qa=stress["avg_qa"],
            generalizable=stress["generalizable_facts"],
        )
    )
    lines.append("")
    lines.append("## Span and Fact Coverage")
    lines.append("")
    lines.append(f"- Main identifier counts: {counter_text(bench['identifier_types'])}.")
    lines.append(f"- Promoted n120 identifier counts: {counter_text(bench_n120['identifier_types'])}.")
    lines.append(f"- Stress identifier counts: {counter_text(stress['identifier_types'])}.")
    lines.append(f"- Main span types: {counter_text(bench['span_types'])}.")
    lines.append(f"- Main fact types: {counter_text(bench['fact_types'])}.")
    lines.append(f"- Main QA-pair count distribution: {counter_text(bench['qa_counts'])}.")
    lines.append(f"- Stress tags are summarized in `results/robustness_report.md`.")
    lines.append("")
    lines.append("## Integrity Checks")
    lines.append("")
    if failures:
        lines.append(f"Status: FAIL ({len(failures)} issue(s)).")
        lines.append("")
        for failure in failures[:100]:
            lines.append(f"- {failure}")
        if len(failures) > 100:
            lines.append(f"- ... {len(failures) - 100} additional failures omitted")
    else:
        lines.append("Status: PASS.")
        lines.append("")
        lines.append("- IDs are unique within each split.")
        lines.append("- Required row, span, fact, and QA keys are present.")
        lines.append("- Every row has at least one direct identifier, one task-critical fact, and one QA pair.")
        lines.append("- Private span texts are found in the source text.")
        lines.append("- Task facts or their aliases are found in the source text.")
        lines.append("- QA answers or their aliases are found in the source text.")
    lines.append("")
    lines.append("## Paper Caveats")
    lines.append("")
    lines.append("- Clinical rows are synthetic templates and should be described as controlled utility examples, not real clinical notes.")
    lines.append("- Legal facts and QA are heuristic TAB-derived annotations with manual spot checks, not expert legal annotation.")
    lines.append("- The stress slice is diagnostic and intentionally over-represents hard privacy-utility overlaps.")
    lines.append("")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    benchmark = read_jsonl(BENCHMARK_PATH)
    benchmark_n120 = read_jsonl(BENCHMARK_N120_PATH)
    robustness = read_jsonl(ROBUSTNESS_PATH)
    failures = validate_rows(benchmark, "benchmark")
    failures.extend(validate_rows(benchmark_n120, "benchmark_n120"))
    failures.extend(validate_rows(robustness, "stress"))
    write_report(benchmark, benchmark_n120, robustness, failures)
    print(f"wrote {OUT_PATH}")
    if failures:
        print(f"FAIL: {len(failures)} benchmark integrity issue(s)")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
