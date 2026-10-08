# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 30 candidate strategies examined; none survived. Outcome: {'REJECTED': 26, 'OVERFIT': 4}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00011 |
| Asset | XAUUSD_D1 |
| Timeframe | 1D |
| Historical period | 2008-01-01 22:00:00+00:00 to 2026-09-30 21:00:00+00:00 (4850 bars) |
| Data capabilities | ohlc, volume |
| Dataset version | fbb372e75435ab65 |
| Mode / budget used | standard - 12 experiments, 30 strategies examined, 1.56 min |
| Backtests counted as trials (all runs on this dataset) | 6153 |

**Splits** (chronological, embargoed): TRAIN 2008-01-01 to 2018-12-31 (2850 bars); VALIDATION 2019-01-30 to 2020-12-31 (497 bars); TEST 2021-02-01 to 2022-12-30 (496 bars); FINAL 2023-01-31 to 2026-09-30 (947 bars)

## Data

- provenance: {'from': 'XAUUSD_H1 (dukascopy_candles(instrument=XAUUSD, start=2008-01-01, end=2026-10-01, granularity=hour, point=0.001))', 'base_sha256': 'b98525cfe3f0495138cbda4b8385986a47a17d1e9b6966c32231388f0b42ed8e', 'base_notes': ["provenance: {'bid_files': 225, 'bid_missing_periods': [], 'ask_files': 225, 'ask_missing_periods': [], 'bars': 112933, 'flat_zero_volume_dropped': 51419, 'spread_median': 0.36599999999998545, 'volume': 'Dukascopy tick volume (not exchange volume)', 'seconds': 0.7, 'field_order': 'open,close,low,high (verified by checks)'}", 'per-bar spread available (median 0.366)', "cross-check vs None: {'kind': 'monthly_mean', 'matches': 225, 'median_abs_diff_pct': 0.07114135929859877, 'p95_abs_diff_pct': 0.34121201481908325, 'return_corr': 0.9979318298761235, 'note': 'monthly-average check: does not verify intraday timestamps', 'status': 'PASSED'}"], 'sessions': 4856, 'short_sessions_dropped': 6, 'session_close': '17:00 America/New_York', 'median_bars_per_session': 23.0}
- per-bar spread available (median 0.392542)
- Quality OK: 4850 raw rows -> 4850 bars; 0 missing (holidays/no fix), 0 duplicates, 0 corrupt, 0 bad prints removed, gaps 0
- Exogenous `us_cpi_yoy`: OK - US CPI-U YoY (BLS). Conservative 35-day publication lag. (lag 35 days)
- Exogenous `us_10y_yield`: OK - US 10Y yield, monthly average (Fed H.15). Known at month end. (lag 1 days)
- Exogenous `vix`: OK - CBOE VIX close (16:15 NY). Usable from the end of its New York day (i.e. from the next session). (lag 0 days)
- Exogenous `brent`: OK - Brent spot (EIA). Usable from the next New York day. (lag 1 days)

## Market discoveries

63 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 2.**

- **arch_lm_5** - Engle ARCH-LM(5): volatility clustering; effect = R^2: effect 0.03122, p=0.00000, q=0.0000, replication p=0.00067 (n=2844)
- **ljung_box_abs_20** - Ljung-Box(20) on |returns|; effect = lag-1 acf of |r|: effect 0.13340, p=0.00000, q=0.0000, replication p=0.00000 (n=2849)
- Descriptive - return_distribution_train: Per-bar log return distribution {"mean_bps": 1.513496106425743, "ann_vol": 0.18126517705206954, "skew": -0.22959878172670858, "excess_kurtosis": 7.281267448214393, "jarque_bera_p": 0.0, "n": 2849}
- Descriptive - return_distribution_validation: Per-bar log return distribution {"mean_bps": 7.438000786424907, "ann_vol": 0.16113530927623784, "skew": -0.6514044258511722, "excess_kurtosis": 5.232245711256137, "jarque_bera_p": 1.830609075109666e-131, "n": 497}
- Descriptive - trend_episode_duration: Directional-change episodes (threshold 0.0597 log) vs 200 shuffled-return paths (TRAIN) {"episodes": 67, "mean_duration": 40.298507462686565, "median_duration": 28.0, "shuffled_mean_duration": 46.13960272597369, "p_longer_than_shuffled": 0.9203980099502488}
- Descriptive - regime_model: GMM regimes on TRAIN, k=3 chosen by BIC {"labels": {"0": "R0: high-vol trending contracting", "1": "R1: high-vol ranging", "2": "R2: low-vol trending contracting"}, "persistence": {"0": 0.7581699346405228, "1": 0.8175732217573222, "2": 0.8433451118963486}, "occupancy": {"0": 0.2722419928825623, "1": 0.42526690391459077, "2": 0.302491103202847}}
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

