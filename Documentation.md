# ML Challenge 2026: Business Entity Resolution Solution

**Team Name:** Memories
**Team Members:** Babul Bishwas, Anshuman Kumar, Sadham Mydeen
**Submission Date:** [Date]

---

## 1. Executive Summary

We develop a large-scale business entity resolution pipeline for identifying corresponding business records across three independent data sources. The solution uses multi-stage candidate generation followed by similarity-based matching, with particular emphasis on high-recall blocking and precision-oriented final decisions because the evaluation metric is F₀.₅.

The approach is designed to handle noisy business names, inconsistent addresses, missing address information, multilingual records, and singleton entities while remaining computationally feasible for datasets containing millions of records.

---

## 2. Methodology

### 2.1 Problem Analysis

The training data contains:

* **2,206,821** Source 1 entities.
* **5,034,616** Source 2 records.
* **5,285,603** Source 3 records.

Source 1 contains no missing values in the provided fields. Source 2 contains **168,967 missing addresses (3.36%)**, while Source 3 contains **175,916 missing addresses (3.33%)**.

The training data contains businesses from the **US and India**. The test data additionally contains **France**, making it important that the pipeline does not assume that the training countries are an exhaustive set.

The test data contains:

* **1,732,544** Source 1 entities.
* **4,887,273** Source 2 records.
* **5,082,316** Source 3 records.

Test-set country distribution includes:

* India
* US
* France

The business-name fields are relatively short, with training medians of approximately **24–25 characters** and maximum lengths above 100 characters. Addresses are longer and more variable, with training medians of approximately **37–41 characters** and maximum lengths reaching approximately 250 characters.

Observed examples demonstrate substantial variation in representation, including:

* Abbreviated legal/business names.
* Typos.
* Different word ordering.
* Upper/lower-case differences.
* Punctuation differences.
* Multilingual and non-Latin business names.
* Different address ordering.
* Abbreviated geographic information.
* Missing addresses.

The ground-truth distribution also shows that singleton handling is important. Of the **2,206,821 Source 1 training entities, 123,247 (5.58%) have no matching records**.

Among non-singleton Source 1 entities, the number of matches can vary considerably, with the observed maximum being **11 matches for a single Source 1 entity**.

The match-count distribution is:

| Matches | Source 1 entities | Percentage |
| ------: | ----------------: | ---------: |
|       0 |           123,247 |      5.58% |
|       1 |           119,157 |      5.40% |
|       2 |           375,212 |     17.00% |
|       3 |           530,841 |     24.05% |
|       4 |           484,115 |     21.94% |
|       5 |           321,957 |     14.59% |
|       6 |           164,868 |      7.47% |
|       7 |            63,968 |      2.90% |
|       8 |            18,680 |      0.85% |
|       9 |             4,205 |      0.19% |
|      10 |               534 |      0.02% |
|      11 |                37 |      0.00% |

This distribution indicates that the solution must support both singleton entities and one-to-many relationships rather than assuming that each Source 1 entity has exactly one match.

### 2.2 Solution Strategy

**Approach Type:** Hybrid Blocking + Similarity-Based Matching

**Core Innovation:** A multi-stage candidate-generation and matching pipeline designed specifically for millions of records.

The pipeline will consist of:

1. Data loading and validation.
2. Unicode-aware field normalization.
3. Name and address representation.
4. Multiple blocking strategies.
5. Candidate-pair generation.
6. Name/address similarity feature computation.
7. Candidate scoring.
8. Conservative match selection.
9. Singleton handling.
10. Output validation.

Because the datasets contain millions of records, expensive similarity calculations will be applied only after blocking has reduced the candidate space.

---

## 3. Candidate Generation (Blocking)

Blocking is a central component of the solution because the Source 1, Source 2, and Source 3 datasets contain millions of records.

Rather than comparing every Source 1 entity against every Source 2 and Source 3 entity, the pipeline generates a restricted candidate set using multiple complementary blocking rules.

### Blocking keys used

The candidate-generation stage will investigate combinations of:

