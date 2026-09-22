# Agent Skills Portfolio Audit — 2026-09

This audit applies the OpenForge agent-skills layering model to actively developed `dasomel` OSS repositories and records the first portfolio rollout. The structural rollout was merged on 2026-09-09; project skills remain `draft` until the fresh-session verification work tracked by OpenForge issue #54 produces the machine-readable evidence required by the Agent Skills standard.

## Portfolio findings

1. `AGENTS.md` adoption was already strong across the established portfolio, but skill adoption was uneven.
2. Existing skills were concentrated in Narwhal, Narwhal Portal, and nfs-quota-agent; other repositories mostly carried project knowledge in AGENTS/CLAUDE/docs.
3. Generic project skill names such as `verification` create collisions when skills are discovered globally.
4. Claude team/model orchestration is useful runtime configuration but should not own portable project workflow knowledge.
5. Personal absolute paths and required dependence on a maintainer-global Claude configuration are not portable repository contracts.
6. Kube Ready Box, Narwhal, and Narwhal Portal had large CLAUDE guides suitable for decomposition; KubeMetal, Beluga, ClusterDeck, and LDAPium already had thin adapters.
7. The earlier portfolio audit reported verification false-green for Beluga Manager and eGovFrame Launcher. Launcher actually had a real nested `launcher/Makefile`; its rollout exposes that owner at repository root. Beluga Manager still needs a deterministic repository-owned verification entrypoint.
8. Siqoq was early enough to establish the layered model before ad-hoc runtime instructions accumulated; its unrelated pre-existing Ruff failure was repaired separately before the agent foundation was merged.
9. `verified`/`stable` maturity is now machine-gated: `.agents/skill-evals/<skill>.json` must bind a fresh-session happy path, failure/edge replay, deterministic checks, runtime identity, skill version, and claim boundary.

## Canonical portfolio layering

```text
OpenForge
  -> agent engineering + Agent Skills standards/templates/auditors

Project AGENTS.md
  -> short agent-neutral execution contract

Project .agents/skills/<project>-<task>/SKILL.md
  -> canonical project-specific repeatable workflow

CLAUDE.md / .claude/skills / runtime rules
  -> thin adapters, routing, commands, hooks, team/model orchestration

scripts / Makefile / tests / CI / policy
  -> deterministic execution and evidence
```

## First rollout status

| Repository | Canonical project skill(s) | CLAUDE / contract change | Verification/maturity status | Structural rollout | Replay tracking |
|---|---|---|---|---|---|
| `openforge` | standard/template/audit layer rather than project skill collection | minimal CLAUDE template + skill/Claude audit rules | standard + machine-readable verification evidence gate merged | #53 / #56 merged | #54 |
| `narwhal` | `narwhal-component-lifecycle`, `narwhal-version-upgrade`, `narwhal-cluster-debug`, `narwhal-verification` | large CLAUDE reduced to routing adapter; durable operational rules moved to project docs; legacy `narwhal-ops` is a deprecated router | split skills remain `draft`; agent-policy trace and CI passed for the restructuring | #183 merged | #184 |
| `narwhal-portal` | `narwhal-portal-frontend`, `narwhal-portal-backend`, `narwhal-portal-qa` | AGENTS is source of truth; CLAUDE is harness adapter; personal absolute Narwhal path removed; legacy `idp-*` entries are deprecated adapters | canonical skills remain `draft` | #91 merged | #92 |
| `nfs-quota-agent` | `nfs-quota-verification` | thin CLAUDE routes to canonical skill; generic `verification` remains only as deprecated adapter | mature historical workflow retained, but no grandfathered `verified` state; #172 aligns maturity to `draft` until evidence exists | #170 merged / #172 alignment | #171 |
| `kube-ready-box` | `kube-ready-box-build-validation` | build matrix/workflow removed from large CLAUDE; adapter points to AGENTS, skill, commands/hooks, playbook and mistakes log | `draft` until representative provider/runtime replay | #40 merged | #41 |
| `kubemetal` | `kubemetal-hybrid-runtime-change` | thin CLAUDE routes to skill; maintainer-global Claude config is no longer a repository requirement | `draft`; restructuring trace + Agent Behavior + CI passed | #72 merged | #73 |
| `beluga` | `beluga-platform-change` | thin CLAUDE routes to skill | `draft`; CI, docs/ADR, supply-chain and SAST gates passed | #122 merged | #123 |
| `beluga-manager` | `beluga-manager-integration-contract` | thin CLAUDE adapter added; i18n docs gate excludes machine-facing agent contracts to avoid duplicate translated sources | intentionally `draft`; deterministic local verification owner is still missing | #52 merged | #51 + #54 |
| `clusterdeck` | `clusterdeck-connection-workflow` | thin CLAUDE routes to skill | `draft`; repository CI passed | #17 merged | #18 |
| `ldapium` | `ldapium-directory-change` | thin CLAUDE routes to skill | `draft`; CI, browser UI E2E, kind E2E, security, CodeQL and air-gap bundle all passed | #139 merged | #140 |
| `egovframe-launcher` | `egovframe-launcher-target-workflow` | thin CLAUDE added; AGENTS points at project workflow and evidence classes | root `make verify` delegates to the existing nested formatter/test/build owner; skill remains `draft`; multi-platform workflow passed | #8 merged | #9 |
| `siqoq` | `siqoq-sim-to-edge-workflow` | root AGENTS + thin CLAUDE established from bootstrap stage | CI-aligned root `make verify`; skill remains `draft`; unrelated Ruff failures fixed separately in #35 before successful agent-foundation CI | #34 merged | #36 |

