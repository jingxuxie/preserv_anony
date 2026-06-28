"""Build a stricter benchmark preview while preserving current example IDs.

This is intentionally separate from ``build_benchmark.py``. It lets us tighten
legal annotations and compare cached anonymizer outputs without changing the
underlying snippets or ID mapping used by those outputs.
"""

from __future__ import annotations

import argparse

from build_benchmark import (
    _application_numbers,
    _article_candidates,
    _claim_aliases,
    _claim_phrase,
    _find_complaint_sentence,
    _find_sentence,
    _legal_outcome,
    _sentences,
    _upsert_direct_legal_id,
)
from io_utils import read_jsonl, write_jsonl


def tighten_legal_row(row: dict) -> dict:
    out = dict(row)
    text = out["text"]
    private_spans = [dict(span) for span in out.get("private_spans", [])]
    for number in _application_numbers(text):
        _upsert_direct_legal_id(private_spans, number)

    sentences = _sentences(text)
    complaint = _find_complaint_sentence(sentences)
    outcome_sent = _find_sentence(
        list(reversed(sentences)),
        [r"\bno violation\b.*\bArticle\b", r"\bviolation of Article\b", r"\binadmissible\b"],
    )
    articles = _article_candidates(text)
    if not articles:
        return out

    facts = [{"type": "legal_basis", "fact": articles[0], "generalization_allowed": False}]
    outcome = _legal_outcome(outcome_sent)
    if outcome:
        facts.append({"type": "outcome", "fact": outcome, "generalization_allowed": False})
    if complaint:
        claim = _claim_phrase(complaint)
        if claim:
            claim_fact = {
                "type": "claim",
                "fact": claim,
                "generalization_allowed": False,
            }
            aliases = _claim_aliases(claim)
            if aliases:
                claim_fact["answer_aliases"] = aliases
            facts.append(claim_fact)

    qa = [{"q": "Which substantive Article was invoked?", "a": articles[0], "answer_aliases": [articles[0]]}]
    if outcome:
        qa.append({"q": "What outcome did the Court state?", "a": outcome, "answer_aliases": [outcome]})
    if complaint:
        claim = _claim_phrase(complaint)
        if claim:
            qa.append({"q": "What core claim was raised?", "a": claim, "answer_aliases": [claim, *_claim_aliases(claim)]})

    out["private_spans"] = private_spans
    out["task_critical_facts"] = facts
    out["qa"] = qa
    return out


def build_rows(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        if row.get("domain") == "legal":
            out.append(tighten_legal_row(row))
        else:
            out.append(row)
    return out


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/benchmark.jsonl")
    parser.add_argument("--out", default="data/processed/benchmark_v2_preview.jsonl")
    args = parser.parse_args()
    rows = build_rows(read_jsonl(args.benchmark))
    write_jsonl(args.out, rows)
    legal = [row for row in rows if row.get("domain") == "legal"]
    print(f"wrote {len(rows)} examples to {args.out}")
    print(f"legal={len(legal)}")


if __name__ == "__main__":
    main()
