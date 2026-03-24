# synthdid: Synthetic Difference-in-Differences Estimation

[![PyPI](https://img.shields.io/pypi/v/synthdid)](https://pypi.org/project/synthdid/)
[![Downloads](https://static.pepy.tech/badge/synthdid/month)](https://pepy.tech/project/synthdid)
[![Last Commit](https://img.shields.io/github/last-commit/d2cml-ai/synthdid.py)](https://github.com/d2cml-ai/synthdid.py)
[![Stars](https://img.shields.io/github/stars/d2cml-ai/synthdid.py)](https://github.com/d2cml-ai/synthdid.py/stargazers)
[![Issues](https://img.shields.io/github/issues/d2cml-ai/synthdid.py)](https://github.com/d2cml-ai/synthdid.py/issues)
[![License](https://img.shields.io/github/license/d2cml-ai/synthdid.py)](https://github.com/d2cml-ai/synthdid.py/blob/main/LICENSE)

A Python implementation of the **Synthetic Difference-in-Differences (SDID)** estimator, providing a comprehensive toolkit for causal inference in panel data settings — including inference methods and visualization utilities.

The package draws on implementations in [R](https://github.com/synth-inference/synthdid), [Julia](https://github.com/d2cml-ai/Synthdid.jl), and [Stata](https://github.com/Daniel-Pailanir/sdid), and extends them to support staggered adoption designs, covariate adjustment, and multiple inference strategies.

---

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)
  - [Block Design](#block-design)
  - [Staggered Adoption Design](#staggered-adoption-design)
  - [Inference Options](#inference-options)

---

## Installation

```bash
pip install synthdid
```

---

## Usage

### Class: `Synthdid`

```python
Synthdid(data, unit, time, treatment, outcome, covariates=None)
```

| Parameter | Description |
|-----------|-------------|
| `outcome` | Outcome variable *(numeric)* |
| `unit` | Unit identifier *(numeric or string)* |
| `time` | Time variable *(numeric)* |
| `treatment` | Treatment dummy — `1` if treated, `0` otherwise *(numeric)* |
| `covariates` | Optional list of covariate column names |

### Methods

| Method | Description |
|--------|-------------|
| `.fit(cov_method=None, did=False, synth=False)` | Estimates the ATT, unit weights, and time weights. Supports covariate adjustment via `"optimized"` or `"projected"` methods. |
| `.vcov(method, n_reps=50)` | Estimates the standard error. Methods: `"placebo"`, `"bootstrap"`, `"jackknife"`. |
| `.summary()` | Returns a summary table with ATT, standard error, t-statistic, and p-value. |
| `.plot_outcomes()` | Plots weighted outcome trends for treated and synthetic control units. |
| `.plot_weights()` | Plots the estimated unit and time weights. |

---

## Examples

```python
from synthdid.get_data import california_prop99, quota
from synthdid.synthdid import Synthdid
from matplotlib import pyplot as plt
import numpy as np
```

### Block Design

Using California Proposition 99 as a classic SDID application:

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
|-|-----|-----------|---|-----------|
| 0 | -15.60383 | 10.789924 | -1.446148 | 0.148136 |

```python
plt.show(california_sdid.plot_outcomes())
plt.show(california_sdid.plot_weights())
```

![Estimated Trends SDID Prop. 99](readme/california_sdid_trends.png)

![Estimated Weights SDID Prop. 99](readme/california_sdid_weights.png)

**Synthetic Control (SC):**

```python
california_sc = Synthdid(df, "State", "Year", "treated", "PacksPerCapita").fit(synth=True)
plt.show(california_sc.plot_outcomes())
plt.show(california_sc.plot_weights())
```

![Estimated Trends SC Prop. 99](readme/california_sc_trends.png)

![Estimated Weights SC Prop. 99](readme/california_sc_weights.png)

**Difference-in-Differences (DiD):**

```python
california_did = Synthdid(df, "State", "Year", "treated", "PacksPerCapita").fit(did=True)
plt.show(california_did.plot_outcomes())
plt.show(california_did.plot_weights())
```

![Estimated Trends DiD Prop. 99](readme/california_did_trends.png)

![Estimated Weights DiD Prop. 99](readme/california_did_weights.png)

---

### Staggered Adoption Design

Using the quota dataset with multiple treatment cohorts:

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
|-|-----|-----------|---|-----------|
| 0 | 8.0341 | 1.684382 | 4.769762 | 0.000002 |

ATT by cohort:

```python
fit_model.att_info
```

| | time | att\_time | att\_wt | N0 | T0 | N1 | T1 |
|-|------|-----------|---------|----|----|----|----|
| 0 | 2000.0 | 8.388868 | 0.170213 | 110 | 10 | 1 | 16 |
| 1 | 2002.0 | 6.967746 | 0.297872 | 110 | 12 | 2 | 14 |
| 2 | 2003.0 | 13.952256 | 0.276596 | 110 | 13 | 2 | 13 |
| 3 | 2005.0 | -3.450543 | 0.117021 | 110 | 15 | 1 | 11 |
| 4 | 2010.0 | 2.749035 | 0.063830 | 110 | 20 | 1 | 6 |
| 5 | 2012.0 | 21.762715 | 0.042553 | 110 | 22 | 1 | 4 |
| 6 | 2013.0 | -0.820324 | 0.031915 | 110 | 23 | 1 | 3 |

**With covariates (optimized method):**

```python
fit_covar_model = (
    Synthdid(df[~df.lngdp.isnull()], "country", "year", "quota", "womparl", covariates=["lngdp"])
    .fit()
    .vcov(method="bootstrap")
    .summary()
)
fit_covar_model.summary2
```

| | ATT | Std. Err. | t | P > \|t\| |
|-|-----|-----------|---|-----------|
| 0 | 8.04901 | 3.395295 | 2.370636 | 0.017757 |

**With covariates (projected method):**

```python
fit_covar_model_projected = (
    Synthdid(df[~df.lngdp.isnull()], "country", "year", "quota", "womparl", covariates=["lngdp"])
    .fit(cov_method="projected")
    .vcov(method="bootstrap")
    .summary()
)
fit_covar_model_projected.summary2
```

| | ATT | Std. Err. | t | P > \|t\| |
|-|-----|-----------|---|-----------|
| 0 | 8.05903 | 3.428897 | 2.350327 | 0.018757 |

---

### Inference Options

Three standard error methods are available: `"bootstrap"`, `"placebo"`, and `"jackknife"`.

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
se_examples.summary2
```

| | ATT | Std. Err. | t | P > \|t\| |
|-|-----|-----------|---|-----------|
| 0 | 10.33066 | 5.404923 | 1.911343 | 0.055961 |

```python
se_examples.vcov(method="placebo").summary()
se_examples.summary2
```

| | ATT | Std. Err. | t | P > \|t\| |
|-|-----|-----------|---|-----------|
| 0 | 10.33066 | 2.244618 | 4.602413 | 0.000004 |

```python
se_examples.vcov(method="jackknife").summary()
se_examples.summary2
```

| | ATT | Std. Err. | t | P > \|t\| |
|-|-----|-----------|---|-----------|
| 0 | 10.33066 | 6.04213 | 1.709771 | 0.087308 |

---

## Related Implementations

| Language | Repository |
|----------|------------|
| R | [synth-inference/synthdid](https://github.com/synth-inference/synthdid) |
| Julia | [d2cml-ai/Synthdid.jl](https://github.com/d2cml-ai/Synthdid.jl) |
| Stata | [Daniel-Pailanir/sdid](https://github.com/Daniel-Pailanir/sdid) |
