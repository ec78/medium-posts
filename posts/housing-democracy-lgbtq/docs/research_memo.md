# Research memo: home prices, electoral democracy and LGBTQ legal equality across U.S. states

*Exploratory, descriptive analysis, 2026-11-08. No result here is a causal
estimate. Full tables are in `output/tables/`, figures in `output/figures/`,
and the pre-specified plan in `docs/analysis_plan.md`.*

## Question

The starting observation: states with higher median home prices seem to have
stronger democracy. Is that true, how robust is it, and does it extend to LGBTQ
legal equality and to consumer prices beyond housing?

Concepts kept separate:
* **Electoral democracy:** SDI 2.0.
* **Voting access:** COVI, a narrower concept.
* **LGBTQ legal rights and protections:** the MAP policy tally and HRC SEI category; neither is a comprehensive human rights index.
* **Housing price levels:** ZHVI.
* **Affordability proxy:** ZHVI / median household income.
* **Consumer price levels:** BEA RPPs.
* **Purchasing power:** BEA real per-capita personal income.

## Data and sample

* **Main cross-section:** 50 states in 2023 (D.C. excluded; SDI 2.0 does not cover it). Every 2023 measure is available for all 50 states.
* **Panels:** SDI x ZHVI for 2000-2023, with 1,180 state-years (ZHVI gaps before 2009). SDI x RPP for 2008-2023, with 799 state-years on an identical sample for every outcome (North Dakota 2008 lacks ZHVI).
* **LGBTQ measures:** MAP tallies come from archived mid-year pages for 2017-2024; the 2023 tally is "current as of 2023-06-28". HRC 2023 categories come from HRC's 2024-01-30 release. MAP's scoring maxima change in most years, so MAP is used cross-sectionally, plus annual rank patterns only.

## Findings

### 1. The original observation holds as a raw between-state correlation

In 2023, SDI and log home values correlate at **r = 0.50** (95% CI 0.26-0.68; Spearman 0.53; n = 50). A one-SD-higher SDI goes with **20% higher home values** (95% CI +10% to +31%), or about **$66k** (CI $34k-$98k).

The association is not driven by a single state: leave-one-out estimates range from +18% to +24%, and every interval excludes zero. It holds for the additive SDI (+22%), ACS self-reported values (+20%), and with Alaska and Hawaii dropped (+20%). The population-weighted estimate, which describes the typical *resident* rather than the typical state, is +25% (CI +4% to +49%).

It is also not a pure housing artifact of measurement: ZHVI and ACS values correlate at 0.99 across states.

There are large exceptions. Tennessee has the lowest SDI but mid-range home values. Illinois has a high SDI but low values. Hawaii, California and Massachusetts sit far above the fitted line.

### 2. The correlation is mostly accounted for by income, education and urbanisation

Adding log median household income, the bachelor's-or-higher share and the urban share cuts the estimate to **+2% per SD (CI -6% to +11%)**:

| Specification | Estimate per SD of SDI | 95% CI |
|---|---|---|
| Plus Census-region indicators | -3% | -8% to +2% |
| Plus 2022 party control (n = 49) | -1% | -10% to +8% |
| Population-weighted | -0.5% | -11% to +11% |

Propagating SDI's posterior uncertainty barely matters. The draws give +19% for C1 and +2% for C2.

These controls are not neutral "confounders removed": education and income sorting is part of how places come to differ in both politics and prices. The defensible reading is that the observation is a proxy for the well-documented income/education/urban gradient. Once states are compared at similar income, education and urbanisation, SDI adds little detectable information about home values.

**Measurement caveat.** Two alternative measures keep a modest adjusted association in 2022:
* Rhodes's Electoral Democracy Score: +11% per SD (CI +3% to +20%), compared with +4% (CI -5% to +13%) for SDI on the same sample.
* The Cost of Voting Index: -10% per SD of voting cost (CI -16% to -4%).

