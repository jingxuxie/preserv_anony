# Privacy Span Recall Audit

Generated: 2026-06-27

This report surfaces the span-level privacy metrics already computed by `src/compute_metrics.py` for the promoted non-oracle run. Direct and quasi span recall measure the fraction of gold privacy spans not found verbatim in each anonymized output; they complement row-level direct-leak rate and QI-risk scoring.

## Gold Span Inventory

| Split | Rows | Direct spans | Quasi spans | Total privacy spans |
|---|---:|---:|---:|---:|
| overall | 70 | 324 | 201 | 525 |
| clinical | 35 | 245 | 105 | 350 |
| legal | 35 | 79 | 96 | 175 |

## Span Recall

| Method | Direct span recall | Quasi span recall | All privacy span recall | Direct leak rows | Quasi leak rows |
|---|---:|---:|---:|---:|---:|
| Generic LLM | 0.921 | 0.475 | 0.772 | 13/70 | 53/70 |
| Privacy-first LLM | 1.000 | 0.895 | 0.967 | 0/70 | 21/70 |
| Critical Span Guard | 1.000 | 0.990 | 0.993 | 0/70 | 2/70 |

## Domain Split

| Domain | Method | Direct span recall | Quasi span recall | All privacy span recall |
|---|---|---:|---:|---:|
| clinical | Generic LLM | 0.996 | 0.371 | 0.809 |
| clinical | Privacy-first LLM | 1.000 | 0.800 | 0.940 |
| clinical | Critical Span Guard | 1.000 | 1.000 | 1.000 |
| legal | Generic LLM | 0.845 | 0.580 | 0.736 |
| legal | Privacy-first LLM | 1.000 | 0.990 | 0.994 |
| legal | Critical Span Guard | 1.000 | 0.979 | 0.986 |

## Leaked Span Inventory

| Method | Direct leaked span instances | Top direct leaks | Quasi leaked span instances | Top quasi leaks |
|---|---:|---|---:|---|
| Generic LLM | 13 | `August 2, 2025` (1); `37645/97` (1); `52363/11` (1); `42007/98` (1); `35396/97` (1); `18753/04` (1) | 97 | `software engineer` (6); `postal worker` (5); `violin maker` (5); `retired judge` (5); `long-haul driver` (4); `farm manager` (4) |
| Privacy-first LLM | 0 | none | 22 | `postal worker` (5); `software engineer` (5); `dental hygienist` (3); `long-haul driver` (2); `retired judge` (2); `farm manager` (2) |
| Critical Span Guard | 0 | none | 3 | `resisting the exercise of official authority` (1); `Northern Ireland` (1); `1976` (1) |

## Paper-Safe Interpretation

- CSG has perfect measured direct span recall on the promoted run and the strongest all-span recall, but it is still a deterministic string audit rather than a formal privacy guarantee.
- Generic prompting removes many obvious direct spans but leaves enough legal identifiers and quasi-identifiers to fail both row-level and span-level privacy checks.
- Privacy-first prompting reaches perfect direct span recall but still retains some quasi-identifying clinical or legal details while losing much more task-critical utility.
