# Risk-Based Operational Trace Policy

## Purpose

Operational traces are selective evidence, not universal process logging. OpenForge therefore requires a trace only when a pull request changes paths classified as high risk by a repository-local policy.

The gate is intentionally change-aware: an old trace already present in the repository is not sufficient. A high-risk pull request must add or modify a trace in the same pull-request diff.

## Contract

Policy schema:

`openforge-agent-risk-policy/v1`

Result schema:

`openforge-agent-risk-result/v1`

The policy defines:

- `defaultRisk`
- `traceRequiredAt`
- `tracePathPrefix`
- ordered repository path rules with risk and reason

Current risk levels are `low`, `medium`, and `high`. The highest matching risk wins.

## CI flow

```text
PR changed paths
  -> repository risk policy
  -> highest risk
  -> trace required?
  -> trace changed in the same diff?
  -> operational trace baseline gate
  -> repository CI evidence remains separate
```

A high-risk change without a same-diff trace fails before the operational baseline comparison.

## Repository profiles

### OpenForge

High-risk examples:

- `.github/workflows/**`
- `templates/scripts/**`
- `templates/agent-eval/**`
- `.agents/**`

Canonical template traces live under `templates/agent-eval/traces/` because OpenForge distributes the reusable template rather than consuming it only as a downstream repository.

### Narwhal

High-risk examples include CI/release workflows, air-gap tooling, install/security scripts, GitOps desired state, version sources of truth, and agent evidence contracts.

### KubeMetal

High-risk examples include CI/release workflows, air-gap tooling, Kubernetes mutation scripts, MLX runtime scripts, Tauri native code, and agent evidence contracts.

### nfs-quota-agent

High-risk examples include CI/release workflows, command/controller code, privileged quota reconciliation, Helm deployment/RBAC, image build inputs, compatibility tooling, and agent evidence contracts.

## Evidence-class boundary

This gate proves only that a high-risk change carries reviewable operational trace evidence and that the trace does not regress below the trusted behavior baseline.

It does not prove runtime correctness. Cluster, native macOS/MLX, privileged filesystem, integration, release, security, and other repository-specific checks remain separate evidence classes.

## Failure found during rollout

The first OpenForge run failed because the initial policy expected downstream `.agents/evals/traces/` layout while OpenForge itself stores reusable template traces under `templates/agent-eval/`. The failure was treated as policy/layout evidence, not bypassed.

The OpenForge profile was corrected to use `templates/agent-eval/traces/`, a real trace for the risk-gate rollout was added, and CI then passed.

This follows the intended recovery model: expose the mismatch, narrow the cause, fix the contract, and verify again rather than weakening the gate.

## AGENT-005 status

This policy strengthens operational evidence collection but does not by itself justify a new portfolio compliance metric. AGENT-005 remains deferred until naturally occurring agent-behavior regressions are caught before merge with actionable signal and acceptable maintenance cost.
