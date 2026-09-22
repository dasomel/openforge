# Decision Management Standard

English | [한국어](decision-management-ko.md)

OpenForge manages durable cross-project engineering decisions as first-class project artifacts.

The normative rule is simple: **if a change alters a reusable OpenForge default and future maintainers are likely to ask why, evaluate it for an ADR before merge.**

## Decision layers

```text
Research / operating evidence
        ↓
Issue / proposal
        ↓
ADR — why this durable choice was made
        ↓
Standard — what the current rule is
        ↓
Template / CI / Policy — how it is reused or enforced
        ↓
Adoption record — where and when it was applied
        ↓
Feedback / new evidence
        └──────────────→ new decision when needed
```

## ADR threshold

An ADR is normally required when a change:

- affects defaults intended for multiple repositories;
- changes architecture or an abstraction/layer boundary;
- changes trust, access, privilege, identity, secret, or release boundaries;
- changes security, supply-chain, compatibility, release, CI resilience, agent-engineering, design-system, governance, or repository policy;
- deliberately chooses among credible alternatives with meaningful trade-offs;
- creates migration, compatibility, or downstream adoption obligations;
- changes a rule likely to be revisited later;
- supersedes a previously accepted cross-project decision.

An ADR is normally not required for:

- typo or wording-only fixes;
- routine implementation work fully determined by an accepted decision;
- dependency refreshes with no policy or contract change;
- project-local choices that are not being promoted as an OpenForge default.

## Required relationship

A durable decision SHOULD NOT exist only in an Issue, PR, chat transcript, or commit message.

When an ADR is accepted:

1. link the affected standard(s);
2. update or add reusable templates/policy/CI when enforcement is appropriate;
3. record downstream rollout separately when adoption is substantial;
4. link evidence, research, Issues, and implementation records;
5. maintain English canonical and Korean first-class documentation where the ADR is user-facing.

## Immutability and supersession

Accepted ADRs are historical records. Do not rewrite an old accepted rationale to match current thinking.

When the decision changes materially:

1. create a new ADR;
2. explain what changed and why;
3. mark the previous ADR `Superseded`;
4. cross-link both records;
5. update the normative standard and adoption guidance.

## Review gate

For non-trivial OpenForge changes, reviewers SHOULD answer:

- Does this change cross the ADR threshold?
- If yes, is the ADR present and linked?
- Does the standard reflect the accepted decision rather than historical discussion?
- Is deterministic enforcement moved to template/CI/policy where practical?
- Is migration/adoption impact recorded?
- Are English/Korean user-facing decision records synchronized?
- Does this supersede an existing ADR?

## Periodic audit

Decision history should be audited periodically rather than only when a new ADR is created.

Audit for:

- standards with durable rationale but no ADR;
- ADRs not linked from their standards;
- accepted ADRs whose implementation has drifted;
- duplicated or contradictory decisions;
- stale exceptions or migrations;
- English/Korean drift;
- adoption records with no decision linkage;
- decisions implemented in reference OSS but not yet generalized into OpenForge.

## References

- [ADR index](adr/README.md)
- [ADR template](../templates/ADR.md)
- [Change Management Standard](change-management.md)
- [Maintainer Governance](maintainer-governance.md)
- [Agent Engineering adoption record](agent-engineering-adoption-2026-08.md)
