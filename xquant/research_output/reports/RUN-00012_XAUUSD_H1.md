# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 80 candidate strategies examined; none survived. Outcome: {'REJECTED': 58, 'OVERFIT': 22}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00012 |
| Asset | XAUUSD_H1 |
| Timeframe | 1h |
| Historical period | 2008-01-01 01:00:00+00:00 to 2026-10-01 00:00:00+00:00 (112933 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | b7a71cf0475f238f |
| Mode / budget used | deep - 22 experiments, 80 strategies examined, 60.82 min |
| Backtests counted as trials (all runs on this dataset) | 148168 |

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

1500 candidate features, 7440 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **50** ['close_loc', 'ret_1', 'diff(sub(fromlow_60,vol_120),1)', 'diff(sub(fromlow_60,x_brent),1)', 'shock_1', 'zscore(diff(abs(fromlow_60),1),60)', 'rank(rank(diff(fromhigh_20,1),250),250)', 'diff(mul(fromlow_250,vol_10),1)', 'ret_2', 'diff(fromhigh_20,1)']
Status counts: {'REJECTED': 6690, 'NOT_CONFIRMED': 510, 'TOO_COMPLEX': 179, 'CONFIRMED': 61}

## Top hypotheses

5075 hypotheses (600 new, 4475 reused from memory). Status counts: {'REJECTED': 5038, 'OVERFIT': 33, 'VALIDATION': 4}

| ID | Hypothesis | n | effect size | p | q | confirm p | status |
|---|---|---|---|---|---|---|---|
| HYP-014797 | When diff(skew_20,5) >= 0.4059 (top 20%), next 3-bar return differs from baseline | 9391 | 0.062 | 0.00016 | 0.0139 | 0.0364 | VALIDATION |
| HYP-012177 | When hour == 16, next 3-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |
| HYP-012178 | When hour == 16, next 6-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |
| HYP-012182 | When hour == 17, next 3-bar return differs from baseline | 0 | n/a | n/a | n/a | n/a | VALIDATION |

Strongest hypotheses that failed confirmation (OVERFIT):

- HYP-014494: When mul(diff(fromlow_250,1),fromlow_20) <= -0.1541 (bottom 20%), next 12-bar return differs from baseline - discovery p=0.00000, confirmation p=0.967, confirmation effect 0.00001 vs 0.00059
- HYP-014789: When diff(skew_20,5) >= 0.8977 (top 10%), next 12-bar return differs from baseline - discovery p=0.00001, confirmation p=0.271, confirmation effect 0.00025 vs 0.00091
- HYP-014493: When mul(diff(fromlow_250,1),fromlow_20) <= -0.1541 (bottom 20%), next 6-bar return differs from baseline - discovery p=0.00003, confirmation p=0.964, confirmation effect 0.00000 vs 0.00035
- HYP-014638: When zscore(zscore(fromlow_60,60),60) >= 1.183 (top 20%), next 6-bar return differs from baseline - discovery p=0.00008, confirmation p=0.448, confirmation effect -0.00010 vs 0.00051
- HYP-014788: When diff(skew_20,5) >= 0.8977 (top 10%), next 6-bar return differs from baseline - discovery p=0.00013, confirmation p=0.612, confirmation effect 0.00008 vs 0.00058

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 4 | 20 | budget: max_strategies (80) examined |
| open_exploration | STOPPED | 4 | 20 | budget: max_strategies (80) examined |
| regime_conditioned | STOPPED | 4 | 20 | budget: max_strategies (80) examined |
| macro_conditioned | STOPPED | 4 | 20 | budget: max_strategies (80) examined |

## Top strategies

### Strategy #1 - STR-000583 - **REJECTED**

**Rules:** LONG when fromhigh_60 in top 20% AND rank(zscore(diff(fromlow_250,1),20),60) in bottom 20% AND diff(diff(zscore(zdist_250,60),1),5) in top 10%; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 3.95

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 78.16% | 5.32% | 1.60 | 0.89 | 1.35 | 9.06% | 360 | 16.0 bps | 55.83% |
| VALIDATION | 15.11% | 7.51% | 2.20 | 1.58 | 2.47 | 4.51% | 50 | 28.2 bps | 58.00% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 1.09, positive windows 100.00%, efficiency 1.19; expanding OOS Sharpe 1.04

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 15.36%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.63, x3: SR 0.30, latency_plus1: SR 0.76, entry_shift_+1: SR 0.73, entry_shift_+2: SR 0.64

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 100.00%

**Overfitting risk:** deflated Sharpe probability 0.063 (after 148168 trials); PBO 0.96; IS->OOS Sharpe ratio 1.78

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.5828335950960677, "pf": 2.203282138486092, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 410 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 1.093270221645287, "positive_windows": 1.0} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.634 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.299 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.755 | SR>0 |
| entry_displacement | reject | PASS | [0.7336442245842757, 0.6384894384433528] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 1.000 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.810 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.617 | > 0 |
| other_regimes | reject | PASS | 0.546 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.245 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.4670407782575175, "phase1": 0.32364818485660773 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.063 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.964 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.8098693028874251 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 148168 trials? -> value 0.06281387526391663 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.9642857142857143 vs <= 0.5

