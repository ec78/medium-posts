"""Estimation helpers: cross-sectional OLS with HC3 / Conley SEs, spatial
diagnostics, influence, leave-one-out, two-way FE panels, Mundlak
between/within decomposition, and index-uncertainty draws."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import stats

SEED = 20261106


# --------------------------------------------------------------------------
# Small utilities
# --------------------------------------------------------------------------

def zscore(s: pd.Series) -> pd.Series:
    return (s - s.mean()) / s.std(ddof=1)


def haversine_km(lat, lon) -> np.ndarray:
    lat, lon = np.radians(np.asarray(lat, float)), np.radians(np.asarray(lon, float))
    dlat = lat[:, None] - lat[None, :]
    dlon = lon[:, None] - lon[None, :]
    a = np.sin(dlat / 2) ** 2 + np.cos(lat[:, None]) * np.cos(lat[None, :]) * np.sin(dlon / 2) ** 2
    return 2 * 6371.0 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


def knn_weights(lat, lon, k: int = 5) -> np.ndarray:
    """Row-standardised inverse-distance weights over each unit's k nearest
    neighbours (by great-circle distance between population centres)."""
    d = haversine_km(lat, lon)
    n = d.shape[0]
    w = np.zeros_like(d)
    for i in range(n):
        order = np.argsort(d[i])
        nn = [j for j in order if j != i][:k]
        w[i, nn] = 1.0 / d[i, nn]
    return w / w.sum(axis=1, keepdims=True)


def morans_i(x: np.ndarray, w: np.ndarray, perms: int = 9999, seed: int = SEED) -> dict:
    x = np.asarray(x, float) - np.mean(x)
    n = len(x)
    s0 = w.sum()

    def stat(v):
        return (n / s0) * (v @ w @ v) / (v @ v)
    obs = stat(x)
    rng = np.random.default_rng(seed)
    sims = np.array([stat(rng.permutation(x)) for _ in range(perms)])
    p = (np.sum(np.abs(sims - sims.mean()) >= abs(obs - sims.mean())) + 1) / (perms + 1)
    return {"morans_i": obs, "expected": -1 / (n - 1), "p_perm_two_sided": p}


# --------------------------------------------------------------------------
# Cross-sectional OLS
# --------------------------------------------------------------------------

@dataclass
class Fit:
    label: str
    formula: str
    res: object
    n: int
    se_type: str

    def coef(self, term: str) -> dict:
        b = self.res.params[term]
        se = self.res.bse[term]
        lo, hi = self.res.conf_int().loc[term]
        return {"model": self.label, "term": term, "coef": b, "se": se, "ci_low": lo, "ci_high": hi,
                "p": self.res.pvalues[term], "n": self.n, "r2": self.res.rsquared, "se_type": self.se_type}


def ols(formula: str, data: pd.DataFrame, label: str, cov: str = "HC3", weights=None, **cov_kw) -> Fit:
    d = data.copy()
    if weights is not None:
        mod = smf.wls(formula, d, weights=d[weights])
    else:
        mod = smf.ols(formula, d)
    res = mod.fit(cov_type=cov, cov_kwds=cov_kw or None)
    return Fit(label, formula, res, int(res.nobs), cov)


def conley_se(fit: Fit, data: pd.DataFrame, cutoff_km: float) -> pd.Series:
    """Conley (1999) spatial-HAC standard errors with a Bartlett kernel in
    great-circle distance. Uses the rows actually used by the model."""
    res = fit.res
    X = res.model.exog
    e = res.resid.values
    rows = data.loc[res.resid.index]
    d = haversine_km(rows.lat.values, rows.lon.values)
    k = np.clip(1 - d / cutoff_km, 0, None)
    xe = X * e[:, None]
    meat = xe.T @ k @ xe
    bread = np.linalg.inv(X.T @ X)
    n, p = X.shape
    v = bread @ meat @ bread * n / (n - p)
    return pd.Series(np.sqrt(np.diag(v)), index=res.params.index)


def influence_table(fit: Fit, data: pd.DataFrame, term: str) -> pd.DataFrame:
    infl = fit.res.get_influence()
    idx = fit.res.resid.index
    out = pd.DataFrame({
        "st": data.loc[idx, "st"].values,
        "cooks_d": infl.cooks_distance[0],
        "leverage": infl.hat_matrix_diag,
        "dfbeta_" + term: infl.dfbetas[:, list(fit.res.params.index).index(term)],
        "studentized_resid": infl.resid_studentized_external,
    })
    return out.sort_values("cooks_d", ascending=False).reset_index(drop=True)


def leave_one_out(formula: str, data: pd.DataFrame, term: str) -> pd.DataFrame:
    rows = []
    for st in data.st:
        r = smf.ols(formula, data[data.st != st]).fit(cov_type="HC3")
        lo, hi = r.conf_int().loc[term]
        rows.append({"dropped": st, "coef": r.params[term], "ci_low": lo, "ci_high": hi})
    return pd.DataFrame(rows)


def index_uncertainty(formula: str, data: pd.DataFrame, mean_col: str, sd_col: str, term: str,
                      draws: int = 2000, seed: int = SEED, standardise: bool = True) -> pd.DataFrame:
    """Re-estimate with the democracy score drawn from N(mean, sd) per state.
    Draws are independent across states (the posterior covariance is not
    published), so this approximates, not reproduces, posterior uncertainty."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(draws):
        d = data.copy()
        d[term] = rng.normal(d[mean_col], d[sd_col])
        if standardise:
            d[term] = zscore(d[term])
        r = smf.ols(formula, d).fit()
        out.append(r.params[term])
    return pd.DataFrame({"coef": out})


