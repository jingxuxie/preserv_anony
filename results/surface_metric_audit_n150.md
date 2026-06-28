# Surface Metric Audit

This audit tests whether generic text-overlap metrics are sufficient proxies for privacy-safe task utility on the 150-example OpenAI run. No new API calls are used.

## Method Means

| Method | N | Char sim | Token F1 | Token Jaccard | TF-IDF cosine | Edit rate | Audited TCFR | QA | Direct leak | QI risk |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| critical_span_guard_extracted | 150 | 0.520 | 0.773 | 0.637 | 0.617 | 0.274 | 0.994 | 0.974 | 0.000 | 0.127 |
| generic_llm | 150 | 0.507 | 0.776 | 0.653 | 0.708 | 0.247 | 0.938 | 0.888 | 0.180 | 1.733 |
| privacy_first_llm | 150 | 0.215 | 0.577 | 0.443 | 0.472 | 0.464 | 0.529 | 0.414 | 0.000 | 0.573 |

## High-Similarity Failures

Rows at or above the median surface score still often fail audited fact, exact QA, or privacy checks.

| Surface metric | Median threshold | Rows | Audited fact-loss rows | QA-failure rows | Privacy failure rows | Any failure rows |
|---|---:|---:|---:|---:|---:|---:|
| char_similarity | 0.402 | 225 | 25 (0.111) | 37 (0.164) | 55 (0.244) | 84 (0.373) |
| token_f1 | 0.722 | 225 | 23 (0.102) | 42 (0.187) | 64 (0.284) | 96 (0.427) |
| token_jaccard | 0.587 | 228 | 23 (0.101) | 40 (0.175) | 67 (0.294) | 99 (0.434) |
| tfidf_cosine | 0.607 | 225 | 34 (0.151) | 55 (0.244) | 73 (0.324) | 116 (0.516) |

## Correlations

Pearson and Spearman correlations are computed over all method-example rows. A strong surface metric would need to track both retained facts and privacy failures, but these metrics do not.

| Surface metric | Pearson vs audited TCFR | Spearman vs audited TCFR | Pearson vs QA | Pearson vs direct leak | Pearson vs QI risk |
|---|---:|---:|---:|---:|---:|
| char_similarity | 0.535 | 0.592 | 0.564 | 0.361 | 0.057 |
| token_f1 | 0.701 | 0.681 | 0.711 | 0.304 | 0.027 |
| token_jaccard | 0.671 | 0.661 | 0.685 | 0.376 | 0.086 |
| tfidf_cosine | 0.558 | 0.547 | 0.564 | 0.326 | 0.145 |
| token_edit_rate | -0.704 | -0.675 | -0.707 | -0.346 | -0.082 |

## Paper-Useful Examples

### High Similarity But Audited Fact Loss

| ID | Method | Token F1 | Audited TCFR | QA | Privacy flags | Failure signal |
|---|---|---:|---:|---:|---|---|
| legal_0016 | generic_llm | 0.905 | 0.500 | 0.500 | QI 3 | QA: What core claim was raised?; audited: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; omitted: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; QI spans: 1 June 2001; 12 July 2006 |
| legal_0032 | generic_llm | 0.902 | 0.500 | 1.000 | direct leak, QI 3 | audited: his detention on remand in exceeded a “reasonable time” within the meaning of Article 5 § 3 of the Convention, which amounted to interference with his private and family life; leaked: 39412/08; QI spans: 4 August 2008 |
| legal_0062 | generic_llm | 0.887 | 0.500 | 0.500 | direct leak, QI 3 | QA: What core claim was raised?; audited: there had been an unlawful use of lethal force against the deceased, Mr John Hemsworth; omitted: there had been an unlawful use of lethal force against the deceased, Mr John Hemsworth; leaked: 58559/09; QI spans: 12 October 2009; Northern Ireland |
| legal_0053 | generic_llm | 0.886 | 0.500 | 0.500 | direct leak, QI 3 | QA: What core claim was raised?; audited: the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he had attempted secretly to film her naked in their bathroom when she was 14 years old; omitted: the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he had attempted secretly to film her naked in their bathroom when she was 14 years old; leaked: 5786/08; QI spans: 21 January 2008; 14 years old |
| legal_0038 | generic_llm | 0.854 | 0.500 | 1.000 | QI 3 | audited: his detention at Oakington was not compatible with Articles 5 § 1 and 14 of the Convention; QI spans: 18 April 2003; Iraq |
| legal_0016 | critical_span_guard_extracted | 0.850 | 0.500 | 1.000 | none | audited: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention |
| legal_0054 | privacy_first_llm | 0.831 | 0.667 | 0.667 | none | QA: What core claim was raised?; audited: when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas the survivor of a married couple or a homosexual relationship registered under the Civil Partnership Act 2004 would be exempt from paying inheritance tax in these circumstances; omitted: when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas the survivor of a married couple or a homosexual relationship registered under the Civil Partnership Act 2004 would be exempt from paying inheritance tax in these circumstances |
| legal_0030 | privacy_first_llm | 0.821 | 0.500 | 0.500 | none | QA: What core claim was raised?; audited: the Polish authorities had failed to take effective steps to enforce his right of contact with his son, which had violated his rights under Article 8 of the Convention; omitted: the Polish authorities had failed to take effective steps to enforce his right of contact with his son, which had violated his rights under Article 8 of the Convention |

