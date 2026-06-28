"""One-command fast experiment pipeline."""

from __future__ import annotations

import argparse

import build_benchmark
import compute_metrics
import run_anonymizers
from anonymizers import METHODS


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--clinical-n", type=int, default=50)
    parser.add_argument("--legal-n", type=int, default=50)
    parser.add_argument("--seed", type=int, default=13)
    parser.add_argument("--benchmark", default="data/processed/benchmark.jsonl")
    parser.add_argument("--outputs", default="data/processed/anonymized_outputs.jsonl")
    parser.add_argument("--scored", default="data/processed/judgments.jsonl")
    parser.add_argument("--summary", default="results/summary.json")
    parser.add_argument("--report", default="results/main_results.md")
    parser.add_argument("--methods", nargs="+", default=METHODS)
    args = parser.parse_args()

    rows = build_benchmark.build_clinical(args.clinical_n, args.seed)
    rows.extend(build_benchmark.build_legal(args.legal_n, args.seed))
    build_benchmark.write_jsonl(args.benchmark, rows)
    print(f"wrote {len(rows)} examples to {args.benchmark}")

    run_anonymizers.run(args.benchmark, args.outputs, args.methods)
    compute_metrics.run(args.benchmark, args.outputs, args.scored, args.summary, args.report)


if __name__ == "__main__":
    main()
