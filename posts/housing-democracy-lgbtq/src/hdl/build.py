"""Load, clean, validate and merge the raw sources into a state-year panel.

Every loader returns a tidy frame keyed by (`st`, `year`) or by `st`, where
`st` is the USPS two-letter state code. The 50 states are the universe; D.C.
and territories are dropped where present, and the dropped rows are logged.

Validation is done with explicit `check_*` helpers that raise on failure, so
a silent upstream change (renamed column, new geography, duplicated rows)
stops the build instead of quietly altering results.
"""
from __future__ import annotations

import html
import re
from pathlib import Path

import numpy as np
import pandas as pd

from .paths import RAW

# --------------------------------------------------------------------------
# State identifiers
# --------------------------------------------------------------------------

# Census regions (4). Source: Census Bureau, "Census Regions and Divisions of
# the United States". Counts are validated below (9/12/16/13).
CENSUS_REGION = {
    "Northeast": "CT ME MA NH RI VT NJ NY PA",
    "Midwest": "IL IN MI OH WI IA KS MN MO NE ND SD",
    "South": "DE FL GA MD NC SC VA WV AL KY MS TN AR LA OK TX",
    "West": "AZ CO ID MT NV NM UT WY AK CA HI OR WA",
}
REGION_OF = {st: reg for reg, sts in CENSUS_REGION.items() for st in sts.split()}


class ValidationError(RuntimeError):
    pass


def check(cond: bool, msg: str) -> None:
    if not cond:
        raise ValidationError(msg)


def check_unique(df: pd.DataFrame, keys: list[str], name: str) -> None:
    dup = df.duplicated(keys, keep=False)
    check(not dup.any(), f"{name}: duplicate keys {keys}:\n{df.loc[dup, keys].head()}")


def check_states(states, name: str, expected: int = 50) -> None:
    s = set(states)
    check(len(s) == expected, f"{name}: expected {expected} states, found {len(s)}")
    check(s <= set(REGION_OF), f"{name}: unknown state codes {sorted(s - set(REGION_OF))}")


def state_crosswalk() -> pd.DataFrame:
    """USPS code, name and FIPS for the 50 states.

    Names and codes come from SDI 2.0; FIPS and population-weighted centres
    from the Census 2020 centres-of-population file. The two are joined on
    name, and the join is required to be complete.
    """
    sdi = pd.read_csv(RAW / "sdi/SDI_2.0.csv")[["st", "state"]].drop_duplicates()
    cen = pd.read_csv(RAW / "census_urban/CenPop2020_Mean_ST.txt", dtype={"STATEFP": str},
                      encoding="utf-8-sig")
    cen = cen.rename(columns={"STATEFP": "fips", "STNAME": "state", "LATITUDE": "lat",
                              "LONGITUDE": "lon", "POPULATION": "pop2020"})
    cw = sdi.merge(cen[["fips", "state", "lat", "lon"]], on="state", how="left", validate="1:1")
    check(cw.fips.notna().all(), f"crosswalk: unmatched names {cw[cw.fips.isna()].state.tolist()}")
    cw["region"] = cw.st.map(REGION_OF)
    check_states(cw.st, "crosswalk")
    counts = cw.region.value_counts().to_dict()
    check(counts == {"South": 16, "West": 13, "Midwest": 12, "Northeast": 9},
          f"crosswalk: unexpected region counts {counts}")
    return cw.sort_values("st").reset_index(drop=True)


# --------------------------------------------------------------------------
# Electoral democracy and voting access
# --------------------------------------------------------------------------

def load_sdi() -> pd.DataFrame:
    d = pd.read_csv(RAW / "sdi/SDI_2.0.csv")
    expected = {"st", "state", "year", "democracy_mcmc", "democracy_mcmc_sd",
                "democracy_mcmc_se", "democracy_additive"}
    check(expected <= set(d.columns), f"SDI: columns changed: {d.columns.tolist()}")
    check_unique(d, ["st", "year"], "SDI")
    check(d.year.between(2000, 2023).all() and d.year.nunique() == 24, "SDI: year range changed")
    check(d.groupby("year").st.nunique().eq(50).all(), "SDI: not 50 states every year")
    check(d[list(expected - {"st", "state"})].notna().all().all(), "SDI: missing values")
    return d.rename(columns={"democracy_mcmc": "sdi", "democracy_mcmc_sd": "sdi_sd",
                             "democracy_mcmc_se": "sdi_se", "democracy_additive": "sdi_additive"}
                    ).drop(columns="state")


