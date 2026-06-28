# Surface Metric Audit

This audit tests whether generic text-overlap metrics are sufficient proxies for privacy-safe task utility on the 70-example OpenAI run. No new API calls are used.

## Method Means

| Method | N | Char sim | Token F1 | Token Jaccard | TF-IDF cosine | Edit rate | Audited TCFR | QA | Direct leak | QI risk |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 70 | 0.492 | 0.768 | 0.633 | 0.623 | 0.281 | 0.993 | 0.981 | 0.000 | 0.057 |
| generic_llm | 70 | 0.507 | 0.768 | 0.646 | 0.705 | 0.256 | 0.929 | 0.867 | 0.186 | 1.757 |
| privacy_first_llm | 70 | 0.203 | 0.564 | 0.433 | 0.471 | 0.476 | 0.514 | 0.410 | 0.000 | 0.586 |

## High-Similarity Failures

Rows at or above the median surface score still often fail audited fact, exact QA, or privacy checks.

| Surface metric | Median threshold | Rows | Audited fact-loss rows | QA-failure rows | Privacy failure rows | Any failure rows |
|---|---:|---:|---:|---:|---:|---:|
| char_similarity | 0.403 | 105 | 10 (0.095) | 15 (0.143) | 26 (0.248) | 38 (0.362) |
| token_f1 | 0.719 | 105 | 6 (0.057) | 16 (0.152) | 30 (0.286) | 42 (0.400) |
| token_jaccard | 0.584 | 105 | 6 (0.057) | 15 (0.143) | 31 (0.295) | 43 (0.410) |
| tfidf_cosine | 0.604 | 105 | 11 (0.105) | 21 (0.200) | 37 (0.352) | 53 (0.505) |

## Correlations

Pearson and Spearman correlations are computed over all method-example rows. A strong surface metric would need to track both retained facts and privacy failures, but these metrics do not.

| Surface metric | Pearson vs audited TCFR | Spearman vs audited TCFR | Pearson vs QA | Pearson vs direct leak | Pearson vs QI risk |
|---|---:|---:|---:|---:|---:|
| char_similarity | 0.567 | 0.632 | 0.602 | 0.372 | 0.054 |
| token_f1 | 0.731 | 0.738 | 0.737 | 0.328 | 0.012 |
| token_jaccard | 0.691 | 0.719 | 0.704 | 0.398 | 0.070 |
| tfidf_cosine | 0.592 | 0.596 | 0.605 | 0.365 | 0.135 |
| token_edit_rate | -0.733 | -0.739 | -0.730 | -0.377 | -0.070 |

## Paper-Useful Examples

### High Similarity But Audited Fact Loss

| ID | Method | Token F1 | Audited TCFR | QA | Privacy flags | Failure signal |
|---|---|---:|---:|---:|---|---|
| legal_0016 | generic_llm | 0.905 | 0.500 | 0.500 | QI 3 | QA: What core claim was raised?; audited: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; omitted: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; QI spans: 1 June 2001; 12 July 2006 |
| legal_0032 | generic_llm | 0.902 | 0.500 | 1.000 | direct leak, QI 3 | audited: his detention on remand in exceeded a “reasonable time” within the meaning of Article 5 § 3 of the Convention, which amounted to interference with his private and family life; leaked: 39412/08; QI spans: 4 August 2008 |
| legal_0016 | critical_span_guard_extracted | 0.850 | 0.500 | 1.000 | none | audited: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention |
| legal_0022 | privacy_first_llm | 0.790 | 0.667 | 0.667 | none | QA: What core claim was raised?; audited: a factual error made by the Court of Cassation had infringed his right of access to court, in violation of Article 6 of the Convention; omitted: a factual error made by the Court of Cassation had infringed his right of access to court, in violation of Article 6 of the Convention |
| legal_0005 | generic_llm | 0.783 | 0.667 | 0.667 | none | QA: What core claim was raised?; audited: the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976; omitted: the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976 |
| legal_0016 | privacy_first_llm | 0.774 | 0.500 | 0.500 | none | QA: What core claim was raised?; audited: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; omitted: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention |
| clinical_0009 | generic_llm | 0.677 | 0.833 | 1.000 | QI 2 | audited: 5 days of fever, productive cough, and right-sided chest pain; omitted: 5 days of fever, productive cough, and right-sided chest pain; oxygen saturation was 88 percent on room air; QI spans: software engineer |
| legal_0026 | privacy_first_llm | 0.676 | 0.000 | 0.000 | none | QA: Which substantive Article was invoked?; What core claim was raised?; audited: Article 6; neither he nor counsel had been granted an opportunity at any stage of the criminal proceedings instituted against him to examine the only direct witnesses and victims of the crime allegedly committed by him in Göttingen in February 2007 and on whose testimonies the applicant’s related conviction relied in breach of Article 6 § 3 (d) of the Convention; omitted: Article 6; neither he nor counsel had been granted an opportunity at any stage of the criminal proceedings instituted against him to examine the only direct witnesses and victims of the crime allegedly committed by him in Göttingen in February 2007 and on whose testimonies the applicant’s related conviction relied in breach of Article 6 § 3 (d) of the Convention |

