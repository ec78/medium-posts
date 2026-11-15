"""Verify bibliographic details of candidate studies against Crossref and
fetch abstracts from OpenAlex.

Output: literature/verified_metadata.json (one record per DOI with the
Crossref title/authors/journal/volume/issue/pages/year and, where OpenAlex
has one, the reconstructed abstract). The evidence table is written by hand
from these records plus full texts where accessible; this script only makes
the bibliographic check reproducible.

Usage:  python scripts/lit_verify.py
"""
from __future__ import annotations

import datetime as dt
import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "literature" / "verified_metadata.json"
HEADERS = {"User-Agent": "housing-democracy-lgbtq research script"}

CANDIDATE_DOIS = [
    # direct / related empirical
    "10.1016/j.jue.2011.09.004",   # Christafore & Leguizamon 2012
    "10.1093/jeg/lbp022",          # Florida & Mellander 2010
    "10.1006/juec.2001.2237",      # Black, Gates, Sanders, Taylor 2002
    "10.1016/j.jhe.2023.101952",   # Political uncertainty and housing markets
    "10.1007/s11113-023-09842-7",  # Baumle, Miller, Gregory 2023
    # supply / politics
    "10.1016/j.jue.2010.10.001",   # Kahn 2011 liberal cities
    "10.1016/j.jue.2012.10.002",   # Hilber & Robert-Nicoud 2013
    "10.1017/S0003055419000844",   # Trounstine 2020
    "10.1257/jep.32.1.3",          # Glaeser & Gyourko 2018
    "10.1162/qjec.2010.125.3.1253",# Saiz 2010
    "10.1257/mac.20170388",        # Hsieh & Moretti 2019
    "10.1016/j.jue.2017.07.002",   # Ganong & Shoag 2017
    "10.1016/j.jue.2021.103337",   # Gyourko, Hartley, Krimmel 2021
    # spatial equilibrium / amenities / prices
    "10.1086/261120",              # Roback 1982
    "10.1162/REST_a_00550",        # Albouy 2016
    "10.1257/pol.5.4.167",         # Gyourko, Mayer, Sinai 2013
    "10.1257/aer.20131706",        # Diamond 2016
    "10.1257/app.5.1.65",          # Moretti 2013
    "10.1093/restud/rdu033",       # Handbury & Weinstein 2015
    "10.3982/ECTA11738",           # Handbury 2021 Econometrica
    # sorting
    "10.1086/687569",              # Mummolo & Nall 2017
    "10.1016/j.polgeo.2014.11.003",# Gimpel & Hui 2015
    "10.1038/s41562-021-01066-z",  # Brown & Enos 2021
    # measurement
    "10.1017/S0003055422000934",   # Grumbach 2023
    "10.1017/psrm.2025.10051",     # Rhodes 2025
    "10.1089/elj.2017.0478",       # Li, Pomante, Schraufnagel 2018
    "10.1089/elj.2024.0037",       # COVI 2024
    "10.1111/ajps.12219",          # Caughey & Warshaw 2016
    "10.1017/S0003055409990050",   # Lax & Phillips 2009
]


def crossref(doi: str) -> dict | None:
    r = requests.get(f"https://api.crossref.org/works/{doi}", headers=HEADERS, timeout=60)
    if r.status_code != 200:
        return None
    m = r.json()["message"]
    year = None
    for key in ("published-print", "published-online", "issued"):
        if m.get(key, {}).get("date-parts"):
            year = m[key]["date-parts"][0][0]
            break
    return {
        "title": (m.get("title") or [None])[0],
        "authors": [f"{a.get('family','')}, {a.get('given','')}".strip(", ") for a in m.get("author", [])],
        "journal": (m.get("container-title") or [None])[0],
        "volume": m.get("volume"),
        "issue": m.get("issue"),
        "pages": m.get("page"),
        "year": year,
        "type": m.get("type"),
        "publisher": m.get("publisher"),
    }


def openalex_abstract(doi: str) -> str | None:
    r = requests.get(f"https://api.openalex.org/works/https://doi.org/{doi}", headers=HEADERS, timeout=60)
    if r.status_code != 200:
        return None
    inv = r.json().get("abstract_inverted_index")
    if not inv:
        return None
    pos = sorted((p, w) for w, ps in inv.items() for p in ps)
    return " ".join(w for _, w in pos)


def s2_abstract(doi: str) -> str | None:
    """Fallback abstract source: Semantic Scholar Graph API."""
    try:
        r = requests.get(f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}",
                         params={"fields": "abstract,tldr"}, headers=HEADERS, timeout=60)
        if r.status_code == 200:
            return r.json().get("abstract")
    except requests.RequestException:
        return None
    return None


def main() -> None:
    today = dt.date.today().isoformat()
    records = []
    for doi in CANDIDATE_DOIS:
        cr = crossref(doi)
        ab = openalex_abstract(doi) if cr else None
        src = "openalex" if ab else None
        if cr and not ab:
            time.sleep(1.2)
            ab = s2_abstract(doi)
            src = "semanticscholar" if ab else None
        records.append({"doi": doi, "checked": today, "crossref": cr, "abstract": ab, "abstract_source": src})
        status = "OK " if cr else "MISSING"
        print(status, doi, "|", (cr or {}).get("year"), "|", str((cr or {}).get("title"))[:80],
              "|", "abstract" if ab else "no-abstract")
        time.sleep(0.2)
    OUT.write_text(json.dumps(records, indent=1, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
