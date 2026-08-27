# OpenForge Architecture Decision Records

OpenForge is a standards repository. A change can affect many downstream OSS projects, so important decisions must preserve not only **what** the current rule is, but **why** it was selected, which alternatives were rejected, and how a future maintainer can supersede it safely.

## When an ADR is required

Create or update an ADR when a decision:

- changes a rule intended for multiple repositories;
- changes architecture, security, supply-chain, release, compatibility, agent-engineering, design-system, governance, or repository policy;
- deliberately rejects a credible alternative;
- widens or narrows a trust/access boundary;
- creates a compatibility or migration obligation;
- changes a default that downstream repositories are expected to inherit;
- is likely to be revisited later and needs historical rationale.

Do not create an ADR for typo fixes, wording-only improvements, routine dependency refreshes that do not change policy, or implementation details already determined by an accepted ADR.

## Status

- `Proposed` — under discussion; not yet normative.
- `Accepted` — current decision.
- `Superseded` — replaced by another ADR; retained for history.
- `Deprecated` — no longer recommended, without a direct replacement.
- `Rejected` — considered but intentionally not adopted.

Accepted ADRs are immutable historical records. If a decision changes materially, create a new ADR and mark the previous one `Superseded` rather than rewriting history.

## ADR format

Each ADR should contain:

1. Status and date
2. Context
3. Decision
4. Alternatives considered
5. Rationale
6. Consequences and trade-offs
7. Affected standards/templates/projects
8. Migration or adoption notes when relevant
9. Related issues, implementation/adoption records, and supersession links

## Decision index

The first ADR pass retrospectively captures high-impact common decisions already embodied in OpenForge standards. It is intentionally selective: not every existing document deserves a separate ADR.

| ADR | Decision | Status | Primary standards |
|---|---|---|---|
| [0001](0001-record-cross-project-decisions.md) | Record cross-project decisions as ADRs | Accepted | governance, change management |
| [0002](0002-english-canonical-korean-first-class.md) | English canonical; Korean first-class translation | Accepted | documentation, i18n |
| [0003](0003-risk-based-oss-security-governance.md) | Use risk-based security/governance for OSS | Accepted | security, governance, exceptions |
| [0004](0004-treat-ai-and-plugins-as-untrusted-input.md) | Treat AI instructions/plugins as untrusted execution inputs | Accepted | AI security, plugin supply chain |
| [0005](0005-require-workflow-impact-analysis-for-upgrades.md) | Require workflow-wide impact analysis for upgrades | Accepted | change management, compatibility |
| [0006](0006-build-security-into-release-supply-chain.md) | Integrate security and supply-chain controls into lifecycle | Accepted | CI, release, supply chain |
| [0007](0007-design-system-standardizes-semantics-not-identity.md) | Standardize UI semantics, not product identity | Accepted | design system |
| [0008](0008-layer-agent-instructions-and-keep-root-context-small.md) | Layer agent instructions and keep root context small | Accepted | agent engineering |
| [0009](0009-evidence-first-agent-verification-and-convergence.md) | Require evidence-first verification and convergence | Accepted | agent engineering |
| [0010](0010-reusable-templates-are-adaptable-baselines.md) | Treat reusable templates as adaptable baselines | Accepted | templates, repository standard |
| [0011](0011-ci-resilience-must-not-encourage-security-bypass.md) | CI resilience must not encourage blind security bypass | Accepted | CI resilience, CI security |
| [0012](0012-document-and-time-bound-intentional-exceptions.md) | Document and time-bound intentional exceptions | Accepted | security exceptions, governance |

## Relationship to standards and adoption records

```text
ADR
  explains why a durable decision exists
        ↓
Standard
  defines the current normative rule
        ↓
Template / CI / Policy
  makes the rule reusable or enforceable
        ↓
Adoption record / Issue / PR
  records where and how it was applied
```

An adoption record such as `docs/agent-engineering-adoption-2026-08.md` is therefore complementary to an ADR: the ADR explains the decision; the adoption record explains the rollout.
