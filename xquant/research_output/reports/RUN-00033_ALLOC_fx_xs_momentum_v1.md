# X-QUANT ALLOCATION STUDY (pre-registered)

> **VERDICT: NO EDGE FOUND**

Research/backtest output only. Not investment advice. No live trading.

**fx_xs_momentum_v1** (xs_momentum) - run RUN-00033, spec sha256 `c2f524501c38fe2b56d543578914a89c75fe13baacf6639a95ff0ed1e7902a8f`, multiple-testing N = 6

> Cross-sectional currency momentum (Menkhoff, Sarno, Schmeling & Schrimpf, Journal of Financial Economics 2012): currencies that appreciated most against the USD over the past weeks keep outperforming those that depreciated most.

Rationale: Dollar-neutral (long 2, short 2): no bet on the direction of the dollar. Caveat: only 6 currencies; the published effect is strongest at monthly horizons and in broader universes.

Rules: currency return vs USD = +EURUSD, +GBPUSD, -USDJPY, -USDCAD, -USDCHF, -USDSEK daily session returns; rebalance at the last session of each week; rank by lookback return; +0.5 in each of the top 2, -0.5 in each of the bottom 2; held until the next rebalance

Pass rule: on TRAIN+VALIDATION (no parameter is fitted): Sharpe > 0 with stationary-bootstrap 95% CI lower bound > 0, deflated Sharpe >= 0.95 (N = allocation variants registered), >= 50% profitable years; then TEST once (Sharpe > 0), then FINAL once

Data: ['EUR', 'GBP', 'JPY', 'CAD', 'CHF', 'SEK'] daily sessions (17:00 NY) 2005-01-03 22:00:00+00:00 .. 2026-09-30 21:00:00+00:00; first valid {'EUR': '2005-01-03 22:00:00+00:00', 'GBP': '2005-01-03 22:00:00+00:00', 'JPY': '2005-01-03 22:00:00+00:00', 'CAD': '2005-01-03 22:00:00+00:00', 'CHF': '2005-01-03 22:00:00+00:00', 'SEK': '2005-01-03 22:00:00+00:00'}
Splits: {'train_end': '2016-12-31', 'validation_end': '2019-12-31', 'test_end': '2022-12-31'}

| Variant | Status | Primary Sharpe (net) | gross | CAGR | Vol | Max DD | Profitable years | Bootstrap 95% CI | DSR | Turnover/yr | Cost drag/yr |
|---|---|---|---|---|---|---|---|---|---|---|---|
| {'lookback': 20} | REJECTED | -0.26 | -0.17 | -2.72% | 9.04% | 43.84% | 33.33% | -0.75..0.21 | 0.01 | 67.50 | 0.83% |
| {'lookback': 60} | REJECTED | -0.11 | -0.05 | -1.40% | 9.28% | 32.02% | 33.33% | -0.55..0.34 | 0.04 | 44.81 | 0.54% |

### {'lookback': 20} - REJECTED

- checks: {'sharpe_positive': False, 'deflated_sharpe': False, 'profitable_years': False, 'bootstrap_ci_above_0': False}
- TRAIN Sharpe -0.20, VALIDATION Sharpe -0.69; average gross exposure 2.00; 
- yearly net returns: {2005: -0.0333, 2006: -0.0211, 2007: -0.043, 2008: 0.2537, 2009: -0.2796, 2010: 0.114, 2011: -0.1115, 2012: 0.0478, 2013: -0.0302, 2014: -0.0673, 2015: 0.0097, 2016: -0.0433, 2017: -0.0839, 2018: 0.0266, 2019: -0.0606}

### {'lookback': 60} - REJECTED

- checks: {'sharpe_positive': False, 'deflated_sharpe': False, 'profitable_years': False, 'bootstrap_ci_above_0': False}
- TRAIN Sharpe -0.03, VALIDATION Sharpe -0.61; average gross exposure 2.00; 
- yearly net returns: {2005: 0.0004, 2006: -0.0128, 2007: -0.0889, 2008: 0.2626, 2009: -0.1525, 2010: -0.0429, 2011: -0.0125, 2012: 0.0121, 2013: 0.0537, 2014: -0.0187, 2015: -0.1144, 2016: 0.08, 2017: -0.0542, 2018: -0.0412, 2019: -0.0235}

## Protected split access

- none (no variant passed the primary sample)

## Limitations

- Daily sessions from Dukascopy CFD/FX mid prices; tick volume only; no risk-free rate (excess returns not computed).
- Weights held constant between rebalances; costs = turnover x fixed cost per unit (no market impact model).
