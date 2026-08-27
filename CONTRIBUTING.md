# Contributing

English | [한국어](CONTRIBUTING-ko.md)

Thank you for contributing.

## Before you start

- Check existing Issues and Pull Requests.
- Open an Issue for significant feature, architecture, security, governance, compatibility, release, agent-engineering, or design-system changes.
- Check the [Decision Management Standard](docs/decision-management.md) when a change may alter a reusable OpenForge default.
- Keep changes small and reviewable.

## ADR gate

Before implementing a durable cross-project policy change, determine whether it crosses the ADR threshold.

An ADR is normally required when the change affects multiple repositories, changes architecture/trust boundaries, deliberately selects among meaningful alternatives, creates migration obligations, or supersedes an accepted decision.

Use [`templates/ADR.md`](templates/ADR.md) and keep the Korean first-class counterpart synchronized with [`templates/ADR-ko.md`](templates/ADR-ko.md).

Do not create ADR noise for typo fixes, wording-only changes, or project-local implementation details already covered by an accepted decision.

## Pull Requests

- Use a focused branch.
- Follow Conventional Commits.
- Link the related Issue.
- Link the ADR when the change crosses the ADR threshold.
- Explain tests, evidence, migration/adoption, and documentation impact.
- Keep English and Korean user-facing documentation synchronized.
- Identify any accepted ADR that the change supersedes.

## Review questions

For non-trivial changes, reviewers should ask:

- Does this change alter a reusable OpenForge default?
- Is a new ADR required or is an existing ADR authoritative?
- Does the normative standard reflect the decision?
- Can deterministic requirements be enforced in CI/policy/templates instead of prose only?
- Are downstream adoption and exceptions documented?
- Are English/Korean decision records synchronized?
