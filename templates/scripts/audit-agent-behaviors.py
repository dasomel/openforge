#!/usr/bin/env python3
"""Behavior-aware OpenForge portfolio audit entrypoint.

This extension loads the canonical audit engine, registers AGENT-004, and then
runs the existing CLI unchanged. It keeps the behavior profile opt-in: projects
without `.agents/behaviors/` receive N/A rather than a compliance penalty.
"""

from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


HERE = Path(__file__).resolve().parent
CORE = HERE / "audit-portfolio.py"

spec = importlib.util.spec_from_file_location("openforge_portfolio_audit", CORE)
if spec is None or spec.loader is None:
    raise RuntimeError(f"Unable to load audit engine: {CORE}")
core = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = core
spec.loader.exec_module(core)

AGENT_004: Dict[str, Any] = {
    "id": "AGENT-004",
    "area": "Agent Engineering",
    "name": "Agent Behavior Specification Profile",
    "target": "Adopted .agents/behaviors/*/BEHAVIOR.md specs have valid frontmatter and directory/name consistency",
    "default_weight": 1,
    "related_adr": "ADR-0009",
    "related_standard": "docs/agent-behaviors.md",
    "priority": "P2",
}


def _parse_behavior_frontmatter(content: str) -> Tuple[Dict[str, str], List[str]]:
    errors: List[str] = []
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, ["missing opening YAML frontmatter delimiter"]

    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return {}, ["missing closing YAML frontmatter delimiter"]

    frontmatter: Dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            errors.append(f"invalid frontmatter line: {line.strip()}")
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip('"\'')

    for required in ("name", "description"):
        if not frontmatter.get(required):
            errors.append(f"missing required frontmatter field: {required}")
    return frontmatter, errors


def _eval_agent_004(self: Any, metric: Dict[str, Any]) -> None:
    behavior_files = sorted(set(self._find_files(".agents/behaviors/*/BEHAVIOR.md")))
    behavior_root = self.full_path / ".agents" / "behaviors"

    if not behavior_root.exists():
        self._add_check(metric, "N/A", "Agent Behavior profile not adopted", "", "Optional adoption-level control")
        return

    if not behavior_files:
        self._add_check(
            metric,
            0,
            "Behavior profile directory exists but contains no BEHAVIOR.md specs",
            "Add at least one .agents/behaviors/<name>/BEHAVIOR.md or remove the unused profile directory.",
            "docs/agent-behaviors.md",
        )
        return

    failures: List[str] = []
    for rel_path in behavior_files:
        content = self._read_file_safe(rel_path)
        frontmatter, errors = _parse_behavior_frontmatter(content)
        directory_name = Path(rel_path).parent.name
        declared_name = frontmatter.get("name")
        if declared_name and declared_name != directory_name:
            errors.append(f"name '{declared_name}' does not match directory '{directory_name}'")
        if errors:
            failures.append(f"{rel_path}: {', '.join(errors)}")

    if failures:
        self._add_check(
            metric,
            0,
            f"{len(failures)}/{len(behavior_files)} behavior specs structurally invalid; {failures[0]}",
            "Fix Behavior frontmatter and directory/name consistency; semantic quality remains a separate eval concern.",
            "Run templates/scripts/validate-behaviors.sh",
        )
    else:
        self._add_check(
            metric,
            2,
            f"Validated {len(behavior_files)} behavior specs with required frontmatter and name/path consistency",
            "",
            "",
        )


def register_behavior_metric() -> None:
    if not any(metric.get("id") == "AGENT-004" for metric in core.METRIC_DEFINITIONS):
        insert_at = next(
            (i for i, metric in enumerate(core.METRIC_DEFINITIONS) if metric.get("id") == "DESIGN-001"),
            len(core.METRIC_DEFINITIONS),
        )
        core.METRIC_DEFINITIONS.insert(insert_at, AGENT_004)
    setattr(core.RepoAuditor, "_eval_agent_004", _eval_agent_004)


register_behavior_metric()

if __name__ == "__main__":
    core.main()
