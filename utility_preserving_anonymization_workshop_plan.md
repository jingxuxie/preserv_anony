# Concrete Workshop Paper Plan: Utility-Preserving Anonymization for Clinical and Legal Meaning

**Working title:** *Do Not Anonymize Away the Answer: Measuring Task-Critical Meaning Loss in Text De-identification*  
**Target venue:** Workshop on Responsibly Enabling Data for Foundation Models, COLM 2026  
**Recommended submission type:** 4-page short paper if the deadline is imminent; 8-page long paper if you have at least 1–2 weeks for a fuller study.  
**Compute assumption:** no local LLMs; limited API budget around $100; local CPU/Python tooling is okay.  
**Main research direction:** evaluate and reduce *utility loss* caused by de-identification/anonymization systems, especially when they remove or alter clinically or legally important facts.

---

## 1. One-sentence paper pitch

Current text de-identification systems are evaluated mostly by whether they remove private identifiers, but for sensitive data used in foundation-model workflows, the harder question is whether anonymization preserves the facts needed for downstream reasoning; this paper introduces a small benchmark, a task-critical meaning-retention metric, and a cheap two-pass anonymization method that preserves clinically/legal critical information while maintaining comparable privacy protection.

---

## 2. Why this is a good workshop paper

The workshop is specifically about responsibly unlocking sensitive data for foundation models, including data transformation, de-identification, anonymization, pseudonymization, and utility–privacy tradeoffs. This idea sits directly at that intersection.

The key gap is not “can we redact PII?” The more interesting gap is:

> **After de-identification, is the transformed text still useful for the task it was supposed to enable?**

For clinical and legal data, utility is not generic fluency. It is preservation of task-critical facts:

- Clinical: diagnosis, medication, dosage, allergy, symptom duration, lab value, temporal sequence, severity.
- Legal: party roles, procedural posture, legal claim, article/statute, court holding, outcome, chronology.

A system can achieve strong PII removal while destroying these facts. That failure is especially relevant for foundation models because de-identified corpora may later be used for RAG, supervised fine-tuning, evaluation, synthetic-data generation, or domain adaptation.

---

## 3. Core research questions

### RQ1: How often do anonymizers remove or alter task-critical meaning?

Measure whether common anonymization methods preserve domain-critical facts, not just whether they remove names, addresses, and dates.

### RQ2: Do common utility metrics miss these failures?

Test whether edit distance, embedding similarity, or semantic similarity can look acceptable even when the anonymized text changes the answer to a clinical/legal question.

### RQ3: Can a simple, low-cost, two-pass anonymization protocol improve utility without giving up privacy?

Propose a method that first identifies task-critical facts, then anonymizes with an explicit constraint to preserve those facts, and finally verifies/repairs the output.

---

## 4. Main claim you want to support

A strong workshop-level claim would be:

> **Span-level PII removal is an incomplete evaluation target for sensitive text transformation. A small amount of task-aware verification substantially reduces clinically/legal meaningful information loss at little additional privacy cost.**

A more cautious claim, suitable for a 4-page paper:

> **In a controlled benchmark of clinical-style and legal text, common anonymization prompts and PII tools frequently remove or alter task-critical facts; task-aware prompting plus verification reduces these errors and exposes a privacy–utility frontier that span-level metrics miss.**

---

## 5. Proposed contribution package

Aim for three contributions:

1. **Benchmark slice:** a small but carefully annotated benchmark of clinical-style and legal snippets with:
   - private identifiers,
   - task-critical facts,
   - downstream QA questions,
   - expected answers before/after anonymization.

2. **Metric:** **Task-Critical Fact Retention**, or **TCFR**:
   - percentage of gold task-critical facts preserved in the anonymized output,
   - plus a contradiction rate for facts that were not merely omitted but changed.

3. **Method:** **Critical Span Guard**, a cheap two-pass API-based anonymization protocol:
   - pass 1: identify privacy spans and task-critical facts,
   - pass 2: anonymize while preserving task-critical facts,
   - pass 3: verify and repair omissions/contradictions.

You do **not** need to train a model.

---

## 6. Recommended paper title options

Choose one:

1. **Do Not Anonymize Away the Answer: Measuring Task-Critical Meaning Loss in Text De-identification**
2. **When De-identification Changes the Facts: Utility-Preserving Anonymization for Sensitive Text**
3. **Beyond PII Recall: Task-Critical Utility Evaluation for Clinical and Legal Text Anonymization**
4. **Preserving the Reason: A Privacy–Utility Audit of Text Anonymization for Domain Reasoning**
5. **Redacted but Useless? Measuring Meaning Loss in Anonymized Clinical and Legal Documents**

My recommendation: **Do Not Anonymize Away the Answer**. It is memorable and directly conveys the problem.

---

## 7. Dataset plan

Use only public or synthetic data. Do **not** send real PHI, client data, private legal documents, or user data to APIs.

### 7.1 Minimum viable dataset for a short paper

Build **100–200 examples** total:

| Split | Examples | Source | Purpose |
|---|---:|---|---|
| Clinical-style synthetic vignettes | 50–100 | Generated from templates | Controlled clinical utility evaluation without PHI |
| Legal snippets | 50–100 | TAB / ECHR-derived public legal text | Realistic legal anonymization utility evaluation |

This is enough for a workshop short paper if the annotation quality is good.

