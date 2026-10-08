# X-QUANT ALLOCATION STUDY (pre-registered)

> **VERDICT: NO EDGE FOUND**

Research/backtest output only. Not investment advice. No live trading.

**vol_managed_nas100_v1** (vol_managed) - run RUN-00031, spec sha256 `b5a6ada30c871cc2247b88fc232a8946e98604bffe8d95fd397f260357463554`, multiple-testing N = 2

> Volatility-managed exposure (Moreira & Muir, Journal of Finance 2017): scaling a long Nasdaq 100 position by the inverse of its recent realised variance gives a higher Sharpe ratio than buy-and-hold with the same average exposure.

Rationale: Uses the one effect this lab has replicated on every asset: volatility clustering. Variance is predictable while the expected return does not rise one-for-one with it, so exposure should fall when variance is high. Literature caveat: later studies report weaker out-of-sample gains.

Rules: daily sessions closing 17:00 NY; weight decided at the close of day t from data up to t, applied to day t+1; w = min(c / RV, cap); c fitted on TRAIN only so that the average weight on TRAIN is 1; benchmark = 1x buy-and-hold; risk-free rate ignored for both (not available) - this slightly favours the levered strategy

Pass rule: on TRAIN+VALIDATION (nothing but the scale c is fitted): managed Sharpe > 0, managed-minus-benchmark Sharpe > 0 with paired stationary-bootstrap p < 0.05, deflated Sharpe >= 0.95 (N = allocation variants registered), >= 50% profitable years; then TEST once (Sharpe difference > 0), then FINAL once

Data: ['NAS100'] daily sessions (17:00 NY) 2013-05-23 21:00:00+00:00 .. 2026-09-30 21:00:00+00:00; first valid {'NAS100': '2013-05-23 21:00:00+00:00'}
Splits: {'train_end': '2019-12-31', 'validation_end': '2021-12-31', 'test_end': '2023-12-31'}

| Variant | Status | Primary Sharpe (net) | gross | CAGR | Vol | Max DD | Profitable years | Bootstrap 95% CI | DSR | Turnover/yr | Cost drag/yr |
|---|---|---|---|---|---|---|---|---|---|---|---|
| {'rv': 'daily', 'window': 22, 'cap': 2.0} | REJECTED | 0.97 | 0.97 | 13.17% | 13.82% | 19.12% | 77.78% | 0.34..1.62 | 0.99 | 13.16 | 0.06% |
| {'rv': 'hourly', 'window': 5, 'cap': 2.0} | REJECTED | 1.06 | 1.07 | 13.23% | 12.42% | 19.04% | 77.78% | 0.44..1.74 | 0.99 | 30.65 | 0.13% |

### {'rv': 'daily', 'window': 22, 'cap': 2.0} - REJECTED

- checks: {'sharpe_positive': True, 'deflated_sharpe': True, 'profitable_years': True, 'beats_benchmark': False}
- buy-and-hold on the same days: Sharpe 1.15, CAGR 22.53%, vol 19.29%, max DD 28.18%; Sharpe difference bootstrap 95% CI -0.68..0.30, P(diff<=0) 0.79
- TRAIN Sharpe 0.88, VALIDATION Sharpe 1.34; average gross exposure 0.89; {'scale_c': 0.01577027486462617, 'train_mean_weight': 0.9999999999999999}
- yearly net returns: {2013: 0.2548, 2014: 0.0968, 2015: -0.0486, 2016: -0.0507, 2017: 0.5078, 2018: 0.0027, 2019: 0.1423, 2020: 0.1757, 2021: 0.1378}

### {'rv': 'hourly', 'window': 5, 'cap': 2.0} - REJECTED

- checks: {'sharpe_positive': True, 'deflated_sharpe': True, 'profitable_years': True, 'beats_benchmark': False}
- buy-and-hold on the same days: Sharpe 1.12, CAGR 21.75%, vol 19.28%, max DD 28.18%; Sharpe difference bootstrap 95% CI -0.53..0.40, P(diff<=0) 0.63
- TRAIN Sharpe 1.03, VALIDATION Sharpe 1.21; average gross exposure 0.90; {'scale_c': 0.014062625265386042, 'train_mean_weight': 0.9999999999999998}
- yearly net returns: {2013: 0.1873, 2014: 0.1132, 2015: -0.0833, 2016: -0.0118, 2017: 0.4408, 2018: 0.018, 2019: 0.3014, 2020: 0.1296, 2021: 0.1269}

## Protected split access

- none (no variant passed the primary sample)

## Limitations

- Daily sessions from Dukascopy CFD/FX mid prices; tick volume only; no risk-free rate (excess returns not computed).
- Weights held constant between rebalances; costs = turnover x fixed cost per unit (no market impact model).
