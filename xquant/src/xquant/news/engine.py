"""NEWS INTELLIGENCE ENGINE.

Pipeline: NEWS -> classification -> (expectation context) -> reaction -> subsequent behaviour.

The default classifier is transparent and deterministic (keyword taxonomy + small sentiment lexicon +
novelty against the previous 24h of headlines). It exists so the *measurement* pipeline can be tested
end to end; whether any news class has predictive power is decided only by the event study. A model-
based classifier (e.g. an LLM) can be plugged in through ``NewsClassifier`` without touching the study.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Protocol

import numpy as np
import pandas as pd

from xquant.data.engine import MarketDataset
from xquant.findings import Finding, apply_fdr
from xquant.macro.event_study import event_study
from xquant.validation.splits import DataSplits

ENGINE = "news"

TAXONOMY: dict[str, list[str]] = {
    "inflation": ["inflation", "cpi", "pce", "prices rose", "price pressures"],
    "employment": ["payrolls", "nfp", "unemployment", "jobless", "jobs report", "wages", "hiring"],
    "central_bank": ["fed", "fomc", "ecb", "rate hike", "rate cut", "powell", "lagarde", "monetary policy", "boj", "boe"],
    "growth": ["gdp", "recession", "pmi", "retail sales", "industrial production", "growth"],
    "geopolitics": ["war", "sanctions", "election", "tariff", "conflict", "invasion"],
    "fiscal": ["budget", "deficit", "debt ceiling", "stimulus", "fiscal"],
    "crisis": ["default", "bank failure", "contagion", "bailout", "crash"],
}
COUNTRIES = {"US": ["u.s.", "united states", "fed", "fomc", "powell", "treasury", "american"],
             "EZ": ["euro zone", "eurozone", "ecb", "lagarde", "germany", "france", "italy", "euro area"],
             "UK": ["britain", "uk", "boe", "bank of england"], "JP": ["japan", "boj"], "CN": ["china", "pboc"]}
POS = {"beat", "beats", "surge", "surges", "strong", "stronger", "rise", "rises", "rally", "upbeat", "growth", "gain", "gains", "hawkish"}
NEG = {"miss", "misses", "plunge", "plunges", "weak", "weaker", "fall", "falls", "slump", "fears", "cut", "losses", "dovish", "recession"}
TIER1 = {"reuters", "bloomberg", "wsj", "financial times", "ft", "federal reserve", "ecb"}


@dataclass
class NewsLabel:
    category: str
    countries: list[str]
    sentiment: float
    importance: int
    novelty: float


class NewsClassifier(Protocol):
    def classify(self, news: pd.DataFrame) -> pd.DataFrame: ...


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z][a-z.']+", text.lower()))


class KeywordNewsClassifier:
    def classify(self, news: pd.DataFrame) -> pd.DataFrame:
        rows = []
        recent: list[tuple[pd.Timestamp, set[str]]] = []
        for ts, item in news.iterrows():
            text = f"{item.get('headline', '')} {item.get('body', '') if isinstance(item.get('body', ''), str) else ''}".lower()
            toks = _tokens(text)
            cat = next((c for c, kws in TAXONOMY.items() if any(k in text for k in kws)), "other")
            countries = [c for c, kws in COUNTRIES.items() if any(k in text for k in kws)]
            sent = (len(toks & POS) - len(toks & NEG)) / max(1, len(toks & (POS | NEG)))
            src = str(item.get("source", "")).lower()
            importance = 1 + int(src in TIER1) + int(cat in {"central_bank", "inflation", "employment", "crisis"})
            recent = [(t, s) for t, s in recent if ts - t < pd.Timedelta("24h")]  # type: ignore[operator]
            sim = max((len(toks & s) / max(1, len(toks | s)) for _, s in recent), default=0.0)
            recent.append((ts, toks))  # type: ignore[arg-type]
            rows.append({"category": cat, "countries": ",".join(countries), "sentiment": sent,
                         "importance": importance, "novelty": 1.0 - sim})
        return pd.DataFrame(rows, index=news.index)


class NewsEngine:
    def __init__(self, ds: MarketDataset, splits: DataSplits, classifier: NewsClassifier | None = None,
                 regimes: pd.Series | None = None) -> None:
        self.ds, self.splits, self.regimes = ds, splits, regimes
        self.classifier = classifier or KeywordNewsClassifier()

    def run(self, fdr_alpha: float = 0.05, min_items: int = 30) -> list[Finding]:
        news = self.ds.news
        if news is None or news.empty:
            return [Finding.insufficient(ENGINE, "news", "news_predictive_power",
                                         "no timestamped news source connected (configure asset.news_source); "
                                         "news questions cannot be answered and no news features are used")]
        labels = self.classifier.classify(news)
        df = news.join(labels)
        span = "{} to {}".format(*self.splits.span("train"))
        train = self.splits.mask("train").to_numpy()
        out: list[Finding] = [Finding.descriptive(ENGINE, "news", "news_coverage", "classified news items", span,
                                                  items=int(len(df)), by_category=df["category"].value_counts().to_dict())]
        for cat, g in df.groupby("category"):
            g = g[g["novelty"] > 0.5]  # repeated headlines are not new information
            ev = pd.DataFrame({"std_surprise": np.sign(g["sentiment"]).replace(0, np.nan)}, index=g.index)
            out += event_study(ev, self.ds.bars["close"], train, f"news_{cat}", ENGINE, span,
                               regimes=self.regimes, min_events=min_items)
        apply_fdr([f for f in out if f.status == "TESTED"], fdr_alpha)
        return out
