# Agent Execution Security Contract

English | [한국어](agent-execution-security-ko.md)

OpenForge defines a reusable security contract for AI/LLM agents, MCP tools, automation workers, and other software actors that can read or mutate external systems.

The contract standardizes **authorization, capability attenuation, approval binding, sandbox enforcement, verification, and recomputable evidence** without prescribing a specific agent framework, policy engine, sandbox implementation, or attestation product.

## Core lifecycle

```text
request
  -> context
  -> tool selection
  -> parameter resolution
  -> canonical resolution artifact
  -> validation
  -> authorization
  -> session authority ceiling
  -> invocation/phase grant
  -> approval when required
  -> runtime decision assertion / revalidation
  -> sandboxed execution
  -> post-state verification
  -> recomputable evidence
  -> expiry / revocation
```

The default rule is **resolve once, then bind every later decision to the same resolved invocation**.

## Trust boundaries

Keep these identities and responsibilities separate:

- human identity
- agent identity
- workload/service identity
- policy decision
- capability grant
- human approval
- executor
- sandbox/runtime enforcement
- evidence recorder/verifier

An agent MUST NOT inherit unrestricted human administrator credentials merely because the human initiated the session.

Model output, retrieved documents, RAG context, tool output, and external content are data inputs. They are not authorization policy.

## Canonical resolution artifact

Parameter resolution MUST produce a canonical representation of the exact operation that could reach the executor.

Recommended fields:

```text
ResolutionArtifact
- resolution_id
- policy_version
- agent_identity
- session_id
- tool
- tool_contract_version
- resolved_target
- normalized_resolved_arguments
- normalized_invocation_version
- invocation_digest
```

Authorization, grant issuance, approval binding, sandbox-rule rendering, executor revalidation, and evidence generation SHOULD consume the same resolution artifact or a cryptographically bound equivalent.

Reading the same source policy file through independent resolution code paths is not sufficient: semantic drift can exist even when configuration files are identical.

## Capability attenuation

Use two levels of authority where risk justifies it.

### Session grant

The session grant defines the maximum authority ceiling for the session/run.

```text
SessionGrant
- grant_id
- agent_identity
- policy_version
- session_id
- allowed_capabilities
- allowed_targets/actions
- issued_at
- expires_at
```

The session grant MUST NOT silently authorize future calls whose resolved target or arguments exceed its original capability boundary.

### Invocation / phase grant

Mutating, destructive, privileged, exfiltrating, or otherwise high-risk operations SHOULD use a short-lived child grant derived from the session ceiling after concrete parameters are resolved.

```text
InvocationGrant
- invocation_grant_id
- parent_session_grant_id
- resolution_id
- agent_identity
- session_id
- policy_version
- tool
- tool_contract_version
- resolved_target
- resolved_arguments_digest
- normalized_invocation_version
- effective_capabilities
- issued_at
- expires_at
```

The executor MUST reject execution when the current invocation cannot reproduce the grant binding.

## Human approval

Approval is a first-class authorization object, not a generic `approved=true` flag.

High-risk approval SHOULD bind to the exact resolved invocation.

```text
Approval
- approval_id
- invocation_grant_id
- resolution_id
- invocation_digest
- approver
- decision
- approved_at
- expires_at
```

A useful digest covers at minimum:

```text
digest(
  agent_identity,
  session_id,
  policy_version,
  tool,
  tool_contract_version,
  resolved_target,
  normalized_resolved_arguments,
  normalized_invocation_version
)
```

Immediately before a side effect or commit boundary, the executor SHOULD revalidate the relevant grant/approval digest and current expiry/revocation state.

## Grant vs evidence boundary

Use this rule:

> Anything the executor must enforce at decision or execution time belongs in the grant or its bound resolution artifact. Everything needed only to explain, verify, correlate, or audit what happened belongs in evidence.

Evidence MUST NOT substitute for enforcement. Recording that a request should have been denied is not equivalent to denying it before the side effect.

## Sandbox and enforcement drift

A sandbox is a second enforcement layer, not a replacement for request-side authorization.

Where practical:

- authorization policy and sandbox rules derive from the same versioned policy source;
- more importantly, grant issuance and sandbox-rule rendering consume the same canonical resolution artifact/digest;
- runtime tests assert forbidden resolved requests are rejected before executor/sandbox handoff;
- separate negative probes verify the sandbox/kernel/container actually enforces the expected boundary;
- drift among declared policy, request-side decision, and effective sandbox/runtime enforcement fails visibly.

A kernel-side denial proves the sandbox boundary. It does not prove the request-side authorization path was correct.

## Revocation and long-running operations

Do not depend on arbitrary mid-syscall revocation.

