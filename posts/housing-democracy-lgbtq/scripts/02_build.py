"""Clean, validate and merge raw sources into analysis-ready files.

Outputs (data/processed/):
    state_year_panel.csv     50 states x 2000-2024, all measures (missing where a source has no value)
    cross_section_2023.csv   the 2023 rows used in the main cross-section
    merge_log.csv            per-source rows, matches and year coverage
    map_policy_tally_2017_2024.csv   parsed MAP snapshots with as-of dates and maxima
    pce_price_index.csv      national PCE price index (DPCERG) used for deflation
    data_dictionary.csv/.md  column descriptions, units, sources, coverage

Usage:  python scripts/02_build.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd  # noqa: E402

from hdl import PROC  # noqa: E402
from hdl.build import build_panel, load_map, load_pce_price_index  # noqa: E402
from hdl.dictionary import write_dictionary  # noqa: E402


def main() -> None:
    panel, log = build_panel()
    panel.to_csv(PROC / "state_year_panel.csv", index=False, float_format="%.6g")
    panel[panel.year == 2023].to_csv(PROC / "cross_section_2023.csv", index=False, float_format="%.6g")
    pd.DataFrame(log).to_csv(PROC / "merge_log.csv", index=False)
    load_map().to_csv(PROC / "map_policy_tally_2017_2024.csv", index=False, float_format="%.6g")
    load_pce_price_index().to_csv(PROC / "pce_price_index.csv", index=False)
    write_dictionary(panel, PROC / "data_dictionary.csv", PROC / "data_dictionary.md")

    print(pd.DataFrame(log).to_string(index=False))
    print(f"\npanel: {panel.shape[0]} rows, {panel.st.nunique()} states, years {panel.year.min()}-{panel.year.max()}")
    cov = panel.groupby("year")[["sdi", "zhvi", "rpp_all", "eds", "covi", "map_overall", "hrc_category",
                                  "acs_value"]].count()
    print("\nnon-missing state counts by year:\n", cov.to_string())


if __name__ == "__main__":
    main()
