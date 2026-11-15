# Data inventory

Feasibility check for every candidate source, done before the sample was
chosen. Access date for all sources: **2026-11-06**, unless noted. The exact
files, URLs and SHA-256 hashes are in [`data/raw/MANIFEST.csv`](../data/raw/MANIFEST.csv).
"Verified" means the file was downloaded and inspected, not just described on
a web page.

## Summary

| Concept | Source | Used as | Years actually available | Status |
|---|---|---|---|---|
| Electoral democracy | Berkeley SDI 2.0 | **Main measure** | 2000-2023, annual, 50 states | Verified |
| Electoral democracy | Rhodes Electoral Democracy Score | Sensitivity (S8) | 2000, 2004, 2008, 2012, 2016, 2020, 2022 | Verified |
| Voting access (narrower) | Cost of Voting Index | Sensitivity (S9) | 1996-2024 presidential and 2022/2024 cycles | Verified |
| Election administration | MIT Elections Performance Index | Not used | (not downloaded) | Already an SDI input |
| Housing price level | Zillow ZHVI (state) | **Main measure** | Monthly 2000-01 to 2026-09; gaps for some states | Verified |
| Housing price level | ACS median owner-occupied value | Sensitivity (S2) | 2022, 2023 obtained (1-year) | Verified |
| Housing appreciation | FHFA all-transactions HPI | Appreciation only (H1) | Quarterly 1975-2026 | Verified |
| Median sale prices | e.g. Redfin, Zillow sale-price series | Not used | - | See notes |
| Consumer price levels | BEA Regional Price Parities | Extension | 2008-2024 annual | Verified |
| Purchasing power | BEA real personal income (SARPI) | Extension | 2008-2024 | Verified |
| Income, population | BEA SAINC1 | Controls / deflation | 1929-2025 | Verified |
| Inflation | BEA NIPA PCE price index (DPCERG) | Deflator | annual | Verified |
| Controls | ACS 1-year (income, education) | Controls | 2022, 2023 obtained | Verified |
| Controls | Census 2020 urban share | Control | 2020 | Verified |
| Controls | Party control (Rhodes replication) | Sensitivity (S7) | 2000-2022 | Verified |
| Mover extension: county home values | Zillow ZHVI (county) | Entry points (2023) | Monthly 2000-2026; 3,062 of 3,142 counties with 2023 values | Verified 2026-11-14 |
| Mover extension: income percentiles, rents, property taxes | ACS 1-year B19080, B25064, B25103 | Mover matrix (2023) | 2023 obtained | Verified 2026-11-14 |
| Mover extension: mortgage rate | Freddie Mac PMMS (30-year fixed, weekly) | Owner cost (2023 mean) | Weekly 1971-2026 | Verified 2026-11-14 |
| LGBTQ legal equality | MAP policy tally (archived pages) | **Extension measure** | Mid-year snapshots 2017-2024 | Verified |
| LGBTQ legal equality | MAP ICPSR 37877 | Not obtained | 2010, 2020 snapshots | Login required |
| LGBTQ legal equality | HRC State Equality Index | Extension (categorical) | 2023 edition categories obtained | Partly verified |

## Electoral democracy

