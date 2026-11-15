"""Run the whole pipeline in order.

Usage:  python scripts/run_all.py            (keeps existing raw files)
        python scripts/run_all.py --force    (re-downloads raw files; results may change with upstream revisions)
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
# 06_mover.py runs before the notebook because the notebook displays its outputs
STEPS = ["01_download.py", "02_build.py", "03_analysis.py", "06_mover.py", "04_notebook.py", "05_literature_tables.py"]

if __name__ == "__main__":
    extra = sys.argv[1:]
    for step in STEPS:
        args = [sys.executable, str(HERE / step)] + (extra if step == "01_download.py" else [])
        print(f"\n=== {step} ===", flush=True)
        subprocess.run(args, check=True)
