# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - No candidate reached positive, trade-sufficient fitness on TRAIN.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00017 |
| Asset | XAUUSD_H1 |
| Timeframe | 1h |
| Historical period | 2008-01-01 01:00:00+00:00 to 2026-10-01 00:00:00+00:00 (112933 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | b7a71cf0475f238f |
| Mode / budget used | standard - 10 experiments, 0 strategies examined, 6.8 min |
| Backtests counted as trials (all runs on this dataset) | 125279 |

**Splits** (chronological, embargoed): TRAIN 2008-01-01 to 2018-12-31 (67108 bars); VALIDATION 2019-01-09 to 2020-12-31 (11717 bars); TEST 2021-01-11 to 2022-12-30 (11702 bars); FINAL 2023-01-10 to 2026-10-01 (22046 bars)

## Data

- provenance: {'bid_files': 225, 'bid_missing_periods': [], 'ask_files': 225, 'ask_missing_periods': [], 'bars': 112933, 'flat_zero_volume_dropped': 51419, 'spread_median': 0.36599999999998545, 'volume': 'Dukascopy tick volume (not exchange volume)', 'seconds': 0.6, 'field_order': 'open,close,low,high (verified by checks)'}
- per-bar spread available (median 0.366)
- cross-check vs None: {'kind': 'monthly_mean', 'matches': 225, 'median_abs_diff_pct': 0.07114135929859877, 'p95_abs_diff_pct': 0.34121201481908325, 'return_corr': 0.9979318298761235, 'note': 'monthly-average check: does not verify intraday timestamps', 'status': 'PASSED'}
- Quality OK: 112933 raw rows -> 112933 bars; 0 missing (holidays/no fix), 0 duplicates, 0 corrupt, 0 bad prints removed, gaps 103
- Exogenous `us_cpi_yoy`: OK - US CPI-U YoY (BLS), 35-day lag (lag 35 days)
- Exogenous `us_10y_yield`: OK - US 10Y yield monthly average (Fed H.15) (lag 1 days)
- Exogenous `vix`: OK - CBOE VIX close, usable from the end of its NY day (lag 0 days)
- Exogenous `brent`: OK - Brent spot (EIA), next NY day (lag 1 days)

## Market discoveries

91 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 7.**

- **ljung_box_returns_10** - Ljung-Box(10) on returns; effect = lag-1 autocorrelation: effect -0.00036, p=0.00000, q=0.0000, replication p=0.00007 (n=67107)
- **runs_test_signs** - Wald-Wolfowitz runs of return signs; effect<0 = longer runs than chance: effect 0.05532, p=0.00000, q=0.0000, replication p=0.00002 (n=67030)
- **big_move_clustering** - P(>2.5 sigma bar next) after a >2.5 sigma bar vs otherwise: effect 0.08206, p=0.00000, q=0.0000, replication p=0.00000 (n=2422)
- **arch_lm_5** - Engle ARCH-LM(5): volatility clustering; effect = R^2: effect 0.04744, p=0.00000, q=0.0000, replication p=0.00000 (n=67102)
- **ljung_box_abs_20** - Ljung-Box(20) on |returns|; effect = lag-1 acf of |r|: effect 0.28409, p=0.00000, q=0.0000, replication p=0.00000 (n=67107)
- **compression_then_expansion** - log(next-20-bar vol / vol60) after the 10% most compressed 5/60 vol ratios (vs rest): effect -0.10629, p=0.00000, q=0.0000, replication p=0.00000 (n=6707)
- **high_vol_mean_reversion** - log(next-20-bar vol / vol60) when vol20 is in its top decile (vs rest): effect -0.12504, p=0.00000, q=0.0000, replication p=0.00194 (n=6710)
- Not replicated: momentum_20_fwd5 (train p=0.00000, validation p=0.1178)
- Not replicated: hour_01 (train p=0.00094, validation p=0.1342)
- Not replicated: hour_02 (train p=0.00365, validation p=0.1888)
- Not replicated: hour_05 (train p=0.00003, validation p=0.0605)
- Not replicated: hour_09 (train p=0.00285, validation p=0.8904)
- Not replicated: hour_16 (train p=0.00252, validation p=0.7712)
- Not replicated: hour_17 (train p=0.00000, validation p=0.0030)
- Descriptive - return_distribution_train: Per-bar log return distribution {"mean_bps": 0.06426486723261299, "ann_vol": 0.1816749757453761, "skew": -0.16289355070566378, "excess_kurtosis": 24.854085823258057, "jarque_bera_p": 0.0, "n": 67107}
- Descriptive - return_distribution_validation: Per-bar log return distribution {"mean_bps": 0.33413645978979595, "ann_vol": 0.16312488973408262, "skew": -0.49385177893153753, "excess_kurtosis": 19.122501576019047, "jarque_bera_p": 0.0, "n": 11717}
- Descriptive - trend_episode_duration: Directional-change episodes (threshold 0.0113 log) vs 200 shuffled-return paths (TRAIN) {"episodes": 1283, "mean_duration": 52.07638347622759, "median_duration": 34.0, "shuffled_mean_duration": 47.053275761434286, "p_longer_than_shuffled": 0.004975124378109453}
- Descriptive - regime_model: GMM regimes on TRAIN, k=5 chosen by BIC {"labels": {"0": "R0: high-vol ranging contracting", "1": "R1: high-vol trending", "2": "R2: low-vol trending contracting", "3": "R3: high-vol trending contracting", "4": "R4: low-vol ranging contracting"}, "persistence": {"0": 0.5585637852124025, "1": 0.7227865126849404, "2": 0.8073394495412844, "3": 0.7793108948795662, "4": 0.6888619854721549}, "occupancy": {"0": 0.23130255859724458, "1": 0.3214

## Macro discoveries

32 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- Descriptive - macro_data_limits: Macro series are latest-vintage (revised) values with conservative publication lags; no consensus data => no surprise analysis {}
- INSUFFICIENT DATA for: CPI, PCE, NFP, Unemployment rate, Average hourly earnings, GDP, PMI, Fed rate decision, ECB rate decision, Central bank statements

## News discoveries

0 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- INSUFFICIENT DATA for: news_predictive_power

## Feature discovery

400 candidate features, 1960 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **27** ['close_loc', 'ret_1', 'shock_1', 'ret_2', 'diff(fromhigh_20,1)', 'mul(diff(zdist_60,1),range_vol)', 'streak', 'rank(zscore(diff(fromlow_250,1),20),60)', 'zscore(zscore(skew_20,20),20)', 'ret_3']
Status counts: {'REJECTED': 1748, 'NOT_CONFIRMED': 139, 'TOO_COMPLEX': 44, 'CONFIRMED': 29}

## Top hypotheses

4475 hypotheses (0 new, 4475 reused from memory). Status counts: {'REJECTED': 4453, 'OVERFIT': 19, 'VALIDATION': 3}

| ID | Hypothesis | n | effect size | p | q | confirm p | status |
|---|---|---|---|---|---|---|---|
| HYP-012177 | When hour == 16, next 3-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |
| HYP-012178 | When hour == 16, next 6-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |
| HYP-012182 | When hour == 17, next 3-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |

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

As of 2026-10-01 00:00:00+00:00, horizon 1 bars. Conditions: hour in quintile 5/5 (current value 20); close_loc in quintile 5/5 (current value 0.853); ret_1 in quintile 4/5 (current value 0.0003863); regime == 0
Sample size 408 (2008-01-04 to 2026-09-29).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.0434% | 29.9% | 25.7%-34.5% | 36.5% |
| B_flat | within +/-0.0434% | 35.3% | 30.8%-40.0% | 28.6% |
| C_down | < -0.0434% | 34.8% | 30.3%-39.5% | 35.0% |

Test vs baseline: p = 0.004 -> conditions are informative.
Invalidated if: hour leaves quintile 5; close_loc leaves quintile 5; ret_1 leaves quintile 4; regime changes

- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- none

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
