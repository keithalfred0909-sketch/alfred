# Synthetic DXY vs Dukascopy DOLLARIDXUSD (hourly mid closes)

Generated 2026-10-04T15:10Z by `scripts/validate_dxy.py`. Synthetic = ICE formula on the 6 Dukascopy hourly pairs (2005-); reference = Dukascopy's own index series (available from 2017-12).

```
{
 "synthetic_bars": 135674,
 "synthetic_start": "2005-01-02 23:00:00+00:00",
 "reference_bars": 47456,
 "reference_start": "2017-12-01 01:00:00+00:00",
 "common_bars": 47455,
 "median_level_diff_pct": 0.11881319000373036,
 "median_abs_level_diff_pct": 0.12066741658807167,
 "p95_abs_level_diff_pct": 0.5386781524680573,
 "hourly_return_corr_by_lag": {
  "-2": 0.002494492613516522,
  "-1": -0.005684731705752188,
  "0": 0.9781862364225807,
  "1": -0.011120239909514888,
  "2": -0.0005602722255922543
 },
 "return_tracking_error_bps": 1.8997935406441424
}
           median  <lambda_0>
timestamp                    
2017        1.092       1.203
2018        0.282       1.017
2019        0.275       0.518
2020        0.008       0.281
2021        0.003       0.031
2022        0.024       0.231
2023        0.199       0.363
2024        0.162       0.330
2025        0.177       0.396
2026        0.156       0.270
```

Reading: hourly returns correlate 0.978 at lag 0 and ~0 at lags +-1/+-2 (timestamps aligned); tracking error 1.9 bps/hour; median level gap 0.12% (larger in 2017-2018, ~1%). The reference is a provider index/CFD whose level can differ from the spot formula; the divergence features use returns and N-bar extremes, which are driven by the return series.
