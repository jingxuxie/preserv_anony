"""Run anonymizers over a benchmark JSONL file."""

from __future__ import annotations

import argparse

from anonymizers import METHODS, anonymize
from io_utils import read_jsonl, write_jsonl


def run(benchmark_path: str, out_path: str, methods: list[str]) -> None:
    examples = read_jsonl(benchmark_path)
    rows = []
    for example in examples:
        for method in methods:
            rows.append(
                {
                    "id": example["id"],
                    "domain": example["domain"],
                    "source": example["source"],
                    "method": method,
                    "text": example["text"],
                    "anonymized_text": anonymize(example, method),
                }
            )
    write_jsonl(out_path, rows)
    print(f"wrote {len(rows)} anonymized outputs to {out_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark", default="data/processed/benchmark.jsonl")
    parser.add_argument("--out", default="data/processed/anonymized_outputs.jsonl")
    parser.add_argument("--methods", nargs="+", default=METHODS)
    args = parser.parse_args()
    run(args.benchmark, args.out, args.methods)


if __name__ == "__main__":
    main()
