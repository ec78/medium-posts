"""Data dictionary for data/processed/state_year_panel.csv."""
from __future__ import annotations

import pandas as pd

# column: (description, units / scale, source, years available)
DICTIONARY = {
    "st": ("USPS state code (key)", "text", "SDI 2.0", "all"),
    "year": ("Calendar year (key)", "year", "-", "2000-2024"),
    "state": ("State name", "text", "SDI 2.0", "all"),
    "fips": ("State FIPS code", "2-digit text", "Census 2020 centres of population", "all"),
    "region": ("Census region (4)", "category", "Census Bureau definition", "all"),
    "lat": ("Latitude of 2020 population-weighted centre", "degrees", "Census CenPop2020", "all"),
    "lon": ("Longitude of 2020 population-weighted centre", "degrees", "Census CenPop2020", "all"),
    "sdi": ("SDI 2.0 electoral democracy score (democracy_mcmc), posterior mean", "latent scale, pooled mean 0, SD 1; higher = more democratic", "Grumbach & Bitton 2024", "2000-2023"),
    "sdi_sd": ("Posterior SD of sdi", "same as sdi", "SDI 2.0", "2000-2023"),
    "sdi_se": ("Naive MCMC standard error of the posterior mean (not sampling uncertainty)", "same as sdi", "SDI 2.0", "2000-2023"),
    "sdi_additive": ("SDI 2.0 additive index (democracy_additive)", "standardised; higher = more democratic", "SDI 2.0", "2000-2023"),
    "eds": ("Rhodes Electoral Democracy Score, posterior mean", "latent scale; higher = more democratic", "Rhodes 2025 replication (Dataverse, CC0)", "2000, 2004, 2008, 2012, 2016, 2020, 2022"),
    "eds_sd": ("Posterior SD of eds", "same as eds", "Rhodes 2025", "as eds"),
    "covi": ("Cost of Voting Index, FinalCOVI", "index; higher = costlier to vote", "costofvotingindex.com", "1996-2024 even election years (2000-2024 here)"),
    "party_control": ("State party control: 1 Democratic trifecta, 0.5 divided, 0 Republican trifecta", "category", "Rhodes 2025 replication (dem-control)", "2000-2022; Nebraska missing"),
    "dem_trifecta": ("1 if party_control == 1", "0/1", "derived", "2000-2022"),
    "rep_trifecta": ("1 if party_control == 0", "0/1", "derived", "2000-2022"),
    "zhvi": ("Zillow Home Value Index, all homes (SFR + condo), 35th-65th percentile tier, smoothed, seasonally adjusted; calendar-year mean of monthly values (>=10 months)", "current dollars", "Zillow Research", "2000-2024 (gaps before 2009)"),
    "zhvi_months": ("Number of monthly ZHVI values averaged", "count", "derived", "as zhvi"),
    "zhvi_real": ("zhvi deflated by national PCE price index", "2023 dollars", "derived", "as zhvi"),
    "log_zhvi": ("ln(zhvi)", "log dollars", "derived", "as zhvi"),
    "log_zhvi_real": ("ln(zhvi_real)", "log 2023 dollars", "derived", "as zhvi"),
    "fhfa_hpi": ("FHFA all-transactions HPI, annual mean of quarters; within-state appreciation only", "index, 1980Q1 = 100 per state", "FHFA", "2000-2024"),
    "acs_value": ("ACS 1-year median value, owner-occupied housing units (B25077), self-reported", "current dollars", "Census ACS summary file", "2022, 2023"),
    "acs_value_moe": ("90% margin of error of acs_value", "dollars", "Census ACS", "2022, 2023"),
    "hh_income": ("ACS 1-year median household income (B19013)", "current dollars", "Census ACS", "2022, 2023"),
    "ba_share": ("Share of adults 25+ with bachelor's degree or higher (B15003 lines 22-25 / line 1)", "proportion", "Census ACS", "2022, 2023"),
    "acs_pop": ("ACS total population (B01003)", "persons", "Census ACS", "2022, 2023"),
    "urban_share": ("2020 Census urban population share (time-invariant)", "proportion", "Census 2020 urban areas county file", "constant"),
    "rpp_all": ("BEA Regional Price Parity, all items", "U.S. = 100 in each year", "BEA SARPP", "2008-2024"),
    "rpp_goods": ("RPP, goods", "U.S. = 100", "BEA SARPP", "2008-2024"),
    "rpp_housing": ("RPP, services: housing (tenant rents; applied to owners too)", "U.S. = 100", "BEA SARPP", "2008-2024"),
    "rpp_utilities": ("RPP, services: utilities", "U.S. = 100", "BEA SARPP", "2008-2024"),
    "rpp_other_services": ("RPP, services: other (excl. rents and utilities)", "U.S. = 100", "BEA SARPP", "2008-2024"),
    "irpd": ("Implicit regional price deflator = RPP x U.S. PCE price index / 100", "2017 = 100", "BEA SAIRPD", "2008-2024"),
    "real_pcpi_rpp": ("Real per-capita personal income = personal income / (RPP x U.S. PCE price index) / population; purchasing-power measure", "constant 2017 dollars", "BEA SARPI line 2", "2008-2024"),
    "population": ("Midyear population", "persons", "BEA SAINC1 line 2", "2000-2024"),
    "pcpi": ("Per-capita personal income", "current dollars", "BEA SAINC1 line 3", "2000-2024"),
    "pcpi_real": ("pcpi deflated by national PCE price index (no regional adjustment)", "2023 dollars", "derived", "2000-2024"),
    "log_pcpi_real": ("ln(pcpi_real)", "log", "derived", "2000-2024"),
    "pce_pi": ("U.S. PCE chain-type price index (NIPA DPCERG)", "2017 = 100", "BEA NIPA", "2000-2024"),
    "price_to_income": ("Affordability proxy: zhvi / hh_income", "ratio", "derived", "2022, 2023"),
    "price_to_pcpi": ("zhvi / pcpi (per-capita, not household, income; different concept)", "ratio", "derived", "2000-2024"),
    "map_so": ("MAP sexual-orientation policy tally", "points (can be negative)", "MAP via Internet Archive", "2017-2024 snapshots"),
    "map_gi": ("MAP gender-identity policy tally", "points (can be negative)", "MAP via Internet Archive", "2017-2024"),
    "map_overall": ("MAP overall LGBTQ policy tally = map_so + map_gi", "points (can be negative)", "MAP via Internet Archive", "2017-2024"),
    "map_max_positive": ("Sum of positive category maxima shown on the snapshot (scoring-system size)", "points", "derived from MAP page", "2017-2024"),
    "map_pct_max": ("map_overall / map_max_positive", "proportion", "derived", "2017-2024"),
    "map_asof": ("MAP page 'current as of' date", "date", "MAP", "2017-2024"),
    "map_snapshot": ("Internet Archive capture date (YYYYMMDD)", "text", "archive.org", "2017-2024"),
    "hrc_category": ("HRC State Equality Index 2023 category (released 2024-01-30)", "ordered category, 4 levels", "HRC press release", "2023 only"),
    "hrc_rank": ("Order of hrc_category, 1 = High Priority ... 4 = Working Toward Innovative Equality; ordinal only, not equally spaced", "1-4", "derived", "2023 only"),
}


def write_dictionary(panel: pd.DataFrame, path_csv, path_md) -> pd.DataFrame:
    rows = []
    for c in panel.columns:
        if c.startswith("log_rpp") or c == "log_real_pcpi_rpp":
            base = c[4:]
            desc = (f"ln({base})", "log", "derived", DICTIONARY[base][3])
        else:
            if c not in DICTIONARY:
                raise KeyError(f"data dictionary missing column {c}")
            desc = DICTIONARY[c]
        rows.append({"column": c, "description": desc[0], "units": desc[1], "source": desc[2],
                     "years": desc[3], "non_missing": int(panel[c].notna().sum()),
                     "dtype": str(panel[c].dtype)})
    d = pd.DataFrame(rows)
    d.to_csv(path_csv, index=False)
    path_md.write_text("# Data dictionary: state_year_panel.csv\n\n50 states x 2000-2024 (1,250 rows). "
                       "Key: (st, year). Missing values mean the source has no value; nothing is interpolated.\n\n"
                       + d.to_markdown(index=False), encoding="utf-8")
    return d
