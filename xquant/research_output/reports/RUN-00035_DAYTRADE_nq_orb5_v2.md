# X-QUANT DAY-TRADING STRATEGY STUDY (pre-registered, 10-point specification)

> **VERDICT: EDGE FOUND (provisional)**

Research/backtest output only. Not investment advice. No live trading.

**nq_orb5_v2** - run RUN-00035, spec sha256 `5937c5c4e381310c77d07326b8fa752a094ad01ea62b83bfdf1f93357fe2f6c7`, multiple-testing N = 2
Data: {'start': '2017-01-03 07:01:00+00:00', 'end': '2026-10-01 00:00:00+00:00', 'minute_bars': 3166825, 'calendar_days': 2967, 'sessions_with_1600_bar': 2428}

- **1_context**: US cash session days (09:30-16:00 New York). Variant A: every such day. Variant B: only in the direction of the weekly VWAP (tick-volume weighted, anchored Sunday 17:00 NY): longs only if the 09:35 close is above it, shorts only if below.
- **2_setup**: The first 5-minute candle of the cash session (09:30-09:35 NY) has a directional body: |close - open| >= 10% of its high-low range. Bullish body -> long setup; bearish body -> short setup.
- **3_entry**: Market order at the open of the first minute after 09:35 (09:35:00), in the direction of the setup. One trade per day maximum.
- **4_stop_loss**: The opposite extreme of the opening candle: its low for longs, its high for shorts. 1R = |entry - stop|. If a minute bar opens beyond the stop, the fill is that bar's open (gap risk).
- **5_take_profit**: 10R; if neither stop nor target is hit, exit at the 16:00 New York close. If stop and target are touched in the same minute, the stop is assumed first.
- **6_risk_management**: Risk 1% of equity per trade (size = 1% equity / stop distance), notional capped at 4x equity (a capped trade risks less than 1%). Daily loss limit 2% of equity; with one trade per day it binds only through gaps or slippage beyond the stop.
- **7_no_trade**: No trade if: the opening candle is a doji (body < 10% of range); the stop distance is below 0.03% of price (unexecutable) ; the session has no 09:35 or 16:00 bar in the data (holiday / half day / gap in data). Not implemented for lack of a reliable historical calendar (declared, not invented): skipping FOMC/CPI/NFP days.
- **8_edge**: Measured in R per trade net of costs (NQ-futures-like: ~0.435 bps per fill = half spread 0.125 + commission 0.06 + slippage 0.25), and as daily returns at 1% risk.
- **9_backtest**: {"data": "Dukascopy 1-minute BID candles (no ASK: costs are fixed, the spread is not used), 2017-01 to 2026-09", "splits": {"train_end": "2020-12-31", "validation_end": "2022-12-31", "test_end": "2024-06-30"}, "pass_rule": "On TRAIN+VALIDATION (nothing is fitted): mean net R > 0 with stationary-bootstrap 95% CI lower bound > 0; deflated Sharpe of daily returns >= 0.95 with N = variants registered for this market; >= 50% profitable years; beats random direction on the same days with the same stops (p < 0.05); still positive at 2x costs and with entry delayed one minute. Then TEST once (mean R > 0), then FINAL once for the best variant."}
- **10_execution**: Fully mechanical: the checklist is the rules above (time, candle body, side, stop price, size formula, target, 16:00 exit). No discretionary step exists to skip.
- **inspiration**: 5-minute opening-range breakout studied on the Nasdaq-100 ETF in recent SSRN work (Zarattini, Barbon & Aziz, 2023). The rules below are this lab's own fixed specification, not a reproduction of that paper; its sample (to 2023) overlaps 2017-2023 here, so only data after mid-2024 (FINAL split) is post-publication.

| Variant | Status | Trades | Trades/yr | Win rate | Mean R net (95% CI) | gross R | PF | Daily Sharpe | CAGR @1% risk | Max DD | Profitable yrs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| {'id': 'A', 'context': 'none'} | ROBUST | 1357 | 228.433 | 24.76% | 0.145 (0.032..0.261) | 0.194 | 1.185 | 0.970 | 27.17% | 22.77% | 100.00% |
| {'id': 'B', 'context': 'weekly_vwap_side'} | REJECTED | 783 | 131.808 | 27.33% | 0.167 (0.014..0.314) | 0.213 | 1.220 | 0.838 | 16.26% | 23.67% | 83.33% |

### Variant {'id': 'A', 'context': 'none'} - ROBUST

- checks: {'mean_r_ci_above_0': True, 'deflated_sharpe': True, 'profitable_years': True, 'beats_random_direction': True, 'cost_x2_positive': True, 'delay_1m_positive': True}
- TRAIN mean R 0.130 (902 trades); VALIDATION mean R 0.176 (455 trades)
- random direction: p = 0.010, null mean R 0.024
- costs x2 / x3 mean R: 0.096 / 0.047; entry +1 / +2 min: 0.059 / 0.049
- parameter neighbours (mean R): {min_body_frac=0.05: 0.142, min_body_frac=0.2: 0.203, target_r=5: 0.096, target_r=20: 0.134, range_minutes=4: 0.125, range_minutes=6: 0.090}
- deflated Sharpe 0.977; top 5% trades share of profit 2.844
- exits {'stop': 1003, 'eod': 323, 'target': 31}; median stop 0.229% of price; average risk actually taken 0.78%
- yearly returns at 1% risk: {2017: 0.0178, 2018: 0.6356, 2019: 0.1779, 2020: 0.2003, 2021: 0.4472, 2022: 0.2241}
- TEST: mean R 0.025, 340 trades, CAGR @1% 2.25%
- FINAL: mean R 0.113, 514 trades, CAGR @1% 11.98%

### Variant {'id': 'B', 'context': 'weekly_vwap_side'} - REJECTED

- checks: {'mean_r_ci_above_0': True, 'deflated_sharpe': False, 'profitable_years': True, 'beats_random_direction': False, 'cost_x2_positive': True, 'delay_1m_positive': True}
- TRAIN mean R 0.165 (512 trades); VALIDATION mean R 0.169 (271 trades)
- random direction: p = 0.418, null mean R 0.154
- costs x2 / x3 mean R: 0.120 / 0.073; entry +1 / +2 min: 0.081 / 0.091
- parameter neighbours (mean R): {min_body_frac=0.05: 0.166, min_body_frac=0.2: 0.218, target_r=5: 0.163, target_r=20: 0.174, range_minutes=4: 0.133, range_minutes=6: 0.129}
- deflated Sharpe 0.949; top 5% trades share of profit 2.219
- exits {'stop': 562, 'eod': 213, 'target': 8}; median stop 0.225% of price; average risk actually taken 0.79%
- yearly returns at 1% risk: {2017: 0.0257, 2018: 0.1601, 2019: 0.2788, 2020: 0.2476, 2021: 0.4597, 2022: -0.1168}

## Protected split access

- test/evaluate: daytrade:nq_orb5_v2:{'id': 'A', 'context': 'none'}
- final/evaluate: daytrade:nq_orb5_v2:{'id': 'A', 'context': 'none'}

## Limitations

- Dukascopy CFD minute mid prices as a proxy for NQ futures; tick volume (weekly VWAP context) is not CME volume.
- No news calendar filter (not available reliably); costs are fixed per fill (no market-impact model).
