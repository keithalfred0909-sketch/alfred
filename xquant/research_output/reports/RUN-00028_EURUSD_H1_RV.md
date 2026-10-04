# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 30 candidate strategies examined; none survived. Outcome: {'REJECTED': 30}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00028 |
| Asset | EURUSD_H1_RV |
| Timeframe | 1h |
| Historical period | 2005-01-02 23:00:00+00:00 to 2026-10-01 00:00:00+00:00 (135749 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | ac266fad2ecea717 |
| Mode / budget used | standard - 12 experiments, 30 strategies examined, 10.59 min |
| Backtests counted as trials (all runs on this dataset) | 7748 |

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
- Exogenous `px_gbpusd`: OK - GBPUSD hourly mid close (Dukascopy), known at the same bar close (lag 0 days)

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

40 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- Descriptive - macro_data_limits: Macro series are latest-vintage (revised) values with conservative publication lags; no consensus data => no surprise analysis {}
- INSUFFICIENT DATA for: CPI, PCE, NFP, Unemployment rate, Average hourly earnings, GDP, PMI, Fed rate decision, ECB rate decision, Central bank statements

## News discoveries

0 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- INSUFFICIENT DATA for: news_predictive_power

## Feature discovery

400 candidate features, 1910 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **43** ['close_loc', 'ret_3', 'streak', 'zdist_10', 'fromlow_20', 'ret_2', 'sess_pos', 'zdist_20', 'shock_1', 'ret_1']
Status counts: {'REJECTED': 1763, 'TOO_COMPLEX': 80, 'CONFIRMED': 52, 'NOT_CONFIRMED': 15}

## Top hypotheses

5015 hypotheses (5015 new, 0 reused from memory). Status counts: {'REJECTED': 4985, 'VALIDATION': 21, 'OVERFIT': 9}

| ID | Hypothesis | n | effect size | p | q | confirm p | status |
|---|---|---|---|---|---|---|---|
| HYP-046092 | When x_us_cpi_yoy_chg5 <= 0 (bottom 10%), next 6-bar return differs from baseline | 52257 | 0.318 | 0.00029 | 0.0466 | 0.0292 | VALIDATION |
| HYP-046102 | When x_us_cpi_yoy_chg5 <= 0 (bottom 20%), next 6-bar return differs from baseline | 52257 | 0.318 | 0.00029 | 0.0466 | 0.0292 | VALIDATION |
| HYP-045760 | When hour == 6, next 1-bar return differs from baseline | 2187 | -0.110 | 0.00000 | 0.0002 | 0.0070 | VALIDATION |
| HYP-045910 | When sess_bar == 12, next 1-bar return differs from baseline | 2187 | -0.109 | 0.00000 | 0.0002 | 0.0070 | VALIDATION |
| HYP-045756 | When hour == 5, next 3-bar return differs from baseline | 2187 | -0.101 | 0.00000 | 0.0020 | 0.0001 | VALIDATION |
| HYP-045906 | When sess_bar == 11, next 3-bar return differs from baseline | 2187 | -0.100 | 0.00000 | 0.0026 | 0.0001 | VALIDATION |
| HYP-045757 | When hour == 5, next 6-bar return differs from baseline | 2187 | -0.095 | 0.00021 | 0.0376 | 0.0208 | VALIDATION |
| HYP-045907 | When sess_bar == 11, next 6-bar return differs from baseline | 2187 | -0.095 | 0.00021 | 0.0376 | 0.0208 | VALIDATION |
| HYP-045836 | When hour == 21, next 3-bar return differs from baseline | 2186 | 0.085 | 0.00000 | 0.0000 | 0.0198 | VALIDATION |
| HYP-045866 | When sess_bar == 3, next 3-bar return differs from baseline | 2187 | 0.084 | 0.00000 | 0.0000 | 0.0198 | VALIDATION |

Strongest hypotheses that failed confirmation (OVERFIT):

- HYP-042121: When zscore(fromlow_250,20) >= 1.418 (top 20%), next 3-bar return differs from baseline - discovery p=0.00000, confirmation p=0.274, confirmation effect -0.00005 vs -0.00017
- HYP-041737: When x_px_gbpusd_div20 <= -1.337 (bottom 10%), next 6-bar return differs from baseline - discovery p=0.00005, confirmation p=0.969, confirmation effect 0.00000 vs -0.00032
- HYP-045841: When hour == 22, next 3-bar return differs from baseline - discovery p=0.00006, confirmation p=0.058, confirmation effect 0.00009 vs 0.00012
- HYP-045871: When sess_bar == 4, next 3-bar return differs from baseline - discovery p=0.00007, confirmation p=0.058, confirmation effect 0.00009 vs 0.00012
- HYP-045840: When hour == 22, next 1-bar return differs from baseline - discovery p=0.00011, confirmation p=0.077, confirmation effect 0.00006 vs 0.00007

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| open_exploration | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| regime_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |
| macro_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |

## Top strategies

### Strategy #1 - STR-000805 - **REJECTED**

**Rules:** SHORT when skew_20 in bottom 10% AND ret_120 in bottom 20% AND sess_ret in bottom 10%; exit after 10 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 10 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 3.18

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 13.45% | 1.06% | 1.91 | 0.72 | 1.14 | 3.82% | 143 | 8.8 bps | 53.85% |
| VALIDATION | 2.48% | 0.83% | 2.37 | 1.02 | 1.78 | 0.55% | 23 | 10.6 bps | 52.17% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.86, positive windows 66.67%, efficiency 0.72; expanding OOS Sharpe 0.87

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 3.64%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.56, x3: SR 0.37, latency_plus1: SR 0.51, entry_shift_+1: SR 0.51, entry_shift_+2: SR 0.57

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 66.67%

**Overfitting risk:** deflated Sharpe probability 0.090 (after 7748 trials); PBO 0.60; IS->OOS Sharpe ratio 1.42

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.0184497144805378, "pf": 2.373817905591926, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 166 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.8555058235953227, "positive_windows": 0.666 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.557 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.374 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.515 | SR>0 |
| entry_displacement | reject | PASS | [0.5087465732971999, 0.5732887860085039] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.667 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.631 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.131 | > 0 |
| other_regimes | reject | FAIL | 0.972 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.445 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.10065033519737529, "phase1": 0.0728528302844182 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.090 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.599 | <= 0.5 |

**Why it is ranked here:** passed 16 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.6309870641111205 vs top 5% trades <= 50% of profit; other_regimes: Does it work in more than one market regime? -> value 0.9722581536171438 vs <= 85% from one regime; deflated_sharpe: Is the train Sharpe significant after 7748 trials? -> value 0.08955963702399228 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.5992063492063492 vs <= 0.5

### Strategy #2 - STR-000802 - **REJECTED**

**Rules:** SHORT when ret_120 in bottom 20% AND skew_20 in bottom 10% AND fromlow_250 in bottom 30%; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 2.68

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 33.82% | 2.46% | 1.86 | 0.91 | 1.42 | 4.62% | 241 | 12.1 bps | 54.36% |
| VALIDATION | 2.83% | 0.94% | 1.62 | 0.69 | 1.08 | 2.59% | 38 | 7.3 bps | 57.89% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.82, positive windows 66.67%, efficiency 0.76; expanding OOS Sharpe 0.87

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 5.58%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.70, x3: SR 0.53, latency_plus1: SR 0.78, entry_shift_+1: SR 0.76, entry_shift_+2: SR 0.72

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 73.33%

**Overfitting risk:** deflated Sharpe probability 0.260 (after 7748 trials); PBO 0.60; IS->OOS Sharpe ratio 0.76

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.690189130139963, "pf": 1.6242736907471196, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 279 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.8165831146414139, "positive_windows": 0.666 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.701 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.534 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.780 | SR>0 |
| entry_displacement | reject | PASS | [0.7573495351814503, 0.7236577954244588] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.733 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.636 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.280 | > 0 |
| other_regimes | reject | PASS | 0.521 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.322 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": 0.1262319225603137, "phase1": -0.1955038371196541 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.260 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.599 | <= 0.5 |

**Why it is ranked here:** passed 16 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.636010085785265 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 7748 trials? -> value 0.25953823579567037 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.5992063492063492 vs <= 0.5

### Strategy #3 - STR-000801 - **REJECTED**

**Rules:** SHORT when ret_120 in bottom 20% AND skew_20 in bottom 10%; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 2.57

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 35.38% | 2.55% | 1.77 | 0.90 | 1.40 | 5.03% | 266 | 11.4 bps | 53.76% |
| VALIDATION | 2.36% | 0.79% | 1.47 | 0.55 | 0.85 | 2.70% | 41 | 5.7 bps | 56.10% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.81, positive windows 50.00%, efficiency 0.64; expanding OOS Sharpe 0.87

**Monte Carlo:** P(loss) under trade bootstrap 0.10%, 95th pct max DD 6.39%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.67, x3: SR 0.49, latency_plus1: SR 0.80, entry_shift_+1: SR 0.77, entry_shift_+2: SR 0.76

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 80.00%

**Overfitting risk:** deflated Sharpe probability 0.247 (after 7748 trials); PBO 0.60; IS->OOS Sharpe ratio 0.61

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.551039931209416, "pf": 1.4697851770780825, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 307 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.8148680199847461, "positive_windows": 0.5} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.668 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.493 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.802 | SR>0 |
| entry_displacement | reject | PASS | [0.7724651376185687, 0.7575020360622642] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.800 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.742 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.287 | > 0 |
| other_regimes | reject | PASS | 0.526 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.359 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": 0.1338799634123858, "phase1": -0.0278257102095689 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.001 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.247 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.599 | <= 0.5 |