These indexes share many inputs with SDI and are sensitivity checks, not replications. Why the adjusted association differs across them (e.g. SDI's opinion-policy residuals, which Rhodes's score omits) is unresolved. The conclusion "SDI adds little after controls" is therefore measure-specific.

### 3. Between states, not within states

* **Between states:** the Mundlak decomposition gives about **+12% per SDI unit** (CI +4% to +20%).
* **Within states** (two-way fixed effects, state-clustered SEs, controlling for real per-capita income): about **+1% per unit** (CI -1% to +3%). Driscoll-Kraay errors give the same point estimate with a slightly wider interval.
* **Long differences:** +3% (CI -3% to +9%) for 2000-2023 and -1% (CI -5% to +3%) for 2008-2023.

Only the 2008-2023 TWFE without the income control has an interval that excludes zero, at +2.9% (CI +0.3% to +5.6%). It is sensitive to window and controls and should not be read as a finding.

The panel is less informative than it looks. Only about 31% of SDI's variance is within states. SDI changes mostly in election years, with a mean absolute change of 0.24 in even years and 0.02 in odd years. Slow-moving institutions measured with error give weak within-state leverage. The within-state relationship is **small and unresolved**, not shown to be zero.

The between-state correlation was about 0.25-0.30 in the 2000s and about 0.50 from 2010 on, as SDI scores spread out after 2010 (the cross-state SD of SDI rose from about 0.6-0.7 to about 1.1).

On appreciation, using FHFA repeat-sales indexes only within states: states with higher SDI in 2000 appreciated more in real terms over 2000-2023, by +6.6 log points per SD (CI 1.4-11.8). Over 2008-2023 there is no relationship. SDI *changes* are unrelated to appreciation in both windows.

### 4. The pattern is not specific to housing

Comparing standardised coefficients (SD of outcome per SD of SDI) in the 2023 cross-section, with the same 50 states:

| Outcome (log) | Bivariate | + education, urban |
|---|---|---|
| Home value (ZHVI) | 0.50 [0.25, 0.74] | 0.12 [-0.11, 0.36] |
| RPP housing rents | 0.55 [0.33, 0.78] | 0.12 [-0.04, 0.27] |
| RPP all items | 0.57 [0.36, 0.77] | 0.17 [-0.02, 0.35] |
| RPP goods | 0.65 [0.45, 0.85] | 0.42 [0.22, 0.63] |
| RPP utilities | 0.33 [0.13, 0.54] | 0.04 [-0.24, 0.32] |
| RPP other services | 0.32 [0.10, 0.53] | 0.03 [-0.26, 0.33] |
| Real per-capita income (RPP-adjusted) | 0.36 [0.13, 0.60] | 0.10 [-0.15, 0.35] |

High-SDI states have higher price levels generally. The standardised association is at least as strong for goods as for housing, though housing varies far more in percentage terms (+16% per SD for rents vs +2.6% for goods). After controls, only goods keeps an association. Spatial goods-price indexes are sensitive to product mix (Handbury & Weinstein 2015), so that residual should not be over-read.

Within states (2008-2023 TWFE, identical 799-row sample), only ZHVI moves with SDI (0.16 SD [0.02, 0.31]). The RPP components and real income are flat. RPP changes are relative to the national level within each year, not state inflation rates. BEA's housing RPP prices tenant rents only.

**Affordability proxy.** Price-to-income ratios also rise with SDI: +9.7% per SD (CI +3% to +17%). With education and urban controls this falls to +3.5% (CI -5% to +12%). The ratio is not a complete affordability measure; it ignores rents, financing, taxes and insurance.

### 5. LGBTQ legal equality extension

