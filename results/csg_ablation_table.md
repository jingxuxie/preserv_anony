# Critical Span Guard Ablation

Cache-only ablation reconstructed from the 50-example non-oracle CSG run.

| Stage | N | Direct leak | Rows with direct leaks | QI risk | Rows with QI hits | TCFR | QA consistency | Edit rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| csg_draft | 50 | 0.060 | 3 | 1.000 | 24 | 0.887 | 0.973 | 0.256 |
| csg_verified | 50 | 0.060 | 3 | 1.000 | 24 | 0.887 | 0.973 | 0.257 |
| csg_verified_safety | 50 | 0.000 | 0 | 0.080 | 2 | 0.897 | 0.990 | 0.278 |

## Domain split

| Domain | Stage | N | Direct leak | QI risk | TCFR | QA consistency |
|---|---|---:|---:|---:|---:|---:|
| clinical | csg_draft | 25 | 0.120 | 1.720 | 0.807 | 0.980 |
| clinical | csg_verified | 25 | 0.120 | 1.720 | 0.807 | 0.980 |
| clinical | csg_verified_safety | 25 | 0.000 | 0.000 | 0.813 | 1.000 |
| legal | csg_draft | 25 | 0.000 | 0.280 | 0.967 | 0.967 |
| legal | csg_verified | 25 | 0.000 | 0.280 | 0.967 | 0.967 |
| legal | csg_verified_safety | 25 | 0.000 | 0.160 | 0.980 | 0.980 |

## Interpretation

- The verify/repair pass did not change this cached sample under deterministic scoring; draft and verified rows are numerically identical.
- The deterministic safety scrub plus legal-Article, case-label, detention-regime, and medication repair closes the remaining direct clinical leak, most synthetic clinical quasi-identifier hits, the sampled legal Article over-generalization, the clean quoted case-label leak, and one utility-irrelevant detention-regime label.
- 2 legal examples remain flagged for quasi-identifiers after safety scrub (`legal_0005`, `legal_0025`); these are legal statute/jurisdiction or offense-description details that overlap with the claim meaning, so they should be framed as frontier cases rather than blindly scrubbed.

