# Legal Benchmark Upgrade Note

The main benchmark now uses these tightened legal annotations while preserving the current example IDs and text, so cached OpenAI outputs remain comparable.

## Annotation changes

- `current`: fact types {'legal_basis': 50, 'claim': 21, 'outcome': 19}, fact-count dist {1: 21, 2: 18, 3: 11}, QA-count dist {1: 31, 2: 19}, direct CODE spans 50, quasi CODE spans 4, malformed claim fragments 1.
- `promoted`: fact types {'legal_basis': 50, 'claim': 40, 'outcome': 19}, fact-count dist {2: 31, 3: 14, 1: 5}, QA-count dist {2: 31, 3: 14, 1: 5}, direct CODE spans 54, quasi CODE spans 0, malformed claim fragments 0.

Sanity check: every promoted row preserves the previous benchmark `id` and `text`.

## Existing 50-example LLM outputs scored after the upgrade

| Method | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA consistency |
|---|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 0.000 | 0.080 | 0.897 | 1.000 | 0.990 |
| generic_llm | 0.160 | 1.740 | 0.817 | 0.940 | 0.890 |
| privacy_first_llm | 0.000 | 0.660 | 0.430 | 0.567 | 0.440 |

## Legal split only

| Method | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA consistency |
|---|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 0.000 | 0.160 | 0.980 | 1.000 | 0.980 |
| generic_llm | 0.320 | 1.480 | 0.960 | 0.960 | 0.960 |
| privacy_first_llm | 0.000 | 0.040 | 0.660 | 0.700 | 0.660 |

## Interpretation

- The v2 annotations are stronger for paper quality: legal claim facts increase from 21 to 40, all application numbers become direct identifiers, and abbreviation-truncated `Protocol No` / `(art` claim fragments are removed.
- With same-ID upgraded annotations, CSG keeps zero direct leaks and low QI risk while preserving all audited task-critical facts on the 50-example sample.
- Exact legal TCFR remains useful but conservative: it gives CSG 0.980 on legal here, while audited TCFR confirms paraphrase-aware retention at 1.000. Privacy-first remains much weaker on legal utility.
- The paper should state that legal claim aliases are heuristic and audited with an LLM judge plus manual examples.
