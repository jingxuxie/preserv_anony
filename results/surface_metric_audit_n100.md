# Surface Metric Audit

This audit tests whether generic text-overlap metrics are sufficient proxies for privacy-safe task utility on the 100-example OpenAI run. No new API calls are used.

## Method Means

| Method | N | Char sim | Token F1 | Token Jaccard | TF-IDF cosine | Edit rate | Audited TCFR | QA | Direct leak | QI risk |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 100 | 0.512 | 0.771 | 0.634 | 0.618 | 0.278 | 0.995 | 0.982 | 0.000 | 0.090 |
| generic_llm | 100 | 0.521 | 0.774 | 0.651 | 0.708 | 0.249 | 0.938 | 0.892 | 0.190 | 1.800 |
| privacy_first_llm | 100 | 0.214 | 0.569 | 0.435 | 0.467 | 0.473 | 0.510 | 0.405 | 0.000 | 0.630 |

## High-Similarity Failures

Rows at or above the median surface score still often fail audited fact, exact QA, or privacy checks.

| Surface metric | Median threshold | Rows | Audited fact-loss rows | QA-failure rows | Privacy failure rows | Any failure rows |
|---|---:|---:|---:|---:|---:|---:|
| char_similarity | 0.410 | 150 | 15 (0.100) | 18 (0.120) | 38 (0.253) | 53 (0.353) |
| token_f1 | 0.721 | 150 | 12 (0.080) | 22 (0.147) | 45 (0.300) | 61 (0.407) |
| token_jaccard | 0.587 | 152 | 12 (0.079) | 20 (0.132) | 47 (0.309) | 63 (0.414) |
| tfidf_cosine | 0.607 | 150 | 19 (0.127) | 29 (0.193) | 52 (0.347) | 73 (0.487) |

## Correlations

Pearson and Spearman correlations are computed over all method-example rows. A strong surface metric would need to track both retained facts and privacy failures, but these metrics do not.

| Surface metric | Pearson vs audited TCFR | Spearman vs audited TCFR | Pearson vs QA | Pearson vs direct leak | Pearson vs QI risk |
|---|---:|---:|---:|---:|---:|
| char_similarity | 0.566 | 0.623 | 0.611 | 0.355 | 0.047 |
| token_f1 | 0.720 | 0.712 | 0.735 | 0.314 | 0.021 |
| token_jaccard | 0.692 | 0.698 | 0.711 | 0.384 | 0.077 |
| tfidf_cosine | 0.575 | 0.569 | 0.592 | 0.344 | 0.151 |
| token_edit_rate | -0.721 | -0.706 | -0.730 | -0.362 | -0.080 |

## Paper-Useful Examples

### High Similarity But Audited Fact Loss

| ID | Method | Token F1 | Audited TCFR | QA | Privacy flags | Failure signal |
|---|---|---:|---:|---:|---|---|
| legal_0016 | generic_llm | 0.905 | 0.500 | 0.500 | QI 3 | QA: What core claim was raised?; audited: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; omitted: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; QI spans: 1 June 2001; 12 July 2006 |
| legal_0032 | generic_llm | 0.902 | 0.500 | 1.000 | direct leak, QI 3 | audited: his detention on remand in exceeded a “reasonable time” within the meaning of Article 5 § 3 of the Convention, which amounted to interference with his private and family life; leaked: 39412/08; QI spans: 4 August 2008 |
| legal_0038 | generic_llm | 0.854 | 0.500 | 1.000 | QI 3 | audited: his detention at Oakington was not compatible with Articles 5 § 1 and 14 of the Convention; QI spans: 18 April 2003; Iraq |
| legal_0016 | critical_span_guard_extracted | 0.850 | 0.500 | 1.000 | none | audited: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention |
| legal_0030 | privacy_first_llm | 0.821 | 0.500 | 0.500 | none | QA: What core claim was raised?; audited: the Polish authorities had failed to take effective steps to enforce his right of contact with his son, which had violated his rights under Article 8 of the Convention; omitted: the Polish authorities had failed to take effective steps to enforce his right of contact with his son, which had violated his rights under Article 8 of the Convention |
| legal_0022 | privacy_first_llm | 0.790 | 0.667 | 0.667 | none | QA: What core claim was raised?; audited: a factual error made by the Court of Cassation had infringed his right of access to court, in violation of Article 6 of the Convention; omitted: a factual error made by the Court of Cassation had infringed his right of access to court, in violation of Article 6 of the Convention |
| legal_0038 | privacy_first_llm | 0.788 | 0.500 | 1.000 | none | audited: his detention at Oakington was not compatible with Articles 5 § 1 and 14 of the Convention |
| legal_0005 | generic_llm | 0.783 | 0.667 | 0.667 | none | QA: What core claim was raised?; audited: the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976; omitted: the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976 |

