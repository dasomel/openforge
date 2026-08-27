# ADR-0009: Require evidence-first verification and convergence for agent work

- Status: Accepted
- Date: 2026-08-27
- Related adoption record: `docs/agent-engineering-adoption-2026-08.md`

## Context

Coding agents can produce plausible patches and completion claims without proving the affected runtime path. They can also continue generating patches after the work has stopped converging.

## Decision

For bug fixes, prefer reproduction before implementation: failing regression test or executable evidence, then the smallest coherent fix, then the same evidence passing and relevant regression verification.

Completion reports distinguish evidence classes and substantive tasks converge to A/B/C:

- A — complete and verified;
- B — meaningful progress with one verified blocker removed and the next isolated;
- C — stop when further work requires unjustified scope, fragile patches, unsupported assumptions, or unacceptable risk.

## Alternatives considered

- Patch first, add tests afterward.
- Treat a passing unit test as sufficient evidence for all runtime properties.
- Continue iterating until the agent reports success.

## Rationale

Evidence constrains hallucination and makes partial progress useful. The convergence model prevents activity from being confused with engineering progress.

## Consequences

- Real cluster/device/filesystem/browser evidence may be required for some claims.
- Mock/stub evidence must not be presented as proof of higher-level runtime behavior.
- Agents are explicitly allowed and expected to stop with evidence rather than accumulate brittle workarounds.

## Affected standards

- `docs/agent-engineering.md`
- `templates/AGENTS.md`
- active OSS agent contracts
