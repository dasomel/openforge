# ADR-0013: Agent 권한을 canonical resolved invocation에 bind한다

- 상태: Accepted
- 날짜: 2026-09-07

## Context

AI/LLM Agent와 automation worker는 tool을 선택하고 parameter를 resolve하며 API, Kubernetes, host operation을 호출해 실제 side effect를 만들 수 있다. 기존 RBAC 또는 broad service credential만으로는 executor에 도달한 정확한 invocation이 policy가 평가하고 사람이 승인한 operation과 동일하다는 것을 증명하기 어렵다.

Authorization, approval, sandbox rendering, execution이 각각 요청을 독립적으로 resolve하면 다음 문제가 발생할 수 있다.

- read-only처럼 보이는 intent가 실제로 mutating call로 resolve됨
- approval 이후 target 또는 arguments가 변경됨
- session이 concrete invocation에 필요한 것보다 넓은 authority를 유지함
- 동일한 policy file을 사용해도 sandbox rule과 authorization이 서로 다른 semantic resolution path를 사용함
- evidence는 남지만 side effect 전에 실제 deny가 발생했는지는 증명하지 못함
- retry 또는 long-running phase가 intended scope/lifetime을 넘어 authority를 재사용함
- agent가 자신의 execution authority를 직접 mint하거나 replay할 수 있으면 올바른 policy decision도 최종 enforcement boundary에서 우회될 수 있음

Narwhal #155와 관련 portfolio discussion을 통해 repository별 복사본이 아니라 cross-project reusable contract가 필요하다는 점이 확인되었다.

## Decision

OpenForge는 vendor-neutral Agent Execution Security Contract를 다음과 같이 표준화한다.

1. Concrete tool invocation을 한 번 resolve하여 policy version, agent/session identity, tool contract version, resolved target, normalized arguments, normalization version, invocation digest를 포함하는 canonical `ResolutionArtifact`를 만든다.
2. Authorization, capability grant issuance, human approval, sandbox-rule rendering, executor revalidation, evidence generation은 동일한 resolution artifact 또는 cryptographically bound equivalent를 사용한다.
3. Session-scoped grant는 모든 후속 호출을 허용하는 durable permission이 아니라 authority ceiling으로 취급한다.
4. Mutating, destructive, privileged, exfiltrating 등 high-risk operation은 attenuated per-invocation/per-phase short-lived grant를 사용한다.
5. Approval은 generic boolean이 아니라 exact resolved invocation에 bind한다.
6. Side-effect 또는 commit boundary에서 grant/approval binding 및 expiry/revocation을 재검증한다.
7. Request-side authorization과 sandbox/runtime enforcement를 서로 다른 security layer로 유지하고 독립적으로 검증한다.
8. Decision-time enforcement에 필요한 정보는 grant 또는 bound resolution artifact에 두고, 설명/검증/correlation/audit 정보는 evidence에 둔다.
9. Authorization decision → grants → approval → runtime assertion → sandbox enforcement → actual execution → observed side effects → post-state verification을 연결하는 recomputable evidence를 요구한다.
10. Cryptographic attestation과 sandbox 구현은 pluggable하게 유지하고 OpenForge는 특정 제품 대신 필요한 security property를 정의한다.
11. PDP(policy decision point), grant issuer/signer, PEP(policy enforcement point), executor를 명시적인 logical responsibility로 구분한다. High-risk operation에서 PEP는 concrete invocation grant를 검증하고, single-use semantics가 필요한 경우 executor handoff 전 또는 그 경계에서 grant를 atomic하게 consume한다.
12. Agent/model runtime은 임의 execution grant를 mint할 수 있는 signing authority를 보유하지 않는다. 한 번 소비된 single-use grant는 두 번째 execution을 승인하는 데 재사용할 수 없다.

## Execution grant enforcement boundary

아래 구조는 logical trust model이며 별도 제품/프로세스로 분리 배포해야 한다는 요구는 아니다.

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
- resolution/invocation binding 검증
- expiry/revocation 검증
- approval binding 검증
- 필요 시 spend-once grant atomic consume
          │
          ▼
Executor / Tool
          │
          ▼
