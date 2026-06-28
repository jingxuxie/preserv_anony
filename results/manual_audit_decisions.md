# Manual Audit Decisions

Date: 2026-06-27

Source artifact: `results/manual_audit_package.md`.

These decisions reflect the promoted legal-annotation benchmark and the 50-example non-oracle LLM run.

## Summary

| Example | Use status | Main lesson | Paper use |
|---|---|---|---|
| `clinical_0006` | Strong main example | Privacy-first removes clinical specifics; CSG preserves them while redacting identifiers. | Use as the clearest clinical utility-loss example. |
| `clinical_0029` | Metric nuance | Exact TCFR undercounts faithful clinical paraphrase; audited TCFR recovers it. | Use to explain exact-vs-audited TCFR. |
| `legal_0001` | Strong privacy example | Generic LLM leaks application number and date while preserving legal utility. | Use as a short direct-leak example. |
| `legal_0006` | Strong main example | Generic leaks legal identifier/date; privacy-first hides Article 6; CSG removes identifiers and preserves Article 6 plus claim. | Use as the clearest legal privacy-utility example. |
| `legal_0008` | Secondary privacy example | Generic leaks application number/date; CSG removes them and preserves Article 5 claim. | Use only if another direct-leak example is needed. |
| `legal_0018` | Metric nuance | CSG preserves the Article 1 home/possessions claim, but exact matching misses a wording change. | Use to discuss legal claim paraphrase and alias limits. |
| `legal_0023` | Strong utility example | Privacy-first hides Article 6; CSG preserves the exact legal basis and claim. | Use as compact legal utility-loss example. |
| `legal_0025` | Frontier example | CSG preserves Article 4 of Protocol No. 7 and the same-act acquittal claim, but retains the offence-description phrase as a measured QI hit. | Use only if discussing both residual frontier rows. |
| `legal_0047` | Secondary privacy example | Generic leaks application number and dates; CSG closes those leaks while preserving Article/outcome/claim. | Use only if space allows. |
| `legal_0005` | Frontier example | CSG preserves the exact legal claim but retains statute-specific quasi-identifiers; generic/privacy-first avoid those hits by losing claim specificity. | Use in limitations/frontier analysis. |

## Paper-Ready Example Set

Recommended compact qualitative set:

1. `clinical_0006`: privacy-first removes the clinically important answer.
2. `legal_0006`: generic leaks an application number/date, privacy-first removes the legal Article, CSG preserves the Article and claim while redacting identifiers.
3. `legal_0005`: CSG preserves the Article 6 / section 42 claim but retains statute-specific `Northern Ireland` and `1976` spans, showing the remaining legal privacy-utility frontier.

Use `clinical_0029` or `legal_0018` only when explaining why exact TCFR is conservative relative to audited/manual retention.

## Example-Level Decisions

### `clinical_0006`

Decision: use as a main clinical example.

Manual audit:

- Generic LLM preserves the clinical answer but retains exact age and occupation, so privacy risk remains.
- Privacy-first LLM removes or generalizes core utility: MCP joints, anti-CCP, rheumatoid arthritis, and methotrexate 15 mg weekly plus folic acid 1 mg daily.
- Critical Span Guard redacts direct identifiers, generalizes age/location/institution, and preserves the medication, dose, lab result, diagnosis, and symptoms.

Claim supported:

- A privacy-first instruction can preserve surface privacy while destroying the answer needed for downstream clinical QA.
- Task-aware preservation constraints can keep named medications/doses/labs without reintroducing direct identifiers.

### `clinical_0029`

Decision: use for metric discussion, not as a headline method example.

Manual audit:

- Exact TCFR marks the CSG output as missing "rebound tenderness was present at McBurney's point" because the anonymized text says "rebound tenderness at McBurney's point".
- This is a faithful paraphrase, so the exact scorer undercounts CSG.
- Generic LLM keeps major facts but loses specificity around McBurney's point and named antibiotics, while retaining age and occupation.
- Privacy-first LLM loses the 18-hour timeline and named antibiotics.

Claim supported:

- Exact/alias TCFR is reproducible but conservative; audited TCFR and manual examples are needed to distinguish paraphrase from real utility loss.

### `legal_0001`

Decision: use as a concise direct-leak example.

Manual audit:

- Generic LLM leaves application number `52363/11` and exact date.
- Privacy-first and CSG remove the application number/date while preserving Article 10 and the freedom-of-expression claim.

Claim supported:

