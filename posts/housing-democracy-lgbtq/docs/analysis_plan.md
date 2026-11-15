# Analysis plan (pre-specified)

Written on 2026-11-06, after the data feasibility check and before any model
was fitted. Changes made after seeing results are listed at the end, with
reasons.

## Concepts kept separate

| Concept | Main measure | What it is not |
|---|---|---|
| Electoral democracy | SDI 2.0 `democracy_mcmc` (Grumbach & Bitton 2024) | Not civil liberties broadly, and not LGBTQ rights |
| Voting access / cost of voting | COVI `FinalCOVI` (higher = costlier) | A narrower concept than electoral democracy |
| LGBTQ legal equality | MAP overall policy tally; HRC SEI category | Not a comprehensive human rights index |
| Housing price level | Zillow ZHVI, calendar-year mean of monthly values | Not affordability |
| Affordability proxy | ZHVI / ACS median household income | Not a complete affordability measure |
| Broader consumer price level | BEA RPPs: all items, goods, housing (rents), utilities, other services | Not an inflation rate, household budget or tax burden |
| Purchasing power | BEA real per-capita personal income (personal income / (RPP x US PCE price index)) | Not affordability of housing specifically |

## Samples

* **Main cross-section:** the 50 states in 2023. 2023 is the last SDI 2.0 year and is
  covered by ZHVI, ACS 1-year, BEA RPP, the MAP tally (snapshot "current as of
  2023-06-28") and the HRC 2023 SEI (released 2024-01-30, covering the 2023
  legislative season). D.C. is excluded because SDI 2.0 does not cover it.
* **Housing panel:** 50 states x 2000-2023 (SDI x ZHVI).
* **Price-level panel:** 50 states x 2008-2023 (RPP years overlapping SDI). All RPP
  outcomes and ZHVI are compared on this identical state-year sample.
* **MAP panel (descriptive only):** 2017-2023 mid-year snapshots. The maximum
  points change in most years, so within-state changes mix policy change with
  scoring change. Only annual cross-sectional correlations are reported.
* No democracy or equality score is interpolated. Years without a score are missing.

## Models and estimands

Notation: state *i*, year *t*. `D` = SDI `democracy_mcmc` standardised to mean 0
and SD 1 across the 50 states in the estimation year (cross-section) or left on
its native pooled scale (panel; native scale has SD of about 1 over 2000-2023).

**C1 (bivariate cross-section, 2023).**
`log ZHVI_i = a + b D_i + e_i`.
Estimand: the difference in mean log home value between states one SD apart on
SDI. It is a descriptive, between-state association. Reported as b and as
100(exp(b)-1) percent.

**C2 (adjusted cross-section).** C1 plus log median household income, the
bachelor's-or-higher share of adults 25+, and the 2020 urban population
share. Estimand: the same association among states with similar income,
education and urbanisation. These controls are partly *consequences* or
*correlates* of the same historical processes (sorting) and partly direct
determinants of housing demand. C2 is therefore not "more causal" than C1. It
shows how much of C1 lines up with these state characteristics.

**C3 (regional sensitivity).** C2 plus Census region indicators (4 regions).
Estimand: within-region association.

**C4 (partisan-control sensitivity).** C2 plus Democratic-trifecta and
Republican-trifecta indicators for 2022, from Rhodes (2025) replication data
(divided government is the reference). Nebraska is missing (nonpartisan
legislature), so n = 49. Partisan control is a likely common cause of
democracy scores (Grumbach 2023) and of LGBTQ policy. It is a separate
sensitivity analysis because it can also be a mediator.

**E1-E3 (equality extension, 2023).** Replace D with the MAP overall tally
(standardised) in C1/C2. Then include D and MAP jointly in C2. Report the
correlation between D and MAP and the variance inflation factor. HRC enters as
category indicators (reference = "High Priority to Achieve Basic Equality")
and is never treated as an equally spaced score.

**P1 (two-way fixed effects panel, 2000-2023).**
`log realZHVI_it = alpha_i + gamma_t + b D_it + c log realPCPI_it + e_it`.
Estimand: the within-state association. A state whose SDI is higher than its
own average, relative to the national year effect, has b higher log home
values. Standard errors are clustered by state (50 clusters). Driscoll-Kraay
standard errors are a sensitivity check for cross-sectional dependence.

**P2 (between vs within, correlated random effects / Mundlak).**
`log realZHVI_it = gamma_t + b_w D_it + b_m Dbar_i + ...`, where b_w is the
within association and b_w + b_m is the between association. Standard errors
are clustered by state.

**P3 (long differences).** The change in log real ZHVI (2000 to 2023, and 2008
to 2023) on the change in D, plus the change in log real PCPI. This is robust
to serial correlation and uses one observation per state.

**R1-R2 (price-level extension).** For each outcome (log RPP all items, goods,
housing rents, utilities, other services, log real per-capita personal income,
log ZHVI), estimate the C1/C2 analogue for 2023 and the P1 analogue for
2008-2023 on the identical state-year sample. RPPs are already relative to the
U.S. level within each year, so year fixed effects are included but RPP changes
are read as relative price-level changes, not state inflation rates.
Comparable effect sizes: standardised coefficients (SD change in outcome per
SD of D) and percent changes.

**A1 (affordability proxy).** C1/C2 with log(ZHVI / median household income) as
outcome. Controls exclude income to avoid putting the denominator on both
sides.

**H1 (appreciation, FHFA).** The FHFA all-transactions HPI is a repeat-sales
appreciation index. Index *levels* are not compared across states. Real log
appreciation for 2000-2023 and 2008-2023 is regressed on the initial SDI and on
the SDI change.

