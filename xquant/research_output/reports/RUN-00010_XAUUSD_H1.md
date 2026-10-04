# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 30 candidate strategies examined; none survived. Outcome: {'REJECTED': 30}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00010 |
| Asset | XAUUSD_H1 |
| Timeframe | 1h |
| Historical period | 2008-01-01 01:00:00+00:00 to 2026-10-01 00:00:00+00:00 (112933 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | b7a71cf0475f238f |
| Mode / budget used | standard - 12 experiments, 30 strategies examined, 9.22 min |
| Backtests counted as trials (all runs on this dataset) | 7099 |

**Splits** (chronological, embargoed): TRAIN 2008-01-01 to 2018-12-31 (67108 bars); VALIDATION 2019-01-09 to 2020-12-31 (11717 bars); TEST 2021-01-11 to 2022-12-30 (11702 bars); FINAL 2023-01-10 to 2026-10-01 (22046 bars)

## Data

- provenance: {'bid_files': 225, 'bid_missing_periods': [], 'ask_files': 225, 'ask_missing_periods': [], 'bars': 112933, 'flat_zero_volume_dropped': 51419, 'spread_median': 0.36599999999998545, 'volume': 'Dukascopy tick volume (not exchange volume)', 'seconds': 0.8, 'field_order': 'open,close,low,high (verified by checks)'}
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

400 candidate features, 1960 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **27** ['close_loc', 'ret_1', 'shock_1', 'ret_2', 'diff(fromhigh_20,1)', 'mul(diff(zdist_60,1),range_vol)', 'streak', 'rank(zscore(diff(fromlow_250,1),20),60)', 'zscore(zscore(skew_20,20),20)', 'ret_3']
Status counts: {'REJECTED': 1748, 'NOT_CONFIRMED': 139, 'TOO_COMPLEX': 44, 'CONFIRMED': 29}

## Top hypotheses

4475 hypotheses (4475 new, 0 reused from memory). Status counts: {'REJECTED': 4453, 'OVERFIT': 19, 'VALIDATION': 3}

| ID | Hypothesis | n | effect size | p | q | confirm p | status |
|---|---|---|---|---|---|---|---|
| HYP-012177 | When hour == 16, next 3-bar return differs from baseline | 1950 | 0.070 | 0.00000 | 0.0006 | 0.0015 | VALIDATION |
| HYP-012178 | When hour == 16, next 6-bar return differs from baseline | 1950 | 0.061 | 0.00020 | 0.0418 | 0.0012 | VALIDATION |
| HYP-012182 | When hour == 17, next 3-bar return differs from baseline | 1950 | 0.057 | 0.00024 | 0.0479 | 0.0009 | VALIDATION |

Strongest hypotheses that failed confirmation (OVERFIT):

- HYP-012186: When hour == 18, next 1-bar return differs from baseline - discovery p=0.00000, confirmation p=0.297, confirmation effect 0.00017 vs 0.00051
- HYP-012181: When hour == 17, next 1-bar return differs from baseline - discovery p=0.00000, confirmation p=0.006, confirmation effect 0.00014 vs -0.00025
- HYP-012187: When hour == 18, next 3-bar return differs from baseline - discovery p=0.00000, confirmation p=0.876, confirmation effect 0.00006 vs 0.00055
- HYP-012188: When hour == 18, next 6-bar return differs from baseline - discovery p=0.00000, confirmation p=0.451, confirmation effect 0.00036 vs 0.00063
- HYP-012257: When volume_z <= -1.142 (bottom 10%), next 3-bar return differs from baseline - discovery p=0.00000, confirmation p=0.652, confirmation effect 0.00003 vs 0.00032

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| open_exploration | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| regime_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |
| macro_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |

## Top strategies

### Strategy #1 - STR-000375 - **REJECTED**

**Rules:** LONG when rank(zscore(fromlow_250,20),250) in top 5% AND x_vix_chg20 in bottom 15%; exit after 20 bars, stop 1.5 x vol x sqrt(hold), take-profit 3.0 x vol x sqrt(hold)

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 20 bars, or stop at 1.5 x vol x sqrt(hold), or take-profit at 3.0 x vol x sqrt(hold)
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 4  |  Composite score: 3.86

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 82.51% | 5.55% | 1.85 | 1.04 | 1.65 | 9.87% | 272 | 22.1 bps | 54.78% |
| VALIDATION | 18.01% | 8.89% | 2.10 | 1.61 | 2.57 | 5.20% | 61 | 27.1 bps | 55.74% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 1.00, positive windows 83.33%, efficiency 0.88; expanding OOS Sharpe 0.91

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 10.15%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.80, x3: SR 0.49, latency_plus1: SR 0.88, entry_shift_+1: SR 0.98, entry_shift_+2: SR 0.81

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 69.23%

**Overfitting risk:** deflated Sharpe probability 0.383 (after 7099 trials); PBO 0.33; IS->OOS Sharpe ratio 1.54

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.608930417036074, "pf": 2.102262113171417, "trad | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 335 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 1.002512002109525, "positive_windows": 0.8333 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.802 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.488 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.879 | SR>0 |
| entry_displacement | reject | PASS | [0.9807670052836157, 0.8057498746406844] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.692 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.643 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.636 | > 0 |
| other_regimes | reject | PASS | 0.394 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.262 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.44862921033050224, "phase1": 0.3159137615945438 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.383 | >= 0.95 |
| probability_backtest_overfitting | overfit | PASS | 0.329 | <= 0.5 |

**Why it is ranked here:** passed 18 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.6433626697576996 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 7099 trials? -> value 0.3831532254767671 vs >= 0.95

### Strategy #2 - STR-000361 - **REJECTED**

**Rules:** LONG when x_vix_chg20 in bottom 15% AND rank(zscore(fromlow_250,20),250) in top 5%; exit after 20 bars, stop 1.5 x vol x sqrt(hold)

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 20 bars, or stop at 1.5 x vol x sqrt(hold)
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 3.80

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 92.41% | 6.05% | 1.93 | 1.06 | 1.74 | 9.18% | 272 | 24.1 bps | 54.78% |
| VALIDATION | 17.16% | 8.48% | 2.05 | 1.52 | 2.40 | 5.20% | 61 | 26.0 bps | 55.74% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.91, positive windows 66.67%, efficiency 0.76; expanding OOS Sharpe 0.87

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 10.45%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.82, x3: SR 0.52, latency_plus1: SR 0.91, entry_shift_+1: SR 1.00, entry_shift_+2: SR 0.81

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 61.54%

**Overfitting risk:** deflated Sharpe probability 0.405 (after 7099 trials); PBO 0.29; IS->OOS Sharpe ratio 1.43

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.5174381558670678, "pf": 2.054041105548445, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 335 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.9093746186628036, "positive_windows": 0.666 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.817 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.521 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.910 | SR>0 |
| entry_displacement | reject | PASS | [1.0025305879111333, 0.8058275485603696] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.615 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.687 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.684 | > 0 |
| other_regimes | reject | PASS | 0.451 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.249 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.4146652977219514, "phase1": 0.2825518603993766} | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.405 | >= 0.95 |
| probability_backtest_overfitting | overfit | PASS | 0.290 | <= 0.5 |

