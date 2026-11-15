"""Mover's-eye extension: affordability matrix and cheapest entry points (2023).

Usage:  python scripts/06_mover.py   (after 02_build.py)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hdl.mover import run_mover  # noqa: E402

if __name__ == "__main__":
    res = run_mover()
    print(f"2023 mean 30-yr rate: {res['rate']:.2f}%")
    print("origins:", " ".join(res["origins"]))
    print("destinations:", " ".join(res["destinations"]))
    print("figures:", *res["figures"], sep="\n  ")
