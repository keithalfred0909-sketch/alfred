# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 30 candidate strategies examined; none survived. Outcome: {'REJECTED': 30}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00026 |
| Asset | EURUSD_H1 |
| Timeframe | 1h |
| Historical period | 2005-01-02 23:00:00+00:00 to 2026-10-01 00:00:00+00:00 (135749 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | ae17a1577bcfcc70 |
| Mode / budget used | standard - 12 experiments, 30 strategies examined, 10.65 min |
| Backtests counted as trials (all runs on this dataset) | 196322 |

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

4805 hypotheses (0 new, 4805 reused from memory). Status counts: {'REJECTED': 4776, 'VALIDATION': 20, 'OVERFIT': 9}

| ID | Hypothesis | n | effect size | p | q | confirm p | status |
|---|---|---|---|---|---|---|---|
| HYP-005406 | When hour == 6, next 1-bar return differs from baseline | 2187 | -0.110 | 0.00000 | 0.0002 | 0.0070 | VALIDATION |
| HYP-029236 | When sess_bar == 12, next 1-bar return differs from baseline | 2187 | -0.109 | 0.00000 | 0.0000 | 0.0070 | VALIDATION |
| HYP-005402 | When hour == 5, next 3-bar return differs from baseline | 2187 | -0.101 | 0.00000 | 0.0032 | 0.0001 | VALIDATION |
| HYP-029232 | When sess_bar == 11, next 3-bar return differs from baseline | 2187 | -0.100 | 0.00000 | 0.0006 | 0.0001 | VALIDATION |
| HYP-029233 | When sess_bar == 11, next 6-bar return differs from baseline | 2187 | -0.095 | 0.00021 | 0.0103 | 0.0208 | VALIDATION |
| HYP-005482 | When hour == 21, next 3-bar return differs from baseline | 2186 | 0.085 | 0.00000 | 0.0000 | 0.0198 | VALIDATION |
| HYP-029192 | When sess_bar == 3, next 3-bar return differs from baseline | 2187 | 0.084 | 0.00000 | 0.0000 | 0.0198 | VALIDATION |
| HYP-005483 | When hour == 21, next 6-bar return differs from baseline | 2186 | 0.082 | 0.00000 | 0.0004 | 0.0291 | VALIDATION |
| HYP-029193 | When sess_bar == 3, next 6-bar return differs from baseline | 2187 | 0.081 | 0.00000 | 0.0001 | 0.0291 | VALIDATION |
| HYP-005433 | When hour == 11, next 6-bar return differs from baseline | 2186 | 0.075 | 0.00007 | 0.0332 | 0.0000 | VALIDATION |

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| open_exploration | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| regime_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |
| macro_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |

## Top strategies

### Strategy #1 - STR-000764 - **REJECTED**

**Rules:** SHORT when zdist_20 in bottom 20% AND zdist_60 in bottom 10% AND sess_pos in top 20%; exit after 15 bars, stop 2.0 x vol x sqrt(hold)

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 15 bars, or stop at 2.0 x vol x sqrt(hold)
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 4  |  Composite score: 2.08

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 17.19% | 1.33% | 2.38 | 0.84 | 1.39 | 3.46% | 96 | 16.5 bps | 58.33% |
| VALIDATION | 1.02% | 0.34% | 1.46 | 0.37 | 0.60 | 1.53% | 21 | 4.8 bps | 52.38% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.74, positive windows 100.00%, efficiency 0.82; expanding OOS Sharpe 0.71

**Monte Carlo:** P(loss) under trade bootstrap 0.30%, 95th pct max DD 4.77%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.65, x3: SR 0.54, latency_plus1: SR 0.54, entry_shift_+1: SR 0.54, entry_shift_+2: SR 0.48

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 73.33%

**Overfitting risk:** deflated Sharpe probability 0.046 (after 196322 trials); PBO 0.67; IS->OOS Sharpe ratio 0.45

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.3743285040375185, "pf": 1.4586220176466176, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 117 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.7443320139900523, "positive_windows": 1.0} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.652 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.536 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.536 | SR>0 |
| entry_displacement | reject | PASS | [0.5366697799734631, 0.4771070702506555] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.733 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.497 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.146 | > 0 |
| other_regimes | reject | PASS | 0.703 | <= 85% from one regime |
| schedule_dependence | reject | FAIL | 0.727 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.2297563701090794, "phase1": 0.02649606544372361 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.003 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.046 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.671 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** schedule_dependence: Does it depend on one weekday/hour? -> value 0.7271900397568024 vs <= 60%; deflated_sharpe: Is the train Sharpe significant after 196322 trials? -> value 0.04583902142932305 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.6706349206349206 vs <= 0.5

