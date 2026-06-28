# Critical Span Guard Ablation

Cache-only ablation reconstructed from the 70-example non-oracle CSG run.

| Stage | N | Direct leak | Rows with direct leaks | QI risk | Rows with QI hits | TCFR | QA consistency | Edit rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| csg_draft | 70 | 0.071 | 5 | 1.000 | 33 | 0.886 | 0.969 | 0.259 |
| csg_verified | 70 | 0.071 | 5 | 1.000 | 33 | 0.886 | 0.969 | 0.259 |
| csg_verified_safety | 70 | 0.000 | 0 | 0.057 | 2 | 0.893 | 0.981 | 0.281 |

## Domain split

| Domain | Stage | N | Direct leak | QI risk | TCFR | QA consistency |
|---|---|---:|---:|---:|---:|---:|
| clinical | csg_draft | 35 | 0.143 | 1.800 | 0.819 | 0.986 |
| clinical | csg_verified | 35 | 0.143 | 1.800 | 0.819 | 0.986 |
| clinical | csg_verified_safety | 35 | 0.000 | 0.000 | 0.824 | 1.000 |
| legal | csg_draft | 35 | 0.000 | 0.200 | 0.952 | 0.952 |
| legal | csg_verified | 35 | 0.000 | 0.200 | 0.952 | 0.952 |
| legal | csg_verified_safety | 35 | 0.000 | 0.114 | 0.962 | 0.962 |

## Interpretation

- The verify/repair pass did not change this cached sample under deterministic scoring; draft and verified rows are numerically identical.
- The deterministic safety scrub plus legal-Article, case-label, detention-regime, and medication repair closes the remaining direct clinical leak, most synthetic clinical quasi-identifier hits, the sampled legal Article over-generalization, the clean quoted case-label leak, and one utility-irrelevant detention-regime label.
- 2 legal examples remain flagged for quasi-identifiers after safety scrub (`legal_0005`, `legal_0025`); these are legal statute/jurisdiction or offense-description details that overlap with the claim meaning, so they should be framed as frontier cases rather than blindly scrubbed.

