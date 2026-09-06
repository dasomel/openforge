# ADR-0013: Bind agent authority to canonical resolved invocations

- Status: Accepted
- Date: 2026-09-07

## Context

AI/LLM agents and automation workers can select tools, resolve parameters, call APIs, execute Kubernetes or host operations, and produce real side effects. Traditional RBAC or a broad service credential does not by itself prove that the exact invocation reaching an executor was the operation that policy evaluated and a human approved.

Several failure modes are possible when authorization, approval, sandbox rendering, and execution each resolve the request independently:

- a read-looking intent resolves into a mutating call;
- target or arguments change after approval;
- a session retains authority that is broader than a concrete invocation needs;
- sandbox rules are generated from the same policy file but a different semantic resolution path;
- evidence records what should have happened without proving the request was denied before the side effect;
- retries or long-running phases reuse authority beyond its intended scope or lifetime.

Narwhal #155 and related portfolio discussions demonstrated that a portable cross-project contract is needed rather than repository-specific copies of the same security model.

## Decision

OpenForge standardizes a vendor-neutral Agent Execution Security Contract with these decisions:

1. Resolve the concrete tool invocation once into a canonical `ResolutionArtifact` that includes policy version, agent/session identity, tool contract version, resolved target, normalized arguments, normalization version, and invocation digest.
2. Authorization, capability grant issuance, human approval, sandbox-rule rendering, executor revalidation, and evidence generation use the same resolution artifact or a cryptographically bound equivalent.
3. Treat a session-scoped grant as an authority ceiling, not durable permission for every later call.
4. Use attenuated per-invocation or per-phase short-lived grants for mutating, destructive, privileged, exfiltrating, or otherwise high-risk operations.
5. Bind approval to the exact resolved invocation rather than a generic boolean approval state.
6. Revalidate grant/approval binding and expiry/revocation at side-effect or commit boundaries.
7. Keep request-side authorization and sandbox/runtime enforcement as distinct security layers and verify both independently.
8. Put decision-time enforcement data in the grant or bound resolution artifact; put explanatory, verification, correlation, and audit data in evidence.
9. Require recomputable evidence that links the authorization decision through grants, approval, runtime assertion, sandbox enforcement, actual execution, observed side effects, and post-state verification.
10. Keep cryptographic attestation and sandbox implementations pluggable; OpenForge specifies required security properties rather than a specific product or mechanism.

## Alternatives considered

- Give each agent a broad static service credential and rely on tool code to behave safely.
- Authorize only the natural-language intent or pre-resolution tool selection.
- Bind approval to a generic operation/boolean without exact tool and argument identity.
- Generate authorization grants and sandbox rules independently from the same policy source.
- Treat kernel/container sandbox denial as sufficient proof of correct request-side authorization.
- Require one specific sandbox or evidence-attestation implementation across all projects.

## Rationale

The same canonical resolved invocation must be visible across recommendation, authorization, approval, enforcement, and evidence. This closes semantic drift that cannot be detected by comparing configuration files alone.

Layering session ceilings with invocation-level attenuation limits the blast radius of long-lived agent sessions. Exact-invocation approval and executor revalidation make authorization independently checkable. Separating request-side decisions from sandbox enforcement avoids confusing a last-line containment mechanism with the earlier policy decision.

Keeping implementation mechanisms pluggable preserves portability across Kubernetes control planes, desktop/local AI runtimes, data platforms, node sandboxes, and service-specific tools.

## Consequences

- Agent-enabled projects need stable tool contracts and deterministic argument normalization/canonicalization.
- High-risk executions carry more metadata and may require additional short-lived grant issuance and approval flow.
- Tests must cover both request-side denial and effective sandbox/runtime enforcement.
- Evidence schemas must preserve enough version and digest information for later replay/recomputation.
- Projects without agent-driven mutation can adopt only the relevant reduced profile.
- Existing approval/evidence implementations may need migration to bind exact resolved invocations.

## Affected standards / projects

- `docs/agent-execution-security.md`
- `docs/agent-engineering.md`
- Narwhal #155 — reference control-plane implementation input
- Narwhal Portal #41/#78 — portal/MCP adoption
- KubeMetal #4/#10/#28 — local agent/ChatOps/remediation adoption
- Beluga #108 — data-platform operations agent adoption
- kube-ready-box #11/#16 — sandbox/runtime enforcement evidence provider
- service-specific adoption where appropriate: nfs-quota-agent, ldapium, ClusterDeck

## Adoption notes

OpenForge owns the reusable contract. Individual repositories own their concrete policy model, tool catalog, runtime implementation, and evidence storage.

Adoption should not copy the full Narwhal issue verbatim. Each repository should declare which profile applies, identify its mutation/egress/privilege boundaries, and prove the common security properties with repository-specific tests.
