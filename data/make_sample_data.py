"""
Generate small, runnable example datasets for the glossary.

Writes two files into the same folder:
  sample_panel.csv            an unbalanced country-year panel with deliberate NA gaps
  sample_timeseries_long.csv  a few monthly series in long (tidy) format

Run once:  python make_sample_data.py
Both the R and Python examples read these files, so the snippets are runnable
in either language without changing anything.
"""

from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).parent
rng = np.random.default_rng(42)


def make_panel() -> pd.DataFrame:
    """Country-year panel, intentionally unbalanced, with missing-value gaps."""
    countries = ["USA", "DEU", "FRA", "BRA", "IND", "UKR"]
    regime = {"USA": "float", "DEU": "float", "FRA": "float",
              "BRA": "peg", "IND": "peg", "UKR": "peg"}
    rows = []
    for c in countries:
        # different countries observed over different (ragged) year ranges
        start = rng.integers(1995, 2001)
        end = rng.integers(2018, 2024)
        for y in range(start, end + 1):
            rows.append({
                "countrycode": c,
                "year": int(y),
                "regime": regime[c],
                "dln_tot": rng.normal(0, 0.05),      # terms-of-trade growth
                "dlny": rng.normal(0.02, 0.03),      # real GDP growth
                "rer": 100 * np.exp(rng.normal(0, 0.1)),  # real exchange rate level
                "cpi": rng.normal(0.03, 0.02),       # inflation
                "openness": np.clip(rng.normal(0.6, 0.2), 0.1, 1.5),
            })
    df = pd.DataFrame(rows)

    # punch holes so missing-value detection has something to find:
    # a single isolated gap and one consecutive run
    df.loc[(df.countrycode == "BRA") & (df.year == 2005), "dlny"] = np.nan
    df.loc[(df.countrycode == "IND") & (df.year.between(2010, 2012)), "rer"] = np.nan
    df.loc[(df.countrycode == "UKR") & (df.year == 2014), ["dlny", "cpi"]] = np.nan
    # drop a couple of rows entirely so the time index itself has holes
    df = df[~((df.countrycode == "FRA") & (df.year.isin([2008, 2009])))]
    return df.sort_values(["countrycode", "year"]).reset_index(drop=True)


def make_timeseries_long() -> pd.DataFrame:
    """Monthly long-format series: columns [date, series, value]."""
    dates = pd.date_range("2022-01-01", periods=24, freq="MS")
    series = {"gdp_index": 100, "cpi_index": 100, "unemployment": 5.0}
    rows = []
    for name, level in series.items():
        walk = level + np.cumsum(rng.normal(0, 0.6, len(dates)))
        for d, v in zip(dates, walk):
            rows.append({"date": d.date().isoformat(), "series": name, "value": round(float(v), 3)})
    df = pd.DataFrame(rows)
    df.loc[(df.series == "unemployment") & (df.date == "2022-05-01"), "value"] = np.nan
    return df


if __name__ == "__main__":
    make_panel().to_csv(OUT / "sample_panel.csv", index=False)
    make_timeseries_long().to_csv(OUT / "sample_timeseries_long.csv", index=False)
    print("Wrote sample_panel.csv and sample_timeseries_long.csv")
