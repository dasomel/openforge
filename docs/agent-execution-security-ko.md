# Agent Execution Security Contract

[English](agent-execution-security.md) | 한국어

OpenForge는 외부 시스템을 조회하거나 변경할 수 있는 AI/LLM Agent, MCP Tool, 자동화 Worker 및 기타 Software Actor를 위한 재사용 가능한 보안 계약을 정의한다.

이 계약은 특정 Agent Framework, Policy Engine, Sandbox 구현 또는 Attestation 제품을 강제하지 않고 **authorization, capability attenuation, approval binding, sandbox enforcement, verification, recomputable evidence**를 공통화한다.

## 핵심 lifecycle

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

기본 원칙은 **한 번 resolve한 뒤 이후의 모든 결정을 동일한 resolved invocation에 bind하는 것**이다.

## Trust boundary

다음 identity와 책임을 분리한다.

- human identity
- agent identity
- workload/service identity
- policy decision
- capability grant
- human approval
- executor
- sandbox/runtime enforcement
- evidence recorder/verifier

사용자가 session을 시작했다는 이유만으로 Agent가 unrestricted human administrator credential을 상속해서는 안 된다.

Model output, retrieved document, RAG context, tool output, external content는 data input이며 authorization policy가 아니다.

## Canonical Resolution Artifact

Parameter resolution은 Executor까지 전달될 수 있는 정확한 operation을 canonical representation으로 생성해야 한다.

권장 필드:

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

Authorization, grant issuance, approval binding, sandbox-rule rendering, executor revalidation, evidence generation은 동일한 resolution artifact 또는 cryptographically bound equivalent를 소비해야 한다.

동일한 source policy file을 서로 다른 resolution code path에서 읽는 것만으로는 충분하지 않다. 설정 파일이 같아도 semantic drift가 발생할 수 있다.

## Capability attenuation

위험도가 높은 경우 권한을 두 단계로 나눈다.

### Session grant

Session grant는 해당 session/run에서 허용 가능한 최대 authority ceiling을 정의한다.

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

Session grant는 이후 호출의 resolved target/arguments가 최초 capability boundary를 벗어나는 경우 이를 암묵적으로 허용해서는 안 된다.

### Invocation / phase grant

Mutating, destructive, privileged, exfiltrating 등 high-risk operation은 concrete parameter가 resolve된 이후 session ceiling에서 파생된 short-lived child grant를 사용해야 한다.

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

현재 invocation이 grant binding을 재현하지 못하면 executor는 실행을 거부해야 한다.

## Human approval

Approval은 단순한 `approved=true` flag가 아니라 first-class authorization object다.

High-risk approval은 정확한 resolved invocation에 bind해야 한다.

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

Invocation digest에는 최소 다음 정보가 포함되는 것이 좋다.

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

Side effect 또는 commit boundary 직전에 executor는 관련 grant/approval digest와 현재 expiry/revocation 상태를 재검증해야 한다.

## Grant와 Evidence의 경계

다음 규칙을 사용한다.

> Executor가 decision/execution time에 강제해야 하는 정보는 grant 또는 bound resolution artifact에 둔다. 실행 후 설명, 검증, correlation, audit에 필요한 정보는 evidence에 둔다.

Evidence는 enforcement를 대체해서는 안 된다. 거부됐어야 할 요청을 기록하는 것과 side effect 전에 실제로 거부하는 것은 다르다.

## Sandbox와 enforcement drift

Sandbox는 두 번째 enforcement layer이며 request-side authorization을 대체하지 않는다.

가능하면 다음을 지킨다.

- authorization policy와 sandbox rule은 동일한 versioned policy source에서 파생한다.
- 더 중요한 것은 grant issuance와 sandbox-rule rendering이 동일한 canonical resolution artifact/digest를 소비하는 것이다.
- runtime test는 forbidden resolved request가 executor/sandbox handoff 전에 차단되는지 검증한다.
- 별도의 negative probe로 sandbox/kernel/container가 예상 boundary를 실제로 강제하는지 검증한다.
- declared policy, request-side decision, effective sandbox/runtime enforcement 간 drift는 명시적으로 실패해야 한다.

Kernel-side denial은 sandbox boundary를 증명할 뿐 request-side authorization path의 정확성을 증명하지는 않는다.

## Revocation과 long-running operation

임의의 mid-syscall revocation semantics에 의존하지 않는다.

- side-effect/commit boundary 전에 grant expiry/revocation을 재검증한다.
- 가능한 경우 long-running high-risk operation을 phase로 나누고 short-lived child grant를 사용한다.
- kill switch/revocation은 향후 grant issuance와 future commit phase를 차단한다.
- failed/partial operation은 silent retry loop가 아니라 explicit recovery/rollback/hold 상태로 전환한다.

