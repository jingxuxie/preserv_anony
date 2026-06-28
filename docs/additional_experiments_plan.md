# Additional Experiment Plan for the Utility-Preserving Anonymization Paper

**Paper:** *Do Not Anonymize Away the Answer: Measuring Task-Critical Meaning Loss in Text De-identification*  
**Current promoted result:** `n150`, 75 synthetic clinical vignettes + 75 TAB-derived legal snippets  
**Current main model:** `gpt-4.1-nano` for the promoted non-oracle anonymization and LLM-assisted fact judging

## 1. Current status

The paper already uses API-backed experiments. The README promotes a non-oracle OpenAI `n150` run, and the cache-only rebuild commands specify `--model gpt-4.1-nano` for anonymization and fact judging. The API-usage report for the n100-to-n150 increment logs provider token usage and cache coverage.

Do **not** claim that the paper has no API usage. A safer paper sentence is:

> We use a low-cost OpenAI model for the promoted non-oracle run and cache all responses. The experiments use only synthetic clinical text and public TAB-derived legal snippets; no real PHI is sent to the API.

Current headline table:

| Method | Direct leak ↓ | QI risk ↓ | Exact TCFR ↑ | Audited TCFR ↑ | QA ↑ |
|---|---:|---:|---:|---:|---:|
| Generic LLM | 0.180 | 1.733 | 0.813 | 0.938 | 0.888 |
| Privacy-first LLM | 0.000 | 0.573 | 0.398 | 0.529 | 0.414 |
| Critical Span Guard | 0.000 | 0.127 | 0.884 | 0.994 | 0.974 |

The main reviewer risks are:

1. The fact-retention judge uses the same low-cost model family as the anonymization run.
2. The privacy audit is mostly string/span-based rather than adversarial LLM-based.
3. The benchmark labels are partly synthetic or heuristic.
4. The strongest CSG gain comes from deterministic safety/repair, so the method should be described honestly.
5. The paper needs evidence that the result is not an artifact of one judge model or one prompt style.

## 2. Priority A — independent high-capability fact-retention audit

**Goal:** show that the TCFR result is not just an artifact of the current low-cost judge.

Use a stronger model as an independent judge, not as the main anonymizer. This strengthens credibility without changing the story that the proposed method is low-cost.

### Design

Input:

- `data/processed/openai_anonymized_outputs_n150.jsonl`
- `data/processed/benchmark_n150_llm.jsonl`

Scope options:

- Full audit: 150 examples × 3 methods = 450 judged rows.
- Budget audit: stratified 60 examples × 3 methods = 180 judged rows.

Recommended stratified 60-example subset:

- 20 clinical examples.
- 20 legal examples.
- 20 hard examples, including all residual CSG QI rows, all CSG audited-fact-loss rows, and high-similarity failure rows.

### Metrics

Report:

- independent audited TCFR by method,
- difference from current audited TCFR,
- agreement rate on per-fact retained/not-retained labels,
- disagreement categories.

Suggested table:

| Method | Current audited TCFR | Independent audited TCFR | Absolute delta | Main disagreement type |
|---|---:|---:|---:|---|
| Generic LLM | ... | ... | ... | ... |
| Privacy-first LLM | ... | ... | ... | ... |
| Critical Span Guard | ... | ... | ... | ... |

### Interpretation

- If the stronger judge agrees with the current judge, claim robustness across judge models.
- If the stronger judge is stricter, report the stricter number and use disagreements as error analysis.
- If the stronger judge raises CSG failures, this is still useful because it makes the paper more honest and reviewer-resistant.

## 3. Priority B — adversarial privacy audit

**Goal:** strengthen privacy evaluation beyond direct string matching.

Current privacy metrics are useful but bounded: direct leak, span recall, and heuristic QI risk. Add an LLM adversary that sees only anonymized text and tries to identify residual risks.

### Prompt concept

```text
You are a privacy auditor. Given only the anonymized text, list any residual direct identifiers, quasi-identifiers, rare attributes, sensitive attributes, unique events, legal case-linkage clues, and combinations of details that could help re-identify a person or case.

Return JSON with:
- severity: 0, 1, 2, or 3
- evidence span
- risk type
- explanation

Do not infer beyond the text.
```

### Metrics

- Mean adversarial risk severity.
- Fraction of rows with severity ≥ 2.
- Fraction of rows where the adversarial auditor identifies a risk not captured by deterministic QI scoring.
- Overlap with known residual CSG QI rows.

Suggested table:

| Method | Mean adversarial risk ↓ | Rows severity ≥2 ↓ | New risks beyond deterministic audit ↓ | Notes |
|---|---:|---:|---:|---|
| Generic LLM | ... | ... | ... | ... |
| Privacy-first LLM | ... | ... | ... | ... |
| Critical Span Guard | ... | ... | ... | ... |

