# OpenForge Architecture Decision Records

[English](README.md) | 한국어

OpenForge는 여러 OSS에 공통으로 적용되는 표준 저장소입니다. 따라서 현재 규칙이 **무엇인지**뿐 아니라, **왜 그 규칙을 선택했는지**, 어떤 대안을 검토하고 제외했는지, 향후 변경할 때 어떤 결정을 대체해야 하는지까지 남겨야 합니다.

## ADR이 필요한 경우

다음과 같은 결정은 ADR을 생성하거나 갱신합니다.

- 여러 Repository에 적용할 공통 규칙을 변경하는 경우
- Architecture, Security, Supply Chain, Release, Compatibility, Agent Engineering, Design System, Governance, Repository Policy를 변경하는 경우
- 현실적인 다른 대안을 의도적으로 선택하지 않은 경우
- Trust/Access Boundary를 확대하거나 축소하는 경우
- Compatibility 또는 Migration 의무가 생기는 경우
- Downstream Repository가 상속할 기본값을 변경하는 경우
- 향후 다시 검토할 가능성이 높아 당시 판단 근거를 보존할 필요가 있는 경우

오탈자, 표현 개선, 정책 변화가 없는 일반적인 Dependency Update, 이미 Accepted ADR에서 결정된 구현 세부 사항에는 ADR을 만들지 않습니다.

## 상태

- `Proposed` — 검토 중이며 아직 표준이 아님
- `Accepted` — 현재 유효한 결정
- `Superseded` — 새로운 ADR로 대체됨. 이력 보존을 위해 삭제하지 않음
- `Deprecated` — 더 이상 권장하지 않지만 직접적인 대체 ADR이 없음
- `Rejected` — 검토했지만 의도적으로 채택하지 않음

Accepted ADR은 역사 기록으로 취급합니다. 결정이 실질적으로 변경되면 기존 ADR의 내용을 다시 쓰지 않고 새로운 ADR을 만든 뒤 기존 ADR을 `Superseded` 처리합니다.

## ADR 구조

각 ADR은 다음 내용을 기록합니다.

1. Status / Date
2. Context
3. Decision
4. Alternatives Considered
5. Rationale
6. Consequences / Trade-offs
7. Affected Standards / Templates / Projects
8. Migration / Adoption
9. Related Issues / Adoption Records / Supersession

## Decision Index

초기 ADR은 이미 OpenForge의 여러 표준에 반영되어 있던 중요한 공통 의사결정을 소급 정리한 것입니다. 모든 문서 변경을 ADR로 만드는 것이 아니라 장기간 유지할 가치가 있는 결정만 선별합니다.

| ADR | 의사결정 | 상태 |
|---|---|---|
| [0001](0001-record-cross-project-decisions-ko.md) | 여러 프로젝트에 영향을 주는 결정을 ADR로 관리 | Accepted |
| [0002](0002-english-canonical-korean-first-class-ko.md) | English canonical + Korean first-class translation | Accepted |
| [0003](0003-risk-based-oss-security-governance-ko.md) | OSS Security/Governance를 Risk 기반으로 적용 | Accepted |
| [0004](0004-treat-ai-and-plugins-as-untrusted-input-ko.md) | AI instruction/plugin을 untrusted execution input으로 취급 | Accepted |
| [0005](0005-require-workflow-impact-analysis-for-upgrades-ko.md) | Upgrade 시 workflow 전체 영향 분석 | Accepted |
| [0006](0006-build-security-into-release-supply-chain-ko.md) | Security/Supply Chain을 lifecycle에 내재화 | Accepted |
| [0007](0007-design-system-standardizes-semantics-not-identity-ko.md) | Design System은 의미를 표준화하고 Product Identity는 보존 | Accepted |
| [0008](0008-layer-agent-instructions-and-keep-root-context-small-ko.md) | Agent instruction을 계층화하고 root context를 작게 유지 | Accepted |
| [0009](0009-evidence-first-agent-verification-and-convergence-ko.md) | Agent 작업에 evidence-first verification과 convergence 적용 | Accepted |
| [0010](0010-reusable-templates-are-adaptable-baselines-ko.md) | Reusable Template은 adaptable baseline으로 제공 | Accepted |
| [0011](0011-ci-resilience-must-not-encourage-security-bypass-ko.md) | CI resilience가 무분별한 Security bypass를 유도하지 않게 설계 | Accepted |
| [0012](0012-document-and-time-bound-intentional-exceptions-ko.md) | 의도적인 예외는 문서화하고 review/expiry 적용 | Accepted |

## Standard 및 Adoption Record와의 관계

```text
ADR
  왜 이 결정을 했는가
       ↓
Standard
  현재 지켜야 할 규칙은 무엇인가
       ↓
Template / CI / Policy
  어떻게 재사용·자동화하는가
       ↓
Adoption Record / Issue / PR
  어디에 어떻게 적용했는가
```

예를 들어 `docs/agent-engineering-adoption-2026-08.md`는 적용 이력을 기록하고, 관련 ADR은 그 적용의 근거가 된 장기 의사결정을 설명합니다.
