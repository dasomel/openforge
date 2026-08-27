# 기여 가이드

[English](CONTRIBUTING.md) | 한국어

기여해 주셔서 감사합니다.

## 시작하기 전에

- 기존 Issue와 Pull Request를 확인합니다.
- 큰 기능, Architecture, Security, Governance, Compatibility, Release, Agent Engineering, Design System 변경은 먼저 Issue를 등록합니다.
- 재사용 가능한 OpenForge Default를 바꿀 가능성이 있다면 [의사결정 관리 표준](docs/decision-management-ko.md)을 확인합니다.
- 변경을 작고 리뷰 가능한 단위로 유지합니다.

## ADR Gate

장기간 유지되고 여러 프로젝트에 영향을 주는 Policy 변경을 구현하기 전에 ADR Threshold를 넘는지 확인합니다.

여러 Repository에 영향을 주거나, Architecture/Trust Boundary를 바꾸거나, 의미 있는 여러 대안 중 하나를 선택하거나, Migration 의무를 만들거나, 기존 Accepted Decision을 대체한다면 일반적으로 ADR이 필요합니다.

[`templates/ADR.md`](templates/ADR.md)와 [`templates/ADR-ko.md`](templates/ADR-ko.md)를 함께 사용해 English canonical + Korean first-class 구조를 유지합니다.

오탈자, 표현만 수정하는 변경, 이미 Accepted Decision에 의해 정해진 Project-local 구현에는 불필요한 ADR을 만들지 않습니다.

## Pull Request

- 목적이 명확한 Branch를 사용합니다.
- Conventional Commits를 사용합니다.
- 관련 Issue를 연결합니다.
- ADR Threshold를 넘는 변경이면 관련 ADR을 연결합니다.
- Test, Evidence, Migration/Adoption, Documentation 영향을 설명합니다.
- 사용자 문서의 English/Korean 버전을 동기화합니다.
- 기존 Accepted ADR을 Supersede한다면 이를 명시합니다.

## Review 질문

중요 변경에서는 다음을 확인합니다.

- 재사용 가능한 OpenForge Default가 바뀌는가?
- 새 ADR이 필요한가, 기존 ADR이 authoritative한가?
- Normative Standard가 Decision을 반영하는가?
- Deterministic Requirement를 Prose 대신 CI/Policy/Template으로 강제할 수 있는가?
- Downstream Adoption과 Exception이 기록되어 있는가?
- English/Korean Decision Record가 동기화되어 있는가?
