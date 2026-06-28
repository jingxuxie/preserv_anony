# Paper-Ready Tables

## Main 120-example non-oracle results.

| Method | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---|---|---|---|---|
| Generic LLM | 0.183 | 1.742 | 0.818 | 0.939 | 0.892 |
| Privacy-first LLM | 0.000 | 0.600 | 0.406 | 0.542 | 0.422 |
| Critical Span Guard | 0.000 | 0.142 | 0.889 | 0.993 | 0.979 |

## Domain split for the 120-example non-oracle run.

| Domain | Method | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---|---|---|---|---|---|
| Clinical | Generic LLM | 0.033 | 2.033 | 0.703 | 0.928 | 0.850 |
| Clinical | Privacy-first LLM | 0.000 | 1.100 | 0.183 | 0.450 | 0.217 |
| Clinical | Critical Span Guard | 0.000 | 0.000 | 0.819 | 0.994 | 1.000 |
| Legal | Generic LLM | 0.333 | 1.450 | 0.933 | 0.950 | 0.933 |
| Legal | Privacy-first LLM | 0.000 | 0.100 | 0.628 | 0.633 | 0.628 |
| Legal | Critical Span Guard | 0.000 | 0.283 | 0.958 | 0.992 | 0.958 |

## Critical Span Guard ablation.

| Stage | Direct leak | QI risk | Exact TCFR | QA |
|---|---|---|---|---|
| CSG draft | 0.067 | 1.025 | 0.885 | 0.972 |
| CSG verified | 0.067 | 1.025 | 0.885 | 0.972 |
| CSG + safety/repair | 0.000 | 0.142 | 0.889 | 0.979 |

## Surface similarity audit for generic utility metrics.

| Method | Token F1 | Edit rate | Audited fact-fail rate | Privacy-fail rate |
|---|---|---|---|---|
| Generic LLM | 0.775 | 0.248 | 0.242 | 0.742 |
| Privacy-first LLM | 0.578 | 0.463 | 0.775 | 0.283 |
| Critical Span Guard | 0.772 | 0.275 | 0.025 | 0.033 |

## Handwritten robustness stress slice.

| Method | Direct leak | QI risk | Exact TCFR | QA |
|---|---|---|---|---|
| Regex | 0.083 | 2.167 | 1.000 | 1.000 |
| Presidio | 0.667 | 2.667 | 0.817 | 0.833 |
| Direct-span oracle | 0.000 | 2.500 | 1.000 | 1.000 |
| Privacy-first oracle | 0.000 | 0.000 | 0.608 | 0.528 |
| CSG oracle | 0.000 | 0.667 | 1.000 | 1.000 |