- Revalidate grant expiry/revocation before side-effect or commit boundaries.
- Decompose long-running high-risk operations into phases with short-lived child grants where practical.
- A kill switch/revocation blocks future grant issuance and future commit phases.
- Failed or partial operations enter explicit recovery/rollback/hold state rather than silent retry loops.

## Recomputable execution evidence

Evidence is a first-class artifact.

Recommended fields:

```text
ExecutionEvidence
- evidence_id
- correlation_id
- resolution_id / invocation_digest
- request_authorization_decision
- request_authorization_assertion_digest
- session_grant_id
- invocation_grant_id
- approval_id / approval_digest
- agent_identity
- model / model_version
- policy_version
- tool / tool_contract_version
- normalized_invocation_version
- resolved_target
- resolved_arguments_hash
- effective_capabilities
- sandbox_policy_digest / enforcement_rules_digest
- pre_state_hash
- result / exit_code
- post_state_hash
- observed_side_effects
- started_at / completed_at
```

Evidence SHOULD link:

```text
request-side decision
  -> resolution artifact
  -> session grant
  -> invocation grant
  -> approval
  -> runtime assertion
  -> sandbox enforcement
  -> actual execution
  -> observed side effect
  -> post-state verification
```

Offline replay SHOULD be able to use the same policy snapshot, normalization/canonicalization version, agent/session context, tool contract, target, and resolved arguments to reproduce the authorization decision and validate the evidence envelope.

Hash chains, HMAC, signatures, append-only logs, TPM-backed attestation, transparency logs, or external verifiers may strengthen tamper evidence, but OpenForge does not require a specific mechanism.

## Minimum risk classes

Projects may adapt names, but the distinction should remain explicit:

- read-only / observational
- diagnostic with bounded side effects
- mutating
- destructive / irreversible
- privileged / host-level
- exfiltrating / external egress

Higher-risk classes require progressively stronger scope, credentials, approval, sandboxing, and verification.

## Required security properties

An adopting project should demonstrate that:

- no agent path inherits unrestricted human admin authority by default;
- every executable tool/capability has explicit scope and risk classification;
- authorization evaluates the fully resolved invocation, not only declared intent;
- high-risk calls use bounded, expiring authority;
- approvals are bound to exact invocation identity when approval is required;
- untrusted model/RAG/tool content cannot override authorization policy;
- request-side deny occurs before sandbox/executor handoff;
- sandbox/runtime enforcement is verified separately with negative probes;
- retries do not silently duplicate unsafe side effects;
- success requires expected actual state, not command exit code alone;
- evidence is recomputable and linked to the authorization chain;
- unsupported capabilities fail closed or are reported explicitly.

## Verification profile

Representative tests include:

1. cross-tenant/cross-cluster/forbidden-target rejection;
2. arguments changed after approval;
3. pre-resolution read intent resolving to mutation;
4. expired/revoked child grant at the next side-effect boundary;
5. request-side deny before sandbox handoff;
6. separate sandbox negative probe;
7. mismatched resolution artifacts between authorization and sandbox renderer;
8. duplicate retry of a non-idempotent operation;
9. command success with post-state mismatch;
10. offline replay with the pinned policy/tool/canonicalization versions.

## Adoption profiles

### Control-plane / portal

Examples: Narwhal, Narwhal Portal.

Implement the full authorization/grant/approval/evidence lifecycle for platform mutations and privileged operations.

### Local AI / Agent runtime

Example: KubeMetal.

Use the same contract for ChatOps, remediation, local agent tools, model-generated actions, and host/Kubernetes operations.

### Data / operations agent

Example: Beluga.

Apply the contract to data-platform operations, governed outbound actions, external API/data egress, and operations agents.

### Sandbox / node foundation

Example: kube-ready-box.

Do not become the policy source of truth. Provide machine-readable sandbox/runtime capability and effective enforcement evidence that higher-level authorization systems can consume.

### Service-specific mutation

Examples: nfs-quota-agent, ldapium, ClusterDeck.

Adopt a reduced profile around service-specific high-risk mutations while preserving the same exact-invocation, approval, verification, and evidence semantics where applicable.

## Non-goals

- implementing an LLM/agent framework;
- requiring a specific policy engine;
- requiring a specific sandbox such as gVisor/Kata/Vetto;
- requiring a specific evidence/attestation product;
- approving arbitrary natural-language commands;
- enabling unsupervised destructive autonomy.

## References / portfolio adoption

The Narwhal agent execution design is a reference implementation input, not the owner of the portable contract:

- `dasomel/narwhal#155`
- `dasomel/narwhal-portal#41`
- `dasomel/narwhal-portal#78`
- `dasomel/kubemetal#4`, `#10`, `#28`
- `dasomel/beluga#108`
- `dasomel/kube-ready-box#11`, `#16`

OpenForge remains the cross-project source of truth for the reusable contract; each repository owns its concrete implementation and runtime evidence.