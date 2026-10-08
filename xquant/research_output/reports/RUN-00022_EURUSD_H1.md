# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 30 candidate strategies examined; none survived. Outcome: {'REJECTED': 28, 'OVERFIT': 2}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00022 |
| Asset | EURUSD_H1 |
| Timeframe | 1h |
| Historical period | 2005-01-02 23:00:00+00:00 to 2026-10-01 00:00:00+00:00 (135749 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | ae17a1577bcfcc70 |
| Mode / budget used | standard - 12 experiments, 30 strategies examined, 10.66 min |
| Backtests counted as trials (all runs on this dataset) | 189361 |

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

## Market discoveries

91 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 5.**

- **runs_test_signs** - Wald-Wolfowitz runs of return signs; effect<0 = longer runs than chance: effect 0.05433, p=0.00000, q=0.0000, replication p=0.00000 (n=74663)
- **big_move_clustering** - P(>2.5 sigma bar next) after a >2.5 sigma bar vs otherwise: effect 0.05300, p=0.00000, q=0.0000, replication p=0.00000 (n=2607)
- **arch_lm_5** - Engle ARCH-LM(5): volatility clustering; effect = R^2: effect 0.03491, p=0.00000, q=0.0000, replication p=0.00000 (n=74976)
- **ljung_box_abs_20** - Ljung-Box(20) on |returns|; effect = lag-1 acf of |r|: effect 0.24848, p=0.00000, q=0.0000, replication p=0.00000 (n=74981)
- **high_vol_mean_reversion** - log(next-20-bar vol / vol60) when vol20 is in its top decile (vs rest): effect -0.12182, p=0.00000, q=0.0000, replication p=0.00000 (n=7487)
- Not replicated: big_move_follow_fwd1 (train p=0.00291, validation p=0.8428)
- Not replicated: big_move_follow_fwd5 (train p=0.00987, validation p=0.6384)
- Not replicated: big_move_follow_fwd10 (train p=0.00628, validation p=0.7878)
- Not replicated: streak3_fwd1 (train p=0.00001, validation p=0.1096)
- Not replicated: streak3_fwd5 (train p=0.00392, validation p=0.3806)
- Not replicated: streak4_fwd1 (train p=0.00364, validation p=0.2327)
- Not replicated: streak4_fwd5 (train p=0.00824, validation p=0.8678)
- Not replicated: streak5_fwd1 (train p=0.00004, validation p=0.1187)
- Not replicated: compression_then_expansion (train p=0.00001, validation p=0.0261)
- Not replicated: hour_05 (train p=0.01068, validation p=0.4139)
- Not replicated: hour_06 (train p=0.00000, validation p=0.2423)
- Not replicated: hour_11 (train p=0.00584, validation p=0.6949)
- Not replicated: hour_12 (train p=0.00141, validation p=0.7841)
- Not replicated: hour_16 (train p=0.00300, validation p=0.0000)
- Not replicated: hour_17 (train p=0.00000, validation p=0.0232)
- Not replicated: hour_19 (train p=0.00126, validation p=0.4818)
- Not replicated: hour_21 (train p=0.00000, validation p=0.0485)
- Not replicated: hour_22 (train p=0.00003, validation p=0.0134)
- Descriptive - return_distribution_train: Per-bar log return distribution {"mean_bps": -0.03387486320133532, "ann_vol": 0.1016995593711208, "skew": -0.04118455200158094, "excess_kurtosis": 13.334597508004002, "jarque_bera_p": 0.0, "n": 74981}
- Descriptive - return_distribution_validation: Per-bar log return distribution {"mean_bps": 0.03370017540857319, "ann_vol": 0.06683311265954167, "skew": 0.5339051102783108, "excess_kurtosis": 15.68079963814369, "jarque_bera_p": 0.0, "n": 18558}
- Descriptive - trend_episode_duration: Directional-change episodes (threshold 0.0068 log) vs 200 shuffled-return paths (TRAIN) {"episodes": 1373, "mean_duration": 54.57246904588492, "median_duration": 36.0, "shuffled_mean_duration": 50.29647883570984, "p_longer_than_shuffled": 0.004975124378109453}
- Descriptive - regime_model: GMM regimes on TRAIN, k=5 chosen by BIC {"labels": {"0": "R0: low-vol ranging contracting", "1": "R1: high-vol trending", "2": "R2: high-vol trending contracting", "3": "R3: high-vol trending contracting", "4": "R4: low-vol ranging contracting"}, "persistence": {"0": 0.701918663361792, "1": 0.5140885566417481, "2": 0.792698144346496, "3": 0.6173273657289002, "4": 0.5164961931861878}, "occupancy": {"0": 0.29074919262284143, "1": 0.162449

## Macro discoveries

32 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- Descriptive - macro_data_limits: Macro series are latest-vintage (revised) values with conservative publication lags; no consensus data => no surprise analysis {}
- INSUFFICIENT DATA for: CPI, PCE, NFP, Unemployment rate, Average hourly earnings, GDP, PMI, Fed rate decision, ECB rate decision, Central bank statements

## News discoveries

0 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- INSUFFICIENT DATA for: news_predictive_power

## Feature discovery

400 candidate features, 1930 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **40** ['mul(abs(on_pos),ret_3)', 'close_loc', 'sub(ny_ret,volratio_5_20)', 'ret_3', 'streak', 'zdist_10', 'fromlow_20', 'ret_2', 'sess_pos', 'zdist_20']
Status counts: {'REJECTED': 1793, 'TOO_COMPLEX': 81, 'CONFIRMED': 49, 'NOT_CONFIRMED': 7}

## Top hypotheses

4805 hypotheses (540 new, 4265 reused from memory). Status counts: {'REJECTED': 4776, 'VALIDATION': 20, 'OVERFIT': 9}

| ID | Hypothesis | n | effect size | p | q | confirm p | status |
|---|---|---|---|---|---|---|---|
| HYP-029236 | When sess_bar == 12, next 1-bar return differs from baseline | 2187 | -0.109 | 0.00000 | 0.0000 | 0.0070 | VALIDATION |
| HYP-029232 | When sess_bar == 11, next 3-bar return differs from baseline | 2187 | -0.100 | 0.00000 | 0.0006 | 0.0001 | VALIDATION |
| HYP-029233 | When sess_bar == 11, next 6-bar return differs from baseline | 2187 | -0.095 | 0.00021 | 0.0103 | 0.0208 | VALIDATION |
| HYP-029192 | When sess_bar == 3, next 3-bar return differs from baseline | 2187 | 0.084 | 0.00000 | 0.0000 | 0.0198 | VALIDATION |
| HYP-029193 | When sess_bar == 3, next 6-bar return differs from baseline | 2187 | 0.081 | 0.00000 | 0.0001 | 0.0291 | VALIDATION |
| HYP-029263 | When sess_bar == 17, next 6-bar return differs from baseline | 2187 | 0.075 | 0.00007 | 0.0043 | 0.0000 | VALIDATION |
| HYP-029292 | When sess_bar == 23, next 3-bar return differs from baseline | 2185 | -0.071 | 0.00002 | 0.0021 | 0.0003 | VALIDATION |
| HYP-029291 | When sess_bar == 23, next 1-bar return differs from baseline | 2185 | -0.069 | 0.00088 | 0.0318 | 0.0000 | VALIDATION |
| HYP-029191 | When sess_bar == 3, next 1-bar return differs from baseline | 2187 | 0.068 | 0.00004 | 0.0037 | 0.0485 | VALIDATION |
| HYP-029262 | When sess_bar == 17, next 3-bar return differs from baseline | 2187 | 0.067 | 0.00204 | 0.0485 | 0.0000 | VALIDATION |

Strongest hypotheses that failed confirmation (OVERFIT):

- HYP-029197: When sess_bar == 4, next 3-bar return differs from baseline - discovery p=0.00007, confirmation p=0.058, confirmation effect 0.00009 vs 0.00012
- HYP-029196: When sess_bar == 4, next 1-bar return differs from baseline - discovery p=0.00012, confirmation p=0.077, confirmation effect 0.00006 vs 0.00007
- HYP-029308: When on_pos <= 0.05531 (bottom 20%), next 6-bar return differs from baseline - discovery p=0.00041, confirmation p=0.797, confirmation effect 0.00003 vs -0.00025
- HYP-028997: When sess_ret <= -4.072 (bottom 10%), next 3-bar return differs from baseline - discovery p=0.00081, confirmation p=0.246, confirmation effect 0.00008 vs -0.00015
- HYP-029283: When sess_bar == 21, next 6-bar return differs from baseline - discovery p=0.00104, confirmation p=0.564, confirmation effect -0.00004 vs -0.00017

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| open_exploration | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| regime_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |
| macro_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |

## Top strategies

### Strategy #1 - STR-000686 - **REJECTED**

**Rules:** SHORT when x_vix_chg63 in bottom 20% AND sub(ny_ret,volratio_5_20) in bottom 30% AND streak in top 15%; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 3.07

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 17.80% | 1.37% | 1.66 | 0.64 | 0.96 | 6.25% | 115 | 14.2 bps | 56.52% |
| VALIDATION | 3.37% | 1.12% | 2.09 | 0.97 | 1.41 | 1.06% | 32 | 10.4 bps | 62.50% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.55, positive windows 83.33%, efficiency 0.82; expanding OOS Sharpe 0.57

**Monte Carlo:** P(loss) under trade bootstrap 0.60%, 95th pct max DD 8.40%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.55, x3: SR 0.44, latency_plus1: SR 0.44, entry_shift_+1: SR 0.48, entry_shift_+2: SR 0.29

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 66.67%

**Overfitting risk:** deflated Sharpe probability 0.011 (after 189361 trials); PBO 0.40; IS->OOS Sharpe ratio 1.53

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.9717687663922496, "pf": 2.0914069530578563, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 147 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.5467703665838615, "positive_windows": 0.833 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.552 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.443 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.439 | SR>0 |
| entry_displacement | reject | PASS | [0.481108583127644, 0.29361431289677675] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.667 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.653 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.166 | > 0 |
| other_regimes | reject | PASS | 0.515 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.466 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.47157219545739215, "phase1": -0.33626837339454 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.006 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.011 | >= 0.95 |
| probability_backtest_overfitting | overfit | PASS | 0.405 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.6533356636291353 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 189361 trials? -> value 0.011082190762785162 vs >= 0.95

### Strategy #2 - STR-000690 - **REJECTED**

**Rules:** SHORT when x_vix_chg63 in bottom 20% AND sub(ny_ret,volratio_5_20) in bottom 30% AND streak in top 20%; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 3.07

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 17.80% | 1.37% | 1.66 | 0.64 | 0.96 | 6.25% | 115 | 14.2 bps | 56.52% |
| VALIDATION | 3.37% | 1.12% | 2.09 | 0.97 | 1.41 | 1.06% | 32 | 10.4 bps | 62.50% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.55, positive windows 83.33%, efficiency 0.82; expanding OOS Sharpe 0.57

**Monte Carlo:** P(loss) under trade bootstrap 1.80%, 95th pct max DD 9.01%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.55, x3: SR 0.44, latency_plus1: SR 0.44, entry_shift_+1: SR 0.48, entry_shift_+2: SR 0.29

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 66.67%

**Overfitting risk:** deflated Sharpe probability 0.011 (after 189361 trials); PBO 0.40; IS->OOS Sharpe ratio 1.53

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.9717687663922496, "pf": 2.0914069530578563, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 147 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.5467703665838615, "positive_windows": 0.833 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.552 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.443 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.439 | SR>0 |
| entry_displacement | reject | PASS | [0.481108583127644, 0.29361431289677675] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.667 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.653 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.166 | > 0 |
| other_regimes | reject | PASS | 0.515 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.466 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.47157219545739215, "phase1": -0.33626837339454 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.018 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.011 | >= 0.95 |
| probability_backtest_overfitting | overfit | PASS | 0.405 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.6533356636291353 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 189361 trials? -> value 0.011082190762785162 vs >= 0.95

### Strategy #3 - STR-000648 - **REJECTED**

**Rules:** SHORT when sess_bar == 11 AND gap in bottom 15%; exit after 3 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 3 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 2.86

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 13.87% | 1.09% | 1.34 | 0.66 | 1.00 | 4.36% | 455 | 2.9 bps | 51.43% |
| VALIDATION | 1.00% | 0.33% | 3.07 | 0.85 | 1.63 | 0.31% | 15 | 6.6 bps | 53.33% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.33, positive windows 50.00%, efficiency 0.87; expanding OOS Sharpe 0.50

**Monte Carlo:** P(loss) under trade bootstrap 0.30%, 95th pct max DD 5.17%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.15, x3: SR -0.33, latency_plus1: SR 0.25, entry_shift_+1: SR 0.25, entry_shift_+2: SR -0.10

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 87.50%; profitable years 86.67%

**Overfitting risk:** deflated Sharpe probability 0.012 (after 189361 trials); PBO 0.59; IS->OOS Sharpe ratio 1.28

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.8499839388252576, "pf": 3.067146856349477, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 470 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.3263468345242819, "positive_windows": 0.5} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.153 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | FAIL | -0.325 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.251 | SR>0 |
| entry_displacement | reject | FAIL | [0.251151711235559, -0.10464721570485665] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.867 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 1.101 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.125 | > 0 |
| other_regimes | reject | PASS | 0.468 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.402 | <= 60% |
| data_perturbation | overfit | PASS | 0.875 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.8483149871614353, "phase1": -0.815534296713100 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.003 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.012 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.587 | <= 0.5 |

**Why it is ranked here:** passed 14 of 20 decisive/informative attacks.

**Why it might fail:** entry_displacement: Does it survive entries delayed by 1 and 2 bars? -> value [0.251151711235559, -0.10464721570485665] vs SR>0 for both delays; few_trades_dependence: Does profit depend on a handful of trades? -> value 1.100943092701073 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 189361 trials? -> value 0.012014343798680022 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.5873015873015873 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- deflated_sharpe: 30
- few_trades_dependence: 28
- probability_backtest_overfitting: 25
- out_of_sample_validation: 11
- entry_displacement: 3
- schedule_dependence: 1
- latency_plus1: 1

Final status of all 30 examined strategies: {'REJECTED': 28, 'OVERFIT': 2}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-10-01 00:00:00+00:00, horizon 1 bars. Conditions: sess_bar in quintile 1/5 (current value 2); close_loc in quintile 2/5 (current value 0.2358); hour in quintile 5/5 (current value 20); regime == 0
Sample size 806 (2005-01-20 to 2026-09-24).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.0226% | 34.0% | 30.8%-37.3% | 35.7% |
| B_flat | within +/-0.0226% | 33.9% | 30.7%-37.2% | 28.7% |
| C_down | < -0.0226% | 32.1% | 29.0%-35.4% | 35.6% |

Test vs baseline: p = 0.004 -> conditions are informative.
Invalidated if: sess_bar leaves quintile 1; close_loc leaves quintile 2; hour leaves quintile 5; regime changes

- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- validation/evaluate: 30

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
