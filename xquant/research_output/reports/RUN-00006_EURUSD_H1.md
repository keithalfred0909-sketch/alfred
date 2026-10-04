# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 30 candidate strategies examined; none survived. Outcome: {'REJECTED': 30}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00006 |
| Asset | EURUSD_H1 |
| Timeframe | 1h |
| Historical period | 2005-01-02 23:00:00+00:00 to 2026-10-01 00:00:00+00:00 (135749 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | ae17a1577bcfcc70 |
| Mode / budget used | standard - 12 experiments, 30 strategies examined, 11.29 min |
| Backtests counted as trials (all runs on this dataset) | 16345 |

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

400 candidate features, 1960 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **32** ['close_loc', 'ret_3', 'streak', 'zdist_10', 'fromlow_20', 'ret_2', 'zdist_20', 'shock_1', 'ret_1', 'fromhigh_20']
Status counts: {'REJECTED': 1829, 'TOO_COMPLEX': 80, 'CONFIRMED': 41, 'NOT_CONFIRMED': 10}

## Top hypotheses

4485 hypotheses (0 new, 4485 reused from memory). Status counts: {'REJECTED': 4471, 'VALIDATION': 9, 'OVERFIT': 5}

| ID | Hypothesis | n | effect size | p | q | confirm p | status |
|---|---|---|---|---|---|---|---|
| HYP-001471 | When close_loc <= 0.1272 (bottom 10%), next 1-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |
| HYP-005402 | When hour == 5, next 3-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |
| HYP-005406 | When hour == 6, next 1-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |
| HYP-005433 | When hour == 11, next 6-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |
| HYP-005462 | When hour == 17, next 3-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |
| HYP-005478 | When hour == 20, next 6-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |
| HYP-005481 | When hour == 21, next 1-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |
| HYP-005482 | When hour == 21, next 3-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |
| HYP-005483 | When hour == 21, next 6-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| open_exploration | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| regime_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |
| macro_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |

## Top strategies

### Strategy #1 - STR-000178 - **REJECTED**

**Rules:** SHORT when close_loc in top 30% AND volratio_10_120 in top 10% AND zdist_20 in bottom 30% AND regime == 2; exit after 15 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 15 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 4  |  Composite score: 3.19

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 19.12% | 1.47% | 1.98 | 0.88 | 1.44 | 3.57% | 193 | 9.1 bps | 58.03% |
| VALIDATION | 3.40% | 1.13% | 2.46 | 1.09 | 1.83 | 0.94% | 37 | 9.0 bps | 56.76% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.79, positive windows 100.00%, efficiency 0.93; expanding OOS Sharpe 0.99

**Monte Carlo:** P(loss) under trade bootstrap 0.10%, 95th pct max DD 3.50%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.67, x3: SR 0.46, latency_plus1: SR 0.64, entry_shift_+1: SR 0.64, entry_shift_+2: SR 0.76

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 73.33%

**Overfitting risk:** deflated Sharpe probability 0.166 (after 16345 trials); PBO 0.73; IS->OOS Sharpe ratio 1.25

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.0931920976836795, "pf": 2.455330047266489, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 230 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.7879958042835572, "positive_windows": 1.0} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.674 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.455 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.641 | SR>0 |
| entry_displacement | reject | PASS | [0.6437539426187222, 0.75976129774423] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.733 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.563 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.186 | > 0 |
| schedule_dependence | reject | PASS | 0.307 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": 0.1904162924357786, "phase1": -0.0864923593808607 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.001 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.166 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.734 | <= 0.5 |

**Why it is ranked here:** passed 15 of 19 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.5633074952266472 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 16345 trials? -> value 0.1659227063857605 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.7341269841269841 vs <= 0.5

### Strategy #2 - STR-000186 - **REJECTED**

**Rules:** SHORT when hour == 17 AND dom == 4; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 2.13

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 16.22% | 1.26% | 2.00 | 0.71 | 1.10 | 2.68% | 104 | 14.5 bps | 51.92% |
| VALIDATION | 1.32% | 0.44% | 1.57 | 0.43 | 0.62 | 2.02% | 25 | 5.2 bps | 56.00% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.37, positive windows 50.00%, efficiency 0.33; expanding OOS Sharpe 0.58

