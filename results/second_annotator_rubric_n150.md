# Second-Annotator Packet for Fixed n150 Audit

This packet is prepared for an independent annotation pass on the fixed n150 audit subset.

## Scope

- Sample version: `n150_fixed_30_second_annotator_v1`.
- Examples: 30 (clinical=15, legal=15).
- Variant rows: 90; each example has blinded variants `A`, `B`, and `C`.
- Method names, existing metric scores, fact-judge labels, and prior manual decisions are intentionally excluded from the annotator packet.
- The answer key is separate and should not be shared until annotation is complete.

## Files

- `data/processed/second_annotator_packet_n150.jsonl`: full blinded packet with original text, transformed text, gold spans, task facts, and QA.
- `results/second_annotator_form_n150.csv`: blank row-level annotation form.
- `results/second_annotator_answer_key_n150.json`: method mapping for post-annotation reconciliation only.

## Annotation Rubric

For each row, compare `transformed_text` against `original_text`, gold privacy spans, task facts, and QA pairs.

| Field | Allowed values | Guidance |
|---|---|---|
| `direct_identifier_retained` | `no`, `yes`, `uncertain` | Mark `yes` if a listed direct identifier or obvious direct alias remains. |
| `quasi_identifier_retained` | `no`, `yes`, `uncertain` | Mark `yes` if a listed quasi-identifier, rare occupation/location/attribute, exact date, or close equivalent remains. |
| `task_fact_retention` | `all`, `minor_loss`, `major_loss`, `uncertain` | `all` means all task facts are recoverable, including accepted generalizations. `major_loss` means at least one answer-critical fact is not recoverable. |
| `qa_answerability` | `all`, `some`, `none`, `uncertain` | Decide whether the provided questions can still be answered from the transformed text. |
| `contradiction_or_hallucination` | `no`, `yes`, `uncertain` | Mark `yes` if the transformed text changes a fact or introduces unsupported task-relevant content. |
| `privacy_utility_overlap` | `no`, `yes`, `uncertain` | Mark `yes` when a retained privacy-sensitive detail appears necessary for the task fact or QA target. |
| `notes` | free text | Briefly cite the retained/leaked span or lost fact. |

## Reconciliation Plan

After annotation, join the completed CSV with `results/second_annotator_answer_key_n150.json` by `example_id` and `variant_code`. Report agreement against the current single-author/manual-style labels separately from deterministic metrics. Do not claim inter-rater agreement until this form is completed by a second annotator.

## Blinded Variant Index

| Example | Domain | Variants |
|---|---|---|
| `clinical_0005` | clinical | A, B, C |
| `clinical_0006` | clinical | A, B, C |
| `clinical_0009` | clinical | A, B, C |
| `clinical_0011` | clinical | A, B, C |
| `clinical_0017` | clinical | A, B, C |
| `clinical_0023` | clinical | A, B, C |
| `clinical_0029` | clinical | A, B, C |
| `clinical_0031` | clinical | A, B, C |
| `clinical_0035` | clinical | A, B, C |
| `clinical_0041` | clinical | A, B, C |
| `clinical_0053` | clinical | A, B, C |
| `clinical_0055` | clinical | A, B, C |
| `clinical_0059` | clinical | A, B, C |
| `clinical_0065` | clinical | A, B, C |
| `clinical_0071` | clinical | A, B, C |
| `legal_0002` | legal | A, B, C |
| `legal_0005` | legal | A, B, C |
| `legal_0006` | legal | A, B, C |
| `legal_0016` | legal | A, B, C |
| `legal_0018` | legal | A, B, C |
| `legal_0025` | legal | A, B, C |
| `legal_0042` | legal | A, B, C |
| `legal_0046` | legal | A, B, C |
| `legal_0053` | legal | A, B, C |
| `legal_0054` | legal | A, B, C |
| `legal_0055` | legal | A, B, C |
| `legal_0056` | legal | A, B, C |
| `legal_0062` | legal | A, B, C |
| `legal_0063` | legal | A, B, C |
| `legal_0070` | legal | A, B, C |
