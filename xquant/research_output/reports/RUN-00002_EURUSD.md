# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 80 candidate strategies examined; none survived. Outcome: {'REJECTED': 59, 'OVERFIT': 21}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00002 |
| Asset | EURUSD |
| Timeframe | 1D |
| Historical period | 1999-01-04 17:00:00+00:00 to 2026-09-25 16:00:00+00:00 (6955 bars) |
| Data capabilities | close only |
| Dataset version | 35fd595cefb7190d |
| Mode / budget used | deep - 22 experiments, 80 strategies examined, 9.88 min |
| Backtests counted as trials (all runs on this dataset) | 112732 |

**Splits** (chronological, embargoed): TRAIN 1999-01-04 to 2014-12-31 (4022 bars); VALIDATION 2015-02-02 to 2018-12-31 (980 bars); TEST 2019-02-01 to 2022-12-30 (978 bars); FINAL 2023-02-01 to 2026-09-25 (915 bars)

## Data

- provenance: {'url': 'https://raw.githubusercontent.com/datasets/exchange-rates/main/data/daily.csv', 'raw_sha256': '944c4937703177bdc5e82ced55b6e50ffcd1f89fef4bbca29785ac7cce8bd6c4', 'rows': 7235, 'downloaded_at': '2026-10-03T23:03:58+00:00', 'filter': {'Country': 'Euro'}, 'snapshot_sha256': '4461d00d0c4fde0091213c99616baeb807ee43b31375d6a60d00f513c8df2166', 'used_snapshot': True, 'orientation': 'inverted (published 0.8466 on 1999-01-04, anchor 1.1812)'}
- close-only data: no open/high/low; intrabar stops and range features unavailable
- no volume data
- Quality OK: 7235 raw rows -> 6955 bars; 280 missing (holidays/no fix), 0 duplicates, 0 corrupt, 0 bad prints removed, gaps 4
- Exogenous `us_cpi_yoy`: OK - US CPI-U all items (BLS), year-over-year %. Stamped at reference month; released ~2 weeks after month end. (lag 35 days)
- Exogenous `us_10y_yield`: OK - US 10Y Treasury yield, monthly average (Fed H.15). Known at month end. (lag 1 days)
- Exogenous `vix`: OK - CBOE VIX close. Closes after the NY noon fix, so usable from the next bar. (lag 1 days)
- Exogenous `brent`: OK - Brent spot (EIA). Usable from the next bar. (lag 1 days)

## Market discoveries

67 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 2.**

