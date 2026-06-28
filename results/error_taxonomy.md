# Error Taxonomy and Current Counts

Counts are row counts over the 50-example cached LLM run. Treat them as audit triage, not final paper statistics.

| Error type | Operational signal | generic_llm | privacy_first_llm | critical_span_guard_extracted |
|---|---|---:|---:|---:|
| Direct identifier leak | direct_leaked_spans is non-empty | 8 | 0 | 0 |
| Quasi-identifier retained | quasi_leaked_spans is non-empty | 38 | 17 | 2 |
| Exact critical fact omitted | omitted_facts is non-empty under exact/alias matching | 27 | 41 | 22 |
| QA answer changed | failed_qa is non-empty | 12 | 40 | 1 |
| LLM-audited fact not retained | fact judge marks at least one fact not retained after applying gold generalization rules | 12 | 38 | 0 |
| LLM-audited contradiction | fact judge marks at least one fact contradicted | 0 | 0 | 0 |
| Likely exact-match undercount | audited TCFR exceeds exact TCFR by at least 0.15 | 25 | 30 | 22 |

## Domain notes

- Direct identifier leak: generic_llm: clinical=0, legal=8
- Quasi-identifier retained: generic_llm: clinical=25, legal=13; privacy_first_llm: clinical=16, legal=1; critical_span_guard_extracted: clinical=0, legal=2
- Exact critical fact omitted: generic_llm: clinical=24, legal=3; privacy_first_llm: clinical=25, legal=16; critical_span_guard_extracted: clinical=21, legal=1
- QA answer changed: generic_llm: clinical=9, legal=3; privacy_first_llm: clinical=24, legal=16; critical_span_guard_extracted: clinical=0, legal=1
- LLM-audited fact not retained: generic_llm: clinical=10, legal=2; privacy_first_llm: clinical=24, legal=14
- Likely exact-match undercount: generic_llm: clinical=24, legal=1; privacy_first_llm: clinical=25, legal=5; critical_span_guard_extracted: clinical=21, legal=1

## Paper-facing interpretation

- Direct leaks in this run are concentrated in generic LLM legal outputs, especially legal application numbers.
- Privacy-first prompting nearly eliminates direct leaks but frequently removes task-critical clinical and legal facts.
- Critical Span Guard has the best current privacy-utility balance, but remaining legal quasi-identifier cases and exact-match undercounts should be manually audited before submission.
- The exact TCFR scorer is intentionally conservative; use the LLM-audited table and manual examples to avoid overclaiming deterministic-string failures.

