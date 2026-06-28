# Legal QA Disagreement Audit

This audit classifies exact legal QA failures using the paraphrase-aware fact judge. It does not make API calls. Article-number failures are counted as specificity losses when the related Article fact is not retained, because legal Article numbers are non-generalizable task-critical facts in this benchmark.

## Summary

| Method | Failed legal QA items | Article specificity loss | Audited utility loss | Exact-phrase artifact |
|---|---:|---:|---:|---:|
| generic_llm | 10 | 1 | 3 | 6 |
| privacy_first_llm | 46 | 21 | 13 | 12 |
| critical_span_guard_extracted | 6 | 0 | 0 | 6 |

## Interpretation

- CSG has 6 failed legal QA items; 6 are exact-phrase artifacts, 0 are audited utility losses, and 0 are Article-specificity losses.
- Most privacy-first legal failures are true utility or Article-specificity losses: the model often replaces Article numbers or concrete claims with generic legal wording. In this run, privacy-first has 21 Article-specificity losses and 13 audited utility losses.
- Generic prompting has fewer QA failures, but some high-overlap outputs still lose legal specificity or leak privacy elsewhere; use this audit alongside the privacy table.

## Failed QA Items

| ID | Method | Question | Category | Judge status | Gold answer / fact |
|---|---|---|---|---|---|
| legal_0002 | generic_llm | What core claim was raised? | exact_phrase_artifact | preserved | an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals ... |
| legal_0005 | generic_llm | What core claim was raised? | audited_utility_loss | generalized_but_acceptable | the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976 |
| legal_0014 | generic_llm | What core claim was raised? | exact_phrase_artifact | preserved | his disenfranchisement as a result of his residence outside the United Kingdom constituted a violation of Article 3 of Protocol No. 1 to the Convention, taken alone and taken together ... |
| legal_0016 | generic_llm | What core claim was raised? | audited_utility_loss | generalized_but_acceptable | the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention |
| legal_0026 | generic_llm | What core claim was raised? | exact_phrase_artifact | preserved | neither he nor counsel had been granted an opportunity at any stage of the criminal proceedings instituted against him to examine the only direct witnesses and victims of the crime ... |
| legal_0036 | generic_llm | What core claim was raised? | exact_phrase_artifact | preserved | they had violated Article 6 §§ 1 and 3 (d) (art. 6-1, art. 6-3-d) of the Convention |
| legal_0040 | generic_llm | Which substantive Article was invoked? | article_specificity_loss | not preserved | Article 18 |
| legal_0053 | generic_llm | What core claim was raised? | audited_utility_loss | generalized_but_acceptable | the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity ... |
| legal_0054 | generic_llm | What core claim was raised? | exact_phrase_artifact | preserved | when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas the survivor of a married couple or a homosexual ... |
| legal_0056 | generic_llm | What core claim was raised? | exact_phrase_artifact | preserved | shortcomings in the British health system in connection with the recruitment of locum doctors and supervision of out-of-hours locum services had led to their father’s death as a ... |
| legal_0002 | privacy_first_llm | What core claim was raised? | audited_utility_loss | generalized_but_acceptable | an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals ... |
| legal_0002 | privacy_first_llm | Which substantive Article was invoked? | exact_phrase_artifact | preserved | Article 8 |
| legal_0005 | privacy_first_llm | What core claim was raised? | audited_utility_loss | omitted | the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976 |
| legal_0005 | privacy_first_llm | Which substantive Article was invoked? | exact_phrase_artifact | preserved | Article 6 |
| legal_0006 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | omitted | Article 6 |
| legal_0007 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | omitted | Article 6 |
| legal_0009 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | omitted | Article 6 |
| legal_0011 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | omitted | Article 6 |
| legal_0012 | privacy_first_llm | What core claim was raised? | audited_utility_loss | generalized_but_acceptable | the impugned decision was disproportionate and violated her right to the enjoyment of her family life under Article 6 of the Basic Law |
| legal_0012 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | omitted | Article 6 |
| legal_0014 | privacy_first_llm | What core claim was raised? | audited_utility_loss | omitted | his disenfranchisement as a result of his residence outside the United Kingdom constituted a violation of Article 3 of Protocol No. 1 to the Convention, taken alone and taken together ... |
| legal_0015 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | generalized_but_acceptable | Article 6 |
| legal_0016 | privacy_first_llm | What core claim was raised? | audited_utility_loss | generalized_but_acceptable | the Polish authorities had failed to take effective steps to enforce his right of contact with his daughter, which had violated his rights under Article 8 of the Convention |
| legal_0017 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | generalized_but_acceptable | Article 6 |
| legal_0018 | privacy_first_llm | What core claim was raised? | audited_utility_loss | omitted | the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the ... |
| legal_0018 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | omitted | Article 1 |
| legal_0019 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | omitted | Article 6 |
| legal_0021 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | generalized_but_acceptable | Article 8 |
| legal_0022 | privacy_first_llm | What core claim was raised? | audited_utility_loss | generalized_but_acceptable | a factual error made by the Court of Cassation had infringed his right of access to court, in violation of Article 6 of the Convention |
| legal_0023 | privacy_first_llm | What core claim was raised? | exact_phrase_artifact | preserved | the length of the criminal proceedings against him |
| legal_0023 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | omitted | Article 6 |
| legal_0024 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | generalized_but_acceptable | Article 6 |
| legal_0025 | privacy_first_llm | What core claim was raised? | exact_phrase_artifact | preserved | the conduct of proceedings for the said traffic offence violated Article 4 of Protocol No. 7, given that he had been acquitted of the offence of resisting the exercise of official ... |
| legal_0026 | privacy_first_llm | What core claim was raised? | audited_utility_loss | omitted | neither he nor counsel had been granted an opportunity at any stage of the criminal proceedings instituted against him to examine the only direct witnesses and victims of the crime ... |
| legal_0026 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | omitted | Article 6 |
| legal_0028 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | omitted | Article 6 |
| legal_0029 | privacy_first_llm | What core claim was raised? | exact_phrase_artifact | preserved | had been brought against her on the grounds that the preparatory stages of the proceedings at both first instance and on appeal had been directed by the same person, the public ... |
| legal_0030 | privacy_first_llm | What core claim was raised? | audited_utility_loss | generalized_but_acceptable | the Polish authorities had failed to take effective steps to enforce his right of contact with his son, which had violated his rights under Article 8 of the Convention |
| legal_0031 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | omitted | Article 6 |
| legal_0032 | privacy_first_llm | Which substantive Article was invoked? | exact_phrase_artifact | preserved | Article 5 |
| legal_0034 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | omitted | Article 6 |
| legal_0036 | privacy_first_llm | What core claim was raised? | audited_utility_loss | omitted | they had violated Article 6 §§ 1 and 3 (d) (art. 6-1, art. 6-3-d) of the Convention |
| legal_0036 | privacy_first_llm | Which substantive Article was invoked? | exact_phrase_artifact | preserved | Article 6 |
| legal_0037 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | generalized_but_acceptable | Article 5 |
| legal_0039 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | omitted | Article 6 |
| legal_0040 | privacy_first_llm | Which substantive Article was invoked? | exact_phrase_artifact | preserved | Article 18 |
| legal_0041 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | generalized_but_acceptable | Article 10 |
| legal_0043 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | omitted | Article 6 |
| legal_0046 | privacy_first_llm | What core claim was raised? | audited_utility_loss | generalized_but_acceptable | because he was a man, he was denied social security benefits equivalent to those received by widows |
| legal_0046 | privacy_first_llm | Which substantive Article was invoked? | article_specificity_loss | generalized_but_acceptable | Article 1 |
| legal_0048 | privacy_first_llm | Which substantive Article was invoked? | exact_phrase_artifact | preserved | Article 5 |
| legal_0051 | privacy_first_llm | Which substantive Article was invoked? | exact_phrase_artifact | preserved | Article 5 |
| legal_0053 | privacy_first_llm | What core claim was raised? | audited_utility_loss | generalized_but_acceptable | the Swedish State had failed to comply with its obligation under Article 8 of the Convention to provide her with remedies against her stepfather’s violation of her personal integrity ... |
| legal_0054 | privacy_first_llm | What core claim was raised? | audited_utility_loss | generalized_but_acceptable | when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas the survivor of a married couple or a homosexual ... |
| legal_0056 | privacy_first_llm | What core claim was raised? | exact_phrase_artifact | preserved | shortcomings in the British health system in connection with the recruitment of locum doctors and supervision of out-of-hours locum services had led to their father’s death as a ... |
| legal_0059 | privacy_first_llm | Which substantive Article was invoked? | exact_phrase_artifact | preserved | Article 5 |
| legal_0002 | critical_span_guard_extracted | What core claim was raised? | exact_phrase_artifact | preserved | an investigation into their sexuality and their discharge from the Royal Navy on the basis of their homosexuality as a result of the absolute policy against the presence of homosexuals ... |
| legal_0014 | critical_span_guard_extracted | What core claim was raised? | exact_phrase_artifact | preserved | his disenfranchisement as a result of his residence outside the United Kingdom constituted a violation of Article 3 of Protocol No. 1 to the Convention, taken alone and taken together ... |
| legal_0018 | critical_span_guard_extracted | What core claim was raised? | exact_phrase_artifact | preserved | the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the ... |
| legal_0026 | critical_span_guard_extracted | What core claim was raised? | exact_phrase_artifact | preserved | neither he nor counsel had been granted an opportunity at any stage of the criminal proceedings instituted against him to examine the only direct witnesses and victims of the crime ... |
| legal_0054 | critical_span_guard_extracted | What core claim was raised? | exact_phrase_artifact | preserved | when the first of them died, the survivor would be required to pay inheritance tax on the dead sister’s share of the family home, whereas the survivor of a married couple or a homosexual ... |
| legal_0056 | critical_span_guard_extracted | What core claim was raised? | exact_phrase_artifact | preserved | shortcomings in the British health system in connection with the recruitment of locum doctors and supervision of out-of-hours locum services had led to their father’s death as a ... |