* **MAP tally:** correlates with log home values at **r = 0.61** (CI 0.40-0.76), more strongly than SDI does. It goes with **+25% home values per SD** (CI +16% to +36%). With income, education and urban controls this falls to +3.5% (CI -6% to +14%).
* **SDI and MAP:** highly correlated (r = 0.75, Spearman 0.77). Entered together with controls, neither is distinguishable from zero: SDI +0.8% (CI -10% to +13%), MAP +3.0% (CI -10% to +18%). With 50 states, the data cannot separate democracy from LGBTQ legal equality. Part of their overlap may also be mechanical, because SDI includes opinion-policy residuals built from state policy liberalism.
* **HRC 2023 categories:** home values are about **66% higher** in "Working Toward Innovative Equality" states (n = 20) than in "High Priority to Achieve Basic Equality" states (n = 23), with CI +40% to +97%. With controls, the gap is +12% (CI -8% to +37%). "Building Equality" has only Utah and Arizona. The categories are ordered but not equally spaced and are modelled as indicators.
* **MAP annual pattern (2017-2024):** the rank correlation of MAP with home values is stable at 0.60-0.67. Its rank correlation with SDI rose from 0.59 (2017) to 0.77 (2023). This is descriptive only, because MAP's scoring changed in most years.

What the extension adds: LGBTQ legal equality follows the same between-state gradient as electoral democracy, slightly more strongly. It is equally explained by income, education and urbanisation, and is statistically inseparable from democracy in this sample. It adds evidence that the original observation reflects a broad bundle of state characteristics (affluence, education, urbanity, Democratic-leaning politics). It does not show that any single institution is associated with prices.

### 6. A mover's-eye view: the cost of moving up the rankings (2023)

This reframes the question. It does not ask why prices differ but what the difference costs a household that moves. Spec: [analysis_plan.md](analysis_plan.md), "Mover's-eye extension" (written after the tercile summary had been seen, so not blind). Tables t11-t14 and t12b; figures f11-f12.

* **Groups.** *Origin*: bottom third on both SDI and MAP (AL, AR, GA, ID, IN, LA, MO, MS, OK, SC, TN, TX, WY; 13 states). *Destination*: top third on both (CA, CO, CT, IL, ME, MN, NJ, NM, NY, OR, VT, WA; 12 states). The mover keeps their origin income: the median across origin states of each income percentile (median about $68k; 20th percentile about $29k; 80th about $132k).
* **Typical homes.** The median destination's typical home value is **1.72x** the median origin's ($412k vs $240k). At the median origin income, the destination home costs 3.7x income (Illinois) to 10.7x (California). Monthly principal, interest and property tax (10% down, 30-year fixed at the 2023 average of 6.81%) would take **more than 30% of gross income in all 12 destinations**, and more than half in 6 (NY, OR, CO, NJ, WA, CA). For reference, the same household pays about 28% at its own state's typical value (t12b), so the 2023 rate environment is tight everywhere.
* **Entry points.** The population-weighted 10th-percentile county value (E-P10) is 15% (CT) to 54% (NY) below the state typical value in destination states. At those entry points, **5 of 12 destinations fall under 30%** for a median-income origin household: Illinois 18%, New Mexico 20%, Maine 24%, Minnesota 26% and New York 26%. The entry-point down payment (10%) runs from about $13k (IL) to $41k (CA).
* **The ratio does not shrink at entry points.** Origin states have cheap counties too, so the destination/origin ratio is 1.84 at E-P10 and 1.69 at the cheapest county of 100k+. The entry point helps a mover only relative to the destination's typical home, not relative to the cheap end of their own state.
* **Renting is a much lower bar.** Destination state median gross rent is 1.44x the origin median; the cheapest large-county rent in destination states is only 1.11x. A median-income origin household would pay under 30% of income for state median rent in 9 of 12 destinations and for the cheapest large-county rent in all 12.
* **By income.** At the 20th percentile, no destination is under 30% on any measure, owning or renting. At the 80th percentile, 8 of 12 typical homes and all 12 entry points are under 30% (t14).
* **Local earners.** Destination residents earning their own state's median income pay a median of about 42% at the typical home (owner_share_local in t12), so the premium also bites locals. It bites harder for a mover whose income does not rise with the move.
* **Correlations.** Log entry-point values still correlate with SDI (0.42) and MAP (0.55), only slightly less than state typical values do (0.50, 0.61). The cheapest large-county rent correlates more weakly (0.31, 0.44).

