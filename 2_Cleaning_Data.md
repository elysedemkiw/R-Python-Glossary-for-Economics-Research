# 02 Clean and transform

Simple column operations first, then the within-group moves you use in panel work.
Assumes `df = pd.read_csv("data/sample_panel.csv")` (Python) or the `read_csv`
equivalent (R)

---

### Standardise column names

**Python code**
```python
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
```
**Python example**
```python
df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
list(df.columns)   # all snake_case now
```
**R code**
```r
df <- janitor::clean_names(df)        # snake_case, deduped, syntactically safe
```
**R example**
```r
df <- janitor::clean_names(df)
```

---

### Rename a column / fix types

**Python code**
```python
df = df.rename(columns={"dlny": "gdp_growth"})
df["year"] = df["year"].astype("int64")
df["regime"] = df["regime"].astype("category")
```
**Python example**
```python
df = df.rename(columns={"dlny": "gdp_growth"})
"gdp_growth" in df.columns   # True
```
**R code**
```r
df <- df %>% rename(gdp_growth = dlny)
df <- df %>% mutate(year = as.integer(year),
                    regime = as.factor(regime))
```
**R example**
```r
df <- df %>% rename(gdp_growth = dlny)
```

---

### Trim and standardise strings

**Python code**
```python
df["countrycode"] = df["countrycode"].str.strip().str.upper()
# df["x"].str.contains("peg"), .str.replace("a", "b"), .str.removesuffix(" Occupations")
```
**Python example**
```python
df["countrycode"].str.contains("RA").sum()   # rows whose code contains "RA"
```
**R code**
```r
df <- df %>% mutate(countrycode = str_trim(str_to_upper(countrycode)))
# str_detect(x, "peg"); str_replace(x, "a", "b"); str_remove(x, " Occupations")
```
**R example**
```r
sum(str_detect(df$countrycode, "RA"))
```

---

### Parse dates (when you have them)

**Python code**
```python
df["date"] = pd.to_datetime(df["date"])
df["yr"], df["mo"] = df["date"].dt.year, df["date"].dt.month
```
**Python example**
```python
ts = pd.read_csv("data/sample_timeseries_long.csv")
ts["date"] = pd.to_datetime(ts["date"])
ts["date"].dt.year.head(1)   # 2022
```
**R code**
```r
library(lubridate)
df <- df %>% mutate(date = ymd(date), yr = year(date), mo = month(date))
```
**R example**
```r
ts <- read_csv("data/sample_timeseries_long.csv") %>% mutate(date = ymd(date))
year(ts$date[1])   # 2022
```

---

### Recode / map values

**Python code**
```python
df["countrycode"] = df["countrycode"].replace({"UVK": "XKX"})   # IMF code -> ISO3
```
**Python example**
```python
df["countrycode"] = df["countrycode"].replace({"UVK": "XKX"})
```
**R code**
```r
df <- df %>% mutate(countrycode = recode(countrycode, UVK = "XKX"))
```
**R example**
```r
df <- df %>% mutate(countrycode = recode(countrycode, UVK = "XKX"))
```

---

### Bucket a continuous variable into categories

**Python code**
```python
import numpy as np
df["big"]  = np.where(df["openness"] > 0.6, "open", "closed")
df["tier"] = pd.cut(df["openness"], bins=[-np.inf, 0.4, 0.8, np.inf],
                    labels=["low", "mid", "high"])
```
**Python example**
```python
df["tier"].value_counts()
```
**R code**
```r
df <- df %>% mutate(big = if_else(openness > 0.6, "open", "closed"),
                    tier = case_when(openness < 0.4 ~ "low",
                                     openness < 0.8 ~ "mid",
                                     TRUE           ~ "high"))
```
**R example**
```r
count(df, tier)
```

---

### Filter rows (and winsorise by dropping)

**Python code**
```python
df = df[df["regime"].isin(["peg", "float"]) & (df["year"] <= 2023)]
df = df[df["gdp_growth"].abs() < 0.20]
```
**Python example**
```python
df = df[df["gdp_growth"].abs() < 0.20]
df.shape   # rows with extreme growth removed
```
**R code**
```r
df <- df %>% filter(regime %in% c("peg", "float"), year <= 2023,
                    abs(gdp_growth) < 0.20)
```
**R example**
```r
df <- df %>% filter(abs(gdp_growth) < 0.20)
```