### 7.2 Stronger dataset for an 8-page paper

Build **300–500 examples**:

| Split | Examples | Source | Purpose |
|---|---:|---|---|
| Clinical-style synthetic vignettes | 150–250 | Template-generated + API paraphrased | Controlled evaluation with known ground truth |
| Legal snippets | 150–250 | TAB snippets around annotated entities | Public legal anonymization evaluation |
| Optional stress-test split | 50 | Handwritten adversarial examples | Dates, rare occupations, multi-party cases, subtle quasi-identifiers |

### 7.3 Clinical-style synthetic vignette design

Each clinical example should include:

- direct PII: patient name, clinic/hospital, city, exact date, phone/email, medical record number;
- quasi-identifiers: age, occupation, rare location, unusual disease/timeline;
- clinical-critical facts: symptoms, duration, diagnosis, medication, dose, lab value, imaging result, allergy, treatment plan;
- 1–3 downstream questions whose answers depend on those clinical facts.

Example schema:

```json
{
  "id": "clinical_042",
  "text": "Maria Lopez, a 43-year-old teacher from Santa Fe, visited North Ridge Clinic on March 3, 2025. She reported 3 weeks of morning stiffness in both hands, swelling of the MCP joints, and fatigue. ESR was elevated and anti-CCP was positive. Dr. Nguyen started methotrexate 15 mg weekly and folic acid.",
  "private_spans": ["Maria Lopez", "Santa Fe", "North Ridge Clinic", "March 3, 2025", "Dr. Nguyen"],
  "task_critical_facts": [
    ["age", "43-year-old"],
    ["symptom", "3 weeks of morning stiffness"],
    ["finding", "MCP joint swelling"],
    ["lab", "anti-CCP positive"],
    ["medication", "methotrexate 15 mg weekly"],
    ["medication", "folic acid"]
  ],
  "qa": [
    {"q": "What medication was started?", "a": "methotrexate 15 mg weekly and folic acid"},
    {"q": "Which lab result supports the suspected diagnosis?", "a": "positive anti-CCP"}
  ]
}
```

Important: the point is not to provide medical advice. The point is to test whether de-identification preserves the facts already present in the text.

### 7.4 Legal snippet design

Use the Text Anonymization Benchmark (TAB) as the main public legal source. TAB contains English-language European Court of Human Rights cases annotated for personal identifiers, masking decisions, confidential attributes, and coreference relations.

For each legal snippet, store:

- direct identifiers: applicant names, relatives, addresses, institutions where appropriate;
- legal-critical facts: roles, claims, court article/statute, alleged violation, procedural sequence, court outcome;
- 1–3 downstream questions.

Example schema:

```json
{
  "id": "legal_017",
  "text": "The applicant, Mr. A., complained under Article 6 that the domestic courts had refused to examine his appeal after the filing deadline was miscalculated by his lawyer. The Court held that there had been no violation because the applicant had been informed of the procedural requirements.",
  "private_spans": ["Mr. A."],
  "task_critical_facts": [
    ["legal_basis", "Article 6"],
    ["claim", "refusal to examine appeal"],
    ["reason", "filing deadline miscalculated by lawyer"],
    ["outcome", "no violation"]
  ],
  "qa": [
    {"q": "Which Article was invoked?", "a": "Article 6"},
    {"q": "What was the Court's outcome?", "a": "no violation"}
  ]
}
```

---

## 8. Methods to compare

Use 4–6 methods. Keep it small and clean.

### Method 0: Original text

Used only as reference. Do not treat as a release candidate.

### Method 1: Regex baseline

Simple patterns for:

- emails,
- phone numbers,
- dates,
- medical record numbers,
- obvious names from synthetic examples.

Why include it: it is a weak but interpretable baseline.

### Method 2: Presidio baseline

Use Microsoft Presidio for PII detection and anonymization. It is an appropriate baseline because it is widely used, easy to run, and designed for sensitive data de-identification workflows.

Suggested replacement strategy:

- `PERSON` → `[PERSON]`
- `LOCATION` → `[LOCATION]`
- `DATE_TIME` → `[DATE]`
- `EMAIL_ADDRESS` → `[EMAIL]`
- `PHONE_NUMBER` → `[PHONE]`
- IDs → `[ID]`

### Method 3: Generic LLM anonymizer

Use a low-cost API model with a generic prompt:

> Remove or replace all personally identifying information. Preserve the meaning of the document.

This is important because many real users do exactly this.

### Method 4: Privacy-first LLM anonymizer

Use an intentionally conservative prompt:

> Remove or generalize any information that could identify a person, including names, dates, locations, organizations, rare occupations, and unique events. When uncertain, remove the information.

This method will probably improve privacy but harm utility. It helps reveal the privacy–utility frontier.

### Method 5: Critical Span Guard — your proposed method

This is the main contribution.

Pipeline:

1. **Extract task-critical facts.**
   Ask the model to list clinical/legal facts that must be preserved for downstream reasoning.

2. **Extract privacy spans.**
   Ask the model to list direct identifiers and quasi-identifiers.

3. **Classify overlaps.**
   Some spans are both privacy-relevant and utility-critical. Examples:
   - age,
   - exact date,
   - rare disease,
   - location,
   - relationship,
   - legal article,
   - court/institution.

