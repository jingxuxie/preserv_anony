# Surface Metric Audit

This audit tests whether generic text-overlap metrics are sufficient proxies for privacy-safe task utility on the 50-example OpenAI run. No new API calls are used.

## Method Means

| Method | N | Char sim | Token F1 | Token Jaccard | Edit rate | Audited TCFR | QA | Direct leak | QI risk |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 50 | 0.509 | 0.771 | 0.636 | 0.278 | 1.000 | 0.990 | 0.000 | 0.080 |
| generic_llm | 50 | 0.504 | 0.767 | 0.646 | 0.257 | 0.940 | 0.890 | 0.160 | 1.740 |
| privacy_first_llm | 50 | 0.218 | 0.575 | 0.443 | 0.463 | 0.567 | 0.440 | 0.000 | 0.660 |

## High-Similarity Failures

Rows at or above the median surface score still often fail audited fact, exact QA, or privacy checks.

| Surface metric | Median threshold | Rows | Audited fact-loss rows | QA-failure rows | Privacy failure rows | Any failure rows |
|---|---:|---:|---:|---:|---:|---:|
| char_similarity | 0.407 | 75 | 6 (0.080) | 8 (0.107) | 19 (0.253) | 26 (0.347) |
| token_f1 | 0.721 | 75 | 2 (0.027) | 8 (0.107) | 22 (0.293) | 28 (0.373) |
| token_jaccard | 0.584 | 75 | 2 (0.027) | 7 (0.093) | 23 (0.307) | 29 (0.387) |

## Correlations

Pearson and Spearman correlations are computed over all method-example rows. A strong surface metric would need to track both retained facts and privacy failures, but these metrics do not.

| Surface metric | Pearson vs audited TCFR | Spearman vs audited TCFR | Pearson vs QA | Pearson vs direct leak | Pearson vs QI risk |
|---|---:|---:|---:|---:|---:|
| char_similarity | 0.605 | 0.667 | 0.620 | 0.379 | 0.017 |
| token_f1 | 0.782 | 0.783 | 0.769 | 0.320 | -0.036 |
| token_jaccard | 0.755 | 0.771 | 0.737 | 0.386 | 0.022 |
| token_edit_rate | -0.773 | -0.776 | -0.754 | -0.376 | -0.020 |

## Paper-Useful Examples

### High Similarity But Audited Fact Loss

| ID | Method | Token F1 | Audited TCFR | QA | Privacy flags | Failure signal |
|---|---|---:|---:|---:|---|---|
| legal_0022 | privacy_first_llm | 0.790 | 0.667 | 0.667 | none | QA: What core claim was raised?; audited: a factual error made by the Court of Cassation had infringed his right of access to court, in violation of Article 6 of the Convention; omitted: a factual error made by the Court of Cassation had infringed his right of access to court, in violation of Article 6 of the Convention |
| legal_0005 | generic_llm | 0.783 | 0.667 | 0.667 | none | QA: What core claim was raised?; audited: the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976; omitted: the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976 |
| clinical_0009 | generic_llm | 0.677 | 0.833 | 1.000 | QI 2 | audited: 5 days of fever, productive cough, and right-sided chest pain; omitted: 5 days of fever, productive cough, and right-sided chest pain; oxygen saturation was 88 percent on room air; QI spans: software engineer |
| legal_0048 | privacy_first_llm | 0.670 | 0.667 | 0.667 | none | QA: Which substantive Article was invoked?; audited: he did not have a speedy review of the lawfulness of his detention, in violation of Article 5 § 4 of the Convention; omitted: Article 5 |
| clinical_0034 | generic_llm | 0.667 | 0.833 | 1.000 | QI 2 | audited: blood pressure fell to 82/48 mmHg; omitted: blood pressure fell to 82/48 mmHg; intramuscular epinephrine 0.3 mg and observation for 4 hours; QI spans: 58-year-old; dental hygienist |
| clinical_0046 | generic_llm | 0.661 | 0.833 | 1.000 | QI 2 | audited: blood pressure fell to 82/48 mmHg; omitted: blood pressure fell to 82/48 mmHg; intramuscular epinephrine 0.3 mg and observation for 4 hours; QI spans: 74-year-old; postal worker |
| legal_0018 | privacy_first_llm | 0.655 | 0.000 | 0.000 | none | QA: Which substantive Article was invoked?; What core claim was raised?; audited: Article 1; the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively; omitted: Article 1; the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively |
| legal_0040 | generic_llm | 0.653 | 0.333 | 0.667 | none | QA: Which substantive Article was invoked?; audited: Article 18; amounted to arbitrary and unlawful interference by the public authorities with the applicant’s private and family life (Article 18 of the Constitution taken together with Articles 15 and 19 - see paragraph 23 below); omitted: Article 18 |

