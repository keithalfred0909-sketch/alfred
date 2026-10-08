# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 30 candidate strategies examined; none survived. Outcome: {'REJECTED': 30}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00021 |
| Asset | XAUUSD_H1 |
| Timeframe | 1h |
| Historical period | 2008-01-01 01:00:00+00:00 to 2026-10-01 00:00:00+00:00 (112933 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | b7a71cf0475f238f |
| Mode / budget used | standard - 12 experiments, 30 strategies examined, 9.09 min |
| Backtests counted as trials (all runs on this dataset) | 154563 |

**Splits** (chronological, embargoed): TRAIN 2008-01-01 to 2018-12-31 (67108 bars); VALIDATION 2019-01-09 to 2020-12-31 (11717 bars); TEST 2021-01-11 to 2022-12-30 (11702 bars); FINAL 2023-01-10 to 2026-10-01 (22046 bars)

## Data

- provenance: {'bid_files': 225, 'bid_missing_periods': [], 'ask_files': 225, 'ask_missing_periods': [], 'bars': 112933, 'flat_zero_volume_dropped': 51419, 'spread_median': 0.36599999999998545, 'volume': 'Dukascopy tick volume (not exchange volume)', 'seconds': 0.7, 'field_order': 'open,close,low,high (verified by checks)'}
- per-bar spread available (median 0.366)
- cross-check vs None: {'kind': 'monthly_mean', 'matches': 225, 'median_abs_diff_pct': 0.07114135929859877, 'p95_abs_diff_pct': 0.34121201481908325, 'return_corr': 0.9979318298761235, 'note': 'monthly-average check: does not verify intraday timestamps', 'status': 'PASSED'}
- Quality OK: 112933 raw rows -> 112933 bars; 0 missing (holidays/no fix), 0 duplicates, 0 corrupt, 0 bad prints removed, gaps 103
- Exogenous `us_cpi_yoy`: OK - US CPI-U YoY (BLS), 35-day lag (lag 35 days)
- Exogenous `us_10y_yield`: OK - US 10Y yield monthly average (Fed H.15) (lag 1 days)
- Exogenous `vix`: OK - CBOE VIX close, usable from the end of its NY day (lag 0 days)
- Exogenous `brent`: OK - Brent spot (EIA), next NY day (lag 1 days)

## Market discoveries

91 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 7.**

- **ljung_box_returns_10** - Ljung-Box(10) on returns; effect = lag-1 autocorrelation: effect -0.00036, p=0.00000, q=0.0000, replication p=0.00007 (n=67107)
- **runs_test_signs** - Wald-Wolfowitz runs of return signs; effect<0 = longer runs than chance: effect 0.05532, p=0.00000, q=0.0000, replication p=0.00002 (n=67030)
- **big_move_clustering** - P(>2.5 sigma bar next) after a >2.5 sigma bar vs otherwise: effect 0.08206, p=0.00000, q=0.0000, replication p=0.00000 (n=2422)
- **arch_lm_5** - Engle ARCH-LM(5): volatility clustering; effect = R^2: effect 0.04744, p=0.00000, q=0.0000, replication p=0.00000 (n=67102)
- **ljung_box_abs_20** - Ljung-Box(20) on |returns|; effect = lag-1 acf of |r|: effect 0.28409, p=0.00000, q=0.0000, replication p=0.00000 (n=67107)
- **compression_then_expansion** - log(next-20-bar vol / vol60) after the 10% most compressed 5/60 vol ratios (vs rest): effect -0.10629, p=0.00000, q=0.0000, replication p=0.00000 (n=6707)
- **high_vol_mean_reversion** - log(next-20-bar vol / vol60) when vol20 is in its top decile (vs rest): effect -0.12504, p=0.00000, q=0.0000, replication p=0.00194 (n=6710)
- Not replicated: momentum_20_fwd5 (train p=0.00000, validation p=0.1178)
- Not replicated: hour_01 (train p=0.00094, validation p=0.1342)
- Not replicated: hour_02 (train p=0.00365, validation p=0.1888)
- Not replicated: hour_05 (train p=0.00003, validation p=0.0605)
- Not replicated: hour_09 (train p=0.00285, validation p=0.8904)
- Not replicated: hour_16 (train p=0.00252, validation p=0.7712)
- Not replicated: hour_17 (train p=0.00000, validation p=0.0030)
- Descriptive - return_distribution_train: Per-bar log return distribution {"mean_bps": 0.06426486723261299, "ann_vol": 0.1816749757453761, "skew": -0.16289355070566378, "excess_kurtosis": 24.854085823258057, "jarque_bera_p": 0.0, "n": 67107}
- Descriptive - return_distribution_validation: Per-bar log return distribution {"mean_bps": 0.33413645978979595, "ann_vol": 0.16312488973408262, "skew": -0.49385177893153753, "excess_kurtosis": 19.122501576019047, "jarque_bera_p": 0.0, "n": 11717}
- Descriptive - trend_episode_duration: Directional-change episodes (threshold 0.0113 log) vs 200 shuffled-return paths (TRAIN) {"episodes": 1283, "mean_duration": 52.07638347622759, "median_duration": 34.0, "shuffled_mean_duration": 47.053275761434286, "p_longer_than_shuffled": 0.004975124378109453}
- Descriptive - regime_model: GMM regimes on TRAIN, k=5 chosen by BIC {"labels": {"0": "R0: high-vol ranging contracting", "1": "R1: high-vol trending", "2": "R2: low-vol trending contracting", "3": "R3: high-vol trending contracting", "4": "R4: low-vol ranging contracting"}, "persistence": {"0": 0.5585637852124025, "1": 0.7227865126849404, "2": 0.8073394495412844, "3": 0.7793108948795662, "4": 0.6888619854721549}, "occupancy": {"0": 0.23130255859724458, "1": 0.3214

## Macro discoveries

32 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- Descriptive - macro_data_limits: Macro series are latest-vintage (revised) values with conservative publication lags; no consensus data => no surprise analysis {}
- INSUFFICIENT DATA for: CPI, PCE, NFP, Unemployment rate, Average hourly earnings, GDP, PMI, Fed rate decision, ECB rate decision, Central bank statements

## News discoveries

0 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- INSUFFICIENT DATA for: news_predictive_power

## Feature discovery

400 candidate features, 1930 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **34** ['close_loc', 'ret_1', 'shock_1', 'mul(zdist_120,zscore(vol_5,250))', 'ret_2', 'streak', 'mul(diff(fromlow_250,1),efficiency_20)', 'diff(ret_10,1)', 'smooth(rank(close_loc,60),10)', 'rank(diff(rank(zdist_20,60),1),60)']
Status counts: {'REJECTED': 1680, 'NOT_CONFIRMED': 170, 'TOO_COMPLEX': 45, 'CONFIRMED': 35}

## Top hypotheses

4835 hypotheses (640 new, 4195 reused from memory). Status counts: {'REJECTED': 4781, 'OVERFIT': 45, 'VALIDATION': 9}

| ID | Hypothesis | n | effect size | p | q | confirm p | status |
|---|---|---|---|---|---|---|---|
| HYP-028596 | When sess_bar == 0, next 1-bar return differs from baseline | 1978 | 0.173 | 0.00000 | 0.0000 | 0.0305 | VALIDATION |
| HYP-028597 | When sess_bar == 0, next 3-bar return differs from baseline | 1978 | 0.106 | 0.00000 | 0.0000 | 0.0362 | VALIDATION |
| HYP-028707 | When sess_bar == 22, next 3-bar return differs from baseline | 1938 | 0.069 | 0.00000 | 0.0001 | 0.0030 | VALIDATION |
| HYP-028703 | When sess_bar == 21, next 6-bar return differs from baseline | 1947 | 0.063 | 0.00017 | 0.0059 | 0.0035 | VALIDATION |
| HYP-028708 | When sess_bar == 22, next 6-bar return differs from baseline | 1938 | 0.061 | 0.00017 | 0.0059 | 0.0014 | VALIDATION |
| HYP-028698 | When sess_bar == 20, next 6-bar return differs from baseline | 1952 | 0.059 | 0.00074 | 0.0182 | 0.0270 | VALIDATION |
| HYP-012177 | When hour == 16, next 3-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |
| HYP-012178 | When hour == 16, next 6-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |
| HYP-012182 | When hour == 17, next 3-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |

Strongest hypotheses that failed confirmation (OVERFIT):

- HYP-028711: When sess_bar == 23, next 1-bar return differs from baseline - discovery p=0.00000, confirmation p=0.282, confirmation effect 0.00018 vs -0.00029
- HYP-028598: When sess_bar == 0, next 6-bar return differs from baseline - discovery p=0.00000, confirmation p=0.074, confirmation effect 0.00021 vs 0.00054
- HYP-028356: When diff(sub(fromhigh_20,pday_pos),1) <= -0.2997 (bottom 10%), next 1-bar return differs from baseline - discovery p=0.00000, confirmation p=0.806, confirmation effect 0.00001 vs 0.00021
- HYP-028349: When diff(zscore(zscore(zdist_20,20),20),1) <= -0.4375 (bottom 20%), next 12-bar return differs from baseline - discovery p=0.00000, confirmation p=0.435, confirmation effect 0.00009 vs 0.00054
- HYP-028642: When sess_bar == 9, next 3-bar return differs from baseline - discovery p=0.00003, confirmation p=0.839, confirmation effect -0.00002 vs -0.00039

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| open_exploration | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| regime_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |
| macro_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |

## Top strategies

### Strategy #1 - STR-000637 - **REJECTED**

**Rules:** LONG when fromhigh_60 in top 5% AND diff(zscore(zscore(zdist_20,20),20),1) in bottom 20%; exit after 15 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 15 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 4.55

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 39.45% | 3.03% | 1.84 | 0.78 | 1.26 | 5.72% | 208 | 16.0 bps | 53.85% |
| VALIDATION | 16.24% | 8.04% | 3.82 | 2.10 | 3.50 | 2.56% | 37 | 40.7 bps | 67.57% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.69, positive windows 66.67%, efficiency 0.84; expanding OOS Sharpe 0.92

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 7.20%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.64, x3: SR 0.33, latency_plus1: SR 0.86, entry_shift_+1: SR 0.86, entry_shift_+2: SR 0.76

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 69.23%

**Overfitting risk:** deflated Sharpe probability 0.024 (after 154563 trials); PBO 0.84; IS->OOS Sharpe ratio 2.70

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 2.0955009054586373, "pf": 3.8195792748067383, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 246 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.6866154932771608, "positive_windows": 0.666 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.638 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.335 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.861 | SR>0 |
| entry_displacement | reject | PASS | [0.861159019485388, 0.7581666458018366] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.692 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.571 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.427 | > 0 |
| other_regimes | reject | PASS | 0.484 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.346 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.8152186922884858, "phase1": 0.2717073904054033} | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.024 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.837 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.5712753106525862 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 154563 trials? -> value 0.02438206732180477 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.8373015873015873 vs <= 0.5

### Strategy #2 - STR-000638 - **REJECTED**

**Rules:** LONG when diff(zscore(zscore(zdist_20,20),20),1) in bottom 20% AND fromhigh_60 in top 5%; exit after 15 bars, take-profit 3.0 x vol x sqrt(hold)

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 15 bars, or take-profit at 3.0 x vol x sqrt(hold)
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 4.48

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 40.55% | 3.10% | 1.86 | 0.80 | 1.30 | 5.58% | 208 | 16.4 bps | 53.85% |
| VALIDATION | 16.33% | 8.09% | 3.83 | 2.10 | 3.53 | 2.56% | 37 | 40.9 bps | 67.57% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.72, positive windows 66.67%, efficiency 0.75; expanding OOS Sharpe 0.59

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 7.05%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.66, x3: SR 0.36, latency_plus1: SR 0.89, entry_shift_+1: SR 0.87, entry_shift_+2: SR 0.74

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 69.23%

**Overfitting risk:** deflated Sharpe probability 0.030 (after 154563 trials); PBO 0.84; IS->OOS Sharpe ratio 2.62

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 2.1044592414527696, "pf": 3.8341213147198783, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 246 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.7238490975047105, "positive_windows": 0.666 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.661 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.356 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.886 | SR>0 |
| entry_displacement | reject | PASS | [0.8662976918145427, 0.7371103892530226] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.692 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.583 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.435 | > 0 |
| other_regimes | reject | PASS | 0.497 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.342 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.8263845593249756, "phase1": 0.26549958867655704 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.030 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.837 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.5831572539126527 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 154563 trials? -> value 0.02985381533298285 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.8373015873015873 vs <= 0.5

### Strategy #3 - STR-000636 - **REJECTED**

**Rules:** LONG when fromhigh_60 in top 5% AND diff(zscore(zscore(zdist_20,20),20),1) in bottom 20%; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 4.33

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 63.19% | 4.49% | 2.03 | 1.00 | 1.64 | 6.80% | 206 | 23.8 bps | 55.83% |
| VALIDATION | 17.55% | 8.67% | 3.07 | 1.87 | 2.96 | 3.32% | 37 | 43.7 bps | 56.76% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.85, positive windows 50.00%, efficiency 0.77; expanding OOS Sharpe 0.88

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 8.30%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.85, x3: SR 0.59, latency_plus1: SR 0.90, entry_shift_+1: SR 0.90, entry_shift_+2: SR 0.81

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 69.23%

**Overfitting risk:** deflated Sharpe probability 0.116 (after 154563 trials); PBO 0.84; IS->OOS Sharpe ratio 1.87

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.8650244392457453, "pf": 3.0704192063648668, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 244 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.8495144881609714, "positive_windows": 0.5} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.854 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.591 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.904 | SR>0 |
| entry_displacement | reject | PASS | [0.9039006733330595, 0.8094624487422046] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.692 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.587 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.579 | > 0 |
| other_regimes | reject | PASS | 0.545 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.281 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.9614221779690413, "phase1": 0.4418876354660746} | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.116 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.837 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.5873151518192992 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 154563 trials? -> value 0.11564645341589957 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.8373015873015873 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- few_trades_dependence: 30
- deflated_sharpe: 30
- probability_backtest_overfitting: 20
- out_of_sample_validation: 12
- other_regimes: 7
- walk_forward: 7
- entry_displacement: 5
- spread_slippage_x2: 5
- monte_carlo_loss_probability: 4
- other_years: 2
- beats_random_entries: 2
- single_event_dependence: 2
- schedule_dependence: 1
- parameter_perturbation: 1
- latency_plus1: 1
- randomized_execution: 1

Final status of all 30 examined strategies: {'REJECTED': 30}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-10-01 00:00:00+00:00, horizon 1 bars. Conditions: sess_bar in quintile 1/5 (current value 1); hour in quintile 5/5 (current value 20); close_loc in quintile 5/5 (current value 0.853); regime == 0
Sample size 970 (2008-01-04 to 2026-09-15).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.0434% | 33.7% | 30.8%-36.7% | 36.5% |
| B_flat | within +/-0.0434% | 30.1% | 27.3%-33.1% | 28.6% |
| C_down | < -0.0434% | 36.2% | 33.2%-39.3% | 35.0% |

Test vs baseline: p = 0.200 -> NOT informative.
Invalidated if: sess_bar leaves quintile 1; hour leaves quintile 5; close_loc leaves quintile 5; regime changes

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
