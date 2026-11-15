"""Mover's-eye extension: affordability matrix and cheapest entry points (2023).

Spec: docs/analysis_plan.md, "Mover's-eye extension". Descriptive only. It
measures the price gap a household faces when moving between states, not why
the gap exists.

`run_mover()` writes processed data (county ZHVI, entry points, the full
origin x destination matrix), tables t11-t14 and figures f11-f12.
"""
from __future__ import annotations

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from . import figures as F
from .analysis import write
from .build import check, check_states, check_unique, state_crosswalk
from .paths import PROC, RAW

YEAR = 2023
DOWN = 0.10          # headline down payment share
DOWN_ALT = 0.20      # sensitivity
TERM_MONTHS = 360
BURDEN = 0.30        # HUD cost-burden line (convention)
POP_LABOUR = 100_000  # E-100k population floor
INCOME_LEVELS = {"p20": "20th pct", "p40": "40th pct", "median": "Median", "p60": "60th pct", "p80": "80th pct"}
GRAY = "#a3a29d"


# --------------------------------------------------------------------------
# Loaders
# --------------------------------------------------------------------------

def _acs(table: str, level: str) -> pd.DataFrame:
    """ACS 2023 1-year table rows for states ('040') or counties ('050')."""
    d = pd.read_csv(RAW / f"acs/acsdt1y{YEAR}-{table}.dat", sep="|", dtype={"GEO_ID": str})
    pat = r"^0400000US\d{2}$" if level == "state" else r"^0500000US\d{5}$"
    d = d[d.GEO_ID.str.match(pat)].copy()
    d["fips"] = d.GEO_ID.str[-2:] if level == "state" else d.GEO_ID.str[-5:]
    return d


def load_mortgage_rate() -> float:
    """Freddie Mac PMMS 30-year fixed rate, mean of 2023 weekly values (percent)."""
    f = pd.read_excel(RAW / "freddiemac/historicalweeklydata.xlsx", header=None, skiprows=7, usecols=[0, 1],
                      names=["week", "frm30"])
    f["week"] = pd.to_datetime(f.week, errors="coerce")
    f["frm30"] = pd.to_numeric(f.frm30, errors="coerce")
    y = f[(f.week.dt.year == YEAR) & f.frm30.notna()]
    check(len(y) >= 50, f"PMMS: only {len(y)} weeks in {YEAR}")
    rate = float(y.frm30.mean())
    check(5 < rate < 9, f"PMMS {YEAR} mean rate implausible: {rate}")
    return rate


def load_state_costs(cw: pd.DataFrame) -> pd.DataFrame:
    """State income percentiles, median gross rent and effective property-tax rate."""
    q = _acs("b19080", "state").rename(columns={"B19080_E001": "p20", "B19080_E002": "p40",
                                                "B19080_E003": "p60", "B19080_E004": "p80"})
    m = _acs("b19013", "state").rename(columns={"B19013_E001": "median"})
    r = _acs("b25064", "state").rename(columns={"B25064_E001": "rent"})
    t = _acs("b25103", "state").rename(columns={"B25103_E001": "re_tax"})
    v = _acs("b25077", "state").rename(columns={"B25077_E001": "acs_value"})
    d = (q[["fips", "p20", "p40", "p60", "p80"]].merge(m[["fips", "median"]], on="fips", validate="1:1")
         .merge(r[["fips", "rent"]], on="fips", validate="1:1").merge(t[["fips", "re_tax"]], on="fips", validate="1:1")
         .merge(v[["fips", "acs_value"]], on="fips", validate="1:1"))
    d = d.merge(cw[["fips", "st"]], on="fips", how="inner", validate="1:1")
    check_states(d.st, "ACS state costs")
    d["tax_rate"] = d.re_tax / d.acs_value
    check(d.tax_rate.between(0.002, 0.03).all(), "effective property-tax rate outside 0.2%-3%")
    check((d.p20 < d.p40).all() and (d.p40 < d["median"]).all() and (d["median"] < d.p60).all()
          and (d.p60 < d.p80).all(), "income percentiles not increasing")
    return d.drop(columns=["fips", "re_tax", "acs_value"])


