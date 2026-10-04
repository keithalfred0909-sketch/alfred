# X-QUANT ALLOCATION STUDY (pre-registered)

> **VERDICT: NO EDGE FOUND**

Research/backtest output only. Not investment advice. No live trading.

**tsmom_diversified_v1** (tsmom) - run RUN-00032, spec sha256 `e49edc3122ff47c55ddfabd7a5cf9403a0764b1288dc316555bb4c876ee3f2a6`, multiple-testing N = 4

> Time-series momentum (Moskowitz, Ooi & Pedersen, Journal of Financial Economics 2012): the sign of an asset's own past return predicts its next-month return; a volatility-scaled, equally weighted portfolio of such positions across FX, metals and an equity index earns a positive Sharpe ratio net of costs.

Rationale: Most-documented systematic premium across asset classes. Caveat: weaker since ~2010; the universe here is small (9 instruments).

Rules: daily sessions closing 17:00 NY; rebalance at the last session of each month using data up to that close; position_i = sign(lookback log return) * 0.10 / (60-session daily vol * sqrt(252)), capped at 3; portfolio = average over instruments with data; held until the next rebalance

Pass rule: on TRAIN+VALIDATION (no parameter is fitted): Sharpe > 0 with stationary-bootstrap 95% CI lower bound > 0, deflated Sharpe >= 0.95 (N = allocation variants registered), >= 50% profitable years; then TEST once (Sharpe > 0), then FINAL once

Data: ['EURUSD', 'GBPUSD', 'USDJPY', 'USDCAD', 'USDCHF', 'USDSEK', 'XAUUSD', 'XAGUSD', 'NAS100'] daily sessions (17:00 NY) 2005-01-03 22:00:00+00:00 .. 2026-09-30 21:00:00+00:00; first valid {'EURUSD': '2005-01-03 22:00:00+00:00', 'GBPUSD': '2005-01-03 22:00:00+00:00', 'USDJPY': '2005-01-03 22:00:00+00:00', 'USDCAD': '2005-01-03 22:00:00+00:00', 'USDCHF': '2005-01-03 22:00:00+00:00', 'USDSEK': '2005-01-03 22:00:00+00:00', 'XAUUSD': '2008-01-01 22:00:00+00:00', 'XAGUSD': '2008-01-01 22:00:00+00:00', 'NAS100': '2013-05-23 21:00:00+00:00'}
Splits: {'train_end': '2016-12-31', 'validation_end': '2019-12-31', 'test_end': '2022-12-31'}

| Variant | Status | Primary Sharpe (net) | gross | CAGR | Vol | Max DD | Profitable years | Bootstrap 95% CI | DSR | Turnover/yr | Cost drag/yr |
|---|---|---|---|---|---|---|---|---|---|---|---|
| {'lookback': 252} | REJECTED | 0.07 | 0.08 | 0.26% | 6.11% | 14.93% | 50.00% | -0.45..0.58 | 0.22 | 4.93 | 0.07% |
| {'lookback': 63} | REJECTED | 0.17 | 0.19 | 0.90% | 6.26% | 14.57% | 60.00% | -0.30..0.63 | 0.36 | 8.20 | 0.11% |

### {'lookback': 252} - REJECTED

- checks: {'sharpe_positive': True, 'deflated_sharpe': False, 'profitable_years': True, 'bootstrap_ci_above_0': False}
- TRAIN Sharpe 0.20, VALIDATION Sharpe -0.47; average gross exposure 1.11; 
- yearly net returns: {2006: -0.0405, 2007: 0.0416, 2008: 0.075, 2009: -0.0364, 2010: 0.0132, 2011: -0.0055, 2012: -0.0262, 2013: 0.0251, 2014: 0.0559, 2015: 0.0744, 2016: -0.0473, 2017: -0.0565, 2018: -0.0283, 2019: 0.0056}

### {'lookback': 63} - REJECTED

- checks: {'sharpe_positive': True, 'deflated_sharpe': False, 'profitable_years': True, 'bootstrap_ci_above_0': False}
- TRAIN Sharpe 0.30, VALIDATION Sharpe -0.41; average gross exposure 1.11; 
- yearly net returns: {2005: 0.0687, 2006: -0.1066, 2007: 0.0447, 2008: 0.0965, 2009: -0.0079, 2010: 0.0894, 2011: 0.035, 2012: -0.0883, 2013: 0.0448, 2014: 0.0987, 2015: -0.0501, 2016: 0.0146, 2017: -0.0543, 2018: 0.0243, 2019: -0.0415}

## Protected split access

- none (no variant passed the primary sample)

## Limitations

- Daily sessions from Dukascopy CFD/FX mid prices; tick volume only; no risk-free rate (excess returns not computed).
- Weights held constant between rebalances; costs = turnover x fixed cost per unit (no market impact model).
