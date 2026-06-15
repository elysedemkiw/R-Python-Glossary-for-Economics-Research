# 06 — Plots

A gallery of the figures that show up in economics papers. Python uses
matplotlib; R uses ggplot2. Save with `fig.savefig("f.png", dpi=150,
bbox_inches="tight")` or `ggsave("f.png", width = 7, height = 5, dpi = 150)`.

Assumes `df` is the panel and `ts` the long time series (with `date` parsed).

---

### Line: one or many time series

**Python — code**
```python
import matplotlib.pyplot as plt
fig, ax = plt.subplots()
for name, sub in ts.groupby("series"):
    ax.plot(sub["date"], sub["value"], label=name, lw=1.5)
ax.set(ylabel="Index", title="Time series"); ax.legend()
```
**Python — example**
```python
# three lines (gdp_index, cpi_index, unemployment) over 24 months
```
**R — code**
```r
ggplot(ts, aes(date, value, colour = series)) +
  geom_line(linewidth = 0.8) +
  labs(x = NULL, y = "Index", colour = NULL, title = "Time series")
```
**R — example**
```r
# same three-line chart
```

---

### Horizontal ranked bar (top-N)

**Python — code**
```python
top = df.groupby("countrycode")["dlny"].mean().sort_values().tail(6)
fig, ax = plt.subplots()
ax.barh(top.index, top.values, color="steelblue")
ax.xaxis.set_major_formatter(lambda x, _: f"{x*100:.1f}%")
ax.set(xlabel="Mean GDP growth", title="Top countries")
```
**Python — example**
```python
# six horizontal bars, longest on top
```
**R — code**
```r
df %>% group_by(countrycode) %>%
  summarise(mean_growth = mean(dlny, na.rm = TRUE), .groups = "drop") %>%
  slice_max(mean_growth, n = 6) %>%
  ggplot(aes(mean_growth, fct_reorder(countrycode, mean_growth))) +
  geom_col(fill = "steelblue") +
  scale_x_continuous(labels = scales::label_percent(accuracy = 0.1)) +
  labs(x = "Mean GDP growth", y = NULL)
```
**R — example**
```r
# same ranked bars
```

---

### Grouped bar

**Python — code**
```python
import numpy as np
piv = df.pivot_table(index="countrycode", columns="regime", values="dlny", aggfunc="mean")
fig, ax = plt.subplots(); x = np.arange(len(piv)); w = 0.4
for i, col in enumerate(piv.columns):
    ax.bar(x + (i - 0.5) * w, piv[col], width=w, label=col)
ax.set_xticks(x); ax.set_xticklabels(piv.index); ax.legend()
```
**Python — example**
```python
# bars dodged by regime within each country
```
**R — code**
```r
df %>% group_by(regime, countrycode) %>%
  summarise(m = mean(dlny, na.rm = TRUE), .groups = "drop") %>%
  ggplot(aes(countrycode, m, fill = regime)) +
  geom_col(position = position_dodge())
```
**R — example**
```r
# same dodged bars
```

---

### Scatter with OLS fit and annotated slope/R²

**Python — code**
```python
import statsmodels.api as sm
d = df.dropna(subset=["openness", "dlny"])
res = sm.OLS(d["dlny"], sm.add_constant(d["openness"])).fit()
xs = np.linspace(d["openness"].min(), d["openness"].max(), 100)
fig, ax = plt.subplots()
ax.scatter(d["openness"], d["dlny"], alpha=0.5)
ax.plot(xs, res.params.iloc[0] + res.params.iloc[1] * xs, "--", color="grey")
ax.text(0.05, 0.95, rf"$\beta={res.params.iloc[1]:.3f},\ R^2={res.rsquared:.3f}$",
        transform=ax.transAxes, va="top",
        bbox=dict(boxstyle="round", fc="white", alpha=0.8))
```
**Python — example**
```python
# scatter + dashed fit line + stats box (mirrors the AEI scatter style)
```
**R — code**
```r
fit <- lm(dlny ~ openness, data = df)
lab <- sprintf("beta = %.3f,  R^2 = %.3f", coef(fit)[2], summary(fit)$r.squared)
ggplot(df, aes(openness, dlny)) +
  geom_point(alpha = 0.5) +
  geom_smooth(method = "lm", se = TRUE, linetype = "dashed", colour = "grey40") +
  annotate("label", x = -Inf, y = Inf, hjust = -0.05, vjust = 1.2, label = lab)
```
**R — example**
```r
# same scatter + fit + label
```