def load_rhodes() -> pd.DataFrame:
    d = pd.read_csv(RAW / "rhodes/democracy_dataset.csv")
    d = d.rename(columns={"State": "st", "Year": "year", "democracy_mcmc": "eds",
                          "democracy_mcmc_sd": "eds_sd"})[["st", "year", "eds", "eds_sd"]]
    check_unique(d, ["st", "year"], "Rhodes EDS")
    check(sorted(d.year.unique()) == [2000, 2004, 2008, 2012, 2016, 2020, 2022], "Rhodes: years changed")
    check_states(d.st, "Rhodes EDS")
    return d


def load_covi() -> pd.DataFrame:
    d = pd.read_excel(RAW / "covi/COVI_Values_1996-2024.xlsx")
    d = d.rename(columns={"state": "st", "FinalCOVI": "covi"})[["st", "year", "covi"]]
    check_unique(d, ["st", "year"], "COVI")
    check_states(d.st, "COVI")
    return d


def load_party_control() -> pd.DataFrame:
    """Ranney-style party control from Rhodes (2025) replication data:
    1 = Democratic trifecta, 0 = Republican trifecta, 0.5 = divided.
    Nebraska (nonpartisan legislature) is missing by construction."""
    d = pd.read_csv(RAW / "rhodes/dem-control.tab", sep="\t")
    d = d.rename(columns={"State": "st", "Year": "year", "ranney4_control": "party_control"})
    d = d[d.st != "DC"][["st", "year", "party_control"]]
    check_unique(d, ["st", "year"], "party control")
    check(set(d.party_control.dropna().unique()) <= {0, 0.5, 1}, "party control: unexpected codes")
    return d


# --------------------------------------------------------------------------
# Housing
# --------------------------------------------------------------------------

def load_zhvi(cw: pd.DataFrame) -> pd.DataFrame:
    """Zillow Home Value Index (all homes, middle tier 35th-65th pct, smoothed,
    seasonally adjusted, monthly). Annual value = mean of the available monthly
    values in the calendar year, kept only if at least 10 of 12 months are
    present (`zhvi_months` records the count). Zillow's state series have
    gaps (e.g. North Dakota before 2009); these are left missing, not filled."""
    z = pd.read_csv(RAW / "zillow/State_zhvi.csv")
    check({"RegionName", "RegionType"} <= set(z.columns), "ZHVI: columns changed")
    check((z.RegionType == "state").all(), "ZHVI: non-state rows")
    dropped = sorted(set(z.RegionName) - set(cw.state))
    check(dropped == ["District of Columbia"], f"ZHVI: unexpected extra regions {dropped}")
    z = z[z.RegionName.isin(cw.state)]
    long = z.melt(id_vars=["RegionName"], value_vars=[c for c in z.columns if re.match(r"\d{4}-\d{2}-\d{2}", c)],
                  var_name="date", value_name="zhvi")
    long["year"] = long.date.str[:4].astype(int)
    agg = long.groupby(["RegionName", "year"]).zhvi.agg(["mean", "count"]).reset_index()
    agg = agg[agg["count"] >= 10].rename(columns={"mean": "zhvi", "RegionName": "state", "count": "zhvi_months"})
    out = agg.merge(cw[["st", "state"]], on="state", validate="m:1").drop(columns=["state"])
    check_unique(out, ["st", "year"], "ZHVI")
    check_states(out[out.year == 2023].st, "ZHVI 2023")
    return out


