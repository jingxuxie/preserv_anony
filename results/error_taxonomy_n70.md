# Error Taxonomy and Current Counts

Counts are row counts over the 70-example cached LLM run. Treat them as audit triage, not final paper statistics.

| Error type | Operational signal | generic_llm | privacy_first_llm | critical_span_guard_extracted |
|---|---|---:|---:|---:|
| Direct identifier leak | direct_leaked_spans is non-empty | 13 | 0 | 0 |
| Quasi-identifier retained | quasi_leaked_spans is non-empty | 53 | 21 | 2 |
| Exact critical fact omitted | omitted_facts is non-empty under exact/alias matching | 40 | 59 | 30 |
| QA answer changed | failed_qa is non-empty | 20 | 58 | 3 |
| LLM-audited fact not retained | fact judge marks at least one fact not retained after applying gold generalization rules | 19 | 56 | 1 |
| LLM-audited contradiction | fact judge marks at least one fact contradicted | 0 | 0 | 0 |
| Likely exact-match undercount | audited TCFR exceeds exact TCFR by at least 0.15 | 37 | 40 | 30 |

## Domain notes

- Direct identifier leak: generic_llm: clinical=1, legal=12
- Quasi-identifier retained: generic_llm: clinical=35, legal=18; privacy_first_llm: clinical=20, legal=1; critical_span_guard_extracted: clinical=0, legal=2
- Exact critical fact omitted: generic_llm: clinical=34, legal=6; privacy_first_llm: clinical=35, legal=24; critical_span_guard_extracted: clinical=27, legal=3
- QA answer changed: generic_llm: clinical=14, legal=6; privacy_first_llm: clinical=34, legal=24; critical_span_guard_extracted: clinical=0, legal=3
- LLM-audited fact not retained: generic_llm: clinical=15, legal=4; privacy_first_llm: clinical=34, legal=22; critical_span_guard_extracted: clinical=0, legal=1
- Likely exact-match undercount: generic_llm: clinical=34, legal=3; privacy_first_llm: clinical=35, legal=5; critical_span_guard_extracted: clinical=27, legal=3

## Paper-facing interpretation

- Direct leaks in this run are concentrated in generic LLM legal outputs, especially legal application numbers.
- Privacy-first prompting nearly eliminates direct leaks but frequently removes task-critical clinical and legal facts.
- Critical Span Guard has the best current privacy-utility balance, but remaining legal quasi-identifier cases and exact-match undercounts should be manually audited before submission.
- The exact TCFR scorer is intentionally conservative; use the LLM-audited table and manual examples to avoid overclaiming deterministic-string failures.