### Why this matters

This answers the likely reviewer question: "Does the privacy result hold if an LLM auditor looks for residual risk rather than only matching known spans?"

## 4. Priority C — small high-capability anonymizer sanity check

**Goal:** test whether CSG still helps when the base anonymizer is stronger.

This should be a small experiment, not the main table.

### Design

Run on 30 hard examples:

- 10 clinical examples with medications, doses, labs, and exact timelines.
- 10 legal examples with Article/statute specificity.
- 10 hard/residual examples from the current audits.

Methods:

1. Strong-model generic anonymization.
2. Strong-model privacy-first anonymization.
3. Strong-model CSG, using the same extraction + preservation + deterministic safety layer structure.

### Expected outcomes

Possible outcomes and interpretations:

- If strong-model generic still leaks or over-redacts, the paper’s motivation is stronger.
- If strong-model privacy-first still removes task facts, the privacy--utility frontier remains real.
- If strong-model CSG improves over low-cost CSG, mention this as future headroom.
- If strong-model generic matches CSG on many rows, frame CSG as a low-cost way to induce stronger-model behavior.

Suggested text for paper:

> On a 30-example hard subset, a stronger-model anonymizer reduces some obvious formatting mistakes but does not remove the need for task-aware preservation constraints. Privacy-first prompting continues to over-generalize legal articles, clinical medications, or numeric values in several rows, while CSG-style structure makes the desired privacy--utility policy explicit.

## 5. Priority D — second-annotator or manual audit

**Goal:** reduce concern that the results depend on a single set of heuristic labels.

You already have `data/processed/second_annotator_packet_n150.jsonl`. Use it.

### Minimal version

Manually review 30 examples × 3 methods = 90 rows.

For each row, annotate:

- direct leak: yes/no,
- residual QI risk: 0–3,
- task facts retained: count,
- QA answer retained: yes/no,
- error category.

Report agreement with current automatic labels:

| Label | Agreement | Notes |
|---|---:|---|
| Direct leak | ... | ... |
| QI risk severe/non-severe | ... | ... |
| Fact retained/not-retained | ... | ... |
| QA retained/not-retained | ... | ... |

### Paper value

This makes the paper look much more serious, even if the manual audit is small. It also justifies using the current metrics as scalable proxies.

## 6. Priority E — add a small ablation of CSG components

The current ablation shows that the verification prompt did not change deterministic metrics and that deterministic safety/repair caused the measured improvement. That honesty is good. Add one more ablation if time allows:

1. Generic LLM.
2. CSG extraction + anonymization only.
3. CSG extraction + anonymization + verification.
4. CSG extraction + anonymization + deterministic safety.
5. Full CSG.

Report:

| Variant | Direct leak | QI risk | TCFR | QA | Takeaway |
|---|---:|---:|---:|---:|---|
| Generic | ... | ... | ... | ... | ... |
| CSG draft | ... | ... | ... | ... | ... |
| CSG + verify | ... | ... | ... | ... | ... |
| CSG + safety | ... | ... | ... | ... | ... |
| Full CSG | ... | ... | ... | ... | ... |

The key claim should be:

> The deterministic layer is not a cosmetic post-processing step; it operationalizes policy choices that single-pass LLM anonymization fails to apply reliably.

## 7. Recommended execution order

If time is tight, do only these:

1. Independent fact-retention audit on 60 stratified examples.
2. Adversarial privacy audit on the same 60 examples.
3. Manual audit of the same 60-example subset or the existing 30-example packet.

If you have one more day:

4. Strong-model anonymizer sanity check on 30 hard examples.
5. Add a concise table to the paper and move detailed disagreement examples to the appendix or repo.

## 8. Paper integration

Add one paragraph to Results:

> To test whether our audited utility results depend on the low-cost judge, we additionally ran an independent high-capability fact-retention audit on a stratified hard subset. The ranking was stable: CSG retained the most task-critical facts, privacy-first prompting remained substantially lower, and most disagreements involved strict jurisdictional or diagnostic specificity rather than direct contradictions.

Add one paragraph to Limitations:

> The independent audit is still model-assisted and should not be treated as expert annotation. Its purpose is to detect sensitivity to judge choice, not to replace human review.

## 9. Final recommendation

The best additional experiment is not "use a stronger model to make the method look better." The best experiment is:

> Use a stronger model as an external auditor and adversary to stress-test the current claims.

That makes the paper more credible while preserving the contribution: a low-cost, task-aware anonymization protocol plus a fact-level privacy--utility evaluation framework.
