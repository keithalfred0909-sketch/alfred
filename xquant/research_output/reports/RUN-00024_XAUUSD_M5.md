# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - No candidate reached positive, trade-sufficient fitness on TRAIN.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00024 |
| Asset | XAUUSD_M5 |
| Timeframe | 5min |
| Historical period | 2022-01-02 23:05:00+00:00 to 2026-10-01 00:00:00+00:00 (336730 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | 00fe48781b20ea92 |
| Mode / budget used | standard - 10 experiments, 0 strategies examined, 11.72 min |
| Backtests counted as trials (all runs on this dataset) | 5749 |

**Splits** (chronological, embargoed): TRAIN 2022-01-02 to 2024-06-30 (176808 bars); VALIDATION 2024-07-02 to 2025-03-31 (53017 bars); TEST 2025-04-02 to 2025-12-31 (53257 bars); FINAL 2026-01-05 to 2026-10-01 (52784 bars)

## Data

- provenance: {'from': 'XAUUSD_M1 (dukascopy_candles(instrument=XAUUSD, start=2022-01-01, end=2026-10-01, granularity=minute, point=0.001))', 'base_sha256': '9fc91a333da5ceafd60a90e0dc26bf05eac98620082df0378b15f89b9ef3ece2', 'base_notes': ["provenance: {'bid_files': 1486, 'bid_missing_periods': [], 'ask_files': 1486, 'ask_missing_periods': [], 'bars': 1683273, 'flat_zero_volume_dropped': 456567, 'spread_median': 0.40199999999992997, 'volume': 'Dukascopy tick volume (not exchange volume)', 'seconds': 7.1, 'field_order': 'open,close,low,high (verified by checks)'}", 'per-bar spread available (median 0.402)', "cross-check vs None: {'kind': 'monthly_mean', 'matches': 57, 'median_abs_diff_pct': 0.07304133461434326, 'p95_abs_diff_pct': 0.35078594305940347, 'return_corr': 0.9980944700933462, 'note': 'monthly-average check: does not verify intraday timestamps', 'status': 'PASSED'}"], 'bars': 336755, 'short_bars_dropped': 24, 'hours': 0.08333333333333333, 'anchor': '17:00 America/New_York'}
- per-bar spread available (median 0.4001)
- Quality WARN: 336731 raw rows -> 336730 bars; 0 missing (holidays/no fix), 0 duplicates, 0 corrupt, 1 bad prints removed, gaps 980
- Exogenous `us_cpi_yoy`: OK - US CPI-U YoY (BLS), 35-day lag (lag 35 days)
- Exogenous `us_10y_yield`: OK - US 10Y yield monthly average (Fed H.15) (lag 1 days)
- Exogenous `vix`: OK - CBOE VIX close, usable from the end of its NY day (lag 0 days)
- Exogenous `brent`: OK - Brent spot (EIA), next NY day (lag 1 days)

## Market discoveries

91 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 5.**

- **big_move_clustering** - P(>2.5 sigma bar next) after a >2.5 sigma bar vs otherwise: effect 0.08924, p=0.00000, q=0.0000, replication p=0.00000 (n=6185)
- **arch_lm_5** - Engle ARCH-LM(5): volatility clustering; effect = R^2: effect 0.04673, p=0.00000, q=0.0000, replication p=0.00000 (n=176802)
- **ljung_box_abs_20** - Ljung-Box(20) on |returns|; effect = lag-1 acf of |r|: effect 0.29945, p=0.00000, q=0.0000, replication p=0.00000 (n=176807)
- **compression_then_expansion** - log(next-20-bar vol / vol60) after the 10% most compressed 5/60 vol ratios (vs rest): effect -0.43308, p=0.00000, q=0.0000, replication p=0.00000 (n=17677)
- **high_vol_mean_reversion** - log(next-20-bar vol / vol60) when vol20 is in its top decile (vs rest): effect -0.13231, p=0.00000, q=0.0000, replication p=0.00000 (n=17680)
- Not replicated: runs_test_signs (train p=0.00000, validation p=0.0126)
- Not replicated: big_move_follow_fwd1 (train p=0.00337, validation p=0.2882)
- Not replicated: hour_16 (train p=0.00059, validation p=0.0196)
- Descriptive - return_distribution_train: Per-bar log return distribution {"mean_bps": 0.013530141856351766, "ann_vol": 0.1423148029652694, "skew": 0.3356052680334556, "excess_kurtosis": 28.415836608137848, "jarque_bera_p": 0.0, "n": 176807}
- Descriptive - return_distribution_validation: Per-bar log return distribution {"mean_bps": 0.054875149579644074, "ann_vol": 0.1354062419715663, "skew": -0.3255762696156821, "excess_kurtosis": 10.516326457562933, "jarque_bera_p": 0.0, "n": 53017}
- Descriptive - trend_episode_duration: Directional-change episodes (threshold 0.0025 log) vs 200 shuffled-return paths (TRAIN) {"episodes": 3866, "mean_duration": 45.7157268494568, "median_duration": 26.0, "shuffled_mean_duration": 42.8160579551207, "p_longer_than_shuffled": 0.004975124378109453}
- Descriptive - regime_model: GMM regimes on TRAIN, k=5 chosen by BIC {"labels": {"0": "R0: low-vol ranging", "1": "R1: high-vol ranging contracting", "2": "R2: low-vol trending contracting", "3": "R3: high-vol trending contracting", "4": "R4: high-vol trending"}, "persistence": {"0": 0.5015682919874537, "1": 0.5485780042742068, "2": 0.5159218417488876, "3": 0.7714629379040746, "4": 0.5837622770651901}, "occupancy": {"0": 0.21823520094134685, "1": 0.2064740224475018

## Macro discoveries

32 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- Descriptive - macro_data_limits: Macro series are latest-vintage (revised) values with conservative publication lags; no consensus data => no surprise analysis {}
- INSUFFICIENT DATA for: CPI, PCE, NFP, Unemployment rate, Average hourly earnings, GDP, PMI, Fed rate decision, ECB rate decision, Central bank statements

## News discoveries

0 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- INSUFFICIENT DATA for: news_predictive_power

## Feature discovery

400 candidate features, 2304 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **27** ['ret_3', 'ret_2', 'zdist_10', 'diff(sub(vol_60,zdist_250),5)', 'ret_5', 'fromhigh_20', 'zscore(zdist_250,20)', 'zdist_20', 'ret_20', 'ret_1']
Status counts: {'REJECTED': 2102, 'TOO_COMPLEX': 111, 'CONFIRMED': 54, 'NOT_CONFIRMED': 37}

## Top hypotheses

3894 hypotheses (3894 new, 0 reused from memory). Status counts: {'REJECTED': 3871, 'OVERFIT': 13, 'VALIDATION': 10}

| ID | Hypothesis | n | effect size | p | q | confirm p | status |
|---|---|---|---|---|---|---|---|
| HYP-035936 | When sess_bar == 272, next 6-bar return differs from baseline | 436 | 0.202 | 0.00008 | 0.0154 | 0.0002 | VALIDATION |
| HYP-035930 | When sess_bar == 271, next 6-bar return differs from baseline | 436 | 0.193 | 0.00016 | 0.0225 | 0.0001 | VALIDATION |
| HYP-035942 | When sess_bar == 273, next 6-bar return differs from baseline | 436 | 0.177 | 0.00014 | 0.0203 | 0.0002 | VALIDATION |
| HYP-035901 | When sess_bar == 266, next 12-bar return differs from baseline | 436 | 0.148 | 0.00007 | 0.0143 | 0.0003 | VALIDATION |
| HYP-035919 | When sess_bar == 269, next 12-bar return differs from baseline | 436 | 0.144 | 0.00012 | 0.0187 | 0.0014 | VALIDATION |
| HYP-035907 | When sess_bar == 267, next 12-bar return differs from baseline | 436 | 0.140 | 0.00008 | 0.0154 | 0.0004 | VALIDATION |
| HYP-035913 | When sess_bar == 268, next 12-bar return differs from baseline | 436 | 0.136 | 0.00009 | 0.0166 | 0.0008 | VALIDATION |
| HYP-034233 | When hour == 16, next 12-bar return differs from baseline | 5232 | 0.116 | 0.00003 | 0.0090 | 0.0000 | VALIDATION |
| HYP-035935 | When sess_bar == 272, next 3-bar return differs from baseline | 436 | 0.103 | 0.00006 | 0.0134 | 0.0016 | VALIDATION |
| HYP-034232 | When hour == 16, next 6-bar return differs from baseline | 5232 | 0.086 | 0.00004 | 0.0105 | 0.0000 | VALIDATION |

Strongest hypotheses that failed confirmation (OVERFIT):

- HYP-035940: When sess_bar == 273, next 1-bar return differs from baseline - discovery p=0.00000, confirmation p=0.516, confirmation effect 0.00002 vs 0.00007
- HYP-033970: When dom == 4, next 24-bar return differs from baseline - discovery p=0.00000, confirmation p=0.175, confirmation effect -0.00044 vs 0.00082
- HYP-033969: When dom == 4, next 12-bar return differs from baseline - discovery p=0.00000, confirmation p=0.155, confirmation effect -0.00023 vs 0.00042
- HYP-033968: When dom == 4, next 6-bar return differs from baseline - discovery p=0.00000, confirmation p=0.156, confirmation effect -0.00011 vs 0.00021
- HYP-033967: When dom == 4, next 3-bar return differs from baseline - discovery p=0.00001, confirmation p=0.167, confirmation effect -0.00005 vs 0.00011

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 1 | 0 | repeated failure: no genome with positive fitness on TRAIN |
| open_exploration | STOPPED | 1 | 0 | repeated failure: no genome with positive fitness on TRAIN |
| regime_conditioned | STOPPED | 1 | 0 | repeated failure: no genome with positive fitness on TRAIN |
| macro_conditioned | STOPPED | 1 | 0 | repeated failure: no genome with positive fitness on TRAIN |

## Top strategies

No strategy reached examination.

## Why the others failed


Final status of all 0 examined strategies: {}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-10-01 00:00:00+00:00, horizon 1 bars. Conditions: sess_bar in quintile 1/5 (current value 23); hour in quintile 5/5 (current value 20); ret_3 in quintile 4/5 (current value 0.0002551); regime == 1
Sample size 2001 (2022-01-04 to 2026-09-30).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.0136% | 31.6% | 29.6%-33.7% | 36.2% |
| B_flat | within +/-0.0136% | 33.6% | 31.6%-35.7% | 28.4% |
| C_down | < -0.0136% | 34.7% | 32.7%-36.8% | 35.5% |

Test vs baseline: p = 0.000 -> conditions are informative.
Invalidated if: sess_bar leaves quintile 1; hour leaves quintile 5; ret_3 leaves quintile 4; regime changes

- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- none

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
