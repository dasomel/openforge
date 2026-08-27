# ADR-0001: 여러 프로젝트에 영향을 주는 의사결정을 ADR로 관리

[English](0001-record-cross-project-decisions.md) | 한국어

- Status: Accepted
- Date: 2026-08-27

## Context

OpenForge의 표준과 기본값은 여러 OSS Repository에 영향을 줄 수 있습니다. 표준 문서는 현재 규칙을 설명하지만 Git 이력과 최종 문서만으로는 왜 해당 선택을 했는지, 어떤 대안을 제외했는지, 향후 어떤 방식으로 안전하게 대체해야 하는지를 찾기 어렵습니다.

## Decision

장기간 유지되는 공통 Engineering 의사결정은 ADR로 기록합니다. Standard는 현재의 normative rule을 담당하고 ADR은 결정의 역사와 근거를 담당합니다.

실질적인 결정 변경은 Accepted ADR을 다시 작성하지 않고 새로운 ADR을 생성하여 필요하면 기존 ADR을 Superseded 처리합니다.

## Alternatives Considered

- Git commit history에만 의존
- Issue/PR에만 근거 기록
- 모든 Standard 문서 안에 과거 근거를 계속 누적
- 모든 Repository 변경을 ADR로 기록

## Rationale

Commit과 Issue는 구현 이력에는 유용하지만 표준이 커질수록 의사결정 근거를 발견하기 어렵습니다. 반대로 모든 역사를 Standard에 넣으면 현재 규칙을 읽기 어려워집니다. 선별적인 ADR 계층이 현재 표준의 가독성과 장기 이력을 함께 유지할 수 있습니다.

## Consequences

- 중요한 공통 결정의 검색과 검토가 쉬워집니다.
- Supersession 관계가 명확해집니다.
- Maintainer는 변경이 ADR 대상인지 판단해야 합니다.
- ADR이 고립된 문서가 되지 않도록 Standard 및 Adoption Record와 연결해야 합니다.
