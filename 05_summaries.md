# 05 Summaries

Descriptives, group summaries, balance tables, correlations.

---

### Describe numeric columns

**Python code**
```python
df.describe().T     # transpose so variables are rows
```
**Python example**
```python
df.describe().T[["mean", "std", "min", "max"]].round(3)
```
**R code**
```r
summary(df)         # base, per-column
```
**R example**
```r
summary(df$dlny)
#    Min. 1st Qu.  Median    Mean 3rd Qu.    Max.
```

---

### Tidy describe: one row per variable

**Python code**
```python
def describe(df):
    num = df.select_dtypes("number")
    out = num.agg(["count", "mean", "std", "min", "median", "max"]).T
    return out.rename(columns={"median": "p50"}).reset_index(names="variable")
```
**Python example**
```python
describe(df).round(3)
#   variable  count   mean    std     min   p50    max
#   dln_tot     148  0.001  0.049  -0.13  0.00  0.13
```
**R code**
```r
describe <- function(df) {
  df %>% select(where(is.numeric)) %>%
    pivot_longer(everything(), names_to = "variable") %>%
    group_by(variable) %>%
    summarise(n = sum(!is.na(value)), mean = mean(value, na.rm = TRUE),
              sd = sd(value, na.rm = TRUE), min = min(value, na.rm = TRUE),
              p50 = median(value, na.rm = TRUE), max = max(value, na.rm = TRUE),
              .groups = "drop")
}
```
**R example**
```r
describe(df)
```

---

### Summarise by group

**Python code**
```python
(df.groupby("regime")
   .agg(n=("dlny", "size"), mean_growth=("dlny", "mean"), sd_growth=("dlny", "std"))
   .reset_index())
```
**Python example**
```python
#   regime   n  mean_growth  sd_growth
#    float  79        0.019      0.031
#      peg  69        0.017      0.030
```
**R code**
```r
df %>% group_by(regime) %>%
  summarise(n = n(), mean_growth = mean(dlny, na.rm = TRUE),
            sd_growth = sd(dlny, na.rm = TRUE), .groups = "drop")
```
**R example**
```r
# # A tibble: 2 x 4  -> float 79 / 0.019, peg 69 / 0.017
```

---

### Frequency and share table

**Python code**
```python
df["regime"].value_counts()
df["regime"].value_counts(normalize=True).rename("share").reset_index()
```
**Python example**
```python
df["regime"].value_counts(normalize=True).round(3)
#   float    0.534
#   peg      0.466
```
**R code**
```r
count(df, regime, name = "n_obs") %>% mutate(share = n_obs / sum(n_obs))
```
**R example**
```r
# float 0.534, peg 0.466
```

---

### Balance table (means of many variables across a group)

**Python code**
```python
def balance_table(df, group, variables):
    return (df.groupby(group)[variables].mean().T
              .rename_axis("variable").reset_index())
```
**Python example**
```python
balance_table(df, "regime", ["dln_tot", "dlny", "rer", "cpi", "openness"]).round(3)
#   variable   float    peg
#   openness   0.60    0.58
#   ...
```
**R code**
```r
balance_table <- function(df, group, vars) {
  df %>% pivot_longer(all_of(vars), names_to = "variable") %>%
    group_by(variable, {{ group }}) %>%
    summarise(mean = mean(value, na.rm = TRUE), .groups = "drop") %>%
    pivot_wider(names_from = {{ group }}, values_from = mean)
}
```
**R example**
```r
balance_table(df, regime, c("dln_tot", "dlny", "rer", "cpi", "openness"))
```

---

### Correlation matrix

**Python code**
```python
df.select_dtypes("number").corr().round(2)
```
**Python example**
```python
df[["dlny", "openness", "cpi"]].corr().round(2)
```
**R code**
```r
df %>% select(where(is.numeric)) %>% cor(use = "pairwise.complete.obs") %>% round(2)
```
**R example**
```r
cor(df[c("dlny", "openness", "cpi")], use = "pairwise.complete.obs")
```
