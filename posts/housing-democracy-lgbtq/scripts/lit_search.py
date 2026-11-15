"""Run logged scholarly searches against the OpenAlex API.

Each query, its date, and the top hits (title, year, venue, DOI, citation
count) are appended to literature/search_results_openalex.jsonl so the search
log can be reproduced. OpenAlex is a free scholarly index (https://openalex.org).

Usage:  python scripts/lit_search.py
"""
from __future__ import annotations

import datetime as dt
import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "literature" / "search_results_openalex.jsonl"
HEADERS = {"User-Agent": "housing-democracy-lgbtq research script"}

# (topic code, query string). Topic codes follow the six literature strands
# plus R = regional prices / spatial equilibrium.
QUERIES = [
    ("1", "state democracy housing prices United States"),
    ("1", "electoral democracy index states property values"),
    ("1", "voting rights restrictions house prices"),
    ("1", "political institutions housing prices states"),
    ("2", "LGBT nondiscrimination law house prices"),
    ("2", "same-sex marriage legalization housing prices"),
    ("2", "gay lesbian households house prices"),
    ("2", "anti-LGBT laws migration intentions states"),
    ("2", "gay men location choice amenities"),
    ("2", "sexual minority migration state policy"),
    ("3", "civil rights laws capitalization property values"),
    ("3", "amenity capitalization housing prices quality of life"),
    ("4", "partisan residential sorting migration"),
    ("4", "skill sorting cities housing prices divergence"),
    ("5", "liberal cities housing supply restrictions"),
    ("5", "land use regulation political ideology"),
    ("5", "housing supply elasticity regulation"),
    ("6", "state democracy index measurement validation"),
    ("6", "cost of voting index states"),
    ("6", "state LGBT policy index measurement"),
    ("6", "state policy liberalism dynamics measurement"),
    ("R", "regional price parities states cost of living"),
    ("R", "goods prices cities variety cost of living"),
    ("R", "real wage inequality local prices housing"),
]


def search(q: str, n: int = 12) -> list[dict]:
    r = requests.get(
        "https://api.openalex.org/works",
        params={"search": q, "per-page": n, "sort": "relevance_score:desc"},
        headers=HEADERS,
        timeout=60,
    )
    r.raise_for_status()
    hits = []
    for w in r.json()["results"]:
        src = (w.get("primary_location") or {}).get("source") or {}
        hits.append(
            {
                "title": w.get("display_name"),
                "year": w.get("publication_year"),
                "venue": src.get("display_name"),
                "doi": w.get("doi"),
                "type": w.get("type"),
                "cited_by": w.get("cited_by_count"),
            }
        )
    return hits


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    with OUT.open("w", encoding="utf-8") as f:
        for topic, q in QUERIES:
            hits = search(q)
            f.write(json.dumps({"date": today, "source": "OpenAlex", "topic": topic,
                                "query": q, "hits": hits}) + "\n")
            print(f"\n[{topic}] {q}")
            for h in hits:
                print(f"   {h['year']} | {h['cited_by']:>5} | {str(h['title'])[:95]} | {h['venue']} | {h['doi']}")
            time.sleep(0.3)


if __name__ == "__main__":
    main()
