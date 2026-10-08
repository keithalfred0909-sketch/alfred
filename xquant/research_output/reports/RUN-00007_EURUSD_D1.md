# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 30 candidate strategies examined; none survived. Outcome: {'REJECTED': 30}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00007 |
| Asset | EURUSD_D1 |
| Timeframe | 1D |
| Historical period | 2005-01-03 22:00:00+00:00 to 2026-09-30 21:00:00+00:00 (5652 bars) |
| Data capabilities | ohlc, volume |
| Dataset version | 154fc3321be0403c |
| Mode / budget used | standard - 12 experiments, 30 strategies examined, 1.98 min |
| Backtests counted as trials (all runs on this dataset) | 12916 |

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

400 candidate features, 1980 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **0** []
Status counts: {'REJECTED': 1980}

## Top hypotheses

1545 hypotheses (0 new, 1545 reused from memory). Status counts: {'REJECTED': 1545}

No hypothesis survived FDR on the discovery window **and** confirmation on the inner holdout.

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 0 | 0 | evidence insufficient: no hypothesis survived FDR + inner-holdout confirmation |
| open_exploration | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| regime_conditioned | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| macro_conditioned | STOPPED | 2 | 10 | budget: max_strategies (30) examined |

## Top strategies

### Strategy #1 - STR-000165 - **REJECTED**

**Rules:** LONG when fromhigh_250 in bottom 5%; exit after 2 bars, take-profit 2.0 x vol x sqrt(hold)

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 2 bars, or take-profit at 2.0 x vol x sqrt(hold)
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 2.38

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 18.78% | 1.73% | 2.09 | 0.63 | 1.09 | 6.72% | 53 | 32.5 bps | 60.38% |
| VALIDATION | 11.57% | 2.84% | 1.61 | 0.67 | 1.05 | 8.80% | 45 | 24.3 bps | 55.56% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.28, positive windows 83.33%, efficiency 0.75; expanding OOS Sharpe 0.26

**Monte Carlo:** P(loss) under trade bootstrap 3.70%, 95th pct max DD 13.60%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.40, x3: SR 0.33, latency_plus1: SR 0.30, entry_shift_+1: SR 0.23, entry_shift_+2: SR 0.06

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 50.00%

**Overfitting risk:** deflated Sharpe probability 0.021 (after 12916 trials); PBO 0.70; IS->OOS Sharpe ratio 1.06

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.6688767294590992, "pf": 1.6149643910171707, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 105 | >= 30 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.28375740524952875, "positive_windows": 0.83 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.397 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.330 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.303 | SR>0 |
| entry_displacement | reject | PASS | [0.23228248048521455, 0.05659584677572449] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.500 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.640 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.163 | > 0 |
| other_regimes | reject | PASS | 0.437 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.412 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.11931651229186432, "phase1": -0.16698903235499 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.037 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.021 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.698 | <= 0.5 |

**Why it is ranked here:** passed 16 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.6399352626889296 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 12916 trials? -> value 0.02123027527275717 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.6984126984126984 vs <= 0.5

### Strategy #2 - STR-000163 - **REJECTED**

**Rules:** LONG when fromhigh_250 in bottom 5%; exit after 2 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 2 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 1  |  Composite score: 2.28

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 22.35% | 2.04% | 2.39 | 0.67 | 1.25 | 7.26% | 52 | 38.8 bps | 61.54% |
| VALIDATION | 9.00% | 2.23% | 1.48 | 0.47 | 0.76 | 8.80% | 42 | 20.5 bps | 54.76% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.40, positive windows 83.33%, efficiency 0.77; expanding OOS Sharpe 0.18

**Monte Carlo:** P(loss) under trade bootstrap 2.70%, 95th pct max DD 13.19%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.40, x3: SR 0.34, latency_plus1: SR 0.38, entry_shift_+1: SR 0.37, entry_shift_+2: SR 0.23

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 50.00%

**Overfitting risk:** deflated Sharpe probability 0.023 (after 12916 trials); PBO 0.70; IS->OOS Sharpe ratio 0.71

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.47382912777825703, "pf": 1.4816270201581634, "t | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 101 | >= 30 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.39562063824200294, "positive_windows": 0.83 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.403 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.344 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.384 | SR>0 |
| entry_displacement | reject | PASS | [0.3685560189436053, 0.2337257120936204] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.500 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.777 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.175 | > 0 |
| other_regimes | reject | PASS | 0.555 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.447 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.20231666650541627, "phase1": -0.15263602964208 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.027 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.023 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.698 | <= 0.5 |

**Why it is ranked here:** passed 16 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.776609117568766 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 12916 trials? -> value 0.02304856895194993 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.6984126984126984 vs <= 0.5

### Strategy #3 - STR-000161 - **REJECTED**

**Rules:** LONG when fromhigh_250 in bottom 10%; exit after 2 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 2 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 1  |  Composite score: 1.87

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 30.94% | 2.73% | 2.03 | 0.76 | 1.32 | 7.31% | 93 | 29.0 bps | 58.06% |
| VALIDATION | 6.07% | 1.52% | 1.28 | 0.31 | 0.48 | 8.80% | 50 | 11.8 bps | 48.00% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.04, positive windows 50.00%, efficiency 0.10; expanding OOS Sharpe 0.04

**Monte Carlo:** P(loss) under trade bootstrap 4.00%, 95th pct max DD 16.34%; random-entry test p = 0.004

**Stress tests:** x2: SR 0.39, x3: SR 0.31, latency_plus1: SR 0.31, entry_shift_+1: SR 0.48, entry_shift_+2: SR 0.38

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 64.29%

**Overfitting risk:** deflated Sharpe probability 0.052 (after 12916 trials); PBO 0.70; IS->OOS Sharpe ratio 0.41

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.30891801713187406, "pf": 1.2812942454136118, "t | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 150 | >= 30 |
| beats_random_entries | reject | PASS | 0.004 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.035338341252650986, "positive_windows": 0.5 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.389 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.310 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.308 | SR>0 |
| entry_displacement | reject | PASS | [0.48109246181384574, 0.37898407481782287] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.643 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.955 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.193 | > 0 |
| other_regimes | reject | PASS | 0.608 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.525 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.1751027613664327, "phase1": -0.233963063683189 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.040 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.052 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.698 | <= 0.5 |

**Why it is ranked here:** passed 16 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.9553837397595223 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 12916 trials? -> value 0.05185413995205003 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.6984126984126984 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- deflated_sharpe: 30
- few_trades_dependence: 25
- probability_backtest_overfitting: 25
- out_of_sample_validation: 21
- beats_random_entries: 6
- walk_forward: 5
- schedule_dependence: 4
- other_years: 3
- other_regimes: 2
- monte_carlo_loss_probability: 2
- single_event_dependence: 1

Final status of all 30 examined strategies: {'REJECTED': 30}

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

- validation/evaluate: 30

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
