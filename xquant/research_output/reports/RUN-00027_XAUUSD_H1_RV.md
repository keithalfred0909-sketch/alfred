# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 30 candidate strategies examined; none survived. Outcome: {'REJECTED': 30}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00027 |
| Asset | XAUUSD_H1_RV |
| Timeframe | 1h |
| Historical period | 2008-01-01 01:00:00+00:00 to 2026-10-01 00:00:00+00:00 (112933 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | d181a911aaa76f99 |
| Mode / budget used | standard - 12 experiments, 30 strategies examined, 8.62 min |
| Backtests counted as trials (all runs on this dataset) | 6806 |

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
- Exogenous `px_silver`: OK - XAGUSD hourly mid close (Dukascopy), known at the same bar close (lag 0 days)

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

40 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- Descriptive - macro_data_limits: Macro series are latest-vintage (revised) values with conservative publication lags; no consensus data => no surprise analysis {}
- INSUFFICIENT DATA for: CPI, PCE, NFP, Unemployment rate, Average hourly earnings, GDP, PMI, Fed rate decision, ECB rate decision, Central bank statements

## News discoveries

0 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- INSUFFICIENT DATA for: news_predictive_power

## Feature discovery

400 candidate features, 1910 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **24** ['close_loc', 'ret_1', 'shock_1', 'ret_2', 'streak', 'diff(ret_10,1)', 'rank(diff(rank(zdist_250,60),1),60)', 'x_px_silver_div1', 'diff(zscore(zscore(zdist_250,20),20),1)', 'diff(x_px_silver_div20,1)']
Status counts: {'REJECTED': 1639, 'NOT_CONFIRMED': 201, 'TOO_COMPLEX': 45, 'CONFIRMED': 25}

## Top hypotheses

4825 hypotheses (4825 new, 0 reused from memory). Status counts: {'REJECTED': 4790, 'OVERFIT': 26, 'VALIDATION': 9}

| ID | Hypothesis | n | effect size | p | q | confirm p | status |
|---|---|---|---|---|---|---|---|
| HYP-040795 | When sess_bar == 0, next 1-bar return differs from baseline | 1978 | 0.173 | 0.00000 | 0.0000 | 0.0305 | VALIDATION |
| HYP-040796 | When sess_bar == 0, next 3-bar return differs from baseline | 1978 | 0.106 | 0.00000 | 0.0000 | 0.0362 | VALIDATION |
| HYP-040736 | When hour == 16, next 3-bar return differs from baseline | 1950 | 0.070 | 0.00000 | 0.0004 | 0.0015 | VALIDATION |
| HYP-040906 | When sess_bar == 22, next 3-bar return differs from baseline | 1938 | 0.069 | 0.00000 | 0.0004 | 0.0030 | VALIDATION |
| HYP-040902 | When sess_bar == 21, next 6-bar return differs from baseline | 1947 | 0.063 | 0.00017 | 0.0290 | 0.0035 | VALIDATION |
| HYP-040907 | When sess_bar == 22, next 6-bar return differs from baseline | 1938 | 0.061 | 0.00017 | 0.0290 | 0.0014 | VALIDATION |
| HYP-040737 | When hour == 16, next 6-bar return differs from baseline | 1950 | 0.061 | 0.00020 | 0.0315 | 0.0012 | VALIDATION |
| HYP-040732 | When hour == 15, next 6-bar return differs from baseline | 1950 | 0.060 | 0.00032 | 0.0444 | 0.0236 | VALIDATION |
| HYP-040741 | When hour == 17, next 3-bar return differs from baseline | 1950 | 0.057 | 0.00024 | 0.0366 | 0.0009 | VALIDATION |

Strongest hypotheses that failed confirmation (OVERFIT):

- HYP-040745: When hour == 18, next 1-bar return differs from baseline - discovery p=0.00000, confirmation p=0.297, confirmation effect 0.00017 vs 0.00051
- HYP-040910: When sess_bar == 23, next 1-bar return differs from baseline - discovery p=0.00000, confirmation p=0.282, confirmation effect 0.00018 vs -0.00029
- HYP-040740: When hour == 17, next 1-bar return differs from baseline - discovery p=0.00000, confirmation p=0.006, confirmation effect 0.00014 vs -0.00025
- HYP-040746: When hour == 18, next 3-bar return differs from baseline - discovery p=0.00000, confirmation p=0.876, confirmation effect 0.00006 vs 0.00055
- HYP-040747: When hour == 18, next 6-bar return differs from baseline - discovery p=0.00000, confirmation p=0.451, confirmation effect 0.00036 vs 0.00063

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| open_exploration | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| regime_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |
| macro_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |

## Top strategies

### Strategy #1 - STR-000766 - **REJECTED**

**Rules:** LONG when efficiency_20 in bottom 20% AND efficiency_10 in bottom 5% AND ret_5 in top 20%; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 2.99

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 30.87% | 2.44% | 1.69 | 0.66 | 1.02 | 6.71% | 125 | 21.5 bps | 63.20% |
| VALIDATION | 4.36% | 2.22% | 2.53 | 1.07 | 1.64 | 2.28% | 10 | 42.7 bps | 60.00% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.38, positive windows 83.33%, efficiency 0.65; expanding OOS Sharpe 0.47

**Monte Carlo:** P(loss) under trade bootstrap 0.90%, 95th pct max DD 11.49%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.49, x3: SR 0.30, latency_plus1: SR 0.68, entry_shift_+1: SR 0.68, entry_shift_+2: SR 0.65

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 87.50%; profitable years 92.31%

**Overfitting risk:** deflated Sharpe probability 0.054 (after 6806 trials); PBO 0.43; IS->OOS Sharpe ratio 1.63

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.0731973974373097, "pf": 2.5321911794295953, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 135 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.37931017641597464, "positive_windows": 0.83 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.491 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.298 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.682 | SR>0 |
| entry_displacement | reject | PASS | [0.6822411619950098, 0.6450285958232918] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.923 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.620 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.276 | > 0 |
| other_regimes | reject | FAIL | 0.880 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.391 | <= 60% |
| data_perturbation | overfit | PASS | 0.875 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.3927753413824437, "phase1": 0.20222337088017944 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.009 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.054 | >= 0.95 |
| probability_backtest_overfitting | overfit | PASS | 0.429 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.6195131501437037 vs top 5% trades <= 50% of profit; other_regimes: Does it work in more than one market regime? -> value 0.879555567275521 vs <= 85% from one regime; deflated_sharpe: Is the train Sharpe significant after 6806 trials? -> value 0.05423185136484642 vs >= 0.95

### Strategy #2 - STR-000769 - **REJECTED**

**Rules:** SHORT when fromlow_250 in top 30% AND ret_2 in bottom 20% AND shock_1 in top 20%; exit after 20 bars, take-profit 3.0 x vol x sqrt(hold)

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 20 bars, or take-profit at 3.0 x vol x sqrt(hold)
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 4  |  Composite score: 2.91

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 24.95% | 2.02% | 1.73 | 0.56 | 0.88 | 5.12% | 96 | 23.2 bps | 54.17% |
| VALIDATION | 6.99% | 3.54% | 2.47 | 0.96 | 1.48 | 3.25% | 15 | 45.1 bps | 66.67% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.47, positive windows 66.67%, efficiency 0.68; expanding OOS Sharpe 0.89

**Monte Carlo:** P(loss) under trade bootstrap 0.80%, 95th pct max DD 11.26%; random-entry test p = 0.004

**Stress tests:** x2: SR 0.45, x3: SR 0.30, latency_plus1: SR 0.33, entry_shift_+1: SR 0.34, entry_shift_+2: SR 0.36

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 61.54%

**Overfitting risk:** deflated Sharpe probability 0.028 (after 6806 trials); PBO 0.43; IS->OOS Sharpe ratio 1.71

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.9635268657111117, "pf": 2.4743195353010154, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 112 | >= 60 |
| beats_random_entries | reject | PASS | 0.004 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.46570913932726277, "positive_windows": 0.66 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.453 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.298 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.334 | SR>0 |
| entry_displacement | reject | PASS | [0.3358986302101883, 0.3605454905257894] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.615 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.661 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.243 | > 0 |
| other_regimes | reject | PASS | 0.587 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.389 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.07741999011511604, "phase1": -0.24070315718487 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.008 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.028 | >= 0.95 |
| probability_backtest_overfitting | overfit | PASS | 0.429 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.6610523211505379 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 6806 trials? -> value 0.02834948877565235 vs >= 0.95

### Strategy #3 - STR-000771 - **REJECTED**

**Rules:** LONG when fromhigh_20 in top 15% AND month == 1; exit after 15 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction LONG
- Exit: after 15 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 2.80

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 28.91% | 2.31% | 1.68 | 0.64 | 1.00 | 9.71% | 171 | 14.9 bps | 56.14% |
| VALIDATION | 3.12% | 1.59% | 1.71 | 0.69 | 1.12 | 1.91% | 30 | 10.3 bps | 43.33% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.79, positive windows 100.00%, efficiency 0.82; expanding OOS Sharpe 0.85

**Monte Carlo:** P(loss) under trade bootstrap 0.90%, 95th pct max DD 10.96%; random-entry test p = 0.006

**Stress tests:** x2: SR 0.34, x3: SR 0.05, latency_plus1: SR 0.62, entry_shift_+1: SR 0.57, entry_shift_+2: SR 0.62

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 84.62%

**Overfitting risk:** deflated Sharpe probability 0.050 (after 6806 trials); PBO 0.93; IS->OOS Sharpe ratio 1.07

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.6875980528299916, "pf": 1.7133382702575686, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 205 | >= 60 |
| beats_random_entries | reject | PASS | 0.006 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.7930366546899571, "positive_windows": 1.0} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.339 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.052 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.620 | SR>0 |
| entry_displacement | reject | PASS | [0.5710877962931925, 0.6180633949578037] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.846 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.702 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.217 | > 0 |
| other_regimes | reject | PASS | 0.433 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.490 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.23079466777677957, "phase1": 0.1649613841054575 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.009 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.050 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.933 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.7021007060009951 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 6806 trials? -> value 0.050000749482027866 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.9325396825396826 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- few_trades_dependence: 30
- deflated_sharpe: 30
- probability_backtest_overfitting: 25
- out_of_sample_validation: 17
- walk_forward: 8
- other_regimes: 7
- other_years: 6
- monte_carlo_loss_probability: 3
- beats_random_entries: 2
- schedule_dependence: 2
- spread_slippage_x2: 1
- entry_displacement: 1

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