### High Similarity But Exact QA Failure

| ID | Method | Token F1 | Audited TCFR | QA | Privacy flags | Failure signal |
|---|---|---:|---:|---:|---|---|
| legal_0016 | generic_llm | 0.905 | 0.500 | 0.500 | QI 3 | QA: What core claim was raised?; audited: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; omitted: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; QI spans: 1 June 2001; 12 July 2006 |
| legal_0018 | critical_span_guard_extracted | 0.885 | 1.000 | 0.500 | none | QA: What core claim was raised?; omitted: the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively |
| legal_0029 | privacy_first_llm | 0.881 | 1.000 | 0.667 | none | QA: What core claim was raised?; omitted: had been brought against her on the grounds that the preparatory stages of the proceedings at both first instance and on appeal had been directed by the same person, the public prosecutor had not been appointed in accordance with domestic law and there had been no public hearing either at first instance or on appeal |
| legal_0026 | generic_llm | 0.880 | 1.000 | 0.500 | none | QA: What core claim was raised?; omitted: neither he nor counsel had been granted an opportunity at any stage of the criminal proceedings instituted against him to examine the only direct witnesses and victims of the crime allegedly committed by him in Göttingen in February 2007 and on whose testimonies the applicant’s related conviction relied in breach of Article 6 § 3 (d) of the Convention |
| legal_0002 | generic_llm | 0.877 | 1.000 | 0.500 | QI 3 | QA: What core claim was raised?; omitted: an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces that existed at the time violated their rights under Article 8, alone and in conjunction with Article 14 of the Convention; QI spans: homosexuality; homosexuals |
| legal_0002 | critical_span_guard_extracted | 0.870 | 1.000 | 0.500 | QI 3 | QA: What core claim was raised?; omitted: an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces that existed at the time violated their rights under Article 8, alone and in conjunction with Article 14 of the Convention; QI spans: homosexuality; homosexuals |
| legal_0026 | critical_span_guard_extracted | 0.847 | 1.000 | 0.500 | none | QA: What core claim was raised?; omitted: neither he nor counsel had been granted an opportunity at any stage of the criminal proceedings instituted against him to examine the only direct witnesses and victims of the crime allegedly committed by him in Göttingen in February 2007 and on whose testimonies the applicant’s related conviction relied in breach of Article 6 § 3 (d) of the Convention |
| legal_0014 | critical_span_guard_extracted | 0.843 | 1.000 | 0.667 | none | QA: What core claim was raised?; omitted: his disenfranchisement as a result of his residence outside the United Kingdom constituted a violation of Article 3 of Protocol No. 1 to the Convention, taken alone and taken together with Article 14 |

### High Similarity But Privacy Failure

| ID | Method | Token F1 | Audited TCFR | QA | Privacy flags | Failure signal |
|---|---|---:|---:|---:|---|---|
| legal_0029 | generic_llm | 0.944 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 35396/97; QI spans: 13 January 1997; 1 June 1999 |
| legal_0037 | generic_llm | 0.937 | 1.000 | 1.000 | direct leak, QI 3 | leaked: Ms Nuray Şen; QI spans: 25 April 1996; 30 April 2002 |
| legal_0047 | generic_llm | 0.928 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 17906/15; QI spans: 10 April 2015; 21 May 2013 |
| legal_0005 | critical_span_guard_extracted | 0.917 | 1.000 | 1.000 | QI 3 | QI spans: Northern Ireland; 1976 |
| legal_0004 | generic_llm | 0.915 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 30457/06; QI spans: 20 July 2006 |
| legal_0025 | generic_llm | 0.913 | 1.000 | 1.000 | QI 3 | QI spans: 23 May 2003; resisting the exercise of official authority |
| legal_0022 | generic_llm | 0.906 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 18753/04; QI spans: 11 February 2004 |
| legal_0048 | generic_llm | 0.905 | 1.000 | 1.000 | QI 2 | QI spans: 23 December 2009 |

## Takeaway

Surface overlap can reward outputs that retain original identifiers and quasi-identifiers, and it can miss exact QA failures or audited fact losses. The paper should therefore treat edit rate and generic similarity as diagnostic foils, not headline privacy or utility metrics.
