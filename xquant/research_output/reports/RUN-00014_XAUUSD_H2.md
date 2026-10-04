# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 30 candidate strategies examined; none survived. Outcome: {'REJECTED': 25, 'OVERFIT': 5}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00014 |
| Asset | XAUUSD_H2 |
| Timeframe | 2h |
| Historical period | 2008-01-01 02:00:00+00:00 to 2026-10-01 01:00:00+00:00 (58055 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | e8c5c39876424950 |
| Mode / budget used | standard - 12 experiments, 30 strategies examined, 4.81 min |
| Backtests counted as trials (all runs on this dataset) | 7193 |

**Splits** (chronological, embargoed): TRAIN 2008-01-01 to 2018-12-31 (34136 bars); VALIDATION 2019-01-09 to 2020-12-31 (6120 bars); TEST 2021-01-11 to 2022-12-30 (6110 bars); FINAL 2023-01-10 to 2026-10-01 (11509 bars)

## Data

- provenance: {'from': 'XAUUSD_H1 (dukascopy_candles(instrument=XAUUSD, start=2008-01-01, end=2026-10-01, granularity=hour, point=0.001))', 'base_sha256': 'b98525cfe3f0495138cbda4b8385986a47a17d1e9b6966c32231388f0b42ed8e', 'base_notes': ["provenance: {'bid_files': 225, 'bid_missing_periods': [], 'ask_files': 225, 'ask_missing_periods': [], 'bars': 112933, 'flat_zero_volume_dropped': 51419, 'spread_median': 0.36599999999998545, 'volume': 'Dukascopy tick volume (not exchange volume)', 'seconds': 0.6, 'field_order': 'open,close,low,high (verified by checks)'}", 'per-bar spread available (median 0.366)', "cross-check vs None: {'kind': 'monthly_mean', 'matches': 225, 'median_abs_diff_pct': 0.07114135929859877, 'p95_abs_diff_pct': 0.34121201481908325, 'return_corr': 0.9979318298761235, 'note': 'monthly-average check: does not verify intraday timestamps', 'status': 'PASSED'}"], 'bars': 58055, 'short_bars_dropped': 0, 'hours': 2, 'anchor': '17:00 America/New_York'}
- per-bar spread available (median 0.37875)
- Quality OK: 58055 raw rows -> 58055 bars; 0 missing (holidays/no fix), 0 duplicates, 0 corrupt, 0 bad prints removed, gaps 15
- Exogenous `us_cpi_yoy`: OK - US CPI-U YoY (BLS), 35-day lag (lag 35 days)
- Exogenous `us_10y_yield`: OK - US 10Y yield monthly average (Fed H.15) (lag 1 days)
- Exogenous `vix`: OK - CBOE VIX close, usable from the end of its NY day (lag 0 days)
- Exogenous `brent`: OK - Brent spot (EIA), next NY day (lag 1 days)

## Market discoveries

79 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 5.**

- **runs_test_signs** - Wald-Wolfowitz runs of return signs; effect<0 = longer runs than chance: effect 0.03988, p=0.00000, q=0.0000, replication p=0.00172 (n=34112)
- **big_move_clustering** - P(>2.5 sigma bar next) after a >2.5 sigma bar vs otherwise: effect 0.06328, p=0.00000, q=0.0000, replication p=0.00336 (n=1235)
- **arch_lm_5** - Engle ARCH-LM(5): volatility clustering; effect = R^2: effect 0.05927, p=0.00000, q=0.0000, replication p=0.00000 (n=34130)
- **ljung_box_abs_20** - Ljung-Box(20) on |returns|; effect = lag-1 acf of |r|: effect 0.27197, p=0.00000, q=0.0000, replication p=0.00000 (n=34135)
- **compression_then_expansion** - log(next-20-bar vol / vol60) after the 10% most compressed 5/60 vol ratios (vs rest): effect -0.07041, p=0.00000, q=0.0000, replication p=0.00127 (n=3410)
- Not replicated: ljung_box_returns_10 (train p=0.00000, validation p=0.0000)
- Not replicated: big_move_follow_fwd10 (train p=0.00595, validation p=0.0584)
- Not replicated: high_vol_mean_reversion (train p=0.00000, validation p=0.0279)
- Not replicated: weekday_fri (train p=0.00211, validation p=0.7207)
- Not replicated: hour_17 (train p=0.00003, validation p=0.0090)
- Descriptive - return_distribution_train: Per-bar log return distribution {"mean_bps": 0.1263233165342029, "ann_vol": 0.1824132667924546, "skew": -0.005203859295644615, "excess_kurtosis": 19.1641276785264, "jarque_bera_p": 0.0, "n": 34135}
- Descriptive - return_distribution_validation: Per-bar log return distribution {"mean_bps": 0.6374137228421829, "ann_vol": 0.15830623544422892, "skew": -0.7786097185978487, "excess_kurtosis": 21.12545771945654, "jarque_bera_p": 0.0, "n": 6120}
- Descriptive - trend_episode_duration: Directional-change episodes (threshold 0.0160 log) vs 200 shuffled-return paths (TRAIN) {"episodes": 657, "mean_duration": 51.25875190258752, "median_duration": 30.0, "shuffled_mean_duration": 46.881614710830675, "p_longer_than_shuffled": 0.009950248756218905}
- Descriptive - regime_model: GMM regimes on TRAIN, k=5 chosen by BIC {"labels": {"0": "R0: high-vol trending expanding", "1": "R1: high-vol ranging contracting", "2": "R2: high-vol trending contracting", "3": "R3: low-vol trending contracting", "4": "R4: low-vol ranging contracting"}, "persistence": {"0": 0.7441434846266471, "1": 0.5735294117647058, "2": 0.7156902908643998, "3": 0.7837837837837838, "4": 0.7995805871779509}, "occupancy": {"0": 0.08012670107930549, "

## Macro discoveries

32 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- Descriptive - macro_data_limits: Macro series are latest-vintage (revised) values with conservative publication lags; no consensus data => no surprise analysis {}
- INSUFFICIENT DATA for: CPI, PCE, NFP, Unemployment rate, Average hourly earnings, GDP, PMI, Fed rate decision, ECB rate decision, Central bank statements

## News discoveries

0 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- INSUFFICIENT DATA for: news_predictive_power

## Feature discovery

400 candidate features, 1960 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **2** ['close_loc', 'ret_1']
Status counts: {'REJECTED': 1863, 'NOT_CONFIRMED': 89, 'TOO_COMPLEX': 6, 'CONFIRMED': 2}

## Top hypotheses

2815 hypotheses (2815 new, 0 reused from memory). Status counts: {'REJECTED': 2814, 'OVERFIT': 1}

No hypothesis survived FDR on the discovery window **and** confirmation on the inner holdout.

Strongest hypotheses that failed confirmation (OVERFIT):

- HYP-017713: When dow == 4, next 6-bar return differs from baseline - discovery p=0.00001, confirmation p=0.598, confirmation effect 0.00016 vs 0.00150

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 0 | 0 | evidence insufficient: no hypothesis survived FDR + inner-holdout confirmation |
| open_exploration | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| regime_conditioned | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| macro_conditioned | STOPPED | 2 | 10 | budget: max_strategies (30) examined |

## Top strategies

### Strategy #1 - STR-000487 - **OVERFIT**

**Rules:** LONG when dow == 4 AND month == 1; exit after 8 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 8 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 4.23

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 26.58% | 2.16% | 4.54 | 0.97 | 1.85 | 1.98% | 48 | 49.1 bps | 66.67% |
| VALIDATION | 5.00% | 2.50% | 4.99 | 1.63 | 4.38 | 1.27% | 8 | 61.0 bps | 75.00% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.71, positive windows 83.33%, efficiency 0.70; expanding OOS Sharpe 0.87

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 3.62%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.87, x3: SR 0.73, latency_plus1: SR 0.95, entry_shift_+1: SR 0.95, entry_shift_+2: SR 0.98

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 84.62%

**Overfitting risk:** deflated Sharpe probability 0.270 (after 7193 trials); PBO 0.74; IS->OOS Sharpe ratio 1.67

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.629843895077504, "pf": 4.985881437766462, "trad | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 57 | >= 40 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.7130990625523256, "positive_windows": 0.833 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.868 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.733 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.945 | SR>0 |
| entry_displacement | reject | PASS | [0.945069460750955, 0.9849051624147888] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.846 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.350 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.178 | > 0 |
| other_regimes | reject | PASS | 0.342 | <= 85% from one regime |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 1.049235663584672, "phase1": 0.9339598504704215} | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.270 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.738 | <= 0.5 |

**Why it is ranked here:** passed 17 of 19 decisive/informative attacks.

**Why it might fail:** deflated_sharpe: Is the train Sharpe significant after 7193 trials? -> value 0.2699069943311697 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.7380952380952381 vs <= 0.5

### Strategy #2 - STR-000486 - **OVERFIT**

**Rules:** LONG when dow == 4 AND month == 1; exit after 10 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 10 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 4.17

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 23.98% | 1.97% | 3.81 | 0.84 | 1.48 | 2.58% | 48 | 44.8 bps | 62.50% |
| VALIDATION | 5.15% | 2.57% | 5.75 | 1.55 | 3.75 | 1.05% | 8 | 62.7 bps | 75.00% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.87, positive windows 100.00%, efficiency 0.97; expanding OOS Sharpe 0.98

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 3.59%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.77, x3: SR 0.64, latency_plus1: SR 0.97, entry_shift_+1: SR 0.97, entry_shift_+2: SR 0.96

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 84.62%

**Overfitting risk:** deflated Sharpe probability 0.139 (after 7193 trials); PBO 0.74; IS->OOS Sharpe ratio 1.85

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.5451357974712472, "pf": 5.747497249339432, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 57 | >= 40 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.8739548311726087, "positive_windows": 1.0} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.765 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.644 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.972 | SR>0 |
| entry_displacement | reject | PASS | [0.9715344794401041, 0.9575038019750175] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.846 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.345 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.193 | > 0 |
| other_regimes | reject | PASS | 0.398 | <= 85% from one regime |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 1.0333805398306868, "phase1": 0.9466007662979291} | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.139 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.738 | <= 0.5 |

