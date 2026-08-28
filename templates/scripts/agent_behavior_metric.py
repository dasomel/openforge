"""Canonical AGENT-004 registration for OpenForge portfolio auditing.

This module extends the stable audit core without introducing third-party
runtime dependencies. AGENT-004 is opt-in by configuration or auto-adopted
when `.agents/behaviors/` exists.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Tuple

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


def parse_behavior_frontmatter(content: str) -> Tuple[Dict[str, str], List[str]]:
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


def register(core: Any) -> None:
    """Register AGENT-004 and additive 2026.09 compatibility behavior."""
    if any(metric.get("id") == "AGENT-004" for metric in core.METRIC_DEFINITIONS):
        return

    insert_at = next(
        (i for i, metric in enumerate(core.METRIC_DEFINITIONS) if metric.get("id") == "DESIGN-001"),
        len(core.METRIC_DEFINITIONS),
    )
    core.METRIC_DEFINITIONS.insert(insert_at, AGENT_004)

    original_init = core.RepoAuditor.__init__

    def repo_init(self: Any, repo_info: Dict[str, Any], workspace_root: Path) -> None:
        original_init(self, repo_info, workspace_root)
        self.agent_behaviors = repo_info.get("agent_behaviors", None)

    def eval_agent_004(self: Any, metric: Dict[str, Any]) -> None:
        behavior_root = self.full_path / ".agents" / "behaviors"
        behavior_files = sorted(set(self._find_files(".agents/behaviors/*/BEHAVIOR.md")))

        if self.agent_behaviors is False:
            self._add_check(metric, "N/A", "Agent Behavior profile explicitly disabled", "", "Optional adoption-level control")
            return

        if not behavior_root.exists():
            if self.agent_behaviors is True:
                self._add_check(
                    metric,
                    0,
                    "Agent Behavior profile required by portfolio config but .agents/behaviors/ is missing",
                    "Create .agents/behaviors/<name>/BEHAVIOR.md specs or set agent_behaviors: false when intentionally not adopted.",
                    "docs/agent-behaviors.md",
                )
            else:
                self._add_check(metric, "N/A", "Agent Behavior profile not adopted", "", "Optional adoption-level control")
            return

        if not behavior_files:
            self._add_check(
                metric,
                0,
                "Behavior profile directory exists but contains no BEHAVIOR.md specs",
                "Add at least one .agents/behaviors/<name>/BEHAVIOR.md or remove/disable the unused profile.",
                "docs/agent-behaviors.md",
            )
            return

        failures: List[str] = []
        for rel_path in behavior_files:
            content = self._read_file_safe(rel_path)
            frontmatter, errors = parse_behavior_frontmatter(content)
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

    core.RepoAuditor.__init__ = repo_init
    core.RepoAuditor._eval_agent_004 = eval_agent_004

    original_validate = core.validate_portfolio_config

    def validate_portfolio_config(config_data: Dict[str, Any]) -> List[str]:
        errors = original_validate(config_data)
        for idx, repo in enumerate(config_data.get("repositories", [])):
            if isinstance(repo, dict) and "agent_behaviors" in repo and not isinstance(repo["agent_behaviors"], bool):
                errors.append(
                    f"Repository '{repo.get('id', idx)}' field 'agent_behaviors' must be true or false when specified"
                )
        return errors

    core.validate_portfolio_config = validate_portfolio_config

    original_run = core.run_portfolio_audit

    def run_portfolio_audit(portfolio: List[Dict[str, Any]], workspace_root: Path) -> Dict[str, Any]:
        result = original_run(portfolio, workspace_root)
        result["metricSetVersion"] = "2026.09"
        result["metricSetChange"] = {
            "type": "additive",
            "added": ["AGENT-004"],
            "notes": "AGENT-004 is N/A unless explicitly required or .agents/behaviors/ is present.",
        }
        return result

    core.run_portfolio_audit = run_portfolio_audit

    original_compare = core.compare_with_baseline

    def compare_with_baseline(current: Dict[str, Any], baseline: Dict[str, Any]) -> Dict[str, Any]:
        comparison = original_compare(current, baseline)
        curr_v = current.get("metricSetVersion", "unknown")
        base_v = baseline.get("metricSetVersion", "unknown")
        if curr_v == "2026.09" and base_v == "2026.08":
            comparison["metricSetVersionStatus"] = "additive-compatible"
            comparison["warning"] = (
                "Metric set 2026.09 adds opt-in AGENT-004. Existing 2026.08 scores remain comparable "
                "for repositories where AGENT-004 is N/A; adopted repositories may gain a new applicable metric."
            )
        return comparison

    core.compare_with_baseline = compare_with_baseline