### High Similarity But Exact QA Failure

| ID | Method | Token F1 | Audited TCFR | QA | Privacy flags | Failure signal |
|---|---|---:|---:|---:|---|---|
| legal_0018 | critical_span_guard_extracted | 0.885 | 1.000 | 0.500 | none | QA: What core claim was raised?; omitted: the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively |
| legal_0029 | privacy_first_llm | 0.881 | 1.000 | 0.667 | none | QA: What core claim was raised?; omitted: had been brought against her on the grounds that the preparatory stages of the proceedings at both first instance and on appeal had been directed by the same person, the public prosecutor had not been appointed in accordance with domestic law and there had been no public hearing either at first instance or on appeal |
| legal_0036 | generic_llm | 0.821 | 1.000 | 0.667 | none | QA: What core claim was raised?; omitted: they had violated Article 6 §§ 1 and 3 (d) (art. 6-1, art. 6-3-d) of the Convention |
| legal_0025 | privacy_first_llm | 0.819 | 1.000 | 0.500 | none | QA: What core claim was raised?; omitted: the conduct of proceedings for the said traffic offence violated Article 4 of Protocol No. 7, given that he had been acquitted of the offence of resisting the exercise of official authority in respect of the same act; QI spans: resisting the exercise of official authority |
| legal_0022 | privacy_first_llm | 0.790 | 0.667 | 0.667 | none | QA: What core claim was raised?; audited: a factual error made by the Court of Cassation had infringed his right of access to court, in violation of Article 6 of the Convention; omitted: a factual error made by the Court of Cassation had infringed his right of access to court, in violation of Article 6 of the Convention |
| legal_0005 | generic_llm | 0.783 | 0.667 | 0.667 | none | QA: What core claim was raised?; audited: the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976; omitted: the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976 |
| clinical_0037 | generic_llm | 0.768 | 1.000 | 0.500 | QI 2 | QA: What anticoagulation plan was started?; omitted: oxygen saturation was 89 percent on room air; apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily; QI spans: 79-year-old; long-haul driver |
| clinical_0049 | generic_llm | 0.735 | 1.000 | 0.500 | QI 2 | QA: What anticoagulation plan was started?; omitted: oxygen saturation was 89 percent on room air; apixaban 10 mg twice daily for 7 days followed by 5 mg twice daily; QI spans: 27-year-old; software engineer |

### High Similarity But Privacy Failure

| ID | Method | Token F1 | Audited TCFR | QA | Privacy flags | Failure signal |
|---|---|---:|---:|---:|---|---|
| legal_0029 | generic_llm | 0.944 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 35396/97; QI spans: 13 January 1997; 1 June 1999 |
| legal_0047 | generic_llm | 0.928 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 17906/15; QI spans: 10 April 2015; 21 May 2013 |
| legal_0005 | critical_span_guard_extracted | 0.917 | 1.000 | 1.000 | QI 3 | QI spans: Northern Ireland; 1976 |
| legal_0025 | generic_llm | 0.913 | 1.000 | 1.000 | QI 3 | QI spans: 23 May 2003; resisting the exercise of official authority |
| legal_0022 | generic_llm | 0.906 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 18753/04; QI spans: 11 February 2004 |
| legal_0048 | generic_llm | 0.905 | 1.000 | 1.000 | QI 2 | QI spans: 23 December 2009 |
| legal_0008 | generic_llm | 0.901 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 37976/06; QI spans: 1 September 2006 |
| legal_0031 | generic_llm | 0.901 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 31834/96; QI spans: 4 June 1996 |

## Takeaway

Surface overlap can reward outputs that retain original identifiers and quasi-identifiers, and it can miss exact QA failures or audited fact losses. The paper should therefore treat edit rate and generic similarity as diagnostic foils, not headline privacy or utility metrics.