1545 hypotheses (1545 new, 0 reused from memory). Status counts: {'REJECTED': 1545}

No hypothesis survived FDR on the discovery window **and** confirmation on the inner holdout.

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 0 | 0 | evidence insufficient: no hypothesis survived FDR + inner-holdout confirmation |
| open_exploration | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| regime_conditioned | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| macro_conditioned | STOPPED | 2 | 10 | budget: max_strategies (30) examined |

## Top strategies

### Strategy #1 - STR-000389 - **OVERFIT**

**Rules:** LONG when x_us_cpi_yoy_chg63 in bottom 15%; exit after 10 bars, stop 1.5 x vol x sqrt(hold)

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 10 bars, or stop at 1.5 x vol x sqrt(hold)
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 3.57

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 61.70% | 4.46% | 2.30 | 0.62 | 0.94 | 12.39% | 44 | 109.2 bps | 72.73% |
| VALIDATION | 18.31% | 9.15% | 3.29 | 1.39 | 2.15 | 3.80% | 9 | 186.8 bps | 66.67% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.47, positive windows 66.67%, efficiency 0.80; expanding OOS Sharpe 0.43

**Monte Carlo:** P(loss) under trade bootstrap 1.10%, 95th pct max DD 19.79%; random-entry test p = 0.004

**Stress tests:** x2: SR 0.68, x3: SR 0.64, latency_plus1: SR 0.72, entry_shift_+1: SR 0.73, entry_shift_+2: SR 0.74

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 61.54%

**Overfitting risk:** deflated Sharpe probability 0.044 (after 6153 trials); PBO 0.67; IS->OOS Sharpe ratio 2.26

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.388363860991918, "pf": 3.2900236599965935, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 53 | >= 30 |
| beats_random_entries | reject | PASS | 0.004 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.470334546864355, "positive_windows": 0.6666 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.678 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.639 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.724 | SR>0 |
| entry_displacement | reject | PASS | [0.733960327143765, 0.7404856045372495] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.615 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.401 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.520 | > 0 |
| other_regimes | reject | PASS | 0.553 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.286 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.34961465102608613, "phase1": 0.4414851794185298 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.011 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.044 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.675 | <= 0.5 |

**Why it is ranked here:** passed 18 of 20 decisive/informative attacks.

**Why it might fail:** deflated_sharpe: Is the train Sharpe significant after 6153 trials? -> value 0.04403571932720516 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.6746031746031746 vs <= 0.5

### Strategy #2 - STR-000388 - **OVERFIT**

**Rules:** LONG when x_us_cpi_yoy_chg63 in bottom 15%; exit after 10 bars, stop 2.0 x vol x sqrt(hold)

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 10 bars, or stop at 2.0 x vol x sqrt(hold)
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 3.50

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 59.54% | 4.33% | 2.26 | 0.60 | 0.91 | 12.79% | 43 | 108.6 bps | 74.42% |
| VALIDATION | 18.67% | 9.32% | 3.43 | 1.35 | 2.00 | 4.95% | 9 | 190.2 bps | 66.67% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.43, positive windows 66.67%, efficiency 0.81; expanding OOS Sharpe 0.37

**Monte Carlo:** P(loss) under trade bootstrap 0.70%, 95th pct max DD 22.82%; random-entry test p = 0.004

**Stress tests:** x2: SR 0.66, x3: SR 0.63, latency_plus1: SR 0.68, entry_shift_+1: SR 0.72, entry_shift_+2: SR 0.71

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 69.23%