4. **Apply transformation policy.**
   - Direct identifiers: replace with typed placeholders.
   - Utility-irrelevant quasi-identifiers: remove or generalize.
   - Utility-critical quasi-identifiers: generalize just enough to reduce identifiability.
   - Domain-critical facts: preserve unless they are direct identifiers.

5. **Verify and repair.**
   Run a second API call to check whether the anonymized text preserved all task-critical facts and did not reintroduce PII. If it failed, ask for a repaired version.

---

## 9. Transformation policy for Critical Span Guard

### 9.1 Clinical policy

| Original span type | Example | Transformation |
|---|---|---|
| Patient name | “Maria Lopez” | `[PATIENT]` |
| Clinician name | “Dr. Nguyen” | `[CLINICIAN]` |
| Hospital/clinic | “North Ridge Clinic” | `[CLINIC]` or “a clinic” |
| Exact date | “March 3, 2025” | “on the visit date” or “day 0” |
| Age | “43-year-old” | preserve if clinically relevant; otherwise “adult” or “early 40s” |
| City | “Santa Fe” | “a city in the Southwest” or `[LOCATION]` |
| Rare occupation | “violin maker” | “manual worker” / “artisan” |
| Diagnosis | “rheumatoid arthritis” | preserve |
| Medication/dose | “methotrexate 15 mg weekly” | preserve |
| Lab value | “anti-CCP positive” | preserve |
| Timeline | “3 weeks of morning stiffness” | preserve |

### 9.2 Legal policy

| Original span type | Example | Transformation |
|---|---|---|
| Applicant name | “Mr. Ivan Petrov” | `[APPLICANT]` |
| Relative name | “his daughter Elena” | “his daughter” |
| City/address | “12 King Street, Sofia” | `[ADDRESS]` or “a city in Bulgaria” |
| Exact date | “17 May 2017” | “the filing date” or “in 2017” depending on utility |
| Court article/statute | “Article 6” | preserve |
| Procedural role | “applicant”, “domestic court” | preserve |
| Outcome | “violation”, “no violation”, “inadmissible” | preserve |
| Legal claim | “lack of access to court” | preserve |
| Institution | “Sofia Regional Court” | generalize if identifying; preserve type as “regional court” |

---

## 10. Evaluation metrics

### 10.1 Privacy metrics

Use at least three privacy metrics:

#### P1. Direct identifier leak rate

For each example, check whether any gold direct identifier remains in the anonymized output.

```text
Direct Identifier Leak Rate = examples with leaked direct identifier / total examples
```

#### P2. PII span recall / false negative rate

If gold spans are available:

```text
PII Recall = removed_gold_pii_spans / total_gold_pii_spans
PII FNR = 1 - PII Recall
```

For synthetic clinical data, you control the gold spans. For TAB, use the annotated spans.

#### P3. Quasi-identifier leakage score

Score whether high-risk quasi-identifiers remain:

- exact date,
- rare location,
- named institution,
- rare occupation,
- specific relationship + location combination,
- unusual event.

Use a 0–3 scale:

| Score | Meaning |
|---:|---|
| 0 | no meaningful quasi-identifiers remain |
| 1 | broad quasi-identifiers remain |
| 2 | specific quasi-identifiers remain |
| 3 | specific combination could plausibly re-identify |

Use an API judge plus manual audit on a subset.

---

### 10.2 Utility metrics

#### U1. Task-Critical Fact Retention, TCFR

This is your main metric.

```text
TCFR = preserved_task_critical_facts / total_task_critical_facts
```

A fact counts as preserved if the anonymized text entails the fact at the intended granularity.

Examples:

- Original: “methotrexate 15 mg weekly”  
  Anonymized: “methotrexate 15 mg weekly” → preserved.
- Original: “methotrexate 15 mg weekly”  
  Anonymized: “a medication” → not preserved.
- Original: “Article 6”  
  Anonymized: “a human rights article” → not preserved for legal QA.
- Original: “March 3, 2025”  
  Anonymized: “day 0” → preserved if only sequence matters; not preserved if exact date is legally required.

#### U2. Critical contradiction rate, CCR

Contradictions are worse than omissions.

```text
CCR = contradicted_task_critical_facts / total_task_critical_facts
```

Examples:

- “anti-CCP positive” → “anti-CCP negative” is a contradiction.
- “no violation” → “violation” is a contradiction.
- “methotrexate” → “metformin” is a contradiction.

#### U3. QA consistency

For each example, ask the same downstream questions on original and anonymized text.

```text
QA Consistency = questions where anonymized answer matches original answer / total questions
```

This is easy to explain in a workshop paper.

#### U4. Generic semantic similarity

Compute one generic metric, such as embedding cosine similarity or BERTScore, to show that generic similarity does not fully capture domain-critical loss.

You do not need to overemphasize this metric. It is mostly a foil.

#### U5. Edit rate

```text
Edit Rate = changed_tokens / original_tokens
```

Useful for showing that a method is not simply preserving utility by barely anonymizing.

---

## 11. Suggested API-judging protocol

Use a low-cost model for most judgments and optionally a stronger model or manual review for audit.

### 11.1 Structured fact-retention judge

Input:

- original text,
- anonymized text,
- gold task-critical facts.

Output JSON:

