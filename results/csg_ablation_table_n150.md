# Critical Span Guard Ablation

Cache-only ablation reconstructed from the 150-example non-oracle CSG run.

| Stage | N | Direct leak | Rows with direct leaks | QI risk | Rows with QI hits | TCFR | QA consistency | Edit rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| csg_draft | 150 | 0.073 | 11 | 1.027 | 74 | 0.881 | 0.969 | 0.255 |
| csg_verified | 150 | 0.073 | 11 | 1.027 | 74 | 0.881 | 0.969 | 0.255 |
| csg_verified_safety | 150 | 0.000 | 0 | 0.127 | 11 | 0.884 | 0.974 | 0.274 |

## Domain split

| Domain | Stage | N | Direct leak | QI risk | TCFR | QA consistency |
|---|---|---:|---:|---:|---:|---:|
| clinical | csg_draft | 75 | 0.147 | 1.760 | 0.818 | 0.993 |
| clinical | csg_verified | 75 | 0.147 | 1.760 | 0.818 | 0.993 |
| clinical | csg_verified_safety | 75 | 0.000 | 0.000 | 0.820 | 1.000 |
| legal | csg_draft | 75 | 0.000 | 0.293 | 0.944 | 0.944 |
| legal | csg_verified | 75 | 0.000 | 0.293 | 0.944 | 0.944 |
| legal | csg_verified_safety | 75 | 0.000 | 0.253 | 0.949 | 0.949 |

## Interpretation

- The verify/repair pass did not change this cached sample under deterministic scoring; draft and verified rows are numerically identical.
- The deterministic safety scrub plus legal-Article, case-label, detention-regime, and medication repair closes the remaining direct clinical leak, most synthetic clinical quasi-identifier hits, the sampled legal Article over-generalization, the clean quoted case-label leak, and one utility-irrelevant detention-regime label.
- 11 legal examples remain flagged for quasi-identifiers after safety scrub (`legal_0002`, `legal_0005`, `legal_0025`, `legal_0042`, `legal_0046`, `legal_0053`, `legal_0054`, `legal_0055`, `legal_0056`, `legal_0062`, `legal_0063`); these are legal statute/jurisdiction or offense-description details that overlap with the claim meaning, so they should be framed as frontier cases rather than blindly scrubbed.

