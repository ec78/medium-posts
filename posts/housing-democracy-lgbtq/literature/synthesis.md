# Literature synthesis

Scope: what existing research says about electoral democracy, LGBTQ legal
equality and housing prices across U.S. states, and what it implies for
interpreting this project's correlations. The evidence table is in
[evidence_table.md](evidence_table.md), the search record in
[search_log.md](search_log.md), and the BibTeX file in
[bibliography.bib](bibliography.bib). All substantive claims below rest on
abstracts; no full texts were accessible.

## 1. Direct evidence: none found

The searches found **no study that relates a U.S. state electoral-democracy index
(SDI, Rhodes's EDS, COVI) to housing prices**, and **no study that relates a state
LGBTQ legal-equality index (MAP, HRC SEI) to housing prices**. The nearest
housing-politics work studies a different object. Nguyen & Vergara-Alert (2023)
use gubernatorial election timing as a source of political *uncertainty* and
find lower house-price growth and transactions in election years. That shows
state politics can register in housing markets, but it says nothing about
whether better-functioning electoral institutions are capitalised into prices.

Not finding a study is not evidence of novelty. Working papers, theses and
policy reports outside OpenAlex and Crossref may exist, and adjacent
literatures may already answer the question under other names (e.g. "quality
of life", "amenities", "policy liberalism").

## 2. LGBTQ-related evidence concerns people and attitudes, not laws

The two housing-price studies involving LGBT populations measure *who lives
where* and *local attitudes*, not legal protections:

* Christafore & Leguizamon (2012), one metro area: more same-sex coupled
  households go with higher prices in liberal neighbourhoods and lower prices
  in conservative ones (classified by a Defense of Marriage Act vote). The
  authors read this as evidence of prejudice.
* Florida & Mellander (2010): a combined "Bohemian-Gay Index" is positively
  related to regional housing values. It is also strongly correlated with
  income, which the authors describe as an indirect channel.

The migration evidence is attitudinal. In Baumle, Miller & Gregory (2023), restrictive
abortion and LGBT laws act more as deterrents than attractions for prospective
migrants, and political orientation predicts responses best. None of this
establishes that state LGBTQ *laws* change housing demand or prices.
Lax & Phillips (2009) show that state LGBT policy closely follows state public
opinion. Opinion and ideology are therefore natural common causes of
equality scores, democracy scores, sorting and prices.

## 3. Mechanisms that would generate the observed correlation without a democracy effect

**Spatial equilibrium and amenity capitalisation.** In Roback's (1982)
framework, anything residents value is capitalised into rents and land
prices. If people valued democratic or rights-protective institutions, prices
could carry a premium. But the same holds for every correlated amenity:
coastline, climate, density, universities. Albouy (2016) finds cross-metro
housing-cost differences are explained more by productivity than by quality
of life, and that the most valuable places are "coastal, sunny, mild,
educated, and large". These traits overlap heavily with high-SDI states.

**Sorting by education and income.** Diamond (2016) and Moretti (2013)
document college graduates concentrating in high-wage, high-rent places since
1980, with endogenous amenities reinforcing the pattern. Ganong & Shoag
(2017) show at the state level that high housing prices deter low-skill
migration into high-income states. Apart from the LGBTQ-equality measures,
education and income are among the strongest correlates of SDI in this
project's data (Pearson r = 0.58 and 0.57 in 2023). Controlling for them
removes most of the SDI-price association. That is consistent with sorting
as a shared background cause, though it does not prove it.

**Direct political sorting is weak.** Mummolo & Nall (2017) find that partisans
state different residential preferences but do not, on average, move to more
politically similar places, because cost, schools and similar concerns dominate. That
cuts against a direct "people move to more democratic states" channel.

**Supply restrictions and politics.** Liberal cities permit less new housing
(Kahn 2011). More desirable places become more regulated through
homeowner political power (Hilber & Robert-Nicoud 2013). Land-use politics
sustain segregation (Trounstine 2020). Geography and regulation together
make some metros inelastic (Saiz 2010; Glaeser & Gyourko 2018;
Gyourko, Mayer & Sinai 2013; Hsieh & Moretti 2019). Grumbach (2023) finds that
Republican control of state government is the main factor reducing SDI
scores, so party control is tied to SDI. A party-supply channel
could produce a positive SDI-price correlation unrelated to electoral democracy
itself. The causation can also run from prices to politics: in Hilber &
Robert-Nicoud's model, high prices create constituencies for regulation.

## 4. Housing-specific or broader prices?

In this project's BEA data, housing-rent price levels vary far more across
states than other components (2023 housing RPP 55-158, all-items 87-112).
Moretti (2013) likewise finds local cost-of-living differences dominated by
housing. Two cautions apply to the non-housing components:

* Handbury & Weinstein (2015) show that conventional spatial goods-price
  comparisons are badly biased by product heterogeneity and variety. Correcting
  for this removes 97% of cross-city variance in food prices and reverses the
  big-city premium.
* Handbury (2021) shows that what a dollar buys depends on the household's income-specific basket.

The goods RPP, built from CPI quotes, may therefore partly reflect product
mix. This project's goods-RPP association with SDI should be read with that in
mind.

## 5. Measurement

* **SDI** (Grumbach 2023; Grumbach & Bitton 2024) is an index of electoral
  institutions and administration, not of civil liberties broadly. Its inputs
  include MIT EPI items and Caughey-Warshaw opinion-policy residuals; Caughey &
  Warshaw (2016) measure state policy liberalism. If social-policy liberalism
  includes LGBT policies (not verified here), part of the SDI-equality
  overlap would be mechanical.
* **Rhodes's EDS** (2025) uses similar Bayesian factor analysis on 53
  indicators in 7 waves and shares many inputs with SDI.
* **COVI** (Li, Pomante & Schraufnagel 2018; Pomante 2025) measures the cost
  of voting only, and its item set changes over editions.
* **MAP and HRC** are advocacy-organisation tallies of LGBTQ-related *laws and
  policies*. Neither is a comprehensive human-rights index. The search found no
  peer-reviewed validation study of either index at the state level.

Because these indexes share sources, agreement among them is a sensitivity
check, not independent replication.

## 6. What this project adds, and what it does not

What the literature already supports: high-price states are high-income,
high-education, coastal, urban and supply-constrained, and these traits
predict both state politics and prices.

What this project adds is a transparent, reproducible description of three things:
1. How much of the SDI-home-value and LGBTQ-equality-home-value correlations
   is accounted for by income, education and urbanisation (most of it).
2. Whether the association exists *within* states over time (small and imprecise).
3. Whether it is specific to housing. It is not: across states the gradient is
   as strong for goods and all-items prices as for housing, and weaker but
   positive for utilities and other services.

It cannot say whether democracy or LGBTQ protections *cause* price
differences. Nothing here identifies a causal effect.
