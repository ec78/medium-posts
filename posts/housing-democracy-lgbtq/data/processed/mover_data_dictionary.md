# Data dictionary: mover extension files (2023)

Built by `scripts/06_mover.py`; spec in docs/analysis_plan.md (Mover's-eye extension). County ZHVI values are derived from Zillow data (attribution required; see STATUS.md).

## entry_points_2023.csv (50 rows)

| column             | description                                                                                         |   non_missing |
|:-------------------|:----------------------------------------------------------------------------------------------------|--------------:|
| st                 | State postal code                                                                                   |            50 |
| n_counties         | Counties (2020 Census county file)                                                                  |            50 |
| n_counties_zhvi    | Counties with a 2023 county ZHVI                                                                    |            50 |
| zhvi_pop_coverage  | Share of 2020 state population in counties with a county ZHVI                                       |            50 |
| entry_p10          | E-P10: population-weighted 10th percentile of 2023 county ZHVI (USD)                                |            50 |
| entry_100k         | E-100k: lowest 2023 county ZHVI among counties with 2020 population >= 100,000 (USD)                |            50 |
| entry_100k_county  | County name for E-100k (Zillow name)                                                                |            50 |
| entry_100k_pop2020 | 2020 population of that county                                                                      |            50 |
| entry_min          | E-min: lowest 2023 county ZHVI in the state (USD)                                                   |            50 |
| entry_min_county   | County name for E-min                                                                               |            50 |
| entry_min_pop2020  | 2020 population of that county                                                                      |            50 |
| zhvi               | State ZHVI 2023, annual mean (USD)                                                                  |            50 |
| group              | origin = bottom third on both SDI and MAP (2023); destination = top third on both; other            |            50 |
| p20                | ACS 2023 household income, 20th percentile (B19080 line 1, USD)                                     |            50 |
| p40                | ACS 2023 household income, 40th percentile (B19080 line 2, USD)                                     |            50 |
| p60                | ACS 2023 household income, 60th percentile (B19080 line 3, USD)                                     |            50 |
| p80                | ACS 2023 household income, 80th percentile (B19080 line 4, USD)                                     |            50 |
| median             | ACS 2023 median household income (B19013, USD)                                                      |            50 |
| rent               | ACS 2023 median gross rent, state (B25064, USD/month, includes utilities)                           |            50 |
| tax_rate           | Effective property-tax rate = ACS B25103 median real-estate taxes / B25077 median value             |            50 |
| rent_entry_100k    | Lowest ACS 2023 county median gross rent among counties with 2023 population >= 100,000 (USD/month) |            50 |
| rent_entry_cfips   | County FIPS for rent_entry_100k (2023 geography; CT planning regions)                               |            50 |
| rent_entry_pop2023 | ACS 2023 population of that county                                                                  |            50 |
| sdi                | SDI 2.0, 2023                                                                                       |            50 |
| map_overall        | MAP overall tally, 2023                                                                             |            50 |

## county_zhvi_2023.csv (3,142 rows)

| column      | description                                              |   non_missing |
|:------------|:---------------------------------------------------------|--------------:|
| cfips       | 5-digit county FIPS (2020 geography)                     |          3142 |
| fips        | 2-digit state FIPS                                       |          3142 |
| COUNTY_NAME | Census county name                                       |          3142 |
| pop2020     | 2020 Census county population                            |          3142 |
| st          | State postal code                                        |          3142 |
| RegionName  | Zillow county name                                       |          3062 |
| zhvi        | State ZHVI 2023, annual mean (USD)                       |          3062 |
| zhvi_months | Months of 2023 with a county ZHVI value (>= 10 required) |          3062 |

## mover_matrix_2023.csv (12,500 rows)

| column                    | description                                                                                               |   non_missing |
|:--------------------------|:----------------------------------------------------------------------------------------------------------|--------------:|
| origin                    | Origin state                                                                                              |         12500 |
| income_level              | Origin income percentile (p20, p40, median, p60, p80)                                                     |         12500 |
| origin_income             | Origin-state household income at that level (USD/year)                                                    |         12500 |
| dest                      | Destination state                                                                                         |         12500 |
| zhvi                      | State ZHVI 2023, annual mean (USD)                                                                        |         12500 |
| entry_p10                 | E-P10: population-weighted 10th percentile of 2023 county ZHVI (USD)                                      |         12500 |
| entry_100k                | E-100k: lowest 2023 county ZHVI among counties with 2020 population >= 100,000 (USD)                      |         12500 |
| rent                      | ACS 2023 median gross rent, state (B25064, USD/month, includes utilities)                                 |         12500 |
| rent_entry_100k           | Lowest ACS 2023 county median gross rent among counties with 2023 population >= 100,000 (USD/month)       |         12500 |
| tax_rate                  | Effective property-tax rate = ACS B25103 median real-estate taxes / B25077 median value                   |         12500 |
| dest_median_income        | Destination median household income (USD/year)                                                            |         12500 |
| pti_median                | Destination ZHVI / origin income                                                                          |         12500 |
| owner_share_median        | Monthly P&I (10% down, 30-yr, 2023 PMMS mean) + property tax at destination ZHVI, / origin monthly income |         12500 |
| down_median               | 10% down payment at destination ZHVI (USD)                                                                |         12500 |
| pti_p10                   | Destination E-P10 / origin income                                                                         |         12500 |
| owner_share_p10           | Same, at destination E-P10                                                                                |         12500 |
| down_p10                  | 10% down payment at E-P10 (USD)                                                                           |         12500 |
| pti_100k                  | Destination E-100k / origin income                                                                        |         12500 |
| owner_share_100k          | Same, at destination E-100k                                                                               |         12500 |
| down_100k                 | 10% down payment at E-100k (USD)                                                                          |         12500 |
| owner_share_median_20down | Same as owner_share_median with 20% down                                                                  |         12500 |
| rent_share_median         | Destination state median gross rent x 12 / origin income                                                  |         12500 |
| rent_share_entry          | Destination rent_entry_100k x 12 / origin income                                                          |         12500 |
| owner_share_local         | owner_share_median computed on the destination's own median income (local-earner reference)               |         12500 |
| origin_group              | group of the origin state                                                                                 |         12500 |
| dest_group                | group of the destination state                                                                            |         12500 |
