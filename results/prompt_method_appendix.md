# Prompt and Method Appendix

Generated appendix for exact prompt transparency and implementation drift checks. The runner constants in `src/run_openai_methods.py` are authoritative for cached OpenAI calls.

## Prompt Inventory

| Prompt | Role | File | Lines | File SHA-256 | Runner constant | Normalized match |
|---|---|---|---:|---|---|---|
| Generic LLM anonymizer | Non-oracle baseline prompt. | `prompts/generic_anonymizer.txt` | 7 | `3bab6f1022312051` | `GENERIC_PROMPT` / `8e6de8ba0d95bde8` | yes |
| Privacy-first LLM anonymizer | Conservative non-oracle baseline prompt. | `prompts/privacy_first_anonymizer.txt` | 8 | `75505faeadda1676` | `PRIVACY_FIRST_PROMPT` / `dc48cfde7fed530e` | yes |
| CSG extraction prompt | Non-oracle extraction of privacy spans and task-critical facts. | `prompts/extract_privacy_and_facts.txt` | 27 | `86a8d7ccc028a961` | `EXTRACT_PRIVACY_AND_FACTS_PROMPT` / `76fcf9d3352b8f3f` | yes |
| CSG anonymization prompt | Non-oracle anonymization using extracted structures. | `prompts/critical_span_guard_extracted.txt` | 22 | `62abedf344da2435` | `CSG_EXTRACTED_PROMPT` / `555a48175ed3b93f` | yes |
| CSG verify/repair prompt | Verifier prompt used before deterministic safety/repair. | `prompts/verify_repair.txt` | 31 | `04056075aa87d451` | `CSG_VERIFY_REPAIR_PROMPT` / `b153a45587155ede` | yes |
| Gold-prompt CSG diagnostic | Gold-informed diagnostic prompt, not the headline method. | `prompts/critical_span_guard_goldprompt.txt` | 19 | `3601eaa2dd104c07` | `CSG_GOLD_PROMPT` / `836609677bf7ef57` | yes |

## Non-Oracle Boundary

- `generic_llm` uses only the source text and the generic anonymizer prompt.
- `privacy_first_llm` uses only the source text and the conservative privacy-first prompt.
- `critical_span_guard_extracted` first extracts privacy spans and task facts from the source text, then anonymizes from those extracted structures, then runs verify/repair, then applies deterministic safety/repair.
- `critical_span_guard_extracted` does not use gold `private_spans`, gold `task_critical_facts`, or gold QA at inference time.
- Gold annotations are used for evaluation, local oracle diagnostics, and fact-judge evaluation prompts, not for the headline non-oracle anonymizer inputs.
- Cache keys are SHA-256 hashes of the model, method, example id, and exact rendered prompt text in `src/run_openai_methods.py`.

## Deterministic Safety/Repair Layer

- Direct safety scrub for email, phone, MRN, record IDs, clinic/hospital names, legal application numbers, exact ages, and synthetic occupations.
- Legal Article placeholder repair to restore task-critical Article numbers when over-generalized.
- Legal case-label repair and detention-regime label generalization when the label is not task-critical.
- Clinical medication placeholder repair for task-critical treatment facts.

## Cache-Only Rebuild

`conda run -n preserv_anony python src/run_openai_methods.py --model gpt-4.1-nano --max-examples 50 --methods generic_llm privacy_first_llm critical_span_guard_extracted --cache-only`

## Drift Check

Status: PASS. Prompt files match the runner constants after normalizing placeholder names and Python-escaped JSON braces.
