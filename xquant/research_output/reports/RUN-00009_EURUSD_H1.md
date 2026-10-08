# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 80 candidate strategies examined; none survived. Outcome: {'REJECTED': 69, 'OVERFIT': 11}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00009 |
| Asset | EURUSD_H1 |
| Timeframe | 1h |
| Historical period | 2005-01-02 23:00:00+00:00 to 2026-10-01 00:00:00+00:00 (135749 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | ae17a1577bcfcc70 |
| Mode / budget used | deep - 22 experiments, 80 strategies examined, 78.8 min |
| Backtests counted as trials (all runs on this dataset) | 178137 |

**Splits** (chronological, embargoed): TRAIN 2005-01-02 to 2016-12-30 (74982 bars); VALIDATION 2017-01-08 to 2019-12-31 (18558 bars); TEST 2020-01-09 to 2022-12-30 (18609 bars); FINAL 2023-01-08 to 2026-10-01 (23240 bars)

## Data

- provenance: {'bid_files': 261, 'bid_missing_periods': [], 'ask_files': 261, 'ask_missing_periods': [], 'bars': 135749, 'flat_zero_volume_dropped': 54883, 'spread_median': 4.999999999988347e-05, 'volume': 'Dukascopy tick volume (not exchange volume)', 'seconds': 0.8, 'field_order': 'open,close,low,high (verified by checks)'}
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

1500 candidate features, 7435 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **50** ['close_loc', 'ret_3', 'streak', 'zdist_10', 'fromlow_20', 'ret_2', 'zdist_20', 'shock_1', 'diff(sub(fromlow_60,x_brent),1)', 'diff(sub(fromlow_60,vol_120),1)']
Status counts: {'REJECTED': 6974, 'TOO_COMPLEX': 341, 'CONFIRMED': 83, 'NOT_CONFIRMED': 37}

## Top hypotheses

5185 hypotheses (700 new, 4485 reused from memory). Status counts: {'REJECTED': 5165, 'OVERFIT': 11, 'VALIDATION': 9}

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

Strongest hypotheses that failed confirmation (OVERFIT):

- HYP-007918: When zscore(fromlow_250,60) >= 1.354 (top 20%), next 6-bar return differs from baseline - discovery p=0.00006, confirmation p=0.324, confirmation effect -0.00009 vs -0.00027
- HYP-008127: When rank(smooth(fromlow_250,5),60) >= 1 (top 10%), next 3-bar return differs from baseline - discovery p=0.00008, confirmation p=0.413, confirmation effect 0.00006 vs -0.00019
- HYP-007917: When zscore(fromlow_250,60) >= 1.354 (top 20%), next 3-bar return differs from baseline - discovery p=0.00015, confirmation p=0.256, confirmation effect -0.00006 vs -0.00014
- HYP-007907: When zscore(fromlow_250,60) >= 1.93 (top 10%), next 3-bar return differs from baseline - discovery p=0.00040, confirmation p=0.314, confirmation effect -0.00007 vs -0.00017
- HYP-008117: When zscore(diff(fromlow_250,20),60) >= 1.052 (top 20%), next 3-bar return differs from baseline - discovery p=0.00044, confirmation p=0.274, confirmation effect -0.00005 vs -0.00012

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 4 | 20 | budget: max_strategies (80) examined |
| open_exploration | STOPPED | 4 | 20 | budget: max_strategies (80) examined |
| regime_conditioned | STOPPED | 4 | 20 | budget: max_strategies (80) examined |
| macro_conditioned | STOPPED | 4 | 20 | budget: max_strategies (80) examined |

## Top strategies

### Strategy #1 - STR-000348 - **REJECTED**

**Rules:** SHORT when close_loc in top 15% AND rank(smooth(fromlow_250,5),60) in bottom 10% AND regime == 2; exit after 15 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 15 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 3.59

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 31.64% | 2.32% | 1.83 | 0.96 | 1.53 | 5.09% | 291 | 9.4 bps | 53.61% |
| VALIDATION | 6.60% | 2.18% | 1.96 | 1.24 | 2.01 | 1.20% | 80 | 8.0 bps | 57.50% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 1.09, positive windows 100.00%, efficiency 1.13; expanding OOS Sharpe 1.20

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 5.04%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.75, x3: SR 0.51, latency_plus1: SR 0.80, entry_shift_+1: SR 0.83, entry_shift_+2: SR 0.74

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 80.00%

**Overfitting risk:** deflated Sharpe probability 0.113 (after 178137 trials); PBO 0.96; IS->OOS Sharpe ratio 1.29

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 1.2440432180300505, "pf": 1.9615402341588413, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 372 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 1.0943688479105855, "positive_windows": 1.0} | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.748 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.506 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.797 | SR>0 |
| entry_displacement | reject | PASS | [0.8337675632471682, 0.7385385030153355] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.800 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.712 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.301 | > 0 |
| schedule_dependence | reject | PASS | 0.322 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.034894944211181736, "phase1": 0.178467586980733 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.113 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.956 | <= 0.5 |

