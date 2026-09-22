# OpenForge Engineering Operating Model

OpenForge treats a repository as an engineering execution context, not only as source storage.

> OpenForge turns engineering intent into reproducible, testable, reviewable, and recoverable systems.

This document is the umbrella operating model. It does not replace the more specific Agent Engineering, Agent Execution Security, Documentation Freshness, Portfolio, Release, or Supply-chain standards; it explains how those controls compose into one lifecycle.

## Lifecycle

```text
Intent
  -> Constraints
  -> Repository Context / Instructions
  -> Human or Agent Implementation
  -> Executable Checks
  -> Evidence
  -> Human Review / Stewardship
  -> Release / Rollback
  -> Observe
  -> Learning Loop
```

A change is not complete merely because code was generated or merged. Completion means that the intended behavior exists at the relevant boundary, the applicable verification passed, evidence is retained, and the release/recovery implications are understood.

## 1. Intent as specification

Substantive work should make the following explicit when they materially affect implementation:

- goal and user/system value
- scope and non-goals
- constraints and forbidden changes
- acceptance criteria
- risks and failure modes
- verification/evidence class
- release/rollback impact

An issue, ADR, spec, or concise work instruction may carry this information. The format is less important than making consequential intent reviewable instead of forcing an implementer or agent to guess it.

## 2. Constraints as policy

Constraints are layered by how objectively they can be enforced.

- **Declarative:** architecture, contribution, security, compatibility, operational guidance.
- **Executable:** lint, tests, schema validation, policy-as-code, dependency/supply-chain checks, CI gates.
- **Judgment:** architecture coherence, user value, maintainability, community fit, usability, ethical/organizational impact.

Deterministic rules should migrate toward executable checks when doing so is reliable. Judgment rules must not be converted into false-green automation merely because they are difficult to review.

## 3. Repository context and instructions

`AGENTS.md` is a repository-level engineering contract for humans and agents. It should stay concise and point to the relevant source-of-truth documents rather than duplicate every style rule.

The instruction hierarchy should answer:

- what the system is and what it is not
- which boundaries are high risk
- which source files own generated state
- which build/test/verification entrypoints are canonical
- what evidence is required before a completion claim
- when the correct convergence state is to stop and escalate

See `agent-engineering.md` for the detailed contract and executable audit model.

## 4. Implementation is not authority

An AI agent, automation, or human contributor may produce a change, but implementation capability does not transfer governance authority.

Where tools can mutate hosts, clusters, identity, data, or external systems, repository instructions are not an authorization boundary. Apply the Agent Execution Security Contract: resolve concrete invocation once, validate/authorize it, attenuate authority, bind approval where required, enforce at runtime, verify post-state, and retain recomputable evidence.

## 5. Rules as executable checks

A written requirement that is objectively machine-verifiable should have an executable owner when practical.

Examples:

```text
"release contains an SBOM"
        -> release artifact validation

"generated files stay synchronized"
        -> regeneration + git diff gate

"portfolio status is canonical"
        -> schema validation + deterministic dashboard generation

"high-risk agent behavior needs evidence"
        -> behavior/eval gate
```

The rule registry and agent audit exist to prevent a prose-only statement from being mistaken for an enforced control.

## 6. Evidence over claims

A statement such as "tests passed" or "implemented" is metadata about evidence, not the evidence itself.

Keep evidence classes distinct:

- unit/stub/mock
- integration
- real runtime / cluster / filesystem / browser / identity-provider / hardware
- static analysis and policy
- build/package
- SBOM/provenance/signature
- post-state verification

Do not use a lower evidence class to claim a stronger property. A mocked command runner can prove argv construction; it cannot prove a real kernel enforced the requested quota.

## 7. Human stewardship

Human responsibility shifts from writing every line toward owning boundaries and consequences:

- architecture and product direction
- permission/risk boundaries
- trade-offs and exceptions
- evidence sufficiency
- release decision
- rollback/recovery readiness
- maintainability and community quality

Automation should reduce repetitive work without erasing accountable review.

## 8. Failure is a first-class design object

Major workflows should define, when relevant:

- explicit failure conditions
- partial/indeterminate outcomes
- timeout and retry semantics
- idempotency/deduplication
- retained failure evidence
- rollback/recovery path
- manual intervention point

For agentic workflows, `partially succeeded` is not equivalent to either success or clean failure and should be represented explicitly when side effects may already have occurred.

## 9. Release and rollback

Prefer reproducible and reversible automation over automation alone.

Important properties include:

- versioned source and dependencies
- pinned or recorded build inputs
- immutable artifacts where practical
- release provenance
- migration compatibility
- rollback or forward-recovery plan
- verification after rollout

## 10. Documentation and learning loop

Implementation changes that affect users, architecture, operations, security, compatibility, or public capability claims must pass the Documentation Freshness review.

Operational findings, incidents, benchmarks, contributor feedback, and adoption results feed the next intent or standard. The loop is human-governed: OpenForge may generate observations or proposals, but it does not autonomously redefine project goals.

## Maturity model

| Level | Meaning | Minimum emphasis |
|---|---|---|
| 0 | Repository | source, README, license |
| 1 | Structured Project | contribution/security docs, basic CI |
| 2 | Automated Engineering | build/test/lint/security/release automation |
| 3 | Agent-Ready Repository | concise instructions, explicit boundaries, deterministic entrypoints |
| 4 | Evidence-Driven Engineering | provenance, runtime evidence, rollback/recovery, executable governance |
| 5 | Human-Governed Learning System | operational feedback and improvement proposals connected to standards |

Level 5 does **not** mean an autonomous repository. Human stewardship and approval boundaries remain authoritative.

## Relationship to current OpenForge controls

- `agent-engineering.md` — repository instruction and convergence contract
- `agent-execution-security.md` — tool/side-effect authorization and evidence
- `agent-behaviors.md` — executable behavioral evaluation
- `documentation-freshness.md` — implementation-to-documentation claim integrity
- `portfolio-dashboard.md` / portfolio registries — cross-project state and evidence
- `reproducible-build.md` / supply-chain standards — build and release integrity
- ADRs — durable architectural decisions

The operating model is therefore not a new parallel framework. It is the composition rule for controls already implemented across OpenForge.