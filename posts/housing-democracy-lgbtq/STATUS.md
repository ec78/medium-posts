# Project status

Last updated: 2026-11-16.

**Published** as [Moving for Your Rights Has a Price Tag](https://medium.com/@eclow/moving-for-your-rights-has-a-price-tag-00673cf91d7f) on 2026-11-16. The post uses figures f01b, f13 and f11.

## Done

* Data feasibility check and inventory ([docs/data_inventory.md](docs/data_inventory.md)).
* Literature search, evidence table, synthesis, search log and bibliography ([literature/](literature/)).
* Pre-specified analysis plan with post hoc changes logged ([docs/analysis_plan.md](docs/analysis_plan.md)).
* Download, clean, merge and validate pipeline; analysis; figures; executed notebook; research memo.
* Mover's-eye extension (2026-11-14): affordability matrix and county entry points (memo section 6; `scripts/06_mover.py`).
* Post-ready figures (2026-11-15): single-panel f01b and simplified mover chart f13; every figure carries a source line.
* Medium post published 2026-11-16.

## Unresolved data issues

| # | Issue | Effect | What would resolve it |
|---|---|---|---|
| 1 | **MAP historical data:** only mid-year archived snapshots (2017-2024) were available. The scoring maxima change in most years, and no per-policy panel was built. | No within-state equality analysis; MAP used cross-sectionally plus rank patterns only. | Download ICPSR 37877 (2010 and 2020 on a consistent indicator set; needs your ICPSR login), or scrape per-policy state profile pages from the archive. |
| 2 | **MAP 2023 timing:** the snapshot is current as of 2023-06-28, so laws effective later in 2023 are not reflected. | Slight timing mismatch with calendar-year SDI. | Use a capture near 2023-12-31 if one exists (not checked). |
| 3 | **HRC:** only 2023 categories (from the press release) were obtained. There are no numeric scores and no earlier editions. | Categorical cross-section only. | Collect archived SEI report PDFs per year; document scoring changes. |
| 4 | **SDI shared inputs:** SDI includes Caughey-Warshaw social opinion-policy residuals. Whether those draw on LGBT policies was not verified. | The SDI-MAP correlation may be partly mechanical. | Check the Caughey-Warshaw policy list; rebuild SDI without those items from `SDI_2.0_item_data.csv`. |
| 5 | **Measure-dependent adjusted result:** Rhodes's EDS and COVI keep an adjusted association with home values (2022); SDI does not. | The "explained by controls" conclusion is SDI-specific. | Item-level comparison of the indexes (next step 2 in the memo). |
| 6 | **ZHVI gaps:** North Dakota before 2009, plus Montana, New Mexico, Wyoming and single months elsewhere. | Unbalanced panel 2000-2008 (46-49 states). | None needed; documented. Zillow could backfill in later vintages. |
| 7 | **ZHVI revisions:** Zillow revises history. | Results tied to the 2026-11-06 vintage (SHA-256 in MANIFEST). | Re-run with `--force` and compare. |
| 8 | **ACS years:** keyless table-based files exist for 2021-2024 only. | ACS controls and the price-to-income ratio only for 2022-2023. | Free Census API key (you would need to register), then extend. |
| 9 | **Party control after 2022:** Rhodes's data end in 2022; Nebraska is missing. | The 2023 sensitivity uses 2022 values; n = 49. | NCSL or Klarner partisan composition for 2023. |
| 10 | **NIPA vs RPP vintages:** the PCE price index in NIPA differs from that embedded in BEA's February 2026 RPP release by under 0.1%. | Negligible. | None. |
| 11 | **COVI download URL** is versioned and may break. | The download step may fail later. | Update the URL from costofvotingindex.com/data. |
| 12 | **Mover extension not blind:** its spec was written after the 2023 tercile summary had been seen. | Group definitions (bottom/top third on both) could have been chosen differently. | Re-run with other cut-offs (e.g. halves, single measure) and report all. |
| 13 | **Mover cost model is partial:** national mortgage rate; no insurance, HOA, maintenance, closing or moving costs; origin income held fixed. | Owner cost shares are understated; the 30% line is a convention. | Add state insurance premiums and closing costs; a scenario with destination wages. |
| 14 | **Renter entry points use counties of 100k+ only** (ACS 1-year); small states have one or two such counties (Vermont: Chittenden only). | Rent entry points are degenerate in small states. | ACS 5-year county rents or HUD Fair Market Rents. |

## Redistribution (decided 2026-11-14: code, tables and figures public; restricted data local)

* **Raw files not redistributed (git-ignored):** SDI 2.0 (no license stated), Zillow state and county files (Terms of Use), Freddie Mac PMMS (terms of use), COVI (no license stated), MAP archived pages and the HRC press release (copyright). Public-domain (BEA, Census, FHFA) and CC0 (Rhodes) raw files are kept.
* **Processed files with values derived from those sources are git-ignored too:** `state_year_panel.csv`, `cross_section_2023.csv`, `map_policy_tally_2017_2024.csv`, `county_zhvi_2023.csv`, `entry_points_2023.csv`, `mover_matrix_2023.csv`. `scripts/run_all.py` rebuilds them from the original sources. Kept in git: data dictionaries, `merge_log.csv` (row counts only) and `pce_price_index.csv` (BEA).
* **Reported results stay public:** `output/tables/`, `output/figures/` and the executed notebook show estimates and some state-level values, as a published analysis would. Every figure carries a source line crediting Zillow and the other providers (defined in `src/hdl/figures.py`, `SOURCES`). Zillow's terms require clear attribution; the post itself should credit Zillow as well.
* **Reproducibility trade-off:** Zillow revises its history, so a rebuild can differ slightly from these results. The SHA-256 hashes in `data/raw/MANIFEST.csv` show whether the inputs changed.
* Nothing has been pushed or published.

## Not done (by instruction)

No providers were contacted, no data requests submitted, no accounts created, nothing paid for, nothing pushed or published.
