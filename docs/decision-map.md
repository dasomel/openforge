# OpenForge Decision Map

English | [한국어](decision-map-ko.md)

This map connects durable OpenForge decisions to the standards, reusable enforcement, and adoption evidence that implement them.

It is a navigation aid, not a second source of truth. ADRs explain **why**, standards define **what**, templates/CI/policy implement **how**, and adoption records show **where/when**.

| ADR | Durable decision | Normative standard(s) | Reusable enforcement / adoption |
|---|---|---|---|
| [0001](adr/0001-record-cross-project-decisions.md) | Record durable cross-project decisions | [Decision Management](decision-management.md), [Change Management](change-management.md) | `templates/ADR.md`, ADR index, contributing review gate |
| [0002](adr/0002-english-canonical-korean-first-class.md) | English canonical, Korean first-class | [Documentation](documentation.md), [Internationalization](i18n.md) | `-ko.md` filename convention, CI filename validation |
| [0003](adr/0003-risk-based-oss-security-governance.md) | Risk-based OSS security/governance | [Security](security.md), [Maintainer Governance](maintainer-governance.md), [Security Exceptions](security-exceptions.md), [Branch Protection](branch-protection.md) | risk-based controls, branch protection baseline, and exception records |
| [0004](adr/0004-treat-ai-and-plugins-as-untrusted-input.md) | Treat AI/plugin inputs as untrusted executable influence | [AI Engineering Security](ai-engineering-security.md), [Plugin Supply Chain](plugin-supply-chain.md) | plugin intake policy, repository-agent security constraints |
| [0005](adr/0005-require-workflow-impact-analysis-for-upgrades.md) | Workflow-wide impact analysis for upgrades | [Change Management](change-management.md), [Upgrade Compatibility](upgrade-compatibility.md) | impact matrix, workflow inventory, compatibility evidence |
| [0006](adr/0006-build-security-into-release-supply-chain.md) | Lifecycle security and supply-chain controls | [Supply Chain](supply-chain.md), [CI Security](ci-security.md), [Release Security](release-security.md) | SBOM/provenance, policy checks, release verification templates |
| [0007](adr/0007-design-system-standardizes-semantics-not-identity.md) | Standardize semantics without erasing product identity | [OSS Design System](design-system.md) | `templates/DESIGN.md`, Figma design system, project archetypes |
| [0008](adr/0008-layer-agent-instructions-and-keep-root-context-small.md) | Layer agent instructions and keep root context small | [Agent Engineering](agent-engineering.md) | `templates/AGENTS.md`, `templates/CODING_STANDARDS.md`, portfolio rollout |
| [0009](adr/0009-evidence-first-agent-verification-and-convergence.md) | Evidence-first agent verification and convergence | [Agent Engineering](agent-engineering.md) | bug-first workflow, A/B/C convergence, [2026-08 adoption record](agent-engineering-adoption-2026-08.md) |
| [0010](adr/0010-reusable-templates-are-adaptable-baselines.md) | Templates are adaptable baselines | [Repository Standard](repository.md) | `templates/` catalog, explicit placeholders and adaptation guidance |
| [0011](adr/0011-ci-resilience-must-not-encourage-security-bypass.md) | CI resilience must preserve assurance | [CI Resilience](ci-resilience.md), [CI Security](ci-security.md) | explicit degraded-state/fallback handling, security exception path |
| [0012](adr/0012-document-and-time-bound-intentional-exceptions.md) | Intentional exceptions are documented and revisited | [Security Exceptions](security-exceptions.md), [Maintainer Governance](maintainer-governance.md) | expiry/review fields, `DESIGN.md` deviation table, change records |

## Audit use

During a periodic OpenForge audit, use this map to check four directions:

1. **ADR → Standard** — every accepted decision still has a normative home.
2. **Standard → Enforcement** — deterministic parts are automated where practical.
3. **Enforcement → Adoption** — reference OSS actually consume the reusable practice.
4. **Adoption → Feedback** — recurring project evidence is promoted back into a decision when it changes the common default.

If any link breaks, treat it as standards drift rather than ordinary documentation debt.
