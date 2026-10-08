# X-QUANT RESEARCH REPORT

> **VERDICT: NO EDGE FOUND** - 30 candidate strategies examined; none survived. Outcome: {'REJECTED': 30}.

Research/backtest output only. Not investment advice. No live trading.

| | |
|---|---|
| Run | RUN-00041 |
| Asset | GBPUSD_H1 |
| Timeframe | 1h |
| Historical period | 2005-01-02 23:00:00+00:00 to 2026-10-01 00:00:00+00:00 (135742 bars) |
| Data capabilities | ohlc, volume, intraday |
| Dataset version | 3267a77c257c8f15 |
| Mode / budget used | standard - 12 experiments, 30 strategies examined, 8.81 min |
| Backtests counted as trials (all runs on this dataset) | 5043 |

**Splits** (chronological, embargoed): TRAIN 2005-01-02 to 2016-12-30 (74978 bars); VALIDATION 2017-01-08 to 2019-12-31 (18557 bars); TEST 2020-01-08 to 2022-12-30 (18609 bars); FINAL 2023-01-09 to 2026-10-01 (23238 bars)

## Data

- provenance: {'bid_files': 261, 'bid_missing_periods': [], 'ask_files': 261, 'ask_missing_periods': [], 'bars': 135742, 'flat_zero_volume_dropped': 54890, 'spread_median': 0.00011999999999989797, 'volume': 'Dukascopy tick volume (not exchange volume)', 'seconds': 0.7, 'field_order': 'open,close,low,high (verified by checks)'}
- per-bar spread available (median 0.00012)
- Quality OK: 135742 raw rows -> 135742 bars; 0 missing (holidays/no fix), 0 duplicates, 0 corrupt, 0 bad prints removed, gaps 16
- Exogenous `us_cpi_yoy`: OK - US CPI-U YoY (BLS). Released ~2 weeks after month end; conservative 35-day lag. (lag 35 days)
- Exogenous `us_10y_yield`: OK - US 10Y yield, monthly average (Fed H.15). Known at month end. (lag 1 days)
- Exogenous `vix`: OK - CBOE VIX close (16:15 New York). Usable from the end of its New York day. (lag 0 days)
- Exogenous `brent`: OK - Brent spot (EIA). Publication time uncertain; usable from the next New York day. (lag 1 days)

## Market discoveries

91 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 5.**

