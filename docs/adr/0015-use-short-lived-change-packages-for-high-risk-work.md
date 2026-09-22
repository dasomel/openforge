# ADR-0015: Use short-lived Change Packages for high-risk work

- Status: Accepted
- Date: 2026-09-18

English | [한국어](0015-use-short-lived-change-packages-for-high-risk-work-ko.md)

## Context

OpenForge already defines change classes, impact analysis, ADRs, verification, evidence and portfolio governance. Those controls are strongest during review and after implementation, but larger changes can still begin before the problem, scope, requirements, acceptance scenarios and verification approach are fixed as one reviewable unit.

Issue templates capture proposals and impact, but they do not consistently preserve requirement-to-task-to-evidence traceability. Introducing a complete parallel specification hierarchy for every change would duplicate code, tests, documentation and ADRs, create drift and impose disproportionate process on small changes.

## Decision

OpenForge will use a risk-scaled, short-lived Change Package:

1. Class A changes use the existing Issue/PR workflow without a separate package.
2. Class B changes require acceptance criteria; a full package remains optional unless the work is complex, cross-component or operationally risky.
3. Class C and D changes require an accepted Change Package before broad implementation.
4. The package records problem, intent, scope/non-goals, stable requirements, acceptance scenarios, decisions, impact analysis, tasks, verification, expected evidence, and rollout/rollback/recovery where applicable.
5. Requirements, tasks and evidence remain traceable through stable identifiers.
6. Exploration, reproduction and reversible prototypes may precede acceptance, but cannot silently establish the final contract or mutate production/shared environments.
7. At completion, durable truth is promoted to code/tests, normative documentation, ADRs, evidence records and portfolio status. The Issue/PR and Git history are the default archive.
8. OpenForge will not introduce a parallel long-lived system-specification tree.

Reusable templates live under `templates/change/`. Projects may maintain the package directly in an Issue/PR or use temporary working-branch files when versioned collaboration is useful.

## Alternatives considered

### Adopt a complete external spec-driven framework

Rejected as the default. OpenForge already owns overlapping Issue, ADR, evidence, agent, CI and portfolio contracts. A second lifecycle and command layer would create duplicate governance and tool coupling.

### Require a package for every change

Rejected. Documentation fixes and small internal changes do not justify the same ceremony as runtime, release or security-boundary changes.

### Keep only Issue and PR prose

Rejected for higher-risk work. Free-form prose does not reliably preserve scope, testable requirements, verification planning or evidence traceability before implementation.

### Permanently archive every package in the repository

Rejected. Long-lived packages would duplicate the artifacts that own current truth and would predictably drift. A package is retained only when it remains useful operational documentation.

## Rationale

Risk scaling adds discipline where a wrong or incomplete contract has meaningful cost without slowing routine maintenance. A reviewed change-scoped contract also gives human and agent implementers a stable target while preserving OpenForge's evidence-first workflow. Promoting durable facts to their owning artifacts keeps the repository from developing a second, stale specification hierarchy.

## Consequences and trade-offs

- Class C/D work gains an explicit pre-implementation review gate.
- Reviewers can trace requirements through implementation and verification evidence.
- Complex work has additional authoring and review overhead.
- Maintainers must re-review material scope changes rather than allowing silent expansion.
- Downstream projects need to adopt the templates and PR fields deliberately; existing Class A/B workflows remain compatible.
- The Change Package cannot replace ADRs, tests, normative documentation, evidence records or portfolio status.

## Affected standards, templates, and projects

- `docs/change-management.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/pull_request_template.md`
- `templates/change/`
- `templates/AGENTS.md`
- `templates/SKILL.md`
- `templates/github/pull_request_template.md`
- downstream OpenForge projects adopting Class C/D workflow controls

## Migration and adoption

This is backward compatible for Class A and routine Class B work. Downstream repositories should adopt the Change Package templates and PR contract when they next update change-management guidance. Existing completed changes do not require retroactive packages.

## Evidence and references

- Change-management standard and templates in this change
- Related ADRs: ADR-0001, ADR-0005, ADR-0009, ADR-0010
