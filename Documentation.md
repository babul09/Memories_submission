# ML Challenge 2026: Business Entity Resolution Solution

**Team Name:** Memories

**Team Members:** Babul Bishwas, Anshuman Kumar, Sadham Mydeen

**Submission Date:** [Date]

---

## 1. Executive Summary

We develop a large-scale business entity resolution pipeline for identifying corresponding business records across three independent data sources.

The solution uses a multi-stage pipeline consisting of:

1. Data validation and preprocessing.
2. Candidate generation through blocking.
3. Similarity feature computation.
4. Candidate scoring and matching.
5. Conservative final match selection.
6. Explicit singleton handling.
7. Submission validation.

The approach is designed to handle noisy business names, inconsistent addresses, missing address information, multilingual records, and one-to-many relationships while remaining computationally feasible for datasets containing millions of records.

Because the evaluation metric is macro F₀.₅, the solution places particular emphasis on precision while maintaining sufficiently high candidate recall.

The implementation is being developed experimentally. Decisions about blocking strategies, similarity features, model type, and thresholds will be finalized only after evaluation on the supplied training data.

---

## 2. Methodology

### 2.1 Problem Analysis

The training data contains:

- **2,206,821** Source 1 entities.
- **5,034,616** Source 2 records.
- **5,285,603** Source 3 records.

Source 1 contains no missing values in the provided fields.

Source 2 contains **168,967 missing addresses (3.36%)**, while Source 3 contains **175,916 missing addresses (3.33%)**.

The training data contains businesses from the **US and India**.

The test data additionally contains **France**, making it important that the pipeline does not assume that the training countries are an exhaustive set.

The test data contains:

- **1,732,544** Source 1 entities.
- **4,887,273** Source 2 records.
- **5,082,316** Source 3 records.

Test-set country distribution includes:

- India
- US
- France

The business-name fields are relatively short, with training medians of approximately **24–25 characters** and maximum lengths above 100 characters.

Addresses are longer and more variable, with training medians of approximately **37–41 characters** and maximum lengths reaching approximately 250 characters.

Observed representation differences include:

- Abbreviated legal/business names.
- Typos.
- Different word ordering.
- Upper/lower-case differences.
- Punctuation differences.
- Multilingual and non-Latin business names.
- Different address ordering.
- Abbreviated geographic information.
- Missing addresses.

The ground-truth distribution also shows that singleton handling is important. Of the **2,206,821 Source 1 training entities, 123,247 (5.58%) have no matching records**.

Among non-singleton Source 1 entities, the number of matches can vary considerably, with the observed maximum being **11 matches for a single Source 1 entity**.

### Match-count distribution

| Matches | Source 1 entities | Percentage |
| ------: | ----------------: | ---------: |
| 0 | 123,247 | 5.58% |
| 1 | 119,157 | 5.40% |
| 2 | 375,212 | 17.00% |
| 3 | 530,841 | 24.05% |
| 4 | 484,115 | 21.94% |
| 5 | 321,957 | 14.59% |
| 6 | 164,868 | 7.47% |
| 7 | 63,968 | 2.90% |
| 8 | 18,680 | 0.85% |
| 9 | 4,205 | 0.19% |
| 10 | 534 | 0.02% |
| 11 | 37 | 0.00% |

This distribution indicates that the solution must support both entities with no matches and entities with multiple valid matches rather than assuming a one-to-one relationship.

---

### 2.2 Solution Strategy

**Approach Type:** Hybrid Blocking + Similarity-Based Matching

**Core Strategy:** Reduce the search space through high-recall candidate generation, then apply more expensive similarity features and a matching model only to candidate pairs.

The planned pipeline is:

```text
Raw TSV data
     |
     v
Data validation
     |
     v
Light normalization
     |
     v
Blocking / candidate generation
     |
     v
Candidate pairs
     |
     v
Similarity features
     |
     v
Matching model
     |
     v
Threshold / decision logic
     |
     v
Final entity matches
     |
     v
Submission validation
```

The exact blocking rules, features, model, and threshold will be selected experimentally.

---

# 3. Data Handling and Preprocessing

## 3.1 Raw Data Preservation

The original supplied TSV files are treated as immutable input data.

The preprocessing stage does **not** replace or modify the original business names, addresses, or country values.

Instead, additional normalized representations are generated.

The design is:

```text
Original fields
     |
     +--> business_name
     +--> business_address
     +--> country
     |
     v
Generated representations
     |
     +--> name_norm
     +--> name_compact
     +--> name_tokens
     +--> address_missing
     +--> address_norm
     +--> address_compact
     +--> address_tokens
     +--> address_numbers
     +--> country_norm
```