* Country.
* Normalized business-name tokens.
* Character-level name prefixes.
* Address tokens.
* Postal/PIN information where available.
* Exact normalized field components.
* Approximate name retrieval where required.

Blocking rules will be combined using a union strategy so that a pair retrieved by any sufficiently reliable blocking rule remains available for the matching stage.

### Candidate pairs generated

**Training:** [To be measured]

**Test:** [To be measured]

### How true matches were protected from being lost

Blocking recall will be explicitly evaluated against the training ground truth.

Multiple blocking strategies will be combined rather than relying on a single blocking key. This is important because a true match may have a substantially different name representation, address ordering, abbreviation pattern, or missing address.

The blocking stage will therefore prioritize **candidate recall**, while the subsequent matching stage will control false positives.

---

## 4. Matching Model

### Features Used

#### Name features

The following features will be evaluated:

* Normalized exact name match.
* Token overlap.
* Jaccard similarity.
* Character-level similarity.
* Levenshtein-style similarity.
* Partial fuzzy similarity.
* TF-IDF cosine similarity.

#### Address features

The following features will be evaluated:

* Normalized address similarity.
* Token overlap.
* Character-level similarity.
* Edit-distance similarity.
* Postal/PIN agreement where available.
* Shared geographic/address tokens.

#### Other features

Additional features include:

* Country agreement.
* Missing-address indicators.
* Combined name/address similarity.
* Relative candidate score.
* Difference between the best and second-best candidate where applicable.

### Model Type

The final matching model will be selected experimentally using the training data.

Candidate approaches will be evaluated using the same validation framework, with preference for a lightweight model that can efficiently score millions of candidate pairs.

### Threshold Selection Method

The final decision threshold will be selected using a held-out validation procedure.

The primary evaluation target will be **macro F₀.₅**, reflecting the challenge's precision-heavy objective.

Special attention will be given to:

* False merges.
* Ambiguous business names.
* Singleton entities.
* Missing-address records.
* Multiple valid matches for the same Source 1 entity.

---

## 5. Results & Error Analysis

### Validation Results

**F₀.₅ Score (macro):** [To be measured]

**Blocking recall:** [To be measured]

**Candidate pairs:** [To be measured]

**Candidate reduction ratio:** [To be measured]

### Common False Positives

To be determined through validation error analysis.

Particular attention will be given to:

* Similar business names at different addresses.
* Generic business names.
* Short business names.
* Records sharing common geographic tokens.
* Over-aggressive fuzzy matches.

### Common False Negatives

To be determined through validation error analysis.

Particular attention will be given to:

* Strongly abbreviated names.
* Typographical differences.
* Different transliterations or scripts.
* Missing addresses.
* Unusual address ordering.
* Candidates missed by blocking.

---

## 6. Conclusion

The dataset analysis demonstrates that the challenge requires a scalable entity-resolution system capable of handling millions of records, noisy business names and addresses, missing information, multilingual records, and one-to-many relationships.

Our solution therefore focuses on high-recall multi-stage candidate generation followed by precision-oriented matching and explicit singleton handling. Final model configuration, threshold values, candidate counts, and validation performance will be reported after controlled experiments on the training data.

---

## Appendix

### A. Code Artefacts

The complete runnable implementation is provided under:

`code/business_entity_resolution/`

Expected structure:

```text
code/
└── business_entity_resolution/
    ├── src/
    │   ├── data_loading.py
    │   ├── preprocessing.py
    │   ├── blocking.py
    │   ├── features.py
    │   ├── matching.py
    │   ├── evaluation.py
    │   └── main.py
    ├── README.md
    └── requirements.txt
```

The pipeline produces:

```text
output/
├── matching_results.tsv
└── candidate_pairs.tsv
```

The README documents the commands required to reproduce the outputs from the supplied datasets.

### B. Additional Results

The final report will include, where useful:

* Blocking recall.
* Candidate-pair counts.
* Candidate reduction ratio.
* F₀.₅ across matching thresholds.
* Precision/recall measurements.
* Error-category analysis.
* Performance by country.
* Performance for records with missing addresses.
* Runtime and memory statistics.
