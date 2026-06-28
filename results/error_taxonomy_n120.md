# Error Taxonomy and Current Counts

Counts are row counts over the 120-example cached LLM run. Treat them as audit triage, not final paper statistics.

| Error type | Operational signal | generic_llm | privacy_first_llm | critical_span_guard_extracted |
|---|---|---:|---:|---:|
| Direct identifier leak | direct_leaked_spans is non-empty | 22 | 0 | 0 |
| Quasi-identifier retained | quasi_leaked_spans is non-empty | 91 | 38 | 9 |
| Exact critical fact omitted | omitted_facts is non-empty under exact/alias matching | 69 | 98 | 52 |
| QA answer changed | failed_qa is non-empty | 28 | 95 | 6 |
| LLM-audited fact not retained | fact judge marks at least one fact not retained after applying gold generalization rules | 29 | 93 | 3 |
| LLM-audited contradiction | fact judge marks at least one fact contradicted | 0 | 1 | 0 |
| Likely exact-match undercount | audited TCFR exceeds exact TCFR by at least 0.15 | 64 | 68 | 51 |

## Domain notes

- Direct identifier leak: generic_llm: clinical=2, legal=20
- Quasi-identifier retained: generic_llm: clinical=60, legal=31; privacy_first_llm: clinical=33, legal=5; critical_span_guard_extracted: clinical=0, legal=9
- Exact critical fact omitted: generic_llm: clinical=59, legal=10; privacy_first_llm: clinical=60, legal=38; critical_span_guard_extracted: clinical=46, legal=6
- QA answer changed: generic_llm: clinical=18, legal=10; privacy_first_llm: clinical=57, legal=38; critical_span_guard_extracted: clinical=0, legal=6
- LLM-audited fact not retained: generic_llm: clinical=23, legal=6; privacy_first_llm: clinical=57, legal=36; critical_span_guard_extracted: clinical=2, legal=1
- LLM-audited contradiction: privacy_first_llm: clinical=1, legal=0
- Likely exact-match undercount: generic_llm: clinical=58, legal=6; privacy_first_llm: clinical=60, legal=8; critical_span_guard_extracted: clinical=45, legal=6

## Paper-facing interpretation

- Direct leaks in this run are concentrated in generic LLM legal outputs, especially legal application numbers.
- Privacy-first prompting nearly eliminates direct leaks but frequently removes task-critical clinical and legal facts.
- Critical Span Guard has the best current privacy-utility balance, but remaining legal quasi-identifier cases and exact-match undercounts should be manually audited before submission.
- The exact TCFR scorer is intentionally conservative; use the LLM-audited table and manual examples to avoid overclaiming deterministic-string failures.