def load_county_zhvi(cw: pd.DataFrame) -> pd.DataFrame:
    """County ZHVI 2023 (annual mean, >= 10 of 12 months) with 2020 Census population."""
    z = pd.read_csv(RAW / "zillow/County_zhvi.csv")
    check((z.RegionType == "county").all(), "county ZHVI: non-county rows")
    z["cfips"] = z.StateCodeFIPS.astype(int).map("{:02d}".format) + z.MunicipalCodeFIPS.astype(int).map("{:03d}".format)
    cols = [c for c in z.columns if c.startswith(f"{YEAR}-")]
    check(len(cols) == 12, f"county ZHVI: {len(cols)} monthly columns for {YEAR}")
    z["zhvi_months"] = z[cols].notna().sum(axis=1)
    z["zhvi"] = z[cols].mean(axis=1)
    z = z[z.zhvi_months >= 10][["cfips", "RegionName", "zhvi", "zhvi_months"]]
    check_unique(z, ["cfips"], "county ZHVI")

    u = pd.read_excel(RAW / "census_urban/2020_UA_COUNTY.xlsx", dtype={"STATE": str, "COUNTY": str})
    u["cfips"] = u.STATE + u.COUNTY
    u = u[["cfips", "STATE", "COUNTY_NAME", "POP_COU"]].rename(columns={"STATE": "fips", "POP_COU": "pop2020"})
    u = u.merge(cw[["fips", "st"]], on="fips", how="inner", validate="m:1")
    check_unique(u, ["cfips"], "2020 county population")

    d = u.merge(z, on="cfips", how="left", validate="1:1")
    unmatched = sorted(set(z.cfips) - set(u.cfips) - {c for c in z.cfips if c.startswith("11")})
    check(len(unmatched) <= 5, f"county ZHVI: {len(unmatched)} Zillow counties not in 2020 county file: {unmatched}")
    d.attrs["unmatched_zillow"] = unmatched
    return d


# --------------------------------------------------------------------------
# Entry points
# --------------------------------------------------------------------------

def _weighted_p10(g: pd.DataFrame) -> float:
    g = g.dropna(subset=["zhvi"]).sort_values("zhvi")
    share = g.pop2020.cumsum() / g.pop2020.sum()
    return float(g.zhvi[share >= 0.10].iloc[0])


def entry_points(county: pd.DataFrame, state_zhvi: pd.DataFrame) -> pd.DataFrame:
    rows = []
    county = county.assign(label=county.RegionName.fillna(county.COUNTY_NAME))  # Zillow names separate city/county
    for st, g in county.groupby("st"):
        has = g.dropna(subset=["zhvi"])
        big = has[has.pop2020 >= POP_LABOUR]
        cheapest = has.loc[has.zhvi.idxmin()]
        cheapest_big = big.loc[big.zhvi.idxmin()] if len(big) else None
        rows.append({
            "st": st,
            "n_counties": len(g), "n_counties_zhvi": len(has),
            "zhvi_pop_coverage": has.pop2020.sum() / g.pop2020.sum(),
            "entry_p10": _weighted_p10(g),
            "entry_100k": cheapest_big.zhvi if cheapest_big is not None else np.nan,
            "entry_100k_county": cheapest_big.label if cheapest_big is not None else "",
            "entry_100k_pop2020": cheapest_big.pop2020 if cheapest_big is not None else np.nan,
            "entry_min": cheapest.zhvi, "entry_min_county": cheapest.label,
            "entry_min_pop2020": cheapest.pop2020,
        })
    e = pd.DataFrame(rows).merge(state_zhvi, on="st", validate="1:1")
    check_states(e.st, "entry points")
    check((e.entry_min <= e.entry_p10 + 1e-6).all(), "E-min above E-P10")
    check((e.entry_p10 <= e.zhvi * 1.05).all(), "E-P10 above state ZHVI (+5%)")
    return e


