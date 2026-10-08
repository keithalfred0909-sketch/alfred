# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 30 candidate strategies examined; none survived. Outcome: {'REJECTED': 30}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00013 |
| Asset | XAUUSD_H4 |
| Timeframe | 4h |
| Historical period | 2008-01-01 02:00:00+00:00 to 2026-10-01 01:00:00+00:00 (29026 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | 56e3a549e904e79c |
| Mode / budget used | standard - 12 experiments, 30 strategies examined, 3.33 min |
| Backtests counted as trials (all runs on this dataset) | 7046 |

**Splits** (chronological, embargoed): TRAIN 2008-01-01 to 2018-12-31 (17055 bars); VALIDATION 2019-01-09 to 2020-12-31 (3059 bars); TEST 2021-01-11 to 2022-12-30 (3057 bars); FINAL 2023-01-10 to 2026-10-01 (5765 bars)

## Data

- provenance: {'from': 'XAUUSD_H1 (dukascopy_candles(instrument=XAUUSD, start=2008-01-01, end=2026-10-01, granularity=hour, point=0.001))', 'base_sha256': 'b98525cfe3f0495138cbda4b8385986a47a17d1e9b6966c32231388f0b42ed8e', 'base_notes': ["provenance: {'bid_files': 225, 'bid_missing_periods': [], 'ask_files': 225, 'ask_missing_periods': [], 'bars': 112933, 'flat_zero_volume_dropped': 51419, 'spread_median': 0.36599999999998545, 'volume': 'Dukascopy tick volume (not exchange volume)', 'seconds': 0.7, 'field_order': 'open,close,low,high (verified by checks)'}", 'per-bar spread available (median 0.366)', "cross-check vs None: {'kind': 'monthly_mean', 'matches': 225, 'median_abs_diff_pct': 0.07114135929859877, 'p95_abs_diff_pct': 0.34121201481908325, 'return_corr': 0.9979318298761235, 'note': 'monthly-average check: does not verify intraday timestamps', 'status': 'PASSED'}"], 'bars': 29075, 'short_bars_dropped': 49, 'hours': 4, 'anchor': '17:00 America/New_York'}
- per-bar spread available (median 0.3875)
- Quality OK: 29026 raw rows -> 29026 bars; 0 missing (holidays/no fix), 0 duplicates, 0 corrupt, 0 bad prints removed, gaps 13
- Exogenous `us_cpi_yoy`: OK - US CPI-U YoY (BLS), 35-day lag (lag 35 days)
- Exogenous `us_10y_yield`: OK - US 10Y yield monthly average (Fed H.15) (lag 1 days)
- Exogenous `vix`: OK - CBOE VIX close, usable from the end of its NY day (lag 0 days)
- Exogenous `brent`: OK - Brent spot (EIA), next NY day (lag 1 days)

## Market discoveries

73 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 3.**

- **ljung_box_returns_10** - Ljung-Box(10) on returns; effect = lag-1 autocorrelation: effect -0.00616, p=0.00001, q=0.0002, replication p=0.00001 (n=17054)
- **arch_lm_5** - Engle ARCH-LM(5): volatility clustering; effect = R^2: effect 0.05854, p=0.00000, q=0.0000, replication p=0.00000 (n=17049)
- **ljung_box_abs_20** - Ljung-Box(20) on |returns|; effect = lag-1 acf of |r|: effect 0.23730, p=0.00000, q=0.0000, replication p=0.00000 (n=17054)
- Not replicated: runs_test_signs (train p=0.00013, validation p=0.0445)
- Not replicated: big_move_follow_fwd5 (train p=0.00375, validation p=0.6790)
- Not replicated: big_move_clustering (train p=0.00014, validation p=0.0091)
- Not replicated: compression_then_expansion (train p=0.00001, validation p=0.0556)
- Not replicated: high_vol_mean_reversion (train p=0.00019, validation p=0.2993)
- Not replicated: weekday_fri (train p=0.00065, validation p=0.5252)
- Not replicated: hour_17 (train p=0.00010, validation p=0.0150)
- Descriptive - return_distribution_train: Per-bar log return distribution {"mean_bps": 0.25284662893720045, "ann_vol": 0.18176135802141918, "skew": 0.12800944223841254, "excess_kurtosis": 16.267381571375925, "jarque_bera_p": 0.0, "n": 17054}
- Descriptive - return_distribution_validation: Per-bar log return distribution {"mean_bps": 1.2752441921523894, "ann_vol": 0.16187498549362536, "skew": -1.4489170415778871, "excess_kurtosis": 25.879518121894645, "jarque_bera_p": 0.0, "n": 3059}
- Descriptive - trend_episode_duration: Directional-change episodes (threshold 0.0227 log) vs 200 shuffled-return paths (TRAIN) {"episodes": 331, "mean_duration": 50.77341389728097, "median_duration": 33.0, "shuffled_mean_duration": 46.20035924905029, "p_longer_than_shuffled": 0.024875621890547265}
- Descriptive - regime_model: GMM regimes on TRAIN, k=5 chosen by BIC {"labels": {"0": "R0: high-vol trending contracting", "1": "R1: high-vol trending contracting", "2": "R2: low-vol ranging contracting", "3": "R3: high-vol ranging", "4": "R4: low-vol trending contracting"}, "persistence": {"0": 0.8502824858757062, "1": 0.5477272727272727, "2": 0.5555258228525555, "3": 0.6859389454209066, "4": 0.7931093296946955}, "occupancy": {"0": 0.10402585953570379, "1": 0.0775

## Macro discoveries

32 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- Descriptive - macro_data_limits: Macro series are latest-vintage (revised) values with conservative publication lags; no consensus data => no surprise analysis {}
- INSUFFICIENT DATA for: CPI, PCE, NFP, Unemployment rate, Average hourly earnings, GDP, PMI, Fed rate decision, ECB rate decision, Central bank statements

## News discoveries

0 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- INSUFFICIENT DATA for: news_predictive_power

## Feature discovery

400 candidate features, 1955 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **0** []
Status counts: {'REJECTED': 1952, 'NOT_CONFIRMED': 3}

## Top hypotheses

2130 hypotheses (2130 new, 0 reused from memory). Status counts: {'REJECTED': 2129, 'OVERFIT': 1}

No hypothesis survived FDR on the discovery window **and** confirmation on the inner holdout.

Strongest hypotheses that failed confirmation (OVERFIT):

- HYP-015562: When dow == 4, next 3-bar return differs from baseline - discovery p=0.00002, confirmation p=0.643, confirmation effect 0.00015 vs 0.00144

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 0 | 0 | evidence insufficient: no hypothesis survived FDR + inner-holdout confirmation |
| open_exploration | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| regime_conditioned | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| macro_conditioned | STOPPED | 2 | 10 | budget: max_strategies (30) examined |

## Top strategies

### Strategy #1 - STR-000440 - **REJECTED**

**Rules:** LONG when x_brent_chg20 in bottom 10% AND zdist_10 in top 20%; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 3.68

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 33.09% | 2.63% | 1.41 | 0.33 | 0.49 | 19.77% | 87 | 32.9 bps | 52.87% |
| VALIDATION | 16.68% | 8.12% | 9.79 | 1.54 | 2.55 | 3.55% | 14 | 110.2 bps | 64.29% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.34, positive windows 83.33%, efficiency 1.49; expanding OOS Sharpe 0.27

**Monte Carlo:** P(loss) under trade bootstrap 5.70%, 95th pct max DD 28.79%; random-entry test p = 0.020

**Stress tests:** x2: SR 0.38, x3: SR 0.31, latency_plus1: SR 0.50, entry_shift_+1: SR 0.43, entry_shift_+2: SR 0.46

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 76.92%

**Overfitting risk:** deflated Sharpe probability 0.003 (after 7046 trials); PBO 0.64; IS->OOS Sharpe ratio 4.68

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.5420495279649096, "pf": 9.787279727215095, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 101 | >= 40 |
| beats_random_entries | reject | PASS | 0.020 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.33542885001222783, "positive_windows": 0.83 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.383 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.314 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.497 | SR>0 |
| entry_displacement | reject | PASS | [0.4346813770748661, 0.4605984159377766] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.769 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.951 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.287 | > 0 |
| other_regimes | reject | PASS | 0.558 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.306 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.40814543230544975, "phase1": 0.4611420104924013 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.057 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.003 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.639 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.9509301319806909 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 7046 trials? -> value 0.0034746363414172262 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.6388888888888888 vs <= 0.5

### Strategy #2 - STR-000450 - **REJECTED**

**Rules:** LONG when close_loc in top 20% AND range_vol in top 10%; exit after 10 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 10 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 2.73

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 85.54% | 5.77% | 1.48 | 0.67 | 1.02 | 12.14% | 330 | 18.7 bps | 56.97% |
| VALIDATION | 16.21% | 7.90% | 1.53 | 0.85 | 1.11 | 10.65% | 65 | 23.1 bps | 56.92% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.50, positive windows 66.67%, efficiency 0.78; expanding OOS Sharpe 0.58

**Monte Carlo:** P(loss) under trade bootstrap 0.30%, 95th pct max DD 21.28%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.48, x3: SR 0.26, latency_plus1: SR 0.42, entry_shift_+1: SR 0.43, entry_shift_+2: SR 0.38

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 92.31%

**Overfitting risk:** deflated Sharpe probability 0.057 (after 7046 trials); PBO 0.60; IS->OOS Sharpe ratio 1.28

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.8494947177404704, "pf": 1.5274943079421068, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 396 | >= 40 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.49876804340886177, "positive_windows": 0.66 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.481 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.261 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.416 | SR>0 |
| entry_displacement | reject | PASS | [0.4329464776567864, 0.37991704773607304] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.923 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.874 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.704 | > 0 |
| other_regimes | reject | PASS | 0.474 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.352 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.1817051063975898, "phase1": 0.33710976586349667 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.003 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.057 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.595 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.873936872882048 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 7046 trials? -> value 0.05745419108291615 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.5952380952380952 vs <= 0.5

### Strategy #3 - STR-000432 - **REJECTED**

**Rules:** LONG when month == 1; exit after 15 bars, stop 1.5 x vol x sqrt(hold)

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 15 bars, or stop at 1.5 x vol x sqrt(hold)
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 2.72

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 37.30% | 2.92% | 1.61 | 0.56 | 0.85 | 13.42% | 100 | 31.7 bps | 57.00% |
| VALIDATION | 3.66% | 1.83% | 1.75 | 0.57 | 0.91 | 3.64% | 16 | 22.5 bps | 56.25% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.93, positive windows 100.00%, efficiency 1.17; expanding OOS Sharpe 0.90

**Monte Carlo:** P(loss) under trade bootstrap 2.30%, 95th pct max DD 17.25%; random-entry test p = 0.028

**Stress tests:** x2: SR 0.44, x3: SR 0.33, latency_plus1: SR 0.49, entry_shift_+1: SR 0.50, entry_shift_+2: SR 0.55

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 84.62%

**Overfitting risk:** deflated Sharpe probability 0.026 (after 7046 trials); PBO 0.94; IS->OOS Sharpe ratio 1.02

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.5699331183986612, "pf": 1.7549245529452906, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 118 | >= 40 |
| beats_random_entries | reject | PASS | 0.028 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.9291157031821717, "positive_windows": 1.0} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.441 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.327 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.493 | SR>0 |
| entry_displacement | reject | PASS | [0.5040355867542153, 0.5477371813804675] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.846 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.629 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.255 | > 0 |
| other_regimes | reject | PASS | 0.337 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.505 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.2923221046550506, "phase1": 0.527673980481642} | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.023 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.026 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.937 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.6287650492989603 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 7046 trials? -> value 0.026079794304013998 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.9365079365079365 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- deflated_sharpe: 30
- probability_backtest_overfitting: 30
- few_trades_dependence: 26
- out_of_sample_validation: 23
- walk_forward: 14
- other_years: 9
- schedule_dependence: 6
- entry_displacement: 4
- beats_random_entries: 4
- monte_carlo_loss_probability: 4
- spread_slippage_x2: 3
- single_event_dependence: 3
- data_perturbation: 3
- parameter_perturbation: 2
- other_regimes: 2
- latency_plus1: 2
- randomized_execution: 2

Final status of all 30 examined strategies: {'REJECTED': 30}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-10-01 01:00:00+00:00, horizon 1 bars. Conditions: vol_20 in quintile 5/5 (current value -5.137); ret_20 in quintile 1/5 (current value -0.03092); zdist_60 in quintile 1/5 (current value -0.7467); regime == 4
Sample size 307 (2008-04-24 to 2026-09-30).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.0909% | 43.0% | 37.6%-48.6% | 37.3% |
| B_flat | within +/-0.0909% | 19.9% | 15.8%-24.7% | 28.3% |
| C_down | < -0.0909% | 37.1% | 31.9%-42.7% | 34.4% |

Test vs baseline: p = 0.004 -> conditions are informative.
Invalidated if: vol_20 leaves quintile 5; ret_20 leaves quintile 1; zdist_60 leaves quintile 1; regime changes

- No validated predictive condition exists; conditioning uses generic context variables (volatility, recent return, distance to mean) only.
- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- validation/evaluate: 30

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
