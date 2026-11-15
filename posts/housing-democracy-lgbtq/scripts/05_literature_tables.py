"""Write literature/evidence_table.csv and .md from the records below.

Bibliographic fields were checked against Crossref (literature/verified_metadata.json).
Findings are paraphrased from abstracts. The `verified_against` field says what
was actually read: no full texts were read unless stated. Claims that rest on
secondary coverage are flagged in `limitations`.

Usage:  python scripts/05_literature_tables.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "literature"

R = []


def add(**kw):
    R.append(kw)


# ---------------------------------------------------------------- related empirical (closest to our question)
add(id="nguyen2023", tier="core", evidence_type="Related empirical",
    citation="Nguyen, V., & Vergara-Alert, C. (2023). Political uncertainty and housing markets. Journal of Housing Economics, 61, 101952.",
    doi="https://doi.org/10.1016/j.jhe.2023.101952", status="Published (peer-reviewed)",
    geography="U.S. states and border counties", years="1982-2018",
    data="Gubernatorial election timing; state and county housing prices, transactions, permits, mortgages",
    method="Elections as quasi-exogenous uncertainty shocks; neighbouring non-election states and border counties as controls",
    finding="Election-year political uncertainty lowers house-price growth and transactions and raises building permits; effects are larger in close elections.",
    limitations="Studies short-run uncertainty around elections, not the quality of democratic institutions; abstract only.",
    relevance="Closest housing study using state political institutions. It shows state politics can move housing markets in the short run, but it does not test democratic quality.",
    verified_against="Abstract (OpenAlex) + Crossref metadata")
add(id="christafore2012", tier="core", evidence_type="Related empirical",
    citation="Christafore, D., & Leguizamon, S. (2012). The influence of gay and lesbian coupled households on house prices in conservative and liberal neighborhoods. Journal of Urban Economics, 71(2), 258-267.",
    doi="https://doi.org/10.1016/j.jue.2011.09.004", status="Published (peer-reviewed)",
    geography="One U.S. metro area (Columbus, Ohio, per secondary coverage)", years="2000 (per secondary coverage)",
    data=">20,000 house sales; same-sex coupled households; neighbourhood votes on a Defense of Marriage Act measure",
    method="Hedonic price regressions with interaction by neighbourhood political orientation",
    finding="More same-sex coupled households is associated with higher prices in more liberal neighbourhoods and lower prices in more conservative ones.",
    limitations="Neighbourhood population composition, not state law; a single metro; geography and years come from press coverage, not the full text.",
    relevance="Related: local attitudes toward LGBT people interact with housing prices. Note that it measures attitudes and residents, not legal protections.",
    verified_against="Abstract (RePEc/IDEAS) + Crossref metadata; full text not accessed")
add(id="florida2010", tier="core", evidence_type="Related empirical",
    citation="Florida, R., & Mellander, C. (2010). There goes the metro: how and why bohemians, artists and gays affect regional housing values. Journal of Economic Geography, 10(2), 167-188.",
    doi="https://doi.org/10.1093/jeg/lbp022", status="Published (peer-reviewed)",
    geography="U.S. regions (data details not verified)", years="Not stated in abstract",
    data="'Bohemian-Gay Index' plus income, wages, technology and human capital",
    method="Cross-sectional statistical models across region sizes",
    finding="The Bohemian-Gay Index has a positive direct association with housing values across model permutations, and is strongly correlated with income (an indirect channel).",
    limitations="Cross-sectional; the composite index mixes population groups; the 'tolerance premium' interpretation is not identified; years and data not checked.",
    relevance="Related: open or tolerant places have higher housing values, but the index is strongly entangled with income. This is the same confounding pattern found here.",
    verified_against="Abstract excerpts (OUP page) + Crossref metadata; full text not accessed")
add(id="baumle2023", tier="core", evidence_type="Related empirical",
    citation="Baumle, A. K., Miller, A., & Gregory, E. (2023). Effects of state-level abortion and LGBT laws and policies on interstate migration attitudes. Population Research and Policy Review, 42(6).",
    doi="https://doi.org/10.1007/s11113-023-09842-7", status="Published (peer-reviewed)",
    geography="United States (survey respondents)", years="Survey published 2023 (fielding dates not checked)",
    data="Survey of 1,061 respondents rating willingness to move to states with restrictive abortion and LGBT policies",
    method="Survey regressions of stated migration attitudes on political orientation, state context and demographics",
    finding="Political orientation is the strongest predictor; restrictive gender and sexuality policies act more as a deterrent to (politically motivated) migration than as an incentive.",
    limitations="Stated attitudes, not observed moves or prices; non-probability sample details not checked.",
    relevance="Mechanism evidence for an LGBTQ-law -> migration -> housing-demand channel. It is attitudinal and does not show price effects.",
    verified_against="Abstract excerpts (University of Houston page) + Crossref metadata")

# ---------------------------------------------------------------- mechanisms: spatial equilibrium, amenities, sorting
add(id="roback1982", tier="core", evidence_type="Mechanism / conceptual",
    citation="Roback, J. (1982). Wages, rents, and the quality of life. Journal of Political Economy, 90(6), 1257-1278.",
    doi="https://doi.org/10.1086/261120", status="Published (peer-reviewed)", geography="U.S. cities", years="1970s data",
    data="City wages, site prices, amenities", method="Spatial-equilibrium model; hedonic estimation",
    finding="Amenities are capitalised into rents (positive gradient); wage effects depend on whether the amenity is also productive.",
    limitations="Classic framework; amenities treated as exogenous.",
    relevance="Framework: if residents value democratic or rights-protective institutions, values should show up in land and housing prices. The same logic applies to any correlated amenity, so a price premium is not evidence about which amenity drives it.",
    verified_against="Abstract (OpenAlex) + Crossref metadata")
add(id="albouy2016", tier="core", evidence_type="Mechanism / conceptual",
    citation="Albouy, D. (2016). What are cities worth? Land rents, local productivity, and the total value of amenities. Review of Economics and Statistics, 98(3), 477-487.",
    doi="https://doi.org/10.1162/REST_a_00550", status="Published (peer-reviewed)", geography="U.S. metropolitan areas", years="Not checked",
    data="Wages and housing costs by metro", method="Spatial-equilibrium accounting with federal taxes and non-traded goods",
    finding="Wage and housing-cost differences across metros are explained more by productivity than by quality of life; the most valuable cities are coastal, sunny, mild, educated and large.",
    limitations="Metro level; amenity values are inferred residually.",
    relevance="Housing-cost gradients mostly reflect productivity and education, which also correlate with SDI. This is consistent with the collapse of the SDI coefficient once controls are added.",
    verified_against="Abstract (OpenAlex) + Crossref metadata")
add(id="gyourko2013", tier="core", evidence_type="Mechanism / conceptual",
    citation="Gyourko, J., Mayer, C., & Sinai, T. (2013). Superstar cities. American Economic Journal: Economic Policy, 5(4), 167-199.",
    doi="https://doi.org/10.1257/pol.5.4.167", status="Published (peer-reviewed)", geography="U.S. metro areas and municipalities", years="~50 years to the 2000s",
    data="Long-run house prices, incomes", method="Descriptive and model-based",
    finding="Long-run appreciation differences are explained by inelastic land supply in unique places combined with a growing number of high-income households nationally.",
    limitations="Metro-level; not about institutions.",
    relevance="An alternative explanation for high-price, high-SDI coastal states: inelastic supply plus aggregate demand.",
    verified_against="Abstract (OpenAlex) + Crossref metadata")
add(id="diamond2016", tier="core", evidence_type="Mechanism / conceptual",
    citation="Diamond, R. (2016). The determinants and welfare implications of US workers' diverging location choices by skill: 1980-2000. American Economic Review, 106(3), 479-524.",
    doi="https://doi.org/10.1257/aer.20131706", status="Published (peer-reviewed)", geography="U.S. cities", years="1980-2000",
    data="Census microdata; city wages, rents, amenities", method="Structural spatial-equilibrium model",
    finding="College graduates increasingly sorted into high-wage, high-rent cities, driven by labour demand and reinforced by endogenous amenities.",
    limitations="City level; amenities endogenous to sorting.",
    relevance="Education sorting jointly shapes housing prices and local politics, so it is a prime common cause of the SDI-price correlation.",
    verified_against="Abstract (OpenAlex) + Crossref metadata")
add(id="moretti2013", tier="core", evidence_type="Mechanism / regional prices",
    citation="Moretti, E. (2013). Real wage inequality. American Economic Journal: Applied Economics, 5(1), 65-103.",
    doi="https://doi.org/10.1257/app.5.1.65", status="Published (peer-reviewed)", geography="U.S. metropolitan areas", years="1980-2000",
    data="Wages; location-specific CPI built mainly from housing costs", method="Deflation by local price index; GE model",
    finding="College graduates concentrated in high-housing-cost metros; at least 22% of the rise in the college premium is offset by spatial cost-of-living differences.",
    limitations="Local CPI dominated by housing costs.",
    relevance="Shows that local price levels differ mostly through housing. This guides the RPP extension: the question is whether SDI tracks housing specifically or prices generally.",
    verified_against="Abstract (OpenAlex) + Crossref metadata")
add(id="mummolo2017", tier="core", evidence_type="Related empirical (null / contrary)",
    citation="Mummolo, J., & Nall, C. (2017). Why partisans do not sort: The constraints on political segregation. Journal of Politics, 79(1), 45-59.",
    doi="https://doi.org/10.1086/687569", status="Published (peer-reviewed)", geography="United States", years="Survey experiments, 2010s",
    data="Original survey experiments; zip-code census and partisanship data", method="Stated preferences vs observed moves",
    finding="Democrats prefer more Democratic, dense, diverse places, but partisans are on average not migrating to more politically distinct communities; common concerns (cost, schools) dominate.",
    limitations="Neighbourhood scale; does not address state-level institutional sorting.",
    relevance="Contrary evidence: direct political sorting by residents is weak. Any institution-price link is more likely to run through education, income and urbanisation than through people moving for democratic quality.",
    verified_against="Abstract (OpenAlex) + Crossref metadata")

# ---------------------------------------------------------------- supply restrictions and politics
add(id="kahn2011", tier="core", evidence_type="Mechanism / supply and politics",
    citation="Kahn, M. E. (2011). Do liberal cities limit new housing development? Evidence from California. Journal of Urban Economics, 69(2), 223-228.",
    doi="https://doi.org/10.1016/j.jue.2010.10.001", status="Published (peer-reviewed)", geography="California cities", years="2000-2008",
    data="City-level permits; voter registration / ideology", method="Panel comparisons within metro areas",
    finding="Liberal cities grant fewer new housing permits than observationally similar cities; growth in liberal voter share goes with slower permit growth.",
    limitations="One state; city scale; ideology, not democratic quality.",
    relevance="Mechanism: political orientation correlates with supply restriction, and SDI correlates with Democratic control (Spearman 0.67 with 2022 party control in this data). This is a channel unrelated to democratic quality as such.",
    verified_against="Abstract (RePEc/IDEAS) + Crossref metadata")
add(id="hilber2013", tier="core", evidence_type="Mechanism / supply and politics",
    citation="Hilber, C. A. L., & Robert-Nicoud, F. (2013). On the origins of land use regulations: Theory and evidence from US metro areas. Journal of Urban Economics, 75, 29-43.",
    doi="https://doi.org/10.1016/j.jue.2012.10.002", status="Published (peer-reviewed)", geography="U.S. metropolitan areas", years="Not checked",
    data="Metro regulation index, development", method="Political-economy model; cross-metro evidence",
    finding="More desirable locations are more developed and, through owner political power, more regulated.",
    limitations="Cross-sectional; regulation measures imperfect.",
    relevance="Reverse-direction channel: high prices and desirability can produce political outcomes (regulation), so associations need not run from institutions to prices.",
    verified_against="Abstract (RePEc/IDEAS) + Crossref metadata")
add(id="glaeser2018", tier="core", evidence_type="Mechanism / supply and politics",
    citation="Glaeser, E., & Gyourko, J. (2018). The economic implications of housing supply. Journal of Economic Perspectives, 32(1), 3-30.",
    doi="https://doi.org/10.1257/jep.32.1.3", status="Published (review)", geography="United States", years="Review",
    data="Review of evidence; price vs construction cost", method="Cost-based approach to identify regulatory 'tax'",
    finding="Evidence suggests, without definitively proving, that the implicit regulatory tax exceeds plausible externalities in many areas; this affects wealth and migration to productive places.",
    limitations="Review; regulatory tax inferred.",
    relevance="Background: price levels across states reflect supply constraints that differ systematically by region and politics.",
    verified_against="Abstract (OpenAlex) + Crossref metadata")
add(id="ganong2017", tier="core", evidence_type="Mechanism / supply and migration",
    citation="Ganong, P., & Shoag, D. (2017). Why has regional income convergence in the U.S. declined? Journal of Urban Economics, 102, 76-90.",
    doi="https://doi.org/10.1016/j.jue.2017.07.002", status="Published (peer-reviewed); also NBER WP 23609", geography="U.S. states", years="Past ~30 years to 2010s",
    data="State incomes, migration, housing prices; new panel of land-use regulation", method="Model plus state panel evidence",
    finding="Rising housing prices in high-income states deter low-skill migration, contributing to the decline in income convergence.",
    limitations="Abstract-level reading only; state-level design details not checked.",
    relevance="State-level evidence that price levels shape who can move, a sorting channel that reinforces income and education gaps correlated with SDI.",
    verified_against="Abstract excerpts (RePEc/IDEAS) + Crossref metadata")

# ---------------------------------------------------------------- regional prices beyond housing
add(id="handbury2015", tier="core", evidence_type="Measurement / regional prices",
    citation="Handbury, J., & Weinstein, D. E. (2015). Goods prices and availability in cities. Review of Economic Studies, 82(1), 258-296.",
    doi="https://doi.org/10.1093/restud/rdu033", status="Published (peer-reviewed)", geography="49 U.S. cities", years="Barcode scanner data (years not checked)",
    data="Household barcode purchase data", method="Theoretically founded spatial price index correcting heterogeneity and variety bias",
    finding="Correcting for product heterogeneity removes 97% of cross-city variance in food price levels; with variety correction, food price levels fall with city size.",
    limitations="Food/grocery only.",
    relevance="Warns that measured goods-price gradients (like BEA's goods RPP, which relies on CPI quotes) may partly reflect product mix. This matters for reading the goods-RPP association.",
    verified_against="Abstract (OpenAlex) + Crossref metadata")

# ---------------------------------------------------------------- additional background (not core)
add(id="handbury2021", tier="additional", evidence_type="Measurement / regional prices",
    citation="Handbury, J. (2021). Are poor cities cheap for everyone? Non-homotheticity and the cost of living across U.S. cities. Econometrica, 89(6), 2679-2715.",
    doi="https://doi.org/10.3982/ECTA11738", status="Published (peer-reviewed)", geography="U.S. cities", years="Not checked",
    data="Grocery product data", method="Non-homothetic price indexes",
    finding="High-income households get about 40% more utility per dollar in wealthy cities relative to poor ones, mostly through product assortment rather than prices.",
    limitations="Grocery products.", relevance="Price-level comparisons depend on whose basket is priced; RPPs use a single average basket.",
    verified_against="Abstract (Crossref) + Crossref metadata")
add(id="saiz2010", tier="additional", evidence_type="Mechanism / supply",
    citation="Saiz, A. (2010). The geographic determinants of housing supply. Quarterly Journal of Economics, 125(3), 1253-1296.",
    doi="https://doi.org/10.1162/qjec.2010.125.3.1253", status="Published (peer-reviewed)", geography="U.S. metropolitan areas", years="Not checked",
    data="Satellite terrain and water data", method="Supply elasticity estimation", finding="Geography (steep slopes, water) severely constrains supply in inelastic metros; regulation is endogenous to prices and growth.",
    limitations="Metro level.", relevance="Coastal geography raises prices independently of institutions and correlates with SDI's regional pattern.",
    verified_against="Abstract (OpenAlex) + Crossref metadata")
add(id="hsieh2019", tier="additional", evidence_type="Mechanism / supply",
    citation="Hsieh, C.-T., & Moretti, E. (2019). Housing constraints and spatial misallocation. American Economic Journal: Macroeconomics, 11(2), 1-39.",
    doi="https://doi.org/10.1257/mac.20170388", status="Published (peer-reviewed)", geography="220 U.S. metropolitan areas", years="1964-2009",
    data="Metro wages and employment", method="Spatial equilibrium model", finding="Housing supply restrictions in high-productivity cities lowered aggregate U.S. growth substantially (36% over 1964-2009 in their model).",
    limitations="Model-dependent magnitude.", relevance="Background on why expensive states are expensive.",
    verified_against="Abstract (OpenAlex) + Crossref metadata")
add(id="trounstine2020", tier="additional", evidence_type="Mechanism / supply and politics",
    citation="Trounstine, J. (2020). The geography of inequality: How land use regulation produces segregation. American Political Science Review, 114(2), 443-455.",
    doi="https://doi.org/10.1017/S0003055419000844", status="Published (peer-reviewed)", geography="U.S. cities", years="1970-2006 and later",
    data="City land-use patterns; Fair Housing Act lawsuits; California precinct initiative votes", method="Panel and quasi-experimental designs",
    finding="Whiter communities support and use restrictive land-use rules, which preserve racial homogeneity and segregation.",
    limitations="City level.", relevance="Land-use politics, prices and civil-rights outcomes are jointly determined, which complicates any institution-to-price reading.",
    verified_against="Abstract (OpenAlex) + Crossref metadata")

# ---------------------------------------------------------------- measurement references
for rec in [
    dict(id="grumbach2023", citation="Grumbach, J. M. (2023). Laboratories of democratic backsliding. American Political Science Review, 117(3), 967-984.",
         doi="https://doi.org/10.1017/S0003055422000934", geography="50 U.S. states", years="2000-2018",
         data="51 indicators of electoral democracy (SDI 1.0)", method="Bayesian latent-variable index; difference-in-differences",
         finding="Develops the State Democracy Index; Republican control of state government substantially reduces democratic performance, while other factors play a minimal role.",
         limitations="SDI 1.0; 2.0 extends to 2023 with 54 indicators.",
         relevance="Source of the main measure; also shows partisan control drives SDI, so partisanship is a key common cause."),
    dict(id="rhodes2025", citation="Rhodes, J. H. (2025/2026). Laboratories of democratic renewal: explaining substantial improvement in the quality of democracy in the American states. Political Science Research and Methods, 14(4), 1269-1286.",
         doi="https://doi.org/10.1017/psrm.2025.10051", geography="50 U.S. states", years="2000-2022 (7 waves)",
         data="53-indicator Electoral Democracy Score", method="Bayesian factor analysis; Coincidence Analysis",
         finding="Substantial improvement in electoral democracy follows paths involving unions and Democratic Party control.",
         limitations="Published online 2025, issue dated 2026; not annual.", relevance="Alternative democracy index used as sensitivity S8."),
    dict(id="li2018", citation="Li, Q., Pomante, M. J., & Schraufnagel, S. (2018). Cost of voting in the American states. Election Law Journal, 17(3), 234-247.",
         doi="https://doi.org/10.1089/elj.2017.0478", geography="50 U.S. states", years="1996-2016 presidential years",
         data="33 election laws in 7 issue areas", method="Principal components; sensitivity analysis; turnout validation",
         finding="Constructs the COVI; higher index values are associated with lower aggregate and self-reported turnout.",
         limitations="Voting access only.", relevance="Voting-access measure (S9), conceptually narrower than electoral democracy."),
    dict(id="pomante2025", citation="Pomante, M. J. (2025). Cost of voting in the American states: 2024. Election Law Journal, 24(1), 52-61.",
         doi="https://doi.org/10.1089/elj.2024.0037", geography="50 U.S. states", years="2024",
         data="State election laws incl. a new absentee-signature item", method="COVI update",
         finding="Oregon most accessible, Mississippi most restrictive in 2024; increasing partisan polarisation in voting access.",
         limitations="Item set changes over editions.", relevance="Documents COVI methodology changes."),
    dict(id="caughey2016", citation="Caughey, D., & Warshaw, C. (2016). The dynamics of state policy liberalism, 1936-2014. American Journal of Political Science, 60(4), 899-913.",
         doi="https://doi.org/10.1111/ajps.12219", geography="U.S. states", years="1936-2014",
         data="148 policies", method="Dynamic latent-variable model",
         finding="First yearly measure of state policy liberalism; little evidence of multidimensionality in policy outputs.",
         limitations="-", relevance="SDI includes Caughey-Warshaw opinion-policy residuals, a potential shared input with LGBTQ policy measures."),
    dict(id="lax2009", citation="Lax, J. R., & Phillips, J. H. (2009). Gay rights in the states: Public opinion and policy responsiveness. American Political Science Review, 103(3), 367-386.",
         doi="https://doi.org/10.1017/S0003055409990050", geography="50 U.S. states", years="Mid-2000s",
         data="State opinion estimates (MRP) on eight LGBT policies", method="Responsiveness and congruence analysis",
         finding="State LGBT policy responds strongly to policy-specific opinion; noncongruence is common and biased conservative; little evidence that institutions condition responsiveness.",
         limitations="Earlier policy era.", relevance="LGBT legal equality largely reflects public opinion. This supports treating opinion and ideology as a common cause of equality, democracy scores and sorting."),
]:
    rec.update(tier="measurement", evidence_type="Measurement reference", status="Published (peer-reviewed)",
               verified_against="Abstract (OpenAlex) + Crossref metadata")
    add(**rec)


def main() -> None:
    df = pd.DataFrame(R)
    cols = ["id", "tier", "evidence_type", "citation", "doi", "status", "geography", "years", "data", "method",
            "finding", "limitations", "relevance", "verified_against"]
    df = df[cols]
    df.to_csv(OUT / "evidence_table.csv", index=False)
    lines = ["# Evidence table", "",
             "No study found directly examines U.S. state electoral-democracy indexes and housing prices, "
             "or state LGBTQ legal-equality indexes and housing prices. That is a statement about this search "
             "(see search_log.md), not a claim that none exists.", "",
             "Tiers: **core** = most useful for interpreting this project; **additional** = background; "
             "**measurement** = index documentation and validation.", ""]
    for tier in ["core", "additional", "measurement"]:
        sub = df[df.tier == tier]
        lines.append(f"## {tier.capitalize()} ({len(sub)})\n")
        lines.append(sub.drop(columns="tier").to_markdown(index=False))
        lines.append("")
    (OUT / "evidence_table.md").write_text("\n".join(lines), encoding="utf-8")
    print(df.groupby(["tier", "evidence_type"]).size())


if __name__ == "__main__":
    main()
