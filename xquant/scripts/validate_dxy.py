"""Validate the synthetic DXY (ICE formula on 6 Dukascopy pairs) against Dukascopy's own DOLLARIDXUSD."""
import json
import numpy as np
import pandas as pd
from xquant.data.sources.basket import BasketSource
from xquant.data.sources.dukascopy_candles import DukascopyCandleSource

syn = BasketSource("dxy", start="2005-01-01", end="2026-10-01", granularity="hour").fetch_series()["close"]
ref = DukascopyCandleSource("DOLLARIDXUSD", "2017-01-01", "2026-10-01", point=0.001).fetch_series()["close"]
both = pd.concat({"syn": syn, "ref": ref}, axis=1, join="inner").dropna()
diff_pct = (both.syn / both.ref - 1) * 100
r = np.log(both).diff().dropna()
lag = {k: float(r.syn.corr(r.ref.shift(k))) for k in (-2, -1, 0, 1, 2)}
yearly = diff_pct.groupby(diff_pct.index.year).agg(["median", lambda s: s.abs().quantile(0.95)])
out = {"synthetic_bars": int(len(syn)), "synthetic_start": str(syn.index[0]), "reference_bars": int(len(ref)),
       "reference_start": str(ref.index[0]), "common_bars": int(len(both)),
       "median_level_diff_pct": float(diff_pct.median()), "median_abs_level_diff_pct": float(diff_pct.abs().median()),
       "p95_abs_level_diff_pct": float(diff_pct.abs().quantile(0.95)),
       "hourly_return_corr_by_lag": lag, "return_tracking_error_bps": float((r.syn - r.ref).std() * 1e4)}
print(json.dumps(out, indent=1))
print(yearly.round(3).to_string())