### Strategy #2 - STR-000581 - **REJECTED**

**Rules:** LONG when fromhigh_60 in top 10% AND rank(zscore(diff(fromlow_250,1),20),60) in bottom 20% AND diff(diff(zscore(zdist_250,60),1),5) in top 10%; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 3.73

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 90.84% | 5.97% | 1.89 | 1.10 | 1.77 | 5.01% | 304 | 21.3 bps | 57.24% |
| VALIDATION | 13.06% | 6.52% | 2.05 | 1.41 | 2.19 | 4.52% | 47 | 26.1 bps | 55.32% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 1.09, positive windows 100.00%, efficiency 1.11; expanding OOS Sharpe 1.04

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 10.99%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.82, x3: SR 0.51, latency_plus1: SR 0.95, entry_shift_+1: SR 0.95, entry_shift_+2: SR 0.79

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 100.00%

**Overfitting risk:** deflated Sharpe probability 0.200 (after 148168 trials); PBO 0.96; IS->OOS Sharpe ratio 1.29

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.4114517977441305, "pf": 2.049521111475661, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 351 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 1.092806756884726, "positive_windows": 1.0} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.822 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.507 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.952 | SR>0 |
| entry_displacement | reject | PASS | [0.949664607692379, 0.793394319955052] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 1.000 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.682 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.666 | > 0 |
| other_regimes | reject | PASS | 0.596 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.256 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.423424345882126, "phase1": 0.4112604338105468} | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.200 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.964 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.6824262599321302 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 148168 trials? -> value 0.1997077736104662 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.9642857142857143 vs <= 0.5

### Strategy #3 - STR-000585 - **REJECTED**

**Rules:** LONG when fromhigh_60 in top 10% AND rank(zscore(diff(fromlow_250,1),20),60) in bottom 20% AND x_us_10y_yield_chg5 in top 10% AND diff(diff(zscore(zdist_250,60),1),5) in top 10%; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 4  |  Composite score: 3.61

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 87.15% | 5.79% | 1.86 | 1.07 | 1.72 | 5.01% | 301 | 20.8 bps | 56.81% |
| VALIDATION | 13.06% | 6.52% | 2.05 | 1.41 | 2.19 | 4.52% | 47 | 26.1 bps | 55.32% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 1.05, positive windows 100.00%, efficiency 1.12; expanding OOS Sharpe 0.98

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 11.64%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.80, x3: SR 0.48, latency_plus1: SR 0.92, entry_shift_+1: SR 0.92, entry_shift_+2: SR 0.74

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 100.00%

**Overfitting risk:** deflated Sharpe probability 0.172 (after 148168 trials); PBO 0.96; IS->OOS Sharpe ratio 1.32

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.4114517977441305, "pf": 2.049521111475661, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 348 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 1.0520184975124995, "positive_windows": 1.0} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.798 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.485 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.917 | SR>0 |
| entry_displacement | reject | PASS | [0.9150291876658811, 0.7401807965744279] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 1.000 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.700 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.646 | > 0 |
| other_regimes | reject | PASS | 0.605 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.263 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.37988705424680524, "phase1": 0.3685259475572058 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.172 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.964 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.7002256649716091 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 148168 trials? -> value 0.17231331365101077 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.9642857142857143 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- deflated_sharpe: 80
- probability_backtest_overfitting: 75
- few_trades_dependence: 51
- out_of_sample_validation: 33
- walk_forward: 3
- spread_slippage_x2: 2
- latency_plus1: 2
- entry_displacement: 2
- randomized_execution: 2
- monte_carlo_loss_probability: 2
- beats_random_entries: 1
- schedule_dependence: 1

Final status of all 80 examined strategies: {'REJECTED': 58, 'OVERFIT': 22}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-10-01 00:00:00+00:00, horizon 1 bars. Conditions: diff(skew_20,5) in quintile 2/5 (current value -0.1939); hour in quintile 5/5 (current value 20); close_loc in quintile 5/5 (current value 0.853); regime == 0
Sample size 401 (2008-01-08 to 2026-09-29).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.0434% | 34.4% | 29.9%-39.2% | 36.5% |
| B_flat | within +/-0.0434% | 29.7% | 25.4%-34.3% | 28.6% |
| C_down | < -0.0434% | 35.9% | 31.4%-40.7% | 35.0% |

Test vs baseline: p = 0.693 -> NOT informative.
Invalidated if: diff(skew_20,5) leaves quintile 2; hour leaves quintile 5; close_loc leaves quintile 5; regime changes

- Conditional frequencies are not significantly different from the unconditional baseline: the current conditions carry no demonstrated information about the next move.
- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- validation/evaluate: 80

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