## Recomputable execution evidence

Evidence는 first-class artifact다.

권장 필드:

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

Evidence는 다음 chain을 안정적인 ID/digest로 연결해야 한다.

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

Offline replay는 동일한 policy snapshot, normalization/canonicalization version, agent/session context, tool contract, target, resolved arguments를 사용해 authorization decision과 evidence envelope를 다시 검증할 수 있어야 한다.

Hash chain, HMAC, signature, append-only log, TPM-backed attestation, transparency log, external verifier 등은 tamper evidence를 강화할 수 있으나 OpenForge는 특정 메커니즘을 강제하지 않는다.

## 최소 risk class

프로젝트마다 명칭은 조정할 수 있지만 구분 자체는 명시적이어야 한다.

- read-only / observational
- diagnostic with bounded side effects
- mutating
- destructive / irreversible
- privileged / host-level
- exfiltrating / external egress

위험도가 높을수록 scope, credential, approval, sandboxing, verification을 강화한다.

## 필수 security property

채택 프로젝트는 최소 다음을 검증해야 한다.

- Agent path가 기본적으로 unrestricted human admin authority를 상속하지 않는다.
- 모든 executable tool/capability에 명시적인 scope와 risk classification이 있다.
- authorization은 declared intent가 아니라 fully resolved invocation을 평가한다.
- high-risk call은 bounded/expiring authority를 사용한다.
- approval이 필요한 경우 exact invocation identity에 bind된다.
- untrusted model/RAG/tool content가 authorization policy를 override할 수 없다.
- request-side deny가 sandbox/executor handoff 전에 발생한다.
- sandbox/runtime enforcement는 별도 negative probe로 검증한다.
- retry가 unsafe side effect를 중복 발생시키지 않는다.
- success는 command exit code가 아니라 expected actual state로 판단한다.
- evidence는 recomputable하고 authorization chain과 연결된다.
- unsupported capability는 fail-closed 또는 명시적인 unsupported 상태로 표현한다.

## 검증 profile

대표 테스트:

1. cross-tenant/cross-cluster/forbidden-target rejection
2. approval 이후 arguments 변경
3. pre-resolution read intent가 mutation으로 resolve되는 경우
4. 다음 side-effect boundary에서 expired/revoked child grant
5. sandbox handoff 이전 request-side deny
6. 별도의 sandbox negative probe
7. authorization과 sandbox renderer가 서로 다른 resolution artifact를 사용하는 drift
8. non-idempotent operation의 duplicate retry
9. command success지만 post-state mismatch
10. pinned policy/tool/canonicalization version을 이용한 offline replay

## Adoption profile

### Control-plane / portal

예: Narwhal, Narwhal Portal.

Platform mutation 및 privileged operation에 full authorization/grant/approval/evidence lifecycle을 적용한다.

### Local AI / Agent runtime

예: KubeMetal.

ChatOps, remediation, local agent tool, model-generated action, host/Kubernetes operation에 동일 contract를 적용한다.

### Data / operations agent

예: Beluga.

Data-platform operation, governed outbound action, external API/data egress, operations agent에 적용한다.

### Sandbox / node foundation

예: kube-ready-box.

Policy source-of-truth가 되지 않는다. 상위 authorization system이 소비할 수 있는 machine-readable sandbox/runtime capability와 effective enforcement evidence를 제공한다.

### Service-specific mutation

예: nfs-quota-agent, ldapium, ClusterDeck.

Service-specific high-risk mutation에 reduced profile을 적용하되 applicable한 경우 exact-invocation, approval, verification, evidence semantics를 유지한다.

## 비범위

- LLM/Agent Framework 자체 구현
- 특정 Policy Engine 강제
- gVisor/Kata/Vetto 등 특정 Sandbox 강제
- 특정 Evidence/Attestation 제품 강제
- arbitrary natural-language command 승인
- unsupervised destructive autonomy 활성화

## References / portfolio adoption

Narwhal Agent execution 설계는 portable contract의 owner가 아니라 reference implementation input으로 취급한다.

- `dasomel/narwhal#155`
- `dasomel/narwhal-portal#41`
- `dasomel/narwhal-portal#78`
- `dasomel/kubemetal#4`, `#10`, `#28`
- `dasomel/beluga#108`
- `dasomel/kube-ready-box#11`, `#16`

OpenForge가 reusable contract의 cross-project source of truth를 유지하고, 각 repository는 concrete implementation과 runtime evidence를 소유한다.