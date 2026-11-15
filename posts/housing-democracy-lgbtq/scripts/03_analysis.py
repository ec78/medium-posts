"""Run all pre-specified analyses; writes output/tables and output/figures.

Usage:  python scripts/03_analysis.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from hdl.analysis import run_all  # noqa: E402

if __name__ == "__main__":
    res = run_all()
    print("figures:", *res["figures"], sep="\n  ")