This allows later experiments to compare different representations without losing the original data.

---

## 3.2 Preprocessing Philosophy

The initial preprocessing strategy is intentionally conservative.

The goal is to remove superficial formatting differences while preserving information that may be useful for entity resolution.

The preprocessing stage does **not** attempt to:

- Correct spelling errors.
- Determine whether two businesses are the same entity.
- Use external business databases.
- Use geocoding services.
- Perform external entity lookup.
- Hard-code the set of possible countries.
- Replace raw values with a single "perfect" canonical representation.

Typos and more complex variations are intended to be handled by the similarity and matching stages.

---

## 3.3 Current Normalization

The current preprocessing implementation is located at:

```text
code/business_entity_resolution/src/preprocessing.py
```

The same preprocessing function is intended to be applied to all training and test sources.

The current normalized representations are:

| Column | Purpose |
|---|---|
| `name_norm` | Conservative normalized business name |
| `name_compact` | Business name with punctuation/spacing removed |
| `name_tokens` | Tokenized business name |
| `address_missing` | Indicates whether an address is unavailable |
| `address_norm` | Conservative normalized address |
| `address_compact` | Compact address representation |
| `address_tokens` | Tokenized address |
| `address_numbers` | Extracted numeric components from the address |
| `country_norm` | Normalized country representation |

The original columns remain present alongside these derived columns.

### Current normalization operations

The initial normalization performs:

- Unicode normalization.
- Case folding.
- Whitespace normalization.
- Conservative punctuation/spacing normalization.
- Token extraction.
- Numeric component extraction.

The current implementation deliberately avoids aggressive transformations such as spelling correction or external transliteration.

---

## 3.4 Intermediate Processed Data

Derived preprocessing outputs are stored separately from the original datasets.

Current intermediate format:

```text
output/
└── processed/
    ├── train_source1.parquet
    ├── train_source2.parquet
    ├── train_source3.parquet
    ├── test_source1.parquet
    ├── test_source2.parquet
    └── test_source3.parquet
```

These files are reproducible derived artifacts and may be regenerated whenever the preprocessing implementation changes.

The original TSV files remain unchanged.

Parquet is used for intermediate processed data to avoid repeatedly parsing the large TSV files during experimentation.

---

## 3.5 Preprocessing Validation

The preprocessing implementation has currently been tested successfully on:

**`train_source1.tsv`**

Observed result:

- Rows processed: **2,206,821**
- Output columns: **13**
- Parquet output successfully generated.
- Original fields preserved.
- Derived normalized fields generated successfully.

Example transformation:

```text
Original:
1795 Westchester Drive, High Point, NC

Normalized:
1795 westchester drive, high point, nc

Extracted address numbers:
[1795]
```

Another example:

```text
Original:
B+ Retail Inc

name_norm:
b+ retail inc

name_compact:
bretailinc
```

The preprocessing stage will be tested against the remaining sources before the full matching pipeline is developed.

---

# 4. Candidate Generation (Blocking)

Blocking is a central component because the Source 1, Source 2, and Source 3 datasets contain millions of records.

A brute-force comparison between all Source 1 and Source 2/3 records would result in an infeasible number of pair comparisons.

The candidate-generation stage will therefore generate a restricted set of potentially matching records.

## 4.1 Blocking Strategies to Investigate

The following strategies will be evaluated:

- Country-based blocking.
- Exact normalized business-name components.
- Business-name token blocking.
- Character-level name prefixes.
- Address-token blocking.
- Postal/PIN information where available.
- Exact normalized field components.
- Multiple complementary blocking rules.
- Approximate name retrieval where necessary.

Blocking rules will initially be combined using a union strategy.

This means a candidate pair retrieved by any sufficiently reliable blocking rule can proceed to the matching stage.

## 4.2 Blocking Objective

The primary objective of blocking is **high candidate recall**.

A true match that is never included in the candidate set cannot be recovered by the downstream matching model.

Therefore:

```text
Blocking:
    prioritize recall

Matching:
    control precision
```

Blocking recall will be measured against the training ground truth.

## 4.3 Blocking Results

**Status:** Not yet implemented.

| Metric | Result |
|---|---:|
| Candidate pairs | [To be measured] |
| Blocking recall | [To be measured] |
| Candidate reduction ratio | [To be measured] |
| Runtime | [To be measured] |
| Memory usage | [To be measured] |

---

# 5. Matching Model

## 5.1 Candidate-Pair Features

After blocking, candidate pairs will be represented using similarity features.

