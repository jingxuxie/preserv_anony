# Additional Experiment Plan for the Utility-Preserving Anonymization Paper

**Paper:** *Do Not Anonymize Away the Answer: Measuring Task-Critical Meaning Loss in Text De-identification*  
**Repo:** `jingxuxie/preserv_anony`  
**Current promoted result:** `n150`, 75 synthetic clinical vignettes + 75 TAB-derived legal snippets  
**Current main model:** `gpt-4.1-nano` for non-oracle anonymization and LLM-assisted fact judging

## 1. Current status

The paper already uses API-based experiments. The README promotes a non-oracle OpenAI `n150` run and the cache-only rebuild commands specify `--model gpt-4.1-nano` for both anonymization and fact judging. The usage report for the n100-to-n150 increment logs 400 API-backed cache rows and 353,187 total provider tokens for that increment alone. Therefore, do **not** claim that the paper has no API usage. A better wording is:

> We use a low-cost OpenAI model for the promoted non-oracle run and cache all responses. The experiments use only synthetic clinical text and public TAB-derived legal snippets; no real PHI is sent to the API.

The current results are already strong:

| Method | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA ↑ |
|---|---:|---:|---:|---:|---:|
| Generic LLM | 0.180 | 1.733 | 0.813 | 0.938 | 0.888 |
| Privacy-first LLM | 0.000 | 0.573 | 0.398 | 0.529 | 0.414 |
| Critical Span Guard | 0.000 | 0.127 | 0.884 | 0.994 | 0.974 |

The main risk is not that the results are weak. The main reviewer risks are:

1. The fact-retention judge uses the same low-cost model family as the anonymization run.
2. The privacy audit is mostly string/span-based, not an adversarial LLM-based leakage audit.
3. The benchmark labels are partly synthetic or heuristic.
4. The method’s strongest gain comes from the deterministic safety/repair layer, so the paper should explain this honestly.
5. The paper needs stronger evidence that results are not an artifact of one judge or one prompt style.

## Execution status update, 2026-06-28

- Priority A is complete on the bounded 60-example stratified subset: `results/gpt55_fact_judge_results_stratified60.md` and `results/gpt55_external_audit_comparison_fact60_privacyhard20.md`.
- Priority B is complete on the hard 20-example privacy subset: `results/gpt55_privacy_judge_results_hard20.md`.
- Priority C is partially complete without new API spend: `results/manual_audit_agreement_n150.md` now summarizes the fixed 30-example audit, verifies that the blinded second-annotator packet is complete, and records reference-label consistency. It is not independent human inter-rater agreement; the next step is still to have a second annotator complete `results/second_annotator_form_n150.csv`.
- Priority D now has a bounded n9 speed screen: `results/gpt55_model_upgrade_report_n9.md`. GPT-5.5 generic prompting removed measured direct leaks on this stress subset, but CSG still had the best GPT-5.5-audited TCFR (0.852 vs. generic 0.815 and privacy-first 0.333). Treat this as a pilot only; the full 30-example model-upgrade check remains future work.
- Priority E is partially complete through `results/openai_api_usage_n150.md` and `results/gpt55_external_audit_usage_report.md`; older n100 cache rows remain proxy-only.

## 2. Recommended experiment package

### Priority A — GPT-5.5 external fact-retention audit

**Goal:** Show that the TCFR result is not just an artifact of the `gpt-4.1-nano` judge.

Use GPT-5.5 as an independent judge, not as the main anonymizer. This is the most useful GPT-5.5 experiment because it strengthens the credibility of the existing results without changing the paper’s story that the method is low-cost.

**Design:**

- Input: existing anonymized outputs from `data/processed/openai_anonymized_outputs_n150.jsonl`.
- Judge model: `gpt-5.5`.
- Scope option 1: all 150 examples × 3 methods = 450 judged rows.
- Scope option 2: stratified subset of 60 examples × 3 methods = 180 judged rows.
- Stratification:
  - 20 clinical rows,
  - 20 legal rows,
  - 20 hard rows, including all residual CSG QI rows, all CSG audited-fact-loss rows, and high-similarity failure rows.

**Metrics:**

- GPT-5.5 audited TCFR by method.
- Difference between GPT-5.5 audited TCFR and current audited TCFR.
- Agreement rate on per-fact retained/not-retained labels.
- Disagreement categories: strict numeric/lab/dose, legal claim paraphrase, jurisdiction specificity, sensitive attribute overlap, judge error.

**Paper value:**

Add one small table:

| Method | Current audited TCFR | GPT-5.5 audited TCFR | Absolute delta | Main disagreement type |
|---|---:|---:|---:|---|
| Generic LLM | ... | ... | ... | ... |
| Privacy-first LLM | ... | ... | ... | ... |
| Critical Span Guard | ... | ... | ... | ... |

**Interpretation:**

- If GPT-5.5 agrees with the current judge: claim robustness across judge models.
- If GPT-5.5 is stricter: report the stricter number and use the disagreements as error analysis.
- If GPT-5.5 raises CSG failures: this is still useful; it makes the paper more honest and reviewer-resistant.