**Why it is ranked here:** passed 17 of 19 decisive/informative attacks.

**Why it might fail:** deflated_sharpe: Is the train Sharpe significant after 7193 trials? -> value 0.13918501528031374 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.7380952380952381 vs <= 0.5

### Strategy #3 - STR-000488 - **OVERFIT**

**Rules:** LONG when dow == 4 AND month == 1; exit after 10 bars, take-profit 3.0 x vol x sqrt(hold)

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 10 bars, or take-profit at 3.0 x vol x sqrt(hold)
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 3.80

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 24.27% | 1.99% | 3.84 | 0.86 | 1.49 | 2.58% | 49 | 44.4 bps | 63.27% |
| VALIDATION | 4.20% | 2.10% | 4.89 | 1.38 | 3.09 | 1.05% | 9 | 45.7 bps | 77.78% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.81, positive windows 83.33%, efficiency 0.82; expanding OOS Sharpe 0.93

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 3.40%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.75, x3: SR 0.63, latency_plus1: SR 0.98, entry_shift_+1: SR 0.94, entry_shift_+2: SR 0.93

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 84.62%

**Overfitting risk:** deflated Sharpe probability 0.161 (after 7193 trials); PBO 0.74; IS->OOS Sharpe ratio 1.60

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.377244592196318, "pf": 4.888808409353472, "trad | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 59 | >= 40 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.8055955356729155, "positive_windows": 0.833 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.755 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.627 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.979 | SR>0 |
| entry_displacement | reject | PASS | [0.9435077030110982, 0.9294251814738275] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.846 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.291 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.175 | > 0 |
| other_regimes | reject | PASS | 0.350 | <= 85% from one regime |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 1.0517631851654894, "phase1": 0.9547693855741112} | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.161 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.738 | <= 0.5 |

