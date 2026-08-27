# Agent Engineering Adoption — 2026-08

## Purpose

This document records the August 2026 portfolio-wide optimization of AI-assisted development instructions across Dasomel OSS repositories.

The change was motivated by repeated experience with coding agents and by community discussion around `AGENTS.md`/`agent.md`: repository instructions can materially improve generated-code quality, but an oversized always-loaded instruction file can also dilute context, duplicate deterministic lint rules, and obscure the project-specific constraints that matter most.

This is an adoption record, not a replacement for [`agent-engineering.md`](agent-engineering.md). The canonical standard remains there.

## Decision

Adopt a layered instruction model across active OSS repositories:

```text
AGENTS.md
  -> concise, high-priority execution contract
  -> scope / architecture boundaries / verification / stop conditions

CODING_STANDARDS.md
  -> detailed coding and review guidance

CONTRIBUTING.md / DESIGN.md / architecture docs
  -> repository-specific process and design context

CLAUDE.md / GEMINI.md / tool-specific files
  -> tool-specific behavior and high-value project gotchas

formatter / linter / tests / policy-as-code / CI
  -> deterministic enforcement
```

The objective is not to maximize the number of instructions. It is to maximize the signal of instructions that require engineering judgment.

## Rules adopted portfolio-wide

### 1. Smallest coherent change

Agents should make the smallest coherent change that solves the requested problem.

Unrelated findings are reported rather than silently fixed. This is intentionally different from optimizing for the fewest changed lines: minimum diff size must not create duplicate APIs, unnecessary wrappers, or worse abstractions.

### 2. Preserve architecture and access boundaries

Layer bypasses, API widening, exported symbol additions, `private -> internal/public` changes, RBAC expansion, and permission expansion are treated as design changes rather than incidental implementation details.

### 3. Bug fixes start with reproduction

Preferred flow:

```text
reproduce
  -> failing regression test or executable evidence
  -> minimal coherent fix
  -> same evidence passes
  -> relevant regression verification
```

A real executable reproduction is acceptable when a deterministic automated test is impractical, such as cluster, filesystem, SSH, browser SSO, VM, or hardware-dependent failures.

### 4. Evidence before completion claims

A green unit test does not automatically prove a real runtime property. Completion reports should distinguish static checks, unit/stub tests, integration tests, build/package checks, security/policy checks, and real runtime/cluster/device/filesystem verification.

### 5. Comments explain why

Generated comments should explain invariants, hazards, compatibility constraints, intent, or non-obvious trade-offs. They should not narrate code that is already self-explanatory.

### 6. Deterministic rules belong in tools

Formatting, braces, import order, supported naming constraints, static analysis, dependency/security policy, generated-file checks, and tests should be enforced by formatter/linter/CI where practical instead of consuming permanent prompt context.

### 7. No arbitrary universal naming limit

Rules such as a universal 30-character function-name limit were deliberately not adopted. Repository and language conventions take precedence, especially where framework or generated APIs legitimately use long names.

### 8. Convergence over activity

Every substantive task should converge to one of three states:

- **A — Complete:** intended behavior works and appropriate verification passes.
- **B — Meaningful progress:** one verified blocker is removed and the next blocker is isolated with evidence.
- **C — Stop:** further work requires unjustified scope expansion, fragile workarounds, unsupported assumptions, or unacceptable risk.

Repeated patch generation without stronger evidence is not progress.

## Repository adoption

The first adoption pass covered the active portfolio, including:

- `openforge`
- `narwhal`
- `narwhal-portal`
- `beluga`
- `beluga-manager`
- `kubemetal`
- `clusterdeck`
- `ldapium`
- `nfs-quota-agent`
- `egovframe-launcher`
- `kube-ready-box`

The common contract is intentionally adapted rather than blindly copied. Existing project-specific guidance remains authoritative where it captures real operational knowledge.

### Notable repository decisions

**nfs-quota-agent**

Its existing `CLAUDE.md` contains high-value quota/filesystem gotchas, stub-vs-real verification limits, privileged execution constraints, and high-risk command paths. These are preserved and referenced rather than replaced with generic rules.

**Beluga**

Existing source-of-truth, isolated kubeconfig, ArgoCD self-heal, namespace/FQDN, and direct-entrypoint verification rules remain project-specific operational constraints.

**Narwhal Portal**

The Next.js-generated agent instruction block is preserved. Portfolio engineering rules are additive and must not remove framework-generated safety guidance.

**ClusterDeck / KubeMetal / Beluga Manager / ldapium / eGovFrame Launcher**

Root agent contracts emphasize their respective architecture and security boundaries instead of generic style preferences.

**kube-ready-box**

The repository has an unusually large `AGENTS.md` containing valuable Packer/VirtualBox/VMware/NixOS failure history together with model-routing and token-strategy guidance. This is treated as a context-dilution remediation case: preserve the knowledge, but move optional orchestration and historical details into linked playbook/mistake documents while keeping the root contract concise.

## OpenForge tracking

The adoption is tracked through the following engineering work:

- `openforge#12` — context-efficient AGENTS / coding standards / TDD / convergence model
- `openforge#13` — reusable agent-engineering documentation and templates
- `openforge#14` — move deterministic rules into lint/CI
- `openforge#15` — repository-specific agent instruction audit matrix
- `narwhal#170` — active OSS portfolio adoption tracker
- `kube-ready-box#31` — split oversized AGENTS into concise contract + playbook

## Review checklist for future repositories

When a new OSS repository adopts OpenForge, review the following before adding a large instruction file:

- What information cannot be inferred reliably from the code?
- Which architecture/security boundaries must never be bypassed casually?
- What are the canonical build, test, lint, and runtime verification commands?
- Which historical gotchas are important enough to load for every task?
- Which rules can be moved to formatter, linter, tests, or CI?
- Does the repository distinguish mocked evidence from real runtime evidence?
- Can a bug be reproduced before a fix is attempted?
- Are unrelated changes explicitly excluded from normal task scope?
- Does the agent know when to stop rather than accumulate fragile patches?

## Expected outcome

The intended result is a repository environment in which AI agents spend less context on generic style instructions and more attention on architecture, invariants, risk, and verification.

The standard should continue to evolve from actual review failures. New rules should be added only when they prevent a recurring class of mistake or encode project knowledge that tooling and code structure cannot express reliably.
