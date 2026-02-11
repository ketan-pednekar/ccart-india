"""
CCART-India v1.3 — DLNA Regression Analysis
-------------------------------------------

This script loads the unified v1.3 master file, aggregates district-level
raw LitPop loss and HWE-calibrated loss to cyclone-level totals, and fits
a log–log regression model:

    log(DLNA) = a + b * log(raw_loss)

The resulting parameters (alpha, b) define the empirical CCART-v2 DLNA
relationship used for synthetic cyclone generation.

Author: Ketan
Version: v1.3
Date: 2026-02-05
"""
import pandas as pd
import numpy as np
import statsmodels.api as sm

MASTER_V13 = r"C:\CMIP data\cmip6\Climada\Projects\ccart-india\data\district_relationships_master_v1_3.csv"
df = pd.read_csv(MASTER_V13)

print(df.shape)
print(df.columns)

event = df.groupby(['sid','cyclone_name','year']).agg(
    raw_loss=('loss_usd_raw','sum'),
    hwe_loss=('loss_usd_hwe','sum'),
    dlna=('dlna_total','first')
).reset_index()

# Drop events with zero or missing raw_loss or dlna
event = event.replace([np.inf, -np.inf], np.nan)
event = event.dropna(subset=['raw_loss','dlna'])
event = event[event['raw_loss'] > 0]
print(event)

X = np.log(event['raw_loss'])
y = np.log(event['dlna'])

X = sm.add_constant(X)
model = sm.OLS(y, X).fit()
print(model.summary())

a = model.params['const']
b = model.params['raw_loss']
alpha = np.exp(a)

print("a =", a)
print("b =", b)
print("alpha =", alpha)
