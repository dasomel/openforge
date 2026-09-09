# Agent Skills Portfolio Audit — 2026-09

This audit applies the OpenForge agent-skills layering model to actively developed `dasomel` OSS repositories and records the first portfolio rollout. An open PR means the target shape is implemented for review, not merged or runtime-verified.

## Portfolio findings

1. `AGENTS.md` adoption was already strong across the established portfolio, but skill adoption was uneven.
2. Existing skills were concentrated in Narwhal, Narwhal Portal, and nfs-quota-agent; other repositories mostly carried project knowledge in AGENTS/CLAUDE/docs.
3. Generic project skill names such as `verification` create collisions when skills are discovered globally.
4. Claude team/model orchestration is useful runtime configuration but should not own portable project workflow knowledge.
5. Personal absolute paths and required dependence on a maintainer-global Claude configuration are not portable repository contracts.
6. Kube Ready Box, Narwhal, and Narwhal Portal had large CLAUDE guides suitable for decomposition; KubeMetal, Beluga, ClusterDeck, and LDAPium already had thin adapters.
7. The earlier portfolio audit reported verification false-green for Beluga Manager and eGovFrame Launcher. Launcher actually had a real nested `launcher/Makefile`; its rollout exposes that owner at repository root. Beluga Manager still needs a deterministic repository-owned verification entrypoint.
8. Siqoq was early enough to establish the layered model before ad-hoc runtime instructions accumulated.

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

| Repository | Canonical project skill(s) in rollout | CLAUDE / contract change | Verification/maturity status | Rollout |
|---|---|---|---|---|
| `openforge` | standard/template/audit layer rather than project skill collection | adds minimal CLAUDE template and skill/Claude audit rules | standard defines fresh-session + failure replay before `verified` | PR #53 |
| `narwhal` | `narwhal-component-lifecycle`, `narwhal-version-upgrade`, `narwhal-cluster-debug`, `narwhal-verification` | large CLAUDE reduced to routing adapter; durable operational rules moved to project docs; legacy `narwhal-ops` becomes deprecated router | new split skills are `draft` until replay | PR #183 |
| `narwhal-portal` | `narwhal-portal-frontend`, `narwhal-portal-backend`, `narwhal-portal-qa` | AGENTS becomes source of truth; CLAUDE becomes harness adapter; personal absolute Narwhal path removed; legacy `idp-*` entries become deprecated uppercase `SKILL.md` adapters | new canonical skills are `draft` until replay | PR #91 |
| `nfs-quota-agent` | `nfs-quota-verification` | thin CLAUDE routes to canonical skill; generic `verification` kept only as deprecated adapter | preserved mature real-filesystem-vs-stub workflow and existing verification trace; canonical migration remains the only initial `verified` skill | PR #170 |
| `kube-ready-box` | `kube-ready-box-build-validation` | build matrix/workflow removed from large CLAUDE; adapter points to AGENTS, skill, commands/hooks, playbook, mistakes log | `draft` until fresh replay on representative build path | PR #40 |
| `kubemetal` | `kubemetal-hybrid-runtime-change` | thin CLAUDE routes to skill; maintainer-global Claude config becomes optional | `draft` until fresh macOS/MLX/Colima replay | PR #72 |
| `beluga` | `beluga-platform-change` | thin CLAUDE routes to skill | `draft` until fresh cluster/GitOps replay | PR #122 |
| `beluga-manager` | `beluga-manager-integration-contract` | adds thin CLAUDE adapter | intentionally `draft`; deterministic local verification owner tracked in issue #51 | PR #52 / issue #51 |
| `clusterdeck` | `clusterdeck-connection-workflow` | thin CLAUDE routes to skill | `draft` until fresh real SSH/kubectl edge replay | PR #17 |
| `ldapium` | `ldapium-directory-change` | thin CLAUDE routes to skill | `draft` until fresh live-LDAP failure replay | PR #139 |
| `egovframe-launcher` | `egovframe-launcher-target-workflow` | adds thin CLAUDE adapter; AGENTS points at skill and real evidence classes | adds root `make verify` delegating to the existing nested formatter/test/build owner; skill stays `draft` until target workflow replay | PR #8 |
| `siqoq` | `siqoq-sim-to-edge-workflow` | adds root AGENTS + thin CLAUDE from the start | adds CI-aligned root `make verify`; skill intentionally `draft` until MVP replay | PR #34 |

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

Newly created or materially split skills start at `draft`, even when their underlying repository already has good tests. Promote to `verified` only after:

1. `SKILL.md` format/hygiene validation;
2. a fresh session with no creation-conversation context;
3. successful execution of the intended workflow;
4. at least one known failure/edge regression;
5. explicit confirmation of what changed and what must not change;
6. each claimed runtime/agent environment when portability is claimed.

The nfs-quota-agent migration is the initial exception because it preserves an existing, separately traced verification workflow rather than introducing a new split workflow.

## Remaining gaps

### P0

- Merge/review OpenForge PR #53 before treating its metadata/lifecycle rules as portfolio policy.
- Beluga Manager issue #51: establish one deterministic local verification command and align CI/local ownership.
- Replay Narwhal and Portal split skills from clean contexts before promoting any to `verified`.

### P1

- Replay KubeMetal, Beluga, ClusterDeck, LDAPium, Kube Ready Box, eGovFrame Launcher, and Siqoq workflows with one failure/edge scenario each.
- Remove deprecated Claude adapters only after supported runtimes discover the canonical `.agents/skills/` paths reliably.
- Add portfolio automation that invokes `audit-agent-skills.py` against checked-out repositories and records results alongside `agent-audit-matrix.md`.

### P2

- Compare successful project skills and promote only genuinely reusable procedures to OpenForge `domain` scope.
- Prune project skills that become fully deterministic scripts/CI or are no longer used.

## Acceptance criteria

The rollout is complete when:

- every active project has a concise root agent contract;
- CLAUDE.md contains only runtime-specific adapter behavior plus references;
- every canonical project skill has a unique project-prefixed name, scope/owner/maturity/version metadata, and a precise description;
- deterministic steps are owned by scripts/Make/tests/CI where possible;
- no canonical skill has a manually maintained divergent mirror;
- fresh-session replay and at least one failure case are recorded before `verified`;
- the portfolio skill audit has no personal absolute paths, malformed skill files, generic canonical project names, or verification false-green for skills that claim completion evidence.