### Strategy #2 - STR-000744 - **REJECTED**

**Rules:** SHORT when ret_3 in top 15% AND sess_ret in top 30% AND sess_bar == 9; exit after 3 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 3 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 1.86

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 13.86% | 1.09% | 1.41 | 0.65 | 0.96 | 2.91% | 313 | 4.1 bps | 53.99% |
| VALIDATION | 0.52% | 0.17% | 1.17 | 0.24 | 0.34 | 1.22% | 34 | 1.5 bps | 55.88% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.55, positive windows 66.67%, efficiency 0.43; expanding OOS Sharpe 0.71

**Monte Carlo:** P(loss) under trade bootstrap 0.60%, 95th pct max DD 5.79%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.28, x3: SR -0.05, latency_plus1: SR 0.36, entry_shift_+1: SR 0.36, entry_shift_+2: SR 0.37

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 80.00%

**Overfitting risk:** deflated Sharpe probability 0.011 (after 196322 trials); PBO 0.65; IS->OOS Sharpe ratio 0.37

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.24183844958719672, "pf": 1.1712130556446072, "t | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 348 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.5541956653560676, "positive_windows": 0.666 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.284 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | FAIL | -0.048 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.359 | SR>0 |
| entry_displacement | reject | PASS | [0.35931556843463447, 0.3650513192226594] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.800 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.966 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.125 | > 0 |
| other_regimes | reject | PASS | 0.452 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.352 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -1.23875341771564, "phase1": -1.1008494105420754} | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.006 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.011 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.655 | <= 0.5 |

**Why it is ranked here:** passed 15 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.9664160218182515 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 196322 trials? -> value 0.01093537310576544 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.6547619047619048 vs <= 0.5

### Strategy #3 - STR-000762 - **REJECTED**

**Rules:** SHORT when zdist_20 in bottom 20% AND sess_pos in top 20% AND streak in top 30%; exit after 15 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 15 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 1.70

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 21.69% | 1.65% | 1.62 | 0.72 | 1.12 | 3.74% | 197 | 10.0 bps | 55.33% |
| VALIDATION | 1.53% | 0.51% | 1.20 | 0.32 | 0.49 | 3.24% | 60 | 2.5 bps | 51.67% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.38, positive windows 66.67%, efficiency 0.64; expanding OOS Sharpe 0.55

**Monte Carlo:** P(loss) under trade bootstrap 0.50%, 95th pct max DD 7.49%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.48, x3: SR 0.31, latency_plus1: SR 0.44, entry_shift_+1: SR 0.44, entry_shift_+2: SR 0.27

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 73.33%

**Overfitting risk:** deflated Sharpe probability 0.019 (after 196322 trials); PBO 0.67; IS->OOS Sharpe ratio 0.45

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.3197294850655584, "pf": 1.2023079283912024, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 257 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.38158276395515583, "positive_windows": 0.66 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.480 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.307 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.444 | SR>0 |
| entry_displacement | reject | PASS | [0.4441431449512596, 0.2690900268388839] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.733 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.785 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.180 | > 0 |
| other_regimes | reject | PASS | 0.601 | <= 85% from one regime |
| schedule_dependence | reject | FAIL | 0.617 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.18354818597267233, "phase1": 0.1693385638564991 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.005 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.019 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.671 | <= 0.5 |

**Why it is ranked here:** passed 16 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.7848203761355027 vs top 5% trades <= 50% of profit; schedule_dependence: Does it depend on one weekday/hour? -> value 0.6167440837393574 vs <= 60%; deflated_sharpe: Is the train Sharpe significant after 196322 trials? -> value 0.018503635251803322 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.6706349206349206 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- deflated_sharpe: 30
- probability_backtest_overfitting: 25
- few_trades_dependence: 24
- out_of_sample_validation: 18
- schedule_dependence: 5
- other_regimes: 2

Final status of all 30 examined strategies: {'REJECTED': 30}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-10-01 00:00:00+00:00, horizon 1 bars. Conditions: hour in quintile 5/5 (current value 20); sess_bar in quintile 1/5 (current value 2); close_loc in quintile 2/5 (current value 0.2358); regime == 0
Sample size 806 (2005-01-20 to 2026-09-24).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.0226% | 34.0% | 30.8%-37.3% | 35.7% |
| B_flat | within +/-0.0226% | 33.9% | 30.7%-37.2% | 28.7% |
| C_down | < -0.0226% | 32.1% | 29.0%-35.4% | 35.6% |

Test vs baseline: p = 0.004 -> conditions are informative.
Invalidated if: hour leaves quintile 5; sess_bar leaves quintile 1; close_loc leaves quintile 2; regime changes

- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- validation/evaluate: 30

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
