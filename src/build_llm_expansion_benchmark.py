"""Build controlled benchmark extensions for non-oracle LLM expansion runs.

The existing promoted headline uses ``data/processed/benchmark.jsonl``.  This
helper appends new rows from the local n200 diagnostic benchmark while keeping
the promoted n100 rows byte-for-byte intact, so cache hits remain valid.
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from io_utils import read_jsonl, write_jsonl


def build(base_path: str, candidate_path: str, out_path: str, target_examples: int) -> None:
    base = read_jsonl(base_path)
    candidates = read_jsonl(candidate_path)
    if target_examples < len(base):
        raise ValueError(f"target_examples={target_examples} is smaller than base size {len(base)}")

    rows = list(base)
    base_ids = {row["id"] for row in base}
    base_domains = Counter(row["domain"] for row in base)
    domains = sorted(base_domains)
    if len(set(base_domains.values())) != 1:
        raise ValueError(f"base split is not balanced: {dict(base_domains)}")
    if target_examples % len(domains) != 0:
        raise ValueError(f"target_examples must divide evenly over domains {domains}")

    target_per_domain = target_examples // len(domains)
    need_by_domain = {domain: target_per_domain - base_domains[domain] for domain in domains}
    if any(need < 0 for need in need_by_domain.values()):
        raise ValueError(f"target split would remove examples: {need_by_domain}")

    extras = []
    for domain in domains:
        domain_candidates = [
            row
            for row in candidates
            if row["domain"] == domain and row["id"] not in base_ids
        ]
        domain_candidates.sort(key=lambda row: row["id"])
        need = need_by_domain[domain]
        if len(domain_candidates) < need:
            raise ValueError(f"not enough {domain} candidates: need {need}, have {len(domain_candidates)}")
        extras.extend(domain_candidates[:need])

    rows.extend(extras)
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    write_jsonl(out, rows)

    counts = Counter(row["domain"] for row in rows)
    added = Counter(row["domain"] for row in extras)
    print(f"base_rows={len(base)} target_rows={len(rows)} added_rows={len(extras)}")
    print("target_domains=" + ", ".join(f"{key}={value}" for key, value in sorted(counts.items())))
    print("added_domains=" + ", ".join(f"{key}={value}" for key, value in sorted(added.items())))
    print(f"wrote {out}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="data/processed/benchmark.jsonl")
    parser.add_argument("--candidates", default="data/processed/benchmark_n200_local.jsonl")
    parser.add_argument("--out", required=True)
    parser.add_argument("--target-examples", type=int, required=True)
    args = parser.parse_args()
    build(args.base, args.candidates, args.out, args.target_examples)


if __name__ == "__main__":
    main()
