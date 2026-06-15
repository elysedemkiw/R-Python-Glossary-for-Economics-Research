# 04 Missing values

Counts and shares first, then whether the gaps are
*isolated* or *consecutive runs* within each unit. The sample panel is seeded
with one isolated gap, one three-period run (IND `rer`, 2010–2012), and one
dropped span (FRA, 2008–2009) so every function returns something visible

---

### Count missing per column (and share)

**Python code**
```python
panel.isna().sum().sum()    # total NA cells
panel.isna().sum()          # per column
panel.isna().mean()         # share per column
```

Two options either `panel = pd.read_csv("[Path]")` or replace like this `df.isna().sum().sum()`
**Python example**
```python
panel.isna().sum()
#   dlny    2
#   rer     3
#   cpi     1
```
**R code**
```r
sum(is.na(panel))           # total NA cells
colSums(is.na(panel))       # per column
colMeans(is.na(panel))      # share per column
```
**R example**
```r
colSums(is.na(panel))
#   dlny rer cpi
#      2   3   1
```

---

### Tidy missingness summary table

**Python code**
```python
def miss_summary(df):
    return (pd.DataFrame({"n_missing": df.isna().sum(),
                          "pct_missing": (100 * df.isna().mean()).round(2)})
            .sort_values("n_missing", ascending=False)
            .rename_axis("column").reset_index())
```
**Python example**
```python
miss_summary(panel).head(3)
#   column  n_missing  pct_missing
#      rer          3         2.03
#     dlny          2         1.35
#      cpi          1         0.68
```
**R code**
```r
miss_summary <- function(df) {
  tibble(column = names(df),
         n_missing = colSums(is.na(df)),
         pct_missing = round(100 * colMeans(is.na(df)), 2)) %>%
    arrange(desc(n_missing))
}
```
**R example**
```r
miss_summary(panel)
# # A tibble: 8 x 3  (rer 3 / 2.03, dlny 2 / 1.35, cpi 1 / 0.68, then zeros)
```

---

### Rows with any / no missing

**Python code**
```python
panel[panel.isna().any(axis=1)]    # rows with at least one NA
panel.dropna()                     # complete rows only
panel.dropna(subset=["dlny"])      # complete on specific columns
```
**Python example**
```python
len(panel), len(panel.dropna())    # (148, 142)
```
**R code**
```r
panel %>% filter(if_any(everything(), is.na))     # rows with at least one NA
panel %>% filter(if_all(everything(), ~ !is.na(.)))  # complete rows
complete.cases(panel)                              # base-R logical vector
```
**R example**
```r
c(nrow(panel), sum(complete.cases(panel)))   # 148 then 142
```

---

### Missingness by group

**Python code**
```python
(panel.groupby("countrycode")["dlny"]
      .apply(lambda s: round(100 * s.isna().mean(), 1))
      .rename("pct_dlny_missing").reset_index())
```
**Python example**
```python
#   countrycode  pct_dlny_missing
#           BRA               4.2
#           UKR               4.5
#           ...               0.0
```
**R code**
```r
panel %>% group_by(countrycode) %>%
  summarise(pct_dlny_missing = round(100 * mean(is.na(dlny)), 1), .groups = "drop")
```
**R example**
```r
# BRA 4.2, UKR 4.5, others 0.0
```

---

### Consecutive NA runs within a unit 

Run-length encoding gives one row per missing run: which unit, where it starts
and ends, and how long it is

