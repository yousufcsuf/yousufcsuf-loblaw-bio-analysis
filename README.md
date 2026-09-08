# Loblaw Bio Immune Cell Analysis

## Overview

This project analyzes immune-cell population data from a clinical trial for Loblaw Bio.

The project is designed to:

- load the provided `cell-count.csv` dataset into a normalized SQLite database
- calculate relative frequencies for five immune-cell populations
- compare miraclib responders and non-responders among melanoma PBMC samples
- perform statistical testing on responder vs non-responder frequencies
- analyze a specific baseline melanoma cohort
- provide an interactive Streamlit dashboard displaying results from Parts 2–4
- provide a reproducible workflow that can be executed using GitHub Codespaces

The project uses:

- Python
- pandas
- SQLite
- SciPy
- Plotly
- Streamlit
- pytest

---

## Quick Start

This project is designed to run in GitHub Codespaces.

### 1. Install dependencies

```bash
make setup
```
