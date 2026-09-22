# 의사결정 관리 표준

[English](decision-management.md) | 한국어

OpenForge는 여러 프로젝트에 장기적으로 영향을 주는 Engineering Decision을 독립적인 관리 대상으로 취급합니다.

핵심 원칙은 단순합니다. **재사용 가능한 OpenForge 기본값을 바꾸고, 나중에 Maintainer가 '왜 이렇게 했는가'를 다시 물을 가능성이 있다면 Merge 전에 ADR 대상인지 검토합니다.**

## Decision Layer

```text
Research / 운영 Evidence
        ↓
Issue / Proposal
        ↓
ADR — 왜 이 장기 결정을 했는가
        ↓
Standard — 현재 지켜야 할 규칙은 무엇인가
        ↓
Template / CI / Policy — 어떻게 재사용·자동화하는가
        ↓
Adoption Record — 어디에 언제 적용했는가
        ↓
Feedback / 새로운 Evidence
        └──────────────→ 필요 시 새로운 Decision
```

## ADR 생성 기준

다음 변경은 일반적으로 ADR이 필요합니다.

- 여러 Repository가 상속할 Default 변경
- Architecture 또는 Abstraction/Layer Boundary 변경
- Trust, Access, Privilege, Identity, Secret, Release Boundary 변경
- Security, Supply Chain, Compatibility, Release, CI Resilience, Agent Engineering, Design System, Governance, Repository Policy 변경
- 의미 있는 Trade-off가 있는 여러 대안 중 하나를 의도적으로 선택
- Migration, Compatibility, Downstream Adoption 의무 생성
- 향후 다시 논쟁할 가능성이 높은 공통 규칙 변경
- 이전 Accepted ADR을 대체하는 결정

다음은 일반적으로 ADR이 필요하지 않습니다.

- 오탈자 또는 표현만 수정
- Accepted Decision으로 이미 결정된 구현 작업
- Policy/Contract 변화가 없는 일반 Dependency Refresh
- OpenForge Default로 승격하지 않는 Project-local 선택

## 필수 연결 관계

장기 Decision이 Issue, PR, Chat, Commit Message에만 남아 있어서는 안 됩니다.

ADR이 Accepted되면:

1. 영향을 받는 Standard를 연결합니다.
2. Enforcement가 적절하면 Template/Policy/CI를 갱신합니다.
3. Downstream Rollout이 크면 별도의 Adoption Record를 만듭니다.
4. Evidence, Research, Issue, Implementation Record를 연결합니다.
5. User-facing ADR은 English canonical + Korean first-class 구조를 유지합니다.

## Immutability / Supersession

Accepted ADR은 History입니다. 현재 판단에 맞게 과거 Accepted Rationale을 다시 쓰지 않습니다.

결정이 실질적으로 변경되면:

1. 새 ADR 생성
2. 변경 이유 기록
3. 기존 ADR을 `Superseded` 처리
4. 양쪽 ADR Cross-link
5. Normative Standard와 Adoption Guidance 갱신

## Review Gate

중요한 OpenForge 변경을 Review할 때 다음을 확인합니다.

- ADR Threshold를 넘는 변경인가?
- 그렇다면 ADR이 존재하고 연결되어 있는가?
- Standard는 현재 Rule에 집중하고 과거 토론은 ADR로 분리되어 있는가?
- 가능한 Deterministic Rule은 Template/CI/Policy로 이동했는가?
- Migration/Adoption 영향이 기록되어 있는가?
- English/Korean Decision Record가 동기화되어 있는가?
- 기존 ADR을 Supersede하는가?

## 정기 Audit

새 ADR을 만들 때뿐 아니라 Decision History를 주기적으로 Audit합니다.

- 중요한 Rationale이 있지만 ADR이 없는 Standard
- Standard에서 연결되지 않는 ADR
- Accepted Decision과 실제 구현의 Drift
- 중복 또는 충돌 Decision
- 오래된 Exception/Migration
- English/Korean Drift
- Decision Link가 없는 Adoption Record
- Reference OSS에서 검증됐지만 OpenForge로 아직 일반화되지 않은 Decision

## References

- [ADR Index](adr/README-ko.md)
- [한국어 ADR Template](../templates/ADR-ko.md)
- [Change Management Standard](change-management-ko.md)
- [Maintainer Governance](maintainer-governance-ko.md)
- [Agent Engineering 적용 기록](agent-engineering-adoption-2026-08.md)
