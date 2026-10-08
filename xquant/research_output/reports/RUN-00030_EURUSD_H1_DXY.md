# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 30 candidate strategies examined; none survived. Outcome: {'REJECTED': 30}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00030 |
| Asset | EURUSD_H1_DXY |
| Timeframe | 1h |
| Historical period | 2005-01-02 23:00:00+00:00 to 2026-10-01 00:00:00+00:00 (135749 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | 97dbd4f218623237 |
| Mode / budget used | standard - 12 experiments, 30 strategies examined, 11.39 min |
| Backtests counted as trials (all runs on this dataset) | 6903 |

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
- Exogenous `px_dxy`: OK - Synthetic ICE US Dollar Index (DXY) from the 6 Dukascopy hourly mid closes (EUR, JPY, GBP, CAD, SEK, CHF; official exponents and constant), known at the same bar close (lag 0 days)
- Exogenous `px_usd_xeur`: OK - Dollar index EX-EUR: the DXY basket without EURUSD, exponents renormalised to sum 1 (JPY, GBP, CAD, SEK, CHF). Divergence vs EURUSD = euro-specific move (lag 0 days)

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

48 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- Descriptive - macro_data_limits: Macro series are latest-vintage (revised) values with conservative publication lags; no consensus data => no surprise analysis {}
- INSUFFICIENT DATA for: CPI, PCE, NFP, Unemployment rate, Average hourly earnings, GDP, PMI, Fed rate decision, ECB rate decision, Central bank statements

## News discoveries

0 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- INSUFFICIENT DATA for: news_predictive_power

## Feature discovery

400 candidate features, 1945 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **50** ['close_loc', 'ret_3', 'streak', 'zdist_10', 'fromlow_20', 'ret_2', 'sess_pos', 'zdist_20', 'shock_1', 'x_px_usd_xeur_div1']
Status counts: {'REJECTED': 1799, 'TOO_COMPLEX': 75, 'CONFIRMED': 60, 'NOT_CONFIRMED': 11}

## Top hypotheses

5285 hypotheses (5285 new, 0 reused from memory). Status counts: {'REJECTED': 5253, 'VALIDATION': 21, 'OVERFIT': 11}

| ID | Hypothesis | n | effect size | p | q | confirm p | status |
|---|---|---|---|---|---|---|---|
| HYP-051377 | When x_us_cpi_yoy_chg5 <= 0 (bottom 10%), next 6-bar return differs from baseline | 52257 | 0.318 | 0.00029 | 0.0461 | 0.0292 | VALIDATION |
| HYP-051387 | When x_us_cpi_yoy_chg5 <= 0 (bottom 20%), next 6-bar return differs from baseline | 52257 | 0.318 | 0.00029 | 0.0461 | 0.0292 | VALIDATION |
| HYP-051045 | When hour == 6, next 1-bar return differs from baseline | 2187 | -0.110 | 0.00000 | 0.0002 | 0.0070 | VALIDATION |
| HYP-051195 | When sess_bar == 12, next 1-bar return differs from baseline | 2187 | -0.109 | 0.00000 | 0.0002 | 0.0070 | VALIDATION |
| HYP-051041 | When hour == 5, next 3-bar return differs from baseline | 2187 | -0.101 | 0.00000 | 0.0017 | 0.0001 | VALIDATION |
| HYP-051191 | When sess_bar == 11, next 3-bar return differs from baseline | 2187 | -0.100 | 0.00000 | 0.0020 | 0.0001 | VALIDATION |
| HYP-051042 | When hour == 5, next 6-bar return differs from baseline | 2187 | -0.095 | 0.00021 | 0.0370 | 0.0208 | VALIDATION |
| HYP-051192 | When sess_bar == 11, next 6-bar return differs from baseline | 2187 | -0.095 | 0.00021 | 0.0370 | 0.0208 | VALIDATION |
| HYP-051121 | When hour == 21, next 3-bar return differs from baseline | 2186 | 0.085 | 0.00000 | 0.0000 | 0.0198 | VALIDATION |
| HYP-051151 | When sess_bar == 3, next 3-bar return differs from baseline | 2187 | 0.084 | 0.00000 | 0.0000 | 0.0198 | VALIDATION |

Strongest hypotheses that failed confirmation (OVERFIT):

- HYP-047102: When x_px_usd_xeur_div20 <= -1.367 (bottom 10%), next 6-bar return differs from baseline - discovery p=0.00000, confirmation p=0.152, confirmation effect 0.00015 vs -0.00043
- HYP-047101: When x_px_usd_xeur_div20 <= -1.367 (bottom 10%), next 3-bar return differs from baseline - discovery p=0.00000, confirmation p=0.083, confirmation effect 0.00010 vs -0.00022
- HYP-047506: When zscore(fromlow_250,20) >= 1.418 (top 20%), next 3-bar return differs from baseline - discovery p=0.00000, confirmation p=0.274, confirmation effect -0.00005 vs -0.00017
- HYP-047103: When x_px_usd_xeur_div20 <= -1.367 (bottom 10%), next 12-bar return differs from baseline - discovery p=0.00000, confirmation p=0.421, confirmation effect 0.00016 vs -0.00070
- HYP-051126: When hour == 22, next 3-bar return differs from baseline - discovery p=0.00006, confirmation p=0.058, confirmation effect 0.00009 vs 0.00012

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| open_exploration | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| regime_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |
| macro_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |

## Top strategies

### Strategy #1 - STR-000843 - **REJECTED**

**Rules:** SHORT when ret_3 in bottom 10% AND volratio_20_120 in top 10% AND dow == 0; exit after 15 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 15 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 2.10

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 16.26% | 1.26% | 2.52 | 0.78 | 1.27 | 2.90% | 78 | 19.3 bps | 58.97% |
| VALIDATION | 0.18% | 0.06% | 1.74 | 0.27 | 0.43 | 0.32% | 4 | 4.5 bps | 75.00% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.80, positive windows 83.33%, efficiency 0.69; expanding OOS Sharpe 0.77

**Monte Carlo:** P(loss) under trade bootstrap 0.00%, 95th pct max DD 3.87%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.62, x3: SR 0.53, latency_plus1: SR 0.63, entry_shift_+1: SR 0.61, entry_shift_+2: SR 0.57

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 66.67%

**Overfitting risk:** deflated Sharpe probability 0.143 (after 6903 trials); PBO 0.80; IS->OOS Sharpe ratio 0.34

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | FAIL | {"sharpe": 0.2679843284682761, "pf": 1.7394289239223677, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 82 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.8023612991938976, "positive_windows": 0.833 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.622 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.534 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.630 | SR>0 |
| entry_displacement | reject | PASS | [0.6111573383392033, 0.5687524508793745] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.667 | >= 0.5 |
| few_trades_dependence | reject | PASS | 0.484 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.127 | > 0 |
| other_regimes | reject | PASS | 0.412 | <= 85% from one regime |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.00520424037267983, "phase1": 0.270110639138964 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.000 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.143 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.802 | <= 0.5 |

**Why it is ranked here:** passed 15 of 19 decisive/informative attacks.

**Why it might fail:** out_of_sample_validation: Does it work out of sample (VALIDATION, thresholds from TRAIN)? -> value {'sharpe': 0.2679843284682761, 'pf': 1.7394289239223677, 'trades': 4} vs SR>0, PF>1, >=5 trades; deflated_sharpe: Is the train Sharpe significant after 6903 trials? -> value 0.14256061235764195 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.8015873015873016 vs <= 0.5

### Strategy #2 - STR-000850 - **REJECTED**

**Rules:** SHORT when volume_z in top 20% AND x_px_usd_xeur_relz60 in bottom 10% AND volratio_20_120 in top 10%; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 3  |  Composite score: 1.34

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 18.98% | 1.46% | 1.89 | 0.71 | 1.12 | 3.83% | 137 | 12.7 bps | 58.39% |
| VALIDATION | 0.11% | 0.04% | 1.03 | 0.03 | 0.04 | 1.80% | 26 | 0.4 bps | 50.00% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.43, positive windows 83.33%, efficiency 0.64; expanding OOS Sharpe 0.48

**Monte Carlo:** P(loss) under trade bootstrap 1.00%, 95th pct max DD 6.93%; random-entry test p = 0.004

**Stress tests:** x2: SR 0.49, x3: SR 0.37, latency_plus1: SR 0.57, entry_shift_+1: SR 0.56, entry_shift_+2: SR 0.41

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 86.67%

**Overfitting risk:** deflated Sharpe probability 0.092 (after 6903 trials); PBO 0.92; IS->OOS Sharpe ratio 0.05

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.03215635501944135, "pf": 1.027806830695243, "tr | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 163 | >= 60 |
| beats_random_entries | reject | PASS | 0.004 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.4278494537971804, "positive_windows": 0.833 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.493 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.367 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.573 | SR>0 |
| entry_displacement | reject | PASS | [0.5577207845723658, 0.4127258741712415] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.867 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.738 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.149 | > 0 |
| other_regimes | reject | PASS | 0.463 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.358 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.25978356688568194, "phase1": 0.1103047336846448 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.010 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.092 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.925 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.7381985476939874 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 6903 trials? -> value 0.09237350185629772 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.9246031746031746 vs <= 0.5

### Strategy #3 - STR-000845 - **REJECTED**

**Rules:** SHORT when ret_60 in top 5% AND hour == 18; exit after 15 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 15 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 1.10

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 23.76% | 1.79% | 1.72 | 0.68 | 0.98 | 6.33% | 175 | 12.2 bps | 62.86% |
| VALIDATION | -0.00% | -0.00% | 1.00 | -0.00 | -0.00 | 1.33% | 16 | -0.0 bps | 50.00% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.47, positive windows 66.67%, efficiency 1.02; expanding OOS Sharpe 0.47

**Monte Carlo:** P(loss) under trade bootstrap 0.50%, 95th pct max DD 8.11%; random-entry test p = 0.002

**Stress tests:** x2: SR 0.49, x3: SR 0.36, latency_plus1: SR 0.50, entry_shift_+1: SR 0.50, entry_shift_+2: SR 0.45

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 93.33%

**Overfitting risk:** deflated Sharpe probability 0.079 (after 6903 trials); PBO 0.80; IS->OOS Sharpe ratio -0.00

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | FAIL | {"sharpe": -0.0011193425659394576, "pf": 0.9988618196948933, | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 192 | >= 60 |
| beats_random_entries | reject | PASS | 0.002 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.4705666661225613, "positive_windows": 0.666 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.485 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.360 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.504 | SR>0 |
| entry_displacement | reject | PASS | [0.5042762146894394, 0.4497602721154565] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.933 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.643 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.196 | > 0 |
| other_regimes | reject | PASS | 0.582 | <= 85% from one regime |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": -0.013863940186417928, "phase1": 0.31629059347562 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.005 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.079 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.802 | <= 0.5 |

**Why it is ranked here:** passed 14 of 19 decisive/informative attacks.

**Why it might fail:** out_of_sample_validation: Does it work out of sample (VALIDATION, thresholds from TRAIN)? -> value {'sharpe': -0.0011193425659394576, 'pf': 0.9988618196948933, 'trades': 16} vs SR>0, PF>1, >=5 trades; few_trades_dependence: Does profit depend on a handful of trades? -> value 0.642977877716298 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 6903 trials? -> value 0.07926133002197899 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.8015873015873016 vs <= 0.5

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- deflated_sharpe: 30
- probability_backtest_overfitting: 30
- out_of_sample_validation: 28
- few_trades_dependence: 28
- entry_displacement: 9
- walk_forward: 7
- other_years: 6
- spread_slippage_x2: 3
- schedule_dependence: 3
- monte_carlo_loss_probability: 3
- latency_plus1: 2
- randomized_execution: 2
- other_regimes: 1
- single_event_dependence: 1
- parameter_perturbation: 1

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
