"""Unsupervised regime discovery.

Regimes are not defined by hand. A Gaussian mixture is fitted on TRAIN only, on backward-looking state
variables (realised volatility, trend efficiency, volatility ratio); the number of regimes is chosen
by BIC. Labels are assigned *after* fitting, from the cluster centroids, purely for readability.
Prediction at bar t uses only state variables computed from data up to t, so the regime series is causal.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np
import pandas as pd
from sklearn.mixture import GaussianMixture

from xquant.errors import InsufficientDataError


def state_variables(close: pd.Series) -> pd.DataFrame:
    lr = np.log(close).diff()
    vol20 = lr.rolling(20, min_periods=15).std()
    vol5 = lr.rolling(5, min_periods=4).std()
    vol60 = lr.rolling(60, min_periods=40).std()
    move20 = (np.log(close) - np.log(close).shift(20)).abs()
    path20 = lr.abs().rolling(20, min_periods=15).sum()
    return pd.DataFrame({
        "log_vol20": np.log(vol20),
        "efficiency20": move20 / path20,
        "vol_ratio": np.log(vol5 / vol60),
    }, index=close.index)


@dataclass
class RegimeModel:
    k: int
    labels: dict[int, str]
    centroids: pd.DataFrame
    bic: dict[int, float]
    mean_: np.ndarray
    std_: np.ndarray
    model: GaussianMixture
    stats: dict[str, Any] = field(default_factory=dict)

    def predict(self, close: pd.Series) -> pd.Series:
        X = state_variables(close)
        ok = X.notna().all(axis=1)
        out = pd.Series(np.nan, index=close.index, name="regime")
        if ok.any():
            Z = (X[ok].to_numpy() - self.mean_) / self.std_
            out[ok] = self.model.predict(Z)
        return out


def _label(centroids: pd.DataFrame) -> dict[int, str]:
    vol_rank = centroids["log_vol20"].rank()
    eff_rank = centroids["efficiency20"].rank()
    k = len(centroids)
    labels = {}
    for i in centroids.index:
        v = "high-vol" if vol_rank[i] > k / 2 else "low-vol"
        e = "trending" if eff_rank[i] > k / 2 else "ranging"
        vr = centroids.loc[i, "vol_ratio"]
        t = " expanding" if vr > 0.15 else (" contracting" if vr < -0.15 else "")
        labels[int(i)] = f"R{i}: {v} {e}{t}"
    return labels


def fit_regimes(close: pd.Series, train: slice, k_range: range = range(2, 6), seed: int = 0) -> RegimeModel:
    X = state_variables(close).iloc[train].dropna()
    if len(X) < 300:
        raise InsufficientDataError(f"regime discovery needs >=300 train bars, got {len(X)}")
    mean, std = X.mean().to_numpy(), X.std().to_numpy()
    Z = (X.to_numpy() - mean) / std
    bics: dict[int, float] = {}
    models: dict[int, GaussianMixture] = {}
    for k in k_range:
        gm = GaussianMixture(n_components=k, covariance_type="full", n_init=4, random_state=seed).fit(Z)
        bics[k] = float(gm.bic(Z))
        models[k] = gm
    best = min(bics, key=lambda kk: bics[kk])
    gm = models[best]
    cent = pd.DataFrame(gm.means_ * std + mean, columns=X.columns)
    model = RegimeModel(k=best, labels=_label(cent), centroids=cent, bic=bics, mean_=mean, std_=std, model=gm)
    reg = model.predict(close).iloc[train].dropna().astype(int)
    trans = pd.crosstab(reg.shift(1).dropna().astype(int), reg.iloc[1:].values, normalize="index")
    model.stats = {"persistence": {int(i): float(trans.loc[i, i]) if i in trans.index and i in trans.columns else 0.0
                                   for i in range(best)},
                   "occupancy": {int(i): float((reg == i).mean()) for i in range(best)}}
    return model