## Paper-Useful Cases

### `legal_0018` / `critical_span_guard_extracted`

- Category: `exact_phrase_artifact`
- Failed question: What core claim was raised?
- Gold answer: the demolition of a house had violated her rights to the peaceful enjoyment of her possessions and to respect for her home under Article 1 of Protocol No. 1 and Article 8 of the Convention respectively
- Judge evidence: The anonymized text states that the applicant alleged that the demolition of a house had violated her rights to peaceful enjoyment of her possessions and to respect for her home under the specified articles, maintaining the core claim with the necessary details.
- Output snippet: PROCEDURE The case originated in an application [ID] against the Kingdom of Sweden lodged with the European human rights body under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the Convention”) by a ...

### `legal_0023` / `privacy_first_llm`

- Category: `article_specificity_loss`
- Failed question: Which substantive Article was invoked?
- Gold answer: Article 6
- Judge evidence: The anonymized text states 'a procedural article' instead of 'Article 6', which does not preserve the specific legal article number.
- Output snippet: PROCEDURE The case originated in an application against a national government lodged with a human rights commission under a former human rights treaty provision by an individual, on a specific date. The applicant complained under a procedural article about ...
- Category: `exact_phrase_artifact`
- Failed question: What core claim was raised?
- Gold answer: the length of the criminal proceedings against him
- Judge evidence: The anonymized text mentions 'the length of criminal proceedings against them,' which faithfully paraphrases the original claim about the length of proceedings against the applicant.
- Output snippet: PROCEDURE The case originated in an application against a national government lodged with a human rights commission under a former human rights treaty provision by an individual, on a specific date. The applicant complained under a procedural article about ...

### `legal_0005` / `generic_llm`

- Category: `audited_utility_loss`
- Failed question: What core claim was raised?
- Gold answer: the issue of a certificate emanating from the Secretary of State, under section 42 of the Fair Employment (Northern Ireland) Act 1976
- Judge evidence: The anonymized text refers to 'the issue of a certificate issued by a government official, under relevant legislation', which generalizes the specific claim but retains the core fact about a certificate issued by a government authority under legislation.
- Output snippet: PROCEDURE The case originated in an application against a country lodged with the European Commission of Human Rights (“the Commission”) under former Article 25 of the Convention for the Protection of Human Rights and Fundamental Freedoms (“the ...