def rent_entry(cw: pd.DataFrame) -> pd.DataFrame:
    """Cheapest ACS county median gross rent among counties of >= 100k (2023 1-year)."""
    r = _acs("b25064", "county")[["fips", "GEO_ID", "B25064_E001"]].rename(columns={"B25064_E001": "rent"})
    p = _acs("b01003", "county")[["fips", "B01003_E001"]].rename(columns={"B01003_E001": "pop2023"})
    d = r.merge(p, on="fips", validate="1:1")
    d["rent"] = pd.to_numeric(d.rent, errors="coerce")
    d["sfips"] = d.fips.str[:2]
    d = d.merge(cw[["fips", "st"]].rename(columns={"fips": "sfips"}), on="sfips", how="inner", validate="m:1")
    d = d[(d.pop2023 >= POP_LABOUR) & d.rent.notna()]
    i = d.groupby("st").rent.idxmin()
    out = d.loc[i, ["st", "rent", "fips", "pop2023"]].rename(
        columns={"rent": "rent_entry_100k", "fips": "rent_entry_cfips", "pop2023": "rent_entry_pop2023"})
    check(out.st.nunique() >= 48, f"rent entry: only {out.st.nunique()} states")
    return out


# --------------------------------------------------------------------------
# Costs
# --------------------------------------------------------------------------

def monthly_owner_cost(price, tax_rate, rate_pct, down=DOWN):
    r = rate_pct / 100 / 12
    loan = np.asarray(price) * (1 - down)
    pi = loan * r / (1 - (1 + r) ** -TERM_MONTHS)
    return pi + np.asarray(price) * np.asarray(tax_rate) / 12


def groups(cs: pd.DataFrame) -> pd.DataFrame:
    g = cs[["st", "sdi", "map_overall"]].copy()
    for v in ["sdi", "map_overall"]:
        g[v + "_third"] = pd.qcut(g[v].rank(method="first"), 3, labels=["low", "mid", "high"]).astype(str)
    g["group"] = np.select([(g.sdi_third == "low") & (g.map_overall_third == "low"),
                            (g.sdi_third == "high") & (g.map_overall_third == "high")],
                           ["origin", "destination"], "other")
    return g


def mover_matrix(st: pd.DataFrame, rate: float) -> pd.DataFrame:
    """Every origin state x destination state x origin income level."""
    o = st[["st"] + list(INCOME_LEVELS)].melt(id_vars="st", var_name="income_level", value_name="origin_income")
    o = o.rename(columns={"st": "origin"})
    dcols = ["st", "zhvi", "entry_p10", "entry_100k", "rent", "rent_entry_100k", "tax_rate", "median"]
    d = st[dcols].rename(columns={"st": "dest", "median": "dest_median_income"})
    m = o.merge(d, how="cross")
    mi = m.origin_income / 12
    for lab, price in [("median", m.zhvi), ("p10", m.entry_p10), ("100k", m.entry_100k)]:
        m[f"pti_{lab}"] = price / m.origin_income
        m[f"owner_share_{lab}"] = monthly_owner_cost(price, m.tax_rate, rate) / mi
        m[f"down_{lab}"] = price * DOWN
    m["owner_share_median_20down"] = monthly_owner_cost(m.zhvi, m.tax_rate, rate, DOWN_ALT) / mi
    m["rent_share_median"] = m.rent * 12 / m.origin_income
    m["rent_share_entry"] = m.rent_entry_100k * 12 / m.origin_income
    m["owner_share_local"] = monthly_owner_cost(m.zhvi, m.tax_rate, rate) / (m.dest_median_income / 12)
    return m


