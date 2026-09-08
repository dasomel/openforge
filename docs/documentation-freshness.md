# Documentation Freshness Standard

OpenForge treats documentation freshness as part of implementation evidence, not as a later publishing task.

## Lifecycle

```text
implementation
  -> executable evidence
  -> documentation impact review
  -> user/operations/security docs update when required
  -> blog/project-story impact review
  -> merge / release
```

A merged change is not permission to describe planned behavior as implemented. User-facing claims must remain bound to behavior that exists on the referenced main/release state.

## Status language

Use explicit lifecycle language when a capability is not generally available:

- `planned` — accepted direction, not implemented
- `experimental` — implemented for evaluation with unstable support expectations
- `implemented` — exists on the referenced main/release and has appropriate executable evidence
- `deprecated` — still present but scheduled for removal/replacement

## Changes that require documentation-impact review

Review documentation in the same change unit when modifying:

- user-visible capabilities or commands
- architecture, component ownership, or data flow
- authentication, authorization, RBAC, secrets, or security boundaries
- configuration, Helm values, flags, environment variables, APIs, or schemas
- supported runtime/platform/filesystem/Kubernetes versions
- install, upgrade, rollback, backup, restore, or incident procedures
- externally visible failure modes or operational recovery
- metrics or published quantitative claims

A dependency-only bump, formatting-only change, or internal refactor can normally declare `none` when it does not alter those contracts.

## Evidence requirements

Documentation claims should point to or be reproducible from one or more of:

- implementation path / committed configuration
- automated test or regression test
- CI/build/package evidence
- real integration/runtime verification when required by the claim
- release artifact, checksum, SBOM, or provenance where relevant
- reproducible command that demonstrates the behavior

Do not use a unit test to support a claim that specifically depends on a real cluster, filesystem, browser, identity provider, VM, hardware device, or external service.

## Numeric and version claims

Prefer one canonical source for test counts, supported versions, incidents, compatibility, and adoption metrics. Generated views should consume that source instead of copying values into multiple prose documents.

If duplication is unavoidable, add a deterministic freshness check or clearly identify which copy is authoritative.

## Blog / portfolio synchronization

`dasomel.github.io` project/docs/post content is downstream presentation state. Its upstream OSS repository remains the implementation source of truth.

The following are strong blog/project-update candidates:

- new user-facing capability
- significant architecture change
- operational/incident lesson
- new platform/runtime/filesystem support
- material security or supply-chain improvement
- reusable engineering lesson proven in production-like or real runtime evidence

Blog content must distinguish current behavior from roadmap/experiment state and should record the upstream project/revision or release when practical.

## PR contract

Every substantive PR should answer:

- Documentation impact: `none`, `updated`, or `follow-up-required`
- Blog / portfolio impact: `none`, `candidate`, or `updated`
- Evidence supporting current-state claims
- Any known stale document intentionally left behind and its tracking issue

`follow-up-required` is not a silent exemption. It must identify why the documentation cannot be safely updated in the same change and where the follow-up is tracked.

## Human judgment boundary

A link checker can prove that a link resolves; it cannot prove that an architecture explanation is accurate. A generated version table can eliminate copy drift; it cannot decide whether a user needs a migration warning.

OpenForge therefore separates deterministic freshness checks from maintainer review of meaning, usability, architecture coherence, and operational clarity.