- **runs_test_signs** - Wald-Wolfowitz runs of return signs; effect<0 = longer runs than chance: effect 0.05242, p=0.00000, q=0.0000, replication p=0.00000 (n=74633)
- **big_move_clustering** - P(>2.5 sigma bar next) after a >2.5 sigma bar vs otherwise: effect 0.05949, p=0.00000, q=0.0000, replication p=0.00001 (n=2652)
- **arch_lm_5** - Engle ARCH-LM(5): volatility clustering; effect = R^2: effect 0.06677, p=0.00000, q=0.0000, replication p=0.00000 (n=74972)
- **ljung_box_abs_20** - Ljung-Box(20) on |returns|; effect = lag-1 acf of |r|: effect 0.28022, p=0.00000, q=0.0000, replication p=0.00000 (n=74977)
- **high_vol_mean_reversion** - log(next-20-bar vol / vol60) when vol20 is in its top decile (vs rest): effect -0.10208, p=0.00000, q=0.0000, replication p=0.00000 (n=7487)
- Not replicated: ljung_box_returns_10 (train p=0.00000, validation p=0.4687)
- Not replicated: streak3_fwd1 (train p=0.00025, validation p=0.1422)
- Not replicated: month_04 (train p=0.00048, validation p=0.8978)
- Not replicated: hour_02 (train p=0.00126, validation p=0.0091)
- Not replicated: hour_14 (train p=0.00698, validation p=0.4079)
- Not replicated: hour_15 (train p=0.00161, validation p=0.6503)
- Not replicated: hour_16 (train p=0.00175, validation p=0.1103)
- Not replicated: hour_17 (train p=0.00000, validation p=0.5188)
- Not replicated: hour_19 (train p=0.00405, validation p=0.9776)
- Not replicated: hour_21 (train p=0.00001, validation p=0.8118)
- Descriptive - return_distribution_train: Per-bar log return distribution {"mean_bps": -0.05880613643768621, "ann_vol": 0.10222497856023155, "skew": -1.572382768308578, "excess_kurtosis": 73.05336510526028, "jarque_bera_p": 0.0, "n": 74977}
- Descriptive - return_distribution_validation: Per-bar log return distribution {"mean_bps": 0.04112715104737545, "ann_vol": 0.0852039513166407, "skew": 0.5312298747316397, "excess_kurtosis": 22.899755256188193, "jarque_bera_p": 0.0, "n": 18557}
- Descriptive - trend_episode_duration: Directional-change episodes (threshold 0.0065 log) vs 200 shuffled-return paths (TRAIN) {"episodes": 1435, "mean_duration": 52.20975609756098, "median_duration": 32.0, "shuffled_mean_duration": 48.93659223494202, "p_longer_than_shuffled": 0.004975124378109453}
- Descriptive - regime_model: GMM regimes on TRAIN, k=5 chosen by BIC {"labels": {"0": "R0: high-vol trending contracting", "1": "R1: high-vol ranging contracting", "2": "R2: high-vol trending contracting", "3": "R3: low-vol trending", "4": "R4: low-vol ranging"}, "persistence": {"0": 0.7485166348802712, "1": 0.6347811197990982, "2": 0.6087748042963772, "3": 0.6989785831960461, "4": 0.5362618914381645}, "occupancy": {"0": 0.25189495035763854, "1": 0.2338128536351019

## Macro discoveries

32 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- Descriptive - macro_data_limits: Macro series are latest-vintage (revised) values with conservative publication lags; no consensus data => no surprise analysis {}
- INSUFFICIENT DATA for: CPI, PCE, NFP, Unemployment rate, Average hourly earnings, GDP, PMI, Fed rate decision, ECB rate decision, Central bank statements

## News discoveries

0 statistical tests on TRAIN (BH-FDR), significant ones re-tested on VALIDATION. **Replicated discoveries: 0.**

- INSUFFICIENT DATA for: news_predictive_power

## Feature discovery

400 candidate features, 1955 (feature, horizon) IC tests on the discovery part of TRAIN; confirmed on the inner holdout: **36** ['diff(sub(fromhigh_60,on_pos),1)', 'ny_ret', 'close_loc', 'smooth(on_pos,3)', 'ret_1', 'shock_1', 'ret_3', 'sess_pos', 'streak', 'zdist_10']
Status counts: {'REJECTED': 1806, 'TOO_COMPLEX': 72, 'CONFIRMED': 49, 'NOT_CONFIRMED': 28}

## Top hypotheses

4810 hypotheses (4810 new, 0 reused from memory). Status counts: {'REJECTED': 4778, 'OVERFIT': 19, 'VALIDATION': 13}

| ID | Hypothesis | n | effect size | p | q | confirm p | status |
|---|---|---|---|---|---|---|---|
| HYP-055228 | When month == 4, next 12-bar return differs from baseline | 4608 | 0.138 | 0.00039 | 0.0498 | 0.0060 | VALIDATION |
| HYP-058150 | When hour == 17, next 1-bar return differs from baseline | 2187 | -0.120 | 0.00000 | 0.0000 | 0.0299 | VALIDATION |
| HYP-058300 | When sess_bar == 23, next 1-bar return differs from baseline | 2185 | -0.120 | 0.00000 | 0.0000 | 0.0299 | VALIDATION |
| HYP-058122 | When hour == 11, next 6-bar return differs from baseline | 2185 | 0.091 | 0.00000 | 0.0003 | 0.0000 | VALIDATION |
| HYP-058272 | When sess_bar == 17, next 6-bar return differs from baseline | 2187 | 0.090 | 0.00000 | 0.0003 | 0.0000 | VALIDATION |
| HYP-054100 | When close_loc <= 0.09367 (bottom 10%), next 1-bar return differs from baseline | 5249 | 0.088 | 0.00000 | 0.0000 | 0.0001 | VALIDATION |
| HYP-058136 | When hour == 14, next 3-bar return differs from baseline | 2187 | 0.078 | 0.00001 | 0.0020 | 0.0058 | VALIDATION |
| HYP-058286 | When sess_bar == 20, next 3-bar return differs from baseline | 2186 | 0.078 | 0.00001 | 0.0020 | 0.0058 | VALIDATION |
| HYP-054110 | When close_loc <= 0.1947 (bottom 20%), next 1-bar return differs from baseline | 10498 | 0.072 | 0.00000 | 0.0000 | 0.0017 | VALIDATION |
| HYP-054105 | When close_loc >= 0.9046 (top 10%), next 1-bar return differs from baseline | 5249 | -0.069 | 0.00000 | 0.0006 | 0.0019 | VALIDATION |

Strongest hypotheses that failed confirmation (OVERFIT):

- HYP-058151: When hour == 17, next 3-bar return differs from baseline - discovery p=0.00000, confirmation p=0.078, confirmation effect -0.00010 vs -0.00024
- HYP-058301: When sess_bar == 23, next 3-bar return differs from baseline - discovery p=0.00000, confirmation p=0.078, confirmation effect -0.00010 vs -0.00024
- HYP-058171: When hour == 21, next 3-bar return differs from baseline - discovery p=0.00000, confirmation p=0.696, confirmation effect 0.00003 vs 0.00016
- HYP-058201: When sess_bar == 3, next 3-bar return differs from baseline - discovery p=0.00000, confirmation p=0.696, confirmation effect 0.00003 vs 0.00016
- HYP-054225: When streak >= 3 (top 10%), next 1-bar return differs from baseline - discovery p=0.00000, confirmation p=0.431, confirmation effect -0.00002 vs -0.00009

## Research lines

| Line | Status | Runs | Examined | Stop reason |
|---|---|---|---|---|
| hypothesis_seeded | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| open_exploration | STOPPED | 2 | 10 | budget: max_strategies (30) examined |
| regime_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |
| macro_conditioned | STOPPED | 1 | 5 | budget: max_strategies (30) examined |

## Top strategies

### Strategy #1 - STR-000916 - **REJECTED**

**Rules:** SHORT when autocorr_60 in top 15% AND x_vix_chg20 in top 15%; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 2.45

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 17.96% | 1.39% | 1.55 | 0.44 | 0.75 | 7.33% | 163 | 10.1 bps | 53.37% |
| VALIDATION | 2.67% | 0.89% | 1.35 | 0.49 | 0.70 | 3.29% | 47 | 5.6 bps | 55.32% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.52, positive windows 83.33%, efficiency 0.85; expanding OOS Sharpe 0.45

**Monte Carlo:** P(loss) under trade bootstrap 3.10%, 95th pct max DD 9.24%; random-entry test p = 0.004

**Stress tests:** x2: SR 0.32, x3: SR 0.19, latency_plus1: SR 0.42, entry_shift_+1: SR 0.42, entry_shift_+2: SR 0.39

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 73.33%

**Overfitting risk:** deflated Sharpe probability 0.008 (after 5043 trials); PBO 0.46; IS->OOS Sharpe ratio 1.12

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.492163680696015, "pf": 1.3464090756232328, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 210 | >= 60 |
| beats_random_entries | reject | PASS | 0.004 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.5155282321394863, "positive_windows": 0.833 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.316 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.194 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.415 | SR>0 |
| entry_displacement | reject | PASS | [0.4160894310990543, 0.3894166740482012] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.733 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 1.029 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.094 | > 0 |
| other_regimes | reject | PASS | 0.364 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.530 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | FAIL | {"phase0": 0.1386410441422129, "phase1": -0.0226248346324344 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.031 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.008 | >= 0.95 |
| probability_backtest_overfitting | overfit | PASS | 0.464 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 1.028777960726761 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 5043 trials? -> value 0.00799191864368167 vs >= 0.95

### Strategy #2 - STR-000913 - **REJECTED**

**Rules:** SHORT when fromlow_60 in bottom 30% AND dom == 5; exit after 15 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 15 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 2.15

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 6.88% | 0.56% | 1.50 | 0.38 | 0.59 | 2.50% | 105 | 6.3 bps | 58.10% |
| VALIDATION | 1.44% | 0.48% | 1.35 | 0.34 | 0.47 | 1.75% | 26 | 5.5 bps | 50.00% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.52, positive windows 83.33%, efficiency 1.12; expanding OOS Sharpe 0.54

**Monte Carlo:** P(loss) under trade bootstrap 4.00%, 95th pct max DD 5.86%; random-entry test p = 0.038

**Stress tests:** x2: SR 0.22, x3: SR 0.06, latency_plus1: SR 0.46, entry_shift_+1: SR 0.44, entry_shift_+2: SR 0.47

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 66.67%

**Overfitting risk:** deflated Sharpe probability 0.008 (after 5043 trials); PBO 0.87; IS->OOS Sharpe ratio 0.89

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.33654433427629477, "pf": 1.3470214686030462, "t | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 131 | >= 60 |
| beats_random_entries | reject | PASS | 0.038 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.5193698753958628, "positive_windows": 0.833 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.216 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.062 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.460 | SR>0 |
| entry_displacement | reject | PASS | [0.4402021044242978, 0.46703923350928694] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.667 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.958 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.060 | > 0 |
| other_regimes | reject | PASS | 0.467 | <= 85% from one regime |
| schedule_dependence | reject | PASS | 0.406 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.2809725046659366, "phase1": 0.38610718322036475 | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.040 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.008 | >= 0.95 |
| probability_backtest_overfitting | overfit | FAIL | 0.873 | <= 0.5 |

**Why it is ranked here:** passed 17 of 20 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.9577820918522355 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 5043 trials? -> value 0.008065553019737423 vs >= 0.95; probability_backtest_overfitting: Is the search process itself overfitting (CSCV PBO)? -> value 0.873015873015873 vs <= 0.5

### Strategy #3 - STR-000915 - **REJECTED**

**Rules:** SHORT when dom == 4 AND regime == 3; exit after 20 bars

- Entry: all conditions true at the close of bar t (thresholds = quantiles fitted on the fit window); fill at the next available price + costs; direction SHORT
- Exit: after 20 bars
- Risk: one position at a time, 1x notional; costs = half spread + commission + slippage per fill
- Complexity: 2  |  Composite score: 2.08

**Performance**

| Split | Return | CAGR | PF | Sharpe | Sortino | Max DD | Trades | Expectancy | Win rate |
|---|---|---|---|---|---|---|---|---|---|
| TRAIN (in-sample) | 8.22% | 0.66% | 1.62 | 0.47 | 0.68 | 2.60% | 92 | 8.6 bps | 60.87% |
| VALIDATION | 0.90% | 0.30% | 1.26 | 0.28 | 0.41 | 1.43% | 22 | 4.1 bps | 50.00% |
| TEST | not evaluated | | | | | | | | |
| FINAL out-of-sample | not evaluated | | | | | | | | |

**Walk-forward:** rolling OOS Sharpe 0.40, positive windows 66.67%, efficiency 0.40; expanding OOS Sharpe 0.41

**Monte Carlo:** P(loss) under trade bootstrap 3.90%, 95th pct max DD 6.07%; random-entry test p = 0.042

**Stress tests:** x2: SR 0.30, x3: SR 0.16, latency_plus1: SR 0.47, entry_shift_+1: SR 0.47, entry_shift_+2: SR 0.40

**Robustness:** parameter neighbours profitable 100.00%; noise-perturbed runs SR>0 100.00%; profitable years 66.67%

**Overfitting risk:** deflated Sharpe probability 0.020 (after 5043 trials); PBO 0.46; IS->OOS Sharpe ratio 0.59

**Adversarial attacks**

| Attack | Kind | Result | Value | Threshold |
|---|---|---|---|---|
| out_of_sample_validation | reject | PASS | {"sharpe": 0.276305670146182, "pf": 1.2638359921734095, "tra | SR>0, PF>1, >=5 trades |
| enough_trades | reject | PASS | 115 | >= 60 |
| beats_random_entries | reject | PASS | 0.042 | p < 0.05 |
| walk_forward | reject | PASS | {"oos_sharpe": 0.4041791970220698, "positive_windows": 0.666 | OOS SR>0 and >=50% windows positive |
| parameter_perturbation | overfit | PASS | 1.000 | >= 0.6 |
| spread_slippage_x2 | reject | PASS | 0.299 | SR>0 at 2x costs |
| spread_slippage_x3 | warn | PASS | 0.164 | SR>0 at 3x costs |
| latency_plus1 | reject | PASS | 0.470 | SR>0 |
| entry_displacement | reject | PASS | [0.47040257787246964, 0.4038935835268991] | SR>0 for both delays |
| randomized_execution | reject | PASS | 1.000 | >= 0.6 of runs SR>0 |
| other_years | reject | PASS | 0.667 | >= 0.5 |
| few_trades_dependence | reject | FAIL | 0.674 | top 5% trades <= 50% of profit |
| single_event_dependence | reject | PASS | 0.069 | > 0 |
| schedule_dependence | reject | PASS | 0.223 | <= 60% |
| data_perturbation | overfit | PASS | 1.000 | >= 0.6 of runs SR>0 |
| timeframe_perturbation | warn | PASS | {"phase0": 0.3520047706905121, "phase1": 0.1844112599710093} | SR>0 both phases |
| monte_carlo_loss_probability | reject | PASS | 0.039 | <= 0.2 |
| deflated_sharpe | overfit | FAIL | 0.020 | >= 0.95 |
| probability_backtest_overfitting | overfit | PASS | 0.464 | <= 0.5 |

**Why it is ranked here:** passed 17 of 19 decisive/informative attacks.

**Why it might fail:** few_trades_dependence: Does profit depend on a handful of trades? -> value 0.6741719935885582 vs top 5% trades <= 50% of profit; deflated_sharpe: Is the train Sharpe significant after 5043 trials? -> value 0.02043926236859198 vs >= 0.95

## Why the others failed

Attacks that eliminated candidates (count of candidates failing each):

- few_trades_dependence: 30
- deflated_sharpe: 30
- probability_backtest_overfitting: 25
- out_of_sample_validation: 23
- other_years: 5
- spread_slippage_x2: 3
- beats_random_entries: 3
- schedule_dependence: 3
- monte_carlo_loss_probability: 3
- walk_forward: 3
- single_event_dependence: 2

Final status of all 30 examined strategies: {'REJECTED': 30}

## Scenario analysis (historical frequencies, not forecasts)

As of 2026-10-01 00:00:00+00:00, horizon 1 bars. Conditions: month in quintile 4/5 (current value 9); hour in quintile 5/5 (current value 20); sess_bar in quintile 1/5 (current value 2); regime == 0
Sample size 1333 (2005-08-01 to 2026-09-30).

| Scenario | Definition | Probability | 95% CI | Baseline |
|---|---|---|---|---|
| A_up | > +0.0237% | 28.7% | 26.4%-31.2% | 35.9% |
| B_flat | within +/-0.0237% | 38.3% | 35.7%-40.9% | 28.7% |
| C_down | < -0.0237% | 33.0% | 30.5%-35.6% | 35.4% |

Test vs baseline: p = 0.000 -> conditions are informative.
Invalidated if: month leaves quintile 4; hour leaves quintile 5; sess_bar leaves quintile 1; regime changes

- Historical frequencies over overlapping windows; not a forecast and not investment advice.

## Protected split access log

- validation/evaluate: 30

## Limitations

- No economic calendar with consensus: surprise/expectation analysis could not run.
- No news source: news intelligence could not run.
- Macro series are latest-vintage values with conservative publication lags (possible mild revision look-ahead for revised series).

## Confidence

The conclusion 'no robust edge' is conditional on the data available (see limitations), the search space explored and the budget. It is evidence of absence within that scope, not proof that no edge exists.