---

### Faceted small multiples (one panel per unit)

**Python — code**
```python
units = df["countrycode"].unique()
fig, axes = plt.subplots(2, 3, figsize=(12, 6))
for ax, u in zip(axes.ravel(), units):
    sub = df[df["countrycode"] == u]
    ax.plot(sub["year"], sub["dlny"]); ax.axhline(0, ls="--", color="grey")
    ax.set_title(u)
fig.tight_layout()
```
**Python — example**
```python
# 2x3 grid, one GDP-growth path per country
```
**R — code**
```r
ggplot(df, aes(year, dlny)) +
  geom_line() + geom_hline(yintercept = 0, linetype = "dashed", colour = "grey50") +
  facet_wrap(~ countrycode, scales = "free_y")
```
**R — example**
```r
# same faceted grid
```

---

### Distribution: histogram + density

**Python — code**
```python
from scipy import stats
vals = df["dlny"].dropna()
fig, ax = plt.subplots()
ax.hist(vals, bins=30, density=True, color="0.8", edgecolor="white")
xs = np.linspace(vals.min(), vals.max(), 200)
ax.plot(xs, stats.gaussian_kde(vals)(xs), lw=1.5)
ax.axvline(vals.mean(), ls="--", color="black")
```
**Python — example**
```python
# histogram with overlaid density and a mean line
```
**R — code**
```r
ggplot(df, aes(dlny)) +
  geom_histogram(aes(y = after_stat(density)), bins = 30, fill = "grey80", colour = "white") +
  geom_density(linewidth = 0.8) +
  geom_vline(aes(xintercept = mean(dlny, na.rm = TRUE)), linetype = "dashed")
```
**R — example**
```r
# same histogram + density
```

---

### Dumbbell / lollipop: two values per category

**Python — code**
```python
cmp = (df.groupby("countrycode").agg(a=("openness", "mean"), b=("dlny", "mean"))
         .sort_values("a"))
cmp["b"] = cmp["b"] + 0.5
fig, ax = plt.subplots(); y = np.arange(len(cmp))
ax.hlines(y, cmp["a"], cmp["b"], color="0.7")
ax.scatter(cmp["a"], y, color="steelblue", s=60, label="A")
ax.scatter(cmp["b"], y, color="tomato", s=60, label="B")
ax.set_yticks(y); ax.set_yticklabels(cmp.index); ax.legend()
```
**Python — example**
```python
# two dots per country joined by a line (like the AEI usage-vs-workforce chart)
```
**R — code**
```r
cmp <- df %>% group_by(countrycode) %>%
  summarise(a = mean(openness, na.rm = TRUE), b = mean(dlny, na.rm = TRUE) + 0.5,
            .groups = "drop")
ggplot(cmp, aes(y = fct_reorder(countrycode, a))) +
  geom_segment(aes(x = a, xend = b, yend = countrycode), colour = "grey70") +
  geom_point(aes(x = a), colour = "steelblue", size = 3) +
  geom_point(aes(x = b), colour = "tomato", size = 3)
```
**R — example**
```r
# same dumbbell
```

---

### Coefficient plot (estimates with CI)

**Python — code**
```python
d = df.dropna(subset=["dlny", "openness", "dln_tot", "cpi"])
res = sm.OLS(d["dlny"], sm.add_constant(d[["openness", "dln_tot", "cpi"]])).fit()
coefs = res.params.drop("const"); ci = res.conf_int().drop("const")
fig, ax = plt.subplots(); yy = np.arange(len(coefs))
ax.errorbar(coefs.values, yy,
            xerr=[coefs.values - ci[0].values, ci[1].values - coefs.values],
            fmt="o", capsize=3)
ax.axvline(0, ls="--", color="grey")
ax.set_yticks(yy); ax.set_yticklabels(coefs.index)
```
**Python — example**
```python
# one point + 95% CI bar per coefficient, vertical line at zero
```
**R — code**
```r
library(broom)
lm(dlny ~ openness + dln_tot + cpi, data = df) %>%
  tidy(conf.int = TRUE) %>% filter(term != "(Intercept)") %>%
  ggplot(aes(estimate, fct_rev(term))) +
  geom_vline(xintercept = 0, linetype = "dashed", colour = "grey50") +
  geom_pointrange(aes(xmin = conf.low, xmax = conf.high))
```
**R — example**
```r
# same coefficient plot
```