**Overfitting risk:** deflated Sharpe probability 0.039 (after 6153 trials); PBO 0.67; IS->OOS Sharpe ratio 2.26

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.3549033370435233, "pf": 3.434772298749283, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 52 | >= 30 |
| beats_random_entries | reject | PASS | 0.004 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.43332483995780813, "positive_windows": 0.66 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.665 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.627 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.681 | SR>0 |
| entry_displacement | reject | PASS | [0.7207594160684695, 0.7055658180198207] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.692 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.407 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.509 | > 0 |
| other_regimes | reject | PASS | 0.489 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.314 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.34923327205855, "phase1": 0.4283851091904199} | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.007 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.039 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.675 | <= 0.5 |

**Why it is ranked here:** passed 18 of 20 decisive/informative attacks.

**Why it might fail:** deflated_sharpe: Is the train Sharpe significant after 6153 trials? -> value 0.03921739121176444 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.6746031746031746 vs <= 0.5

### Strategy #3 - STR-000409 - **REJECTED**

**Rules:** LONG when volume_z in bottom 10% AND regime == 2; exit after 5 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 5 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 3.44

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 16.26% | 1.38% | 1.67 | 0.38 | 0.57 | 9.96% | 42 | 35.9 bps | 61.90% |
| VALIDATION | 12.26% | 6.21% | 4.74 | 1.43 | 2.40 | 4.36% | 10 | 115.7 bps | 80.00% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.42, positive windows 66.67%, efficiency 0.51; expanding OOS Sharpe -0.02

**Monte Carlo:** P(loss) under trade bootstrap 3.20%, 95th pct max DD 13.38%; random-entry test p = 0.118

**Stress tests:** x2: SR 0.49, x3: SR 0.43, latency_plus1: SR 0.51, entry_shift_+1: SR 0.58, entry_shift_+2: SR 0.73

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 53.85%

**Overfitting risk:** deflated Sharpe probability 0.006 (after 6153 trials); PBO 0.93; IS->OOS Sharpe ratio 3.78

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.4281937005308531, "pf": 4.7359734036614745, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 52 | >= 30 |
| beats_random_entries | reject | FAIL | 0.118 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.41544855221801585, "positive_windows": 0.66 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.493 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.434 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.513 | SR>0 |
| entry_displacement | reject | PASS | [0.576067802909348, 0.7346247809261814] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.538 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.586 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.181 | > 0 |
| schedule_dependence | reject | PASS | 0.311 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.3999819471985261, "phase1": 0.33113423374050127 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.032 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.006 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.929 | <= 0.5 |

**Why it is ranked here:** passed 15 of 19 decisive/informative attacks.

**Why it might fail:** beats_random_entries: Does its timing beat random entries with the same exits and costs? -> value 0.11776447105788423 vs p < 0.05; few_trades_dependence: Does profit depend on a handful of trades? -> value 0.5862661363573983 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 6153 trials? -> value 0.006108208887422577 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.9285714285714286 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- deflated_sharpe: 30
- probability_backtest_overfitting: 25
- few_trades_dependence: 24
- beats_random_entries: 12
- out_of_sample_validation: 6
- schedule_dependence: 3
- walk_forward: 2
- latency_plus1: 1
- monte_carlo_loss_probability: 1
- other_years: 1

Final status of all 30 examined strategies: {'OVERFIT': 4, 'REJECTED': 26}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-09-30 21:00:00+00:00, horizon 5 bars. Conditions: vol_20 in quintile 5/5 (current value -4.25); ret_20 in quintile 1/5 (current value -0.05374); zdist_60 in quintile 2/5 (current value -0.2247); regime == 0
Sample size 80 (2008-03-20 to 2026-04-15).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.6983% | 41.2% | 31.1%-52.2% | 40.4% |
| B_flat | within +/-0.6983% | 20.0% | 12.7%-30.0% | 27.2% |
| C_down | < -0.6983% | 38.8% | 28.8%-49.7% | 32.4% |

Test vs baseline: p = 0.776 -> NOT informative.
Invalidated if: vol_20 leaves quintile 5; ret_20 leaves quintile 1; zdist_60 leaves quintile 2; regime changes

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