### High Similarity But Exact QA Failure

| ID | Method | Token F1 | Audited TCFR | QA | Privacy flags | Failure signal |
|---|---|---:|---:|---:|---|---|
| legal_0016 | generic_llm | 0.905 | 0.500 | 0.500 | QI 3 | QA: What core claim was raised?; audited: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; omitted: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; QI spans: 1 June 2001; 12 July 2006 |
| legal_0018 | critical_span_guard_extracted | 0.885 | 1.000 | 0.500 | none | QA: What core claim was raised?; omitted: the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively |
| legal_0029 | privacy_first_llm | 0.881 | 1.000 | 0.667 | none | QA: What core claim was raised?; omitted: had been brought against her on the grounds that the preparatory stages of the proceedings at both first instance and on appeal had been directed by the same person, the public prosecutor had not been appointed in accordance with domestic law and there had been no public hearing either at first instance or on appeal |
| legal_0026 | generic_llm | 0.880 | 1.000 | 0.500 | none | QA: What core claim was raised?; omitted: neither he nor counsel had been granted an opportunity at any stage of the criminal proceedings instituted against him to examine the only direct witnesses and victims of the crime allegedly committed by him in Göttingen in February 2007 and on whose testimonies the applicant’s related conviction relied in breach of Article 6 § 3 (d) of the Convention |
| legal_0026 | critical_span_guard_extracted | 0.847 | 1.000 | 0.500 | none | QA: What core claim was raised?; omitted: neither he nor counsel had been granted an opportunity at any stage of the criminal proceedings instituted against him to examine the only direct witnesses and victims of the crime allegedly committed by him in Göttingen in February 2007 and on whose testimonies the applicant’s related conviction relied in breach of Article 6 § 3 (d) of the Convention |
| legal_0014 | critical_span_guard_extracted | 0.843 | 1.000 | 0.667 | none | QA: What core claim was raised?; omitted: his disenfranchisement as a result of his residence outside the United Kingdom constituted a violation of Article 3 of Protocol No. 1 to the Convention, taken alone and taken together with Article 14 |
| legal_0014 | generic_llm | 0.836 | 1.000 | 0.667 | none | QA: What core claim was raised?; omitted: his disenfranchisement as a result of his residence outside the United Kingdom constituted a violation of Article 3 of Protocol No. 1 to the Convention, taken alone and taken together with Article 14 |
| legal_0036 | generic_llm | 0.821 | 1.000 | 0.667 | none | QA: What core claim was raised?; omitted: they had violated Article 6 §§ 1 and 3 (d) (art. 6-1, art. 6-3-d) of the Convention |

### High Similarity But Privacy Failure

| ID | Method | Token F1 | Audited TCFR | QA | Privacy flags | Failure signal |
|---|---|---:|---:|---:|---|---|
| legal_0029 | generic_llm | 0.944 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 35396/97; QI spans: 13 January 1997; 1 June 1999 |
| legal_0047 | generic_llm | 0.928 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 17906/15; QI spans: 10 April 2015; 21 May 2013 |
| legal_0005 | critical_span_guard_extracted | 0.917 | 1.000 | 1.000 | QI 3 | QI spans: Northern Ireland; 1976 |
| legal_0025 | generic_llm | 0.913 | 1.000 | 1.000 | QI 3 | QI spans: 23 May 2003; resisting the exercise of official authority |
| legal_0022 | generic_llm | 0.906 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 18753/04; QI spans: 11 February 2004 |
| legal_0048 | generic_llm | 0.905 | 1.000 | 1.000 | QI 2 | QI spans: 23 December 2009 |
| legal_0016 | generic_llm | 0.905 | 0.500 | 0.500 | QI 3 | QA: What core claim was raised?; audited: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; omitted: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; QI spans: 1 June 2001; 12 July 2006 |
| legal_0021 | generic_llm | 0.904 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 29865/96; QI spans: 20 December 1995 |

## Takeaway

Surface overlap can reward outputs that retain original identifiers and quasi-identifiers, and it can miss exact QA failures or audited fact losses. The paper should therefore treat edit rate and generic similarity as diagnostic foils, not headline privacy or utility metrics.
