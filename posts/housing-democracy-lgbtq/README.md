# Home prices, electoral democracy and LGBTQ legal equality across U.S. states

Research project for an upcoming post. It tests an informal observation,
*states with higher home prices seem to have stronger democracy*, and asks
whether home prices also track LGBTQ legal equality and broader consumer
price levels. The analysis is descriptive; it estimates no causal effects.

## Research questions

1. Across the 50 states, are home values associated with electoral democracy (SDI 2.0)? How sensitive is that to measurement and to income, education, urbanisation, region and party control?
2. Is the association between states, within states over time, or both?
3. Is it specific to housing, or does it extend to other consumer prices (BEA Regional Price Parities) and to purchasing power?
4. Are home values associated with LGBTQ legal rights and protections (MAP policy tally, HRC State Equality Index categories), and can that be separated from democracy?
5. What does the gap cost a household moving from a low-ranked to a high-ranked state, and are there cheaper entry points? (descriptive, mover's-eye extension)

## Main findings (details in [docs/research_memo.md](docs/research_memo.md))

* **The raw observation holds.** In 2023, a 1-SD-higher SDI goes with about 20% higher home values (95% CI +10% to +31%; r = 0.50; n = 50). No single state drives it.
* **Income, education and urbanisation account for most of it.** With those controls the estimate is +2% (CI -6% to +11%); with region or party control it is near zero. Rhodes's Electoral Democracy Score and the Cost of Voting Index keep a modest adjusted association, so this conclusion depends on the measure.
* **Between states, not within.** Between states the association is about +12% per SDI unit. Within states it is about +1% (CI -1% to +3%). Long differences are near zero. The within-state data are weak because SDI moves slowly and mainly in election years.
* **Not housing-specific.** Across states, SDI tracks goods and all-items price levels about as strongly as housing (standardised 0.5-0.65). Within states, only home values (weakly) move with SDI.
* **LGBTQ legal equality follows the same pattern.** The MAP tally correlates with home values at r = 0.61. Controls absorb most of it, and with 50 states it cannot be separated from SDI (r = 0.75 between them).
* **The mover's cost is real, whatever its cause.** For a median-income household from the states ranked lowest on both measures, a typical home in every top-ranked state would take more than 30% of gross income (2023 rates, 10% down). At cheaper entry points (the cheapest-county tenth of residents), 5 of 12 come in under 30%, and renting the cheapest large county is under 30% in all 12. At the 20th income percentile nothing is. See memo section 6.

## Layout

```
README.md, STATUS.md            overview; unresolved data issues and redistribution notes
requirements.txt                pinned top-level packages (requirements-lock.txt = full environment)
docs/data_inventory.md          every candidate source: coverage, units, access, comparability
docs/analysis_plan.md           pre-specified models, estimands, sensitivity set, post hoc log
docs/research_memo.md           findings, sensitivity, limitations, next steps
data/raw/MANIFEST.csv           URL, access date, size, SHA-256 and redistribution note for every raw file
data/processed/                 state_year_panel.csv (50 x 2000-2024), cross_section_2023.csv,
                                data_dictionary.{csv,md}, merge_log.csv, map_policy_tally_2017_2024.csv,
                                entry_points_2023.csv, county_zhvi_2023.csv, mover_matrix_2023.csv (+ mover_data_dictionary.md)
src/hdl/                        reusable code: build (load/clean/validate/merge), stats, analysis, mover, figures
scripts/01_download.py ... 06   pipeline steps; run_all.py runs them in order (06_mover before 04_notebook)
notebooks/analysis.ipynb        executed notebook calling src/hdl
output/tables/                  model and descriptive tables (.csv + .md)
output/figures/                 figures (.png + .svg)
literature/                     evidence_table.{csv,md}, synthesis.md, search_log.md, bibliography.bib,
                                verified_metadata.json, search_results_openalex.jsonl
```

## Setup and commands

Python 3.12. From this folder:

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python scripts\run_all.py          # download (missing files only), build, analyse, notebook, literature tables
```

Individual steps:

```powershell
.venv\Scripts\python scripts\01_download.py      # add --force to re-fetch (upstream data get revised)
.venv\Scripts\python scripts\02_build.py         # validation raises on duplicate keys, unmatched states, changed years
.venv\Scripts\python scripts\03_analysis.py
.venv\Scripts\python scripts\06_mover.py         # mover affordability matrix and entry points (2023)
.venv\Scripts\python scripts\04_notebook.py      # regenerates and executes notebooks/analysis.ipynb
.venv\Scripts\python scripts\05_literature_tables.py
.venv\Scripts\python scripts\lit_search.py       # re-runs the logged OpenAlex queries (results will drift)
.venv\Scripts\python scripts\lit_verify.py       # re-checks DOIs against Crossref
```

All paths are relative to this folder. Seeds: 20261106 (permutation tests, SDI posterior draws, plot jitter). No API keys, logins or payments are needed.

**Data not in this repository.** Raw and processed files containing values from Zillow, the State Democracy Index, the Cost of Voting Index, MAP or HRC are git-ignored because their terms do not clearly permit redistribution. On a fresh clone, run `scripts\run_all.py` first: it downloads the originals and rebuilds every processed file. Zillow revises its history, so results can differ slightly from the published ones; compare SHA-256 hashes against `data/raw/MANIFEST.csv`. See [STATUS.md](STATUS.md).

## Sources

Berkeley State Democracy Index 2.0 (Grumbach & Bitton 2024); Rhodes (2025) replication data (CC0); Cost of Voting Index; Zillow Home Value Index (state and county); Freddie Mac PMMS; FHFA HPI; U.S. Census Bureau (ACS 1-year, 2020 urban areas, centres of population); BEA (Regional Price Parities, personal income, PCE price index); Movement Advancement Project policy tallies (via Internet Archive); Human Rights Campaign State Equality Index 2023. Full citations: [literature/bibliography.bib](literature/bibliography.bib).