## Why these skills are project-scoped

The first rollout deliberately avoids creating a large OpenForge catalog of generic `build`, `debug`, `verify`, or framework skills. The selected workflows carry repository-specific invariants that a model should not rediscover on each task:

- Narwhal GitOps/component/cluster operational ownership.
- Narwhal Portal API/UI/auth/cross-repository seams.
- nfs-quota-agent stub-versus-real-filesystem verification.
- Kube Ready Box provider/architecture build invariants.
- KubeMetal Apple Silicon host-compute versus Kubernetes-control split.
- Beluga shared-cluster/GitOps/domain-entry verification.
- Beluga Manager authoritative-upstream versus correlation/domain ownership.
- ClusterDeck SSH/kubeconfig/user-config safety flow.
- LDAPium real LDAP/OpenLDAP semantics and E2E behavior.
- eGovFrame Launcher heterogeneous target lifecycle/toolchains.
- Siqoq simulation-to-edge interface and physical safety boundary.

## Candidate domain families — promote only after evidence

These remain comparison candidates, not shared skills yet:

- Kubernetes platform change/evidence: Narwhal, Beluga, KubeMetal.
- External-process / CLI integration evidence: ClusterDeck, eGovFrame Launcher, KubeMetal.
- API/UI boundary verification: Narwhal Portal, Beluga Manager.
- Build-image validation: Kube Ready Box and future image-builder repositories.
- Real service versus mock evidence: nfs-quota-agent filesystems, LDAPium LDAP, ClusterDeck SSH, Portal/Beluga integrations.

Do not promote a project workflow to `domain` merely because two skills have similar prose. Promotion requires at least two successful project implementations whose procedure can be reused without importing project-specific assumptions.

## CLAUDE.md audit rules

Portfolio `CLAUDE.md` should converge on:

```text
@AGENTS.md

Claude-only adapter
  -> project skill routing
  -> .claude/rules / commands / hooks references
  -> optional runtime/team/model orchestration
  -> no generic engineering-rule copies
  -> no personal absolute path requirement
  -> no required maintainer-global config
```

A large legacy CLAUDE.md must be classified rather than deleted mechanically:

- repository-wide invariant -> `AGENTS.md` or stable project doc;
- repeatable task workflow -> project skill;
- historical incident -> mistakes/lessons log;
- deterministic check -> script/Make/test/CI;
- Claude-only agent/team/command behavior -> CLAUDE/rules/hooks.

## Skill maturity and rollout gate

Newly created or materially split skills start at `draft`, even when their underlying repository already has good tests. Existing skills are not grandfathered. Promote to `verified` only after:

1. `SKILL.md` format/hygiene validation;
2. a fresh session with no creation-conversation context;
3. successful execution of the intended workflow;
4. at least one known failure/edge regression;
5. repository-owned deterministic verification;
6. explicit confirmation of what changed and what must not change;
7. each claimed runtime/agent environment when portability is claimed;
8. `.agents/skill-evals/<skill-name>.json` using `openforge-agent-skill-verification/v1`, with `skillVersion` matching `metadata.openforge-version`.

OpenForge issue #54 is the portfolio tracker for this maturity gate. Promotion remains project-owned: OpenForge records and validates evidence, but does not infer `verified` from a merged PR or green CI alone.

## Remaining gaps

### P0

- Complete fresh-session replay work tracked by #54 and the project-local replay issues in the table above, including nfs-quota-agent #171.
- Beluga Manager #51: establish one deterministic local verification command and align CI/local ownership before promoting its skill.

### P1

- Remove deprecated Claude adapters only after supported runtimes reliably discover the canonical `.agents/skills/` paths.
- Add portfolio automation that invokes `audit-agent-skills.py` against checked-out repositories and records results alongside `agent-audit-matrix.md`.

### P2

- Compare successful project replays and promote only genuinely reusable procedures to OpenForge `domain` scope.
- Prune project skills that become fully deterministic scripts/CI or are no longer used.

## Acceptance criteria

The structural rollout is complete: all first-wave standardization PRs above are merged. The maturity rollout is complete only when:

- every active project has a concise root agent contract;
- CLAUDE.md contains only runtime-specific adapter behavior plus references;
- every canonical project skill has a unique project-prefixed name, scope/owner/maturity/version metadata, and a precise description;
- deterministic steps are owned by scripts/Make/tests/CI where possible;
- no canonical skill has a manually maintained divergent mirror;
- fresh-session replay and at least one failure case are recorded before `verified`;
- every `verified`/`stable` skill has valid `openforge-agent-skill-verification/v1` evidence matching its skill version;
- the portfolio skill audit has no personal absolute paths, malformed skill files, generic canonical project names, or verification false-green.