## Inference

* Cross-sections: HC3 standard errors (n = 50). Spatial dependence: Moran's I
  of residuals using inverse-distance weights among each state's 5 nearest
  neighbours (2020 population-weighted state centres), with a permutation
  p-value (seed 20261106, 9,999 permutations), plus Conley spatial-HAC
  standard errors with 500 km and 1,000 km Bartlett cutoffs.
* Panels: state-clustered SEs; Driscoll-Kraay as a sensitivity check; long
  differences.
* Index uncertainty: re-estimate C1/C2 over 2,000 draws of SDI from
  N(`democracy_mcmc`, `democracy_mcmc_sd`). The draws are independent across
  states, which approximates the posterior. Seed 20261106.
* Influence: Cook's distance, DFBETA for D, leave-one-state-out coefficients.

## Pre-specified sensitivity set (no others added without being labelled post hoc)

S1 additive SDI; S2 ACS median owner-occupied value instead of ZHVI; S3
dollar-level ZHVI instead of log; S4 drop Alaska and Hawaii; S5 population
weights (changes the estimand to the person-weighted association); S6 region
indicators (C3); S7 partisan control (C4); S8 Rhodes Electoral Democracy Score,
2022 cross-section with 2022 housing; S9 COVI 2022 (voting access, a narrower
concept) with 2022 housing; S10 SDI measurement uncertainty draws.

## What would count against the original observation

* A small or unstable C1 coefficient, or one driven by one or two states (LOO).
* A C1 coefficient that shrinks toward zero in C2. This means the observation
  is a proxy for income, education and urbanisation.
* A within-state P1 coefficient near zero while the between association is
  large. This means no evidence that democracy changes track price changes.
* Similar associations for all RPP components. This would point to a general
  price-level or sorting pattern rather than anything housing-specific.

## Post hoc changes

Added after the plan was written, all labelled post hoc:

1. **P1c**: the TWFE with log real PCPI restricted to 2008-2023, added to compare with the RPP-panel window. It is post hoc. Its interval includes zero; the no-control 2008-2023 ZHVI estimate in the price-level table (pre-specified as part of R2) excludes zero. Neither is treated as a finding because results differ by window and controls.
2. **Price-level controls (R1)**: the plan said "C1/C2 analogue". C2's income control was replaced by education and urban share only, for every RPP outcome, because one outcome (real per-capita income) is itself income. This was decided before seeing R1 results, but it is a deviation from the plan's wording.
3. **Variance decomposition and odd/even-year SDI changes** (t05c): descriptive diagnostics added to explain within-state power.
4. **HRC category summary** (t07b) and the **SDI vs 2022 party-control rank correlation** (0.67, used in the evidence table): descriptive only.
5. **ZHVI annual rule**: the plan said calendar-year mean. Missing months in Zillow's series forced a rule of at least 10 of 12 months, set before any model was run.

## Mover's-eye extension (added 2026-11-14; not blind)

Written after the 2023 tercile summary (median home value and income by SDI and
MAP thirds) had been seen, so it is not pre-specified in the strict sense. The
rules below were fixed before any of the new data were downloaded.

**Question.** What does it cost a household from a low-ranked state to move to
a high-ranked one, and is there a cheaper entry point inside high-ranked states?
Purely descriptive: it measures the price gap a mover faces, not why it exists.

**Groups (2023).** States are split into thirds on SDI and on the MAP overall
tally (`pd.qcut` on ranks, ties broken by row order). *Origin group*: bottom
third on both. *Destination group*: top third on both. Every other state-pair is
kept in the full 50 x 50 matrix.

**Origin income.** ACS 2023 1-year household income: the 20th, 40th, 60th and
80th percentiles (B19080 quintile upper limits) and the median (B19013).
Headline: the median. The mover is assumed to keep their origin income (remote
worker, retiree, or anyone whose pay does not change). Destination median
income is shown as the local-earner reference.

**Destination costs.**
* *Price-to-income*: 2023 ZHVI / origin income.
* *Owner cost share*: monthly principal and interest on a 30-year fixed loan at
  the 2023 average Freddie Mac PMMS rate, 10% down (20% as sensitivity), plus
  property tax at the state's effective rate (ACS B25103 median real-estate
  taxes / B25077 median value), divided by origin monthly income. Insurance,
  HOA fees and maintenance are excluded, so this understates costs.
* *Rent share*: ACS 2023 median gross rent (B25064, includes utilities) x 12 /
  origin income.
* *Threshold*: 30% of gross income (HUD's cost-burden line). This is a
  convention, not a measure of whether a move is feasible. Down payment
  (10% of price) is reported in dollars.

**Entry points (2023, home values).** County ZHVI (Zillow, same series
definition as the state index; annual mean with at least 10 of 12 months),
weighted by 2020 Census county population.
* *E-P10 (primary)*: population-weighted 10th percentile of county ZHVI, i.e.
  the home value at or below which the cheapest-county tenth of residents live.
* *E-100k*: cheapest county with population of at least 100,000 (a rough proxy
  for a labour market).
* *E-min*: cheapest county with any data (often small and rural; shown only).
* Coverage: share of state population in counties with a ZHVI value.

**Entry points (rent).** Cheapest ACS 2023 1-year county median gross rent
among counties of at least 100,000 people (1-year estimates exist only for
counties of 65,000+).

**Summaries.** For each measure: median across destination states vs median
across origin states, and the ratio. Correlation (Pearson, n = 50) of log
entry-point value with SDI and MAP, compared with the state-median correlation.

**What would weaken the "premium" framing.** Entry-point values in high-ranked
states near origin medians; origin-income cost shares under 30% for most
destinations at entry points.
