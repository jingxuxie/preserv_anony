# Paper-Ready Tables

## Main 150-example non-oracle results.

| Method | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---|---|---|---|---|
| Generic LLM | 0.180 | 1.733 | 0.813 | 0.938 | 0.888 |
| Privacy-first LLM | 0.000 | 0.573 | 0.398 | 0.529 | 0.414 |
| Critical Span Guard | 0.000 | 0.127 | 0.884 | 0.994 | 0.974 |

## Domain split for the 150-example non-oracle run.

| Domain | Method | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---|---|---|---|---|---|
| Clinical | Generic LLM | 0.027 | 2.027 | 0.704 | 0.933 | 0.853 |
| Clinical | Privacy-first LLM | 0.000 | 1.067 | 0.193 | 0.458 | 0.227 |
| Clinical | Critical Span Guard | 0.000 | 0.000 | 0.820 | 0.996 | 1.000 |
| Legal | Generic LLM | 0.333 | 1.440 | 0.922 | 0.942 | 0.922 |
| Legal | Privacy-first LLM | 0.000 | 0.080 | 0.602 | 0.600 | 0.602 |
| Legal | Critical Span Guard | 0.000 | 0.253 | 0.949 | 0.993 | 0.949 |

## Critical Span Guard ablation.

| Stage | Direct leak | QI risk | Exact TCFR | QA |
|---|---|---|---|---|
| CSG draft | 0.073 | 1.027 | 0.881 | 0.969 |
| CSG verified | 0.073 | 1.027 | 0.881 | 0.969 |
| CSG + safety/repair | 0.000 | 0.127 | 0.884 | 0.974 |

## Surface similarity audit for generic utility metrics.

| Method | Token F1 | Edit rate | Audited fact-fail rate | Privacy-fail rate |
|---|---|---|---|---|
| Generic LLM | 0.776 | 0.247 | 0.240 | 0.747 |
| Privacy-first LLM | 0.577 | 0.464 | 0.793 | 0.273 |
| Critical Span Guard | 0.773 | 0.274 | 0.020 | 0.027 |

## Handwritten robustness stress slice.

| Method | Direct leak | QI risk | Exact TCFR | QA |
|---|---|---|---|---|
| Regex | 0.083 | 2.167 | 1.000 | 1.000 |
| Presidio | 0.667 | 2.667 | 0.817 | 0.833 |
| Direct-span oracle | 0.000 | 2.500 | 1.000 | 1.000 |
| Privacy-first oracle | 0.000 | 0.000 | 0.608 | 0.528 |
| CSG oracle | 0.000 | 0.667 | 1.000 | 1.000 |