def load_fhfa() -> pd.DataFrame:
    """FHFA all-transactions state HPI (quarterly, not seasonally adjusted,
    1980Q1 = 100). Annual value = mean of the 4 quarters. Index levels are
    only comparable within a state over time."""
    f = pd.read_csv(RAW / "fhfa/HPI_AT_state.csv", header=None, names=["st", "year", "qtr", "hpi"])
    f = f[f.st.isin(REGION_OF)]
    g = f.groupby(["st", "year"]).hpi.agg(["mean", "count"]).reset_index()
    g = g[g["count"] == 4].rename(columns={"mean": "fhfa_hpi"}).drop(columns="count")
    check_unique(g, ["st", "year"], "FHFA")
    return g


def _acs_table(year: int, table: str) -> pd.DataFrame:
    d = pd.read_csv(RAW / f"acs/acsdt1y{year}-{table}.dat", sep="|", dtype={"GEO_ID": str})
    d = d[d.GEO_ID.str.match(r"^0400000US\d{2}$")].copy()
    d["fips"] = d.GEO_ID.str[-2:]
    return d


def load_acs(cw: pd.DataFrame, year: int) -> pd.DataFrame:
    """ACS 1-year state estimates: median owner-occupied home value (B25077,
    self-reported), median household income (B19013), bachelor's-or-higher
    share of adults 25+ (B15003 lines 22-25 / line 1), population (B01003)."""
    v = _acs_table(year, "b25077")[["fips", "B25077_E001", "B25077_M001"]]
    i = _acs_table(year, "b19013")[["fips", "B19013_E001"]]
    e = _acs_table(year, "b15003")
    e["ba_share"] = e[[f"B15003_E0{k}" for k in (22, 23, 24, 25)]].sum(axis=1) / e["B15003_E001"]
    p = _acs_table(year, "b01003")[["fips", "B01003_E001"]]
    d = v.merge(i, on="fips").merge(e[["fips", "ba_share"]], on="fips").merge(p, on="fips")
    d = d.rename(columns={"B25077_E001": "acs_value", "B25077_M001": "acs_value_moe",
                          "B19013_E001": "hh_income", "B01003_E001": "acs_pop"})
    d = d.merge(cw[["fips", "st"]], on="fips", how="inner", validate="1:1").drop(columns="fips")
    d["year"] = year
    check_states(d.st, f"ACS {year}")
    check(d[["acs_value", "hh_income", "ba_share"]].gt(0).all().all(), f"ACS {year}: non-positive values")
    check(d.ba_share.between(0.15, 0.65).all(), f"ACS {year}: implausible BA share")
    return d


def load_urban(cw: pd.DataFrame) -> pd.DataFrame:
    """2020 Census urban population share, aggregated from the county file."""
    u = pd.read_excel(RAW / "census_urban/2020_UA_COUNTY.xlsx", dtype={"STATE": str})
    g = u.groupby("STATE")[["POP_COU", "POP_URB"]].sum().reset_index()
    g["urban_share"] = g.POP_URB / g.POP_COU
    d = cw[["fips", "st"]].merge(g.rename(columns={"STATE": "fips"}), on="fips", how="left", validate="1:1")
    check(d.urban_share.notna().all(), "urban: missing states")
    return d[["st", "urban_share"]]


# --------------------------------------------------------------------------
# BEA prices and income
# --------------------------------------------------------------------------

def _bea_wide(path: Path, cw: pd.DataFrame) -> pd.DataFrame:
    d = pd.read_csv(path, dtype={"GeoFIPS": str}, encoding="latin-1")
    d = d[d.GeoFIPS.notna() & d.LineCode.notna()].copy()
    d["fips"] = d.GeoFIPS.str.strip().str.strip('"').str[:2]
    d = d[d.GeoFIPS.str.strip().str.strip('"').str.endswith("000")]
    years = [c for c in d.columns if re.fullmatch(r"\d{4}", c)]
    long = d.melt(id_vars=["fips", "LineCode", "Description"], value_vars=years,
                  var_name="year", value_name="value")
    long["year"] = long.year.astype(int)
    long["value"] = pd.to_numeric(long.value, errors="coerce")
    return long.merge(cw[["fips", "st"]], on="fips", how="inner")


