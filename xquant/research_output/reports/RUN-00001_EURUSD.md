# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 30 candidate strategies examined; none survived. Outcome: {'REJECTED': 30}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00001 |
| Asset | EURUSD |
| Timeframe | 1D |
| Historical period | 1999-01-04 17:00:00+00:00 to 2026-09-25 16:00:00+00:00 (6955 bars) |
| Data capabilities | close only |
| Dataset version | 35fd595cefb7190d |
| Mode / budget used | standard - 12 experiments, 30 strategies examined, 1.76 min |
| Backtests counted as trials (all runs on this dataset) | 7951 |

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

400 candidate features, 1980 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **0** []
Status counts: {'REJECTED': 1980}

## Top hypotheses

1470 hypotheses (1470 new, 0 reused from memory). Status counts: {'REJECTED': 1464, 'OVERFIT': 6}

No hypothesis survived FDR on the discovery window **and** confirmation on the inner holdout.

Strongest hypotheses that failed confirmation (OVERFIT):

- HYP-000234: When vol_60 <= -5.31 (bottom 20%), next 10-bar return differs from baseline - discovery p=0.00006, confirmation p=0.465, confirmation effect -0.00184 vs 0.00815
- HYP-000232: When vol_60 <= -5.31 (bottom 20%), next 3-bar return differs from baseline - discovery p=0.00008, confirmation p=0.312, confirmation effect -0.00083 vs 0.00250
- HYP-000235: When vol_60 <= -5.31 (bottom 20%), next 20-bar return differs from baseline - discovery p=0.00009, confirmation p=0.234, confirmation effect -0.00601 vs 0.01553
- HYP-000233: When vol_60 <= -5.31 (bottom 20%), next 5-bar return differs from baseline - discovery p=0.00010, confirmation p=0.348, confirmation effect -0.00120 vs 0.00406
- HYP-000749: When month == 1, next 10-bar return differs from baseline - discovery p=0.00010, confirmation p=0.003, confirmation effect 0.01248 vs -0.01083

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 0 | 0 | evidence insufficient: no hypothesis survived FDR + inner-holdout confirmation |
| open_exploration | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| regime_conditioned | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| macro_conditioned | STOPPED | 2 | 10 | budget: max_strategies (30) examined |

## Top strategies

### Strategy #1 - STR-000005 - **REJECTED**

**Rules:** SHORT when x_vix_chg20 in top 10%; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 1  |  Composite score: 2.37

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 48.32% | 2.49% | 1.67 | 0.42 | 0.62 | 15.64% | 56 | 70.4 bps | 62.50% |
| VALIDATION | 8.59% | 2.13% | 2.49 | 0.45 | 0.64 | 6.18% | 13 | 63.4 bps | 61.54% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.07, positive windows 66.67%, efficiency 0.42; expanding OOS Sharpe 0.18

**Monte Carlo:** P(loss) under trade bootstrap 3.00%, 95th pct max DD 26.32%; random-entry test p = 0.010

**Stress tests:** x2: SR 0.45, x3: SR 0.43, latency_plus1: SR 0.45, entry_shift_-1: SR 0.34, entry_shift_+1: SR 0.52

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 70.00%

**Overfitting risk:** deflated Sharpe probability 0.058 (after 1088 trials); PBO 0.48; IS->OOS Sharpe ratio 1.05

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.44533939360036945, "pf": 2.4949786155082423, "t | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 70 | >= 30 |
| beats_random_entries | reject | PASS | 0.010 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.06781801015942215, "positive_windows": 0.66 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.450 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.431 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.446 | SR>0 |
| entry_displacement | reject | PASS | [0.33639572072390056, 0.5248520835702328] | SR>0 both ways |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.700 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.547 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.412 | > 0 |
| other_regimes | reject | PASS | 0.488 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.479 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.25004512057947875, "phase1": 0.1114992398380536 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.030 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.058 | >= 0.95 |
| probability_backtest_overfitting | overfit | PASS | 0.476 | <= 0.5 |

**Why it is ranked here:** passed 18 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.547402450873823 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 1088 trials? -> value 0.057660153930750475 vs >= 0.95

### Strategy #2 - STR-000030 - **REJECTED**

**Rules:** LONG when x_us_cpi_yoy_chg63 in bottom 20%; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 1  |  Composite score: 1.89

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 29.14% | 1.61% | 1.85 | 0.33 | 0.49 | 10.59% | 44 | 58.1 bps | 59.09% |
| VALIDATION | 3.95% | 1.00% | 1.62 | 0.24 | 0.35 | 6.59% | 7 | 55.3 bps | 57.14% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.43, positive windows 83.33%, efficiency 1.37; expanding OOS Sharpe 0.23

