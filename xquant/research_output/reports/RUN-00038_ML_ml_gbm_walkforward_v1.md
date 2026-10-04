# X-QUANT ML WALK-FORWARD STUDY (pre-registered)

> **VERDICT: NO EDGE FOUND**

Research/backtest output only. Not investment advice. No live trading.

**ml_gbm_walkforward_v1** - run RUN-00038, spec sha256 `142415d8203af5008b79e3454ad351af1126686d065ac56fd2f3baac217949b0`, multiple-testing N = 3

> A gradient-boosting classifier trained only on past data, using the lab's generic causal feature set, predicts the sign of the next 6-bar (6 h) return well enough that trading its most confident predictions is profitable after costs.

Model: {'class': 'sklearn HistGradientBoostingClassifier', 'max_depth': 3, 'learning_rate': 0.05, 'max_iter': 200, 'l2_regularization': 1.0, 'early_stopping': False, 'random_state': 0}
Walk-forward: expanding window; retrain on 1 January of each year using bars up to 6 bars before the year start (purge); first prediction year = 3 full years after the data start; predictions for each year come only from the model trained before it
Trading rule: long when p >= 90th percentile of the model's in-sample predicted probabilities, short when p <= 10th percentile (thresholds from the training data of that model); entry at the next bar open, exit after hold=6 bars (lab convention: close of bar f+6); one position per side at a time; the asset config's costs
Pass rule: per asset, on the walk-forward predictions inside TRAIN+VALIDATION: combined long+short per-bar returns with Sharpe > 0 and stationary-bootstrap 95% CI lower bound > 0, deflated Sharpe >= 0.95 with N = 3 (one per asset), >= 50% profitable years, still positive at 2x costs; then TEST once (Sharpe > 0), then FINAL once for the best asset

| Asset | Status | First prediction | Trades | Sharpe (95% CI) | Ann. return | Profitable years | Sharpe at 2x costs | DSR |
|---|---|---|---|---|---|---|---|---|
| EURUSD_H1 | REJECTED | 2008-01-01 | 5292 | -0.51 (-1.07..0.03) | -3.46% | 33.33% | -1.84 | 0.00 |
| XAUUSD_H1 | REJECTED | 2011-01-02 | 3543 | -1.11 (-1.81..-0.45) | -10.91% | 20.00% | -2.70 | 0.00 |
| NAS100_H1_NQ | REJECTED | 2016-01-04 | 1699 | 0.15 (-0.48..0.86) | 2.45% | 66.67% | -0.01 | 0.31 |

### EURUSD_H1 - REJECTED
- checks: {'sharpe_ci_above_0': False, 'deflated_sharpe': False, 'profitable_years': False, 'cost_x2_positive': False}
- yearly: {2008: -0.0368, 2009: 0.0073, 2010: 0.0017, 2011: 0.0562, 2012: -0.1284, 2013: -0.0157, 2014: -0.0875, 2015: -0.0596, 2016: 0.0489, 2017: -0.0936, 2018: -0.0425, 2019: -0.0651}

### XAUUSD_H1 - REJECTED
- checks: {'sharpe_ci_above_0': False, 'deflated_sharpe': False, 'profitable_years': False, 'cost_x2_positive': False}
- yearly: {2011: -0.0221, 2012: 0.051, 2013: -0.0701, 2014: -0.1905, 2015: 0.0293, 2016: -0.2, 2017: -0.2215, 2018: -0.0653, 2019: -0.3015, 2020: -0.0985}

### NAS100_H1_NQ - REJECTED
- checks: {'sharpe_ci_above_0': False, 'deflated_sharpe': False, 'profitable_years': True, 'cost_x2_positive': False}
- yearly: {2016: 0.061, 2017: 0.0517, 2018: -0.0234, 2019: 0.056, 2020: 0.097, 2021: -0.1001}

## Protected split access

- none (no asset passed the primary sample)