def load_rpp(cw: pd.DataFrame) -> pd.DataFrame:
    """BEA Regional Price Parities by state (SARPP; U.S. = 100 each year).
    Lines: 1 all items, 2 goods, 3 services: housing (tenant rents),
    4 services: utilities, 5 services: other."""
    names = {1: "rpp_all", 2: "rpp_goods", 3: "rpp_housing", 4: "rpp_utilities", 5: "rpp_other_services"}
    d = _bea_wide(RAW / "bea/sarpp/SARPP_STATE_2008_2024.csv", cw)
    d = d[d.LineCode.isin(names)]
    w = d.pivot_table(index=["st", "year"], columns="LineCode", values="value").rename(columns=names)
    w.columns.name = None
    w = w.reset_index()
    check_unique(w, ["st", "year"], "RPP")
    check(w[list(names.values())].notna().all().all(), "RPP: missing values")
    check(sorted(w.year.unique()) == list(range(2008, 2025)), "RPP: years changed")
    return w


def load_irpd(cw: pd.DataFrame) -> pd.DataFrame:
    d = _bea_wide(RAW / "bea/sarpp/SAIRPD_STATE_2008_2024.csv", cw)
    return d[d.LineCode == 1][["st", "year", "value"]].rename(columns={"value": "irpd"})


def load_real_income(cw: pd.DataFrame) -> pd.DataFrame:
    """SARPI line 2: real per-capita personal income, constant 2017 dollars,
    = personal income / (RPP x U.S. PCE price index) / population."""
    d = _bea_wide(RAW / "bea/sarpp/SARPI_STATE_2008_2024.csv", cw)
    return d[d.LineCode == 2][["st", "year", "value"]].rename(columns={"value": "real_pcpi_rpp"})


def load_sainc1(cw: pd.DataFrame) -> pd.DataFrame:
    """SAINC1: line 2 population, line 3 per-capita personal income (current $)."""
    d = _bea_wide(RAW / "bea/sainc/SAINC1__ALL_AREAS_1929_2025.csv", cw)
    d = d[d.LineCode.isin([2, 3]) & d.year.between(1999, 2025)]
    w = d.pivot_table(index=["st", "year"], columns="LineCode", values="value").rename(
        columns={2: "population", 3: "pcpi"})
    w.columns.name = None
    return w.reset_index()


def load_pce_price_index() -> pd.DataFrame:
    """National PCE chain-type price index (NIPA series DPCERG, 2017 = 100),
    annual, from BEA's NIPA flat file."""
    d = pd.read_csv(RAW / "bea/NipaDataA.txt", dtype=str)
    d.columns = ["series", "year", "value"]
    d = d[d.series == "DPCERG"].copy()
    d["year"] = d.year.astype(int)
    d["pce_pi"] = d.value.str.replace(",", "").astype(float)
    d = d[d.year >= 1999][["year", "pce_pi"]]
    check(d.year.is_unique and {2000, 2023} <= set(d.year), "PCE price index: years missing")
    return d


# --------------------------------------------------------------------------
# LGBTQ legal equality
# --------------------------------------------------------------------------

def _cells(row_html: str) -> list[str]:
    return [html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
            for c in re.findall(r"<td[^>]*>(.*?)</td>", row_html, flags=re.S)]


def parse_map_snapshot(path: Path) -> pd.DataFrame:
    """Parse one archived MAP 'Equality Maps' page into state rows with the
    sexual-orientation, gender-identity and overall policy tallies, the
    page's 'current as of' date, and the maximum attainable positive points
    implied by the category denominators."""
    t = path.read_text(encoding="utf-8", errors="replace")
    rows = re.findall(r'profile_state/([A-Z]{2})">[^<]+</a>\s*</td>(.*?)</tr>\s*<tr[^>]*>(.*?)</tr>', t, flags=re.S)
    if not rows:
        return pd.DataFrame()
    m = re.search(r"current as of\s*(\d{2}/\d{2}/\d{4})", t, flags=re.I)
    asof = pd.to_datetime(m.group(1), format="%m/%d/%Y") if m else pd.NaT
    out = []
    for st, so_html, gi_html in rows:
        so, gi = _cells(so_html), _cells(gi_html)
        so_tot, gi_tot, overall = (float(x) for x in so[-3:])

        def max_pos(cells):
            tot = 0.0
            for c in cells:
                if "/" in c:
                    mx = float(c.split("/")[1])
                    tot += max(mx, 0.0)
            return tot
        out.append({"st": st, "map_so": so_tot, "map_gi": gi_tot, "map_overall": overall,
                    "map_max_positive": max_pos(so[1:-3]) + max_pos(gi[1:]), "map_asof": asof})
    d = pd.DataFrame(out)
    # sanity: overall = SO + GI on every row
    check(np.allclose(d.map_so + d.map_gi, d.map_overall, atol=0.011),
          f"MAP {path.name}: overall != SO + GI")
    return d