- **arch_lm_5** - Engle ARCH-LM(5): volatility clustering; effect = R^2: effect 0.03844, p=0.00000, q=0.0000, replication p=0.00049 (n=4016)
- **ljung_box_abs_20** - Ljung-Box(20) on |returns|; effect = lag-1 acf of |r|: effect 0.03021, p=0.00000, q=0.0000, replication p=0.00000 (n=4021)
- Descriptive - return_distribution_train: Per-bar log return distribution {"mean_bps": 0.06005822004823337, "ann_vol": 0.09969113726647495, "skew": 0.11549459162500492, "excess_kurtosis": 2.2438418158947284, "jarque_bera_p": 7.687324737756818e-186, "n": 4021}
- Descriptive - return_distribution_validation: Per-bar log return distribution {"mean_bps": 0.1485437864717685, "ann_vol": 0.08892521550878996, "skew": 0.11528734251390334, "excess_kurtosis": 2.0808209716589765, "jarque_bera_p": 1.3702109143328367e-39, "n": 980}
- Descriptive - trend_episode_duration: Directional-change episodes (threshold 0.0387 log) vs 200 shuffled-return paths (TRAIN) {"episodes": 54, "mean_duration": 70.72222222222223, "median_duration": 49.0, "shuffled_mean_duration": 56.3739157374933, "p_longer_than_shuffled": 0.014925373134328358}
- Descriptive - regime_model: GMM regimes on TRAIN, k=5 chosen by BIC {"labels": {"0": "R0: low-vol trending contracting", "1": "R1: high-vol ranging", "2": "R2: high-vol ranging", "3": "R3: low-vol trending contracting", "4": "R4: high-vol trending"}, "persistence": {"0": 0.5918367346938775, "1": 0.6067297581493165, "2": 0.7762762762762763, "3": 0.6553398058252428, "4": 0.7536363636363637}, "occupancy": {"0": 0.09844299347061777, "1": 0.2388247112004018, "2": 0.334
- INSUFFICIENT DATA for: hour_of_day, minute, session_open_close, intraday_seasonality, atr, gaps_open_vs_close, bar_range_structure, large_candles_body_wick, volume_liquidity

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

1470 hypotheses (0 new, 1470 reused from memory). Status counts: {'REJECTED': 1464, 'OVERFIT': 6}

No hypothesis survived FDR on the discovery window **and** confirmation on the inner holdout.

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 0 | 0 | evidence insufficient: no hypothesis survived FDR + inner-holdout confirmation |
| open_exploration | STOPPED | 6 | 30 | no improvement / repeated failure (6 runs) |
| regime_conditioned | STOPPED | 5 | 25 | budget: max_strategies (80) examined |
| macro_conditioned | STOPPED | 5 | 25 | budget: max_strategies (80) examined |

## Top strategies

### Strategy #1 - STR-000097 - **OVERFIT**

**Rules:** LONG when zdist_20 in top 15% AND x_vix_chg20 in bottom 30%; exit after 10 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 10 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 2.82

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 61.18% | 3.02% | 3.88 | 0.88 | 1.42 | 6.81% | 44 | 108.5 bps | 75.00% |
| VALIDATION | 6.48% | 1.62% | 4.51 | 0.71 | 1.24 | 4.09% | 7 | 89.7 bps | 85.71% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.40, positive windows 83.33%, efficiency 0.57; expanding OOS Sharpe 0.42

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 8.70%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.82, x3: SR 0.80, latency_plus1: SR 0.53, entry_shift_-1: SR 0.75, entry_shift_+1: SR 0.65

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 75.00%

**Overfitting risk:** deflated Sharpe probability 0.182 (after 112732 trials); PBO 0.92; IS->OOS Sharpe ratio 0.80

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.7074693667807467, "pf": 4.511844285408994, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 51 | >= 30 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.3990417909314115, "positive_windows": 0.833 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.822 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.798 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.533 | SR>0 |
| entry_displacement | reject | PASS | [0.7486657158878288, 0.6461296196316059] | SR>0 both ways |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.750 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.281 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.487 | > 0 |
| other_regimes | reject | PASS | 0.451 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.316 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.02381396014063058, "phase1": -0.22853557624018 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.182 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.921 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** deflated_sharpe: Is the train Sharpe significant after 112732 trials? -> value 0.1819710956334437 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.9206349206349206 vs <= 0.5

### Strategy #2 - STR-000055 - **OVERFIT**

**Rules:** SHORT when x_us_cpi_yoy_z250 in top 30% AND x_us_cpi_yoy_chg5 in top 10%; exit after 8 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 8 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 2.75

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 39.77% | 2.11% | 3.97 | 0.71 | 1.19 | 4.07% | 41 | 81.7 bps | 73.17% |
| VALIDATION | 8.35% | 2.08% | 2.41 | 0.64 | 1.03 | 3.90% | 13 | 61.7 bps | 69.23% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.53, positive windows 100.00%, efficiency 0.98; expanding OOS Sharpe 0.68

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 7.42%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.67, x3: SR 0.64, latency_plus1: SR 0.50, entry_shift_-1: SR 0.53, entry_shift_+1: SR 0.50

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 70.00%

**Overfitting risk:** deflated Sharpe probability 0.051 (after 112732 trials); PBO 0.86; IS->OOS Sharpe ratio 0.90

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.6399551109533734, "pf": 2.4127690265902078, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 54 | >= 30 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.5311520384075188, "positive_windows": 1.0} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.667 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.640 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.497 | SR>0 |
| entry_displacement | reject | PASS | [0.5310643212494119, 0.4970439828510805] | SR>0 both ways |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.700 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.312 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.370 | > 0 |
| other_regimes | reject | PASS | 0.324 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.335 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.11028399033270775, "phase1": 0.3097732121485089 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.051 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.861 | <= 0.5 |

**Why it is ranked here:** passed 18 of 20 decisive/informative attacks.

**Why it might fail:** deflated_sharpe: Is the train Sharpe significant after 112732 trials? -> value 0.051182051838890456 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.8611111111111112 vs <= 0.5

### Strategy #3 - STR-000099 - **OVERFIT**

**Rules:** LONG when x_vix_chg20 in bottom 30% AND zdist_20 in top 15%; exit after 10 bars, stop 1.5 x vol x sqrt(hold)

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 10 bars, or stop at 1.5 x vol x sqrt(hold)
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 2.74

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 62.41% | 3.07% | 4.07 | 0.90 | 1.46 | 6.81% | 44 | 110.2 bps | 75.00% |
| VALIDATION | 6.48% | 1.62% | 4.51 | 0.71 | 1.24 | 4.09% | 7 | 89.7 bps | 85.71% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.45, positive windows 83.33%, efficiency 0.67; expanding OOS Sharpe 0.45

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 8.60%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.84, x3: SR 0.81, latency_plus1: SR 0.54, entry_shift_-1: SR 0.77, entry_shift_+1: SR 0.64

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 75.00%

**Overfitting risk:** deflated Sharpe probability 0.205 (after 112732 trials); PBO 0.92; IS->OOS Sharpe ratio 0.79

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.7074693667807467, "pf": 4.511844285408994, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 51 | >= 30 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.4456251063341708, "positive_windows": 0.833 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.839 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.815 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.542 | SR>0 |
| entry_displacement | reject | PASS | [0.770735973892233, 0.6415941553817878] | SR>0 both ways |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.750 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.277 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.495 | > 0 |
| other_regimes | reject | PASS | 0.451 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.326 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.010698013727010838, "phase1": -0.2420943992055 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.205 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.921 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** deflated_sharpe: Is the train Sharpe significant after 112732 trials? -> value 0.20471379481007407 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.9206349206349206 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- deflated_sharpe: 80
- probability_backtest_overfitting: 75
- out_of_sample_validation: 43
- few_trades_dependence: 30
- other_years: 20
- walk_forward: 10
- latency_plus1: 1
- schedule_dependence: 1
- beats_random_entries: 1

Final status of all 80 examined strategies: {'OVERFIT': 21, 'REJECTED': 59}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-09-25 16:00:00+00:00, horizon 5 bars. Conditions: vol_20 in quintile 1/5 (current value -6.073); ret_20 in quintile 1/5 (current value -0.02201); zdist_60 in quintile 2/5 (current value -0.457)
Sample size 30 (2006-02-24 to 2026-06-08).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.3916% | 46.7% | 30.2%-63.9% | 37.2% |
| B_flat | within +/-0.3916% | 33.3% | 19.2%-51.2% | 26.1% |
| C_down | < -0.3916% | 20.0% | 9.5%-37.3% | 36.7% |

Test vs baseline: p = 0.698 -> NOT informative.
Invalidated if: vol_20 leaves quintile 1; ret_20 leaves quintile 1; zdist_60 leaves quintile 2

- No validated predictive condition exists; conditioning uses generic context variables (volatility, recent return, distance to mean) only.
- Conditional frequencies are not significantly different from the unconditional baseline: the current conditions carry no demonstrated information about the next move.
- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- validation/evaluate: 80

## Limitations

- Price data is one close per day (Fed H.10 noon NY rate): no OHLC, no volume, no intraday; stops are evaluated on closes only and execution is assumed at the next daily fix plus costs.
- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
