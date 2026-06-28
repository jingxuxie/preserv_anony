# Surface Metric Audit

This audit tests whether generic text-overlap metrics are sufficient proxies for privacy-safe task utility on the 120-example OpenAI run. No new API calls are used.

## Method Means

| Method | N | Char sim | Token F1 | Token Jaccard | TF-IDF cosine | Edit rate | Audited TCFR | QA | Direct leak | QI risk |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 120 | 0.521 | 0.772 | 0.636 | 0.619 | 0.275 | 0.993 | 0.979 | 0.000 | 0.142 |
| generic_llm | 120 | 0.504 | 0.775 | 0.652 | 0.710 | 0.248 | 0.939 | 0.892 | 0.183 | 1.742 |
| privacy_first_llm | 120 | 0.219 | 0.578 | 0.444 | 0.476 | 0.463 | 0.542 | 0.422 | 0.000 | 0.600 |

## High-Similarity Failures

Rows at or above the median surface score still often fail audited fact, exact QA, or privacy checks.

| Surface metric | Median threshold | Rows | Audited fact-loss rows | QA-failure rows | Privacy failure rows | Any failure rows |
|---|---:|---:|---:|---:|---:|---:|
| char_similarity | 0.407 | 180 | 20 (0.111) | 25 (0.139) | 46 (0.256) | 65 (0.361) |
| token_f1 | 0.722 | 180 | 15 (0.083) | 31 (0.172) | 52 (0.289) | 73 (0.406) |
| token_jaccard | 0.587 | 182 | 15 (0.082) | 29 (0.159) | 54 (0.297) | 75 (0.412) |
| tfidf_cosine | 0.607 | 180 | 23 (0.128) | 39 (0.217) | 60 (0.333) | 88 (0.489) |

## Correlations

Pearson and Spearman correlations are computed over all method-example rows. A strong surface metric would need to track both retained facts and privacy failures, but these metrics do not.

| Surface metric | Pearson vs audited TCFR | Spearman vs audited TCFR | Pearson vs QA | Pearson vs direct leak | Pearson vs QI risk |
|---|---:|---:|---:|---:|---:|
| char_similarity | 0.551 | 0.610 | 0.588 | 0.356 | 0.073 |
| token_f1 | 0.717 | 0.698 | 0.726 | 0.303 | 0.029 |
| token_jaccard | 0.689 | 0.684 | 0.701 | 0.375 | 0.089 |
| tfidf_cosine | 0.574 | 0.564 | 0.581 | 0.328 | 0.151 |
| token_edit_rate | -0.716 | -0.689 | -0.721 | -0.346 | -0.082 |

## Paper-Useful Examples

### High Similarity But Audited Fact Loss

| ID | Method | Token F1 | Audited TCFR | QA | Privacy flags | Failure signal |
|---|---|---:|---:|---:|---|---|
| legal_0016 | generic_llm | 0.905 | 0.500 | 0.500 | QI 3 | QA: What core claim was raised?; audited: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; omitted: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; QI spans: 1 June 2001; 12 July 2006 |
| legal_0032 | generic_llm | 0.902 | 0.500 | 1.000 | direct leak, QI 3 | audited: his detention on remand in exceeded a “reasonable time” within the meaning of Article 5 § 3 of the Convention, which amounted to interference with his private and family life; leaked: 39412/08; QI spans: 4 August 2008 |
| legal_0053 | generic_llm | 0.886 | 0.500 | 0.500 | direct leak, QI 3 | QA: What core claim was raised?; audited: the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he had attempted secretly to film her naked in their bathroom when she was 14 years old; omitted: the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he had attempted secretly to film her naked in their bathroom when she was 14 years old; leaked: 5786/08; QI spans: 21 January 2008; 14 years old |
| legal_0038 | generic_llm | 0.854 | 0.500 | 1.000 | QI 3 | audited: his detention at Oakington was not compatible with Articles 5 § 1 and 14 of the Convention; QI spans: 18 April 2003; Iraq |
| legal_0016 | critical_span_guard_extracted | 0.850 | 0.500 | 1.000 | none | audited: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention |
| legal_0054 | privacy_first_llm | 0.831 | 0.667 | 0.667 | none | QA: What core claim was raised?; audited: when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas the survivor of a married couple or a homosexual relationship registered under the Civil Partnership Act 2004 would be exempt from paying inheritance tax in these circumstances; omitted: when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas the survivor of a married couple or a homosexual relationship registered under the Civil Partnership Act 2004 would be exempt from paying inheritance tax in these circumstances |
| legal_0030 | privacy_first_llm | 0.821 | 0.500 | 0.500 | none | QA: What core claim was raised?; audited: the Polish authorities had failed to take effective steps to enforce his right of contact with his son, which had violated his rights under Article 8 of the Convention; omitted: the Polish authorities had failed to take effective steps to enforce his right of contact with his son, which had violated his rights under Article 8 of the Convention |
| legal_0053 | privacy_first_llm | 0.812 | 0.500 | 0.500 | none | QA: What core claim was raised?; audited: the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he had attempted secretly to film her naked in their bathroom when she was 14 years old; omitted: the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he had attempted secretly to film her naked in their bathroom when she was 14 years old |

