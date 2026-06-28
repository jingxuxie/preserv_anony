# Paper-Ready Tables

## Main 70-example non-oracle results.

| Method | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---|---|---|---|---|
| Generic LLM | 0.186 | 1.757 | 0.805 | 0.929 | 0.867 |
| Privacy-first LLM | 0.000 | 0.586 | 0.390 | 0.514 | 0.410 |
| Critical Span Guard | 0.000 | 0.057 | 0.893 | 0.993 | 0.981 |

## Domain split for the 70-example non-oracle run.

| Domain | Method | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---|---|---|---|---|---|
| Clinical | Generic LLM | 0.029 | 2.029 | 0.676 | 0.914 | 0.800 |
| Clinical | Privacy-first LLM | 0.000 | 1.143 | 0.190 | 0.433 | 0.229 |
| Clinical | Critical Span Guard | 0.000 | 0.000 | 0.824 | 1.000 | 1.000 |
| Legal | Generic LLM | 0.343 | 1.486 | 0.933 | 0.943 | 0.933 |
| Legal | Privacy-first LLM | 0.000 | 0.029 | 0.590 | 0.595 | 0.590 |
| Legal | Critical Span Guard | 0.000 | 0.114 | 0.962 | 0.986 | 0.962 |

## Critical Span Guard ablation.

| Stage | Direct leak | QI risk | Exact TCFR | QA |
|---|---|---|---|---|
| CSG draft | 0.071 | 1.000 | 0.886 | 0.969 |
| CSG verified | 0.071 | 1.000 | 0.886 | 0.969 |
| CSG + safety/repair | 0.000 | 0.057 | 0.893 | 0.981 |

## Surface similarity audit for generic utility metrics.

| Method | Token F1 | Edit rate | Audited fact-fail rate | Privacy-fail rate |
|---|---|---|---|---|
| Generic LLM | 0.768 | 0.256 | 0.271 | 0.757 |
| Privacy-first LLM | 0.564 | 0.476 | 0.800 | 0.286 |
| Critical Span Guard | 0.768 | 0.281 | 0.014 | 0.014 |

## Handwritten robustness stress slice.

| Method | Direct leak | QI risk | Exact TCFR | QA |
|---|---|---|---|---|
| Regex | 0.083 | 2.167 | 1.000 | 1.000 |
| Presidio | 0.667 | 2.667 | 0.817 | 0.833 |
| Direct-span oracle | 0.000 | 2.500 | 1.000 | 1.000 |
| Privacy-first oracle | 0.000 | 0.000 | 0.608 | 0.528 |
| CSG oracle | 0.000 | 0.667 | 1.000 | 1.000 |
