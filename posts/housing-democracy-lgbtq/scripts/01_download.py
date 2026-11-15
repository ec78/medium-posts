"""Download every raw source file and write data/raw/MANIFEST.csv.

Each entry records the URL, local path, access date, byte size and SHA-256 so
later runs can detect silent upstream revisions. Existing files are kept
unless --force is passed (upstream files are revised; re-downloading changes
results, so it is opt-in).

No API keys, logins, payments or data requests are used. The Census API now
requires a key, so ACS values come from the keyless table-based summary
files on www2.census.gov instead.

Usage:
    python scripts/01_download.py            # fetch missing files only
    python scripts/01_download.py --force    # re-fetch everything
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import time
import zipfile
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
UA = {"User-Agent": "Mozilla/5.0 (housing-democracy-lgbtq research script)"}

ACS_BASE = "https://www2.census.gov/programs-surveys/acs/summary_file/{y}/table-based-SF/data/1YRData/acsdt1y{y}-{t}.dat"
WAYBACK = "https://web.archive.org/web/{ts}id_/https://www.lgbtmap.org/equality-maps/"
DATAVERSE = "https://dataverse.harvard.edu/api/access/datafile/{fid}?format=original"

# Wayback Machine captures of MAP's "Equality Maps" policy-tally table.
# Timestamps were located with the archive.org availability API, targeting
# 1 July of each year. 2015 and 2016 captures exist but contain no tally table.
MAP_SNAPSHOTS = [
    "20150626224545", "20160701053248", "20170708060434", "20180622142207",
    "20190627161037", "20200702181641", "20210630211544", "20220703183400",
    "20230701105242", "20240702040323",
]

# (local path relative to data/raw, url, redistribution note)
SOURCES: list[tuple[str, str, str]] = [
    # Electoral democracy
    ("sdi/SDI_2.0.csv", "https://democracypolicylab.berkeley.edu/wp-content/uploads/2025/01/SDI_2.0.csv",
     "No license stated; not redistributed (download script only)"),
    ("sdi/variables_list.csv", "https://democracypolicylab.berkeley.edu/wp-content/uploads/2024/12/variables_list.csv",
     "No license stated; not redistributed"),
    ("sdi/SDI-2.0-Report.pdf", "https://democracypolicylab.berkeley.edu/wp-content/uploads/2024/12/SDI-2.0-Report.pdf",
     "No license stated; not redistributed"),
    ("rhodes/democracy_dataset.csv", DATAVERSE.format(fid=11946564), "CC0 1.0 (Harvard Dataverse doi:10.7910/DVN/NXULWY)"),
    ("rhodes/dem-control.tab", DATAVERSE.format(fid=11946570), "CC0 1.0 (Harvard Dataverse doi:10.7910/DVN/NXULWY)"),
    ("rhodes/README.rtf", DATAVERSE.format(fid=11946534), "CC0 1.0"),
    ("rhodes/replication.R", DATAVERSE.format(fid=11946555), "CC0 1.0"),
    ("covi/COVI_Values_1996-2024.xlsx",
     "https://img1.wsimg.com/blobby/go/6390118f-6ee4-4460-a245-79d1f8be7ec6/downloads/"
     "b11df6a2-164a-422e-9823-98015a03d011/COVI%20Values%201996-2024%20website.xlsx?ver=1783966107770",
     "No license stated; not redistributed. URL is versioned and may change; see costofvotingindex.com/data"),
    # Housing
    ("zillow/State_zhvi.csv",
     "https://files.zillowstatic.com/research/public_csvs/zhvi/State_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
     "Zillow Terms of Use; attribution required; not redistributed"),
    ("zillow/County_zhvi.csv",
     "https://files.zillowstatic.com/research/public_csvs/zhvi/County_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv",
     "Zillow Terms of Use; attribution required; not redistributed"),
    ("freddiemac/historicalweeklydata.xlsx", "https://www.freddiemac.com/pmms/docs/historicalweeklydata.xlsx",
     "Freddie Mac PMMS; terms of use apply; not redistributed (annual mean kept in data/processed)"),
    ("fhfa/HPI_AT_state.csv", "https://www.fhfa.gov/hpi/download/quarterly_datasets/hpi_at_state.csv",
     "U.S. government work (public domain)"),
    # Prices, income (BEA)
    ("bea/SARPP.zip", "https://apps.bea.gov/regional/zip/SARPP.zip", "U.S. government work (public domain)"),
    ("bea/SAINC.zip", "https://apps.bea.gov/regional/zip/SAINC.zip",
     "Public domain; large (17 MB) so only SAINC1 is extracted and kept in git"),
    ("bea/NipaDataA.txt", "https://apps.bea.gov/national/Release/TXT/NipaDataA.txt",
     "Public domain; large (12 MB); not kept in git (only the extracted PCE price index is)"),
    ("bea/Methodology-for-Regional-Price-Parities.pdf",
     "https://www.bea.gov/sites/default/files/methodologies/Methodology-for-Regional-Price-Parities_0.pdf",
     "Public domain"),
    # Controls (Census)
    ("census_urban/2020_UA_COUNTY.xlsx", "https://www2.census.gov/geo/docs/reference/ua/2020_UA_COUNTY.xlsx",
     "Public domain; large (10 MB); not kept in git"),
    ("census_urban/CenPop2020_Mean_ST.txt", "https://www2.census.gov/geo/docs/reference/cenpop2020/CenPop2020_Mean_ST.txt",
     "Public domain"),
    # LGBTQ legal equality
    ("hrc/sei2023_press_release.html",
     "https://www.hrc.org/press-releases/new-hrc-state-equality-index-shows-devastating-impact-of-radical-anti-lgbtq-2023-state-legislative-season",
     "HRC copyright; not redistributed (category lists transcribed in data/processed)"),
]
for y in (2022, 2023):
    for t in ("b25077", "b19013", "b15003", "b01003"):
        SOURCES.append((f"acs/acsdt1y{y}-{t}.dat", ACS_BASE.format(y=y, t=t), "Public domain"))
# Mover's-eye extension (2023 only): income quintile limits, median gross rent, real-estate taxes
for t in ("b19080", "b25064", "b25103"):
    SOURCES.append((f"acs/acsdt1y2023-{t}.dat", ACS_BASE.format(y=2023, t=t), "Public domain"))
for ts in MAP_SNAPSHOTS:
    SOURCES.append((f"map/wb_{ts[:8]}_equality_maps.html", WAYBACK.format(ts=ts),
                    "MAP copyright, archived by Internet Archive; not redistributed"))


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    for attempt in range(3):
        try:
            r = requests.get(url, headers=UA, timeout=180)
            r.raise_for_status()
            dest.write_bytes(r.content)
            return
        except requests.RequestException as e:
            if attempt == 2:
                raise RuntimeError(f"failed to download {url}: {e}") from e
            time.sleep(3 * (attempt + 1))


def extract() -> None:
    """Unpack the BEA zips into sub-folders (only the tables we use)."""
    with zipfile.ZipFile(RAW / "bea/SARPP.zip") as z:
        z.extractall(RAW / "bea/sarpp")
    with zipfile.ZipFile(RAW / "bea/SAINC.zip") as z:
        for n in z.namelist():
            if n.startswith("SAINC1__"):
                z.extract(n, RAW / "bea/sainc")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    manifest_path = RAW / "MANIFEST.csv"
    previous = {}
    if manifest_path.exists():
        with manifest_path.open(newline="", encoding="utf-8") as f:
            previous = {row["path"]: row for row in csv.DictReader(f)}

    rows = []
    for rel, url, note in SOURCES:
        dest = RAW / rel
        if args.force or not dest.exists():
            print("downloading", rel)
            fetch(url, dest)
            accessed = dt.date.today().isoformat()
        else:
            accessed = previous.get(rel, {}).get("accessed") or dt.date.fromtimestamp(dest.stat().st_mtime).isoformat()
        rows.append({"path": rel, "url": url, "accessed": accessed, "bytes": dest.stat().st_size,
                     "sha256": sha256(dest), "redistribution": note})
    extract()
    with manifest_path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {manifest_path.relative_to(ROOT)} ({len(rows)} files)")


if __name__ == "__main__":
    main()
