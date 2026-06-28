# Baseline Bridge Report

This report separates deployable local baselines, gold-informed diagnostics, and the 50-example non-oracle LLM headline run. It is meant to prevent unfair comparisons between oracle rows and deployable systems.

## Full 100-Example Local Baselines and Oracles

| Method | Comparison role | N | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---|---:|---:|---:|---:|---:|---:|
| Regex rules | Deployable local baseline | 100 | 0.080 | 1.700 | 1.000 | NA | 1.000 |
| Presidio baseline | Deployable local baseline | 100 | 0.490 | 2.490 | 0.697 | NA | 0.802 |
| Direct-span oracle | Gold-informed diagnostic | 100 | 0.000 | 2.810 | 1.000 | NA | 1.000 |
| Privacy-first oracle | Gold-informed diagnostic | 100 | 0.000 | 0.010 | 0.478 | NA | 0.365 |
| CSG oracle | Gold-informed diagnostic | 100 | 0.000 | 0.170 | 1.000 | NA | 1.000 |

## Full 100-Example Domain Split

| Domain | Method | Direct leak | QI risk | Exact TCFR | QA |
|---|---|---:|---:|---:|---:|
| Clinical | Regex rules | 0.000 | 2.000 | 1.000 | 1.000 |
| Clinical | Presidio baseline | 0.000 | 2.000 | 0.440 | 0.650 |
| Clinical | Direct-span oracle | 0.000 | 3.000 | 1.000 | 1.000 |
| Clinical | Privacy-first oracle | 0.000 | 0.000 | 0.557 | 0.330 |
| Clinical | CSG oracle | 0.000 | 0.000 | 1.000 | 1.000 |
| Legal | Regex rules | 0.160 | 1.400 | 1.000 | 1.000 |
| Legal | Presidio baseline | 0.980 | 2.980 | 0.953 | 0.953 |
| Legal | Direct-span oracle | 0.000 | 2.620 | 1.000 | 1.000 |
| Legal | Privacy-first oracle | 0.000 | 0.020 | 0.400 | 0.400 |
| Legal | CSG oracle | 0.000 | 0.340 | 1.000 | 1.000 |

## 50-Example Non-Oracle LLM Run

| Method | Comparison role | N | Direct leak | QI risk | Exact TCFR | Audited TCFR | QA |
|---|---|---:|---:|---:|---:|---:|---:|
| Generic LLM | Non-oracle LLM baseline | 50 | 0.160 | 1.740 | 0.817 | 0.940 | 0.890 |
| Privacy-first LLM | Non-oracle LLM baseline | 50 | 0.000 | 0.660 | 0.430 | 0.567 | 0.440 |
| Critical Span Guard | Non-oracle proposed method | 50 | 0.000 | 0.080 | 0.897 | 1.000 | 0.990 |

## Bridge Interpretation

- Regex and direct-span oracle rows show why direct identifier removal is incomplete: they preserve task facts but retain high quasi-identifier risk.
- Presidio is a useful off-the-shelf baseline, but in this setup it misses many legal application identifiers and over-redacts some clinical task facts.
- Privacy-first oracle redaction is the opposite corner of the frontier: it nearly eliminates measured QI risk but removes many facts needed for downstream QA.
- CSG oracle is not deployable because it uses gold annotations, but it shows the target tradeoff is feasible when privacy spans and task facts are separated correctly.
- The non-oracle CSG result is the fair headline method comparison: it uses extracted structures rather than gold spans/facts at inference time.

## Paper-Safe Wording

Use the 100-example local table as a diagnostic baseline anchor, not as the main headline. The main deployable-method claim should come from the 50-example non-oracle LLM run, while the oracle rows should be described as upper-bound or frontier diagnostics.

## Compact Manuscript Sentence

A 100-example local diagnostic run gives the same qualitative frontier: regex and direct-span replacement preserve TCFR but leave high QI risk, Presidio misses many legal identifiers and loses clinical facts, and privacy-first oracle redaction protects privacy at large utility cost.
