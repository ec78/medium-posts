"""Generate and execute notebooks/analysis.ipynb.

The notebook is a thin, readable layer over src/hdl: it rebuilds nothing by
hand, it calls the same functions as scripts/03_analysis.py and displays the
results with short interpretive notes.

Usage:  python scripts/04_notebook.py
"""
from __future__ import annotations

from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "notebooks" / "analysis.ipynb"

md = nbf.v4.new_markdown_cell
code = nbf.v4.new_code_cell

cells = [
    md("""# Housing prices, electoral democracy and LGBTQ legal equality across U.S. states

Exploratory, descriptive analysis. Nothing here estimates a causal effect.

Three concepts are kept separate throughout:

* **Electoral democracy:** Berkeley State Democracy Index (SDI) 2.0, `democracy_mcmc`.
* **LGBTQ legal rights and protections:** the MAP overall policy tally and the HRC State Equality Index category. Neither is a comprehensive human rights index.
* **Housing prices and affordability:** the Zillow Home Value Index (ZHVI), with ZHVI / median household income as an affordability *proxy*.

The pre-specified models are in `docs/analysis_plan.md`; model labels (C1, P1, S1, ...) match it."""),
    code("""import sys
from pathlib import Path
ROOT = Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd
from IPython.display import Image, Markdown, display
from hdl import PROC, FIG
from hdl.analysis import run_all, load

pd.set_option("display.width", 200, "display.max_columns", 30, "display.precision", 3)
print("pandas", pd.__version__)"""),
    md("## 1. Data and merge validation\n\n`scripts/02_build.py` built the panel and raised on any failed check: duplicate keys, unmatched states, unexpected year ranges, or broken BEA identities. The merge log and coverage are shown below."),
    code("""display(pd.read_csv(PROC / "merge_log.csv"))
panel, cs = load()
cov = panel.groupby("year")[["sdi", "zhvi", "rpp_all", "eds", "covi", "map_overall", "hrc_category", "acs_value"]].count()
cov"""),
    md("ZHVI has gaps before 2009 (North Dakota, Montana, New Mexico and Wyoming). Those state-years are missing; nothing is interpolated. SDI 2.0 ends in 2023, so the 2024 SDI values are missing by design."),
    code("res = run_all()  # writes output/tables and output/figures"),
    md("## 2. The 2023 cross-section"),
    code("res['desc']"),
    code("res['corr']"),
    code("display(Image(str(FIG / 'f01_sdi_vs_home_values_2023.png')))"),
    md("""States with higher SDI scores have higher home values. The rank correlation is about 0.53. The scatter also shows wide dispersion: Tennessee (lowest SDI) has higher values than Illinois (one of the highest), and Hawaii, California and Massachusetts sit far above the line."""),
    code("res['cross']['table'][['model','term','coef','ci_low','ci_high','pct_per_sd','n','r2','conley1000_se','resid_morans_i','morans_p']]"),
    md("""**Reading C1 vs C2.** The bivariate coefficient (C1: about +20% home value per SD of SDI) falls to about +2% once median household income, the college share and the urban share are added (C2). The C2 interval comfortably includes zero. These controls are not neutral: education and income are themselves part of the sorting story. The original observation is consistent with democracy scores and home values *both* lining up with richer, more educated, more urban states. On its own it does not point to anything specific to democracy.

Residuals are spatially autocorrelated (Moran's I about 0.4). Conley spatial-HAC standard errors are similar to the HC3 ones, and regional indicators remove most of the residual spatial pattern."""),
    code("res['sens']"),
    md("""**Sensitivity.** The C1/C2 pattern holds with:
* the additive SDI;
* ACS self-reported values;
* dollar levels;
* Alaska and Hawaii dropped;
* population weights, which change the estimand to the person-weighted association;
* region or party-control controls;
* SDI posterior draws.

Two alternative measures differ. Rhodes's Electoral Democracy Score (2022) and the Cost of Voting Index (2022, a narrower voting-access measure) keep a modest adjusted association of about 10% per SD. These indexes share many inputs with SDI, so they are sensitivity checks, not independent replications. The difference is a measurement question worth flagging, not a resolved finding."""),
    code("display(Image(str(FIG / 'f04_leave_one_out.png')))\nres['influence']['summary']"),
    md("## 3. Between vs within states"),
    code("display(Image(str(FIG / 'f02_annual_correlations.png')))\nres['vardecomp']"),
    md("""The between-state correlation rose from about 0.25-0.30 in the 2000s to about 0.5 from 2010 onward, as SDI scores spread out. About 31% of SDI's variance is within states. SDI changes are concentrated in even (election) years: the mean absolute change is about 0.24 in even years and about 0.02 in odd years. The annual panel therefore carries far fewer independent changes than its 24 rows suggest."""),
    code("display(Image(str(FIG / 'f03_within_state.png')))\nres['panel']['table']"),
    md("""**Within states** (two-way FE, state-clustered SEs), a one-unit rise in SDI goes with roughly 1% higher real home values. The interval runs from about -1% to +4%. Driscoll-Kraay standard errors and long differences agree, and the 2008-2023 long difference is slightly negative. **Between states** (Mundlak), the association is about +12% per unit. The relationship is mainly a between-state pattern. Slow-moving institutions and few effective within-state changes mean the within estimate is imprecise, not a demonstrated zero."""),
    code("res['appreciation']"),
    md("FHFA repeat-sales indexes are used only for appreciation, never for cross-state levels. States with higher SDI in 2000 appreciated more over 2000-2023, but not over 2008-2023. SDI *changes* are unrelated to appreciation in both windows."),
    md("## 4. Affordability proxy"),
    code("display(Image(str(FIG / 'f08_price_to_income.png')))"),
    md("Price-to-income ratios rise with SDI too, more weakly (r about 0.37). The association disappears with education and urban controls (model A1 in the table above). This ratio ignores rents, interest rates, taxes and insurance, so it is a proxy only."),
    md("## 5. Broader price levels (BEA Regional Price Parities)"),
    code("display(Image(str(FIG / 'f05_price_level_extension.png')))\nres['prices']"),
    md("""Across states in 2023, SDI is about as strongly associated with the all-items and **goods** RPPs (standardised about 0.57-0.65) as with home values and rents (about 0.50-0.55). Utilities and other services are weaker (about 0.3). The pattern is not specific to housing; it is a general price-level gradient. With education and urban controls, the housing-rent and all-items associations shrink toward zero, while goods keeps a modest association. Within states over 2008-2023 (identical 799 state-year sample), only ZHVI shows a small positive coefficient, and RPP components are flat. RPP changes are relative to the U.S. level within a year, not state inflation rates. BEA's housing RPP is based on tenant rents only."""),
    md("## 6. LGBTQ legal equality extension"),
    code("display(Image(str(FIG / 'f07_map_scatter.png')))\nres['cross']['vif']"),
    code("display(Image(str(FIG / 'f06_hrc_categories.png')))\nres['hrc']"),
    code("display(Image(str(FIG / 'f09_map_annual.png')))\nres['map_annual']"),
    md("""MAP's tally is somewhat *more* strongly associated with home values than SDI is (r about 0.61 vs 0.50). It shows the same collapse once income, education and urbanisation are controlled (E2). SDI and MAP are highly correlated (r = 0.75); together (E3), neither coefficient is distinguishable from zero. With 50 states the data cannot separate them. HRC categories tell the same story: the top category's median ZHVI is about $429k vs $252k in the lowest, and the gap shrinks substantially with controls. The "Building Equality" group has only two states (Utah, Arizona). The MAP-SDI rank correlation rose from 0.59 (2017) to 0.77 (2023). MAP's maximum attainable points changed in most years, so within-state changes in the tally are not interpreted."""),
    md("""## 7. A mover's-eye view (descriptive, 2023)

This section asks what the price gap costs a household that moves, not why the gap exists. Spec: `docs/analysis_plan.md`, "Mover's-eye extension" (written after the tercile summary had been seen, so not blind). *Origin* states rank in the bottom third on both SDI and the MAP tally; *destination* states rank in the top third on both. The mover keeps their origin income. Costs use the 2023 average 30-year rate, 10% down, and the state's effective property-tax rate; insurance and maintenance are excluded."""),
    code("""from hdl.mover import run_mover
mv = run_mover()  # writes data/processed/{entry_points,county_zhvi,mover_matrix}_2023.csv, t11-t14, f11-f12
print(f"2023 mean 30-year fixed rate: {mv['rate']:.2f}%")
print("origin states:", " ".join(mv['origins']))
print("destination states:", " ".join(mv['destinations']))
mv['origin_income']"""),
    code("display(Image(str(FIG / 'f11_entry_points.png')))\nmv['t13']"),
    md("""**Entry points.** E-P10 is the county home value below which the cheapest-county tenth of a state's residents live. It is 15-54% below the state typical value in destination states. But origin states have cheap counties too, so the destination/origin ratio barely moves (1.72 at state typical values, 1.84 at E-P10). Rents are different: the cheapest large-county rent in destination states is only about 11% above the origin median, versus 44% for state median rents. Small states with one large county (Vermont) make E-100k degenerate."""),
    code("display(Image(str(FIG / 'f12_mover_cost_share.png')))\nmv['t14']"),
    code("mv['t12'][['dest','zhvi','entry_p10','pti_median','pti_p10','owner_share_median','owner_share_p10','rent_share_median','rent_share_entry','owner_share_local','down_median','down_p10']]"),
    code("mv['home']"),
    md("""**Reading the matrix.** A median-income household from the origin states (about $68k) would spend more than 30% of gross income on principal, interest and tax at the typical home in all 12 destinations, and over half of income in 6 of them. At entry points, 5 of 12 come in under 30% (IL, NM, ME, NY, MN). The same household at home pays about 28% at its own state's typical value (2023 rates make ownership tight everywhere). Renting is far more accessible: state median rent is under 30% in 9 of 12 destinations and the cheapest large-county rent in all 12. Households at the 20th percentile (about $29k) are over 30% everywhere on every measure. These are illustrative calculations under stated assumptions, not evidence that anyone was prevented from moving."""),
    md("## Environment"),
    code("""import numpy, scipy, statsmodels, matplotlib
for m in (numpy, scipy, statsmodels, matplotlib, pd):
    print(m.__name__, m.__version__)
print(sys.version)"""),
]

nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3"}})
NB.parent.mkdir(exist_ok=True)
NotebookClient(nb, timeout=1200, kernel_name="python3", resources={"metadata": {"path": str(NB.parent)}}).execute()
nbf.write(nb, NB)
print("wrote and executed", NB.relative_to(ROOT))
