# Project-specific Agent Instruction Audit Matrix

This document tracks active repositories against the OpenForge context-efficient agent engineering standard.

The audit is intentionally split into two layers:

1. **Automatable inventory** — instruction files, architecture/source-of-truth docs, build entrypoints, CI presence, test directories.
2. **Human review** — high-risk paths, duplicated/obsolete prompt rules, architecture boundaries, access-control constraints, and whether the documented commands are actually canonical.

Run the reusable inventory script from a checked-out repository:

```bash
bash templates/scripts/audit-agent-repo.sh /path/to/repository repository-name
```

## Initial portfolio audit

| Repository | Root instructions | Source-of-truth / architecture | Build / test entrypoint | Deterministic tooling | Bug reproduction | Human-review finding |
| --- | --- | --- | --- | --- | --- | --- |
| `narwhal` | `AGENTS.md`, `CLAUDE.md` | `README.md`, `CONTRIBUTING.md`, project docs | `Makefile` | `.pre-commit-config.yaml`, `.markdownlint.json`, GitHub Actions | Strong candidate for automation | Large `CLAUDE.md` remains valuable for project-specific source maps/high-risk context, but should be reviewed for generic rules duplicated by `AGENTS.md` or tooling. |
| `kubemetal` | `AGENTS.md`, `CLAUDE.md` | `DESIGN.md`, `README.md`, `docs/` | `Makefile`, `package.json` | GitHub Actions and project build tooling | Strong candidate for automation | Architecture guidance is explicit through `DESIGN.md`; audit should focus on macOS/host-runtime boundaries and avoiding duplicated generic agent guidance. |

## Required fields per repository

Each portfolio audit should record:

- root instruction file(s)
- project-specific source-of-truth documents
- canonical build/test/lint command
- high-risk paths
- whether bug reproduction can be automated
- deterministic rules already enforced by tooling
- duplicated or obsolete prompt rules
- missing architecture, permission, or access-boundary guidance

## Interpretation

An `AGENTS.md` file is not sufficient by itself. A repository is considered **agent-ready** only when an agent can determine the intended architecture boundaries, execute relevant verification, distinguish real evidence from assumptions, and avoid expanding privileges or public API surface without an explicit design decision.

The audit script therefore reports inventory evidence only. It must not assign a final readiness grade automatically; architecture fit and risk boundaries remain human-judgment standards.

## Portfolio order

The initial review order from issue #15 is:

`narwhal` → `narwhal-portal` → `beluga` → `beluga-manager` → `kubemetal` → `clusterdeck` → `ldapium` → `nfs-quota-agent` → `egovframe-launcher` → `kube-ready-box`.
