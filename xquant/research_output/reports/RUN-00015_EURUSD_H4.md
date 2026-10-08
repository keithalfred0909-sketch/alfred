# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 30 candidate strategies examined; none survived. Outcome: {'REJECTED': 26, 'OVERFIT': 4}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00015 |
| Asset | EURUSD_H4 |
| Timeframe | 4h |
| Historical period | 2005-01-03 02:00:00+00:00 to 2026-10-01 01:00:00+00:00 (33944 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | 9f17d2bbc91a25b7 |
| Mode / budget used | standard - 12 experiments, 30 strategies examined, 3.87 min |
| Backtests counted as trials (all runs on this dataset) | 8126 |

**Splits** (chronological, embargoed): TRAIN 2005-01-03 to 2016-12-30 (18748 bars); VALIDATION 2017-01-09 to 2019-12-31 (4641 bars); TEST 2020-01-09 to 2022-12-30 (4653 bars); FINAL 2023-01-09 to 2026-10-01 (5812 bars)

## Data

- provenance: {'from': 'EURUSD_H1 (dukascopy_candles(instrument=EURUSD, start=2005-01-01, end=2026-10-01, granularity=hour, point=1e-05))', 'base_sha256': 'b4364e784525f919143a9b2624500b75ef9cd1e1feaf30079f1feb5b24320971', 'base_notes': ["provenance: {'bid_files': 261, 'bid_missing_periods': [], 'ask_files': 261, 'ask_missing_periods': [], 'bars': 135749, 'flat_zero_volume_dropped': 54883, 'spread_median': 4.999999999988347e-05, 'volume': 'Dukascopy tick volume (not exchange volume)', 'seconds': 0.7, 'field_order': 'open,close,low,high (verified by checks)'}", 'per-bar spread available (median 5e-05)', "cross-check vs EURUSD: {'matches': 5445, 'median_abs_diff_bps': 0.6749699999986092, 'p95_abs_diff_bps': 2.350823999998975, 'return_corr': 0.9978510238484267, 'local_time': '12:00', 'tz': 'America/New_York', 'median_abs_diff_bps_shift-1h': 6.857475000001667, 'median_abs_diff_bps_shift+1h': 5.440820000000568, 'status': 'PASSED'}"], 'bars': 33948, 'short_bars_dropped': 4, 'hours': 4, 'anchor': '17:00 America/New_York'}
- per-bar spread available (median 5.625e-05)
- Quality OK: 33944 raw rows -> 33944 bars; 0 missing (holidays/no fix), 0 duplicates, 0 corrupt, 0 bad prints removed, gaps 15
- Exogenous `us_cpi_yoy`: OK - US CPI-U YoY (BLS). Released ~2 weeks after month end; conservative 35-day lag. (lag 35 days)
- Exogenous `us_10y_yield`: OK - US 10Y yield, monthly average (Fed H.15). Known at month end. (lag 1 days)
- Exogenous `vix`: OK - CBOE VIX close (16:15 New York). Usable from the end of its New York day. (lag 0 days)
- Exogenous `brent`: OK - Brent spot (EIA). Publication time uncertain; usable from the next New York day. (lag 1 days)

## Market discoveries

73 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 2.**

- **arch_lm_5** - Engle ARCH-LM(5): volatility clustering; effect = R^2: effect 0.02840, p=0.00000, q=0.0000, replication p=0.00000 (n=18742)
- **ljung_box_abs_20** - Ljung-Box(20) on |returns|; effect = lag-1 acf of |r|: effect 0.17138, p=0.00000, q=0.0000, replication p=0.00000 (n=18747)
- Not replicated: runs_test_signs (train p=0.00004, validation p=0.0690)
- Not replicated: hour_05 (train p=0.00000, validation p=0.2028)
- Not replicated: hour_13 (train p=0.00055, validation p=0.4568)
- Not replicated: hour_17 (train p=0.00000, validation p=0.0000)
- Not replicated: hour_21 (train p=0.00000, validation p=0.0317)
- Descriptive - return_distribution_train: Per-bar log return distribution {"mean_bps": -0.13453595619489472, "ann_vol": 0.1001138536343185, "skew": 0.008409370209966587, "excess_kurtosis": 8.301745177548513, "jarque_bera_p": 0.0, "n": 18747}
- Descriptive - return_distribution_validation: Per-bar log return distribution {"mean_bps": 0.1347571332110108, "ann_vol": 0.06514306250227488, "skew": 0.09522219488658874, "excess_kurtosis": 4.343294754273608, "jarque_bera_p": 0.0, "n": 4641}
- Descriptive - trend_episode_duration: Directional-change episodes (threshold 0.0142 log) vs 200 shuffled-return paths (TRAIN) {"episodes": 331, "mean_duration": 56.48036253776435, "median_duration": 37.0, "shuffled_mean_duration": 52.32705435252644, "p_longer_than_shuffled": 0.05970149253731343}
- Descriptive - regime_model: GMM regimes on TRAIN, k=5 chosen by BIC {"labels": {"0": "R0: low-vol ranging", "1": "R1: high-vol ranging contracting", "2": "R2: low-vol trending contracting", "3": "R3: high-vol trending", "4": "R4: high-vol trending contracting"}, "persistence": {"0": 0.4986270022883295, "1": 0.6255631965852502, "2": 0.7254302103250478, "3": 0.7017357421183138, "4": 0.5373856912318451}, "occupancy": {"0": 0.2336433611289288, "1": 0.2254115886251871,

## Macro discoveries

32 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- Descriptive - macro_data_limits: Macro series are latest-vintage (revised) values with conservative publication lags; no consensus data => no surprise analysis {}
- INSUFFICIENT DATA for: CPI, PCE, NFP, Unemployment rate, Average hourly earnings, GDP, PMI, Fed rate decision, ECB rate decision, Central bank statements

## News discoveries

0 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- INSUFFICIENT DATA for: news_predictive_power

## Feature discovery

400 candidate features, 1955 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **1** ['abs(volume_z)']
Status counts: {'REJECTED': 1954, 'CONFIRMED': 1}

## Top hypotheses

2155 hypotheses (2155 new, 0 reused from memory). Status counts: {'REJECTED': 2153, 'VALIDATION': 2}

| ID | Hypothesis | n | effect size | p | q | confirm p | status |
|---|---|---|---|---|---|---|---|
| HYP-021431 | When hour == 17, next 1-bar return differs from baseline | 2187 | -0.096 | 0.00000 | 0.0008 | 0.0022 | VALIDATION |
| HYP-021436 | When hour == 21, next 1-bar return differs from baseline | 2188 | 0.096 | 0.00000 | 0.0000 | 0.0138 | VALIDATION |

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| open_exploration | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| regime_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |
| macro_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |

## Top strategies

### Strategy #1 - STR-000529 - **OVERFIT**

**Rules:** SHORT when dom == 14 AND volratio_5_20 in bottom 20%; exit after 3 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 3 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 3.72

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 7.58% | 0.61% | 2.21 | 0.60 | 1.00 | 1.65% | 57 | 12.8 bps | 59.65% |
| VALIDATION | 4.21% | 1.40% | 5.09 | 1.21 | 2.96 | 0.81% | 15 | 27.5 bps | 60.00% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.77, positive windows 83.33%, efficiency 1.09; expanding OOS Sharpe 0.67

**Monte Carlo:** P(loss) under trade bootstrap 0.20%, 95th pct max DD 2.80%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.63, x3: SR 0.53, latency_plus1: SR 0.51, entry_shift_+1: SR 0.43, entry_shift_+2: SR 0.37

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 80.00%

**Overfitting risk:** deflated Sharpe probability 0.036 (after 8126 trials); PBO 0.58; IS->OOS Sharpe ratio 2.01

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.2075977287985948, "pf": 5.089968369910054, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 72 | >= 40 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.7669364641620471, "positive_windows": 0.833 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.632 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.529 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.510 | SR>0 |
| entry_displacement | reject | PASS | [0.42808093769441574, 0.3669158944547889] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.800 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.449 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.092 | > 0 |
| other_regimes | reject | PASS | 0.454 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.370 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.16710756650179354, "phase1": -0.31021173834988 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.002 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.036 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.579 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** deflated_sharpe: Is the train Sharpe significant after 8126 trials? -> value 0.03555110075946379 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.5793650793650794 vs <= 0.5

### Strategy #2 - STR-000527 - **OVERFIT**

**Rules:** SHORT when bars_into_month == 25 AND volratio_5_20 in bottom 30%; exit after 15 bars, take-profit 1.0 x vol x sqrt(hold)

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 15 bars, or take-profit at 1.0 x vol x sqrt(hold)
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 3.31

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 21.16% | 1.61% | 4.18 | 1.02 | 1.99 | 3.84% | 46 | 41.7 bps | 76.09% |
| VALIDATION | 2.91% | 0.97% | 4.44 | 1.01 | 1.86 | 0.81% | 12 | 23.9 bps | 66.67% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.73, positive windows 100.00%, efficiency 0.79; expanding OOS Sharpe 0.67

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 3.46%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.95, x3: SR 0.90, latency_plus1: SR 0.72, entry_shift_+1: SR 0.73, entry_shift_+2: SR 0.52

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 100.00%

**Overfitting risk:** deflated Sharpe probability 0.381 (after 8126 trials); PBO 0.58; IS->OOS Sharpe ratio 0.99

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.0128674899734285, "pf": 4.440793275609635, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 58 | >= 40 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.7299643767513564, "positive_windows": 1.0} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.954 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.901 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.718 | SR>0 |
| entry_displacement | reject | PASS | [0.7321185507251322, 0.5239365534590126] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 1.000 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.212 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.203 | > 0 |
| other_regimes | reject | PASS | 0.355 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.427 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": 0.031120274201963664, "phase1": -0.23853892063600 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.381 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.579 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** deflated_sharpe: Is the train Sharpe significant after 8126 trials? -> value 0.38112464888505687 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.5793650793650794 vs <= 0.5

### Strategy #3 - STR-000526 - **OVERFIT**

**Rules:** SHORT when bars_into_month == 25 AND volratio_5_20 in bottom 30%; exit after 15 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 15 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 2.95

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 22.78% | 1.72% | 4.05 | 0.94 | 1.70 | 5.42% | 46 | 44.6 bps | 71.74% |
| VALIDATION | 2.36% | 0.79% | 3.80 | 0.63 | 1.07 | 1.24% | 12 | 19.5 bps | 66.67% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.78, positive windows 100.00%, efficiency 0.81; expanding OOS Sharpe 0.73

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 3.61%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.84, x3: SR 0.79, latency_plus1: SR 0.65, entry_shift_+1: SR 0.65, entry_shift_+2: SR 0.55

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 100.00%

**Overfitting risk:** deflated Sharpe probability 0.280 (after 8126 trials); PBO 0.58; IS->OOS Sharpe ratio 0.67

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.6330137549696573, "pf": 3.802516863443384, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 58 | >= 40 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.777345170910773, "positive_windows": 1.0} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.841 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.792 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.653 | SR>0 |
| entry_displacement | reject | PASS | [0.6525925028079651, 0.5483784859180979] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 1.000 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.350 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.199 | > 0 |
| other_regimes | reject | PASS | 0.475 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.412 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.04662239976491655, "phase1": -0.17483743499479 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.280 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.579 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** deflated_sharpe: Is the train Sharpe significant after 8126 trials? -> value 0.28000097533080304 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.5793650793650794 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- deflated_sharpe: 30
- probability_backtest_overfitting: 30
- few_trades_dependence: 22
- out_of_sample_validation: 18
- walk_forward: 2
- entry_displacement: 2
- other_years: 2
- beats_random_entries: 1
- monte_carlo_loss_probability: 1
- schedule_dependence: 1

Final status of all 30 examined strategies: {'OVERFIT': 4, 'REJECTED': 26}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-10-01 01:00:00+00:00, horizon 1 bars. Conditions: hour in quintile 5/5 (current value 21); abs(volume_z) in quintile 5/5 (current value 2.431); regime == 3
Sample size 961 (2005-04-04 to 2026-09-22).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.0483% | 33.0% | 30.1%-36.0% | 36.1% |
| B_flat | within +/-0.0483% | 34.7% | 31.7%-37.7% | 28.5% |
| C_down | < -0.0483% | 32.4% | 29.5%-35.4% | 35.4% |

Test vs baseline: p = 0.000 -> conditions are informative.
Invalidated if: hour leaves quintile 5; abs(volume_z) leaves quintile 5; regime changes

- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- validation/evaluate: 30

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