```json
{
  "fact_judgments": [
    {
      "fact": "methotrexate 15 mg weekly",
      "status": "preserved",
      "evidence": "The anonymized text states methotrexate 15 mg weekly."
    },
    {
      "fact": "anti-CCP positive",
      "status": "omitted",
      "evidence": "The anonymized text only says lab tests were abnormal."
    }
  ],
  "summary": {
    "preserved": 1,
    "omitted": 1,
    "contradicted": 0
  }
}
```

Allowed statuses:

- `preserved`
- `generalized_but_acceptable`
- `omitted`
- `contradicted`
- `unclear`

For the headline metric, count `preserved` and `generalized_but_acceptable` as retained only when the gold annotation says generalization is acceptable.

### 11.2 Privacy judge

Input:

- original text,
- anonymized text,
- known private spans.

Output JSON:

```json
{
  "direct_identifier_leaks": ["North Ridge Clinic"],
  "quasi_identifier_risks": [
    {
      "span": "43-year-old teacher from Santa Fe",
      "risk_level": 2,
      "reason": "specific age, occupation, and city combination"
    }
  ],
  "overall_privacy_score": 2
}
```

Use this to supplement deterministic gold-span matching.

### 11.3 Manual audit

Manually review at least:

- 20 clinical examples × all methods, or
- 10% of all examples × all methods.

Report inter-rater agreement only if you have another annotator. If you are solo, report “single-author manual audit” and be transparent.

---

## 12. Prompt templates

### 12.1 Generic anonymizer prompt

```text
You are de-identifying sensitive text before it is used for AI research.
Remove or replace personally identifying information, including names, addresses, exact dates, contact information, IDs, institutions, and other details that could identify a person.
Preserve the meaning of the document as much as possible.
Return only the anonymized text.

Text:
{TEXT}
```

### 12.2 Privacy-first anonymizer prompt

```text
You are de-identifying sensitive text before it is used for AI research.
Your priority is privacy protection.
Remove, replace, or generalize any information that could identify a person, including direct identifiers, rare locations, exact dates, named institutions, rare occupations, unique events, and combinations of details.
When uncertain, generalize or remove the information.
Return only the anonymized text.

Text:
{TEXT}
```

### 12.3 Critical fact extraction prompt

```text
You are helping evaluate whether anonymization preserves task-critical meaning.
Given the text below, extract facts that must be preserved for downstream domain reasoning.

For clinical-style text, preserve symptoms, diagnosis, medication, dose, allergy, lab result, imaging result, temporal sequence, severity, and clinically relevant age/sex only when needed.
For legal text, preserve party roles, legal basis, claim, procedure, court reasoning, outcome, chronology, and statute/article references.

Do not include names, addresses, phone numbers, emails, or record IDs unless they are essential to the domain task.

Return JSON with this schema:
{
  "domain": "clinical" or "legal",
  "task_critical_facts": [
    {"type": "...", "fact": "...", "generalization_allowed": true/false, "reason": "..."}
  ]
}

Text:
{TEXT}
```

### 12.4 Privacy span extraction prompt

```text
You are auditing sensitive text for privacy risks.
Identify direct identifiers and quasi-identifiers.

Direct identifiers include names, contact details, addresses, exact dates, IDs, account numbers, and named institutions tied to a person.
Quasi-identifiers include age, occupation, city, rare disease/event, family relation, and combinations of details that may enable re-identification.

Return JSON:
{
  "direct_identifiers": [{"span": "...", "type": "..."}],
  "quasi_identifiers": [{"span": "...", "type": "...", "risk": 0-3, "reason": "..."}]
}

Text:
{TEXT}
```

### 12.5 Critical Span Guard anonymizer prompt

```text
You are anonymizing sensitive text for AI research.
You must protect privacy while preserving task-critical domain meaning.

Privacy spans to remove or generalize:
{PRIVACY_SPANS_JSON}

Task-critical facts to preserve:
{TASK_CRITICAL_FACTS_JSON}

Rules:
1. Replace direct identifiers with typed placeholders such as [PATIENT], [PERSON], [CLINICIAN], [COURT], [LOCATION], [DATE], [ID].
2. Generalize quasi-identifiers when possible instead of deleting them.
3. Preserve task-critical facts needed for clinical or legal reasoning.
4. If a span is both privacy-relevant and task-critical, preserve the least identifying version that keeps the downstream meaning.
5. Do not invent new facts.
6. Return only the anonymized text.

Original text:
{TEXT}
```

### 12.6 Verification and repair prompt

```text
You are verifying anonymized text.
Compare the original and anonymized text using the task-critical facts and privacy spans below.

Original text:
{ORIGINAL_TEXT}

Anonymized text:
{ANONYMIZED_TEXT}

Task-critical facts:
{TASK_CRITICAL_FACTS_JSON}

Known privacy spans:
{PRIVACY_SPANS_JSON}

Check for:
1. leaked direct identifiers,
2. high-risk quasi-identifiers,
3. omitted task-critical facts,
4. contradicted task-critical facts,
5. invented facts.

If the anonymized text is acceptable, return:
{"status": "accept", "text": "..."}

If not, return:
{"status": "repair", "issues": [...], "text": "REPAIRED_ANONYMIZED_TEXT"}

The repaired text must not reintroduce direct identifiers.
```

### 12.7 QA consistency prompt

```text
Answer the question using only the provided text.
Return JSON: {"answer": "...", "evidence": "..."}

Text:
{TEXT}

Question:
{QUESTION}
```

