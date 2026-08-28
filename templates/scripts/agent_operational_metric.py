"""Canonical AGENT-005 operational Agent Evaluation profile registration."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Dict, List

AGENT_005: Dict[str, Any] = {
    "id": "AGENT-005",
    "area": "Agent Engineering",
    "name": "Operational Agent Evaluation Profile",
    "target": "Adopted agent evals expose a strict trace, trusted baseline, live verification binding, regression gate, and CI wiring",
    "default_weight": 1,
    "related_adr": "ADR-0009",
    "related_standard": "docs/agent-evaluation-operations.md",
    "priority": "P2",
}

TYPED_EVIDENCE = ("ci:", "test:", "runtime:", "artifact:", "policy:")


def _load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:
        return None, str(exc)


def register(core: Any) -> None:
    if any(metric.get("id") == "AGENT-005" for metric in core.METRIC_DEFINITIONS):
        return

    insert_at = next(
        (i for i, metric in enumerate(core.METRIC_DEFINITIONS) if metric.get("id") == "DESIGN-001"),
        len(core.METRIC_DEFINITIONS),
    )
    core.METRIC_DEFINITIONS.insert(insert_at, AGENT_005)

    original_init = core.RepoAuditor.__init__

    def repo_init(self: Any, repo_info: Dict[str, Any], workspace_root: Path) -> None:
        original_init(self, repo_info, workspace_root)
        self.agent_evals = repo_info.get("agent_evals", None)

    def eval_agent_005(self: Any, metric: Dict[str, Any]) -> None:
        root = self.full_path / ".agents" / "evals"
        if self.agent_evals is False:
            self._add_check(metric, "N/A", "Operational Agent Evaluation profile explicitly disabled", "", "Optional adoption-level control")
            return
        if not root.exists():
            if self.agent_evals is True:
                self._add_check(metric, 0, "Operational Agent Evaluation profile required but .agents/evals/ is missing", "Adopt the executable eval contract or set agent_evals: false.", "docs/agent-evaluation-operations.md")
            else:
                self._add_check(metric, "N/A", "Operational Agent Evaluation profile not adopted", "", "Optional adoption-level control")
            return

        required = ["evaluate.py", "gate.py", "baseline.eval.json"]
        missing = [name for name in required if not (root / name).is_file()]
        binder = next((name for name in ("bind-verification.py", "bind-agent-verification.py") if (root / name).is_file()), None)
        if not binder:
            missing.append("bind-verification.py")
        traces = sorted((root / "traces").glob("*.json")) if (root / "traces").is_dir() else []
        if not traces:
            missing.append("traces/*.json")
        if missing:
            self._add_check(metric, 0, f"Operational eval contract incomplete: missing {', '.join(missing)}", "Provide evaluator, baseline gate, live binder, and at least one operational trace.", "docs/agent-evaluation-operations.md")
            return

        failures: List[str] = []
        baseline, err = _load_json(root / "baseline.eval.json")
        if err or not isinstance(baseline, dict) or baseline.get("schemaVersion") != "openforge-agent-eval/v1" or not isinstance(baseline.get("results"), list):
            failures.append("baseline.eval.json is not a valid openforge-agent-eval/v1 baseline")

        strict_traces = 0
        live_ready = 0
        for path in traces:
            trace, trace_err = _load_json(path)
            if trace_err or not isinstance(trace, dict) or trace.get("schemaVersion") != "openforge-agent-trace/v1":
                failures.append(f"{path.name}: invalid trace schema")
                continue
            if trace.get("consistencyMode") != "strict":
                continue
            strict_traces += 1
            events = trace.get("events", []) if isinstance(trace.get("events"), list) else []
            verification = [e for e in events if e.get("type") in {"verification", "regression_verification"}]
            claims = [e for e in events if e.get("type") == "completion_claim"]
            outcomes = [e for e in events if e.get("type") == "task_outcome" and str(e.get("state", "")).upper() in {"A", "B", "C"}]
            typed = any(any(str(ref).startswith(TYPED_EVIDENCE) for ref in e.get("evidence", [])) for e in verification)
            statuses = all(str(e.get("status", "")).lower() in {"pending", "passed", "failed", "success", "failure"} for e in verification) if verification else False
            if verification and claims and outcomes and typed and statuses:
                live_ready += 1

        if strict_traces == 0:
            failures.append("no consistencyMode=strict operational trace")
        elif live_ready == 0:
            failures.append("strict traces lack explicit verification status, typed evidence, completion claim, or task outcome")

        workflows = self._get_all_workflows_content()
        binder_ref = bool(re.search(r"bind-(?:agent-)?verification\.py", workflows))
        gate_ref = ".agents/evals/gate.py" in workflows
        trace_ref = "--trace" in workflows
        if not (binder_ref and gate_ref and trace_ref):
            failures.append("CI does not wire live verification binding and regression gating")

        if failures:
            self._add_check(metric, 0, f"Operational eval contract invalid: {failures[0]}", "Repair executable evidence semantics and CI wiring; file presence alone is insufficient.", "docs/agent-evaluation-operations.md")
        else:
            self._add_check(metric, 2, f"Validated operational eval contract with {strict_traces} strict trace(s), trusted baseline, live binder, and CI regression gate", "", "")

    core.RepoAuditor.__init__ = repo_init
    core.RepoAuditor._eval_agent_005 = eval_agent_005

    original_validate = core.validate_portfolio_config
    def validate_portfolio_config(config_data: Dict[str, Any]) -> List[str]:
        errors = original_validate(config_data)
        for idx, repo in enumerate(config_data.get("repositories", [])):
            if isinstance(repo, dict) and "agent_evals" in repo and not isinstance(repo["agent_evals"], bool):
                errors.append(f"Repository '{repo.get('id', idx)}' field 'agent_evals' must be true or false when specified")
        return errors
    core.validate_portfolio_config = validate_portfolio_config

    original_run = core.run_portfolio_audit
    def run_portfolio_audit(portfolio, workspace_root):
        result = original_run(portfolio, workspace_root)
        result["metricSetVersion"] = "2026.10"
        result["metricSetChange"] = {
            "type": "additive",
            "added": ["AGENT-005"],
            "notes": "AGENT-005 is N/A unless explicitly required or .agents/evals/ is adopted; it requires an executable live-evidence/regression-gate contract, not directory presence.",
        }
        return result
    core.run_portfolio_audit = run_portfolio_audit

    original_compare = core.compare_with_baseline
    def compare_with_baseline(current, baseline):
        comparison = original_compare(current, baseline)
        curr_v = current.get("metricSetVersion", "unknown")
        base_v = baseline.get("metricSetVersion", "unknown")
        if curr_v == "2026.10" and base_v in {"2026.09", "2026.08"}:
            comparison["metricSetVersionStatus"] = "additive-compatible"
            comparison["warning"] = "Metric set 2026.10 adds opt-in AGENT-005; prior scores remain comparable where the operational eval profile is N/A."
        return comparison
    core.compare_with_baseline = compare_with_baseline