### Priority B — GPT-5.5 adversarial privacy audit

**Goal:** Strengthen privacy evaluation beyond direct string matching.

Current privacy metrics are strong but bounded: direct leak, span recall, and heuristic QI risk. Add an LLM adversary that sees only anonymized text and tries to identify remaining privacy risks.

**Prompt concept:**

> You are a privacy auditor. Given only the anonymized text, list any residual direct identifiers, quasi-identifiers, rare attributes, sensitive attributes, unique events, legal case-linkage clues, and combinations of details that could help re-identify a person or case. Return JSON with severity 0-3, evidence span, and explanation. Do not infer beyond the text.

**Design:**

- Run on the same rows as Priority A.
- Judge model: `gpt-5.5`.
- Compare against current deterministic QI flags.
- Score at row level:
  - `llm_privacy_flag`: any severity ≥ 2,
  - `llm_direct_flag`: direct identifier flagged,
  - `llm_qi_flag`: quasi-identifier or linkage detail flagged,
  - `overflag_rate`: flags that are clearly not privacy-relevant under manual review.

**Paper value:**

Add a result paragraph:

> A stronger GPT-5.5 privacy audit produces the same qualitative frontier: generic outputs remain privacy-risky, privacy-first outputs reduce leakage at large utility cost, and CSG has the fewest severe residual privacy flags except for policy-sensitive legal overlap cases.

If the LLM auditor flags more CSG cases, present them as residual-risk audit cases rather than failures. That fits the paper’s thesis.

### Priority C — Manual/second-annotator audit of the existing packet

**Goal:** Reduce dependence on LLM judges.

The repo already has a blinded second-annotator packet for 30 examples × 3 variants. Use it.

**Design:**

- Annotator sees original text, anonymized text, gold task facts, and QA items.
- Annotator labels each fact:
  - preserved,
  - acceptably generalized,
  - omitted,
  - contradicted,
  - unclear.
- Annotator also labels residual privacy risk:
  - direct identifier leak,
  - low-risk QI,
  - high-risk QI,
  - task-critical privacy/utility overlap,
  - no issue.

**Metrics:**

- Agreement with current audited TCFR.
- Agreement with deterministic privacy flags.
- Manual TCFR by method on the 30-example packet.
- Manual privacy-flag rate by method.

**Paper value:**

Even a small manual audit makes the paper much stronger because it shows the results are not purely self-judged by an LLM.

### Priority D — Add a small “model upgrade” anonymization sanity check

**Goal:** Answer the likely reviewer question: “Is CSG only better because the model is weak? Would a stronger model solve this with a generic prompt?”

Do **not** replace the main experiment with GPT-5.5. Instead, run a small sanity check.

**Design:**

- Select 30 examples:
  - 10 clinical,
  - 10 legal,
  - 10 hard/residual/frontier cases.
- Run three methods with GPT-5.5:
  - generic prompt,
  - privacy-first prompt,
  - CSG prompt.
- Score with the existing deterministic metrics plus GPT-5.5 or current fact judge.

**Expected paper contribution:**

This answers whether stronger general prompting removes the need for task-aware structure.

**Possible outcomes:**

- If GPT-5.5 generic still leaks or over-redacts: strong support for the method.
- If GPT-5.5 generic is much better: frame CSG as a cheap way to get similar behavior from low-cost models.
- If GPT-5.5 CSG improves further: claim the protocol is model-compatible, not model-specific.

### Priority E — Better cost accounting

**Goal:** Make the paper attractive to the workshop and aligned with your limited-compute story.

Add a short cost paragraph or appendix table:

| Experiment | Model | Rows | Calls | Input tokens | Output tokens | Estimated cost |
|---|---|---:|---:|---:|---:|---:|
| n150 anonymization | gpt-4.1-nano | 150 × 3 methods | ... | ... | ... | ... |
| n150 fact judge | gpt-4.1-nano | 450 | ... | ... | ... | ... |
| GPT-5.5 external audit | gpt-5.5 | 180 or 450 | ... | ... | ... | ... |

This makes a clear argument: the method is not a large-scale training paper; it is a low-cost evaluation and transformation protocol.

## 3. Should you use GPT-5.5?

Yes, but use it strategically.

The best use is **external audit**, not main anonymization. The current paper’s value proposition is that a structured, low-cost protocol improves the privacy-utility frontier. If you switch the whole paper to GPT-5.5 anonymization, the story becomes more expensive and less accessible. If you instead use GPT-5.5 as an independent judge/adversary, it strengthens the paper while preserving the low-cost method story.

Recommended ordering:

1. GPT-5.5 fact-retention audit on 60 stratified examples.
2. GPT-5.5 adversarial privacy audit on the same examples.
3. Manual audit of the same or overlapping 30 examples.
4. Optional GPT-5.5 anonymizer sanity check on 30 examples.

## 4. Implementation notes

### Add an ID filter to the fact judge

`src/run_fact_judge.py` currently supports `--methods` and `--cache-only`, but it does not appear to support an ID subset flag. Add one of these:

