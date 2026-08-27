# Project-specific Agent Instruction Audit Matrix

This document tracks active repositories against the OpenForge context-efficient agent engineering standard.

The audit is intentionally split into two layers:

1. **Automatable inventory** — instruction files, architecture/source-of-truth docs, build entrypoints, CI/tooling, test directories, and obvious context-bloat signals.
2. **Human review** — high-risk paths, duplicated/obsolete prompt rules, architecture boundaries, access-control constraints, and whether documented commands are actually canonical.

Run the reusable inventory script from a checked-out repository:

```bash
bash templates/scripts/audit-agent-repo.sh /path/to/repository repository-name
```

## Initial portfolio audit

| Repository | Root instructions | Source-of-truth / architecture | Build / test entrypoint | Deterministic tooling | Bug reproduction | Human-review finding |
| --- | --- | --- | --- | --- | --- | --- |
| `narwhal` | `AGENTS.md`, `CLAUDE.md` | `README.md`, `CONTRIBUTING.md`, project docs | `Makefile` | pre-commit, markdownlint, Actions | Strong | Review long `CLAUDE.md` for generic guidance duplicated by AGENTS/tooling; preserve project-specific source maps and operational hazards. |
| `narwhal-portal` | `AGENTS.md`, `CLAUDE.md` | `DESIGN.md`, `README.md` | `Makefile`, frontend package tooling | Actions/frontend tooling | Strong | Architecture contract is explicit; keep UI/domain/API boundaries and auth/RBAC behavior prominent, trim generic agent prose when duplicated. |
| `beluga` | `AGENTS.md`, `CLAUDE.md` | `README.md`, `VERSIONS.md`, `docs/` | `Makefile`, `Vagrantfile` | policies, tests, scripts | Strong | GitOps/policy/config paths are high risk. Treat version pins, networking, storage, and destructive cluster operations as explicit design changes. |
| `beluga-manager` | `AGENTS.md` | `README.md`, `CONTRIBUTING.md`, `docs/` | Not obvious at root | `.editorconfig`, Actions | Review needed | Documentation baseline is good, but canonical build/test entrypoint should be made obvious before relying on agent execution. |
| `kubemetal` | `AGENTS.md`, `CLAUDE.md` | `DESIGN.md`, `README.md`, `docs/` | `Makefile`, `package.json` | Actions/project tooling | Strong | Preserve macOS host/guest runtime boundary and privileged host operations; avoid duplicating generic instructions across agent files. |
| `clusterdeck` | `AGENTS.md` | `README.md`, `CONTRIBUTING.md`, `docs/` | `Makefile`, `package.json`, Rust/Tauri sources | `.editorconfig`, Actions | Moderate | `AGENTS.md` is larger than the newer concise baseline. Separate Tauri/Rust privileged operations and UI guidance from always-loaded generic rules. |
| `ldapium` | `AGENTS.md`, `CLAUDE.md` | `README.md`, `CONTRIBUTING.md` | `Makefile` | Actions/project tooling | Strong | LDAP schema, credentials, TLS, bootstrap/migration, and directory mutation paths need explicit access/destructive-change boundaries. |
| `nfs-quota-agent` | `AGENTS.md`, `CLAUDE.md` | `DESIGN.md`, `CONTRIBUTING.md` | `Makefile`, Go module | golangci-lint, Actions | Strong | Privileged filesystem/quota operations are high risk. Keep kernel/filesystem compatibility and mount/destructive boundaries project-specific. |
| `egovframe-launcher` | `AGENTS.md` | `README.md`, `docs/` | Launcher/scripts; root command not obvious | Actions | Review needed | Add an obvious canonical build/test/lint entrypoint and architecture boundary for launcher UI/CLI/system-process execution. |
| `kube-ready-box` | `AGENTS.md`, `CLAUDE.md`, `.agent/`, `.codex/`, `.claude/` | `README.md`, `docs/` | `Makefile`, `Vagrantfile` | ShellCheck, Actions | Strong | Highest context-dilution risk: AGENTS and CLAUDE are each ~16 KB plus multiple agent-specific directories. Split reusable rules into tooling/docs and retain only project hazards, canonical commands, and boundaries in root contract. |

## Portfolio findings

The initial audit shows three recurring patterns:

- **Context duplication:** mature repositories often have both `AGENTS.md` and a much larger agent-specific file. The large file is justified only when it carries project-specific source maps, operational hazards, or tool-specific integration context.
- **Command discoverability gaps:** `beluga-manager` and `egovframe-launcher` need a clearer canonical build/test/lint entrypoint before agents can verify changes deterministically.
- **Privilege boundaries:** infrastructure repositories need explicit guidance around cluster mutation, filesystem/quota operations, credentials, host execution, RBAC, and destructive actions. These are architecture/safety contracts, not formatter rules.

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
- obvious instruction-context bloat that warrants human review

## Interpretation

An `AGENTS.md` file is not sufficient by itself. A repository is considered **agent-ready** only when an agent can determine the intended architecture boundaries, execute relevant verification, distinguish real evidence from assumptions, and avoid expanding privileges or public API surface without an explicit design decision.

The audit script therefore reports inventory evidence and a `context_bloat=review` signal when a root instruction file exceeds the conservative 12 KB review threshold. This is not a failure grade: architecture fit, necessity of project-specific context, and risk boundaries remain human-judgment standards.

## Follow-up priority

1. `kube-ready-box` — reduce root instruction duplication/context load.
2. `beluga-manager` — establish canonical build/test/lint entrypoint.
3. `egovframe-launcher` — establish canonical verification entrypoint and launcher execution boundary.
4. `clusterdeck` — split large root AGENTS guidance into concise contract plus linked design/coding guidance.
5. Remaining repositories — deduplicate generic `CLAUDE.md` guidance without removing valuable project-specific source maps or hazards.