**Monte Carlo:** P(loss) under trade bootstrap 10.00%, 95th pct max DD 21.49%; random-entry test p = 0.072

**Stress tests:** x2: SR 0.24, x3: SR 0.23, latency_plus1: SR 0.40, entry_shift_-1: SR 0.27, entry_shift_+1: SR 0.37

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 45.00%

**Overfitting risk:** deflated Sharpe probability 0.006 (after 7951 trials); PBO 0.70; IS->OOS Sharpe ratio 0.74

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.24058226594378349, "pf": 1.6225874476094029, "t | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 52 | >= 30 |
| beats_random_entries | reject | FAIL | 0.072 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.43414797006971473, "positive_windows": 0.83 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.244 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.228 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.397 | SR>0 |
| entry_displacement | reject | PASS | [0.2652299628621549, 0.36864453920403495] | SR>0 both ways |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | FAIL | 0.450 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.756 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.169 | > 0 |
| other_regimes | reject | PASS | 0.343 | <= 85% from one regime |
| schedule_dependence | reject | FAIL | 0.687 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.03469506668563264, "phase1": 0.0846038571088717 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.100 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.006 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.698 | <= 0.5 |

**Why it is ranked here:** passed 14 of 20 decisive/informative attacks.

**Why it might fail:** beats_random_entries: Does its timing beat random entries with the same exits and costs? -> value 0.0718562874251497 vs p < 0.05; other_years: Does it work across years, not only in some? -> value 0.45 vs >= 0.5; few_trades_dependence: Does profit depend on a handful of trades? -> value 0.7557106265838521 vs top 5% trades <= 50% of profit; schedule_dependence: Does it depend on one weekday/hour? -> value 0.6874237100422915 vs <= 60%; deflated_sharpe: Is the train Sharpe significant after 7951 trials? -> value 0.005777185625134924 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.6984126984126984 vs <= 0.5

### Strategy #3 - STR-000023 - **REJECTED**

**Rules:** SHORT when x_vix_chg5 in bottom 10% AND regime == 2; exit after 2 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 2 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 1.84

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 13.76% | 0.81% | 1.69 | 0.42 | 0.66 | 5.28% | 78 | 16.5 bps | 58.97% |
| VALIDATION | 1.74% | 0.44% | 1.40 | 0.27 | 0.44 | 1.64% | 20 | 8.6 bps | 55.00% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.06, positive windows 66.67%, efficiency 0.30; expanding OOS Sharpe 0.19

**Monte Carlo:** P(loss) under trade bootstrap 3.70%, 95th pct max DD 7.84%; random-entry test p = 0.016

**Stress tests:** x2: SR 0.31, x3: SR 0.23, latency_plus1: SR 0.20, entry_shift_-1: SR 0.17, entry_shift_+1: SR 0.32

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 65.00%

**Overfitting risk:** deflated Sharpe probability 0.015 (after 7242 trials); PBO 0.92; IS->OOS Sharpe ratio 0.64

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.2678601397371718, "pf": 1.3966830302857458, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 98 | >= 30 |
| beats_random_entries | reject | PASS | 0.016 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.06011673724800517, "positive_windows": 0.66 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.311 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.233 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.195 | SR>0 |
| entry_displacement | reject | PASS | [0.17455846325834437, 0.31593915224824537] | SR>0 both ways |
| randomized_execution | reject | PASS | 0.960 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.650 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.678 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.118 | > 0 |
| schedule_dependence | reject | PASS | 0.520 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.05695940922677311, "phase1": -0.22843876349171 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.037 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.015 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.921 | <= 0.5 |

**Why it is ranked here:** passed 15 of 19 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.6781852450110422 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 7242 trials? -> value 0.01535182658938029 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.9206349206349206 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- deflated_sharpe: 30
- few_trades_dependence: 24
- out_of_sample_validation: 22
- probability_backtest_overfitting: 20
- other_years: 14
- walk_forward: 12
- beats_random_entries: 9
- schedule_dependence: 6
- other_regimes: 2
- monte_carlo_loss_probability: 2
- entry_displacement: 1
- single_event_dependence: 1

Final status of all 30 examined strategies: {'REJECTED': 30}

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

- validation/evaluate: 30

## Limitations

- Price data is one close per day (Fed H.10 noon NY rate): no OHLC, no volume, no intraday; stops are evaluated on closes only and execution is assumed at the next daily fix plus costs.
- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
