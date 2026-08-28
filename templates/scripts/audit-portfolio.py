#!/usr/bin/env python3
"""Canonical OpenForge Portfolio Compliance Auditor entrypoint.

The stable implementation lives in audit-core.py. Canonical metric extensions
are registered here before the CLI or library API is exposed.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CORE = HERE / "audit-core.py"

spec = importlib.util.spec_from_file_location("openforge_audit_core", CORE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load audit core: {CORE}")
core = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = core
spec.loader.exec_module(core)

from agent_behavior_metric import register as register_agent_behavior_metric
from agent_operational_metric import register as register_agent_operational_metric

register_agent_behavior_metric(core)
register_agent_operational_metric(core)


def __getattr__(name: str):
    return getattr(core, name)


if __name__ == "__main__":
    core.main()
