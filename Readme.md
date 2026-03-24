<div align="center">

# synthdid

### Synthetic Difference-in-Differences Estimation for Python

[![PyPI](https://img.shields.io/pypi/v/synthdid?color=blue&label=PyPI)](https://pypi.org/project/synthdid/)
[![Downloads](https://static.pepy.tech/badge/synthdid/month)](https://pepy.tech/project/synthdid)
[![Last Commit](https://img.shields.io/github/last-commit/d2cml-ai/synthdid.py)](https://github.com/d2cml-ai/synthdid.py)
[![Stars](https://img.shields.io/github/stars/d2cml-ai/synthdid.py?style=flat)](https://github.com/d2cml-ai/synthdid.py/stargazers)
[![Issues](https://img.shields.io/github/issues/d2cml-ai/synthdid.py)](https://github.com/d2cml-ai/synthdid.py/issues)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/d2cml-ai/synthdid.py/blob/main/LICENSE)

A Python implementation of the **Synthetic Difference-in-Differences (SDID)** estimator —
a modern causal inference method for panel data that combines the strengths of Synthetic Control and Difference-in-Differences.

[Installation](#installation) • [Usage](#usage) • [Examples](#examples) • [Related Work](#related-implementations)

</div>

---

## Overview

`synthdid` supports:

- **Block designs** — single adoption period (classic SDID, SC, and DiD)
- **Staggered adoption** — multiple treatment cohorts across time
- **Covariate adjustment** — via `"optimized"` or `"projected"` methods
- **Inference** — bootstrap, placebo, and jackknife standard errors
- **Visualization** — weighted outcome trends and weight distribution plots

The package draws on implementations in [R](https://github.com/synth-inference/synthdid), [Julia](https://github.com/d2cml-ai/Synthdid.jl), and [Stata](https://github.com/Daniel-Pailanir/sdid).

---

## Installation

```bash
pip install synthdid
```

---

## Usage

### Class: `Synthdid`

```python
from synthdid.synthdid import Synthdid

Synthdid(data, unit, time, treatment, outcome, covariates=None)
```

**Constructor parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `data` | `DataFrame` | Panel dataset in long format |
| `unit` | `str` | Column name for unit identifier |
| `time` | `str` | Column name for time variable |
| `treatment` | `str` | Column name for treatment dummy (`1` = treated, `0` = control) |
| `outcome` | `str` | Column name for outcome variable |
| `covariates` | `list[str]` | *(optional)* List of covariate column names |

**Methods:**

| Method | Returns | Description |
|--------|---------|-------------|
| `.fit(cov_method=None, did=False, synth=False)` | `self` | Estimates ATT, unit weights, and time weights |
| `.vcov(method, n_reps=50)` | `self` | Computes standard errors (`"bootstrap"`, `"placebo"`, `"jackknife"`) |
| `.summary()` | `self` | Computes ATT summary table |
| `.plot_outcomes()` | `Figure` | Plots weighted outcome trends |
| `.plot_weights()` | `Figure` | Plots unit and time weight distributions |

> **Note:** `.fit()`, `.vcov()`, and `.summary()` return `self` and can be chained.

---

## Examples

```python
from synthdid.get_data import california_prop99, quota
from synthdid.synthdid import Synthdid
from matplotlib import pyplot as plt
```

---

### Block Design

> **Dataset:** California Proposition 99 — effect of a tobacco control program on cigarette consumption.

#### Synthetic DiD (SDID)

```python
df = california_prop99()

california_sdid = (
    Synthdid(df, "State", "Year", "treated", "PacksPerCapita")
    .fit()
    .vcov()
    .summary()
)
california_sdid.summary2
```

| | ATT | Std. Err. | t | P > \|t\| |
|--|-----------|-----------|-----------|-----------|
| 0 | -15.60383 | 10.789924 | -1.446148 | 0.148136 |

```python
plt.show(california_sdid.plot_outcomes())
plt.show(california_sdid.plot_weights())
```

![Estimated Trends SDID Prop. 99](readme/california_sdid_trends.png)
![Estimated Weights SDID Prop. 99](readme/california_sdid_weights.png)

#### Synthetic Control (SC)

```python
california_sc = (
    Synthdid(df, "State", "Year", "treated", "PacksPerCapita")
    .fit(synth=True)
)
plt.show(california_sc.plot_outcomes())
plt.show(california_sc.plot_weights())
```

![Estimated Trends SC Prop. 99](readme/california_sc_trends.png)
![Estimated Weights SC Prop. 99](readme/california_sc_weights.png)

#### Difference-in-Differences (DiD)

```python
california_did = (
    Synthdid(df, "State", "Year", "treated", "PacksPerCapita")
    .fit(did=True)
)
plt.show(california_did.plot_outcomes())
plt.show(california_did.plot_weights())
```

![Estimated Trends DiD Prop. 99](readme/california_did_trends.png)
![Estimated Weights DiD Prop. 99](readme/california_did_weights.png)

---

### Staggered Adoption Design

> **Dataset:** Gender quota laws — effect on women's parliamentary representation across multiple countries and adoption years.

```python
df = quota()

fit_model = (
    Synthdid(df, "country", "year", "quota", "womparl")
    .fit()
    .vcov()
    .summary()
)
fit_model.summary2
```

| | ATT | Std. Err. | t | P > \|t\| |
|--|--------|-----------|-----------|-----------|
| 0 | 8.0341 | 1.684382 | 4.769762 | 0.000002 |

**ATT decomposed by treatment cohort:**

```python
fit_model.att_info
```

| | time | att\_time | att\_wt | N0 | T0 | N1 | T1 |
|--|--------|-----------|---------|-----|----|----|-----|
| 0 | 2000.0 | 8.388868 | 0.170213 | 110 | 10 | 1 | 16 |
| 1 | 2002.0 | 6.967746 | 0.297872 | 110 | 12 | 2 | 14 |
| 2 | 2003.0 | 13.952256 | 0.276596 | 110 | 13 | 2 | 13 |
| 3 | 2005.0 | -3.450543 | 0.117021 | 110 | 15 | 1 | 11 |
| 4 | 2010.0 | 2.749035 | 0.063830 | 110 | 20 | 1 | 6 |
| 5 | 2012.0 | 21.762715 | 0.042553 | 110 | 22 | 1 | 4 |
| 6 | 2013.0 | -0.820324 | 0.031915 | 110 | 23 | 1 | 3 |

**With covariates — optimized method:**

```python
fit_covar_model = (
    Synthdid(
        df[~df.lngdp.isnull()], "country", "year", "quota", "womparl",
        covariates=["lngdp"]
    )
    .fit()
    .vcov(method="bootstrap")
    .summary()
)
fit_covar_model.summary2
```

| | ATT | Std. Err. | t | P > \|t\| |
|--|---------|-----------|-----------|-----------|
| 0 | 8.04901 | 3.395295 | 2.370636 | 0.017757 |

**With covariates — projected method:**

```python
fit_covar_model_projected = (
    Synthdid(
        df[~df.lngdp.isnull()], "country", "year", "quota", "womparl",
        covariates=["lngdp"]
    )
    .fit(cov_method="projected")
    .vcov(method="bootstrap")
    .summary()
)
fit_covar_model_projected.summary2
```

| | ATT | Std. Err. | t | P > \|t\| |
|--|---------|-----------|-----------|-----------|
| 0 | 8.05903 | 3.428897 | 2.350327 | 0.018757 |

---

### Inference Options

Three variance estimation strategies are available and can be swapped without re-fitting:

| Method | Description |
|--------|-------------|
| `"bootstrap"` | Resamples units with replacement |
| `"placebo"` | Assigns placebo treatments to control units |
| `"jackknife"` | Leave-one-unit-out resampling |

```python
countries_for_excluding = ["Algeria", "Kenya", "Samoa", "Swaziland", "Tanzania"]

se_examples = (
    Synthdid(
        df[~df.country.isin(countries_for_excluding)],
        "country", "year", "quota", "womparl"
    )
    .fit()
    .vcov(method="bootstrap")
    .summary()
)
```

| Method | ATT | Std. Err. | t | P > \|t\| |
|--------|---------|-----------|-----------|-----------|
| Bootstrap | 10.33066 | 5.404923 | 1.911343 | 0.055961 |
| Placebo | 10.33066 | 2.244618 | 4.602413 | 0.000004 |
| Jackknife | 10.33066 | 6.04213 | 1.709771 | 0.087308 |

---

## Related Implementations

| Language | Package | Authors |
|----------|---------|---------|
| R | [synth-inference/synthdid](https://github.com/synth-inference/synthdid) | Arkhangelsky et al. |
| Julia | [d2cml-ai/Synthdid.jl](https://github.com/d2cml-ai/Synthdid.jl) | D2CML Team |
| Stata | [Daniel-Pailanir/sdid](https://github.com/Daniel-Pailanir/sdid) | Daniel Pailanir |

---

<div align="center">

Developed by the [D2CML Team](https://github.com/d2cml-ai) · MIT License

</div>