### UC Berkeley State Democracy Index (SDI) 2.0. **Main measure.**
* **Provider / URL:** Democracy Policy Lab, Goldman School of Public Policy, UC Berkeley. https://democracypolicylab.berkeley.edu/state-democracy-index/. Data file: `https://democracypolicylab.berkeley.edu/wp-content/uploads/2025/01/SDI_2.0.csv`. Indicator list and report also downloaded.
* **Citation:** Grumbach, Jacob M., and Francesca Bitton. 2024. *State Democracy Index 2.0 Report.* UC Berkeley, December 2, 2024. Original index: Grumbach (2023), *APSR* 117(3): 967-984.
* **Measures:** `democracy_mcmc` (Bayesian factor-analysis score; main), `democracy_mcmc_sd` (posterior SD), `democracy_mcmc_se` (naive MCMC SE, equal to SD/100, so it reflects simulation error rather than measurement uncertainty), `democracy_additive` (additive index; the report calls it "a validation check and simple alternative").
* **Units / direction:** latent scale, set to mean 0 and SD 1 pooled over all state-years. Higher = better democratic performance.
* **Coverage:** 50 states (no D.C.), 2000-2023, annual, 1,200 rows, no missing values.
* **Inputs:** 54 indicators (list in `data/raw/sdi/variables_list.csv`). They include MIT Elections Performance Index items, voter ID, registration rules, felony disenfranchisement, gerrymandering metrics, and **Caughey-Warshaw economic and social opinion-policy residuals**. The social residual depends on state social-policy liberalism, which plausibly includes LGBT policies, so SDI may share inputs with the LGBTQ equality measures (see [STATUS](../STATUS.md)).
* **Frequency in practice:** annual rows, but changes cluster in even (election) years. Mean absolute annual change is 0.24 in even years and 0.02 in odd years. For the additive score, 38 of 50 states have an identical value in 2022 and 2023.
* **Format / access:** CSV, free, no login. **No license stated**, so the raw file is not redistributed; the download script fetches it.
* **Version consistency:** only SDI 2.0 is used. SDI 1.0 (2000-2018, 51 indicators) is a different release. The two are not spliced.

### Rhodes Electoral Democracy Score (EDS). **Sensitivity.**
* **Citation:** Rhodes, Jesse H. 2025/2026. "Laboratories of democratic renewal." *Political Science Research and Methods* 14(4): 1269-1286. https://doi.org/10.1017/psrm.2025.10051 (online 13 Oct 2025; open access CC BY 4.0). Replication data: https://doi.org/10.7910/DVN/NXULWY (Harvard Dataverse, **CC0 1.0**, published 2025-08-18).
* **Measure:** `democracy_mcmc` in `democracy_dataset.csv`. Bayesian factor analysis (MCMCfactanal, 1 factor, 1,000 burn-in and 1,000 draws) on 53 indicators. Higher = more democratic.
* **Coverage:** 50 states x 7 years (2000, 2004, 2008, 2012, 2016, 2020, 2022). It is not annual and nothing is interpolated.
* **Overlap with SDI:** it shares many indicators (EPI items, voter ID, gerrymandering, felony disenfranchisement) but omits the opinion-policy residuals. It is a sensitivity check, not an independent replication.

### Cost of Voting Index (COVI). **Sensitivity; narrower concept.**
* **Provider / URL:** https://costofvotingindex.com/data. File "COVI Values 1996-2024 website.xlsx". The URL is versioned and may change.
* **Citations:** Li, Pomante & Schraufnagel (2018), *Election Law Journal* 17(3): 234-247; Pomante (2025), *ELJ* 24(1): 52-61 (2024 update).
* **Measure:** `FinalCOVI`. Higher = **more costly** voting. It covers registration, voter ID, early and absentee voting and similar laws. It measures voting access only, not electoral democracy broadly.
* **Coverage:** 50 states, 1996-2024, presidential years plus 2022.
* **Methodology changes:** FinalCOVI recalculates 1996-2016 with considerations added in 2020 and corrects coding errors. Initial vs final values correlate at r = .75. 2020 and 2022 reflect Election Day law. A separate COVID-COVI exists for 2020, and a 2022 IRT variant is provided. Use FinalCOVI consistently.
* **License:** none stated, so the file is not redistributed.

### MIT Elections Performance Index (EPI)
* https://electionlab.mit.edu/research/projects/election-performance-index. It measures election administration (wait times, rejection rates, online tools). It was **not used separately**, because 22 of the 54 SDI 2.0 indicators are attributed to the EPI in the SDI variables list. Using it as a "robustness" measure would re-use the same data.

## Housing