# --------------------------------------------------------------------------
# Figures
# --------------------------------------------------------------------------

def fig_entry_dumbbell(e: pd.DataFrame) -> str:
    F.style()
    d = e.sort_values("zhvi").reset_index(drop=True)
    colour = d.group.map({"destination": F.S1, "origin": F.S2}).fillna(GRAY)
    fig, ax = plt.subplots(figsize=(7.2, 10))
    y = np.arange(len(d))
    ax.hlines(y, d.entry_p10, d.zhvi, color=colour, lw=2, alpha=0.55)
    ax.scatter(d.entry_p10, y, s=34, facecolor=F.SURFACE, edgecolor=colour, linewidth=2, zorder=3,
               label="Entry point (cheapest-county tenth of residents)")
    ax.scatter(d.zhvi, y, s=34, color=colour, edgecolor=F.SURFACE, linewidth=1.2, zorder=3,
               label="State typical value")
    ax.set_yticks(y)
    ax.set_yticklabels(d.st, fontsize=7.5)
    for t, g in zip(ax.get_yticklabels(), d.group):
        t.set_color(F.INK if g != "other" else F.INK2)
        t.set_fontweight("bold" if g != "other" else "normal")
    ax.set_xscale("log")
    ax.xaxis.set_major_locator(matplotlib.ticker.FixedLocator([100e3, 150e3, 200e3, 300e3, 400e3, 600e3, 800e3]))
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    F.dollars(ax, axis="x")
    ax.grid(axis="y", visible=False)
    ax.set_xlabel("Zillow Home Value Index, 2023 (log scale)")
    ax.set_title("Typical home value vs cheapest entry point, by state (2023)")
    handles = [plt.Line2D([], [], marker="o", ls="", color=F.S1, label="High on democracy and LGBTQ equality"),
               plt.Line2D([], [], marker="o", ls="", color=F.S2, label="Low on both"),
               plt.Line2D([], [], marker="o", ls="", color=GRAY, label="Other states"),
               plt.Line2D([], [], marker="o", ls="", color=F.INK2, label="Filled: state typical value"),
               plt.Line2D([], [], marker="o", ls="", mfc=F.SURFACE, mec=F.INK2, mew=2,
                          label="Open: entry point (P10 of county values)")]
    ax.legend(handles=handles, loc="lower right", fontsize=8)
    return F.save(fig, "f11_entry_points")


def fig_cost_heatmap(tab: pd.DataFrame) -> str:
    """Owner cost share for destinations x origin income, at state median and at entry point."""
    F.style()
    levels = list(INCOME_LEVELS.values())
    fig, axes = plt.subplots(1, 2, figsize=(9.5, 5.6), sharey=True)
    cmap = matplotlib.colors.LinearSegmentedColormap.from_list("blue", ["#eef4fc"] + F.BLUE_RAMP)
    for ax, (col, title) in zip(axes, [("owner_share_median", "At the state's typical home value"),
                                       ("owner_share_p10", "At the state's entry point")]):
        w = tab.pivot(index="dest", columns="income_level", values=col)[list(INCOME_LEVELS)]
        w = w.loc[tab.drop_duplicates("dest").sort_values("zhvi").dest]
        ax.imshow(w.values, cmap=cmap, vmin=0, vmax=1.0, aspect="auto")
        for i in range(w.shape[0]):
            for j in range(w.shape[1]):
                v = w.values[i, j]
                ax.text(j, i, f"{v:.0%}", ha="center", va="center", fontsize=8,
                        color=F.SURFACE if v > 0.55 else F.INK, fontweight="bold" if v > BURDEN else "normal")
        ax.set_xticks(range(len(levels)))
        ax.set_xticklabels(levels, fontsize=8)
        ax.set_yticks(range(w.shape[0]))
        ax.set_yticklabels(w.index)
        ax.grid(False)
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Household income in the origin states")
    fig.suptitle("Monthly ownership cost as a share of income, for a household from a low-ranked state (2023)",
                 x=0.01, ha="left", fontweight="bold", fontsize=11)
    fig.text(0.01, -0.04, "Principal, interest and property tax; 10% down, 30-year fixed at the 2023 average rate. "
             "Excludes insurance and maintenance.\nOrigin income = median across the 13 low-ranked states of each "
             "income percentile. Bold = above 30% of gross income.", fontsize=8, color=F.INK2)
    fig.tight_layout()
    return F.save(fig, "f12_mover_cost_share")