**Why it is ranked here:** passed 18 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.6869632415471758 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 7099 trials? -> value 0.4050403422919544 vs >= 0.95

### Strategy #3 - STR-000364 - **REJECTED**

**Rules:** LONG when x_vix_chg20 in bottom 20% AND rank(zscore(fromlow_250,20),250) in top 5%; exit after 20 bars, stop 1.5 x vol x sqrt(hold), take-profit 2.0 x vol x sqrt(hold)

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 20 bars, or stop at 1.5 x vol x sqrt(hold), or take-profit at 2.0 x vol x sqrt(hold)
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 4  |  Composite score: 3.76

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 62.00% | 4.43% | 1.45 | 0.80 | 1.21 | 10.80% | 378 | 12.8 bps | 52.65% |
| VALIDATION | 20.10% | 9.88% | 1.96 | 1.74 | 2.85 | 3.90% | 80 | 22.9 bps | 57.50% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.44, positive windows 83.33%, efficiency 0.68; expanding OOS Sharpe 0.71

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 13.81%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.52, x3: SR 0.11, latency_plus1: SR 0.75, entry_shift_+1: SR 0.65, entry_shift_+2: SR 0.41

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 69.23%

**Overfitting risk:** deflated Sharpe probability 0.130 (after 7099 trials); PBO 0.29; IS->OOS Sharpe ratio 2.19

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.7429325180729482, "pf": 1.9619306147894402, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 460 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.4449363005187204, "positive_windows": 0.833 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.518 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.113 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.750 | SR>0 |
| entry_displacement | reject | PASS | [0.646592915242106, 0.4144250592943628] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.692 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.781 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.543 | > 0 |
| other_regimes | reject | PASS | 0.360 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.264 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.23224321917102464, "phase1": 0.037296907175233} | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.130 | >= 0.95 |
| probability_backtest_overfitting | overfit | PASS | 0.290 | <= 0.5 |

**Why it is ranked here:** passed 18 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.7813993315345149 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 7099 trials? -> value 0.1297955080984911 vs >= 0.95

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- few_trades_dependence: 30
- deflated_sharpe: 30
- probability_backtest_overfitting: 20
- out_of_sample_validation: 6
- schedule_dependence: 5
- spread_slippage_x2: 5
- monte_carlo_loss_probability: 4
- walk_forward: 4
- other_years: 4
- beats_random_entries: 3
- parameter_perturbation: 3
- other_regimes: 2
- single_event_dependence: 2
- latency_plus1: 1
- entry_displacement: 1
- randomized_execution: 1
- data_perturbation: 1

Final status of all 30 examined strategies: {'REJECTED': 30}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-10-01 00:00:00+00:00, horizon 1 bars. Conditions: hour in quintile 5/5 (current value 20); close_loc in quintile 5/5 (current value 0.853); ret_1 in quintile 4/5 (current value 0.0003863); regime == 0
Sample size 408 (2008-01-04 to 2026-09-29).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.0434% | 29.9% | 25.7%-34.5% | 36.5% |
| B_flat | within +/-0.0434% | 35.3% | 30.8%-40.0% | 28.6% |
| C_down | < -0.0434% | 34.8% | 30.3%-39.5% | 35.0% |

Test vs baseline: p = 0.004 -> conditions are informative.
Invalidated if: hour leaves quintile 5; close_loc leaves quintile 5; ret_1 leaves quintile 4; regime changes

- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- validation/evaluate: 30

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