---

## 13. Experiment matrix

### Minimum viable short-paper matrix

| Dataset | Examples | Methods | Metrics |
|---|---:|---|---|
| Synthetic clinical | 50 | Regex, Presidio, generic LLM, Critical Span Guard | PII leak, TCFR, CCR, QA consistency |
| Legal TAB snippets | 50 | Regex, Presidio, generic LLM, Critical Span Guard | PII leak, TCFR, CCR, QA consistency |

This is enough for a clear 4-page paper.

### Stronger long-paper matrix

| Dataset | Examples | Methods | Metrics |
|---|---:|---|---|
| Synthetic clinical | 150–250 | Regex, Presidio, generic LLM, privacy-first LLM, utility-aware LLM, Critical Span Guard | All metrics |
| Legal TAB snippets | 150–250 | Same | All metrics |
| Stress tests | 50 | Best 3 methods | Failure taxonomy |

---

## 14. Expected results and hypotheses

You can pre-register these hypotheses internally:

### H1: Presidio/regex will preserve many clinical/legal facts but miss contextual privacy risks.

Because these methods mostly operate over recognizable PII spans, they may leave quasi-identifiers and role-specific contextual clues.

### H2: Privacy-first LLM anonymization will reduce quasi-identifier risk but hurt TCFR and QA consistency.

This method is likely to remove dates, locations, ages, organizations, and rare events. Some of those are task-critical.

### H3: Generic LLM anonymization will have variable behavior and occasional hallucination/meaning drift.

This gives you an important qualitative finding even if the average metrics look good.

### H4: Critical Span Guard will improve TCFR and QA consistency over generic/privacy-first anonymization at similar direct identifier leak rates.

This is the main positive result you want.

### H5: Generic semantic similarity will correlate weakly with TCFR/QA consistency.

This supports the claim that domain utility needs targeted evaluation.

---

## 15. Figures and tables to include

### Figure 1: Privacy–utility frontier

X-axis: privacy risk, e.g. quasi-identifier leakage score or direct leak rate.  
Y-axis: TCFR or QA consistency.  
Each point is a method.

Expected story:

- regex/Presidio: high utility, moderate privacy risk;
- privacy-first LLM: lower privacy risk, lower utility;
- generic LLM: unstable;
- Critical Span Guard: better balance.

### Figure 2: Semantic similarity vs TCFR

Scatter plot showing examples where semantic similarity is high but TCFR is low. These are compelling failure cases.

### Table 1: Main quantitative results

| Method | Direct leak ↓ | QI risk ↓ | TCFR ↑ | CCR ↓ | QA consistency ↑ | Edit rate ↓ |
|---|---:|---:|---:|---:|---:|---:|
| Regex | ... | ... | ... | ... | ... | ... |
| Presidio | ... | ... | ... | ... | ... | ... |
| Generic LLM | ... | ... | ... | ... | ... | ... |
| Privacy-first LLM | ... | ... | ... | ... | ... | ... |
| Critical Span Guard | ... | ... | ... | ... | ... | ... |

### Table 2: Error taxonomy

| Error type | Clinical example | Legal example | Common method |
|---|---|---|---|
| Medication removed | dose replaced by `[NUMBER]` | N/A | regex/overzealous |
| Legal basis removed | N/A | “Article 6” replaced by `[ID]` | regex/LLM |
| Outcome changed | N/A | “no violation” changed to “violation” | LLM |
| Timeline destroyed | “3 weeks” removed | filing sequence removed | privacy-first |
| Quasi-ID leak | rare disease + city retained | named institution + exact date retained | Presidio/generic |

### Table 3: Cost and latency

Show that the approach is feasible under limited API budget.

---

## 16. API budget estimate

Keep API calls small and batched.

A conservative 200-example run:

| Component | Approx calls | Approx tokens/call | Approx total tokens |
|---|---:|---:|---:|
| Generate synthetic clinical data | 100 | 1,000–1,500 | 100k–150k |
| Generic LLM anonymization | 200 | 1,200–1,800 | 240k–360k |
| Privacy-first anonymization | 200 | 1,200–1,800 | 240k–360k |
| Critical Span Guard extraction | 200 | 1,500–2,500 | 300k–500k |
| Critical Span Guard anonymization | 200 | 1,500–2,500 | 300k–500k |
| Verification/repair | 200 | 2,000–3,000 | 400k–600k |
| QA consistency judging | 1,000–1,500 | 700–1,200 | 700k–1.8M |
| Privacy/utility judging | 1,000 | 1,000–1,500 | 1M–1.5M |
| **Total** | — | — | **~3.3M–5.8M tokens** |

This should fit comfortably under $100 using a low-cost API model, even with retries and a stronger-model audit on a subset.

Cost-saving tips:

- Use one cheap model for generation, anonymization, and judging.
- Use a stronger model only for 10–20% audit or ambiguous examples.
- Cache extraction results.
- Use short snippets, not full documents.
- Use structured JSON outputs to reduce re-processing.
- Run the Batch API if your timeline allows.

---

## 17. Suggested implementation structure

