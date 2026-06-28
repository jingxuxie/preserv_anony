# Privacy Span Recall Audit

Generated: 2026-06-27

This report surfaces the span-level privacy metrics already computed by `src/compute_metrics.py` for the promoted non-oracle run. Direct and quasi span recall measure the fraction of gold privacy spans not found verbatim in each anonymized output; they complement row-level direct-leak rate and QI-risk scoring.

## Gold Span Inventory

| Split | Rows | Direct spans | Quasi spans | Total privacy spans |
|---|---:|---:|---:|---:|
| overall | 100 | 459 | 291 | 750 |
| clinical | 50 | 350 | 150 | 500 |
| legal | 50 | 109 | 141 | 250 |

## Span Recall

| Method | Direct span recall | Quasi span recall | All privacy span recall | Direct leak rows | Quasi leak rows |
|---|---:|---:|---:|---:|---:|
| Generic LLM | 0.918 | 0.469 | 0.762 | 19/100 | 78/100 |
| Privacy-first LLM | 1.000 | 0.885 | 0.961 | 0/100 | 33/100 |
| Critical Span Guard | 1.000 | 0.978 | 0.987 | 0/100 | 5/100 |

## Domain Split

| Domain | Method | Direct span recall | Quasi span recall | All privacy span recall |
|---|---|---:|---:|---:|
| clinical | Generic LLM | 0.994 | 0.360 | 0.804 |
| clinical | Privacy-first LLM | 1.000 | 0.800 | 0.940 |
| clinical | Critical Span Guard | 1.000 | 1.000 | 1.000 |
| legal | Generic LLM | 0.842 | 0.577 | 0.720 |
| legal | Privacy-first LLM | 1.000 | 0.969 | 0.982 |
| legal | Critical Span Guard | 1.000 | 0.956 | 0.974 |

## Leaked Span Inventory

| Method | Direct leaked span instances | Top direct leaks | Quasi leaked span instances | Top quasi leaks |
|---|---:|---|---:|---|
| Generic LLM | 19 | `August 2, 2025` (1); `December 24, 2025` (1); `37645/97` (1); `52363/11` (1); `42007/98` (1); `35396/97` (1) | 145 | `teacher` (7); `software engineer` (7); `long-haul driver` (6); `postal worker` (6); `violin maker` (6); `retired judge` (6) |
| Privacy-first LLM | 0 | none | 35 | `postal worker` (6); `software engineer` (6); `dental hygienist` (6); `long-haul driver` (4); `farm manager` (3); `retired judge` (2) |
| Critical Span Guard | 0 | none | 8 | `resisting the exercise of official authority` (1); `Northern Ireland` (1); `1976` (1); `widows` (1); `homosexuality` (1); `homosexuals` (1) |

## Paper-Safe Interpretation

- CSG has perfect measured direct span recall on the promoted run and the strongest all-span recall, but it is still a deterministic string audit rather than a formal privacy guarantee.
- Generic prompting removes many obvious direct spans but leaves enough legal identifiers and quasi-identifiers to fail both row-level and span-level privacy checks.
- Privacy-first prompting reaches perfect direct span recall but still retains some quasi-identifying clinical or legal details while losing much more task-critical utility.
