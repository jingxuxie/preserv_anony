# Threat Model and Release Policy

Bounded privacy framing for the current utility-preserving anonymization study. This report is deliberately narrower than a formal anonymization guarantee.

## Release Scenario

- Intended setting: transforming sensitive text before controlled AI research use, evaluation, retrieval experiments, or dataset inspection.
- Data in this package: 75 synthetic clinical vignettes and 75 public TAB-derived ECHR snippets in the promoted non-oracle benchmark; 12 handwritten diagnostic stress examples.
- Primary release concern: whether transformed text still exposes direct identifiers or quasi-identifying facts while preserving the task-critical facts needed for downstream reasoning.
- Public-release posture: treat outputs as research artifacts requiring citation, provenance, license preservation, and residual-risk review before redistribution.

## Attacker Model

| Attacker capability | In scope? | How this package addresses it |
|---|---|---|
| String search for known direct identifiers such as names, emails, phone numbers, MRNs, legal application numbers, and exact dates. | yes | Measured by direct identifier leak rate and direct leaked spans. |
| Inspection of retained quasi-identifiers such as age, occupation, city, nationality, institution, sensitive status, statute labels, or event descriptions. | yes | Measured by heuristic QI risk and residual QI audit. |
| Task user who needs clinical or legal facts after transformation. | yes | Measured by exact TCFR, audited TCFR, and QA consistency. |
| Motivated adversary with external databases, linkage attacks, or case-specific background knowledge. | no | Explicitly out of scope; no k-anonymity, differential privacy, or adversarial re-identification guarantee is claimed. |
| Legal or regulatory compliance auditor. | no | The package is an empirical research study, not HIPAA, GDPR, court, or institutional compliance evidence. |

## Current Measured Residual Risk

| Method | Role | N | Direct leak rows | Mean direct leak | QI rows | Mean QI risk | Exact TCFR | QA |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Generic LLM | Non-oracle LLM baseline | 150 | 27 | 0.180 | 114 | 1.733 | 0.813 | 0.888 |
| Privacy-first LLM | Conservative non-oracle baseline | 150 | 0 | 0.000 | 45 | 0.573 | 0.398 | 0.414 |
| Critical Span Guard | Non-oracle proposed method | 150 | 0 | 0.000 | 11 | 0.127 | 0.884 | 0.974 |

CSG residual QI rows: legal_0002, legal_0005, legal_0025, legal_0042, legal_0046, legal_0053, legal_0054, legal_0055, legal_0056, legal_0062, legal_0063. Direct leak rows: 0/150.

## Frontier Cases

- The eleven residual CSG QI rows in the promoted 150-example run are legal task-critical overlap or frontier cases: `legal_0002`, `legal_0005`, `legal_0025`, `legal_0042`, `legal_0046`, `legal_0053`, `legal_0054`, `legal_0055`, `legal_0056`, `legal_0062`, and `legal_0063`.
- The stress slice shows the same issue under controlled diagnostics: CSG oracle preserves QA while retaining task-critical QI on 6/12 rows; privacy-first oracle removes QI but fails QA on 11/12 rows.
- This supports a policy-sensitive frontier claim rather than a claim that all residual QI is technically unavoidable.

## Policy Guidance

| Use case | Recommended policy | Rationale |
|---|---|---|
| Internal method evaluation | Use strict task annotations and report residual QI rows. | Keeps utility target measurable and makes frontier cases inspectable. |
| Public benchmark release | Share synthetic clinical rows as controlled examples with provenance; release TAB-derived legal subsets only with upstream license and residual-risk notes. | Clinical rows are synthetic; legal snippets remain public case text with sensitive allegations. |
| Privacy-aggressive downstream sharing | Consider generalized legal-claim annotations and rerun residual QI auditing. | Can reduce residual QI but changes the legal utility target. |
| Compliance or adversarial privacy claims | Do not use this package as sufficient evidence. | The metrics do not prove formal anonymization or protection against external-linkage attacks. |

## Paper-Safe Wording

We evaluate direct string leakage and heuristic quasi-identifier retention under a bounded release scenario. The method reduces measured direct and quasi-identifier risk on this sample, but it is not a formal anonymization guarantee and does not protect against motivated re-identification with external knowledge.

## Inventory Cross-Check

- Main benchmark domains: clinical=75, legal=75.
- Robustness CSG oracle QI risk: 0.667; privacy-first oracle QA: 0.528.

Status: PASS. Threat model is bounded and explicitly excludes formal anonymization, compliance, and adversarial linkage guarantees.
