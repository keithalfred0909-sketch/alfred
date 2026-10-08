# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 30 candidate strategies examined; none survived. Outcome: {'REJECTED': 30}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00016 |
| Asset | EURUSD_H2 |
| Timeframe | 2h |
| Historical period | 2005-01-03 00:00:00+00:00 to 2026-10-01 01:00:00+00:00 (67880 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | 91fce3090ce495e5 |
| Mode / budget used | standard - 12 experiments, 30 strategies examined, 6.17 min |
| Backtests counted as trials (all runs on this dataset) | 8271 |

**Splits** (chronological, embargoed): TRAIN 2005-01-03 to 2016-12-30 (37494 bars); VALIDATION 2017-01-09 to 2019-12-31 (9280 bars); TEST 2020-01-09 to 2022-12-30 (9305 bars); FINAL 2023-01-09 to 2026-10-01 (11621 bars)

## Data

- provenance: {'from': 'EURUSD_H1 (dukascopy_candles(instrument=EURUSD, start=2005-01-01, end=2026-10-01, granularity=hour, point=1e-05))', 'base_sha256': 'b4364e784525f919143a9b2624500b75ef9cd1e1feaf30079f1feb5b24320971', 'base_notes': ["provenance: {'bid_files': 261, 'bid_missing_periods': [], 'ask_files': 261, 'ask_missing_periods': [], 'bars': 135749, 'flat_zero_volume_dropped': 54883, 'spread_median': 4.999999999988347e-05, 'volume': 'Dukascopy tick volume (not exchange volume)', 'seconds': 0.7, 'field_order': 'open,close,low,high (verified by checks)'}", 'per-bar spread available (median 5e-05)', "cross-check vs EURUSD: {'matches': 5445, 'median_abs_diff_bps': 0.6749699999986092, 'p95_abs_diff_bps': 2.350823999998975, 'return_corr': 0.9978510238484267, 'local_time': '12:00', 'tz': 'America/New_York', 'median_abs_diff_bps_shift-1h': 6.857475000001667, 'median_abs_diff_bps_shift+1h': 5.440820000000568, 'status': 'PASSED'}"], 'bars': 67880, 'short_bars_dropped': 0, 'hours': 2, 'anchor': '17:00 America/New_York'}
- per-bar spread available (median 5e-05)
- Quality OK: 67880 raw rows -> 67880 bars; 0 missing (holidays/no fix), 0 duplicates, 0 corrupt, 0 bad prints removed, gaps 15
- Exogenous `us_cpi_yoy`: OK - US CPI-U YoY (BLS). Released ~2 weeks after month end; conservative 35-day lag. (lag 35 days)
- Exogenous `us_10y_yield`: OK - US 10Y yield, monthly average (Fed H.15). Known at month end. (lag 1 days)
- Exogenous `vix`: OK - CBOE VIX close (16:15 New York). Usable from the end of its New York day. (lag 0 days)
- Exogenous `brent`: OK - Brent spot (EIA). Publication time uncertain; usable from the next New York day. (lag 1 days)

## Market discoveries

79 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 4.**

- **arch_lm_5** - Engle ARCH-LM(5): volatility clustering; effect = R^2: effect 0.02566, p=0.00000, q=0.0000, replication p=0.00000 (n=37488)
- **ljung_box_abs_20** - Ljung-Box(20) on |returns|; effect = lag-1 acf of |r|: effect 0.21759, p=0.00000, q=0.0000, replication p=0.00000 (n=37493)
- **high_vol_mean_reversion** - log(next-20-bar vol / vol60) when vol20 is in its top decile (vs rest): effect -0.11950, p=0.00000, q=0.0000, replication p=0.00000 (n=3739)
- **hour_21** - next-bar return at hour 21 (vs other hours): effect 0.00016, p=0.00000, q=0.0000, replication p=0.00134 (n=3126)
- Not replicated: ljung_box_returns_10 (train p=0.00002, validation p=0.6209)
- Not replicated: runs_test_signs (train p=0.00000, validation p=0.0060)
- Not replicated: big_move_clustering (train p=0.00000, validation p=0.0283)
- Not replicated: streak3_fwd1 (train p=0.00106, validation p=0.1655)
- Not replicated: hour_05 (train p=0.00000, validation p=0.1508)
- Not replicated: hour_11 (train p=0.00001, validation p=0.9117)
- Not replicated: hour_15 (train p=0.00718, validation p=0.0062)
- Not replicated: hour_17 (train p=0.00001, validation p=0.0000)
- Not replicated: hour_19 (train p=0.00052, validation p=0.3727)
- Not replicated: regime2_fwd5 (train p=0.00135, validation p=0.8931)
- Descriptive - return_distribution_train: Per-bar log return distribution {"mean_bps": -0.06807053704519164, "ann_vol": 0.10172067579040195, "skew": 0.05377275754276359, "excess_kurtosis": 10.454721016441509, "jarque_bera_p": 0.0, "n": 37493}
- Descriptive - return_distribution_validation: Per-bar log return distribution {"mean_bps": 0.06739308784830832, "ann_vol": 0.0656165417910039, "skew": 0.21276008410506267, "excess_kurtosis": 8.76123505803521, "jarque_bera_p": 0.0, "n": 9280}
- Descriptive - trend_episode_duration: Directional-change episodes (threshold 0.0099 log) vs 200 shuffled-return paths (TRAIN) {"episodes": 675, "mean_duration": 55.39555555555555, "median_duration": 34.0, "shuffled_mean_duration": 51.2198700033675, "p_longer_than_shuffled": 0.009950248756218905}
- Descriptive - regime_model: GMM regimes on TRAIN, k=5 chosen by BIC {"labels": {"0": "R0: high-vol trending contracting", "1": "R1: high-vol trending contracting", "2": "R2: low-vol ranging", "3": "R3: low-vol trending", "4": "R4: high-vol ranging contracting"}, "persistence": {"0": 0.4437299035369775, "1": 0.7942809966976884, "2": 0.6265465465465465, "3": 0.587594988704046, "4": 0.5305923616523772}, "occupancy": {"0": 0.02491122206498812, "1": 0.35575254318746163

## Macro discoveries

32 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- Descriptive - macro_data_limits: Macro series are latest-vintage (revised) values with conservative publication lags; no consensus data => no surprise analysis {}
- INSUFFICIENT DATA for: CPI, PCE, NFP, Unemployment rate, Average hourly earnings, GDP, PMI, Fed rate decision, ECB rate decision, Central bank statements

## News discoveries

0 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- INSUFFICIENT DATA for: news_predictive_power

## Feature discovery

400 candidate features, 1960 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **16** ['close_loc', 'ret_1', 'streak', 'shock_1', 'ret_2', 'zdist_10', 'ret_3', 'mul(diff(zdist_60,1),range_vol)', 'fromlow_20', 'zdist_20']
Status counts: {'REJECTED': 1912, 'TOO_COMPLEX': 28, 'CONFIRMED': 16, 'NOT_CONFIRMED': 4}

## Top hypotheses

2905 hypotheses (2905 new, 0 reused from memory). Status counts: {'REJECTED': 2901, 'VALIDATION': 4}

| ID | Hypothesis | n | effect size | p | q | confirm p | status |
|---|---|---|---|---|---|---|---|
| HYP-024316 | When hour == 5, next 1-bar return differs from baseline | 2187 | -0.116 | 0.00000 | 0.0005 | 0.0021 | VALIDATION |
| HYP-024356 | When hour == 21, next 1-bar return differs from baseline | 2187 | 0.092 | 0.00000 | 0.0001 | 0.0152 | VALIDATION |
| HYP-024357 | When hour == 21, next 3-bar return differs from baseline | 2187 | 0.086 | 0.00000 | 0.0003 | 0.0294 | VALIDATION |
| HYP-024332 | When hour == 11, next 3-bar return differs from baseline | 2187 | 0.078 | 0.00006 | 0.0470 | 0.0000 | VALIDATION |

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| open_exploration | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| regime_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |
| macro_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |

## Top strategies

### Strategy #1 - STR-000561 - **REJECTED**

**Rules:** SHORT when x_brent_chg20 in top 10% AND ret_20 in bottom 15% AND ret_2 in bottom 15%; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 1.74

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 28.68% | 2.12% | 3.33 | 0.92 | 1.50 | 3.70% | 64 | 39.4 bps | 71.88% |
| VALIDATION | 0.15% | 0.05% | 1.13 | 0.07 | 0.09 | 1.37% | 4 | 3.8 bps | 75.00% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.52, positive windows 66.67%, efficiency 0.46; expanding OOS Sharpe 0.66

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 4.48%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.77, x3: SR 0.72, latency_plus1: SR 0.79, entry_shift_+1: SR 0.77, entry_shift_+2: SR 0.85

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 73.33%

**Overfitting risk:** deflated Sharpe probability 0.262 (after 8271 trials); PBO 0.46; IS->OOS Sharpe ratio 0.08

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | FAIL | {"sharpe": 0.07423728062676752, "pf": 1.130683817505693, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 68 | >= 40 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.5158406881865908, "positive_windows": 0.666 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.772 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.723 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.790 | SR>0 |
| entry_displacement | reject | PASS | [0.7704029319054764, 0.8546857928957089] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.733 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.372 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.203 | > 0 |
| other_regimes | reject | PASS | 0.574 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.531 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.018596543911067045, "phase1": 0.01184530145901 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.262 | >= 0.95 |
| probability_backtest_overfitting | overfit | PASS | 0.460 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** out_of_sample_validation: Does it work out of sample (VALIDATION, thresholds from TRAIN)? -> value {'sharpe': 0.07423728062676752, 'pf': 1.130683817505693, 'trades': 4} vs SR>0, PF>1, >=5 trades; deflated_sharpe: Is the train Sharpe significant after 8271 trials? -> value 0.26244518490688185 vs >= 0.95

### Strategy #2 - STR-000531 - **REJECTED**

**Rules:** SHORT when dow == 4 AND skew_20 in bottom 20%; exit after 8 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 8 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 1.61

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 27.38% | 2.04% | 1.55 | 0.77 | 1.23 | 4.82% | 232 | 10.4 bps | 56.47% |
| VALIDATION | 0.63% | 0.21% | 1.07 | 0.13 | 0.19 | 2.57% | 68 | 0.9 bps | 57.35% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.41, positive windows 83.33%, efficiency 0.42; expanding OOS Sharpe 0.57

**Monte Carlo:** P(loss) under trade bootstrap 0.30%, 95th pct max DD 9.41%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.48, x3: SR 0.29, latency_plus1: SR 0.70, entry_shift_+1: SR 0.70, entry_shift_+2: SR 0.48

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 66.67%

**Overfitting risk:** deflated Sharpe probability 0.120 (after 8271 trials); PBO 0.85; IS->OOS Sharpe ratio 0.17

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.13057692632139192, "pf": 1.073414523380154, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 300 | >= 40 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.4053210473631192, "positive_windows": 0.833 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.483 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.291 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.703 | SR>0 |
| entry_displacement | reject | PASS | [0.7032960329896062, 0.48402346804021495] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.667 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.922 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.213 | > 0 |
| other_regimes | reject | PASS | 0.745 | <= 85% from one regime |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.5504199624939551, "phase1": 0.4927182808946894} | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.003 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.120 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.849 | <= 0.5 |

**Why it is ranked here:** passed 16 of 19 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.9215654785577466 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 8271 trials? -> value 0.11990423246181697 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.8492063492063492 vs <= 0.5

### Strategy #3 - STR-000547 - **REJECTED**

**Rules:** SHORT when x_vix_z250 in top 10% AND zdist_60 in top 20%; exit after 10 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 10 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 1.57

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 13.89% | 1.09% | 1.88 | 0.60 | 0.91 | 4.03% | 94 | 13.8 bps | 62.77% |
| VALIDATION | 0.31% | 0.10% | 1.06 | 0.08 | 0.12 | 2.14% | 33 | 0.9 bps | 51.52% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.62, positive windows 83.33%, efficiency 0.79; expanding OOS Sharpe 0.48

**Monte Carlo:** P(loss) under trade bootstrap 2.80%, 95th pct max DD 6.52%; random-entry test p = 0.010

**Stress tests:** x2: SR 0.41, x3: SR 0.30, latency_plus1: SR 0.52, entry_shift_+1: SR 0.53, entry_shift_+2: SR 0.52

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 73.33%

**Overfitting risk:** deflated Sharpe probability 0.039 (after 8271 trials); PBO 0.86; IS->OOS Sharpe ratio 0.13

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.07966926916402302, "pf": 1.0605469261261011, "t | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 127 | >= 40 |
| beats_random_entries | reject | PASS | 0.010 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.6210094207074136, "positive_windows": 0.833 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.406 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.296 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.520 | SR>0 |
| entry_displacement | reject | PASS | [0.526361718660361, 0.5247160465933302] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.733 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.688 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.107 | > 0 |
| other_regimes | reject | PASS | 0.626 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.468 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.2592215406510367, "phase1": 0.41180826260983866 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.028 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.039 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.857 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.6882399740289278 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 8271 trials? -> value 0.038890739271811844 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.8571428571428571 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- deflated_sharpe: 30
- out_of_sample_validation: 28
- probability_backtest_overfitting: 25
- few_trades_dependence: 24
- schedule_dependence: 4
- walk_forward: 3
- other_regimes: 1
- spread_slippage_x2: 1
- other_years: 1

Final status of all 30 examined strategies: {'REJECTED': 30}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-10-01 01:00:00+00:00, horizon 1 bars. Conditions: hour in quintile 5/5 (current value 21); close_loc in quintile 2/5 (current value 0.2358); ret_1 in quintile 2/5 (current value -0.0002869); regime == 3
Sample size 323 (2005-03-15 to 2026-09-29).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.0327% | 32.2% | 27.3%-37.5% | 35.7% |
| B_flat | within +/-0.0327% | 40.2% | 35.0%-45.7% | 28.7% |
| C_down | < -0.0327% | 27.6% | 23.0%-32.7% | 35.7% |

Test vs baseline: p = 0.000 -> conditions are informative.
Invalidated if: hour leaves quintile 5; close_loc leaves quintile 2; ret_1 leaves quintile 2; regime changes

- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- validation/evaluate: 30

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