```text
utility_preserving_anonymization/
  data/
    raw/
      tab/
      synthetic_clinical_seed.jsonl
    processed/
      benchmark.jsonl
      anonymized_outputs.jsonl
      judgments.jsonl
  prompts/
    generic_anonymizer.txt
    privacy_first_anonymizer.txt
    critical_fact_extractor.txt
    privacy_span_extractor.txt
    critical_span_guard.txt
    verifier_repair.txt
    qa_consistency.txt
  src/
    build_synthetic_clinical.py
    build_tab_snippets.py
    run_anonymizers.py
    run_judges.py
    compute_metrics.py
    make_tables.py
  paper/
    main.tex
    references.bib
  README.md
```

---

## 18. Minimal pseudocode

```python
for example in benchmark:
    outputs = {}

    outputs["regex"] = regex_anonymize(example["text"])
    outputs["presidio"] = presidio_anonymize(example["text"])
    outputs["generic_llm"] = call_llm(GENERIC_PROMPT, text=example["text"])
    outputs["privacy_first_llm"] = call_llm(PRIVACY_FIRST_PROMPT, text=example["text"])

    critical_facts = call_llm_json(CRITICAL_FACT_PROMPT, text=example["text"])
    privacy_spans = call_llm_json(PRIVACY_SPAN_PROMPT, text=example["text"])

    draft = call_llm(
        CRITICAL_SPAN_GUARD_PROMPT,
        text=example["text"],
        critical_facts=critical_facts,
        privacy_spans=privacy_spans,
    )

    repaired = call_llm_json(
        VERIFY_REPAIR_PROMPT,
        original_text=example["text"],
        anonymized_text=draft,
        critical_facts=critical_facts,
        privacy_spans=privacy_spans,
    )

    outputs["critical_span_guard"] = repaired["text"]

    for method, anonymized in outputs.items():
        privacy_result = privacy_metrics(example, anonymized)
        utility_result = utility_metrics(example, anonymized)
        save_result(example["id"], method, privacy_result, utility_result)
```

---

## 19. Statistical analysis

Keep statistics simple and reviewer-friendly.

### 19.1 Report confidence intervals

Use bootstrap confidence intervals over examples for:

- direct leak rate,
- quasi-identifier risk,
- TCFR,
- CCR,
- QA consistency.

### 19.2 Use paired comparisons

Because every method is evaluated on the same examples, use paired tests:

- McNemar test for binary QA consistency,
- Wilcoxon signed-rank for per-example TCFR,
- bootstrap difference in means as a simple alternative.

### 19.3 Report effect sizes

Do not only report p-values. Report absolute differences:

```text
Critical Span Guard improved TCFR by +14.2 points over generic LLM anonymization while changing direct identifier leak rate by +0.3 points.
```

Even if numbers are preliminary, this framing is strong.

---

## 20. Failure taxonomy

Annotate 30–50 failures manually and group them.

### Privacy failures

1. Direct identifier left unchanged.
2. Partial identifier left unchanged.
3. Quasi-identifier combination remains.
4. Placeholder inconsistency enables linkage.
5. Rewritten text introduces a new identifying detail.

### Utility failures

1. Critical fact omitted.
2. Critical fact contradicted.
3. Critical fact over-generalized.
4. Temporal sequence destroyed.
5. Entity role changed.
6. Hallucinated fact added.
7. Numeric value altered.
8. Legal/clinical term mistaken for PII.

This taxonomy can be one of the most valuable parts of the paper.

---

## 21. Paper outline for a 4-page short paper

### Abstract, 150–200 words

Problem, benchmark, metric, method, key result.

### 1. Introduction, ~0.75 page

- Sensitive clinical/legal text is valuable for foundation models.
- De-identification is necessary but often evaluated only as PII detection.
- For downstream use, preserving task-critical meaning matters.
- Contributions: benchmark, metric, method, empirical audit.

### 2. Related work, ~0.5 page

Cover:

- clinical de-identification and clinical information retention;
- TAB/legal anonymization;
- privacy–utility tradeoffs in text anonymization;
- LLMs as anonymizers/judges/attackers.

### 3. Benchmark and metrics, ~1 page

- Data sources.
- Annotation schema.
- TCFR, CCR, QA consistency, privacy metrics.

### 4. Methods, ~0.75 page

- Baselines.
- Critical Span Guard.
- API budget and reproducibility.

### 5. Results, ~0.75 page

- Main table.
- One figure.
- 2–3 qualitative examples.

### 6. Limitations and responsible use, ~0.25 page

- Synthetic clinical data is not real PHI.
- LLM judges need manual validation.
- No claim of HIPAA/GDPR compliance.
- API use should be limited to public/synthetic data.

---

## 22. Paper outline for an 8-page long paper

### 1. Introduction

Emphasize why “safe but useless” transformations fail the goal of responsibly enabling data.

### 2. Background and related work

Separate subsections:

- de-identification and anonymization;
- clinical information retention;
- legal anonymization and TAB;
- privacy–utility tradeoffs;
- LLM-based evaluation.

### 3. Task formulation

Define:

- original text `x`,
- anonymizer `A(x)`,
- private spans `P`,
- task-critical facts `F`,
- downstream questions `Q`,
- privacy risk `R`,
- utility `U`.

### 4. Benchmark construction

Detail sampling, annotation, clinical template generation, QA construction, quality control.

### 5. Metrics

Formalize TCFR, CCR, QA consistency, direct leak rate, QI risk.

### 6. Critical Span Guard method

Include algorithm box.