def load_map() -> pd.DataFrame:
    frames = []
    for p in sorted((RAW / "map").glob("wb_*_equality_maps.html")):
        d = parse_map_snapshot(p)
        if d.empty:
            continue
        d["map_snapshot"] = p.name[3:11]
        frames.append(d)
    d = pd.concat(frames, ignore_index=True)
    d = d[d.st.isin(REGION_OF)].copy()
    d["year"] = d.map_asof.dt.year
    check_unique(d, ["st", "year"], "MAP")
    for y, g in d.groupby("year"):
        check_states(g.st, f"MAP {y}")
    d["map_pct_max"] = d.map_overall / d.map_max_positive
    return d


HRC_CATEGORIES = [
    "High Priority to Achieve Basic Equality",
    "Building Equality",
    "Solidifying Equality",
    "Working Toward Innovative Equality",
]


def load_hrc_2023(cw: pd.DataFrame) -> pd.DataFrame:
    """HRC 2023 State Equality Index categories, parsed from the HRC press
    release of 2024-01-30 (category lists are given there for all states)."""
    t = (RAW / "hrc/sei2023_press_release.html").read_text(encoding="utf-8", errors="replace")
    t = re.sub(r"<script.*?</script>|<style.*?</style>", "", t, flags=re.S)
    t = html.unescape(re.sub(r"<[^>]+>", "\n", t))
    t = re.sub(r"\s+", " ", t)
    name_to_st = dict(zip(cw.state, cw.st))
    rows = []
    for cat in HRC_CATEGORIES:
        m = re.search(re.escape(cat) + r".{0,120}?:\s*(.*?)(?:Five states|Two in|Twenty-Three|The State Equality Index tells)",
                      t, flags=re.S)
        check(m is not None, f"HRC: category not found: {cat}")
        names = [n.strip() for n in m.group(1).split(",")]
        for n in names:
            if n == "District of Columbia":
                continue
            check(n in name_to_st, f"HRC: unknown state name {n!r}")
            rows.append({"st": name_to_st[n], "hrc_category": cat})
    d = pd.DataFrame(rows)
    check_unique(d, ["st"], "HRC 2023")
    check_states(d.st, "HRC 2023")
    counts = d.hrc_category.value_counts().to_dict()
    check(counts == {"High Priority to Achieve Basic Equality": 23, "Working Toward Innovative Equality": 20,
                     "Solidifying Equality": 5, "Building Equality": 2}, f"HRC: counts {counts}")
    d["hrc_rank"] = d.hrc_category.map({c: i for i, c in enumerate(HRC_CATEGORIES, start=1)})
    d["year"] = 2023
    return d


# --------------------------------------------------------------------------
# Merge
# --------------------------------------------------------------------------

