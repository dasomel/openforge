# Portfolio Instruction-Debt Audit — 2026-09

This report records the coordinated second pass for OpenForge issues #83, #84, and #85.

## Scope

Initial active OSS batch:

| Repository | Result |
|---|---|
| `dasomel/narwhal` | Root contract changed to task-relevant inspection, risk-proportional verification, explicit autonomy boundary, and canonical OpenForge references. |
| `dasomel/narwhal-portal` | Root contract changed to task-relevant inspection while preserving the generated Next.js rule block; browser/auth/live integration evidence remains risk-scoped. |
| `dasomel/kubemetal` | Unconditional repository-wide reading removed. Existing architecture invariants and measured runtime gotchas retained because they are high-value project knowledge, not generic prompt policy. |
| `dasomel/nfs-quota-agent` | Root reading and verification requirements made task/risk relevant; Claude adapter no longer loads the verification skill for every change. Filesystem/kernel/privilege gotchas retained. |
| `dasomel/kube-ready-box` | Existing layered contract already uses a source map, project skill routing, and a separate 700+ line technical reference loaded by section. No mechanical rewrite required in this pass. |
| `dasomel/beluga` | Unconditional platform-document loading replaced by task-relevant source-map routing; user/live-cluster verification made proportional to affected paths. |
| `dasomel/beluga-manager` | Root contract changed to task-relevant guidance, explicit autonomy boundaries, and proportional verification. |
| `dasomel/ldapium` | Unconditional multi-document loading replaced by task-relevant routing; live LDAP/browser evidence remains required only when the affected property needs it. High-value OpenLDAP gotchas retained. |
| `dasomel/egovframe-launcher` | Root contract changed to task-relevant project-skill loading and proportional real-toolchain verification. |

## CLAUDE.md findings

The reviewed `CLAUDE.md` files are already thin adapters that import/reference `AGENTS.md`, route to project skills, and keep Claude-specific harness behavior separate. They were not expanded with duplicated canonical policy.

One actionable exception was `nfs-quota-agent`, where the adapter previously required the verification skill before every completion claim. It now activates only for quota/runtime/user-visible changes that need evidence beyond ordinary local checks.

## Skill findings

The portfolio contains canonical project skills plus some legacy Claude skill names kept as compatibility routers. These adapters explicitly redirect to canonical project skills rather than carrying duplicate workflows. They are therefore compatibility shims, not model-specific prompt forks.

No model-generation-specific prompt fork was introduced. OpenForge policy remains model-agnostic; any future model/runtime override requires repeated observed failure evidence, an eval/reproduction, a narrow mitigation, and a review/removal condition.

## What was intentionally retained

Instruction cleanup must not destroy repository-specific knowledge that prevents known failures. The second pass therefore retained:

- KubeMetal control/compute, bridge, port, MLX/Tauri, deploy-target, and measured runtime invariants;
- NFS Quota filesystem rounding, kernel-module, privilege, host-file, and enforcement-evidence constraints;
- LDAPium OpenLDAP ACL/replication/accesslog and live-server testing constraints;
- Beluga GitOps/shared-cluster safety and real gateway/auth entry-path requirements;
- Kube Ready Box provider/architecture and historical build invariants.

These are high-value constraints. Future cleanup should move them behind progressive disclosure only when the destination preserves discoverability for the affected task.

## Resulting portfolio contract

```text
OpenForge canonical standards
  -> AGENTS.md: minimal persistent project invariants + boundaries + completion contract
  -> project skills: narrow task-specific workflows
  -> references/scripts: progressive detail and executable checks
  -> CLAUDE.md/tool adapters: runtime routing only
  -> validation: proportional to task risk and user impact
```

Safe local/disposable inspect-edit-build-test-fix-retest loops may proceed without repeated approval when already inside the requested scope. Shared, production, destructive, release/publish, credential/permission, or unrelated external mutations remain authorization boundaries.

## Verification and limitation

This pass verified the current repository instruction files through the GitHub source after changes and recorded commit-level adoption in issue #85. It did not execute each repository's runtime test suite because the changes are repository guidance rather than product/runtime code, and GitHub commit status availability varies by repository. No runtime correctness claim is made from this documentation-only rollout.

Future portfolio audits should use `templates/scripts/audit-instruction-debt.py` plus representative before/after task evals. Improvement is measured by verified task outcomes, unnecessary reads/tool calls, approval interruptions, context cost, skill activation quality, and preserved high-value constraints — not by prompt size alone.