# --------------------------------------------------------------------------
# Panels
# --------------------------------------------------------------------------

def twfe(formula_rhs: str, y: str, data: pd.DataFrame, label: str, cluster: str = "st",
         driscoll_kraay_lags: int | None = None) -> Fit:
    """Two-way FE via state and year dummies. Default: state-clustered SEs.
    With driscoll_kraay_lags, uses Driscoll-Kraay (statsmodels 'nw-groupsum')."""
    d = data.dropna(subset=[y] + [v.strip() for v in formula_rhs.split("+")]).copy()
    f = f"{y} ~ {formula_rhs} + C(st) + C(year)"
    mod = smf.ols(f, d)
    if driscoll_kraay_lags is None:
        res = mod.fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d[cluster])[0]})
        se = "cluster(state)"
    else:
        d = d.sort_values(["year", "st"])
        mod = smf.ols(f, d)
        res = mod.fit(cov_type="nw-groupsum",
                      cov_kwds={"time": pd.factorize(d["year"], sort=True)[0], "maxlags": driscoll_kraay_lags})
        se = f"Driscoll-Kraay({driscoll_kraay_lags})"
    return Fit(label, f, res, int(res.nobs), se)


def mundlak(y: str, x: str, controls: list[str], data: pd.DataFrame, label: str) -> tuple[Fit, dict]:
    """Correlated random effects: y on x_it, mean_i(x), controls and their
    state means, plus year dummies; SEs clustered by state.
    within = b[x]; between = b[x] + b[xbar]."""
    cols = [x] + controls
    d = data.dropna(subset=[y] + cols).copy()
    for c in cols:
        d[c + "_bar"] = d.groupby("st")[c].transform("mean")
    rhs = " + ".join(cols + [c + "_bar" for c in cols])
    f = f"{y} ~ {rhs} + C(year)"
    res = smf.ols(f, d).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d["st"])[0]})
    fit = Fit(label, f, res, int(res.nobs), "cluster(state)")
    # between effect and its SE via the linear combination
    names = list(res.params.index)
    L = np.zeros(len(names))
    L[names.index(x)] = 1
    L[names.index(x + "_bar")] = 1
    t = res.t_test(L)
    between = {"model": label, "term": "between (x + xbar)", "coef": float(t.effect[0]),
               "se": float(t.sd[0][0]), "ci_low": float(t.conf_int()[0][0]),
               "ci_high": float(t.conf_int()[0][1]), "p": float(t.pvalue), "n": fit.n,
               "r2": res.rsquared, "se_type": "cluster(state)"}
    return fit, between


def spearman(a, b) -> tuple[float, float]:
    r = stats.spearmanr(a, b, nan_policy="omit")
    return float(r.statistic), float(r.pvalue)


def pearson(a, b) -> tuple[float, float, float, float]:
    """Pearson r, p, and a Fisher-z 95% CI."""
    m = ~(pd.isna(a) | pd.isna(b))
    a, b = np.asarray(a)[m], np.asarray(b)[m]
    r, p = stats.pearsonr(a, b)
    z, se = np.arctanh(r), 1 / np.sqrt(len(a) - 3)
    return float(r), float(p), float(np.tanh(z - 1.96 * se)), float(np.tanh(z + 1.96 * se))
