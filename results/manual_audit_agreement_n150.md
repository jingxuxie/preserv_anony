# Manual Audit Agreement and Readiness Report

Generated: 2026-06-28

This report synthesizes the fixed manual-style audit and the blinded second-annotator packet without new API calls.
Scope caveat: the packet is ready for independent annotation, but it has not been completed; the agreement checks below are artifact-consistency checks against current reference labels, not inter-rater agreement.

## Fixed-Subset Summary

- Examples: 30 (clinical=15, legal=15).
- Method rows: 90.
- Sample version: `n150_fixed_30_v1`.
- The subset intentionally includes all promoted CSG residual-QI and strict-specificity caveat rows.

## Method-Row Summary

| Method | Rows | Direct rate | QI rate | Audited TCFR | Fact-loss rate | QA-fail rate | Clean rate |
|---|---:|---:|---:|---:|---:|---:|---:|
| Generic LLM | 30 | 0.233 | 0.833 | 0.844 | 0.567 | 0.667 | 0.033 |
| Privacy-first LLM | 30 | 0.000 | 0.300 | 0.511 | 0.867 | 0.933 | 0.000 |
| Critical Span Guard | 30 | 0.000 | 0.367 | 0.972 | 0.100 | 0.200 | 0.133 |

## Blinded Packet Readiness

| Check | Value |
|---|---:|
| Packet rows | 90 |
| Examples | 30 |
| Packet IDs match fixed audit | True |
| Complete A/B/C variants | True |
| Answer key complete and separated | True |
| Method-label leak rows in packet | 0 |
| Completed independent annotations | False |

## Reference-Label Consistency

| Reference field | Positive rows | Agreements | Agreement rate |
|---|---:|---:|---:|
| `direct_identifier_retained` | 7/90 | 90/90 | 1.000 |
| `quasi_identifier_retained` | 45/90 | 90/90 | 1.000 |
| `audited_fact_loss` | 46/90 | 90/90 | 1.000 |
| `exact_qa_failure` | 54/90 | 90/90 | 1.000 |
| `exact_match_artifact` | 56/90 | 90/90 | 1.000 |

## Paper-Use Caveats

- The fixed subset is enriched for difficult and caveat rows, so subset rates are not population estimates.
- The second-annotator packet is ready and blinded, but no independent annotation has been completed.
- Reference-label consistency checks validate artifact synchronization, not human inter-rater reliability.

Recommended wording: fixed-subset evidence confirms that CSG remains the best utility-preserving method on the deliberately hard audit subset, while the prepared blinded packet enables a future independent annotation pass.
