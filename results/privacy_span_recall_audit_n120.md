# Privacy Span Recall Audit

Generated: 2026-06-28

This report surfaces the span-level privacy metrics already computed by `src/compute_metrics.py` for the promoted non-oracle run. Direct and quasi span recall measure the fraction of gold privacy spans not found verbatim in each anonymized output; they complement row-level direct-leak rate and QI-risk scoring.

## Gold Span Inventory

| Split | Rows | Direct spans | Quasi spans | Total privacy spans |
|---|---:|---:|---:|---:|
| overall | 120 | 549 | 358 | 907 |
| clinical | 60 | 420 | 180 | 600 |
| legal | 60 | 129 | 178 | 307 |

## Span Recall

| Method | Direct span recall | Quasi span recall | All privacy span recall | Direct leak rows | Quasi leak rows |
|---|---:|---:|---:|---:|---:|
| Generic LLM | 0.919 | 0.484 | 0.770 | 22/120 | 91/120 |
| Privacy-first LLM | 1.000 | 0.888 | 0.962 | 0/120 | 38/120 |
| Critical Span Guard | 1.000 | 0.969 | 0.980 | 0/120 | 9/120 |

## Domain Split

| Domain | Method | Direct span recall | Quasi span recall | All privacy span recall |
|---|---|---:|---:|---:|
| clinical | Generic LLM | 0.995 | 0.361 | 0.805 |
| clinical | Privacy-first LLM | 1.000 | 0.806 | 0.942 |
| clinical | Critical Span Guard | 1.000 | 1.000 | 1.000 |
| legal | Generic LLM | 0.843 | 0.606 | 0.735 |
| legal | Privacy-first LLM | 1.000 | 0.970 | 0.983 |
| legal | Critical Span Guard | 1.000 | 0.937 | 0.959 |

## Leaked Span Inventory

| Method | Direct leaked span instances | Top direct leaks | Quasi leaked span instances | Top quasi leaks |
|---|---:|---|---:|---|
| Generic LLM | 22 | `August 2, 2025` (1); `December 24, 2025` (1); `18753/04` (1); `35396/97` (1); `37770/97` (1); `5786/08` (1) | 169 | `dental hygienist` (8); `teacher` (8); `software engineer` (8); `farm manager` (8); `long-haul driver` (7); `violin maker` (7) |
| Privacy-first LLM | 0 | none | 41 | `dental hygienist` (8); `software engineer` (7); `postal worker` (7); `long-haul driver` (4); `farm manager` (3); `retired judge` (2) |
| Critical Span Guard | 0 | none | 17 | `Rom` (1); `British` (1); `10 September 2009` (1); `14 May 2009` (1); `14 years old` (1); `resisting the exercise of official authority` (1) |

## Paper-Safe Interpretation

- CSG has perfect measured direct span recall on the promoted run and the strongest all-span recall, but it is still a deterministic string audit rather than a formal privacy guarantee.
- Generic prompting removes many obvious direct spans but leaves enough legal identifiers and quasi-identifiers to fail both row-level and span-level privacy checks.
- Privacy-first prompting reaches perfect direct span recall but still retains some quasi-identifying clinical or legal details while losing much more task-critical utility.
