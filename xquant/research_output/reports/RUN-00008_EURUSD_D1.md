# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 80 candidate strategies examined; none survived. Outcome: {'REJECTED': 69, 'OVERFIT': 11}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00008 |
| Asset | EURUSD_D1 |
| Timeframe | 1D |
| Historical period | 2005-01-03 22:00:00+00:00 to 2026-09-30 21:00:00+00:00 (5652 bars) |
| Data capabilities | ohlc, volume |
| Dataset version | 154fc3321be0403c |
| Mode / budget used | deep - 23 experiments, 80 strategies examined, 12.18 min |
| Backtests counted as trials (all runs on this dataset) | 147456 |

**Splits** (chronological, embargoed): TRAIN 2005-01-03 to 2014-12-31 (2604 bars); VALIDATION 2015-01-30 to 2018-12-31 (1017 bars); TEST 2019-01-30 to 2022-12-30 (1019 bars); FINAL 2023-01-30 to 2026-09-30 (952 bars)

## Data

- provenance: {'from': 'EURUSD_H1 (dukascopy_candles(instrument=EURUSD, start=2005-01-01, end=2026-10-01, granularity=hour, point=1e-05))', 'base_sha256': 'b4364e784525f919143a9b2624500b75ef9cd1e1feaf30079f1feb5b24320971', 'base_notes': ["provenance: {'bid_files': 261, 'bid_missing_periods': [], 'ask_files': 261, 'ask_missing_periods': [], 'bars': 135749, 'flat_zero_volume_dropped': 54883, 'spread_median': 4.999999999988347e-05, 'volume': 'Dukascopy tick volume (not exchange volume)', 'seconds': 0.7, 'field_order': 'open,close,low,high (verified by checks)'}", 'per-bar spread available (median 5e-05)', "cross-check vs EURUSD: {'matches': 5445, 'median_abs_diff_bps': 0.6749699999986092, 'p95_abs_diff_bps': 2.350823999998975, 'return_corr': 0.9978510238484267, 'local_time': '12:00', 'tz': 'America/New_York', 'median_abs_diff_bps_shift-1h': 6.857475000001667, 'median_abs_diff_bps_shift+1h': 5.440820000000568, 'status': 'PASSED'}"], 'sessions': 5667, 'short_sessions_dropped': 15, 'session_close': '17:00 America/New_York', 'median_bars_per_session': 24.0}
- per-bar spread available (median 5.60417e-05)
- Quality OK: 5652 raw rows -> 5652 bars; 0 missing (holidays/no fix), 0 duplicates, 0 corrupt, 0 bad prints removed, gaps 0
- Exogenous `us_cpi_yoy`: OK - US CPI-U YoY (BLS). Conservative 35-day publication lag. (lag 35 days)
- Exogenous `us_10y_yield`: OK - US 10Y yield, monthly average (Fed H.15). Known at month end. (lag 1 days)
- Exogenous `vix`: OK - CBOE VIX close (16:15 NY). Usable from the end of its New York day (i.e. from the next session). (lag 0 days)
- Exogenous `brent`: OK - Brent spot (EIA). Usable from the next New York day. (lag 1 days)

## Market discoveries

63 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 2.**

- **arch_lm_5** - Engle ARCH-LM(5): volatility clustering; effect = R^2: effect 0.07582, p=0.00000, q=0.0000, replication p=0.00001 (n=2598)
- **ljung_box_abs_20** - Ljung-Box(20) on |returns|; effect = lag-1 acf of |r|: effect 0.12398, p=0.00000, q=0.0000, replication p=0.00000 (n=2603)
- Not replicated: zdist20_low_fwd20 (train p=0.00096, validation p=0.1477)
- Descriptive - return_distribution_train: Per-bar log return distribution {"mean_bps": -0.4106134928658655, "ann_vol": 0.09841442479061191, "skew": 0.08723897436158556, "excess_kurtosis": 1.9635659211007495, "jarque_bera_p": 3.0085564856670596e-92, "n": 2603}
- Descriptive - return_distribution_validation: Per-bar log return distribution {"mean_bps": 0.1263927057051802, "ann_vol": 0.08932771191185823, "skew": 0.16173508145271634, "excess_kurtosis": 2.1660919785319157, "jarque_bera_p": 7.305544098074e-45, "n": 1017}
- Descriptive - trend_episode_duration: Directional-change episodes (threshold 0.0362 log) vs 200 shuffled-return paths (TRAIN) {"episodes": 40, "mean_duration": 59.925, "median_duration": 36.0, "shuffled_mean_duration": 51.24682903418777, "p_longer_than_shuffled": 0.0945273631840796}
- Descriptive - regime_model: GMM regimes on TRAIN, k=3 chosen by BIC {"labels": {"0": "R0: low-vol trending contracting", "1": "R1: high-vol ranging", "2": "R2: high-vol trending"}, "persistence": {"0": 0.6429980276134122, "1": 0.8355817875210793, "2": 0.8114942528735632}, "occupancy": {"0": 0.1981279251170047, "1": 0.4625585023400936, "2": 0.33931357254290173}}
- INSUFFICIENT DATA for: hour_of_day, minute, session_open_close, intraday_seasonality

