# Agent Skills Portfolio Audit — 2026-09

This audit applies the OpenForge agent-skills layering model to actively developed `dasomel` OSS repositories. It is a migration plan, not a claim that every proposed skill already exists.

## Portfolio findings

1. `AGENTS.md` adoption is strong across the established portfolio, but skill adoption is uneven.
2. Existing project skills are concentrated in Narwhal, Narwhal Portal, and nfs-quota-agent.
3. Several repositories use a healthy thin `CLAUDE.md` that only imports `AGENTS.md`; Narwhal, Narwhal Portal, and Kube Ready Box still carry larger project knowledge/workflow blocks in `CLAUDE.md`.
4. Generic project skill names such as `verification` risk collisions when skills are installed globally.
5. Some Claude instructions contain runtime orchestration/model routing that is valuable but not portable skill content.
6. Personal absolute paths and required dependence on a maintainer-global Claude configuration should not be repository contracts.
7. `beluga-manager` and `egovframe-launcher` still have verification false-green findings in the existing portfolio audit; skills must route to real executable owners rather than paper over missing commands.
8. `siqoq` is new enough that the agent contract/skill structure should be established before ad-hoc instructions accumulate.

## Target layering by project

| Repository | Current state | Project skills / specialization target | CLAUDE.md target | Priority |
|---|---|---|---|---|
| `narwhal` | AGENTS + large CLAUDE + `narwhal-ops` | Keep a project router, separate component lifecycle, upgrade, cluster-debug, and verification knowledge as references/workflows when they diverge; avoid broad generic trigger lists | Thin adapter; move stable gotchas to docs/skill references and Claude-only lane orchestration to `.claude/rules/` | P0 |
| `narwhal-portal` | AGENTS + large CLAUDE + frontend/backend/orchestrator/qa skills | Keep `idp-frontend`, `idp-backend`, `idp-qa`; treat orchestration as Claude/runtime-specific when it is about subagent lanes rather than domain knowledge | Remove personal absolute paths; retain cross-repo ownership rule and Claude-only harness routing by reference | P0 |
| `nfs-quota-agent` | AGENTS + thin CLAUDE + `verification` skill | Rename/migrate toward `nfs-quota-verification`; preserve real-filesystem vs stub evidence split | Already close to target | P0 |
| `kube-ready-box` | AGENTS + large CLAUDE, commands/hooks | `kube-ready-box-build-validation`, `kube-ready-box-release`; move build-matrix and repeatable validation workflow out of CLAUDE | Thin adapter pointing to skills, commands, mistakes log | P1 |
| `kubemetal` | AGENTS + thin CLAUDE, no skills | `kubemetal-ml-pipeline`, `kubemetal-verification` | Already close to target; keep harness reference only | P1 |
| `beluga` | AGENTS + thin CLAUDE, no skills | `beluga-cluster-lifecycle`, `beluga-verification` | Already target shape | P1 |
| `beluga-manager` | AGENTS only, no skills | `beluga-manager-integration`, `beluga-manager-verification`; verification skill must call a newly established deterministic project entrypoint | Add minimal adapter only if Claude-specific behavior is needed | P0 |
| `clusterdeck` | AGENTS + thin CLAUDE, no skills | `clusterdeck-ssh-kubeconfig`, `clusterdeck-verification` | Already target shape | P1 |
| `ldapium` | AGENTS + thin CLAUDE, no skills | `ldapium-directory-change`, `ldapium-verification` | Already target shape | P1 |
| `egovframe-launcher` | AGENTS only, no skills | `egovframe-launcher-generation`, `egovframe-launcher-verification`; establish deterministic verify/build/test owner first | Add minimal adapter if needed | P0 |
| `siqoq` | no root AGENTS/CLAUDE/skills detected at audit time | start with `siqoq-edge-ai-workflow` only after the architecture and executable verification path stabilize | start from minimal adapter template, not a large guide | P0 |

## Common skill families

These are candidates for OpenForge `domain` guidance only when two or more projects prove the same workflow can be reused without project assumptions.

- Kubernetes platform change/verification: Narwhal, Beluga, KubeMetal.
- Go CLI/service verification: nfs-quota-agent, ClusterDeck, LDAPium, eGovFrame Launcher where applicable.
- Portal UI/API boundary verification: Narwhal Portal, Beluga Manager.
- Build-image/release validation: Kube Ready Box and future image-builder repositories.

Do not centralize these prematurely. Project evidence comes first.

## CLAUDE.md audit rules

Portfolio rollout should make `CLAUDE.md` converge on this shape:

```text
@AGENTS.md

Claude-only adapter
  -> project skill routing
  -> .claude/rules / commands / hooks references
  -> no generic engineering-rule copies
  -> no personal machine path requirement
```

A long existing CLAUDE.md is not deleted mechanically. Each section must be classified as repository contract, project skill workflow, stable documentation, incident history, deterministic check, or Claude-only adapter behavior and moved to the owner for that class.

## Migration order

### Wave 1 — correctness and collision risk

1. OpenForge standard/template/audit controls.
2. nfs-quota-agent generic skill name migration.
3. Narwhal / Narwhal Portal CLAUDE and skill routing cleanup.
4. beluga-manager / egovframe-launcher deterministic verification ownership.
5. Siqoq root agent contract.

### Wave 2 — project specialization

Add only high-value project workflows to KubeMetal, Beluga, ClusterDeck, LDAPium, and Kube Ready Box. Each skill must be replayed from a fresh session before `verified` maturity.

### Wave 3 — promotion and pruning

Compare successful project skills. Promote genuinely shared workflows to `domain` scope, delete overlaps, and deprecate legacy Claude-only copies when adapters are verified.

## Acceptance criteria

The rollout is complete when:

- every active project has a concise root agent contract;
- CLAUDE.md contains only Claude/runtime-specific adapter behavior plus references;
- every project skill has a unique project-prefixed name, scope/owner/maturity/version metadata, and a precise description;
- deterministic steps are scripts/Make/CI targets where possible;
- no canonical skill has a manually maintained divergent mirror;
- fresh-session replay and at least one failure case are recorded before `verified`;
- portfolio audit reports no verification false-green for skills that claim completion evidence.
