# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - No candidate reached positive, trade-sufficient fitness on TRAIN.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00019 |
| Asset | XAUUSD_M30 |
| Timeframe | 30min |
| Historical period | 2022-01-02 23:30:00+00:00 to 2026-10-01 00:00:00+00:00 (56124 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | 34d6bd7330bee03f |
| Mode / budget used | standard - 9 experiments, 0 strategies examined, 1.98 min |
| Backtests counted as trials (all runs on this dataset) | 3773 |

**Splits** (chronological, embargoed): TRAIN 2022-01-02 to 2024-06-30 (29467 bars); VALIDATION 2024-07-02 to 2025-03-31 (8837 bars); TEST 2025-04-02 to 2025-12-31 (8878 bars); FINAL 2026-01-05 to 2026-10-01 (8798 bars)

## Data

- provenance: {'from': 'XAUUSD_M1 (dukascopy_candles(instrument=XAUUSD, start=2022-01-01, end=2026-10-01, granularity=minute, point=0.001))', 'base_sha256': '9fc91a333da5ceafd60a90e0dc26bf05eac98620082df0378b15f89b9ef3ece2', 'base_notes': ["provenance: {'bid_files': 1486, 'bid_missing_periods': [], 'ask_files': 1486, 'ask_missing_periods': [], 'bars': 1683273, 'flat_zero_volume_dropped': 456567, 'spread_median': 0.40199999999992997, 'volume': 'Dukascopy tick volume (not exchange volume)', 'seconds': 7.2, 'field_order': 'open,close,low,high (verified by checks)'}", 'per-bar spread available (median 0.402)', "cross-check vs None: {'kind': 'monthly_mean', 'matches': 57, 'median_abs_diff_pct': 0.07304133461434326, 'p95_abs_diff_pct': 0.35078594305940347, 'return_corr': 0.9980944700933462, 'note': 'monthly-average check: does not verify intraday timestamps', 'status': 'PASSED'}"], 'bars': 56132, 'short_bars_dropped': 8, 'hours': 0.5, 'anchor': '17:00 America/New_York'}
- per-bar spread available (median 0.399917)
- Quality OK: 56124 raw rows -> 56124 bars; 0 missing (holidays/no fix), 0 duplicates, 0 corrupt, 0 bad prints removed, gaps 35
- Exogenous `us_cpi_yoy`: OK - US CPI-U YoY (BLS), 35-day lag (lag 35 days)
- Exogenous `us_10y_yield`: OK - US 10Y yield monthly average (Fed H.15) (lag 1 days)
- Exogenous `vix`: OK - CBOE VIX close, usable from the end of its NY day (lag 0 days)
- Exogenous `brent`: OK - Brent spot (EIA), next NY day (lag 1 days)

## Market discoveries

91 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 5.**

- **big_move_clustering** - P(>2.5 sigma bar next) after a >2.5 sigma bar vs otherwise: effect 0.12422, p=0.00000, q=0.0000, replication p=0.00028 (n=962)
- **arch_lm_5** - Engle ARCH-LM(5): volatility clustering; effect = R^2: effect 0.01860, p=0.00000, q=0.0000, replication p=0.00000 (n=29461)
- **ljung_box_abs_20** - Ljung-Box(20) on |returns|; effect = lag-1 acf of |r|: effect 0.25495, p=0.00000, q=0.0000, replication p=0.00000 (n=29466)
- **compression_then_expansion** - log(next-20-bar vol / vol60) after the 10% most compressed 5/60 vol ratios (vs rest): effect -0.19118, p=0.00000, q=0.0000, replication p=0.00013 (n=2943)
- **high_vol_mean_reversion** - log(next-20-bar vol / vol60) when vol20 is in its top decile (vs rest): effect -0.40801, p=0.00000, q=0.0000, replication p=0.00000 (n=2946)
- Not replicated: runs_test_signs (train p=0.00000, validation p=0.0475)
- Not replicated: hour_16 (train p=0.00060, validation p=0.0192)
- Not replicated: hour_17 (train p=0.00048, validation p=0.4048)
- Not replicated: hour_18 (train p=0.00290, validation p=0.4901)
- Descriptive - return_distribution_train: Per-bar log return distribution {"mean_bps": 0.08138732870042292, "ann_vol": 0.14095309657922966, "skew": 0.22389848866276038, "excess_kurtosis": 21.027947596386973, "jarque_bera_p": 0.0, "n": 29466}
- Descriptive - return_distribution_validation: Per-bar log return distribution {"mean_bps": 0.33101384946064644, "ann_vol": 0.13548376140629637, "skew": -0.628960533673986, "excess_kurtosis": 8.597110681676224, "jarque_bera_p": 0.0, "n": 8837}
- Descriptive - trend_episode_duration: Directional-change episodes (threshold 0.0068 log) vs 200 shuffled-return paths (TRAIN) {"episodes": 529, "mean_duration": 55.48771266540643, "median_duration": 40.0, "shuffled_mean_duration": 50.75104964496557, "p_longer_than_shuffled": 0.004975124378109453}
- Descriptive - regime_model: GMM regimes on TRAIN, k=5 chosen by BIC {"labels": {"0": "R0: high-vol ranging", "1": "R1: high-vol trending contracting", "2": "R2: high-vol trending contracting", "3": "R3: low-vol ranging contracting", "4": "R4: low-vol trending"}, "persistence": {"0": 0.5041531747149092, "1": 0.7242524916943521, "2": 0.5628830595734249, "3": 0.6204064587973274, "4": 0.7401242236024844}, "occupancy": {"0": 0.2413769667312332, "1": 0.1022870153260611,

## Macro discoveries

32 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- Descriptive - macro_data_limits: Macro series are latest-vintage (revised) values with conservative publication lags; no consensus data => no surprise analysis {}
- INSUFFICIENT DATA for: CPI, PCE, NFP, Unemployment rate, Average hourly earnings, GDP, PMI, Fed rate decision, ECB rate decision, Central bank statements

## News discoveries

0 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- INSUFFICIENT DATA for: news_predictive_power

## Feature discovery

400 candidate features, 1960 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **3** ['ret_3', 'smooth(shock_1,3)', 'close_loc']
Status counts: {'REJECTED': 1939, 'NOT_CONFIRMED': 16, 'CONFIRMED': 3, 'TOO_COMPLEX': 2}

## Top hypotheses

1585 hypotheses (1585 new, 0 reused from memory). Status counts: {'REJECTED': 1582, 'OVERFIT': 3}

No hypothesis survived FDR on the discovery window **and** confirmation on the inner holdout.

Strongest hypotheses that failed confirmation (OVERFIT):

- HYP-025692: When dom == 4, next 4-bar return differs from baseline - discovery p=0.00000, confirmation p=0.213, confirmation effect -0.00043 vs 0.00084
- HYP-025693: When dom == 4, next 8-bar return differs from baseline - discovery p=0.00002, confirmation p=0.235, confirmation effect -0.00081 vs 0.00149
- HYP-025691: When dom == 4, next 1-bar return differs from baseline - discovery p=0.00008, confirmation p=0.254, confirmation effect -0.00011 vs 0.00022

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 0 | 0 | evidence insufficient: no hypothesis survived FDR + inner-holdout confirmation |
| open_exploration | STOPPED | 1 | 0 | repeated failure: no genome with positive fitness on TRAIN |
| regime_conditioned | STOPPED | 1 | 0 | repeated failure: no genome with positive fitness on TRAIN |
| macro_conditioned | STOPPED | 1 | 0 | repeated failure: no genome with positive fitness on TRAIN |

## Top strategies

No strategy reached examination.

## Why the others failed


Final status of all 0 examined strategies: {}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-10-01 00:00:00+00:00, horizon 1 bars. Conditions: ret_3 in quintile 3/5 (current value -1.444e-05); smooth(shock_1,3) in quintile 3/5 (current value 0.002923); close_loc in quintile 4/5 (current value 0.7708); regime == 1
Sample size 302 (2022-01-06 to 2026-09-30).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.0331% | 29.1% | 24.3%-34.5% | 36.7% |
| B_flat | within +/-0.0331% | 38.4% | 33.1%-44.0% | 28.3% |
| C_down | < -0.0331% | 32.5% | 27.4%-37.9% | 35.0% |

Test vs baseline: p = 0.000 -> conditions are informative.
Invalidated if: ret_3 leaves quintile 3; smooth(shock_1,3) leaves quintile 3; close_loc leaves quintile 4; regime changes

- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- none

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