- Generic "remove PII, preserve meaning" prompting can miss legal identifiers that are privacy-relevant but not semantically central.

### `legal_0006`

Decision: use as a main legal example.

Manual audit:

- Generic LLM leaves application number `37645/97` and exact date, while preserving Article 6.
- Privacy-first LLM removes the direct identifiers but replaces Article 6 with "a specified article", so the downstream Article question cannot be answered.
- Critical Span Guard removes the application number/name/date and preserves Article 6 plus the reasonable-time civil-proceedings claim.

Claim supported:

- Privacy and utility failures can occur in opposite directions on the same example: generic prompting leaks identifiers, while privacy-first prompting removes the legally critical answer.
- CSG gives the desired tradeoff on this case.

### `legal_0018`

Decision: use for legal metric nuance.

Manual audit:

- Generic LLM preserves Article 1 and the home/possessions claim.
- Privacy-first LLM hides Article 1 and generalizes the legal basis to "relevant articles".
- CSG preserves Article 1 and the substance of the claim, but exact matching misses the shift from "the peaceful enjoyment of her possessions" to "peaceful enjoyment of her possessions".

Claim supported:

- Legal claim facts are especially sensitive to wording; audited/manual retention is needed alongside exact TCFR.

### `legal_0005`

Decision: use as a residual frontier/error-analysis example.

Manual audit:

- Generic LLM removes the direct identifiers and quasi-identifiers, but generalizes the section 42 Fair Employment claim enough that the core-claim QA fails.
- Privacy-first LLM also avoids the measured QI hits, but removes Article 6 and the specific section 42 claim.
- CSG removes the application number, name, date, country, nationality, and other direct context while preserving Article 6 and the exact section 42 Fair Employment claim.
- The preserved claim still contains `Northern Ireland` and `1976` because they are embedded in the statute name, so the row remains a measured QI-risk case.

Claim supported:

- Some legal facts are simultaneously useful and identifying: statute/jurisdiction/year specificity may be needed for legal reasoning but still count as residual quasi-identifying context.

### `legal_0023`

Decision: use as a compact legal utility example if more than one legal example is needed.

Manual audit:

- Generic LLM preserves Article 6 and the length-of-proceedings claim.
- Privacy-first LLM generalizes Article 6 to "a procedural article", breaking the downstream Article question.
- CSG preserves Article 6 while redacting application number, country, institution, name, nationality, and date.

Claim supported:

- Privacy-first prompting often removes the precise legal basis even when that basis is task-critical and not itself a direct identifier.

### `legal_0025`

Decision: use only if discussing both residual frontier examples.

Manual audit:

- Generic LLM preserves Article 4 and the same-act acquittal claim, but retains exact dates and the offence-description phrase.
- Privacy-first LLM removes dates but still retains the offence-description phrase, and exact QA misses the core claim even though the fact judge treats it as preserved.
- CSG removes application number, name, country, nationality, and dates while preserving Article 4 of Protocol No. 7 and the same-act acquittal claim.
- The phrase `resisting the exercise of official authority` remains because it is embedded in the annotated legal claim, so the row remains a measured QI-risk case.

Claim supported:

- Offence-description specificity can be necessary for legal reasoning and still act as quasi-identifying text.

### `legal_0047`

Decision: secondary direct-leak example; do not foreground unless space allows.

Manual audit:

- Generic LLM leaves application number `17906/15` and exact dates.
- Privacy-first and CSG both preserve Article 6, inadmissibility, and the Court-of-Appeal reasoning claim.
- CSG redacts more identifiers than generic while preserving legal utility.

Claim supported:

- Generic legal anonymization can preserve meaning while still leaking formal case identifiers.

## Resulting Wording Discipline

Use:

- "CSG improves the observed privacy-utility tradeoff in this 50-example sample."
- "The deterministic safety/repair layer is responsible for the measured privacy improvement in the CSG ablation."
- "Exact TCFR undercounts faithful paraphrase; audited/manual checks help separate paraphrase from utility loss."
- "The remaining CSG legal privacy issue is statute/jurisdiction or offense-description specificity that can overlap with claim meaning."

Avoid:

- "The verifier improves performance." The current ablation does not show that.
- "Privacy-first anonymization always harms legal utility." Some legal rows preserve enough utility.
- "The LLM judge is ground truth." Manual audit finds where deterministic and judge scores both need interpretation.
- "CSG solves legal anonymization." `legal_0005` and `legal_0025` still retain some case-specific quasi-identifiers.