**Why it is ranked here:** passed 16 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.7422953211411504 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 7748 trials? -> value 0.24685973802590733 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.5992063492063492 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- few_trades_dependence: 30
- deflated_sharpe: 30
- probability_backtest_overfitting: 25
- out_of_sample_validation: 20
- schedule_dependence: 7
- spread_slippage_x2: 4
- entry_displacement: 3
- other_years: 3
- other_regimes: 2
- walk_forward: 2
- monte_carlo_loss_probability: 2
- beats_random_entries: 1

Final status of all 30 examined strategies: {'REJECTED': 30}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-10-01 00:00:00+00:00, horizon 1 bars. Conditions: x_us_cpi_yoy_chg5 in quintile 5/5 (current value 0); hour in quintile 5/5 (current value 20); sess_bar in quintile 1/5 (current value 2); regime == 0
Sample size 3896 (2005-01-06 to 2026-09-30).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.0226% | 34.5% | 33.1%-36.1% | 35.7% |
| B_flat | within +/-0.0226% | 33.2% | 31.8%-34.7% | 28.7% |
| C_down | < -0.0226% | 32.2% | 30.8%-33.7% | 35.6% |

Test vs baseline: p = 0.000 -> conditions are informative.
Invalidated if: x_us_cpi_yoy_chg5 leaves quintile 5; hour leaves quintile 5; sess_bar leaves quintile 1; regime changes

- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- validation/evaluate: 30

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