### High Similarity But Exact QA Failure

| ID | Method | Token F1 | Audited TCFR | QA | Privacy flags | Failure signal |
|---|---|---:|---:|---:|---|---|
| legal_0054 | critical_span_guard_extracted | 0.919 | 1.000 | 0.667 | QI 3 | QA: What core claim was raised?; omitted: when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas the survivor of a married couple or a homosexual relationship registered under the Civil Partnership Act 2004 would be exempt from paying inheritance tax in these circumstances; QI spans: sister; sister’s |
| legal_0016 | generic_llm | 0.905 | 0.500 | 0.500 | QI 3 | QA: What core claim was raised?; audited: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; omitted: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; QI spans: 1 June 2001; 12 July 2006 |
| legal_0053 | generic_llm | 0.886 | 0.500 | 0.500 | direct leak, QI 3 | QA: What core claim was raised?; audited: the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he had attempted secretly to film her naked in their bathroom when she was 14 years old; omitted: the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he had attempted secretly to film her naked in their bathroom when she was 14 years old; leaked: 5786/08; QI spans: 21 January 2008; 14 years old |
| legal_0018 | critical_span_guard_extracted | 0.885 | 1.000 | 0.500 | none | QA: What core claim was raised?; omitted: the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively |
| legal_0029 | privacy_first_llm | 0.881 | 1.000 | 0.667 | none | QA: What core claim was raised?; omitted: had been brought against her on the grounds that the preparatory stages of the proceedings at both first instance and on appeal had been directed by the same person, the public prosecutor had not been appointed in accordance with domestic law and there had been no public hearing either at first instance or on appeal |
| legal_0026 | generic_llm | 0.880 | 1.000 | 0.500 | none | QA: What core claim was raised?; omitted: neither he nor counsel had been granted an opportunity at any stage of the criminal proceedings instituted against him to examine the only direct witnesses and victims of the crime allegedly committed by him in Göttingen in February 2007 and on whose testimonies the applicant’s related conviction relied in breach of Article 6 § 3 (d) of the Convention |
| legal_0002 | generic_llm | 0.877 | 1.000 | 0.500 | QI 3 | QA: What core claim was raised?; omitted: an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces that existed at the time violated their rights under Article 8, alone and in conjunction with Article 14 of the Convention; QI spans: homosexuality; homosexuals |
| legal_0002 | critical_span_guard_extracted | 0.870 | 1.000 | 0.500 | QI 3 | QA: What core claim was raised?; omitted: an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals in the armed forces that existed at the time violated their rights under Article 8, alone and in conjunction with Article 14 of the Convention; QI spans: homosexuality; homosexuals |

### High Similarity But Privacy Failure

| ID | Method | Token F1 | Audited TCFR | QA | Privacy flags | Failure signal |
|---|---|---:|---:|---:|---|---|
| legal_0029 | generic_llm | 0.944 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 35396/97; QI spans: 13 January 1997; 1 June 1999 |
| legal_0037 | generic_llm | 0.937 | 1.000 | 1.000 | direct leak, QI 3 | leaked: Ms Nuray Şen; QI spans: 25 April 1996; 30 April 2002 |
| legal_0047 | generic_llm | 0.928 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 17906/15; QI spans: 10 April 2015; 21 May 2013 |
| legal_0054 | critical_span_guard_extracted | 0.919 | 1.000 | 0.667 | QI 3 | QA: What core claim was raised?; omitted: when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas the survivor of a married couple or a homosexual relationship registered under the Civil Partnership Act 2004 would be exempt from paying inheritance tax in these circumstances; QI spans: sister; sister’s |
| legal_0005 | critical_span_guard_extracted | 0.917 | 1.000 | 1.000 | QI 3 | QI spans: Northern Ireland; 1976 |
| legal_0004 | generic_llm | 0.915 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 30457/06; QI spans: 20 July 2006 |
| legal_0055 | generic_llm | 0.915 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 28426/06; QI spans: 28 June 2006; participate in a labour market policy programme. |
| legal_0025 | generic_llm | 0.913 | 1.000 | 1.000 | QI 3 | QI spans: 23 May 2003; resisting the exercise of official authority |

## Takeaway

Surface overlap can reward outputs that retain original identifiers and quasi-identifiers, and it can miss exact QA failures or audited fact losses. The paper should therefore treat edit rate and generic similarity as diagnostic foils, not headline privacy or utility metrics.
