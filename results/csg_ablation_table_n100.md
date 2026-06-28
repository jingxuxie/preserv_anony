# Critical Span Guard Ablation

Cache-only ablation reconstructed from the 100-example non-oracle CSG run.

| Stage | N | Direct leak | Rows with direct leaks | QI risk | Rows with QI hits | TCFR | QA consistency | Edit rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| csg_draft | 100 | 0.070 | 7 | 0.990 | 48 | 0.893 | 0.973 | 0.256 |
| csg_verified | 100 | 0.070 | 7 | 0.990 | 48 | 0.893 | 0.973 | 0.257 |
| csg_verified_safety | 100 | 0.000 | 0 | 0.090 | 5 | 0.898 | 0.982 | 0.278 |

## Domain split

| Domain | Stage | N | Direct leak | QI risk | TCFR | QA consistency |
|---|---|---:|---:|---:|---:|---:|
| clinical | csg_draft | 50 | 0.140 | 1.740 | 0.830 | 0.990 |
| clinical | csg_verified | 50 | 0.140 | 1.740 | 0.830 | 0.990 |
| clinical | csg_verified_safety | 50 | 0.000 | 0.000 | 0.833 | 1.000 |
| legal | csg_draft | 50 | 0.000 | 0.240 | 0.957 | 0.957 |
| legal | csg_verified | 50 | 0.000 | 0.240 | 0.957 | 0.957 |
| legal | csg_verified_safety | 50 | 0.000 | 0.180 | 0.963 | 0.963 |

## Interpretation

- The verify/repair pass did not change this cached sample under deterministic scoring; draft and verified rows are numerically identical.
- The deterministic safety scrub plus legal-Article, case-label, detention-regime, and medication repair closes the remaining direct clinical leak, most synthetic clinical quasi-identifier hits, the sampled legal Article over-generalization, the clean quoted case-label leak, and one utility-irrelevant detention-regime label.
- 5 legal examples remain flagged for quasi-identifiers after safety scrub (`legal_0002`, `legal_0005`, `legal_0025`, `legal_0042`, `legal_0046`); these are legal statute/jurisdiction or offense-description details that overlap with the claim meaning, so they should be framed as frontier cases rather than blindly scrubbed.

