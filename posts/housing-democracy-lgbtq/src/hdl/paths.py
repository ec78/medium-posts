"""Project-relative paths. Everything is resolved from this file, so code runs
from any working directory."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
PROC = ROOT / "data" / "processed"
FIG = ROOT / "output" / "figures"
TAB = ROOT / "output" / "tables"

for _p in (PROC, FIG, TAB):
    _p.mkdir(parents=True, exist_ok=True)