**Monte Carlo:** P(loss) under trade bootstrap 0.20%, 95th pct max DD 5.18%; random-entry test p = 0.004

**Stress tests:** x2: SR 0.48, x3: SR 0.35, latency_plus1: SR 0.60, entry_shift_+1: SR 0.60, entry_shift_+2: SR 0.57

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 66.67%

**Overfitting risk:** deflated Sharpe probability 0.059 (after 16345 trials); PBO 0.75; IS->OOS Sharpe ratio 0.61

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.43066293122254795, "pf": 1.574515086110352, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 130 | >= 60 |
| beats_random_entries | reject | PASS | 0.004 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.37137724204757094, "positive_windows": 0.5} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.478 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.347 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.597 | SR>0 |
| entry_displacement | reject | PASS | [0.5968883015420138, 0.5724783773094254] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.667 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.570 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.135 | > 0 |
| other_regimes | reject | PASS | 0.393 | <= 85% from one regime |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": -0.07983035116023542, "phase1": 0.674895246587144 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.002 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.059 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.750 | <= 0.5 |

**Why it is ranked here:** passed 16 of 19 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.5697529667554819 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 16345 trials? -> value 0.059385270926369485 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.75 vs <= 0.5

### Strategy #3 - STR-000183 - **REJECTED**

**Rules:** SHORT when x_vix_chg63 in bottom 10% AND ret_20 in bottom 10% AND rank(zscore(diff(fromlow_250,1),20),60) in top 30%; exit after 10 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 10 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 1.86

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 22.26% | 1.69% | 2.26 | 0.89 | 1.50 | 2.67% | 118 | 17.0 bps | 57.63% |
| VALIDATION | 0.18% | 0.06% | 1.54 | 0.13 | 0.19 | 0.64% | 8 | 2.3 bps | 25.00% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.55, positive windows 50.00%, efficiency 0.43; expanding OOS Sharpe 0.88

**Monte Carlo:** P(loss) under trade bootstrap 0.10%, 95th pct max DD 4.51%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.68, x3: SR 0.57, latency_plus1: SR 0.64, entry_shift_+1: SR 0.72, entry_shift_+2: SR 0.84

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 53.33%

**Overfitting risk:** deflated Sharpe probability 0.176 (after 16345 trials); PBO 0.60; IS->OOS Sharpe ratio 0.15

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.13375288180374326, "pf": 1.5429654902025987, "t | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 126 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.5522290045039489, "positive_windows": 0.5} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.685 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.570 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.643 | SR>0 |
| entry_displacement | reject | PASS | [0.7176967285340947, 0.8438788052942315] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.533 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.528 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.147 | > 0 |
| other_regimes | reject | PASS | 0.488 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.429 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": 0.30338152890316916, "phase1": -0.093338243949458 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.001 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.176 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.599 | <= 0.5 |

**Why it is ranked here:** passed 16 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.5278902722456051 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 16345 trials? -> value 0.1760096124819106 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.5992063492063492 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- few_trades_dependence: 30
- deflated_sharpe: 30
- out_of_sample_validation: 25
- probability_backtest_overfitting: 25
- other_regimes: 8
- beats_random_entries: 2
- walk_forward: 1
- other_years: 1
- single_event_dependence: 1

Final status of all 30 examined strategies: {'REJECTED': 30}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-10-01 00:00:00+00:00, horizon 1 bars. Conditions: close_loc in quintile 2/5 (current value 0.2358); hour in quintile 5/5 (current value 20); ret_3 in quintile 3/5 (current value -0.0002207); regime == 0
Sample size 364 (2005-01-20 to 2026-09-24).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.0226% | 32.7% | 28.1%-37.7% | 35.7% |
| B_flat | within +/-0.0226% | 40.7% | 35.7%-45.8% | 28.7% |
| C_down | < -0.0226% | 26.6% | 22.4%-31.4% | 35.6% |

Test vs baseline: p = 0.000 -> conditions are informative.
Invalidated if: close_loc leaves quintile 2; hour leaves quintile 5; ret_3 leaves quintile 3; regime changes

- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- validation/evaluate: 30

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
