# synthdid: Synthetic Difference-in-Differences Estimation

[![PyPI](https://img.shields.io/pypi/v/synthdid?color=blue&label=PyPI)](https://pypi.org/project/synthdid/) [![Downloads](https://static.pepy.tech/badge/synthdid/month)](https://pepy.tech/project/synthdid) [![Last Commit](https://img.shields.io/github/last-commit/d2cml-ai/synthdid.py)](https://github.com/d2cml-ai/synthdid.py) [![Stars](https://img.shields.io/github/stars/d2cml-ai/synthdid.py?style=flat)](https://github.com/d2cml-ai/synthdid.py/stargazers) [![Issues](https://img.shields.io/github/issues/d2cml-ai/synthdid.py)](https://github.com/d2cml-ai/synthdid.py/issues) [![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/d2cml-ai/synthdid.py/blob/main/LICENSE)

The **synthdid** package implements the Synthetic Difference-in-Differences (SDID) estimator for causal inference in panel data settings. It provides tools for estimating average treatment effects, computing standard errors, and visualizing results. The package supports:

- **Block designs** — a single treatment adoption period, with support for SDID, Synthetic Control (SC), and standard Difference-in-Differences (DiD) estimators
- **Staggered adoption designs** — units are treated at different points in time, with cohort-level ATT decomposition
- **Covariate adjustment** — via `"optimized"` or `"projected"` methods
- **Multiple inference strategies** — bootstrap, placebo, and jackknife standard errors
- **Visualization** — weighted outcome trend plots and weight distribution plots

The SDID estimator reweights and differentiates the data to remove unit-level and time-level fixed effects simultaneously, combining the strengths of Synthetic Control and DiD into a single estimator that is robust to heterogeneous treatment effects.

## Getting Started

The **synthdid** package implements the framework put forward in:

- [Arkhangelsky, Dmitry, Susan Athey, David A. Hirshberg, Guido W. Imbens, and Stefan Wager. "Synthetic Difference-in-Differences." *American Economic Review*, Vol. 111, No. 12, pp. 4088–4118, 2021.](https://doi.org/10.1257/aer.20190159)

For staggered adoption, the implementation follows the approach described in:

- [Clarke, Damian, Daniel Pailanir, Susan Athey, and Stefan Wager. "Synthetic Difference in Differences Estimation." *The Stata Journal*, 2023.](https://doi.org/10.1177/1536867X231196345)

This project draws on implementations in [R](https://github.com/synth-inference/synthdid), [Julia](https://github.com/d2cml-ai/Synthdid.jl), and [Stata](https://github.com/Daniel-Pailanir/sdid).

## Installation

You can install **synthdid** from PyPI with:

```bash
pip install synthdid
```

or directly from GitHub:

```bash
pip install git+https://github.com/d2cml-ai/synthdid.py
```

## Basic Example

### Block Design

The following example estimates the effect of California's Proposition 99 — a comprehensive tobacco control program enacted in 1989 — on cigarette consumption. This is the canonical application in Arkhangelsky et al. (2021).

```python
from synthdid.get_data import california_prop99
from synthdid.synthdid import Synthdid
from matplotlib import pyplot as plt

df = california_prop99()
```

The dataset contains annual state-level observations from 1970 to 2000. The relevant variables are:

- **PacksPerCapita** — per capita cigarette consumption in packs per year. This is the outcome variable
- **State** — U.S. state identifier
- **Year** — calendar year
- **treated** — dummy equal to 1 for California post-1989, 0 otherwise

To estimate the ATT using the SDID estimator:

```python
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

We estimate that Proposition 99 reduced cigarette consumption by approximately 15.6 packs per capita. To visualize the weighted outcome trends and the estimated weights:

```python
plt.show(california_sdid.plot_outcomes())
plt.show(california_sdid.plot_weights())
```

![Estimated Trends SDID Prop. 99](readme/california_sdid_trends.png)

![Estimated Weights SDID Prop. 99](readme/california_sdid_weights.png)

The package also supports the Synthetic Control (SC) and Difference-in-Differences (DiD) estimators through the same interface, using the `synth` and `did` flags in `.fit()`:

```python
# Synthetic Control
california_sc = Synthdid(df, "State", "Year", "treated", "PacksPerCapita").fit(synth=True)
plt.show(california_sc.plot_outcomes())
plt.show(california_sc.plot_weights())
```

![Estimated Trends SC Prop. 99](readme/california_sc_trends.png)

![Estimated Weights SC Prop. 99](readme/california_sc_weights.png)

```python
# Difference-in-Differences
california_did = Synthdid(df, "State", "Year", "treated", "PacksPerCapita").fit(did=True)
plt.show(california_did.plot_outcomes())
plt.show(california_did.plot_weights())
```

![Estimated Trends DiD Prop. 99](readme/california_did_trends.png)

![Estimated Weights DiD Prop. 99](readme/california_did_weights.png)

### Staggered Adoption Design

The following example estimates the effect of gender quota laws on women's parliamentary representation across multiple countries, where different countries adopted the law at different points in time.

```python
from synthdid.get_data import quota

df = quota()
```

The dataset contains country-year observations. The relevant variables are:

- **womparl** — share of women in parliament (%). This is the outcome variable
- **country** — country identifier
- **year** — calendar year
- **quota** — dummy equal to 1 once a country has adopted a gender quota law, 0 otherwise
- **lngdp** — log of GDP per capita (available as an optional covariate)

To estimate the overall ATT and the cohort-level decomposition:

```python
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

We estimate that gender quota laws increased women's parliamentary representation by approximately 8 percentage points. The ATT decomposed by treatment cohort is available through the `att_info` attribute:

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

Where `time` is the cohort adoption year, `att_time` is the cohort-specific ATT, `att_wt` is the cohort weight in the overall ATT, `N0`/`N1` are the number of control/treated units, and `T0`/`T1` are the number of pre/post-treatment periods.

## Covariate Adjustment

When covariates are available, they can be included to improve the quality of the synthetic control. The `"optimized"` method (default) jointly estimates the weights and the covariate coefficients, while `"projected"` first removes the covariate variation by projection and then estimates the weights on the residuals.

```python
# Optimized method
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

```python
# Projected method
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

## Inference

Three standard error estimation methods are available. They can be called on an already-fitted model without re-running `.fit()`:

- **`"bootstrap"`** — resamples units with replacement. Suitable for large samples.
- **`"placebo"`** — assigns placebo treatments to control units and estimates the variance of the null distribution. Recommended when the number of treated units is small.
- **`"jackknife"`** — leave-one-unit-out resampling. Conservative and computationally intensive.

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
|--|---------|-----------|-----------|-----------|
| 0 | 10.33066 | 5.404923 | 1.911343 | 0.055961 |

```python
se_examples.vcov(method="placebo").summary()
se_examples.summary2
```

| | ATT | Std. Err. | t | P > \|t\| |
|--|---------|-----------|-----------|-----------|
| 0 | 10.33066 | 2.244618 | 4.602413 | 0.000004 |

```python
se_examples.vcov(method="jackknife").summary()
se_examples.summary2
```

| | ATT | Std. Err. | t | P > \|t\| |
|--|---------|-----------|-----------|-----------|
| 0 | 10.33066 | 6.04213 | 1.709771 | 0.087308 |

## How to cite

If you use **synthdid** in your research, please cite both the original paper and this package:

**Original paper:**
```
@article{Arkhangelsky2021,
  author  = {Arkhangelsky, Dmitry and Athey, Susan and Hirshberg, David A. and Imbens, Guido W. and Wager, Stefan},
  title   = {Synthetic Difference-in-Differences},
  journal = {American Economic Review},
  volume  = {111},
  number  = {12},
  pages   = {4088--4118},
  year    = {2021},
  doi     = {10.1257/aer.20190159}
}
```

**This package:**
```
@software{synthdid,
  author  = {Flores, Jhon and Caceres, Franco and Grijalba, Rodrigo and Quispe, Alexander and Clarke, Damian and Nicho, Jesus},
  title   = {{synthdid: Synthetic Difference-in-Differences Estimation in Python}},
  year    = {2026},
  url     = {https://github.com/d2cml-ai/synthdid.py}
}
```
