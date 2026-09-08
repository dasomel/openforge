#!/usr/bin/env python3
"""Deprecated compatibility entrypoint for the behavior-aware audit.

Use `audit-portfolio.py`; AGENT-004 is now registered canonically there.
"""

from __future__ import annotations

import runpy
from pathlib import Path

TARGET = Path(__file__).resolve().parent / "audit-portfolio.py"

if __name__ == "__main__":
    runpy.run_path(str(TARGET), run_name="__main__")