### Name features

Candidate features include:

- Normalized exact name match.
- Compact-name exact match.
- Token overlap.
- Jaccard similarity.
- Character-level similarity.
- Levenshtein-style similarity.
- Partial fuzzy similarity.
- TF-IDF cosine similarity.

### Address features

Candidate features include:

- Normalized address similarity.
- Compact-address similarity.
- Token overlap.
- Character-level similarity.
- Edit-distance similarity.
- Postal/PIN agreement where available.
- Shared geographic/address tokens.
- Numeric-component overlap.

### Other features

Additional features include:

- Country agreement.
- Missing-address indicators.
- Combined name/address similarity.
- Relative candidate score.
- Difference between the best and second-best candidate where applicable.

The exact feature set will be selected through controlled experiments.

---

## 5.2 Model Type

The final matching model has not yet been selected.

Candidate approaches will be evaluated using the training data.

The initial preference is for a lightweight model that:

- Can score large numbers of candidate pairs efficiently.
- Handles heterogeneous similarity features.
- Can be trained using the supplied training data.
- Allows threshold tuning.
- Can be reproduced easily within the challenge constraints.

Potential baseline models will be evaluated before selecting the final model.

---

## 5.3 Training and Validation

Training/validation experiments will be performed using the supplied training data and ground truth.

Validation will be designed to avoid unnecessary information leakage between training and validation entities.

Model selection will consider:

- Precision.
- Recall.
- Macro F₀.₅.
- False-positive behavior.
- False-negative behavior.
- Runtime.
- Memory usage.

The final threshold will be selected using validation performance rather than arbitrary similarity cutoffs.

---

## 5.4 Threshold Selection

The primary evaluation target is **macro F₀.₅**.

The threshold-selection process will investigate multiple thresholds and measure the resulting entity-level performance.

Particular attention will be given to:

- False merges.
- Ambiguous business names.
- Generic business names.
- Singleton entities.
- Missing-address records.
- Multiple valid matches for a Source 1 entity.

---

# 6. Results & Error Analysis

## 6.1 Validation Results

**Status:** Pending implementation of blocking and matching.

| Metric | Result |
|---|---:|
| Macro F₀.₅ | [To be measured] |
| Precision | [To be measured] |
| Recall | [To be measured] |
| Blocking recall | [To be measured] |
| Candidate pairs | [To be measured] |
| Candidate reduction ratio | [To be measured] |
| Runtime | [To be measured] |
| Peak memory | [To be measured] |

---

## 6.2 Threshold Experiment

A threshold sweep will be performed after the matching model is implemented.

| Threshold | Precision | Recall | Macro F₀.₅ | Candidate/Match Count |
|---:|---:|---:|---:|---:|
| [ ] | [ ] | [ ] | [ ] | [ ] |
| [ ] | [ ] | [ ] | [ ] | [ ] |
| [ ] | [ ] | [ ] | [ ] | [ ] |

The selected threshold will be documented after validation.

---

## 6.3 Common False Positives

To be determined through validation error analysis.

Particular attention will be given to:

- Similar business names at different addresses.
- Generic business names.
- Short business names.
- Records sharing common geographic tokens.
- Over-aggressive fuzzy matches.
- Incorrect matches caused by weak blocking keys.

---

## 6.4 Common False Negatives

To be determined through validation error analysis.

Particular attention will be given to:

- Strongly abbreviated names.
- Typographical differences.
- Different transliterations or scripts.
- Missing addresses.
- Unusual address ordering.
- Candidates missed by blocking.
- Excessively restrictive blocking rules.

---

# 7. Experiment Log

This section records important implementation decisions and experimental results so that approaches are not accidentally repeated or forgotten.

## Experiment 001 — Initial Data Analysis

**Status:** Completed

### Observations

- Millions of records are present in each source.
- Source 1 contains 2,206,821 training entities.
- Source 2 and Source 3 contain substantially more records.
- Some Source 2/3 addresses are missing.
- The test set contains France in addition to the US and India present in training.
- Source 1 entities can have zero, one, or multiple matches.
- The maximum observed number of matches for a Source 1 entity is 11.
- 5.58% of training Source 1 entities have zero matches.

### Decision

A brute-force matching strategy is not appropriate.

The pipeline must use blocking followed by more expensive pairwise matching.

---

## Experiment 002 — Preserve Raw Data and Generate Derived Representations

**Status:** Completed

### Decision

The original TSV data will remain untouched.

Preprocessing will generate additional normalized representations rather than replacing the raw fields.

### Reason