```python
parser.add_argument("--ids-file", default=None)
```

Then filter outputs:

```python
if args.ids_file:
    keep_ids = {line.strip() for line in open(args.ids_file) if line.strip()}
    outputs = [row for row in outputs if row["id"] in keep_ids]
```

This lets you reuse the existing judge infrastructure for GPT-5.5 without creating extra filtered files.

### Suggested command for GPT-5.5 fact audit

```bash
conda run -n preserv_anony python src/run_fact_judge.py \
  --benchmark data/processed/benchmark_n150_llm.jsonl \
  --model gpt-5.5 \
  --outputs data/processed/openai_anonymized_outputs_n150.jsonl \
  --ids-file data/processed/gpt55_audit_ids_60.txt \
  --out data/processed/gpt55_fact_judgments_stratified60.jsonl \
  --summary results/gpt55_fact_judge_summary_stratified60.json \
  --report results/gpt55_fact_judge_results_stratified60.md
```

### Suggested command for cache-only rebuild

```bash
conda run -n preserv_anony python src/run_fact_judge.py \
  --benchmark data/processed/benchmark_n150_llm.jsonl \
  --model gpt-5.5 \
  --outputs data/processed/openai_anonymized_outputs_n150.jsonl \
  --ids-file data/processed/gpt55_audit_ids_60.txt \
  --out data/processed/gpt55_fact_judgments_stratified60.jsonl \
  --summary results/gpt55_fact_judge_summary_stratified60.json \
  --report results/gpt55_fact_judge_results_stratified60.md \
  --cache-only
```

### Suggested new script: `src/run_privacy_judge.py`

Reuse the caching functions from `run_openai_methods.py`. The output schema should be simple:

```json
{
  "id": "legal_0005",
  "method": "critical_span_guard_extracted",
  "model": "gpt-5.5",
  "privacy_findings": [
    {
      "type": "quasi_identifier|direct_identifier|sensitive_attribute|linkage_combination",
      "severity": 0,
      "span": "...",
      "reason": "...",
      "task_critical_overlap": true
    }
  ],
  "max_severity": 0,
  "has_severe_flag": false
}
```

### Suggested adversarial privacy prompt

```text
You are a privacy auditor for anonymized clinical or legal text.

Anonymized text:
{anonymized_text}

Task: identify residual privacy risks visible in the anonymized text. Look for:
1. direct identifiers, including names, exact dates, application/case numbers, record numbers, contact details, and named institutions tied to a person;
2. quasi-identifiers, including rare occupation, specific location, age, nationality, family relation, rare event, exact statute/jurisdiction detail, sensitive attribute, or unusual combination of details;
3. facts that might be both task-critical and privacy-relevant.

Return only valid JSON:
{
  "findings": [
    {
      "type": "direct_identifier|quasi_identifier|sensitive_attribute|linkage_combination|none",
      "severity": 0-3,
      "span": "exact text span or empty string",
      "reason": "brief explanation",
      "task_critical_overlap": true or false
    }
  ],
  "overall_severity": 0-3,
  "summary": "brief summary"
}

Do not infer beyond the text. If there are no visible privacy risks, return an empty findings list and severity 0.
```

## 5. What to add to the paper after these experiments

### New Methods paragraph

Add a paragraph after the existing LLM-audited TCFR description:

> To test judge dependence, we additionally run an external GPT-5.5 audit on a stratified subset of examples. The external audit re-evaluates task-critical fact retention and residual privacy risk without changing the anonymized outputs. This isolates evaluation robustness from anonymization performance.

### New Results table

Add one compact table:

| Method | Current audited TCFR | GPT-5.5 TCFR | GPT-5.5 severe privacy flags | Manual TCFR subset |
|---|---:|---:|---:|---:|
| Generic LLM | ... | ... | ... | ... |
| Privacy-first LLM | ... | ... | ... | ... |
| Critical Span Guard | ... | ... | ... | ... |

### New Error Analysis paragraph

Write about disagreements, not just means:

> The GPT-5.5 judge was stricter on legal jurisdiction specificity and clinical diagnostic specificity. Most CSG disagreements came from policy-sensitive cases where the retained fact is also the answer, whereas privacy-first disagreements came from omitted legal claims and over-generalized clinical facts.

## 6. Minimum package if the deadline is very close

If you only have bandwidth for one addition, do this:

1. Run GPT-5.5 fact-retention audit on the 60-example stratified subset.
2. Add one table comparing current audited TCFR vs GPT-5.5 audited TCFR.
3. Add one paragraph saying this is an external judge robustness check.
4. Keep GPT-5.5 out of the main anonymization table.

That gives the largest credibility boost for the least implementation risk.

## 7. API and privacy caution

Use only synthetic clinical vignettes and public TAB-derived legal snippets in API calls. Do not send real PHI, private client documents, unpublished legal documents, or user data. Keep the paper’s ethics section clear: the work studies evaluation and transformation behavior, not compliance or safe release of real sensitive corpora.
