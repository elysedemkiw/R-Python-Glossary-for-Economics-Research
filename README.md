#R & Python Glossary for Econ Research

Basic but common tools:) 

| # | File | Actions covered |
|---|------|-----------------|
| 01 | Inspect | read CSV/Excel/Stata/parquet, first look, dimensions, frequency tables, write out |
| 02 | Clean | names, types, strings, dates, recode, bucket, filter, dedupe, winsorise, lag/lead, within-group demean, interpolate |
| 03 | Reshape | long ↔ wide for a time series **and** a panel, one and many variables, tidy → model-ready |
| 04 | Missing | counts and shares, by group, **consecutive-gap (run-length) detection**, time-index gaps |
| 05 | Summaries | describe, group summaries, frequency/share, balance table, correlations |
| 06 | Plots | line, ranked bar, grouped bar, scatter+fit, facets, distribution, dumbbell, coefficient plot |
| 07 | Regression tables | tidy one model, several side by side, export to LaTeX/Word, robust/clustered SE, panel fixed effects |


```bash
# 1. generate the example data (writes two CSVs into data/)
python data/make_sample_data.py

# 2. open any glossary/*.md and paste the snippet you need.
#    Run code from the repo root so the data/... paths resolve.
```

Python needs `pandas numpy matplotlib scipy statsmodels` (see `requirements.txt`).
R needs `tidyverse haven readxl janitor zoo broom modelsummary fixest naniar`.
