# 01: Read, write, inspect

Each action below shows the Python code, a Python example, then the R code and an
R example. Run everything from the repo root so `data/...` resolves

---

### Read a CSV

**Python code**
```python
import pandas as pd
df = pd.read_csv("data/sample_panel.csv")
```
**Python  example**
```python
df = pd.read_csv("data/sample_panel.csv")
df.shape          # (148, 8)
```
**R code**
```r
library(readr)
df <- read_csv("data/sample_panel.csv")
```
**R example**
```r
df <- read_csv("data/sample_panel.csv")
dim(df)           # [1] 148   8
```

---

### Read other formats (Stata, Excel, parquet)

**Python code**
```python
df = pd.read_stata("file.dta")
df = pd.read_excel("file.xlsx", sheet_name=0, skiprows=0)   # needs openpyxl
df = pd.read_parquet("file.parquet")
df = pd.read_csv("file.csv", na_values=["", "NA", "."])      # custom NA strings
df = pd.read_csv("file.csv", skiprows=3)                      # skip metadata rows
```
**Python example**
```python
df = pd.read_stata("wages.dta")   # Stata labels become a pandas categorical
```
**R code**
```r
df <- haven::read_dta("file.dta")
df <- readxl::read_excel("file.xlsx", sheet = 1, skip = 0)
df <- read_csv("file.csv", na = c("", "NA", "."))
df <- read_csv("file.csv", skip = 3)
```
**R example**
```r
df <- haven::read_dta("wages.dta")   # labelled columns; use haven::as_factor()
```

---

### First look at a frame

**Python code**
```python
df.info()         # columns, non-null counts, dtypes (the best first look)
```
**Pytho example**
```python
df.info()
# <class 'pandas.DataFrame'>  RangeIndex: 148 entries
#  #   Column       Non-Null Count  Dtype
#  0   countrycode  148 non-null    object
#  3   dln_tot      148 non-null    float64
#  4   dlny         146 non-null    float64   <- 2 missing
```
**R code**
```r
glimpse(df)       # one line per column: name, type, first values
```
**R example**
```r
glimpse(df)
# Rows: 148  Columns: 8
# $ countrycode <chr> "BRA", "BRA", ...
# $ year        <dbl> 1995, 1996, ...
```

---

### Dimensions, names, types

**Python code**
```python
df.shape            # (rows, cols)
list(df.columns)    # column names
df.dtypes           # column types
```
**Python example**
```python
list(df.columns)
# ['countrycode', 'year', 'regime', 'dln_tot', 'dlny', 'rer', 'cpi', 'openness']
```
**R code**
```r
dim(df)             # rows, cols
names(df)           # column names
sapply(df, class)   # column types
```
**R example**
```r
names(df)
# [1] "countrycode" "year" "regime" "dln_tot" "dlny" "rer" "cpi" "openness"
```

---

### Unique counts and frequency tables

**Python code**
```python
df["countrycode"].nunique()             # number of distinct values
df["regime"].value_counts()             # frequency table
df.value_counts(["countrycode", "regime"])   # cross-tab as counts
```
**Python example**
```python
df["regime"].value_counts()
# float    79
# peg      69
```
**R code**
```r
n_distinct(df$countrycode)              # number of distinct values
count(df, regime)                        # frequency table
count(df, countrycode, regime)           # cross-tab as long counts
```
**R example**
```r
count(df, regime)
# # A tibble: 2 x 2
#   regime     n
#   <chr>  <int>
# 1 float     79
# 2 peg       69
```

---

### Write out

**Python code**
```python
df.to_csv("out.csv", index=False)
df.to_stata("out.dta")
df.to_parquet("out.parquet")
```
**Python example**
```python
df.to_csv("out.csv", index=False)   # index=False keeps the row numbers out
```
**R code**
```r
write_csv(df, "out.csv")
haven::write_dta(df, "out.dta")
saveRDS(df, "out.rds")              # fast R-native round-trip
```
**R example**
```r
write_csv(df, "out.csv")
```