# --------------------------------------------------------------------------
# Data dictionary for the processed mover files
# --------------------------------------------------------------------------

_COLS = {
    "st": "State postal code", "group": "origin = bottom third on both SDI and MAP (2023); destination = top third on both; other",
    "origin_group": "group of the origin state", "dest_group": "group of the destination state",
    "n_counties": "Counties (2020 Census county file)", "n_counties_zhvi": "Counties with a 2023 county ZHVI",
    "zhvi_pop_coverage": "Share of 2020 state population in counties with a county ZHVI",
    "entry_p10": "E-P10: population-weighted 10th percentile of 2023 county ZHVI (USD)",
    "entry_100k": "E-100k: lowest 2023 county ZHVI among counties with 2020 population >= 100,000 (USD)",
    "entry_100k_county": "County name for E-100k (Zillow name)", "entry_100k_pop2020": "2020 population of that county",
    "entry_min": "E-min: lowest 2023 county ZHVI in the state (USD)", "entry_min_county": "County name for E-min",
    "entry_min_pop2020": "2020 population of that county", "zhvi": "State ZHVI 2023, annual mean (USD)",
    "p20": "ACS 2023 household income, 20th percentile (B19080 line 1, USD)",
    "p40": "ACS 2023 household income, 40th percentile (B19080 line 2, USD)",
    "median": "ACS 2023 median household income (B19013, USD)",
    "p60": "ACS 2023 household income, 60th percentile (B19080 line 3, USD)",
    "p80": "ACS 2023 household income, 80th percentile (B19080 line 4, USD)",
    "rent": "ACS 2023 median gross rent, state (B25064, USD/month, includes utilities)",
    "tax_rate": "Effective property-tax rate = ACS B25103 median real-estate taxes / B25077 median value",
    "rent_entry_100k": "Lowest ACS 2023 county median gross rent among counties with 2023 population >= 100,000 (USD/month)",
    "rent_entry_cfips": "County FIPS for rent_entry_100k (2023 geography; CT planning regions)",
    "rent_entry_pop2023": "ACS 2023 population of that county", "sdi": "SDI 2.0, 2023", "map_overall": "MAP overall tally, 2023",
    "cfips": "5-digit county FIPS (2020 geography)", "fips": "2-digit state FIPS", "COUNTY_NAME": "Census county name",
    "pop2020": "2020 Census county population", "RegionName": "Zillow county name",
    "zhvi_months": "Months of 2023 with a county ZHVI value (>= 10 required)",
    "origin": "Origin state", "dest": "Destination state", "income_level": "Origin income percentile (p20, p40, median, p60, p80)",
    "origin_income": "Origin-state household income at that level (USD/year)",
    "dest_median_income": "Destination median household income (USD/year)",
    "pti_median": "Destination ZHVI / origin income", "pti_p10": "Destination E-P10 / origin income",
    "pti_100k": "Destination E-100k / origin income",
    "owner_share_median": "Monthly P&I (10% down, 30-yr, 2023 PMMS mean) + property tax at destination ZHVI, / origin monthly income",
    "owner_share_p10": "Same, at destination E-P10", "owner_share_100k": "Same, at destination E-100k",
    "owner_share_median_20down": "Same as owner_share_median with 20% down",
    "down_median": "10% down payment at destination ZHVI (USD)", "down_p10": "10% down payment at E-P10 (USD)",
    "down_100k": "10% down payment at E-100k (USD)",
    "rent_share_median": "Destination state median gross rent x 12 / origin income",
    "rent_share_entry": "Destination rent_entry_100k x 12 / origin income",
    "owner_share_local": "owner_share_median computed on the destination's own median income (local-earner reference)",
}


