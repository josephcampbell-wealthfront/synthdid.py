"""Regenerate Python trajectory figures for Comparativa.tex."""
import warnings; warnings.filterwarnings('ignore')
import sys; sys.path.insert(0, 'c:/Users/ronco/Desktop/synthdid.py')
import numpy as np, pandas as pd, pydataset, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from synthdid.synthdid import Synthdid

OUT = 'c:/Users/ronco/Desktop/synthdid.py/comparativa_figs'

df = pydataset.data('Cigar').copy()
df['year'] = df['year'] + 1900
df['real_price'] = df['price'] * 100 / df['cpi']
df = df.sort_values(['state','year'])
df['pct_change'] = df.groupby('state')['real_price'].pct_change() * 100
nat_trend = df.groupby('year')['pct_change'].median()
df['excess_pct'] = df['pct_change'] - df['year'].map(nat_trend)
window = df[(df['year'] >= 1974) & (df['year'] <= 1988)]
treated_info = window[window['excess_pct'] > 10].groupby('state')['year'].min().reset_index().rename(columns={'year': 'tyear'})
treated_states = set(treated_info['state'])
treated_year = dict(zip(treated_info['state'], treated_info['tyear']))
df['treatment'] = df.apply(
    lambda r: 1 if (r['state'] in treated_states and r['year'] >= treated_year[r['state']]) else 0, axis=1)

cohort_years = [1975, 1976, 1978, 1979, 1981, 1983, 1986]

np.random.seed(42)
m = Synthdid(df, 'state', 'year', 'treatment', 'sales').fit()
m.plot_outcomes()

for i, fig in enumerate(m.plot_outcomes):
    year = cohort_years[i]
    path = f'{OUT}/py_trends_{year}.png'
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f'Saved {path}')

print('Done.')
