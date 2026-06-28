# Critical Span Guard Ablation

Cache-only ablation reconstructed from the 120-example non-oracle CSG run.

| Stage | N | Direct leak | Rows with direct leaks | QI risk | Rows with QI hits | TCFR | QA consistency | Edit rate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| csg_draft | 120 | 0.067 | 8 | 1.025 | 60 | 0.885 | 0.972 | 0.255 |
| csg_verified | 120 | 0.067 | 8 | 1.025 | 60 | 0.885 | 0.972 | 0.255 |
| csg_verified_safety | 120 | 0.000 | 0 | 0.142 | 9 | 0.889 | 0.979 | 0.275 |

## Domain split

| Domain | Stage | N | Direct leak | QI risk | TCFR | QA consistency |
|---|---|---:|---:|---:|---:|---:|
| clinical | csg_draft | 60 | 0.133 | 1.717 | 0.817 | 0.992 |
| clinical | csg_verified | 60 | 0.133 | 1.717 | 0.817 | 0.992 |
| clinical | csg_verified_safety | 60 | 0.000 | 0.000 | 0.819 | 1.000 |
| legal | csg_draft | 60 | 0.000 | 0.333 | 0.953 | 0.953 |
| legal | csg_verified | 60 | 0.000 | 0.333 | 0.953 | 0.953 |
| legal | csg_verified_safety | 60 | 0.000 | 0.283 | 0.958 | 0.958 |

## Interpretation

- The verify/repair pass did not change this cached sample under deterministic scoring; draft and verified rows are numerically identical.
- The deterministic safety scrub plus legal-Article, case-label, detention-regime, and medication repair closes the remaining direct clinical leak, most synthetic clinical quasi-identifier hits, the sampled legal Article over-generalization, the clean quoted case-label leak, and one utility-irrelevant detention-regime label.
- 9 legal examples remain flagged for quasi-identifiers after safety scrub (`legal_0002`, `legal_0005`, `legal_0025`, `legal_0042`, `legal_0046`, `legal_0053`, `legal_0054`, `legal_0055`, `legal_0056`); these are legal statute/jurisdiction or offense-description details that overlap with the claim meaning, so they should be framed as frontier cases rather than blindly scrubbed.