**Why it is ranked here:** passed 16 of 19 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.7117579995303183 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 178137 trials? -> value 0.11301389967977282 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.9563492063492064 vs <= 0.5

### Strategy #2 - STR-000327 - **REJECTED**

**Rules:** SHORT when rank(smooth(fromlow_250,5),60) in bottom 10% AND skew_20 in bottom 20% AND diff(zdist_250,20) in bottom 10% AND regime == 2; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 4  |  Composite score: 2.50

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 41.79% | 2.95% | 1.88 | 1.08 | 1.68 | 4.16% | 294 | 11.9 bps | 54.76% |
| VALIDATION | 3.12% | 1.04% | 1.59 | 0.67 | 1.03 | 2.39% | 59 | 5.2 bps | 54.24% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.71, positive windows 83.33%, efficiency 0.62; expanding OOS Sharpe 0.90

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 6.25%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.79, x3: SR 0.58, latency_plus1: SR 0.99, entry_shift_+1: SR 0.99, entry_shift_+2: SR 0.95

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 93.33%

**Overfitting risk:** deflated Sharpe probability 0.217 (after 178137 trials); PBO 0.99; IS->OOS Sharpe ratio 0.62

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.6716542220493266, "pf": 1.5931899612935023, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 354 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.7066665309317864, "positive_windows": 0.833 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.790 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.581 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.986 | SR>0 |
| entry_displacement | reject | PASS | [0.9924253441457059, 0.9517016199396019] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.933 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.595 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.352 | > 0 |
| schedule_dependence | reject | PASS | 0.491 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.22309527659151931, "phase1": 0.2941087576007081 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.217 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.992 | <= 0.5 |

**Why it is ranked here:** passed 16 of 19 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.5947320742953629 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 178137 trials? -> value 0.21650717284835297 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.9920634920634921 vs <= 0.5

### Strategy #3 - STR-000276 - **OVERFIT**

**Rules:** SHORT when efficiency_10 in bottom 10% AND dom == 4 AND x_brent_chg5 in bottom 20%; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 2.42

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 32.75% | 2.39% | 3.29 | 1.27 | 2.25 | 3.23% | 99 | 28.6 bps | 65.66% |
| VALIDATION | 1.00% | 0.34% | 1.53 | 0.34 | 0.50 | 1.38% | 23 | 4.3 bps | 60.87% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 1.14, positive windows 83.33%, efficiency 0.81; expanding OOS Sharpe 1.19

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 3.95%; random-entry test p = 0.002

**Stress tests:** x2: SR 1.04, x3: SR 0.93, latency_plus1: SR 1.03, entry_shift_+1: SR 1.08, entry_shift_+2: SR 1.04

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 93.33%

**Overfitting risk:** deflated Sharpe probability 0.457 (after 178137 trials); PBO 0.52; IS->OOS Sharpe ratio 0.27

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.33802705680246214, "pf": 1.534168492267788, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 122 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 1.1446887531726273, "positive_windows": 0.833 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 1.036 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.931 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 1.031 | SR>0 |
| entry_displacement | reject | PASS | [1.0768159497578726, 1.0420556556241063] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.933 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.428 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.269 | > 0 |
| other_regimes | reject | PASS | 0.410 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.312 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.401633996625298, "phase1": 0.45328276448552446} | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.457 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.516 | <= 0.5 |

**Why it is ranked here:** passed 18 of 20 decisive/informative attacks.

**Why it might fail:** deflated_sharpe: Is the train Sharpe significant after 178137 trials? -> value 0.4574851743714905 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.5158730158730159 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- deflated_sharpe: 80
- probability_backtest_overfitting: 80
- out_of_sample_validation: 56
- few_trades_dependence: 40
- schedule_dependence: 2
- other_regimes: 1
- beats_random_entries: 1
- other_years: 1

Final status of all 80 examined strategies: {'REJECTED': 69, 'OVERFIT': 11}

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

- validation/evaluate: 80

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