**What this supports.** "On average, moving from the lowest-ranked to the highest-ranked states for democracy and LGBTQ legal equality means paying much more for housing. For a household on a typical income from a low-ranked state, buying a typical home there would take more than 30% of gross income in every high-ranked state. Cheaper entry points (cheaper counties, and especially renting) exist in most of them. For lower-income households, even those are out of reach under standard affordability lines." Legal protections apply statewide, so an entry point gives the same legal protection as the state's most expensive county. Jobs, services and community may differ.

**What it does not support.** That anyone was prevented from moving: there are no data here on intended or blocked moves. That prices reflect the value of democracy or equality: the gap is a price gap between groups of states, not a premium paid for institutions. The 30% line is a convention; insurance, maintenance, moving costs, job changes and destination wages are excluded; the mover is assumed to keep origin income. The grouping uses the bottom and top thirds on two measures. Idaho is an expensive origin state and would change any "cheap origin" story told about it.

## Inference notes

* **Spatial dependence:** cross-sectional residuals are spatially autocorrelated (Moran's I about 0.4, permutation p < 0.001, 5-nearest-neighbour weights). Conley spatial-HAC SEs (500 and 1,000 km) are close to HC3 SEs. Region indicators remove most of the residual spatial pattern (Moran's I = 0.03).
* **Serial dependence:** handled with state-clustered SEs (50 clusters), Driscoll-Kraay SEs and long differences.
* **Multiplicity:** about 40 pre-specified estimates are reported. Isolated p < 0.05 results among them, such as HRC "Solidifying Equality" with controls (-17%, n = 5), should be treated as noise unless replicated.

## Material limitations

1. **Descriptive only.** Fixed effects, controls and lags do not identify causal effects. The literature points to strong common causes (sorting, partisanship, opinion) and to reverse channels (prices to regulation politics).
2. **Fifty units.** Effects of a few percent cannot be distinguished from zero, and overlapping concepts (SDI, MAP, HRC) cannot be separated.
3. **Overlapping and shared-input measures.** SDI includes EPI items and policy-liberalism residuals; Rhodes's EDS and COVI share inputs with SDI; MAP and HRC tally overlapping laws.
4. **Slow-moving institutions.** About 31% of SDI's variance is within states, and changes cluster in election years.
5. **Timing.** The MAP 2023 snapshot is mid-year; HRC covers the 2023 session; SDI is calendar-year; party control is from 2022.
6. **Housing measures.** ZHVI is a model estimate that Zillow revises; ACS values are self-reported; the BEA housing RPP is based on rents; the affordability proxy is partial.
7. **Controls as mediators.** Income and education can be outcomes of the same historical processes, so C2 is a different estimand, not a "cleaner" one.
8. **Literature reviewed at abstract level only.**

## Next steps

1. Obtain ICPSR 37877 (you would need to log in) for a 2010 vs 2020 MAP comparison on a consistent indicator set, and pair it with SDI changes.
2. Investigate why Rhodes's EDS and COVI keep an adjusted association while SDI does not. Rebuild SDI without the opinion-policy residuals using `SDI_2.0_item_data.csv`, which is available but not used here.
3. Extend the county analysis (now used only for entry points) to separate state institutions from local sorting, and add metro rents (e.g. HUD Fair Market Rents) for renter entry points in states with few large counties.
4. Collect archived HRC SEI reports for an annual categorical panel, documenting scoring changes.
5. If a causal question is pursued, look for discrete, plausibly exogenous institutional changes (court-ordered redistricting, ballot-initiative reforms) and pre-register the design.
