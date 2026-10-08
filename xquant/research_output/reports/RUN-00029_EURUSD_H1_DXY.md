# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - [pre-registered 'dxy_smt_eurusd_v1', N=12] 12 candidate strategies examined; none survived. Outcome: {'REJECTED': 12}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00029 |
| Asset | EURUSD_H1_DXY |
| Timeframe | 1h |
| Historical period | 2005-01-02 23:00:00+00:00 to 2026-10-01 00:00:00+00:00 (135749 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | 97dbd4f218623237 |
| Mode / budget used | standard - 1 experiments, 12 strategies examined, 3.89 min |
| Backtests counted as trials (all runs on this dataset) | 12 |

**Splits** (chronological, embargoed): TRAIN 2005-01-02 to 2016-12-30 (74982 bars); VALIDATION 2017-01-08 to 2019-12-31 (18558 bars); TEST 2020-01-09 to 2022-12-30 (18609 bars); FINAL 2023-01-08 to 2026-10-01 (23240 bars)

## Data

- provenance: {'bid_files': 261, 'bid_missing_periods': [], 'ask_files': 261, 'ask_missing_periods': [], 'bars': 135749, 'flat_zero_volume_dropped': 54883, 'spread_median': 4.999999999988347e-05, 'volume': 'Dukascopy tick volume (not exchange volume)', 'seconds': 0.7, 'field_order': 'open,close,low,high (verified by checks)'}
- per-bar spread available (median 5e-05)
- cross-check vs EURUSD: {'matches': 5445, 'median_abs_diff_bps': 0.6749699999986092, 'p95_abs_diff_bps': 2.350823999998975, 'return_corr': 0.9978510238484267, 'local_time': '12:00', 'tz': 'America/New_York', 'median_abs_diff_bps_shift-1h': 6.857475000001667, 'median_abs_diff_bps_shift+1h': 5.440820000000568, 'status': 'PASSED'}
- Quality OK: 135749 raw rows -> 135749 bars; 0 missing (holidays/no fix), 0 duplicates, 0 corrupt, 0 bad prints removed, gaps 16
- Exogenous `us_cpi_yoy`: OK - US CPI-U YoY (BLS). Released ~2 weeks after month end; conservative 35-day lag. (lag 35 days)
- Exogenous `us_10y_yield`: OK - US 10Y yield, monthly average (Fed H.15). Known at month end. (lag 1 days)
- Exogenous `vix`: OK - CBOE VIX close (16:15 New York). Usable from the end of its New York day. (lag 0 days)
- Exogenous `brent`: OK - Brent spot (EIA). Publication time uncertain; usable from the next New York day. (lag 1 days)
- Exogenous `px_dxy`: OK - Synthetic ICE US Dollar Index (DXY) from the 6 Dukascopy hourly mid closes (EUR, JPY, GBP, CAD, SEK, CHF; official exponents and constant), known at the same bar close (lag 0 days)
- Exogenous `px_usd_xeur`: OK - Dollar index EX-EUR: the DXY basket without EURUSD, exponents renormalised to sum 1 (JPY, GBP, CAD, SEK, CHF). Divergence vs EURUSD = euro-specific move (lag 0 days)

## Pre-registered hypothesis (confirmatory mode)

**dxy_smt_eurusd_v1** - registered 2026-10-04T14:57:32.552143+00:00 by X-QUANT, on the user's question 'does DXY divergence help EUR/USD?' (2026-10-04), written before any DXY-based feature had been evaluated; spec sha256 `cdd31221ca4dfad14e2e6ec992846e1dce42aa9339bc1d0bf3925633364f7183`

> SMT divergence between EUR/USD and the US Dollar Index predicts a EUR/USD reversal: when EUR/USD closes below its previous N-bar low and the DXY does NOT close above its previous N-bar high, EUR/USD rises over the following hours; the mirror case at highs predicts a fall.

Rationale: Popular discretionary concept ('SMT divergence'). The DXY is 57.6% EUR, so a non-confirmation means the other five currencies moved against the dollar: the euro-specific move is the outlier and should mean-revert. Prior: weak. Related SMT tests on gold/silver (RUN-00027) and EUR/USD-GBP/USD (RUN-00028) found nothing - recorded for transparency; they do not involve DXY features. Exits are time-based only (3/6/12 one-hour bars); costs, splits and the full adversarial battery are the lab defaults for EURUSD_H1.

Variants fixed in advance (12):

1. LONG when x_px_dxy_smt20 == 1; exit after 3 bars
2. LONG when x_px_dxy_smt20 == 1; exit after 6 bars
3. LONG when x_px_dxy_smt20 == 1; exit after 12 bars
4. SHORT when x_px_dxy_smt20 == -1; exit after 3 bars
5. SHORT when x_px_dxy_smt20 == -1; exit after 6 bars
6. SHORT when x_px_dxy_smt20 == -1; exit after 12 bars
7. LONG when x_px_dxy_smt60 == 1; exit after 3 bars
8. LONG when x_px_dxy_smt60 == 1; exit after 6 bars
9. LONG when x_px_dxy_smt60 == 1; exit after 12 bars
10. SHORT when x_px_dxy_smt60 == -1; exit after 3 bars
11. SHORT when x_px_dxy_smt60 == -1; exit after 6 bars
12. SHORT when x_px_dxy_smt60 == -1; exit after 12 bars

Multiple-testing N for the deflated Sharpe: **12**
- Clean: no feature in the spec had been used by exploratory research before registration.


## Pre-registered variants

| Strategy | Rules | Status | Train SR | Val SR | Val trades | Failed attacks |
|---|---|---|---|---|---|---|
| STR-000834 | LONG when x_px_dxy_smt60 == 1; exit after 12 bars | REJECTED | -0.65 | -0.05 | 148 | out_of_sample_validation, beats_random_entries, walk_forward, parameter_perturbation, spread_slippage_x2, latency_plus1, entry_displacement, randomized_execution, other_years, few_trades_dependence, single_event_dependence, schedule_dependence, data_perturbation, monte_carlo_loss_probability, deflated_sharpe |
| STR-000836 | SHORT when x_px_dxy_smt60 == -1; exit after 6 bars | REJECTED | -0.24 | -0.37 | 171 | out_of_sample_validation, beats_random_entries, parameter_perturbation, spread_slippage_x2, latency_plus1, entry_displacement, randomized_execution, other_years, few_trades_dependence, single_event_dependence, schedule_dependence, data_perturbation, monte_carlo_loss_probability, deflated_sharpe |
| STR-000837 | SHORT when x_px_dxy_smt60 == -1; exit after 12 bars | REJECTED | -0.21 | -0.53 | 153 | out_of_sample_validation, beats_random_entries, walk_forward, parameter_perturbation, spread_slippage_x2, latency_plus1, entry_displacement, randomized_execution, other_years, few_trades_dependence, single_event_dependence, schedule_dependence, data_perturbation, monte_carlo_loss_probability, deflated_sharpe |
| STR-000828 | LONG when x_px_dxy_smt20 == 1; exit after 12 bars | REJECTED | -0.85 | -0.31 | 259 | out_of_sample_validation, beats_random_entries, walk_forward, parameter_perturbation, spread_slippage_x2, latency_plus1, entry_displacement, randomized_execution, other_years, few_trades_dependence, single_event_dependence, schedule_dependence, data_perturbation, monte_carlo_loss_probability, deflated_sharpe |
| STR-000830 | SHORT when x_px_dxy_smt20 == -1; exit after 6 bars | REJECTED | -0.18 | -0.75 | 260 | out_of_sample_validation, beats_random_entries, walk_forward, parameter_perturbation, spread_slippage_x2, latency_plus1, entry_displacement, randomized_execution, other_years, few_trades_dependence, single_event_dependence, schedule_dependence, data_perturbation, monte_carlo_loss_probability, deflated_sharpe |
| STR-000835 | SHORT when x_px_dxy_smt60 == -1; exit after 3 bars | REJECTED | -0.04 | -1.13 | 196 | out_of_sample_validation, parameter_perturbation, spread_slippage_x2, latency_plus1, entry_displacement, randomized_execution, other_years, few_trades_dependence, single_event_dependence, schedule_dependence, data_perturbation, monte_carlo_loss_probability, deflated_sharpe |
| STR-000833 | LONG when x_px_dxy_smt60 == 1; exit after 6 bars | REJECTED | -0.95 | -0.82 | 166 | out_of_sample_validation, beats_random_entries, walk_forward, parameter_perturbation, spread_slippage_x2, latency_plus1, entry_displacement, randomized_execution, other_years, few_trades_dependence, single_event_dependence, schedule_dependence, data_perturbation, monte_carlo_loss_probability, deflated_sharpe |
| STR-000827 | LONG when x_px_dxy_smt20 == 1; exit after 6 bars | REJECTED | -0.93 | -0.76 | 286 | out_of_sample_validation, beats_random_entries, walk_forward, parameter_perturbation, spread_slippage_x2, latency_plus1, entry_displacement, randomized_execution, other_years, few_trades_dependence, single_event_dependence, schedule_dependence, data_perturbation, monte_carlo_loss_probability, deflated_sharpe |
| STR-000831 | SHORT when x_px_dxy_smt20 == -1; exit after 12 bars | REJECTED | -0.21 | -1.16 | 233 | out_of_sample_validation, beats_random_entries, walk_forward, parameter_perturbation, spread_slippage_x2, latency_plus1, entry_displacement, randomized_execution, other_years, few_trades_dependence, single_event_dependence, schedule_dependence, data_perturbation, monte_carlo_loss_probability, deflated_sharpe |
| STR-000829 | SHORT when x_px_dxy_smt20 == -1; exit after 3 bars | REJECTED | -0.20 | -1.35 | 295 | out_of_sample_validation, walk_forward, parameter_perturbation, spread_slippage_x2, latency_plus1, entry_displacement, randomized_execution, other_years, few_trades_dependence, single_event_dependence, schedule_dependence, data_perturbation, monte_carlo_loss_probability, deflated_sharpe |
| STR-000826 | LONG when x_px_dxy_smt20 == 1; exit after 3 bars | REJECTED | -1.12 | -0.93 | 310 | out_of_sample_validation, beats_random_entries, walk_forward, parameter_perturbation, spread_slippage_x2, latency_plus1, entry_displacement, randomized_execution, other_years, few_trades_dependence, single_event_dependence, schedule_dependence, data_perturbation, monte_carlo_loss_probability, deflated_sharpe |
| STR-000832 | LONG when x_px_dxy_smt60 == 1; exit after 3 bars | REJECTED | -0.78 | -1.20 | 179 | out_of_sample_validation, beats_random_entries, walk_forward, parameter_perturbation, spread_slippage_x2, latency_plus1, entry_displacement, randomized_execution, other_years, few_trades_dependence, single_event_dependence, schedule_dependence, data_perturbation, monte_carlo_loss_probability, deflated_sharpe |

Detail of the top 3:

### Strategy #1 - STR-000834 - **REJECTED**

**Rules:** LONG when x_px_dxy_smt60 == 1; exit after 12 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 12 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 1  |  Composite score: -0.81

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | -21.34% | -1.98% | 0.75 | -0.65 | -0.88 | 23.70% | 546 | -4.4 bps | 49.27% |
| VALIDATION | -0.32% | -0.11% | 0.98 | -0.05 | -0.08 | 6.57% | 148 | -0.2 bps | 47.97% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe -0.41, positive windows 33.33%, efficiency n/a; expanding OOS Sharpe -0.40

**Monte Carlo:** P(loss) under trade bootstrap 99.00%, 95th pct max DD 34.95%; random-entry test p = 0.778

**Stress tests:** x2: SR -0.92, x3: SR -1.27, latency_plus1: SR -0.75, entry_shift_+1: SR -0.69, entry_shift_+2: SR -0.63

**Robustness:** parameter neighbours profitable 0.00%; noise-perturbed runs SR>0 0.00%; profitable years 46.67%

**Overfitting risk:** deflated Sharpe probability 0.000 (after 12 trials); PBO 0.23; IS->OOS Sharpe ratio n/a

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | FAIL | {"sharpe": -0.05389699821066209, "pf": 0.9801901970798255, " | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 694 | >= 60 |
| beats_random_entries | reject | FAIL | 0.778 | p < 0.05 |
| walk_forward | reject | FAIL | {"oos_sharpe": -0.4120316684266913, "positive_windows": 0.33 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | FAIL | 0.000 | >= 0.6 |
| spread_slippage_x2 | reject | FAIL | -0.918 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | FAIL | -1.270 | SR>0 at 3x costs |
| latency_plus1 | reject | FAIL | -0.747 | SR>0 |
| entry_displacement | reject | FAIL | [-0.6902552963647227, -0.6333725561291855] | SR>0 for both delays |
| randomized_execution | reject | FAIL | 0.000 | >= 0.6 of runs SR>0 |
| other_years | reject | FAIL | 0.467 | >= 0.5 |
| few_trades_dependence | reject | FAIL | null | top 5% trades <= 50% of profit |
| single_event_dependence | reject | FAIL | -0.266 | > 0 |
| schedule_dependence | reject | FAIL | 1.000 | <= 60% |
| data_perturbation | overfit | FAIL | 0.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.6406588969309623, "phase1": -0.177614993379222 | SR>0 both phases |
| monte_carlo_loss_probability | reject | FAIL | 0.990 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.000 | >= 0.95 |
| probability_backtest_overfitting | overfit | PASS | 0.226 | <= 0.5 |

**Why it is ranked here:** passed 2 of 19 decisive/informative attacks.

**Why it might fail:** out_of_sample_validation: Does it work out of sample (VALIDATION, thresholds from TRAIN)? -> value {'sharpe': -0.05389699821066209, 'pf': 0.9801901970798255, 'trades': 148} vs SR>0, PF>1, >=5 trades; beats_random_entries: Does its timing beat random entries with the same exits and costs? -> value 0.7784431137724551 vs p < 0.05; walk_forward: Does it survive rolling walk-forward re-fitting? -> value {'oos_sharpe': -0.4120316684266913, 'positive_windows': 0.3333333333333333} vs OOS SR>0 and >=50% windows positive; spread_slippage_x2: Does it survive doubled spread, commission and slippage? -> value -0.9181193935017115 vs SR>0 at 2x costs; latency_plus1: Does it survive one extra bar of latency? -> value -0.7467693075939278 vs SR>0; entry_displacement: Does it survive entries delayed by 1 and 2 bars? -> value [-0.6902552963647227, -0.6333725561291855] vs SR>0 for both delays; randomized_execution: Does it survive random delays and 10% skipped trades? -> value 0.0 vs >= 0.6 of runs SR>0; other_years: Does it work across years, not only in some? -> value 0.4666666666666667 vs >= 0.5; few_trades_dependence: Does profit depend on a handful of trades? -> value inf vs top 5% trades <= 50% of profit; single_event_dependence: Is it still profitable without its best month? -> value -0.26613356586516634 vs > 0; schedule_dependence: Does it depend on one weekday/hour? -> value 1.0 vs <= 60%; monte_carlo_loss_probability: Under trade-order bootstrap, is a loss unlikely? -> value 0.99 vs <= 0.2; parameter_perturbation: Does it survive +/-25% parameter changes? -> value 0.0 vs >= 0.6; data_perturbation: Does it survive small noise added to prices? -> value 0.0 vs >= 0.6 of runs SR>0; deflated_sharpe: Is the train Sharpe significant after 12 trials? -> value 4.007048952945622e-05 vs >= 0.95

### Strategy #2 - STR-000836 - **REJECTED**

**Rules:** SHORT when x_px_dxy_smt60 == -1; exit after 6 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 6 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 1  |  Composite score: -0.96

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | -7.21% | -0.62% | 0.91 | -0.24 | -0.34 | 13.50% | 670 | -1.1 bps | 48.51% |
| VALIDATION | -2.00% | -0.68% | 0.87 | -0.37 | -0.49 | 4.43% | 171 | -1.2 bps | 47.37% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.06, positive windows 50.00%, efficiency n/a; expanding OOS Sharpe -0.04

**Monte Carlo:** P(loss) under trade bootstrap 83.50%, 95th pct max DD 24.71%; random-entry test p = 0.170

**Stress tests:** x2: SR -0.77, x3: SR -1.28, latency_plus1: SR -0.43, entry_shift_+1: SR -0.53, entry_shift_+2: SR -0.51

**Robustness:** parameter neighbours profitable 0.00%; noise-perturbed runs SR>0 0.00%; profitable years 40.00%

**Overfitting risk:** deflated Sharpe probability 0.006 (after 12 trials); PBO 0.23; IS->OOS Sharpe ratio n/a

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | FAIL | {"sharpe": -0.3671202995995057, "pf": 0.8739402851895994, "t | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 842 | >= 60 |
| beats_random_entries | reject | FAIL | 0.170 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.05576328428424512, "positive_windows": 0.5} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | FAIL | 0.000 | >= 0.6 |
| spread_slippage_x2 | reject | FAIL | -0.765 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | FAIL | -1.275 | SR>0 at 3x costs |
| latency_plus1 | reject | FAIL | -0.427 | SR>0 |
| entry_displacement | reject | FAIL | [-0.5272692953316971, -0.5052137165186587] | SR>0 for both delays |
| randomized_execution | reject | FAIL | 0.000 | >= 0.6 of runs SR>0 |
| other_years | reject | FAIL | 0.400 | >= 0.5 |
| few_trades_dependence | reject | FAIL | null | top 5% trades <= 50% of profit |
| single_event_dependence | reject | FAIL | -0.117 | > 0 |
| schedule_dependence | reject | FAIL | 1.000 | <= 60% |
| data_perturbation | overfit | FAIL | 0.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.9103338726786886, "phase1": -0.627574962574042 | SR>0 both phases |
| monte_carlo_loss_probability | reject | FAIL | 0.835 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.006 | >= 0.95 |
| probability_backtest_overfitting | overfit | PASS | 0.226 | <= 0.5 |

**Why it is ranked here:** passed 3 of 19 decisive/informative attacks.

**Why it might fail:** out_of_sample_validation: Does it work out of sample (VALIDATION, thresholds from TRAIN)? -> value {'sharpe': -0.3671202995995057, 'pf': 0.8739402851895994, 'trades': 171} vs SR>0, PF>1, >=5 trades; beats_random_entries: Does its timing beat random entries with the same exits and costs? -> value 0.16966067864271456 vs p < 0.05; spread_slippage_x2: Does it survive doubled spread, commission and slippage? -> value -0.765202473876746 vs SR>0 at 2x costs; latency_plus1: Does it survive one extra bar of latency? -> value -0.42727630362534014 vs SR>0; entry_displacement: Does it survive entries delayed by 1 and 2 bars? -> value [-0.5272692953316971, -0.5052137165186587] vs SR>0 for both delays; randomized_execution: Does it survive random delays and 10% skipped trades? -> value 0.0 vs >= 0.6 of runs SR>0; other_years: Does it work across years, not only in some? -> value 0.4 vs >= 0.5; few_trades_dependence: Does profit depend on a handful of trades? -> value inf vs top 5% trades <= 50% of profit; single_event_dependence: Is it still profitable without its best month? -> value -0.11703527227892394 vs > 0; schedule_dependence: Does it depend on one weekday/hour? -> value 1.0 vs <= 60%; monte_carlo_loss_probability: Under trade-order bootstrap, is a loss unlikely? -> value 0.835 vs <= 0.2; parameter_perturbation: Does it survive +/-25% parameter changes? -> value 0.0 vs >= 0.6; data_perturbation: Does it survive small noise added to prices? -> value 0.0 vs >= 0.6 of runs SR>0; deflated_sharpe: Is the train Sharpe significant after 12 trials? -> value 0.006128865783737539 vs >= 0.95

### Strategy #3 - STR-000837 - **REJECTED**

**Rules:** SHORT when x_px_dxy_smt60 == -1; exit after 12 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 12 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 1  |  Composite score: -1.36

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | -7.81% | -0.67% | 0.92 | -0.21 | -0.30 | 12.95% | 584 | -1.4 bps | 48.80% |
| VALIDATION | -3.41% | -1.16% | 0.84 | -0.53 | -0.71 | 4.88% | 153 | -2.3 bps | 45.75% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe -0.07, positive windows 50.00%, efficiency n/a; expanding OOS Sharpe 0.03

**Monte Carlo:** P(loss) under trade bootstrap 85.60%, 95th pct max DD 29.68%; random-entry test p = 0.427

**Stress tests:** x2: SR -0.64, x3: SR -1.00, latency_plus1: SR -0.36, entry_shift_+1: SR -0.40, entry_shift_+2: SR -0.31

**Robustness:** parameter neighbours profitable 0.00%; noise-perturbed runs SR>0 0.00%; profitable years 26.67%

**Overfitting risk:** deflated Sharpe probability 0.008 (after 12 trials); PBO 0.23; IS->OOS Sharpe ratio n/a

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | FAIL | {"sharpe": -0.5277449669863911, "pf": 0.8373238666538746, "t | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 738 | >= 60 |
| beats_random_entries | reject | FAIL | 0.427 | p < 0.05 |
| walk_forward | reject | FAIL | {"oos_sharpe": -0.07045922510398743, "positive_windows": 0.5 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | FAIL | 0.000 | >= 0.6 |
| spread_slippage_x2 | reject | FAIL | -0.636 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | FAIL | -0.999 | SR>0 at 3x costs |
| latency_plus1 | reject | FAIL | -0.363 | SR>0 |
| entry_displacement | reject | FAIL | [-0.39641019086697676, -0.31381854778318796] | SR>0 for both delays |
| randomized_execution | reject | FAIL | 0.000 | >= 0.6 of runs SR>0 |
| other_years | reject | FAIL | 0.267 | >= 0.5 |
| few_trades_dependence | reject | FAIL | null | top 5% trades <= 50% of profit |
| single_event_dependence | reject | FAIL | -0.148 | > 0 |
| schedule_dependence | reject | FAIL | 1.000 | <= 60% |
| data_perturbation | overfit | FAIL | 0.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.7699569121753386, "phase1": -0.215867293777061 | SR>0 both phases |
| monte_carlo_loss_probability | reject | FAIL | 0.856 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.008 | >= 0.95 |
| probability_backtest_overfitting | overfit | PASS | 0.226 | <= 0.5 |

**Why it is ranked here:** passed 2 of 19 decisive/informative attacks.

**Why it might fail:** out_of_sample_validation: Does it work out of sample (VALIDATION, thresholds from TRAIN)? -> value {'sharpe': -0.5277449669863911, 'pf': 0.8373238666538746, 'trades': 153} vs SR>0, PF>1, >=5 trades; beats_random_entries: Does its timing beat random entries with the same exits and costs? -> value 0.42714570858283435 vs p < 0.05; walk_forward: Does it survive rolling walk-forward re-fitting? -> value {'oos_sharpe': -0.07045922510398743, 'positive_windows': 0.5} vs OOS SR>0 and >=50% windows positive; spread_slippage_x2: Does it survive doubled spread, commission and slippage? -> value -0.6358697305969535 vs SR>0 at 2x costs; latency_plus1: Does it survive one extra bar of latency? -> value -0.36257306163874525 vs SR>0; entry_displacement: Does it survive entries delayed by 1 and 2 bars? -> value [-0.39641019086697676, -0.31381854778318796] vs SR>0 for both delays; randomized_execution: Does it survive random delays and 10% skipped trades? -> value 0.0 vs >= 0.6 of runs SR>0; other_years: Does it work across years, not only in some? -> value 0.26666666666666666 vs >= 0.5; few_trades_dependence: Does profit depend on a handful of trades? -> value inf vs top 5% trades <= 50% of profit; single_event_dependence: Is it still profitable without its best month? -> value -0.14755656869820505 vs > 0; schedule_dependence: Does it depend on one weekday/hour? -> value 1.0 vs <= 60%; monte_carlo_loss_probability: Under trade-order bootstrap, is a loss unlikely? -> value 0.856 vs <= 0.2; parameter_perturbation: Does it survive +/-25% parameter changes? -> value 0.0 vs >= 0.6; data_perturbation: Does it survive small noise added to prices? -> value 0.0 vs >= 0.6 of runs SR>0; deflated_sharpe: Is the train Sharpe significant after 12 trials? -> value 0.008119455873137114 vs >= 0.95

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- out_of_sample_validation: 12
- parameter_perturbation: 12
- spread_slippage_x2: 12
- latency_plus1: 12
- entry_displacement: 12
- randomized_execution: 12
- other_years: 12
- few_trades_dependence: 12
- single_event_dependence: 12
- schedule_dependence: 12
- data_perturbation: 12
- monte_carlo_loss_probability: 12
- deflated_sharpe: 12
- beats_random_entries: 10
- walk_forward: 10

Final status of all 12 examined strategies: {'REJECTED': 12}

## Scenario analysis (historical frequencies, not forecasts)

Scenario analysis: not run

## Protected split access log

- validation/evaluate: 12

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