## Macro discoveries

32 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- Descriptive - macro_data_limits: Macro series are latest-vintage (revised) values with conservative publication lags; no consensus data => no surprise analysis {}
- INSUFFICIENT DATA for: CPI, PCE, NFP, Unemployment rate, Average hourly earnings, GDP, PMI, Fed rate decision, ECB rate decision, Central bank statements

## News discoveries

0 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- INSUFFICIENT DATA for: news_predictive_power

## Feature discovery

1500 candidate features, 7480 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **0** []
Status counts: {'REJECTED': 7480}

## Top hypotheses

1545 hypotheses (0 new, 1545 reused from memory). Status counts: {'REJECTED': 1545}

No hypothesis survived FDR on the discovery window **and** confirmation on the inner holdout.

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 0 | 0 | evidence insufficient: no hypothesis survived FDR + inner-holdout confirmation |
| open_exploration | STOPPED | 6 | 30 | no improvement / repeated failure (6 runs) |
| regime_conditioned | STOPPED | 6 | 27 | no improvement / repeated failure (6 runs) |
| macro_conditioned | STOPPED | 5 | 23 | budget: max_strategies (80) examined |

## Top strategies

### Strategy #1 - STR-000221 - **OVERFIT**

**Rules:** SHORT when ret_2 in top 10% AND volratio_10_120 in top 15%; exit after 2 bars, take-profit 1.0 x vol x sqrt(hold)

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 2 bars, or take-profit at 1.0 x vol x sqrt(hold)
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 3.27

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 25.11% | 2.26% | 5.09 | 1.06 | 2.21 | 2.34% | 37 | 60.6 bps | 75.68% |
| VALIDATION | 5.57% | 1.40% | 7.40 | 0.92 | 2.09 | 1.43% | 11 | 49.3 bps | 81.82% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 1.02, positive windows 100.00%, efficiency 0.94; expanding OOS Sharpe 1.00

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 2.84%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.99, x3: SR 0.95, latency_plus1: SR 0.47, entry_shift_+1: SR 0.53, entry_shift_+2: SR 0.40

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 71.43%

**Overfitting risk:** deflated Sharpe probability 0.095 (after 147456 trials); PBO 0.75; IS->OOS Sharpe ratio 0.86

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.9151303925500961, "pf": 7.400916054727444, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 49 | >= 30 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 1.0187080257295773, "positive_windows": 1.0} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.992 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.946 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.472 | SR>0 |
| entry_displacement | reject | PASS | [0.5284732711366351, 0.4011706730016022] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.714 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.196 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.237 | > 0 |
| other_regimes | reject | PASS | 0.789 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.307 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": 0.19067262138160962, "phase1": -0.285982394407571 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.095 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.746 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** deflated_sharpe: Is the train Sharpe significant after 147456 trials? -> value 0.09540302233997838 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.746031746031746 vs <= 0.5

### Strategy #2 - STR-000222 - **OVERFIT**

**Rules:** SHORT when ret_2 in top 10% AND volratio_10_120 in top 15%; exit after 1 bars, take-profit 1.0 x vol x sqrt(hold)

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 1 bars, or take-profit at 1.0 x vol x sqrt(hold)
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 3.03

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 22.11% | 2.01% | 5.81 | 1.12 | 2.42 | 1.92% | 41 | 48.7 bps | 82.93% |
| VALIDATION | 3.61% | 0.91% | 3.78 | 0.75 | 1.68 | 1.27% | 12 | 29.6 bps | 58.33% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 1.01, positive windows 100.00%, efficiency 0.89; expanding OOS Sharpe 1.02

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 2.42%; random-entry test p = 0.002

