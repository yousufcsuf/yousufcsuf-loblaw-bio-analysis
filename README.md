# Loblaw Bio Immune Cell Analysis

## Overview

This project implements the four parts of the Loblaw Bio clinical-trial assessment using Python, SQLite, pandas, SciPy, Plotly, Streamlit, and pytest.

It:

- loads `cell-count.csv` into SQLite
- calculates per-sample immune-cell frequencies
- compares miraclib responders vs non-responders
- performs statistical testing and boxplot visualization
- answers the requested baseline cohort questions
- provides an interactive Streamlit dashboard

Dashboard:  
https://yousufcsuf-loblaw-bio-analysis-z5jyfy2c5l9rfqkjfwocyo.streamlit.app/

---

## Quick Start

Designed for GitHub Codespaces.

### Install dependencies

```bash
make setup
```

### Run the full pipeline

```bash
make pipeline
```

This runs:

```bash
python load_data.py
python analysis.py
```

It creates the SQLite database, loads the data, performs Parts 2–4, and generates the output files.

### Start the dashboard

```bash
make dashboard
```

### Run tests

```bash
pytest -q
```

Expected grader workflow:

```bash
make setup
make pipeline
make dashboard
```

---

## Project Structure

```text
.
├── cell-count.csv
├── load_data.py
├── analysis.py
├── app.py
├── requirements.txt
├── Makefile
├── README.md
├── tests/
│   └── test_analysis.py
└── outputs/
```

`make pipeline` creates `clinical_trial.db` in the repository root.

---

# Part 1: Data Management

## Database Schema

The CSV contains subject-level, sample-level, and cell-measurement data, so the database uses three tables.

### `subjects`

```text
project
subject
condition
age
sex
treatment
response
```

Primary key:

```text
(project, subject)
```

### `samples`

```text
sample
project
subject
sample_type
time_from_treatment_start
```

Primary key:

```text
sample
```

Foreign key:

```text
(project, subject)
REFERENCES subjects(project, subject)
```

### `cell_counts`

```text
sample
population
count
```

Primary key:

```text
(sample, population)
```

Foreign key:

```text
sample
REFERENCES samples(sample)
```

The five cell-count columns are converted from wide to long format before loading:

```text
b_cell
cd8_t_cell
cd4_t_cell
nk_cell
monocyte
```

## Schema Rationale

The schema models:

```text
Subject -> Sample -> Cell Measurement
```

This reduces repeated data, improves data integrity, and makes SQL analysis easier.

For larger production workloads, I would keep the same logical schema but migrate from SQLite to PostgreSQL and add indexes on commonly filtered/joined columns such as project, subject, sample, treatment, condition, timepoint, and population.

---

# Part 2: Cell Population Frequencies

For each sample:

```text
total_count = sum of the five population counts
```

For each population:

```text
percentage = count / total_count * 100
```

The result contains:

```text
sample
total_count
population
count
percentage
```

Output:

```text
outputs/frequency_table.csv
```

The pipeline validates that percentages sum to approximately 100% for each sample.

---

# Part 3: Statistical Analysis

The comparison includes only:

```text
condition = melanoma
treatment = miraclib
sample_type = PBMC
response = yes or no
```

Responders and non-responders are compared for all five immune-cell populations.

A two-sided Mann–Whitney U test is used, with Bonferroni correction for five comparisons:

```text
0.05 / 5 = 0.01
```

Result:

> No immune-cell population showed a statistically significant difference in relative frequency between miraclib responders and non-responders after Bonferroni correction.

Outputs:

```text
outputs/statistical_results.csv
outputs/responder_boxplots.html
```

The same boxplots and statistical results are also shown in the dashboard.

Note: repeated samples from the same subjects mean the observations are not fully independent. A mixed-effects or repeated-measures model would be more appropriate for a production longitudinal analysis.

---

# Part 4: Data Subset Analysis

Baseline cohort:

```text
condition = melanoma
treatment = miraclib
sample_type = PBMC
time_from_treatment_start = 0
```

Results:

```text
Total samples: 656

Samples by project:
prj1: 384
prj3: 272

Subjects by response:
Responders: 331
Non-responders: 325

Subjects by sex:
Female: 312
Male: 344
```

For melanoma male responders at time 0 across all treatment and sample types:

```text
Average B-cell count = 10206.15
```

Output:

```text
outputs/baseline_cohort.csv
```

---

# Code Structure

## `load_data.py`

- reads `cell-count.csv`
- initializes the SQLite schema
- loads all source data
- creates `clinical_trial.db`

Run directly with:

```bash
python load_data.py
```

## `analysis.py`

- calculates frequencies
- performs statistical analysis
- runs Part 4 queries
- generates output files

## `app.py`

Displays Parts 2–4 through Streamlit.

The analysis logic is kept separate from the UI for easier testing and maintenance.

---

# Makefile

Required targets:

```bash
make setup
make pipeline
make dashboard
```

`make pipeline` runs the complete pipeline sequentially with no manual intervention.

---

# Testing

Run:

```bash
pytest -q
```

Tests verify:

- expected frequency-table row count
- percentages sum to approximately 100%
- correct baseline cohort
- correct Part 4 B-cell average

---

# Reproducibility

From a fresh GitHub Codespaces environment:

```bash
make setup
make pipeline
pytest -q
make dashboard
```

No command-line arguments or manual data-processing steps are required.

---

# Note

The assessment text mentions `quintazide`. No quintazide observations are present in the supplied dataset, so it is not included in the analysis.