def write_mover_dictionary(frames: dict) -> None:
    parts = ["# Data dictionary: mover extension files (2023)\n\n",
             "Built by `scripts/06_mover.py`; spec in docs/analysis_plan.md (Mover's-eye extension). "
             "County ZHVI values are derived from Zillow data (attribution required; see STATUS.md).\n"]
    for name, df in frames.items():
        missing = [c for c in df.columns if c not in _COLS]
        check(not missing, f"mover dictionary missing columns {missing}")
        d = pd.DataFrame({"column": df.columns, "description": [_COLS[c] for c in df.columns],
                          "non_missing": [int(df[c].notna().sum()) for c in df.columns]})
        parts.append(f"\n## {name} ({len(df):,} rows)\n\n" + d.to_markdown(index=False) + "\n")
    (PROC / "mover_data_dictionary.md").write_text("".join(parts), encoding="utf-8")


# --------------------------------------------------------------------------
# Run
# --------------------------------------------------------------------------

def run_mover() -> dict:
    cw = state_crosswalk()
    cs = pd.read_csv(PROC / "cross_section_2023.csv")
    rate = load_mortgage_rate()
    g = groups(cs)

    county = load_county_zhvi(cw)
    county.to_csv(PROC / "county_zhvi_2023.csv", index=False, float_format="%.6g")
    e = entry_points(county, cs[["st", "zhvi"]]).merge(g[["st", "group"]], on="st", validate="1:1")
    st = (e.merge(load_state_costs(cw), on="st", validate="1:1")
          .merge(rent_entry(cw), on="st", how="left", validate="1:1")
          .merge(cs[["st", "sdi", "map_overall"]], on="st", validate="1:1"))
    check_states(st.st, "mover state table")
    st.to_csv(PROC / "entry_points_2023.csv", index=False, float_format="%.6g")

    m = mover_matrix(st, rate).merge(g[["st", "group"]].rename(columns={"st": "origin", "group": "origin_group"}),
                                     on="origin").merge(g[["st", "group"]].rename(columns={"st": "dest", "group": "dest_group"}),
                                                        on="dest")
    check(len(m) == 50 * 50 * len(INCOME_LEVELS), "matrix size")
    m.to_csv(PROC / "mover_matrix_2023.csv", index=False, float_format="%.6g")

    origins = sorted(g.st[g.group == "origin"])
    dests = sorted(g.st[g.group == "destination"])

    # t11: entry points, every state
    t11 = st[["st", "group", "zhvi", "entry_p10", "entry_100k", "entry_100k_county", "entry_min", "entry_min_county",
              "entry_min_pop2020", "zhvi_pop_coverage", "rent", "rent_entry_100k"]].copy()
    t11["p10_vs_state"] = t11.entry_p10 / t11.zhvi - 1
    t11 = write(t11.sort_values(["group", "zhvi"], ascending=[True, False]), "t11_entry_points", ".2f")

    # t12: destination costs for a median-income household from the origin group
    oinc = st.loc[st.st.isin(origins), list(INCOME_LEVELS)].median()
    rows = []
    for lev, inc in oinc.items():
        for _, r in st[st.st.isin(dests)].iterrows():
            row = {"dest": r.st, "income_level": lev, "origin_income": inc, "zhvi": r.zhvi, "entry_p10": r.entry_p10,
                   "dest_median_income": r["median"]}
            for lab, price in [("median", r.zhvi), ("p10", r.entry_p10), ("100k", r.entry_100k)]:
                row[f"pti_{lab}"] = price / inc
                row[f"owner_share_{lab}"] = float(monthly_owner_cost(price, r.tax_rate, rate)) / (inc / 12)
            row["owner_share_median_20down"] = float(monthly_owner_cost(r.zhvi, r.tax_rate, rate, DOWN_ALT)) / (inc / 12)
            row["rent_share_median"] = r.rent * 12 / inc
            row["rent_share_entry"] = r.rent_entry_100k * 12 / inc
            row["owner_share_local"] = float(monthly_owner_cost(r.zhvi, r.tax_rate, rate)) / (r["median"] / 12)
            row["down_median"] = r.zhvi * DOWN
            row["down_p10"] = r.entry_p10 * DOWN
            rows.append(row)
    heat = pd.DataFrame(rows)
    t12 = write(heat[heat.income_level == "median"].sort_values("zhvi").drop(columns="income_level"),
                "t12_mover_destinations", ".2f")

    # Same costs at home, for the origin group (reference)
    home = st[st.st.isin(origins)].copy()
    home["owner_share_home"] = monthly_owner_cost(home.zhvi, home.tax_rate, rate) / (home["median"] / 12)
    home["rent_share_home"] = home.rent * 12 / home["median"]
    home = write(home[["st", "median", "zhvi", "rent", "tax_rate", "owner_share_home", "rent_share_home"]]
                 .sort_values("zhvi"), "t12b_origin_home_costs", ".3f")

    # t13: group summary and correlations
    def med(col, sts):
        return float(st.loc[st.st.isin(sts), col].median())
    rows = []
    for col, label in [("zhvi", "Home value: state typical (ZHVI)"), ("entry_p10", "Home value: entry point E-P10"),
                       ("entry_100k", "Home value: cheapest county >= 100k (E-100k)"),
                       ("entry_min", "Home value: cheapest county (E-min)"),
                       ("rent", "Median gross rent: state"), ("rent_entry_100k", "Median gross rent: cheapest county >= 100k")]:
        ok = st[col].notna() & (st[col] > 0)
        rows.append({"measure": label, "origin_median": med(col, origins), "destination_median": med(col, dests),
                     "ratio": med(col, dests) / med(col, origins),
                     "r_log_with_sdi": np.corrcoef(np.log(st.loc[ok, col]), st.loc[ok, "sdi"])[0, 1],
                     "r_log_with_map": np.corrcoef(np.log(st.loc[ok, col]), st.loc[ok, "map_overall"])[0, 1],
                     "n": int(ok.sum())})
    t13 = write(pd.DataFrame(rows), "t13_entry_summary", ".3f")

    # t14: how many destinations are under 30% for each origin income level
    rows = []
    for lev in INCOME_LEVELS:
        h = heat[heat.income_level == lev]
        rows.append({"origin_income_level": INCOME_LEVELS[lev], "origin_income": oinc[lev],
                     "owner_under30_median": int((h.owner_share_median <= BURDEN).sum()),
                     "owner_under30_p10": int((h.owner_share_p10 <= BURDEN).sum()),
                     "owner_under30_20down": int((h.owner_share_median_20down <= BURDEN).sum()),
                     "rent_under30_median": int((h.rent_share_median <= BURDEN).sum()),
                     "rent_under30_entry": int((h.rent_share_entry <= BURDEN).sum()),
                     "n_destinations": len(h)})
    t14 = write(pd.DataFrame(rows), "t14_destinations_under_30pct", ".0f")

    write_mover_dictionary({"entry_points_2023.csv": st, "county_zhvi_2023.csv": county,
                            "mover_matrix_2023.csv": m})
    figs = [fig_entry_dumbbell(st), fig_cost_heatmap(heat)]
    return {"rate": rate, "origins": origins, "destinations": dests, "origin_income": oinc, "state": st,
            "county": county, "matrix": m, "t11": t11, "t12": t12, "t13": t13, "t14": t14, "home": home,
            "figures": figs}