### 7. Experiments

Methods, models, prompts, costs, statistical analysis.

### 8. Results

Quantitative tables, plots, ablations.

### 9. Error analysis

Failure taxonomy and examples.

### 10. Discussion, limitations, ethics

Governance and responsible release.

---

## 23. Recommended abstract draft

> De-identification is a common prerequisite for using sensitive clinical and legal text in foundation-model workflows, but existing evaluations often focus on whether personally identifying spans are removed rather than whether the transformed text remains useful for downstream reasoning. We study a failure mode in which anonymization removes or alters task-critical facts such as medications, lab results, legal claims, statutes, procedural events, and court outcomes. We introduce a small benchmark of clinical-style and legal snippets annotated with private spans, task-critical facts, and downstream QA pairs, and propose Task-Critical Fact Retention (TCFR) and Critical Contradiction Rate (CCR) as utility metrics for anonymized text. We compare regex redaction, Presidio, generic LLM anonymization, privacy-first LLM anonymization, and a simple two-pass method, Critical Span Guard, which explicitly separates privacy spans from task-critical facts before verifying the transformed output. In preliminary experiments, we find that stronger privacy instructions can substantially degrade task utility, while generic semantic similarity often misses domain-critical meaning loss. Critical Span Guard improves task-critical retention while maintaining comparable direct-identifier leakage. These results suggest that responsible data transformation for foundation models should evaluate not only what private information was removed, but also what task-relevant meaning survived.

Replace “preliminary experiments” with concrete numbers after you run it.

---

## 24. Introduction skeleton

Use this structure:

1. **Motivation:** Foundation models need high-quality domain data, but clinical and legal text is sensitive.
2. **Existing solution:** De-identification/anonymization is used to transform sensitive text.
3. **Problem:** Most evaluation focuses on PII removal; downstream utility is under-specified.
4. **Observation:** In clinical/legal domains, many tokens that look “sensitive” are also task-critical.
5. **Example:** Removing a date, age, medication dose, statute number, or court outcome can change the answer.
6. **Contribution:** benchmark + TCFR/CCR metrics + Critical Span Guard method.
7. **Workshop relevance:** responsibly enabling sensitive data for foundation models requires measuring both privacy and task-specific utility.

---

## 25. Strong qualitative examples to look for

Find examples like these and put 2–3 in the paper:

### Clinical failure

Original:

> The patient started warfarin 5 mg daily after a pulmonary embolism.

Bad anonymization:

> The patient started [MEDICATION] after a medical condition.

Why bad: medication and condition are the clinically important facts.

### Legal failure

Original:

> The Court found a violation of Article 8.

Bad anonymization:

> The Court found a violation of [NUMBER].

Why bad: Article 8 is the legal basis and should not be treated like an identifying number.

### Temporal failure

Original:

> Symptoms began two days after vaccination and resolved within one week.

Bad anonymization:

> Symptoms began after an event and later resolved.

Why bad: temporal relation may be the key utility.

### Privacy–utility overlap

Original:

> A 91-year-old violin maker from a small village presented with a rare disease.

Good anonymization depends on task:

- if age matters clinically: “an adult over 90”;
- if occupation is irrelevant: “retired worker”;
- if rare disease is clinically central: preserve it;
- if village is identifying: generalize to region.

---

## 26. Practical execution checklist

### Setup

- [ ] Create repository.
- [ ] Download TAB or prepare legal snippets.
- [ ] Implement regex baseline.
- [ ] Install Presidio baseline.
- [ ] Create API wrapper with retry and JSON validation.
- [ ] Create prompt files.
- [ ] Add cache so every API response is saved.

### Data

- [ ] Generate 50–100 synthetic clinical vignettes.
- [ ] Sample 50–100 legal snippets.
- [ ] Add gold private spans for synthetic data.
- [ ] Extract or manually annotate private spans for legal snippets.
- [ ] Create 1–3 QA pairs per example.
- [ ] Create task-critical fact lists.

### Experiments

- [ ] Run regex.
- [ ] Run Presidio.
- [ ] Run generic LLM anonymizer.
- [ ] Run privacy-first LLM anonymizer.
- [ ] Run Critical Span Guard.
- [ ] Run privacy judges.
- [ ] Run utility judges.
- [ ] Run QA consistency.
- [ ] Compute metrics.
- [ ] Bootstrap confidence intervals.

### Manual audit

- [ ] Sample 20–50 examples.
- [ ] Manually classify utility failures.
- [ ] Manually classify privacy failures.
- [ ] Add 2–3 qualitative examples to the paper.

### Writing

- [ ] Main result table.
- [ ] Privacy–utility frontier figure.
- [ ] Failure taxonomy table.
- [ ] Abstract.
- [ ] Limitations.
- [ ] Ethics/responsible use section.
- [ ] Release README.

---

## 27. Emergency 24-hour version

If the deadline is essentially tomorrow, do this:

### Scope

- 50 synthetic clinical examples.
- 50 legal snippets.
- 3 methods only:
  - Presidio,
  - generic LLM anonymizer,
  - Critical Span Guard.
- Metrics:
  - direct identifier leak rate,
  - TCFR,
  - QA consistency,
  - 10-example manual error analysis.

### Paper framing

Submit as a **preliminary study / negative-results short paper**.

Main result:

> Even simple anonymization methods can remove clinically/legal important facts; task-aware verification is a lightweight way to expose and reduce this failure mode.

### What to avoid

- Do not try to run a huge benchmark.
- Do not compare too many models.
- Do not claim compliance.
- Do not overfit to a fancy method.
- Do not wait for perfect data.

---

## 28. Stronger 1–2 week version

If you have more time:

- Increase to 300–500 examples.
- Add privacy-first anonymization.
- Add quasi-identifier leakage score.
- Add manual audit on 50–100 examples.
- Add correlation analysis showing semantic similarity misses fact loss.
- Add a small ablation:
  - Critical Span Guard without verification,
  - Critical Span Guard with verification,
  - Critical Span Guard with repair.

This would make the paper much stronger.

---

## 29. What reviewers will likely care about

### They will like

- Clear workshop fit.
- Concrete privacy–utility framing.
- No expensive training.
- Public/synthetic data.
- Reproducible prompts and code.
- Qualitative examples that expose real failure modes.
- Honest limitations.

### They may criticize

- Synthetic clinical data may not reflect real notes.
- LLM-based judging can be unreliable.
- Legal/clinical utility is task-dependent.
- Presidio/regex are not the strongest possible baselines.
- Critical Span Guard may be prompt-engineering rather than a model contribution.

### Preemptive responses

- Emphasize this is a workshop paper and benchmark/evaluation contribution.
- Validate LLM judges with manual audit.
- Include both clinical-style and legal domains to show the issue is general.
- Release data/prompts so others can extend it.
- Frame the method as a simple baseline for task-aware anonymization, not a final solution.

---

## 30. Limitations and ethics language

Include a paragraph like this:

> This work does not claim that any evaluated method produces legally compliant anonymization or de-identification. Our clinical-style examples are synthetic and are intended only for evaluating meaning preservation under controlled conditions. We do not process real patient records or private legal documents through third-party APIs. Our LLM-based judges are used as scalable approximations and are manually audited on a subset, but they may miss subtle privacy leaks or domain-meaning changes. We view the benchmark and metrics as tools for auditing transformation pipelines, not as certification that transformed data is safe for release.

---

## 31. Related work pointers

Use these in the paper’s related work section.

### Workshop scope

- **Workshop on Responsibly Enabling Data for Foundation Models @ COLM 2026.** The workshop calls out data transformation, de-identification/anonymization/pseudonymization, and utility–privacy tradeoffs as topics of interest.  
  URL: https://re-data-colm2026.github.io/

### Clinical information retention

- **Aghakasiri et al. (2025), “Not What the Doctor Ordered: Surveying LLM-based De-identification and Quantifying Clinical Information Loss.”** This is the closest related work. It argues that de-identification evaluation is inconsistent and that classification metrics fail to capture clinically relevant changes.  
  URL: https://arxiv.org/abs/2509.14464

### Legal anonymization benchmark

- **Pilán et al. (2022), “The Text Anonymization Benchmark (TAB).”** TAB is an open-source corpus of ECHR legal cases annotated with personal identifiers, masking decisions, confidential attributes, and coreference relations.  
  URL: https://arxiv.org/abs/2202.00443  
  GitHub: https://github.com/NorskRegnesentral/text-anonymization-benchmark

### Privacy–utility text anonymization

- **Loiseau et al. (2026), “Adaptive Text Anonymization: Learning Privacy-Utility Trade-offs via Prompt Optimization.”** Useful for positioning your work in privacy–utility tradeoff evaluation.  
  URL: https://arxiv.org/abs/2602.20743

- **Loiseau et al. (2025), “Tau-Eval: A Unified Evaluation Framework for Useful and Private Text Anonymization.”** Useful for broader evaluation framing.  
  URL: https://arxiv.org/abs/2506.05979

### Re-identification and quasi-identifiers

- **Krčo et al. (2026), “RAT-Bench: A Comprehensive Benchmark for Text Anonymization.”** Focuses on re-identification risk from direct and indirect identifiers.  
  URL: https://arxiv.org/abs/2602.12806

- **Jiang et al. (2026), “Paradox of De-identification: A Critique of HIPAA Safe Harbour in the Age of LLMs.”** Useful for motivating why direct identifier removal is insufficient in clinical text.  
  URL: https://arxiv.org/abs/2602.08997

### Tools and policy anchors

- **Microsoft Presidio.** Data protection and de-identification SDK.  
  URL: https://microsoft.github.io/presidio/

- **HHS HIPAA de-identification guidance.** Official guidance on Expert Determination and Safe Harbor methods.  
  URL: https://www.hhs.gov/hipaa/for-professionals/special-topics/de-identification/index.html

- **OpenAI API data controls.** Use only public/synthetic data unless you have appropriate agreements and controls; by default, API usage may generate abuse monitoring logs retained up to 30 days.  
  URL: https://developers.openai.com/api/docs/guides/your-data

---

## 32. Recommended final positioning

Your paper should not sound like “we built the best anonymizer.” It should sound like:

> **We show that responsible data transformation requires task-aware utility evaluation. In clinical and legal text, anonymization can remove the very facts that make the data valuable. We provide a lightweight benchmark, metric, and baseline method that make this tradeoff visible and reproducible.**

This is the kind of contribution workshops often value: clear problem, timely framing, feasible method, reproducible evaluation, and practical implications.

