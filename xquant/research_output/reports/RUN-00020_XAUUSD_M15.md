# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - No candidate reached positive, trade-sufficient fitness on TRAIN.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00020 |
| Asset | XAUUSD_M15 |
| Timeframe | 15min |
| Historical period | 2022-01-02 23:15:00+00:00 to 2026-10-01 00:00:00+00:00 (112250 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | fb1eb3596dd0408b |
| Mode / budget used | standard - 10 experiments, 0 strategies examined, 4.92 min |
| Backtests counted as trials (all runs on this dataset) | 6975 |

**Splits** (chronological, embargoed): TRAIN 2022-01-02 to 2024-06-30 (58936 bars); VALIDATION 2024-07-02 to 2025-03-31 (17675 bars); TEST 2025-04-02 to 2025-12-31 (17756 bars); FINAL 2026-01-05 to 2026-10-01 (17595 bars)

## Data

- provenance: {'from': 'XAUUSD_M1 (dukascopy_candles(instrument=XAUUSD, start=2022-01-01, end=2026-10-01, granularity=minute, point=0.001))', 'base_sha256': '9fc91a333da5ceafd60a90e0dc26bf05eac98620082df0378b15f89b9ef3ece2', 'base_notes': ["provenance: {'bid_files': 1486, 'bid_missing_periods': [], 'ask_files': 1486, 'ask_missing_periods': [], 'bars': 1683273, 'flat_zero_volume_dropped': 456567, 'spread_median': 0.40199999999992997, 'volume': 'Dukascopy tick volume (not exchange volume)', 'seconds': 7.2, 'field_order': 'open,close,low,high (verified by checks)'}", 'per-bar spread available (median 0.402)', "cross-check vs None: {'kind': 'monthly_mean', 'matches': 57, 'median_abs_diff_pct': 0.07304133461434326, 'p95_abs_diff_pct': 0.35078594305940347, 'return_corr': 0.9980944700933462, 'note': 'monthly-average check: does not verify intraday timestamps', 'status': 'PASSED'}"], 'bars': 112257, 'short_bars_dropped': 7, 'hours': 0.25, 'anchor': '17:00 America/New_York'}
- per-bar spread available (median 0.399833)
- Quality OK: 112250 raw rows -> 112250 bars; 0 missing (holidays/no fix), 0 duplicates, 0 corrupt, 0 bad prints removed, gaps 979
- Exogenous `us_cpi_yoy`: OK - US CPI-U YoY (BLS), 35-day lag (lag 35 days)
- Exogenous `us_10y_yield`: OK - US 10Y yield monthly average (Fed H.15) (lag 1 days)
- Exogenous `vix`: OK - CBOE VIX close, usable from the end of its NY day (lag 0 days)
- Exogenous `brent`: OK - Brent spot (EIA), next NY day (lag 1 days)

## Market discoveries

91 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 6.**

- **runs_test_signs** - Wald-Wolfowitz runs of return signs; effect<0 = longer runs than chance: effect 0.03210, p=0.00000, q=0.0000, replication p=0.00046 (n=58865)
- **big_move_clustering** - P(>2.5 sigma bar next) after a >2.5 sigma bar vs otherwise: effect 0.11609, p=0.00000, q=0.0000, replication p=0.00000 (n=2400)
- **arch_lm_5** - Engle ARCH-LM(5): volatility clustering; effect = R^2: effect 0.01748, p=0.00000, q=0.0000, replication p=0.00000 (n=58930)
- **ljung_box_abs_20** - Ljung-Box(20) on |returns|; effect = lag-1 acf of |r|: effect 0.26620, p=0.00000, q=0.0000, replication p=0.00000 (n=58935)
- **compression_then_expansion** - log(next-20-bar vol / vol60) after the 10% most compressed 5/60 vol ratios (vs rest): effect -0.50230, p=0.00000, q=0.0000, replication p=0.00000 (n=5890)
- **high_vol_mean_reversion** - log(next-20-bar vol / vol60) when vol20 is in its top decile (vs rest): effect -0.32069, p=0.00000, q=0.0000, replication p=0.00000 (n=5892)
- Not replicated: hour_16 (train p=0.00057, validation p=0.0189)
- Not replicated: hour_17 (train p=0.00027, validation p=0.3714)
- Descriptive - return_distribution_train: Per-bar log return distribution {"mean_bps": 0.040617641802226566, "ann_vol": 0.14158401097813705, "skew": 0.3599725108504265, "excess_kurtosis": 28.157084378722974, "jarque_bera_p": 0.0, "n": 58935}
- Descriptive - return_distribution_validation: Per-bar log return distribution {"mean_bps": 0.16579935281166447, "ann_vol": 0.13653675102529245, "skew": -0.4508315933339715, "excess_kurtosis": 10.700869441943688, "jarque_bera_p": 0.0, "n": 17675}
- Descriptive - trend_episode_duration: Directional-change episodes (threshold 0.0045 log) vs 200 shuffled-return paths (TRAIN) {"episodes": 1186, "mean_duration": 49.65261382799326, "median_duration": 33.0, "shuffled_mean_duration": 46.063161371219, "p_longer_than_shuffled": 0.004975124378109453}
- Descriptive - regime_model: GMM regimes on TRAIN, k=5 chosen by BIC {"labels": {"0": "R0: high-vol trending contracting", "1": "R1: high-vol trending contracting", "2": "R2: high-vol ranging", "3": "R3: low-vol trending contracting", "4": "R4: low-vol ranging contracting"}, "persistence": {"0": 0.6113146113146113, "1": 0.7691988950276243, "2": 0.5592025469981807, "3": 0.683301783972925, "4": 0.6526433358153388}, "occupancy": {"0": 0.08343520782396088, "1": 0.12292

## Macro discoveries

32 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- Descriptive - macro_data_limits: Macro series are latest-vintage (revised) values with conservative publication lags; no consensus data => no surprise analysis {}
- INSUFFICIENT DATA for: CPI, PCE, NFP, Unemployment rate, Average hourly earnings, GDP, PMI, Fed rate decision, ECB rate decision, Central bank statements

## News discoveries

0 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- INSUFFICIENT DATA for: news_predictive_power

## Feature discovery

400 candidate features, 1955 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **21** ['mul(diff(zdist_60,1),range_vol)', 'ret_1', 'shock_1', 'diff(fromhigh_20,1)', 'streak', 'close_loc', 'mul(diff(fromhigh_60,1),fromhigh_250)', 'zdist_10', 'rank(zscore(diff(fromlow_250,1),20),60)', 'ret_2']
Status counts: {'REJECTED': 1894, 'TOO_COMPLEX': 30, 'CONFIRMED': 21, 'NOT_CONFIRMED': 10}

## Top hypotheses

1745 hypotheses (1745 new, 0 reused from memory). Status counts: {'REJECTED': 1740, 'OVERFIT': 4, 'VALIDATION': 1}

| ID | Hypothesis | n | effect size | p | q | confirm p | status |
|---|---|---|---|---|---|---|---|
| HYP-027657 | When hour == 16, next 4-bar return differs from baseline | 1744 | 0.117 | 0.00001 | 0.0057 | 0.0000 | VALIDATION |

Strongest hypotheses that failed confirmation (OVERFIT):

- HYP-027438: When dom == 4, next 8-bar return differs from baseline - discovery p=0.00000, confirmation p=0.188, confirmation effect -0.00044 vs 0.00083
- HYP-027437: When dom == 4, next 4-bar return differs from baseline - discovery p=0.00001, confirmation p=0.178, confirmation effect -0.00023 vs 0.00043
- HYP-027439: When dom == 4, next 16-bar return differs from baseline - discovery p=0.00002, confirmation p=0.221, confirmation effect -0.00081 vs 0.00147
- HYP-027436: When dom == 4, next 1-bar return differs from baseline - discovery p=0.00006, confirmation p=0.235, confirmation effect -0.00005 vs 0.00011

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

As of 2026-10-01 00:00:00+00:00, horizon 1 bars. Conditions: hour in quintile 5/5 (current value 20); mul(diff(zdist_60,1),range_vol) in quintile 4/5 (current value 0.3247); ret_1 in quintile 4/5 (current value 0.0002551); regime == 3
Sample size 1213 (2022-01-07 to 2026-09-29).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.0235% | 29.6% | 27.1%-32.2% | 36.6% |
| B_flat | within +/-0.0235% | 38.3% | 35.6%-41.1% | 28.1% |
| C_down | < -0.0235% | 32.1% | 29.5%-34.7% | 35.3% |

Test vs baseline: p = 0.000 -> conditions are informative.
Invalidated if: hour leaves quintile 5; mul(diff(zdist_60,1),range_vol) leaves quintile 4; ret_1 leaves quintile 4; regime changes

- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- none

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
