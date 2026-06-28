# External Audit Comparison

External auditor model: `gpt-5.5`

## Fact Retention

| Method | N | Current audited TCFR | External audited TCFR | Delta | Fact-label agreement | Main disagreement type |
|---|---:|---:|---:|---:|---:|---|
| critical_span_guard_extracted | 60 | 0.986 | 0.917 | -0.069 | 0.912 | clinical numeric/specificity |
| generic_llm | 60 | 0.925 | 0.875 | -0.050 | 0.935 | clinical numeric/specificity |
| privacy_first_llm | 60 | 0.594 | 0.483 | -0.111 | 0.833 | clinical numeric/specificity |

## Disagreement Counts

| Method | Category | Count |
|---|---|---:|
| critical_span_guard_extracted | clinical numeric/specificity | 13 |
| critical_span_guard_extracted | sensitive attribute overlap | 3 |
| critical_span_guard_extracted | legal specificity | 2 |
| critical_span_guard_extracted | other | 1 |
| generic_llm | clinical numeric/specificity | 8 |
| generic_llm | other | 3 |
| generic_llm | sensitive attribute overlap | 3 |
| privacy_first_llm | clinical numeric/specificity | 22 |
| privacy_first_llm | legal specificity | 8 |
| privacy_first_llm | generalization/paraphrase | 3 |
| privacy_first_llm | other | 2 |
| privacy_first_llm | sensitive attribute overlap | 1 |
