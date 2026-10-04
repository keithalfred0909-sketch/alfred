# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 30 candidate strategies examined; none survived. Outcome: {'REJECTED': 30}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00004 |
| Asset | EURUSD_H1 |
| Timeframe | 1h |
| Historical period | 2005-01-02 23:00:00+00:00 to 2026-10-01 00:00:00+00:00 (135749 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | ae17a1577bcfcc70 |
| Mode / budget used | standard - 12 experiments, 30 strategies examined, 9.8 min |
| Backtests counted as trials (all runs on this dataset) | 7425 |

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

81 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 5.**

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
- INSUFFICIENT DATA for: regime_discovery

## Macro discoveries

32 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- Descriptive - macro_data_limits: Macro series are latest-vintage (revised) values with conservative publication lags; no consensus data => no surprise analysis {}
- INSUFFICIENT DATA for: CPI, PCE, NFP, Unemployment rate, Average hourly earnings, GDP, PMI, Fed rate decision, ECB rate decision, Central bank statements

## News discoveries

0 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- INSUFFICIENT DATA for: news_predictive_power

## Feature discovery

400 candidate features, 1960 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **32** ['close_loc', 'ret_3', 'streak', 'zdist_10', 'fromlow_20', 'ret_2', 'zdist_20', 'shock_1', 'ret_1', 'fromhigh_20']
Status counts: {'REJECTED': 1829, 'TOO_COMPLEX': 80, 'CONFIRMED': 41, 'NOT_CONFIRMED': 10}

## Top hypotheses

4485 hypotheses (4485 new, 0 reused from memory). Status counts: {'REJECTED': 4471, 'VALIDATION': 9, 'OVERFIT': 5}

| ID | Hypothesis | n | effect size | p | q | confirm p | status |
|---|---|---|---|---|---|---|---|
| HYP-005406 | When hour == 6, next 1-bar return differs from baseline | 2187 | -0.110 | 0.00000 | 0.0002 | 0.0070 | VALIDATION |
| HYP-005402 | When hour == 5, next 3-bar return differs from baseline | 2187 | -0.101 | 0.00000 | 0.0032 | 0.0001 | VALIDATION |
| HYP-005482 | When hour == 21, next 3-bar return differs from baseline | 2186 | 0.085 | 0.00000 | 0.0000 | 0.0198 | VALIDATION |
| HYP-005483 | When hour == 21, next 6-bar return differs from baseline | 2186 | 0.082 | 0.00000 | 0.0004 | 0.0291 | VALIDATION |
| HYP-005433 | When hour == 11, next 6-bar return differs from baseline | 2186 | 0.075 | 0.00007 | 0.0332 | 0.0000 | VALIDATION |
| HYP-005462 | When hour == 17, next 3-bar return differs from baseline | 2187 | -0.071 | 0.00002 | 0.0198 | 0.0003 | VALIDATION |
| HYP-005481 | When hour == 21, next 1-bar return differs from baseline | 2186 | 0.069 | 0.00003 | 0.0236 | 0.0485 | VALIDATION |
| HYP-005478 | When hour == 20, next 6-bar return differs from baseline | 2187 | 0.064 | 0.00005 | 0.0332 | 0.0352 | VALIDATION |
| HYP-001471 | When close_loc <= 0.1272 (bottom 10%), next 1-bar return differs from baseline | 5249 | 0.060 | 0.00013 | 0.0459 | 0.0000 | VALIDATION |

Strongest hypotheses that failed confirmation (OVERFIT):

- HYP-005487: When hour == 22, next 3-bar return differs from baseline - discovery p=0.00006, confirmation p=0.058, confirmation effect 0.00009 vs 0.00012
- HYP-001957: When rank(fromlow_250,60) >= 0.9833 (top 10%), next 3-bar return differs from baseline - discovery p=0.00008, confirmation p=0.529, confirmation effect -0.00005 vs -0.00019
- HYP-005486: When hour == 22, next 1-bar return differs from baseline - discovery p=0.00011, confirmation p=0.077, confirmation effect 0.00006 vs 0.00007
- HYP-001958: When rank(fromlow_250,60) >= 0.9833 (top 10%), next 6-bar return differs from baseline - discovery p=0.00014, confirmation p=0.502, confirmation effect -0.00008 vs -0.00032
- HYP-001968: When rank(fromlow_250,60) >= 0.9 (top 20%), next 6-bar return differs from baseline - discovery p=0.00016, confirmation p=0.624, confirmation effect -0.00004 vs -0.00024

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| open_exploration | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| regime_conditioned | STOPPED | 0 | 0 | evidence insufficient: no regime model |
| macro_conditioned | STOPPED | 2 | 10 | budget: max_strategies (30) examined |

## Top strategies

### Strategy #1 - STR-000111 - **REJECTED**

**Rules:** SHORT when skew_20 in bottom 15% AND efficiency_20 in top 30% AND vol_5 in top 30%; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 1.64

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 43.49% | 3.05% | 1.50 | 0.86 | 1.31 | 6.50% | 421 | 8.6 bps | 53.21% |
| VALIDATION | 0.48% | 0.16% | 1.06 | 0.09 | 0.13 | 2.74% | 56 | 0.9 bps | 53.57% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.78, positive windows 100.00%, efficiency 0.70; expanding OOS Sharpe 0.59

**Monte Carlo:** P(loss) under trade bootstrap 0.20%, 95th pct max DD 10.42%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.54, x3: SR 0.32, latency_plus1: SR 0.66, entry_shift_-1: SR 2.98, entry_shift_+1: SR 0.65

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 73.33%

**Overfitting risk:** deflated Sharpe probability 0.209 (after 7425 trials); PBO 0.84; IS->OOS Sharpe ratio 0.11

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.09127120120414979, "pf": 1.0585068454144642, "t | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 479 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.7812680704675627, "positive_windows": 1.0} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.540 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.320 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.657 | SR>0 |
| entry_displacement | reject | PASS | [2.9779454455579613, 0.6494113089801594] | SR>0 both ways |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.733 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.956 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.334 | > 0 |
| schedule_dependence | reject | PASS | 0.443 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.05187174996483835, "phase1": 0.1057968972260413 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.002 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.209 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.841 | <= 0.5 |

**Why it is ranked here:** passed 16 of 19 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.956135220953933 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 7425 trials? -> value 0.20878216518727194 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.8412698412698413 vs <= 0.5

### Strategy #2 - STR-000120 - **REJECTED**

**Rules:** SHORT when ret_5 in top 20% AND dom == 5; exit after 15 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 15 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 1.58

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 15.33% | 1.19% | 1.90 | 0.68 | 1.10 | 2.91% | 98 | 14.6 bps | 60.20% |
| VALIDATION | 0.35% | 0.12% | 1.15 | 0.13 | 0.18 | 1.26% | 20 | 1.7 bps | 50.00% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.54, positive windows 83.33%, efficiency 0.56; expanding OOS Sharpe 0.55

**Monte Carlo:** P(loss) under trade bootstrap 1.90%, 95th pct max DD 6.74%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.46, x3: SR 0.35, latency_plus1: SR 0.68, entry_shift_-1: SR -0.08, entry_shift_+1: SR 0.68

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 66.67%

**Overfitting risk:** deflated Sharpe probability 0.069 (after 7425 trials); PBO 0.92; IS->OOS Sharpe ratio 0.19

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.12828465484444448, "pf": 1.1473624710483157, "t | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 119 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.5353855674885473, "positive_windows": 0.833 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.461 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.351 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.683 | SR>0 |
| entry_displacement | reject | FAIL | [-0.07797157078812221, 0.6832734685013867] | SR>0 both ways |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.667 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.804 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.100 | > 0 |
| schedule_dependence | reject | PASS | 0.302 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.46068217105213505, "phase1": 0.4106323112582027 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.019 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.069 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.917 | <= 0.5 |

**Why it is ranked here:** passed 15 of 19 decisive/informative attacks.

**Why it might fail:** entry_displacement: Does it survive entries displaced by +/-1 bar? -> value [-0.07797157078812221, 0.6832734685013867] vs SR>0 both ways; few_trades_dependence: Does profit depend on a handful of trades? -> value 0.8040480528597839 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 7425 trials? -> value 0.06898114582938902 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.9166666666666666 vs <= 0.5

### Strategy #3 - STR-000114 - **REJECTED**

**Rules:** SHORT when skew_20 in bottom 15% AND vol_5 in top 30% AND efficiency_20 in top 30%; exit after 15 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 15 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 1.56

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 33.56% | 2.44% | 1.42 | 0.75 | 1.13 | 6.77% | 459 | 6.3 bps | 52.29% |
| VALIDATION | 0.36% | 0.12% | 1.05 | 0.08 | 0.11 | 2.51% | 57 | 0.6 bps | 45.61% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.66, positive windows 66.67%, efficiency 0.70; expanding OOS Sharpe 0.56

**Monte Carlo:** P(loss) under trade bootstrap 0.30%, 95th pct max DD 10.65%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.41, x3: SR 0.15, latency_plus1: SR 0.49, entry_shift_-1: SR 3.10, entry_shift_+1: SR 0.48

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 66.67%

**Overfitting risk:** deflated Sharpe probability 0.113 (after 7425 trials); PBO 0.84; IS->OOS Sharpe ratio 0.11

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.0789218326087316, "pf": 1.0455493694957105, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 518 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.6647016685592065, "positive_windows": 0.666 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.405 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.148 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.486 | SR>0 |
| entry_displacement | reject | PASS | [3.1000450219143323, 0.479241654482589] | SR>0 both ways |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.667 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 1.053 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.258 | > 0 |
| schedule_dependence | reject | PASS | 0.466 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.036340488409521705, "phase1": 0.110184487574602 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.003 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.113 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.841 | <= 0.5 |

**Why it is ranked here:** passed 16 of 19 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 1.0530540270190198 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 7425 trials? -> value 0.1134492901289228 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.8412698412698413 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- few_trades_dependence: 30
- deflated_sharpe: 30
- probability_backtest_overfitting: 30
- out_of_sample_validation: 26
- entry_displacement: 13
- schedule_dependence: 4
- other_years: 3
- spread_slippage_x2: 2
- monte_carlo_loss_probability: 2
- walk_forward: 2
- beats_random_entries: 1
- single_event_dependence: 1

Final status of all 30 examined strategies: {'REJECTED': 30}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-10-01 00:00:00+00:00, horizon 1 bars. Conditions: hour in quintile 5/5 (current value 20); close_loc in quintile 2/5 (current value 0.2358); ret_3 in quintile 3/5 (current value -0.0002207)
Sample size 1593 (2005-01-05 to 2026-09-24).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.0226% | 28.1% | 25.9%-30.3% | 35.7% |
| B_flat | within +/-0.0226% | 41.3% | 38.9%-43.7% | 28.7% |
| C_down | < -0.0226% | 30.6% | 28.4%-32.9% | 35.6% |

Test vs baseline: p = 0.000 -> conditions are informative.
Invalidated if: hour leaves quintile 5; close_loc leaves quintile 2; ret_3 leaves quintile 3

- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- validation/evaluate: 30

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
