# Error Taxonomy and Current Counts

Counts are row counts over the 150-example cached LLM run. Treat them as audit triage, not final paper statistics.

| Error type | Operational signal | generic_llm | privacy_first_llm | critical_span_guard_extracted |
|---|---|---:|---:|---:|
| Direct identifier leak | direct_leaked_spans is non-empty | 27 | 0 | 0 |
| Quasi-identifier retained | quasi_leaked_spans is non-empty | 114 | 45 | 11 |
| Exact critical fact omitted | omitted_facts is non-empty under exact/alias matching | 88 | 125 | 67 |
| QA answer changed | failed_qa is non-empty | 36 | 121 | 9 |
| LLM-audited fact not retained | fact judge marks at least one fact not retained after applying gold generalization rules | 36 | 119 | 3 |
| LLM-audited contradiction | fact judge marks at least one fact contradicted | 0 | 1 | 0 |
| Likely exact-match undercount | audited TCFR exceeds exact TCFR by at least 0.15 | 81 | 86 | 66 |

## Domain notes

- Direct identifier leak: generic_llm: clinical=2, legal=25
- Quasi-identifier retained: generic_llm: clinical=75, legal=39; privacy_first_llm: clinical=40, legal=5; critical_span_guard_extracted: clinical=0, legal=11
- Exact critical fact omitted: generic_llm: clinical=74, legal=14; privacy_first_llm: clinical=75, legal=50; critical_span_guard_extracted: clinical=58, legal=9
- QA answer changed: generic_llm: clinical=22, legal=14; privacy_first_llm: clinical=71, legal=50; critical_span_guard_extracted: clinical=0, legal=9
- LLM-audited fact not retained: generic_llm: clinical=27, legal=9; privacy_first_llm: clinical=71, legal=48; critical_span_guard_extracted: clinical=2, legal=1
- LLM-audited contradiction: privacy_first_llm: clinical=1, legal=0
- Likely exact-match undercount: generic_llm: clinical=73, legal=8; privacy_first_llm: clinical=75, legal=11; critical_span_guard_extracted: clinical=57, legal=9

## Paper-facing interpretation

- Direct leaks in this run are concentrated in generic LLM legal outputs, especially legal application numbers.
- Privacy-first prompting nearly eliminates direct leaks but frequently removes task-critical clinical and legal facts.
- Critical Span Guard has the best current privacy-utility balance, but remaining legal quasi-identifier cases and exact-match undercounts should be manually audited before submission.
- The exact TCFR scorer is intentionally conservative; use the LLM-audited table and manual examples to avoid overclaiming deterministic-string failures.