Different matching experiments may require different representations. Keeping the raw data allows representations to be changed without losing information.

---

## Experiment 003 — Conservative Text Normalization

**Status:** Completed — initial version

### Tested on

`train_source1.tsv`

### Operations

- Unicode normalization.
- Case folding.
- Whitespace normalization.
- Conservative punctuation normalization.
- Tokenization.
- Numeric extraction from addresses.

### Result

Successfully processed:

**2,206,821 rows**

and generated:

**13 columns**

including the original fields and normalized representations.

### Decision

Keep preprocessing conservative.

Do not attempt spelling correction, entity identification, or external data enrichment at this stage.

---

## Experiment 004 — Parquet Intermediate Storage

**Status:** Completed

### Decision

Use Parquet for derived preprocessing outputs.

### Reason

The datasets contain millions of records. Repeatedly parsing the original TSV files during experiments is unnecessary overhead.

The Parquet files are derived artifacts and can be regenerated whenever preprocessing changes.

---

## Experiment 005 — Dependency for Parquet Support

**Status:** Completed

### Decision

Use `pyarrow` for Pandas Parquet support.

### Reason

Pandas requires a Parquet engine such as `pyarrow` or `fastparquet`.

The selected dependency will be pinned in `requirements.txt`.

---

## Experiment 006 — Blocking

**Status:** Not started

### Planned investigation

Evaluate multiple complementary blocking strategies and measure:

- Candidate count.
- Blocking recall.
- Reduction ratio.
- Runtime.
- Memory usage.

---

## Experiment 007 — Similarity Features

**Status:** Not started

### Planned investigation

Evaluate name, address, numeric, country, and combined similarity features.

---

## Experiment 008 — Matching Model

**Status:** Not started

### Planned investigation

Compare lightweight candidate-scoring models using the same validation procedure.

---

## Experiment 009 — Threshold Selection

**Status:** Not started

### Planned investigation

Perform a threshold sweep and evaluate macro F₀.₅ at the entity level.

---

## Experiment 010 — Error Analysis

**Status:** Not started

### Planned investigation

Analyze false positives and false negatives by error category.

---

# 8. Conclusion

The initial dataset analysis demonstrates that the challenge requires a scalable entity-resolution system capable of handling:

- Millions of records.
- Noisy business names.
- Inconsistent addresses.
- Missing information.
- Multilingual records.
- One-to-many relationships.
- Entities with no matches.

The first implemented component is a conservative preprocessing layer that preserves raw data while generating additional normalized representations.

The next stage is blocking, which will determine how the millions of records are reduced to a computationally manageable set of candidate pairs.

Final model configuration, blocking rules, thresholds, candidate counts, runtime, and validation performance will be reported after controlled experiments on the training data.

---

# Appendix A — Code Artefacts

The runnable implementation is provided under:

```text
code/business_entity_resolution/
```

Current/expected structure:

```text
code/
└── business_entity_resolution/
    ├── src/
    │   ├── preprocessing.py
    │   ├── blocking.py
    │   ├── features.py
    │   ├── matching.py
    │   ├── evaluation.py
    │   └── main.py
    │
    ├── README.md
    └── requirements.txt
```

Additional modules may be added as the implementation develops.

The final pipeline produces:

```text
output/
├── matching_results.tsv
└── candidate_pairs.tsv
```

Intermediate derived preprocessing data is stored separately under:

```text
output/
└── processed/
```

---

# Appendix B — Reproducibility

The intended workflow is:

```text
Supplied TSV files
        |
        v
Preprocessing
        |
        v
Processed intermediate data
        |
        v
Blocking
        |
        v
Candidate pairs
        |
        v
Feature generation
        |
        v
Model scoring
        |
        v
Final matches
        |
        v
Submission validation
```

All derived data should be reproducible from the supplied datasets and the code in the repository.

The original supplied datasets should not be modified.

---

# Appendix C — Final Results

This section will be completed after the final experiments.

### Final Model

**Model:** [To be determined]

**Parameters:** [To be determined]

**Threshold:** [To be determined]

### Final Performance

**Macro F₀.₅:** [To be measured]

**Precision:** [To be measured]

**Recall:** [To be measured]

**Blocking Recall:** [To be measured]

### Final Candidate Statistics

**Candidate pairs:** [To be measured]

**Candidate reduction ratio:** [To be measured]

### Runtime

**Preprocessing:** [To be measured]

**Blocking:** [To be measured]

**Feature generation:** [To be measured]

**Matching:** [To be measured]

**Total:** [To be measured]

### Error Analysis

[To be completed after final validation.]