**Why it is ranked here:** passed 17 of 19 decisive/informative attacks.

**Why it might fail:** deflated_sharpe: Is the train Sharpe significant after 7193 trials? -> value 0.16092499480911343 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.7380952380952381 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- deflated_sharpe: 30
- probability_backtest_overfitting: 25
- few_trades_dependence: 24
- out_of_sample_validation: 16
- walk_forward: 7
- other_years: 4
- other_regimes: 3
- beats_random_entries: 3
- monte_carlo_loss_probability: 2
- schedule_dependence: 1
- spread_slippage_x2: 1
- single_event_dependence: 1

Final status of all 30 examined strategies: {'OVERFIT': 5, 'REJECTED': 25}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-10-01 01:00:00+00:00, horizon 1 bars. Conditions: close_loc in quintile 5/5 (current value 0.853); ret_1 in quintile 3/5 (current value 0.0003863); regime == 4
Sample size 510 (2008-01-30 to 2026-09-09).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.0607% | 30.0% | 26.2%-34.1% | 36.6% |
| B_flat | within +/-0.0607% | 38.2% | 34.1%-42.5% | 29.0% |
| C_down | < -0.0607% | 31.8% | 27.9%-35.9% | 34.4% |

Test vs baseline: p = 0.000 -> conditions are informative.
Invalidated if: close_loc leaves quintile 5; ret_1 leaves quintile 3; regime changes

- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- validation/evaluate: 30

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