Post-state verification + evidence
```

Session grant는 authority ceiling이며 unrestricted execution token이 아니다. Concrete child grant는 canonical resolution 이후에만 파생되며 PEP가 실제로 enforce할 정확한 invocation에 bind된다.

Replay가 duplicate 또는 unsafe side effect를 만들 수 있는 operation에서는 PEP가 atomic consumed-state 또는 동등한 idempotency primitive를 유지하여 동일 grant를 두 번 spend하지 못하게 해야 한다. Request retry가 execution authority 재사용을 의미하지는 않는다. 새로운 side effect가 필요한 retry는 policy에서 정의한 reauthorization/idempotency 경로를 따라야 한다.

Signer/issuer는 PDP나 다른 trusted control-plane component와 함께 구현할 수 있고 PEP도 executor와 colocate할 수 있다. 다만 logical responsibility와 testable trust boundary는 명확해야 하며, agent/model process가 tool call을 요청할 수 있다는 이유만으로 valid grant까지 임의로 mint할 수 있어서는 안 된다.

## Alternatives considered

- Agent에 broad static service credential을 부여하고 tool implementation 자체의 안전성에 의존
- Natural-language intent 또는 pre-resolution tool selection만 authorization
- Exact tool/argument identity 없이 generic operation/boolean에 approval bind
- 동일 policy source를 사용하지만 grant와 sandbox rule을 서로 다른 resolution path에서 생성
- Kernel/container sandbox deny를 request-side authorization이 정확했다는 충분한 증거로 간주
- Agent가 자신의 execution grant를 서명하는 credential/key를 보유
- TTL이 끝날 때까지 valid grant를 무제한 replay 가능하게 처리
- 모든 프로젝트에 특정 sandbox 또는 evidence-attestation 구현을 강제

## Rationale

Recommendation, authorization, approval, enforcement, evidence 전체에서 동일한 canonical resolved invocation이 보여야 한다. 그래야 configuration file 비교만으로는 찾을 수 없는 semantic drift를 차단할 수 있다.

Session ceiling과 invocation-level attenuation을 결합하면 long-lived agent session의 blast radius를 줄일 수 있다. Exact-invocation approval과 executor revalidation은 authorization을 독립적으로 재검증 가능하게 만든다. Request-side decision과 sandbox enforcement를 분리하면 최후의 containment layer를 earlier policy decision과 혼동하지 않게 된다.

PDP/issuer/PEP/executor responsibility를 명시적으로 분리하면 또 하나의 gap을 막을 수 있다. 올바른 authorization decision만으로는 충분하지 않으며, 최종 execution point가 해당 invocation을 위해 발급된 정확한 authority를 소비하고 있음을 증명해야 한다. Spend-once semantics는 non-idempotent/high-impact operation의 replay를 막고, signing authority를 agent 밖에 두면 requester가 스스로 권한을 발급하는 것을 방지할 수 있다.

Implementation mechanism을 pluggable하게 유지하면 Kubernetes control plane, desktop/local AI runtime, data platform, node sandbox, service-specific tool에 공통 적용할 수 있다.

## Consequences

- Agent-enabled project는 stable tool contract와 deterministic argument normalization/canonicalization이 필요하다.
- High-risk execution에는 추가 metadata, short-lived grant issuance, approval flow가 필요할 수 있다.
- Single-use grant를 사용하는 PEP는 replay/idempotency 상태를 관리해야 한다.
- Signing/issuance credential은 agent/model runtime과 분리된 trust boundary를 가져야 한다.
- Test는 request-side deny, grant-binding mismatch, expired/revoked grant, consumed-grant replay, effective sandbox/runtime enforcement를 모두 검증해야 한다.
- Evidence schema는 이후 replay/recomputation에 필요한 version, digest, grant, consume-result 정보를 보존해야 한다.
- Agent-driven mutation이 없는 프로젝트는 relevant reduced profile만 채택할 수 있다.
- 기존 approval/evidence 구현은 exact resolved invocation binding을 위해 migration이 필요할 수 있다.

## Affected standards / projects

- `docs/agent-execution-security.md`
- `docs/agent-engineering.md`
- Narwhal #73/#155 — reference control-plane implementation input
- Narwhal Portal #41/#78 — portal/MCP adoption
- KubeMetal #4/#10/#28 — local agent/ChatOps/remediation adoption
- Beluga #108 — data-platform operations agent adoption
- kube-ready-box #11/#16 — sandbox/runtime enforcement evidence provider
- applicable한 service-specific adoption: nfs-quota-agent, ldapium, ClusterDeck

## Adoption notes

Reusable contract의 source of truth는 OpenForge가 소유한다. 각 repository는 concrete policy model, tool catalog, runtime implementation, grant issuance/signing mechanism, PEP placement, evidence storage를 소유한다.

Adoption 과정에서 Narwhal issue 전체를 그대로 복사하지 않는다. 각 repository가 자신의 profile, mutation/egress/privilege boundary를 선언하고 repository-specific test로 공통 security property를 증명해야 한다.
