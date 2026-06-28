# Privacy Span Recall Audit

Generated: 2026-06-28

This report surfaces the span-level privacy metrics already computed by `src/compute_metrics.py` for the promoted non-oracle run. Direct and quasi span recall measure the fraction of gold privacy spans not found verbatim in each anonymized output; they complement row-level direct-leak rate and QI-risk scoring.

## Gold Span Inventory

| Split | Rows | Direct spans | Quasi spans | Total privacy spans |
|---|---:|---:|---:|---:|
| overall | 150 | 684 | 444 | 1128 |
| clinical | 75 | 525 | 225 | 750 |
| legal | 75 | 159 | 219 | 378 |

## Span Recall

| Method | Direct span recall | Quasi span recall | All privacy span recall | Direct leak rows | Quasi leak rows |
|---|---:|---:|---:|---:|---:|
| Generic LLM | 0.919 | 0.485 | 0.771 | 27/150 | 114/150 |
| Privacy-first LLM | 1.000 | 0.893 | 0.964 | 0/150 | 45/150 |
| Critical Span Guard | 1.000 | 0.972 | 0.982 | 0/150 | 11/150 |

## Domain Split

| Domain | Method | Direct span recall | Quasi span recall | All privacy span recall |
|---|---|---:|---:|---:|
| clinical | Generic LLM | 0.996 | 0.360 | 0.805 |
| clinical | Privacy-first LLM | 1.000 | 0.809 | 0.943 |
| clinical | Critical Span Guard | 1.000 | 1.000 | 1.000 |
| legal | Generic LLM | 0.841 | 0.609 | 0.736 |
| legal | Privacy-first LLM | 1.000 | 0.976 | 0.986 |
| legal | Critical Span Guard | 1.000 | 0.943 | 0.963 |

## Leaked Span Inventory

| Method | Direct leaked span instances | Top direct leaks | Quasi leaked span instances | Top quasi leaks |
|---|---:|---|---:|---|
| Generic LLM | 27 | `December 24, 2025` (1); `August 2, 2025` (1); `33176/06` (1); `17906/15` (1); `28426/06` (1); `35396/97` (1) | 210 | `teacher` (10); `software engineer` (10); `dental hygienist` (10); `postal worker` (9); `farm manager` (9); `retired judge` (9) |
| Privacy-first LLM | 0 | none | 49 | `dental hygienist` (10); `postal worker` (9); `software engineer` (8); `long-haul driver` (6); `farm manager` (3); `retired judge` (2) |
| Critical Span Guard | 0 | none | 19 | `participate in a labour market policy programme.` (1); `sister` (1); `sister’s` (1); `sister’` (1); `four votes to three` (1); `widows` (1) |

## Paper-Safe Interpretation

- CSG has perfect measured direct span recall on the promoted run and the strongest all-span recall, but it is still a deterministic string audit rather than a formal privacy guarantee.
- Generic prompting removes many obvious direct spans but leaves enough legal identifiers and quasi-identifiers to fail both row-level and span-level privacy checks.
- Privacy-first prompting reaches perfect direct span recall but still retains some quasi-identifying clinical or legal details while losing much more task-critical utility.
