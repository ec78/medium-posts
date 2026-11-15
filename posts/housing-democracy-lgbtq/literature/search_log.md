# Literature search log

**Search dates:** 2026-11-06 to 2026-11-08.

## Sources searched

| Source | How | Notes |
|---|---|---|
| OpenAlex (scholarly index) | `scripts/lit_search.py`, 24 logged queries, top 12 hits each, relevance-sorted | Raw hits in `search_results_openalex.jsonl` |
| Crossref API | `scripts/lit_verify.py`, DOI lookups and `query.bibliographic` title searches | Verifies authors, title, journal, volume, issue, pages, year |
| OpenAlex / Semantic Scholar / Crossref abstracts | `scripts/lit_verify.py` | Semantic Scholar returned HTTP 429 (rate limit) for most requests |
| RePEc / IDEAS, publisher and university pages | Manual fetch | Abstracts for Christafore & Leguizamon, Kahn, Hilber & Robert-Nicoud, Ganong & Shoag, Florida & Mellander (OUP page), Baumle et al. (University of Houston page) |
| General web search | 6 queries | Used to locate candidates and dataset documentation only; never cited as evidence |
| Official dataset documentation | Provider pages and PDFs | SDI 2.0 report, BEA RPP methodology (July 2025), MAP data-request page, HRC press release, Rhodes replication README and R script |

Access limits: ScienceDirect, Springer and Nature pages returned HTTP 403 or login redirects, so **no full texts were read**. Every finding in the evidence table is based on the abstract only, unless the table says otherwise. ICPSR study pages returned HTTP 403.

## Queries (OpenAlex)

Topic codes: 1 democracy and housing; 2 LGBTQ protections and housing, migration or location; 3 institutions, civil rights and amenity capitalisation; 4 sorting; 5 supply restrictions and politics; 6 measurement; R regional prices.

| Topic | Query |
|---|---|
| 1 | state democracy housing prices United States |
| 1 | electoral democracy index states property values |
| 1 | voting rights restrictions house prices |
| 1 | political institutions housing prices states |
| 2 | LGBT nondiscrimination law house prices |
| 2 | same-sex marriage legalization housing prices |
| 2 | gay lesbian households house prices |
| 2 | anti-LGBT laws migration intentions states |
| 2 | gay men location choice amenities |
| 2 | sexual minority migration state policy |
| 3 | civil rights laws capitalization property values |
| 3 | amenity capitalization housing prices quality of life |
| 4 | partisan residential sorting migration |
| 4 | skill sorting cities housing prices divergence |
| 5 | liberal cities housing supply restrictions |
| 5 | land use regulation political ideology |
| 5 | housing supply elasticity regulation |
| 6 | state democracy index measurement validation |
| 6 | cost of voting index states |
| 6 | state LGBT policy index measurement |
| 6 | state policy liberalism dynamics measurement |
| R | regional price parities states cost of living |
| R | goods prices cities variety cost of living |
| R | real wage inequality local prices housing |

Additional targeted OpenAlex queries: "Why do gay men live in San Francisco"; "restrictive abortion LGBTQ laws migration deterrence states"; "anti-transgender legislation migration intentions"; "state LGBTQ policy index validity measurement Movement Advancement Project".

Crossref title searches: "Do liberal cities limit new housing development Evidence from California Kahn"; "state abortion LGBTQ laws migration preferences Population Research and Policy Review"; "anti-LGBTQ laws interstate migration labor".

Web searches (candidate discovery only): "state democracy index housing prices U.S. states association study"; "LGBT nondiscrimination laws effect on house prices or migration U.S. states empirical study"; "Christafore Leguizamon ..."; "Florida Mellander 'There goes the metro' ..."; "ICPSR Movement Advancement Project ..."; "HRC State Equality Index report years ...".

## Results

* **Direct evidence (state democracy index and housing prices; state LGBTQ legal-equality index and housing prices):** none found. The closest housing-politics study is Nguyen & Vergara-Alert (2023) on election-year uncertainty. The closest LGBTQ-housing studies concern neighbourhood population composition and attitudes (Christafore & Leguizamon 2012; Florida & Mellander 2010), not state law. This is a result of these searches, not proof that no such study exists. Working papers, dissertations and non-indexed reports may have been missed.
* **Null or contrary evidence kept:** Mummolo & Nall (2017) find that partisans do not, on average, move to more politically similar places. That cuts against a simple "people move to democratic or LGBTQ-protective states and bid up prices" story.
* **Index quality vs. mechanisms:** most relevant mechanism literature is about metros (spatial equilibrium, supply). Applying it to states is an inference.

## Identified but not included in the evidence table

| Study | Reason |
|---|---|
| Black, Gates, Sanders & Taylor (2002), "Why do gay men live in San Francisco?", *JUE* 51(1): 54-76, doi:10.1006/juec.2001.2237 | Metadata verified; abstract not accessible (publisher elided, 403). Its argument (location sorting tied to amenities and household structure) is relevant background, but claims could not be checked. |
| Gimpel & Hui (2015), *Political Geography* 48: 130-142 | Metadata verified; abstract not retrieved |
| Brown & Enos (2021), *Nature Human Behaviour* 5(8): 998-1008 | Metadata verified; abstract not retrieved |
| Gyourko, Hartley & Krimmel (2021), Wharton index, *JUE* 124: 103337 | Metadata verified; abstract not retrieved; regulation measurement, not needed for the state-level analysis |
| Nikolaou (2022), *Southern Economic Journal*, same-sex marriage laws, hate crimes and employment discrimination | Off-topic outcome (not housing or migration) |
| "State Political Uncertainty and Local Housing Markets" (AEA 2023 conference listing) | Appears to be the working-paper version of Nguyen & Vergara-Alert (2023); not separately verified |
| Redfin (2024) report on homes in states with LGBTQ housing protections | Industry descriptive report; not scholarly |
| Trevor Project research brief on state policy and youth relocation | Advocacy research brief; correlational; not reviewed |
| Cross-national democracy/V-Dem measurement papers returned by searches | Different unit (countries) |