### High Similarity But Exact QA Failure

| ID | Method | Token F1 | Audited TCFR | QA | Privacy flags | Failure signal |
|---|---|---:|---:|---:|---|---|
| legal_0054 | critical_span_guard_extracted | 0.919 | 1.000 | 0.667 | QI 3 | QA: What core claim was raised?; omitted: when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas the survivor of a married couple or a homosexual relationship registered under the Civil Partnership Act 2004 would be exempt from paying inheritance tax in these circumstances; QI spans: sister; sister’s |
| legal_0069 | generic_llm | 0.912 | 1.000 | 0.500 | none | QA: What core claim was raised?; omitted: State security forces had destroyed his home and possessions and had forced him to leave his place of residence with no possibility of return and that he had been denied an effective remedy in domestic law in violation of Articles 3, 6, 8, 13 and 14 of the Convention and Article 1 of Protocol No. 1 |
| legal_0016 | generic_llm | 0.905 | 0.500 | 0.500 | QI 3 | QA: What core claim was raised?; audited: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; omitted: the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention; QI spans: 1 June 2001; 12 July 2006 |
| legal_0070 | generic_llm | 0.899 | 1.000 | 0.500 | direct leak, QI 3 | QA: What core claim was raised?; omitted: the Regional Appeals Commission was no independent and impartial tribunal within the meaning of Article 6 of the Convention by virtue of its composition; leaked: 58141/00; QI spans: 14 April 2000; 15 April 1999 |
| legal_0062 | generic_llm | 0.887 | 0.500 | 0.500 | direct leak, QI 3 | QA: What core claim was raised?; audited: there had been an unlawful use of lethal force against the deceased, Mr John Hemsworth; omitted: there had been an unlawful use of lethal force against the deceased, Mr John Hemsworth; leaked: 58559/09; QI spans: 12 October 2009; Northern Ireland |
| legal_0053 | generic_llm | 0.886 | 0.500 | 0.500 | direct leak, QI 3 | QA: What core claim was raised?; audited: the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he had attempted secretly to film her naked in their bathroom when she was 14 years old; omitted: the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity when he had attempted secretly to film her naked in their bathroom when she was 14 years old; leaked: 5786/08; QI spans: 21 January 2008; 14 years old |
| legal_0018 | critical_span_guard_extracted | 0.885 | 1.000 | 0.500 | none | QA: What core claim was raised?; omitted: the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively |
| legal_0029 | privacy_first_llm | 0.881 | 1.000 | 0.667 | none | QA: What core claim was raised?; omitted: had been brought against her on the grounds that the preparatory stages of the proceedings at both first instance and on appeal had been directed by the same person, the public prosecutor had not been appointed in accordance with domestic law and there had been no public hearing either at first instance or on appeal |

### High Similarity But Privacy Failure

| ID | Method | Token F1 | Audited TCFR | QA | Privacy flags | Failure signal |
|---|---|---:|---:|---:|---|---|
| legal_0029 | generic_llm | 0.944 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 35396/97; QI spans: 13 January 1997; 1 June 1999 |
| legal_0037 | generic_llm | 0.937 | 1.000 | 1.000 | direct leak, QI 3 | leaked: Ms Nuray Şen; QI spans: 25 April 1996; 30 April 2002 |
| legal_0047 | generic_llm | 0.928 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 17906/15; QI spans: 10 April 2015; 21 May 2013 |
| legal_0054 | critical_span_guard_extracted | 0.919 | 1.000 | 0.667 | QI 3 | QA: What core claim was raised?; omitted: when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas the survivor of a married couple or a homosexual relationship registered under the Civil Partnership Act 2004 would be exempt from paying inheritance tax in these circumstances; QI spans: sister; sister’s |
| legal_0064 | generic_llm | 0.918 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 28881/07; QI spans: 7 July 2007 |
| legal_0065 | generic_llm | 0.918 | 1.000 | 1.000 | QI 2 | QI spans: 24 April 2009 |
| legal_0005 | critical_span_guard_extracted | 0.917 | 1.000 | 1.000 | QI 3 | QI spans: Northern Ireland; 1976 |
| legal_0004 | generic_llm | 0.915 | 1.000 | 1.000 | direct leak, QI 3 | leaked: 30457/06; QI spans: 20 July 2006 |

## Takeaway

Surface overlap can reward outputs that retain original identifiers and quasi-identifiers, and it can miss exact QA failures or audited fact losses. The paper should therefore treat edit rate and generic similarity as diagnostic foils, not headline privacy or utility metrics.
