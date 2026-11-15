"""All pre-specified analyses (see docs/analysis_plan.md).

`run_all()` writes CSV/Markdown tables to output/tables and figures to
output/figures, and returns a dict of result frames for the notebook.
Model labels (C1, P1, R1, S1, ...) match the analysis plan.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import figures as F
from .paths import PROC, TAB
from .stats import (SEED, conley_se, index_uncertainty, influence_table, knn_weights, leave_one_out,
                    morans_i, mundlak, ols, pearson, spearman, twfe, zscore)

HP = "High Priority to Achieve Basic Equality"
RPP_OUTCOMES = {
    "log_zhvi_real": "Home value (ZHVI, real)",
    "log_rpp_housing": "RPP: housing rents",
    "log_rpp_all": "RPP: all items",
    "log_rpp_goods": "RPP: goods",
    "log_rpp_utilities": "RPP: utilities",
    "log_rpp_other_services": "RPP: other services",
    "log_real_pcpi_rpp": "Real per-capita income (RPP-adjusted)",
}


def pct(b: float) -> float:
    return 100 * (np.exp(b) - 1)


def write(df: pd.DataFrame, name: str, floatfmt: str = ".3f") -> pd.DataFrame:
    df.to_csv(TAB / f"{name}.csv", index=False, float_format="%.6g")
    (TAB / f"{name}.md").write_text(df.to_markdown(index=False, floatfmt=floatfmt), encoding="utf-8")
    return df


def load() -> tuple[pd.DataFrame, pd.DataFrame]:
    panel = pd.read_csv(PROC / "state_year_panel.csv", dtype={"fips": str})
    cs = panel[panel.year == 2023].copy().reset_index(drop=True)
    # partisan control is observed through 2022 only -> use 2022 value (documented)
    pc22 = panel.loc[panel.year == 2022, ["st", "party_control", "dem_trifecta", "rep_trifecta"]]
    cs = cs.drop(columns=["party_control", "dem_trifecta", "rep_trifecta"]).merge(pc22, on="st")
    cs["D"] = zscore(cs.sdi)
    cs["D_add"] = zscore(cs.sdi_additive)
    cs["MAP"] = zscore(cs.map_overall)
    cs["log_hh_income"] = np.log(cs.hh_income)
    cs["log_acs_value"] = np.log(cs.acs_value)
    cs["log_pti"] = np.log(cs.price_to_income)
    cs["zhvi_k"] = cs.zhvi / 1000
    return panel, cs


CONTROLS = "log_hh_income + ba_share + urban_share"


# --------------------------------------------------------------------------
# Descriptives
# --------------------------------------------------------------------------

def descriptives(cs: pd.DataFrame) -> pd.DataFrame:
    cols = {"sdi": "SDI 2.0 (democracy_mcmc)", "sdi_additive": "SDI 2.0 additive", "zhvi": "ZHVI ($)",
            "acs_value": "ACS median owner-occupied value ($)", "hh_income": "ACS median household income ($)",
            "price_to_income": "ZHVI / median HH income", "map_overall": "MAP overall policy tally",
            "rpp_all": "RPP all items", "rpp_housing": "RPP housing rents", "rpp_goods": "RPP goods",
            "rpp_utilities": "RPP utilities", "rpp_other_services": "RPP other services",
            "real_pcpi_rpp": "Real per-capita personal income (2017 $, RPP-adjusted)",
            "ba_share": "Bachelor's+ share (25+)", "urban_share": "Urban share (2020)"}
    rows = []
    for c, lab in cols.items():
        s = cs[c]
        rows.append({"variable": lab, "n": s.notna().sum(), "mean": s.mean(), "sd": s.std(), "min": s.min(),
                     "median": s.median(), "max": s.max()})
    return write(pd.DataFrame(rows), "t01_descriptives_2023", ".3g")


def correlations(cs: pd.DataFrame) -> pd.DataFrame:
    pairs = [
        ("sdi", "zhvi", "SDI vs ZHVI ($)"), ("sdi", "log_zhvi", "SDI vs log ZHVI"),
        ("sdi_additive", "log_zhvi", "SDI additive vs log ZHVI"),
        ("sdi", "log_acs_value", "SDI vs log ACS median value"),
        ("sdi", "log_pti", "SDI vs log(ZHVI / HH income)"),
        ("sdi", "log_hh_income", "SDI vs log HH income"), ("sdi", "ba_share", "SDI vs BA share"),
        ("sdi", "urban_share", "SDI vs urban share"),
        ("map_overall", "log_zhvi", "MAP tally vs log ZHVI"), ("map_overall", "log_pti", "MAP tally vs log(ZHVI / income)"),
        ("sdi", "map_overall", "SDI vs MAP tally"), ("hrc_rank", "sdi", "HRC category (ordinal) vs SDI"),
        ("hrc_rank", "log_zhvi", "HRC category (ordinal) vs log ZHVI"),
        ("hrc_rank", "map_overall", "HRC category (ordinal) vs MAP tally"),
        ("log_zhvi", "log_acs_value", "log ZHVI vs log ACS value (measurement check)"),
    ]
    rows = []
    for a, b, lab in pairs:
        rs, ps = spearman(cs[a], cs[b])
        row = {"pair": lab, "n": int(cs[[a, b]].dropna().shape[0]), "spearman": rs, "spearman_p": ps}
        if not a.startswith("hrc"):  # ordinal categories: rank correlation only
            r, p, lo, hi = pearson(cs[a], cs[b])
            row.update({"pearson": r, "pearson_ci_low": lo, "pearson_ci_high": hi, "pearson_p": p})
        rows.append(row)
    return write(pd.DataFrame(rows), "t02_correlations_2023")


# --------------------------------------------------------------------------
# Cross-sectional models
# --------------------------------------------------------------------------

def cross_section_models(cs: pd.DataFrame) -> dict:
    specs = [
        ("C1 bivariate", "log_zhvi ~ D", "D"),
        ("C2 + income, education, urban", f"log_zhvi ~ D + {CONTROLS}", "D"),
        ("C3 C2 + region", f"log_zhvi ~ D + {CONTROLS} + C(region)", "D"),
        ("C4 C2 + party control (2022)", f"log_zhvi ~ D + {CONTROLS} + dem_trifecta + rep_trifecta", "D"),
        ("E1 MAP bivariate", "log_zhvi ~ MAP", "MAP"),
        ("E2 MAP + controls", f"log_zhvi ~ MAP + {CONTROLS}", "MAP"),
        ("E3 SDI + MAP + controls (SDI)", f"log_zhvi ~ D + MAP + {CONTROLS}", "D"),
        ("E3 SDI + MAP + controls (MAP)", f"log_zhvi ~ D + MAP + {CONTROLS}", "MAP"),
        ("A1 log(ZHVI/income) bivariate", "log_pti ~ D", "D"),
        ("A1 log(ZHVI/income) + educ, urban", "log_pti ~ D + ba_share + urban_share", "D"),
        ("A1m log(ZHVI/income) ~ MAP", "log_pti ~ MAP", "MAP"),
    ]
    W = knn_weights(cs.lat, cs.lon, k=5)
    rows, fits = [], {}
    for lab, f, term in specs:
        fit = ols(f, cs, lab)
        fits[lab] = fit
        row = fit.coef(term)
        row["pct_per_sd"] = pct(row["coef"])
        for km in (500, 1000):
            se = conley_se(fit, cs, km)[term]
            row[f"conley{km}_se"] = se
        mi = morans_i(fit.res.resid.values, W[np.ix_(fit.res.resid.index, fit.res.resid.index)]
                      / W[np.ix_(fit.res.resid.index, fit.res.resid.index)].sum(axis=1, keepdims=True))
        row["resid_morans_i"] = mi["morans_i"]
        row["morans_p"] = mi["p_perm_two_sided"]
        rows.append(row)
    tab = write(pd.DataFrame(rows), "t03_cross_section_models")
    # collinearity between SDI and MAP
    r = np.corrcoef(cs.D, cs.MAP)[0, 1]
    vif = pd.DataFrame([{"pair": "SDI vs MAP (2023)", "pearson_r": r, "vif_bivariate": 1 / (1 - r ** 2)}])
    write(vif, "t03b_sdi_map_collinearity")
    # full coefficient listings for the main models
    full = []
    for lab in ["C1 bivariate", "C2 + income, education, urban", "E3 SDI + MAP + controls (SDI)"]:
        res = fits[lab].res
        ci = res.conf_int()
        for t in res.params.index:
            full.append({"model": lab, "term": t, "coef": res.params[t], "se_hc3": res.bse[t],
                         "ci_low": ci.loc[t, 0], "ci_high": ci.loc[t, 1], "n": int(res.nobs),
                         "r2": res.rsquared})
    write(pd.DataFrame(full), "t03c_cross_section_full_coefficients")
    return {"table": tab, "fits": fits, "vif": vif}


def hrc_models(cs: pd.DataFrame) -> pd.DataFrame:
    ref = f"C(hrc_category, Treatment(reference='{HP}'))"
    rows = []
    for lab, f in [("HRC categories", f"log_zhvi ~ {ref}"), ("HRC categories + controls", f"log_zhvi ~ {ref} + {CONTROLS}")]:
        fit = ols(f, cs, lab)
        ci = fit.res.conf_int()
        for t in fit.res.params.index:
            if "hrc_category" in t:
                cat = t.split("[T.")[1].rstrip("]")
                rows.append({"model": lab, "category_vs_high_priority": cat,
                             "n_in_category": int((cs.hrc_category == cat).sum()), "coef": fit.res.params[t],
                             "ci_low": ci.loc[t, 0], "ci_high": ci.loc[t, 1], "pct": pct(fit.res.params[t]),
                             "n": fit.n})
    means = cs.groupby("hrc_category").agg(n=("st", "size"), median_zhvi=("zhvi", "median"),
                                           mean_sdi=("sdi", "mean")).reset_index()
    write(means, "t07b_hrc_category_summary", ".3g")
    return write(pd.DataFrame(rows), "t07_hrc_category_models")


def sensitivity(panel: pd.DataFrame, cs: pd.DataFrame) -> pd.DataFrame:
    rows = []

    def add(label, fit, term, note=""):
        r = fit.coef(term)
        r.update({"spec": label, "note": note})
        rows.append(r)

    f2 = f"log_zhvi ~ D + {CONTROLS}"
    add("Main C1", ols("log_zhvi ~ D", cs, "C1"), "D")
    add("Main C2", ols(f2, cs, "C2"), "D")
    add("S1 additive SDI (C1)", ols("log_zhvi ~ D_add", cs, "S1"), "D_add")
    add("S1 additive SDI (C2)", ols(f2.replace("D +", "D_add +"), cs, "S1"), "D_add")
    add("S2 ACS median value (C1)", ols("log_acs_value ~ D", cs, "S2"), "D")
    add("S2 ACS median value (C2)", ols(f"log_acs_value ~ D + {CONTROLS}", cs, "S2"), "D")
    add("S3 ZHVI in $000 (C1)", ols("zhvi_k ~ D", cs, "S3"), "D", "coefficient in $000 per SD")
    add("S3 ZHVI in $000 (C2)", ols(f"zhvi_k ~ D + {CONTROLS}", cs, "S3"), "D", "coefficient in $000 per SD")
    sub = cs[~cs.st.isin(["AK", "HI"])].copy()
    sub["D"] = zscore(sub.sdi)
    add("S4 drop AK, HI (C1)", ols("log_zhvi ~ D", sub, "S4"), "D")
    add("S4 drop AK, HI (C2)", ols(f2, sub, "S4"), "D")
    add("S5 population-weighted (C1)", ols("log_zhvi ~ D", cs, "S5", weights="population"), "D",
        "estimand: person-weighted association")
    add("S5 population-weighted (C2)", ols(f2, cs, "S5", weights="population"), "D",
        "estimand: person-weighted association")
    add("S6 region indicators (C3)", ols(f2 + " + C(region)", cs, "S6"), "D")
    add("S7 party control 2022 (C4)", ols(f2 + " + dem_trifecta + rep_trifecta", cs, "S7"), "D", "Nebraska missing")

    # S8 Rhodes EDS / S9 COVI: 2022 cross-section with 2022 housing
    p22 = panel[panel.year == 2022].copy()
    p22["log_hh_income"] = np.log(p22.hh_income)
    for col, lab, note in [("sdi", "SDI 2022 (reference for S8/S9)", "same 2022 sample"),
                           ("eds", "S8 Rhodes EDS 2022", "shares many inputs with SDI"),
                           ("covi", "S9 COVI 2022 (higher = costlier voting)", "voting access, narrower concept")]:
        p22["X"] = zscore(p22[col])
        add(lab + " (C1)", ols("log_zhvi ~ X", p22, lab), "X", note)
        add(lab + " (C2)", ols(f"log_zhvi ~ X + {CONTROLS}", p22, lab), "X", note)
    tab = pd.DataFrame(rows)
    tab["pct_per_sd"] = np.where(tab.spec.str.startswith("S3"), np.nan, pct(tab.coef))
    tab = tab[["spec", "coef", "se", "ci_low", "ci_high", "p", "pct_per_sd", "n", "r2", "note"]]

    # S10 SDI posterior-draw uncertainty
    s10 = []
    for lab, f in [("S10 SDI draws (C1)", "log_zhvi ~ D"), ("S10 SDI draws (C2)", f2)]:
        draws = index_uncertainty(f, cs, "sdi", "sdi_sd", "D")
        s10.append({"spec": lab, "coef": draws.coef.mean(), "ci_low": draws.coef.quantile(0.025),
                    "ci_high": draws.coef.quantile(0.975), "n": len(cs),
                    "note": "2,000 draws; interval reflects index uncertainty only, not sampling error"})
    tab = pd.concat([tab, pd.DataFrame(s10)], ignore_index=True)
    return write(tab, "t04_sensitivity")


def influence(cs: pd.DataFrame) -> dict:
    fit1 = ols("log_zhvi ~ D", cs, "C1")
    fit2 = ols(f"log_zhvi ~ D + {CONTROLS}", cs, "C2")
    inf1 = influence_table(fit1, cs, "D").head(8)
    inf1.insert(0, "model", "C1")
    inf2 = influence_table(fit2, cs, "D").head(8)
    inf2.insert(0, "model", "C2")
    write(pd.concat([inf1, inf2]), "t09_influence_top8")
    loo1 = leave_one_out("log_zhvi ~ D", cs, "D")
    loo2 = leave_one_out(f"log_zhvi ~ D + {CONTROLS}", cs, "D")
    loo = pd.concat([loo1.assign(model="C1"), loo2.assign(model="C2")])
    write(loo, "t09b_leave_one_out")
    summ = loo.groupby("model").agg(min_coef=("coef", "min"), max_coef=("coef", "max"),
                                    dropped_at_min=("coef", lambda s: loo.loc[s.idxmin(), "dropped"].iloc[0] if hasattr(loo.loc[s.idxmin(), "dropped"], "iloc") else loo.loc[s.idxmin(), "dropped"]),
                                    n_ci_excluding_zero=("ci_low", lambda s: int((s > 0).sum()))).reset_index()
    write(summ, "t09c_leave_one_out_summary")
    return {"loo": loo, "summary": summ, "inf": pd.concat([inf1, inf2])}


# --------------------------------------------------------------------------
# Panels
# --------------------------------------------------------------------------

def annual_correlations(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for y, g in panel[panel.year.between(2000, 2023)].groupby("year"):
        g = g.dropna(subset=["sdi", "log_zhvi"])
        r, p, lo, hi = pearson(g.sdi, g.log_zhvi)
        rs, _ = spearman(g.sdi, g.log_zhvi)
        rows.append({"year": y, "n": len(g), "pearson": r, "ci_low": lo, "ci_high": hi, "spearman": rs,
                     "sd_sdi": g.sdi.std()})
    return write(pd.DataFrame(rows), "t08_annual_sdi_zhvi_correlations")


def map_annual(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for y, g in panel.dropna(subset=["map_overall"]).groupby("year"):
        r1, _ = spearman(g.map_overall, g.log_zhvi)
        row = {"year": y, "map_asof": g.map_asof.iloc[0], "map_max_positive": g.map_max_positive.iloc[0],
               "n": len(g), "spearman_map_logzhvi": r1}
        if g.sdi.notna().all():
            row["spearman_map_sdi"] = spearman(g.map_overall, g.sdi)[0]
            row["spearman_sdi_logzhvi"] = spearman(g.sdi, g.log_zhvi)[0]
        rows.append(row)
    return write(pd.DataFrame(rows), "t08b_map_annual_correlations")


def sdi_variance_decomposition(panel: pd.DataFrame) -> pd.DataFrame:
    p = panel[panel.year.between(2000, 2023)].copy()
    rows = []
    for c in ["sdi", "log_zhvi_real"]:
        q = p.dropna(subset=[c])
        total = q[c].var()
        within = (q[c] - q.groupby("st")[c].transform("mean")).var()
        tw = q[c] - q.groupby("st")[c].transform("mean") - q.groupby("year")[c].transform("mean") + q[c].mean()
        rows.append({"variable": c, "total_var": total, "within_state_share": within / total,
                     "two_way_residual_share": tw.var() / total})
    # how often SDI changes in odd years
    s = p.sort_values(["st", "year"])
    s["d"] = s.groupby("st").sdi.diff().abs()
    odd = s[s.year % 2 == 1].d.mean()
    even = s[(s.year % 2 == 0) & (s.year > 2000)].d.mean()
    rows.append({"variable": "mean |annual change in SDI|: odd years / even years", "total_var": np.nan,
                 "within_state_share": odd, "two_way_residual_share": even})
    return write(pd.DataFrame(rows), "t05c_variance_decomposition")


def panel_models(panel: pd.DataFrame) -> dict:
    p = panel[panel.year.between(2000, 2023)].copy()
    rows = []
    specs = [
        ("P1a TWFE, no controls", "sdi", None),
        ("P1b TWFE + log real PCPI", "sdi + log_pcpi_real", None),
        ("P1b Driscoll-Kraay(3)", "sdi + log_pcpi_real", 3),
    ]
    for lab, rhs, dk in specs:
        fit = twfe(rhs, "log_zhvi_real", p, lab, driscoll_kraay_lags=dk)
        r = fit.coef("sdi")
        r["pct_per_unit"] = pct(r["coef"])
        r["n_states"] = p.dropna(subset=["log_zhvi_real"]).st.nunique()
        rows.append(r)
    # Same-window TWFE 2008-2023 (for comparison with RPP panel)
    q = p[p.year >= 2008]
    fit = twfe("sdi + log_pcpi_real", "log_zhvi_real", q, "P1c TWFE 2008-2023 + log real PCPI")
    r = fit.coef("sdi")
    r["pct_per_unit"] = pct(r["coef"])
    rows.append(r)
    # Mundlak within / between
    mfit, between = mundlak("log_zhvi_real", "sdi", ["log_pcpi_real"], p, "P2 Mundlak (CRE)")
    w = mfit.coef("sdi")
    w["term"] = "within (x)"
    rows += [w, between]
    for r in rows[-2:]:
        r["pct_per_unit"] = pct(r["coef"])
    # Long differences
    ld_rows = []
    for start in (2000, 2008):
        a = p[p.year == start].set_index("st")
        b = p[p.year == 2023].set_index("st")
        d = pd.DataFrame({"dy": b.log_zhvi_real - a.log_zhvi_real, "dsdi": b.sdi - a.sdi,
                          "dinc": b.log_pcpi_real - a.log_pcpi_real, "sdi0": a.sdi}).dropna().reset_index()
        for lab, f, term in [(f"P3 long diff {start}-2023", "dy ~ dsdi", "dsdi"),
                             (f"P3 long diff {start}-2023 + d log PCPI", "dy ~ dsdi + dinc", "dsdi")]:
            fit = ols(f, d, lab)
            r = fit.coef(term)
            r["pct_per_unit"] = pct(r["coef"])
            ld_rows.append(r)
    rows += ld_rows
    tab = write(pd.DataFrame(rows), "t05_panel_models")
    return {"table": tab, "mundlak": mfit}


def appreciation(panel: pd.DataFrame) -> pd.DataFrame:
    """H1: FHFA real log appreciation vs initial SDI and SDI change."""
    rows = []
    for start in (2000, 2008):
        a = panel[panel.year == start].set_index("st")
        b = panel[panel.year == 2023].set_index("st")
        d = pd.DataFrame({
            "app": np.log(b.fhfa_hpi / a.fhfa_hpi) - np.log(b.pce_pi / a.pce_pi),
            "sdi0": a.sdi, "dsdi": b.sdi - a.sdi}).dropna().reset_index()
        d["sdi0_z"] = zscore(d.sdi0)
        for lab, f, term in [(f"H1 real appreciation {start}-2023 ~ initial SDI (z)", "app ~ sdi0_z", "sdi0_z"),
                             (f"H1 real appreciation {start}-2023 ~ SDI change", "app ~ dsdi", "dsdi")]:
            fit = ols(f, d, lab)
            r = fit.coef(term)
            r["mean_appreciation_log"] = d.app.mean()
            rows.append(r)
    return write(pd.DataFrame(rows), "t10_fhfa_appreciation")


# --------------------------------------------------------------------------
# Price-level extension
# --------------------------------------------------------------------------

def price_levels(panel: pd.DataFrame, cs: pd.DataFrame) -> pd.DataFrame:
    rows = []
    # Cross-section 2023, identical 50-state sample
    for y, lab in RPP_OUTCOMES.items():
        d = cs.copy()
        for spec, f in [("2023 bivariate", f"{y} ~ D"), ("2023 + educ, urban", f"{y} ~ D + ba_share + urban_share")]:
            fit = ols(f, d, spec)
            r = fit.coef("D")
            d["yz"] = zscore(d[y])
            rz = ols(f.replace(y, "yz", 1), d, spec).coef("D")
            r.update({"outcome": lab, "spec": spec, "pct": pct(r["coef"]), "std_coef": rz["coef"],
                      "std_ci_low": rz["ci_low"], "std_ci_high": rz["ci_high"]})
            rows.append(r)
    # Panel 2008-2023, identical state-year sample across outcomes
    p = panel[panel.year.between(2008, 2023)].dropna(subset=list(RPP_OUTCOMES)).copy()
    n_common = len(p)
    for y, lab in RPP_OUTCOMES.items():
        fit = twfe("sdi", y, p, "TWFE 2008-2023 (common sample)")
        r = fit.coef("sdi")
        within_sd = (p[y] - p.groupby("st")[y].transform("mean") - p.groupby("year")[y].transform("mean")
                     + p[y].mean()).std()
        sdi_within_sd = (p.sdi - p.groupby("st").sdi.transform("mean") - p.groupby("year").sdi.transform("mean")
                         + p.sdi.mean()).std()
        r.update({"outcome": lab, "spec": "TWFE 2008-2023 (common sample)", "pct": pct(r["coef"]),
                  "std_coef": r["coef"] * sdi_within_sd / within_sd,
                  "std_ci_low": r["ci_low"] * sdi_within_sd / within_sd,
                  "std_ci_high": r["ci_high"] * sdi_within_sd / within_sd})
        rows.append(r)
    # ZHVI full sample for reference
    fit = twfe("sdi", "log_zhvi_real", panel[panel.year.between(2000, 2023)], "TWFE 2000-2023 (full ZHVI sample)")
    r = fit.coef("sdi")
    r.update({"outcome": RPP_OUTCOMES["log_zhvi_real"], "spec": "TWFE 2000-2023 (full ZHVI sample)", "pct": pct(r["coef"])})
    rows.append(r)
    tab = pd.DataFrame(rows)[["outcome", "spec", "coef", "se", "ci_low", "ci_high", "p", "pct", "std_coef",
                              "std_ci_low", "std_ci_high", "n", "r2", "se_type"]]
    tab.attrs["n_common"] = n_common
    return write(tab, "t06_price_level_extension")


# --------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------

def make_figures(panel, cs, res) -> list[str]:
    F.style()
    import matplotlib.pyplot as plt
    out = []
    hl = ["CA", "HI", "WA", "TN", "IL", "MT", "WI", "MA"]

    # F1 raw and log scatter
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    F.scatter_labeled(ax[0], cs.sdi, cs.zhvi, cs.st, "SDI 2.0 electoral democracy score, 2023",
                      "Zillow home value index, 2023", "Home values vs electoral democracy (dollars)", hl)
    F.dollars(ax[0])
    F.scatter_labeled(ax[1], cs.sdi, cs.zhvi, cs.st, "SDI 2.0 electoral democracy score, 2023",
                      "Zillow home value index, 2023 (log scale)", "Same data, log scale (fit on log values)", hl, logy=True)
    F.log_dollar_axis(ax[1])
    fig.text(0.01, -0.03, "50 states. Line: OLS fit. ZHVI = mean of monthly values (35th-65th pct homes).", fontsize=8, color=F.INK2)
    out.append(F.save(fig, "f01_sdi_vs_home_values_2023"))

    # F2 annual cross-sectional correlations
    ac = res["annual"]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.fill_between(ac.year, ac.ci_low, ac.ci_high, color=F.S1, alpha=0.15, lw=0)
    ax.plot(ac.year, ac.pearson, color=F.S1, marker="o", ms=4, label="Pearson r (95% CI)")
    ax.plot(ac.year, ac.spearman, color=F.S2, marker="s", ms=4, label="Spearman rho")
    ax.axhline(0, color=F.INK2, lw=1, ls="--")
    ax.set_ylabel("Correlation, SDI vs log home value")
    ax.set_title("Between-state correlation by year, 2000-2023")
    ax.legend(loc="upper left")
    fig.text(0.01, -0.04, "Each point is a separate 46-50 state cross-section (ZHVI gaps before 2009).",
             fontsize=8, color=F.INK2)
    out.append(F.save(fig, "f02_annual_correlations"))

    # F3 within-state partial plot (two-way demeaned)
    p = panel[panel.year.between(2000, 2023)].dropna(subset=["log_zhvi_real", "sdi"]).copy()
    for c in ["sdi", "log_zhvi_real"]:
        p[c + "_tw"] = p[c] - p.groupby("st")[c].transform("mean") - p.groupby("year")[c].transform("mean") + p[c].mean()
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.scatter(p.sdi_tw, p.log_zhvi_real_tw, s=10, color=F.S1, alpha=0.45, lw=0)
    F._fit_line(ax, p.sdi_tw.values, p.log_zhvi_real_tw.values)
    ax.set_xlabel("SDI, deviation from state and year means")
    ax.set_ylabel("log real home value, deviation from state and year means")
    ax.set_title("Within-state variation, 2000-2023")
    fig.text(0.01, -0.03, f"{len(p)} state-years. Approximate two-way demeaning (unbalanced panel); "
             "coefficients in t05 come from dummy-variable regressions.", fontsize=8, color=F.INK2)
    out.append(F.save(fig, "f03_within_state"))

    # F4 leave-one-out
    loo = res["influence"]["loo"]
    fig, ax = plt.subplots(1, 2, figsize=(12, 7), sharex=True)
    for a, m, col in [(ax[0], "C1", F.S1), (ax[1], "C2", F.S2)]:
        d = loo[loo.model == m].sort_values("coef").reset_index(drop=True)
        F.coef_plot(a, d, "dropped", f"{m}: coefficient on SDI with each state dropped",
                    "log home value per SD of SDI", color=col)
        a.tick_params(axis="y", labelsize=6.5)
    out.append(F.save(fig, "f04_leave_one_out"))

    # F5 price-level extension
    t = res["prices"]
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.8), sharey=True)
    for a, spec, col, ttl in [(ax[0], "2023 bivariate", F.S1, "Cross-section 2023 (between states)"),
                              (ax[1], "TWFE 2008-2023 (common sample)", F.S2, "TWFE 2008-2023 (within states)")]:
        d = t[t.spec == spec].copy()
        d = d.set_index("outcome").loc[list(RPP_OUTCOMES.values())].reset_index()
        d = d.rename(columns={"std_coef": "coef_s"})
        d2 = pd.DataFrame({"outcome": d.outcome, "coef": d.coef_s, "ci_low": d.std_ci_low, "ci_high": d.std_ci_high})
        F.coef_plot(a, d2, "outcome", ttl, "standardised coefficient (SD of outcome per SD of SDI)", color=col)
    out.append(F.save(fig, "f05_price_level_extension"))

    # F6 HRC categories
    from .build import HRC_CATEGORIES
    fig, ax = plt.subplots(figsize=(9, 4.8))
    rng = np.random.default_rng(SEED)
    for i, cat in enumerate(HRC_CATEGORIES):
        d = cs[cs.hrc_category == cat]
        x = i + rng.uniform(-0.12, 0.12, len(d))
        ax.scatter(x, d.zhvi, s=36, color=F.BLUE_RAMP[i], edgecolor=F.INK2, lw=0.6, zorder=3)
        ax.hlines(d.zhvi.median(), i - 0.25, i + 0.25, color=F.INK, lw=2)
        for xi, yi, s in zip(x, d.zhvi, d.st):
            ax.annotate(s, (xi, yi), xytext=(4, 0), textcoords="offset points", fontsize=6.5, color=F.INK2)
    ax.set_xticks(range(4))
    ax.set_xticklabels([f"{c.replace(' to ', ' to\n').replace('Toward ', 'Toward\n')}\n(n={(cs.hrc_category == c).sum()})"
                        for c in HRC_CATEGORIES], fontsize=8)
    F.log_dollar_axis(ax)
    ax.set_ylabel("ZHVI 2023 (log scale)")
    ax.set_title("Home values by HRC 2023 State Equality Index category")
    ax.grid(axis="x", visible=False)
    fig.text(0.01, -0.06, "Black bar = median. Categories are ordered, not equally spaced. HRC SEI 2023 released 2024-01-30.",
             fontsize=8, color=F.INK2)
    out.append(F.save(fig, "f06_hrc_categories"))

    # F7 MAP vs home values, SDI vs MAP
    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    F.scatter_labeled(ax[0], cs.map_overall, cs.zhvi, cs.st, "MAP overall LGBTQ policy tally (as of 2023-06-28)",
                      "ZHVI 2023 (log scale)", "Home values vs LGBTQ policy tally", hl, logy=True)
    F.log_dollar_axis(ax[0])
    F.scatter_labeled(ax[1], cs.sdi, cs.map_overall, cs.st, "SDI 2.0, 2023", "MAP overall policy tally",
                      "Democracy vs LGBTQ policy tally", hl, color=F.S3)
    out.append(F.save(fig, "f07_map_scatter"))

    # F8 affordability proxy
    fig, ax = plt.subplots(figsize=(7, 5))
    F.scatter_labeled(ax, cs.sdi, cs.price_to_income, cs.st, "SDI 2.0, 2023",
                      "ZHVI / ACS median household income, 2023", "Price-to-income ratio (affordability proxy)", hl)
    out.append(F.save(fig, "f08_price_to_income"))

    # F9 MAP annual correlations
    ma = res["map_annual"]
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(ma.year, ma.spearman_map_logzhvi, color=F.S1, marker="o", label="MAP tally vs log ZHVI")
    m2 = ma.dropna(subset=["spearman_map_sdi"])
    ax.plot(m2.year, m2.spearman_map_sdi, color=F.S3, marker="s", label="MAP tally vs SDI")
    ax.plot(m2.year, m2.spearman_sdi_logzhvi, color=F.S2, marker="^", label="SDI vs log ZHVI")
    ax.set_ylim(0, 1)
    ax.set_ylabel("Spearman rho (50 states)")
    ax.set_title("Annual rank correlations, MAP snapshots 2017-2024")
    ax.legend(loc="lower left")
    fig.text(0.01, -0.05, "MAP maximum points change in most years; compare years only as rank patterns.",
             fontsize=8, color=F.INK2)
    out.append(F.save(fig, "f09_map_annual"))

    # F10 measurement: ZHVI vs ACS
    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    F.scatter_labeled(ax, cs.acs_value, cs.zhvi, cs.st, "ACS median owner-occupied value (self-reported), 2023",
                      "ZHVI, 2023", "Two home-value measures, 2023", ["HI", "CA", "ME", "VT", "MT"])
    lim = [min(cs.acs_value.min(), cs.zhvi.min()) * 0.9, max(cs.acs_value.max(), cs.zhvi.max()) * 1.05]
    ax.plot(lim, lim, color=F.INK2, lw=1, ls="--")
    F.dollars(ax)
    F.dollars(ax, "x")
    out.append(F.save(fig, "f10_zhvi_vs_acs"))
    return out


def run_all() -> dict:
    panel, cs = load()
    res = {}
    res["desc"] = descriptives(cs)
    res["corr"] = correlations(cs)
    res["cross"] = cross_section_models(cs)
    res["hrc"] = hrc_models(cs)
    res["sens"] = sensitivity(panel, cs)
    res["influence"] = influence(cs)
    res["annual"] = annual_correlations(panel)
    res["map_annual"] = map_annual(panel)
    res["vardecomp"] = sdi_variance_decomposition(panel)
    res["panel"] = panel_models(panel)
    res["appreciation"] = appreciation(panel)
    res["prices"] = price_levels(panel, cs)
    res["figures"] = make_figures(panel, cs, res)
    return res
