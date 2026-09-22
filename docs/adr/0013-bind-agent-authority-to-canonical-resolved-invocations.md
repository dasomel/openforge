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
- retries or long-running phases reuse authority beyond its intended scope or lifetime;
- an agent that can mint or replay its own execution authority can bypass a correct policy decision at the final enforcement boundary.

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
11. Keep the policy decision point (PDP), grant issuer/signer, policy enforcement point (PEP), and executor as explicit logical responsibilities. For high-risk operations, the PEP verifies the concrete invocation grant and, where single-use semantics apply, atomically consumes the grant before or at executor handoff.
12. The agent/model runtime must not possess the signing authority that can mint arbitrary execution grants. A consumed single-use grant cannot be replayed to authorize a second execution.

## Execution grant enforcement boundary

The following is a logical trust model, not a requirement to deploy separate products or processes:

```text
Canonical ResolutionArtifact
          │
          ▼
PDP / Authorization Decision
          │
          ▼
Grant Issuer / Signer
(action-bound child grant)
          │
          ▼
Human Approval (when required)
          │
          ▼
PEP
- verify resolution/invocation binding
- verify expiry/revocation
- verify approval binding
- atomically consume spend-once grant where required
          │
          ▼
Executor / Tool
          │
          ▼
Post-state verification + evidence
```

A session grant remains an authority ceiling and is not itself an unrestricted execution token. The concrete child grant is derived only after resolution and is bound to the exact invocation that the PEP will enforce.

Where replay would create duplicate or unsafe side effects, the PEP must maintain an atomic consumed-state or equivalent idempotency primitive so the same grant cannot be spent twice. Retrying a request does not imply reusing execution authority; a retry that requires another side effect must follow the policy-defined reauthorization/idempotency path.

The signer/issuer may be implemented alongside the PDP or another trusted control-plane component, and the PEP may be colocated with the executor, provided the responsibilities remain independently testable. The agent/model process itself must not be able to mint valid grants simply because it can request or propose a tool call.

## Alternatives considered

- Give each agent a broad static service credential and rely on tool code to behave safely.
- Authorize only the natural-language intent or pre-resolution tool selection.
- Bind approval to a generic operation/boolean without exact tool and argument identity.
- Generate authorization grants and sandbox rules independently from the same policy source.
- Treat kernel/container sandbox denial as sufficient proof of correct request-side authorization.
- Let the agent hold the credential/key that signs its own execution grants.
- Treat a valid grant as indefinitely replayable until its TTL expires.
- Require one specific sandbox or evidence-attestation implementation across all projects.

## Rationale

The same canonical resolved invocation must be visible across recommendation, authorization, approval, enforcement, and evidence. This closes semantic drift that cannot be detected by comparing configuration files alone.

Layering session ceilings with invocation-level attenuation limits the blast radius of long-lived agent sessions. Exact-invocation approval and executor revalidation make authorization independently checkable. Separating request-side decisions from sandbox enforcement avoids confusing a last-line containment mechanism with the earlier policy decision.

Explicit PDP/issuer/PEP/executor responsibilities close another gap: a correct authorization decision is not sufficient if the final execution point cannot prove that it is consuming the exact authority issued for that invocation. Spend-once semantics provide replay resistance for non-idempotent or high-impact operations, while keeping the signing authority outside the agent prevents the requester from self-authorizing.

Keeping implementation mechanisms pluggable preserves portability across Kubernetes control planes, desktop/local AI runtimes, data platforms, node sandboxes, and service-specific tools.

## Consequences

- Agent-enabled projects need stable tool contracts and deterministic argument normalization/canonicalization.
- High-risk executions carry more metadata and may require additional short-lived grant issuance and approval flow.
- PEP implementations need replay/idempotency state when grants are defined as single-use.
- Signing/issuance credentials require a trust boundary separate from the agent/model runtime.
- Tests must cover request-side denial, grant-binding mismatch, expired/revoked grants, replay of consumed grants, and effective sandbox/runtime enforcement.
- Evidence schemas must preserve enough version, digest, grant, and consume-result information for later replay/recomputation.
- Projects without agent-driven mutation can adopt only the relevant reduced profile.
- Existing approval/evidence implementations may need migration to bind exact resolved invocations.

## Affected standards / projects

- `docs/agent-execution-security.md`
- `docs/agent-engineering.md`
- Narwhal #73/#155 — reference control-plane implementation input
- Narwhal Portal #41/#78 — portal/MCP adoption
- KubeMetal #4/#10/#28 — local agent/ChatOps/remediation adoption
- Beluga #108 — data-platform operations agent adoption
- kube-ready-box #11/#16 — sandbox/runtime enforcement evidence provider
- service-specific adoption where appropriate: nfs-quota-agent, ldapium, ClusterDeck

## Adoption notes

OpenForge owns the reusable contract. Individual repositories own their concrete policy model, tool catalog, runtime implementation, grant issuance/signing mechanism, PEP placement, and evidence storage.

Adoption should not copy the full Narwhal issue verbatim. Each repository should declare which profile applies, identify its mutation/egress/privilege boundaries, and prove the common security properties with repository-specific tests.
