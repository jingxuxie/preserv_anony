# Error Taxonomy and Current Counts

Counts are row counts over the 100-example cached LLM run. Treat them as audit triage, not final paper statistics.

| Error type | Operational signal | generic_llm | privacy_first_llm | critical_span_guard_extracted |
|---|---|---:|---:|---:|
| Direct identifier leak | direct_leaked_spans is non-empty | 19 | 0 | 0 |
| Quasi-identifier retained | quasi_leaked_spans is non-empty | 78 | 33 | 5 |
| Exact critical fact omitted | omitted_facts is non-empty under exact/alias matching | 56 | 83 | 41 |
| QA answer changed | failed_qa is non-empty | 23 | 81 | 4 |
| LLM-audited fact not retained | fact judge marks at least one fact not retained after applying gold generalization rules | 24 | 81 | 1 |
| LLM-audited contradiction | fact judge marks at least one fact contradicted | 0 | 1 | 0 |
| Likely exact-match undercount | audited TCFR exceeds exact TCFR by at least 0.15 | 52 | 56 | 41 |

## Domain notes

- Direct identifier leak: generic_llm: clinical=2, legal=17
- Quasi-identifier retained: generic_llm: clinical=50, legal=28; privacy_first_llm: clinical=29, legal=4; critical_span_guard_extracted: clinical=0, legal=5
- Exact critical fact omitted: generic_llm: clinical=49, legal=7; privacy_first_llm: clinical=50, legal=33; critical_span_guard_extracted: clinical=37, legal=4
- QA answer changed: generic_llm: clinical=16, legal=7; privacy_first_llm: clinical=48, legal=33; critical_span_guard_extracted: clinical=0, legal=4
- LLM-audited fact not retained: generic_llm: clinical=19, legal=5; privacy_first_llm: clinical=48, legal=33; critical_span_guard_extracted: clinical=0, legal=1
- LLM-audited contradiction: privacy_first_llm: clinical=1, legal=0
- Likely exact-match undercount: generic_llm: clinical=48, legal=4; privacy_first_llm: clinical=50, legal=6; critical_span_guard_extracted: clinical=37, legal=4

## Paper-facing interpretation

- Direct leaks in this run are concentrated in generic LLM legal outputs, especially legal application numbers.
- Privacy-first prompting nearly eliminates direct leaks but frequently removes task-critical clinical and legal facts.
- Critical Span Guard has the best current privacy-utility balance, but remaining legal quasi-identifier cases and exact-match undercounts should be manually audited before submission.
- The exact TCFR scorer is intentionally conservative; use the LLM-audited table and manual examples to avoid overclaiming deterministic-string failures.