### Zillow Home Value Index (ZHVI), state. **Main measure.**
* **URL:** `https://files.zillowstatic.com/research/public_csvs/zhvi/State_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv` (Zillow Research data page, https://www.zillow.com/research/data/; the page returned HTTP 403 to automated fetching, but the file downloaded).
* **Measure:** "typical home value": all homes (single-family and condo), middle tier (35th-65th percentile), smoothed and seasonally adjusted. These are model-based *estimated values* of the housing stock, not transaction prices. Current dollars.
* **Coverage:** 50 states + D.C.; monthly January 2000 to September 2026. **Gaps:** North Dakota is missing 108 months (before 2009), Montana 61, New Mexico and Wyoming 27, and several states have a single month missing.
* **Annual rule:** calendar-year mean of monthly values, kept if at least 10 of 12 months are present. This leaves 46-49 states in 2000-2008 and 50 from 2009.
* **Revisions:** Zillow revises the full history when its model changes (the ZHVI methodology was rebuilt in 2019-2023). The values used are the vintage downloaded on 2026-11-06 (SHA-256 in the manifest).
* **Terms:** Zillow Terms of Use require attribution, so the raw file is not redistributed.
* **Why main:** it is a dollar *level* comparable across states and years, annual, and covers the full SDI period.

### ACS median value of owner-occupied housing units (B25077). **Sensitivity.**
* **URL pattern:** `https://www2.census.gov/programs-surveys/acs/summary_file/{year}/table-based-SF/data/1YRData/acsdt1y{year}-b25077.dat`
* **Measure:** the owner's *self-reported* estimate of what the home would sell for, in current dollars, with a margin of error.
* **Access:** the Census Data API now **requires a key** (requests redirect to `missing_key.html`). A key is free, but obtaining one means registering on your behalf, so the keyless table-based summary files are used. These exist for **2021-2024 only**, so 2022 and 2023 were downloaded. Earlier ACS years would need the API key or the older sequence-based summary files.
* **Comparability:** ACS 1-year 2020 estimates were released only as experimental, and self-reports lag market moves. For 2023, log ZHVI and log ACS value correlate at r = 0.990, though levels differ (e.g. Maine, Vermont and Montana have ZHVI well above ACS).

### FHFA House Price Index, all-transactions, states. **Appreciation only.**
* **URL:** https://www.fhfa.gov/hpi/download/quarterly_datasets/hpi_at_state.csv. U.S. government work.
* **Measure:** repeat-sales (plus appraisals) index, not seasonally adjusted, 1980Q1 = 100 for *each* state. **Levels are not comparable across states**; only within-state appreciation is meaningful.
* **Coverage:** 50 states + D.C., 1975Q1 to 2026Q2. Annual value = mean of 4 quarters.

### Mover's-eye extension sources (accessed 2026-11-14)
* **Zillow county ZHVI:** `https://files.zillowstatic.com/research/public_csvs/zhvi/County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv`. Same series definition as the state ZHVI. 2023 annual mean kept if at least 10 of 12 months are present. 80 of 3,142 counties lack 2023 values (mostly small; Alaska's covered counties hold 88% of its population, every other state at least 93%). Zillow uses pre-2022 Connecticut counties, which match the 2020 Census county file used for population weights. Zillow terms apply: raw file not redistributed; derived county values are in `data/processed/county_zhvi_2023.csv` (decision needed before publishing; see STATUS).
* **County population weights:** 2020 Census county populations from `2020_UA_COUNTY.xlsx` (already downloaded). Not 2023 estimates; adequate for weighting and the 100k threshold.
* **ACS 2023 1-year B19080** (household income quintile upper limits: 20th, 40th, 60th, 80th percentiles), **B25064** (median gross rent, includes utilities; states and counties of 65k+), **B25103** (median real-estate taxes paid; divided by B25077 for an effective tax rate). Same keyless table-based summary files as above. County rows for Connecticut are 2022+ planning regions.
* **Freddie Mac Primary Mortgage Market Survey:** `https://www.freddiemac.com/pmms/docs/historicalweeklydata.xlsx`. U.S. weekly 30-year fixed rate; 2023 mean = 6.81% (52 weeks). National, not state-specific; the survey rate excludes fees and points. Freddie Mac terms of use apply: raw file git-ignored; only the annual mean is used.

### Median sale prices
* Sale-price series (Zillow median sale price, Redfin, NAR) start in the late 2000s or later at state level and reflect the composition of homes that happened to sell. They were not needed for the main question and were not downloaded. Composition effects: a median sale price moves when the *mix* of homes sold changes, even if no home changed value. ZHVI (a stock estimate) and FHFA (repeat sales) are designed to limit this. ACS reflects the stock but relies on owner perception.

## Prices and income (BEA)

### Regional Price Parities by state (SARPP). **Extension.**
* **URL:** https://apps.bea.gov/regional/zip/SARPP.zip; landing page https://www.bea.gov/data/prices-inflation/regional-price-parities-state-and-metro-area. Methodology: *Methodology for Regional Price Parities, Real PCE, and Real Personal Income* (BEA, July 2025), downloaded.
* **Release / vintage:** last updated **2026-02-19**, with new statistics for 2024 and revised statistics for 2008-2023. The next release is listed for 2026-12-10.
* **Coverage verified:** 50 states + D.C., annual **2008-2024**. The overlap with SDI 2.0 is **2008-2023** (16 years).
* **Published components (lines):** 1 all items; 2 goods; 3 services: housing; 4 services: utilities; 5 services: other. Goods and the services components are *published* series, so no subtraction or aggregation was needed.
* **Housing RPP definition:** price levels come from **tenant-occupied rents** (ACS PUMS). "No imputation of owner-occupied rents is used in the price levels; instead, BEA uses rent price levels for both renters and owners." Owner-imputed rents enter only as expenditure *weights*.
* **Methodology changes:** in December 2021, 2008-2019 were revised to PCE-based weights, annual ACS PUMS rents and annual (not 5-year averaged) CPI relatives. In December 2022, utilities were redefined (adding other fuels and water, with EIA electricity and gas prices). The current vintage applies these consistently across 2008-2024. BEA notes the CPI "was not designed for place-to-place comparisons", and volatile medical and education items use national price levels.
* **Interpretation:** RPPs compare price *levels* across states **within a year** (U.S. = 100). A change in RPP is a change *relative to the nation*, not a state inflation rate. BEA's implicit regional price growth = (RPP_t / RPP_t-1) x (U.S. PCE price index_t / _t-1).

### Implicit regional price deflators (SAIRPD) and real personal income (SARPI)
* Same zip. IRPD = RPP x U.S. PCE price index / 100 (the build checks this identity). SARPI line 2 is **real per-capita personal income** in constant 2017 dollars, defined as personal income / (RPP x national PCE price index) / population. This is the income-adjusted purchasing-power measure. It is not an affordability measure, a household budget or a tax-burden measure.

### SAINC1 (personal income, population) and NIPA PCE price index
* https://apps.bea.gov/regional/zip/SAINC.zip (SAINC1 last updated 2026-09-30, revised 2009-2025). https://apps.bea.gov/national/Release/TXT/NipaDataA.txt, series `DPCERG` (PCE chain-type price index, 2017 = 100). The NIPA vintage differs from the PCE index embedded in the February 2026 RPP release by under 0.1% in 2021-2023 (e.g. 2023: 120.505 vs 120.511), because NIPA was revised later. National deflation uses NIPA; BEA's own real-income series is used as published.

## Controls

* **ACS 1-year** (2022, 2023): median household income (B19013), educational attainment (B15003; bachelor's or higher = lines 22-25 over line 1), population (B01003). Public domain.
* **2020 Census urban share:** county file https://www2.census.gov/geo/docs/reference/ua/2020_UA_COUNTY.xlsx, aggregated to states (urban population / total). Check: Vermont = 35.1%, matching published figures. Constant over time.
* **Population-weighted state centres (2020):** https://www2.census.gov/geo/docs/reference/cenpop2020/CenPop2020_Mean_ST.txt, used for spatial weights and Conley SEs.
* **Party control:** `dem-control.tab` in Rhodes (2025) replication data (CC0): 1 = Democratic trifecta, 0 = Republican, 0.5 = divided. Covers 2000-2022; Nebraska is missing (nonpartisan legislature) and D.C. ends in 2016. The 2023 cross-section uses 2022 values. The underlying source is as documented by Rhodes; it was not independently checked.

## LGBTQ legal equality

### Movement Advancement Project (MAP) policy tally. **Extension measure.**
* **Provider:** Movement Advancement Project, https://www.mapresearch.org (formerly lgbtmap.org). Methodology: https://mapresearch.org/about/methodology/equality/. Data-request page (accessed 2026-11-06): MAP has "tracked LGBTQ policies since 2006" but "did not start creating the LGBTQ Policy Scores until mid-2015", and "our historical archives are more limited". It points users to the Wayback Machine and to ICPSR.
* **What was obtained:** Internet Archive captures of the "Equality Maps" overview page (`https://www.lgbtmap.org/equality-maps/`), one per year near 1 July. The 2015 and 2016 captures contain **no tally table**. Captures for 2017-2024 contain, for each state, sexual-orientation (SO), gender-identity (GI) and overall tallies, category sub-scores in "earned/maximum" form, and a "current as of" date:

  | Capture | Current as of | Max positive points | Category structure |
  |---|---|---|---|
  | 2017-07-08 | 2017-07-07 | 40 (varies by state) | 6 categories (old framework) |
  | 2018-06-22 | 2018-06-21 | 37 | 7 categories, religious exemptions added |
  | 2019-06-27 | 2019-06-26 | 40.5 | 7 categories (healthcare, criminal justice) |
  | 2020-07-02 | 2020-07-01 | 38.5 | maxima changed |
  | 2021-06-30 | 2021-06-30 | 38.5 | same as 2020 |
  | 2022-07-03 | 2022-07-01 | 42.5 | youth and criminal justice maxima raised |
  | 2023-07-01 | **2023-06-28** | 43.5 | GI healthcare maximum raised |
  | 2024-07-02 | 2024-06-27 | 44.5 | relationship maximum raised |

* **Measure / direction:** additive points; anti-LGBTQ laws subtract, so tallies can be negative. Higher = more LGBTQ-protective law. It covers *legal rights and protections* only.
* **Comparability:** the scoring framework changed in most years (the maxima above), so year-to-year changes in a state's tally mix **policy change with scoring change**. A consistent policy-level panel would need the per-policy indicators from state profile pages or ICPSR. The tally is used as a 2023 cross-section, plus annual *rank* correlations described only as patterns.
* **2023 timing:** the snapshot is current as of 2023-06-28. Laws taking effect later in 2023 are not reflected. SDI's 2023 value refers to the calendar year.
* **Redistribution:** MAP content, so the archived HTML is not redistributed; the parsed numbers are in `data/processed/`. See STATUS for the open question on publishing derived values.

### MAP / ICPSR 37877, "Mapping LGBTQ Equality: 2010 to 2020, United States"
* Study 37877, V2 (2021-07-14). About 40 laws and policies as of 1 January 2010 and 1 January 2020, with SO, GI and overall tallies for 50 states, D.C. and territories. ICPSR pages returned HTTP 403 to automated access; ICPSR states the data are available to member institutions and require a login. **Not downloaded.** This would let you, after logging in yourself, compare 2010 vs 2020 on a consistent indicator set.

### HRC State Equality Index (SEI). **Extension (categorical).**
* **Provider:** Human Rights Campaign Foundation with Equality Federation. https://www.hrc.org/resources/state-equality-index (not the Municipal Equality Index).
* **What was obtained:** the 2023 SEI press release (2024-01-30), which lists every state's category: "Working Toward Innovative Equality" (20 states + D.C.), "Solidifying Equality" (5), "Building Equality" (2), and "High Priority to Achieve Basic Equality" (23, which "indicates an SEI score below 30"). The lists were parsed from the saved HTML and validated to 50 states.
* **Measure:** four *ordered* categories. They are not treated as equally spaced numbers; models use category indicators, and correlations are rank-based.
* **Available years:** annual editions exist from 2014 (web search returned HRC press releases for several editions, including 2018-2021, 2023 and 2024; the full list of editions and their scoring changes was not compiled). Live state scorecards show only the current (2024) edition. Numeric scores and per-state scorecards for earlier editions would have to come from the archived report PDFs; these were not collected, so no HRC panel is built.
* **Timing:** the 2023 SEI covers the 2023 legislative season, so it is roughly contemporaneous with SDI 2023.

## Steps that need you (not done)

* **ICPSR 37877:** log in (ICPSR account, member institution) and download. This is free for member institutions.
* **Census API key** (free registration) to extend ACS controls to more years.
* **Contacting MAP or HRC** for dated historical snapshots or permission to redistribute derived values. Not done, as instructed.