**Python code**
```python
import numpy as np
def na_runs(df, group, time, value):
    out = []
    for key, sub in df.sort_values([group, time]).groupby(group):
        is_na = sub[value].isna().to_numpy()
        if not is_na.any():
            continue
        run_id = np.cumsum(np.r_[True, is_na[1:] != is_na[:-1]])  # new run on each flip
        s = sub.assign(_isna=is_na, _run=run_id)
        for _, r in s[s["_isna"]].groupby("_run"):
            out.append({group: key, "run_start_time": r[time].iloc[0],
                        "run_end_time": r[time].iloc[-1], "run_length": len(r)})
    return pd.DataFrame(out)
```
**Python example**
```python
na_runs(panel, "countrycode", "year", "rer")
#   countrycode  run_start_time  run_end_time  run_length
#           IND            2010          2012           3
```
**R code**
```r
na_runs <- function(df, group, time, value) {
  g <- rlang::as_name(rlang::enquo(group))    # resolve names to strings once
  t <- rlang::as_name(rlang::enquo(time))
  v <- rlang::as_name(rlang::enquo(value))
  df %>% arrange(.data[[g]], .data[[t]]) %>% group_by(.data[[g]]) %>%
    group_modify(function(.x, .key) {
      r <- rle(is.na(.x[[v]]))                 # consecutive-run encoder
      ends <- cumsum(r$lengths); starts <- ends - r$lengths + 1
      tibble(run_start_time = .x[[t]][starts], run_end_time = .x[[t]][ends],
             run_length = r$lengths, is_missing = r$values) %>%
        filter(is_missing) %>% select(-is_missing)
    }) %>% ungroup()
}
```
**R example**
```r
na_runs(panel, countrycode, year, rer)
# # A tibble: 1 x 4  -> IND, 2010, 2012, 3
```

---

### Longest NA gap per unit

A one-number-per-unit quality flag (0 if the column is complete for that unit).

**Python code**
```python
def longest_na_gap(df, group, time, value):
    runs = na_runs(df, group, time, value)
    units = pd.DataFrame({group: df[group].unique()})
    if runs.empty:
        return units.assign(max_consecutive_na=0)
    g = runs.groupby(group)["run_length"].max().rename("max_consecutive_na")
    return units.merge(g, on=group, how="left").fillna({"max_consecutive_na": 0})
```
**Python example**
```python
longest_na_gap(panel, "countrycode", "year", "rer")
#   IND -> 3, all others -> 0
```
**R code**
```r
longest_na_gap <- function(df, group, time, value) {
  na_runs(df, {{ group }}, {{ time }}, {{ value }}) %>%
    group_by({{ group }}) %>%
    summarise(max_consecutive_na = max(run_length), .groups = "drop")
}
```
**R example**
```r
longest_na_gap(panel, countrycode, year, rer)
# IND -> 3
```

---

### Gaps in the time index itself (whole rows absent)

Different question: are the periods a consecutive 1-step sequence, or are whole
unit-years missing?

**Python code**
```python
def index_gaps(df, group, time):
    def f(sub):
        n_obs = len(sub); span = int(sub[time].max() - sub[time].min() + 1)
        return pd.Series({"n_obs": n_obs, "span": span,
                          "is_consecutive": n_obs == span,
                          "n_missing_periods": span - n_obs})
    return df.sort_values([group, time]).groupby(group).apply(f).reset_index()
```
**Python example**
```python
index_gaps(panel, "countrycode", "year")
#   countrycode  n_obs  span  is_consecutive  n_missing_periods
#           FRA     24    26           False                  2
#           USA     28    28            True                  0
```
**R code**
```r
index_gaps <- function(df, group, time) {
  df %>% arrange({{ group }}, {{ time }}) %>% group_by({{ group }}) %>%
    summarise(n_obs = dplyr::n(),
              span = max({{ time }}) - min({{ time }}) + 1,
              is_consecutive = n_obs == span,
              n_missing_periods = span - n_obs, .groups = "drop")
}
```
**R example**
```r
index_gaps(panel, countrycode, year)
# FRA: n_obs 24, span 26, is_consecutive FALSE, n_missing_periods 2
```

> Tip: in R, `naniar::miss_var_summary(panel)` and `vis_miss(panel)` give
> ready-made tables and plots; in Python, `missingno.matrix(panel)` does the same.
