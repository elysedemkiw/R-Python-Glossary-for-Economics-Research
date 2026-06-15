# 07 — Regression results into tables

Tidy one model, put several side by side and export them, add robust/clustered
standard errors, and run panel fixed effects. Defaults are the low-friction ones:
`summary_col` in Python, `modelsummary` in R.

---

### Fit one model and tidy it

**Python — code**
```python
import statsmodels.formula.api as smf
m1 = smf.ols("dlny ~ openness + dln_tot", data=df).fit()

def tidy(res):
    out = pd.DataFrame({"term": res.params.index, "estimate": res.params.values,
                        "std_error": res.bse.values, "statistic": res.tvalues.values,
                        "p_value": res.pvalues.values})
    ci = res.conf_int(); out["conf_low"], out["conf_high"] = ci[0].values, ci[1].values
    return out
```
**Python — example**
```python
tidy(m1).round(3)
#         term  estimate  std_error  statistic  p_value
#    Intercept     0.025      0.008      3.157    0.002
#     openness    -0.011      0.012     -0.894    0.373
#      dln_tot     0.030      0.053      0.563    0.574
#   (N = 146; rows with missing dlny are dropped)
```
**R — code**
```r
library(broom)
m1 <- lm(dlny ~ openness + dln_tot, data = df)
tidy(m1, conf.int = TRUE)     # term, estimate, std.error, statistic, p.value, conf.*
glance(m1)                    # r.squared, nobs, AIC, ...
```
**R — example**
```r
tidy(m1, conf.int = TRUE)
# # A tibble: 3 x 7
```

---

### Several models side by side

**Python — code**
```python
from statsmodels.iolib.summary2 import summary_col
m2 = smf.ols("dlny ~ openness + dln_tot + cpi", data=df).fit()
m3 = smf.ols("dlny ~ openness + dln_tot + cpi + C(regime)", data=df).fit()
table = summary_col([m1, m2, m3], model_names=["Base", "Plus CPI", "Plus regime"],
                    stars=True, float_format="%.3f",
                    info_dict={"N": lambda x: f"{int(x.nobs)}",
                               "R2": lambda x: f"{x.rsquared:.3f}"})
print(table)
```
**Python — example**
```python
print(table)
# ==============================================
#                    Base   Plus CPI Plus regime
# Intercept        0.025*** 0.022*** 0.023***
# openness        -0.011   -0.013   -0.013
# dln_tot          0.030    0.031    0.029
# cpi                       0.140    0.138
# N                146      146      146
# R2               0.007    0.014    0.015
```
**R — code**
```r
library(modelsummary)
m2 <- lm(dlny ~ openness + dln_tot + cpi, data = df)
m3 <- lm(dlny ~ openness + dln_tot + cpi + regime, data = df)
msummary(list("Base" = m1, "Plus CPI" = m2, "Plus regime" = m3),
         stars = c('*' = .1, '**' = .05, '***' = .01),
         gof_omit = "AIC|BIC|Log.Lik", output = "markdown")
```
**R — example**
```r
# three-column table printed as markdown, stars and N / R2 rows
```

---

### Export the table to LaTeX / Word / HTML

**Python — code**
```python
open("table.tex", "w").write(table.as_latex())
open("table.html", "w").write(table.as_html())
```
**Python — example**
```python
# table.tex now holds a tabular you can \input{} into a paper
```
**R — code**
```r
msummary(list(m1, m2, m3), output = "table.tex")    # also .docx, .html, .md
```
**R — example**
```r
# writes table.tex (or .docx for a Word manuscript)
```

---

### Robust / clustered standard errors

**Python — code**
```python
m_rob = smf.ols("dlny ~ openness + dln_tot", data=df).fit(cov_type="HC1")     # robust
m_cl  = smf.ols("dlny ~ openness + dln_tot", data=df).fit(
            cov_type="cluster", cov_kwds={"groups": df["countrycode"]})        # clustered
```
**Python — example**
```python
m_cl.bse.round(3)   # standard errors now clustered by country
```
**R — code**
```r
msummary(list(m1, m2), vcov = "robust")          # robust SEs in the table
msummary(list(m1, m2), vcov = ~ countrycode)     # clustered by country
```
**R — example**
```r
msummary(list(m1), vcov = ~ countrycode)
```

---

### Panel fixed effects

**Python — code**
```python
# pip install linearmodels
from linearmodels.panel import PanelOLS
p = df.dropna(subset=["dlny", "openness", "dln_tot"]).set_index(["countrycode", "year"])
fe = PanelOLS.from_formula(
        "dlny ~ openness + dln_tot + EntityEffects + TimeEffects", data=p
     ).fit(cov_type="clustered", cluster_entity=True)   # two-way FE, clustered SE
print(fe.summary)
```
**Python — example**
```python
print(fe.params)   # within-country, within-year slopes
```
**R — code**
```r
library(fixest)
fe1 <- feols(dlny ~ openness + dln_tot | countrycode,        data = df)  # country FE
fe2 <- feols(dlny ~ openness + dln_tot | countrycode + year, data = df)  # two-way FE
etable(fe1, fe2)                  # console table with FE rows; SEs clustered by 1st FE
```
**R — example**
```r
etable(fe1, fe2)
# feols objects also drop straight into msummary(list(fe1, fe2), output = "fe.tex")
```
