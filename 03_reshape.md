# 03 Reshape: long to wide (and VV)

*Long* = one row per observation (an id, a variable name, a value).
*Wide* = one row per unit, each former variable spread into its own column.

pandas verbs: `pivot` / `pivot_table` (long→wide), `melt` (wide→long).
tidyr verbs: `pivot_wider` (long→wide), `pivot_longer` (wide→long).

---

### Time series: long → wide

**Python code**
```python
ts = pd.read_csv("data/sample_timeseries_long.csv")   # date, series, value
ts_wide = ts.pivot(index="date", columns="series", values="value").reset_index()
```
**Python example**
```python
ts_wide.head(3)
#         date  cpi_index  gdp_index  unemployment
#   2022-01-01    100.036    101.071         5.207
#   2022-02-01     99.255    101.753         5.434
```
**R code**
```r
ts <- read_csv("data/sample_timeseries_long.csv")
ts_wide <- ts %>% pivot_wider(names_from = series, values_from = value)
```
**R example**
```r
head(ts_wide, 3)
# # A tibble: 3 x 4
#   date       cpi_index gdp_index unemployment
#   2022-01-01      100.      101.          5.21
```

---

### Time series: wide → long

**Python code**
```python
ts_back = ts_wide.melt(id_vars="date", var_name="series", value_name="value")
```
**Python example**
```python
ts_back.head(2)
#         date     series    value
#   2022-01-01  cpi_index  100.036
```
**R code**
```r
ts_back <- ts_wide %>% pivot_longer(cols = -date, names_to = "series",
                                    values_to = "value")
```
**R example**
```r
head(ts_back, 2)
```

---

### Panel, one variable: long → wide (years become columns)

**Python code**
```python
panel = pd.read_csv("data/sample_panel.csv")
gdp_wide = panel.pivot(index="countrycode", columns="year", values="dlny")
gdp_wide.columns = [f"y{c}" for c in gdp_wide.columns]     # y1995, y1996, ...
gdp_wide = gdp_wide.reset_index()
```
**Python example**
```python
gdp_wide.iloc[:3, :5]
#   countrycode     y1995    y1996    y1997     y1998
#           BRA -0.039792 0.042483 0.017926 -0.024416
#           DEU  0.028031 0.051979 0.005411  0.005021
```
**R code**
```r
panel <- read_csv("data/sample_panel.csv")
gdp_wide <- panel %>% select(countrycode, year, dlny) %>%
  pivot_wider(names_from = year, values_from = dlny, names_prefix = "y")
```
**R example**
```r
gdp_wide[1:3, 1:5]
# # A tibble: 3 x 5  with columns countrycode, y1995, y1996, y1997, y1998
```

---

### Panel, one variable: wide → long

**Python code**
```python
gdp_long = (gdp_wide.melt(id_vars="countrycode", var_name="year", value_name="dlny")
                    .assign(year=lambda d: d["year"].str.lstrip("y").astype(int)))
```
**Python example**
```python
gdp_long.head(2)
#   countrycode  year      dlny
#           BRA  1995 -0.039792
```
**R code**
```r
gdp_long <- gdp_wide %>%
  pivot_longer(cols = -countrycode, names_to = "year", values_to = "dlny",
               names_prefix = "y", names_transform = list(year = as.integer))
```
**R example**
```r
head(gdp_long, 2)
```

---

### Panel, many variables at once: long → wide

**Python code**
```python
panel_wide = panel.pivot_table(index="countrycode", columns="year",
                               values=["dlny", "rer", "cpi"], aggfunc="first")
panel_wide.columns = [f"{var}_{yr}" for var, yr in panel_wide.columns]  # dlny_1995, rer_1995, ...
panel_wide = panel_wide.reset_index()
```
**Python example**
```python
[c for c in panel_wide.columns if c.endswith("_1995")]
#   ['cpi_1995', 'dlny_1995', 'rer_1995']
```
**R code**
```r
panel_wide <- panel %>%
  pivot_wider(id_cols = countrycode, names_from = year,
              values_from = c(dlny, rer, cpi), names_sep = "_")
```
**R example**
```r
grep("_1995$", names(panel_wide), value = TRUE)
# "dlny_1995" "rer_1995" "cpi_1995"
```

---

### Panel, many variables: wide → long (recover the panel)

**Python code**
```python
long = panel_wide.melt(id_vars="countrycode", var_name="var_year", value_name="value")
long[["variable", "year"]] = long["var_year"].str.rsplit("_", n=1, expand=True)
long["year"] = long["year"].astype(int)
panel_long = (long.pivot_table(index=["countrycode", "year"],
                               columns="variable", values="value").reset_index())
```
**Python example**
```python
panel_long.columns.tolist()
#   ['countrycode', 'year', 'cpi', 'dlny', 'rer']
```
**R code**
```r
panel_long <- panel_wide %>%
  pivot_longer(cols = -countrycode,
               names_to = c(".value", "year"), names_pattern = "(.*)_(\\d+)",
               names_transform = list(year = as.integer))
```
**R example**
```r
names(panel_long)
# "countrycode" "year" "dlny" "rer" "cpi"
```

---

### Tidy (unit, year, variable, value) → model-ready

When data arrives stacked as variable/value and you want unit-year rows with one
column per variable ( usual metrics layout):

**Python code**
```python
tidy = panel.melt(id_vars=["countrycode", "year"],
                  value_vars=["dlny", "rer", "cpi"],
                  var_name="variable", value_name="value")
model_ready = (tidy.pivot_table(index=["countrycode", "year"],
                                columns="variable", values="value").reset_index())
```
**Python example**
```python
model_ready.head(1)
#   countrycode  year   cpi      dlny     rer
#           BRA  1995  0.00 -0.039792  87.84
```
**R code**
```r
tidy_panel <- panel %>%
  pivot_longer(c(dlny, rer, cpi), names_to = "variable", values_to = "value")
model_ready <- tidy_panel %>%
  pivot_wider(id_cols = c(countrycode, year), names_from = variable,
              values_from = value)
```
**R example**
```r
head(model_ready, 1)
```