---

### Drop duplicates

**Python code**
```python
df = df.drop_duplicates()                               # exact dup rows
df = df.drop_duplicates(subset=["countrycode", "year"]) # one row per key
```
**Python example**
```python
df.duplicated(["countrycode", "year"]).sum()   # 0 once keys are unique
```
**R code**
```r
df <- df %>% distinct()                                       # exact dup rows
df <- df %>% distinct(countrycode, year, .keep_all = TRUE)    # one row per key
```
**Rexample**
```r
sum(duplicated(df[c("countrycode", "year")]))   # 0
```

---

### Winsorise (clip instead of drop)

**Python code**
```python
def winsorize(s, p=0.01):
    lo, hi = s.quantile(p), s.quantile(1 - p)
    return s.clip(lo, hi)
df["gdp_growth_w"] = winsorize(df["gdp_growth"])
```
**Python example**
```python
df["gdp_growth_w"] = winsorize(df["gdp_growth"])
df["gdp_growth_w"].max() <= df["gdp_growth"].quantile(0.99)   # True
```
**R code**
```r
winsorize <- function(x, p = 0.01) {
  lo <- quantile(x, p, na.rm = TRUE); hi <- quantile(x, 1 - p, na.rm = TRUE)
  pmin(pmax(x, lo), hi)
}
df <- df %>% mutate(gdp_growth_w = winsorize(gdp_growth))
```
**R example**
```r
df <- df %>% mutate(gdp_growth_w = winsorize(gdp_growth))
```

---

### Lag / lead within group

**Python code**
```python
df = df.sort_values(["countrycode", "year"])
g = df.groupby("countrycode", group_keys=False)
df["gdp_lag1"]  = g["gdp_growth"].shift(1)
df["gdp_lead1"] = g["gdp_growth"].shift(-1)
```
**Python example**
```python
df.loc[df.countrycode == "BRA", ["year", "gdp_growth", "gdp_lag1"]].head(2)
#    year  gdp_growth  gdp_lag1
#    1995   -0.039792       NaN     <- first year has no lag
#    1996    0.042483 -0.039792
```
**R code**
```r
df <- df %>% arrange(countrycode, year) %>% group_by(countrycode) %>%
  mutate(gdp_lag1 = lag(gdp_growth, 1),
         gdp_lead1 = lead(gdp_growth, 1)) %>% ungroup()
```
**R example**
```r
df %>% filter(countrycode == "BRA") %>% select(year, gdp_growth, gdp_lag1) %>% head(2)
```

---

### Demean within group

**Python code**
```python
g = df.groupby("countrycode", group_keys=False)
df["gdp_demean"] = g["gdp_growth"].transform(lambda x: x - x.mean())
df["rer_norm"]   = g["rer"].transform(lambda x: x / x.iloc[0])   # index to first obs
```
**Python example**
```python
df.groupby("countrycode")["gdp_demean"].mean().round(10)   # 0.0 for every country
```
**R code**
```r
df <- df %>% group_by(countrycode) %>%
  mutate(gdp_demean = gdp_growth - mean(gdp_growth, na.rm = TRUE),
         rer_norm   = rer / first(rer)) %>% ungroup()
```
**R example**
```r
df %>% group_by(countrycode) %>% summarise(m = mean(gdp_demean, na.rm = TRUE))
```

---

### Interpolate gaps within group

**Python code**
```python
g = df.groupby("countrycode", group_keys=False)
df["rer_filled"] = (g["rer"].transform(lambda x: x.interpolate(limit_direction="both"))
                            .fillna(g["rer"].transform("mean")))
```
**Python example**
```python
df["rer"].isna().sum(), df["rer_filled"].isna().sum()   # (3, 0)
```
**R code**
```r
library(zoo)
df <- df %>% group_by(countrycode) %>%
  mutate(rer_filled = na.approx(rer, na.rm = FALSE),
         rer_filled = if_else(is.na(rer_filled), mean(rer, na.rm = TRUE), rer_filled)) %>%
  ungroup()
```
**R example**
```r
sum(is.na(df$rer)); sum(is.na(df$rer_filled))   # 3 then 0
```