def build_panel() -> tuple[pd.DataFrame, list[dict]]:
    """Return the state-year panel (50 states x 2000-2024) and a merge log."""
    cw = state_crosswalk()
    log: list[dict] = []
    base = pd.MultiIndex.from_product([cw.st, range(2000, 2025)], names=["st", "year"]).to_frame(index=False)
    base = base.merge(cw[["st", "state", "fips", "region", "lat", "lon"]], on="st", validate="m:1")

    pieces = {
        "sdi": load_sdi(),
        "rhodes": load_rhodes(),
        "covi": load_covi(),
        "party": load_party_control(),
        "zhvi": load_zhvi(cw),
        "fhfa": load_fhfa(),
        "acs": pd.concat([load_acs(cw, 2022), load_acs(cw, 2023)]),
        "rpp": load_rpp(cw),
        "irpd": load_irpd(cw),
        "real_income": load_real_income(cw),
        "sainc1": load_sainc1(cw),
        "map": load_map(),
        "hrc": load_hrc_2023(cw),
    }
    panel = base
    for name, df in pieces.items():
        check_unique(df, ["st", "year"], name)
        before = len(panel)
        keys = df[["st", "year"]]
        in_window = keys[keys.year.between(2000, 2024)]
        matched = in_window.merge(base[["st", "year"]], how="inner").shape[0]
        panel = panel.merge(df, on=["st", "year"], how="left", validate="1:1")
        check(len(panel) == before, f"merge {name}: row count changed")
        log.append({"source": name, "rows_in_source": len(df), "rows_in_2000_2024": len(in_window),
                    "rows_matched": matched, "unmatched_in_window": len(in_window) - matched,
                    "years": f"{df.year.min()}-{df.year.max()}"})
        check(len(in_window) == matched, f"merge {name}: {len(in_window) - matched} unmatched rows")

    panel = panel.merge(load_urban(cw), on="st", validate="m:1")
    panel = panel.merge(load_pce_price_index(), on="year", how="left", validate="m:1")

    # Derived variables -----------------------------------------------------
    p23 = panel.loc[panel.year == 2023, "pce_pi"].iloc[0]
    panel["zhvi_real"] = panel.zhvi * p23 / panel.pce_pi           # 2023 dollars
    panel["pcpi_real"] = panel.pcpi * p23 / panel.pce_pi           # 2023 dollars, national deflator
    panel["log_zhvi"] = np.log(panel.zhvi)
    panel["log_zhvi_real"] = np.log(panel.zhvi_real)
    panel["log_pcpi_real"] = np.log(panel.pcpi_real)
    panel["price_to_income"] = panel.zhvi / panel.hh_income         # ACS years only
    panel["price_to_pcpi"] = panel.zhvi / panel.pcpi                # all years (different concept)
    for c in ["rpp_all", "rpp_goods", "rpp_housing", "rpp_utilities", "rpp_other_services", "real_pcpi_rpp"]:
        panel[f"log_{c}"] = np.log(panel[c])
    panel["dem_trifecta"] = (panel.party_control == 1).astype(float).where(panel.party_control.notna())
    panel["rep_trifecta"] = (panel.party_control == 0).astype(float).where(panel.party_control.notna())

    # Consistency checks on derived values ---------------------------------
    check(panel.loc[panel.year.between(2000, 2023), "sdi"].notna().all(), "SDI missing in 2000-2023")
    check(panel.loc[panel.year == 2024, "sdi"].isna().all(), "SDI should be missing in 2024 (no interpolation)")
    check(panel.loc[panel.year.between(2009, 2024), "zhvi"].notna().all(), "ZHVI missing after 2008")
    check(panel.loc[panel.year == 2023, ["acs_value", "hh_income", "map_overall", "hrc_category",
                                         "rpp_all"]].notna().all().all(), "2023 cross-section incomplete")
    # IRPD should equal RPP x national PCE price index / 100 (BEA identity), using BEA's own vintage
    sub = panel.dropna(subset=["irpd", "rpp_all"])
    us_pi = (sub.irpd * 100 / sub.rpp_all).groupby(sub.year).agg(["min", "max"])
    check(((us_pi["max"] - us_pi["min"]) < 0.01).all(), "IRPD != RPP x PCE price index")
    # ACS income vs BEA per-capita income should be strongly related
    c23 = panel[panel.year == 2023]
    check(np.corrcoef(np.log(c23.hh_income), np.log(c23.pcpi))[0, 1] > 0.8, "ACS vs BEA income mismatch")
    # ZHVI vs ACS median value should be strongly related in levels
    check(np.corrcoef(np.log(c23.zhvi), np.log(c23.acs_value))[0, 1] > 0.9, "ZHVI vs ACS value mismatch")
    return panel.sort_values(["st", "year"]).reset_index(drop=True), log