**Stress tests:** x2: SR 1.00, x3: SR 0.94, latency_plus1: SR 0.54, entry_shift_+1: SR 0.50, entry_shift_+2: SR 0.33

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 57.14%

**Overfitting risk:** deflated Sharpe probability 0.134 (after 147456 trials); PBO 0.75; IS->OOS Sharpe ratio 0.68

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.7548282987993424, "pf": 3.77696491398302, "trad | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 54 | >= 30 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 1.00988693759463, "positive_windows": 1.0} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.995 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.938 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.536 | SR>0 |
| entry_displacement | reject | PASS | [0.5036316836694937, 0.32669983031843425] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.571 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.172 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.196 | > 0 |
| other_regimes | reject | PASS | 0.725 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.337 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": 0.19067262138160962, "phase1": -0.285982394407571 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.134 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.746 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** deflated_sharpe: Is the train Sharpe significant after 147456 trials? -> value 0.13447505542505533 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.746031746031746 vs <= 0.5

### Strategy #3 - STR-000212 - **OVERFIT**

**Rules:** SHORT when volume_z in bottom 20% AND x_brent_chg20 in bottom 30%; exit after 3 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 3 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 2.56

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 33.08% | 2.90% | 2.65 | 0.93 | 1.57 | 3.58% | 69 | 41.4 bps | 59.42% |
| VALIDATION | 6.64% | 1.66% | 1.56 | 0.51 | 0.70 | 6.85% | 26 | 24.7 bps | 61.54% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.95, positive windows 100.00%, efficiency 0.88; expanding OOS Sharpe 0.91

**Monte Carlo:** P(loss) under trade bootstrap 0.10%, 95th pct max DD 9.64%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.78, x3: SR 0.71, latency_plus1: SR 0.52, entry_shift_+1: SR 0.71, entry_shift_+2: SR 0.51

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 78.57%

**Overfitting risk:** deflated Sharpe probability 0.055 (after 147456 trials); PBO 0.90; IS->OOS Sharpe ratio 0.54

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.5051038644720741, "pf": 1.5557465342031378, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 96 | >= 30 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.946839699586444, "positive_windows": 1.0} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.781 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.714 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.523 | SR>0 |
| entry_displacement | reject | PASS | [0.7075877642262448, 0.514949407812075] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.786 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.409 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.321 | > 0 |
| other_regimes | reject | PASS | 0.507 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.377 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.26576703677949354, "phase1": 0.1167143827901141 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.001 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.055 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.905 | <= 0.5 |

**Why it is ranked here:** passed 18 of 20 decisive/informative attacks.

**Why it might fail:** deflated_sharpe: Is the train Sharpe significant after 147456 trials? -> value 0.05513170735117458 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.9047619047619048 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- deflated_sharpe: 80
- probability_backtest_overfitting: 80
- out_of_sample_validation: 63
- few_trades_dependence: 27
- walk_forward: 1
- entry_displacement: 1
- schedule_dependence: 1

Final status of all 80 examined strategies: {'OVERFIT': 11, 'REJECTED': 69}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-09-30 21:00:00+00:00, horizon 5 bars. Conditions: vol_20 in quintile 1/5 (current value -6.027); ret_20 in quintile 1/5 (current value -0.02258); zdist_60 in quintile 1/5 (current value -0.7528); regime == 2
Sample size 63 (2007-06-12 to 2026-09-23).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.3539% | 33.3% | 22.9%-45.6% | 36.8% |
| B_flat | within +/-0.3539% | 36.5% | 25.7%-48.9% | 26.3% |
| C_down | < -0.3539% | 30.2% | 20.2%-42.4% | 36.9% |

Test vs baseline: p = 0.707 -> NOT informative.
Invalidated if: vol_20 leaves quintile 1; ret_20 leaves quintile 1; zdist_60 leaves quintile 1; regime changes

- No validated predictive condition exists; conditioning uses generic context variables (volatility, recent return, distance to mean) only.
- Conditional frequencies are not significantly different from the unconditional baseline: the current conditions carry no demonstrated information about the next move.
- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- validation/evaluate: 80

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
