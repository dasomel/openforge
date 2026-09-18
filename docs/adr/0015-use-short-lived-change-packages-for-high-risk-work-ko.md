# ADR-0015: 고위험 작업에 Short-lived Change Package 사용

- Status: Accepted
- Date: 2026-09-18

[English](0015-use-short-lived-change-packages-for-high-risk-work.md) | 한국어

## 배경

OpenForge는 이미 Change Class, Impact Analysis, ADR, Verification, Evidence, Portfolio Governance를 정의하고 있습니다. 이 통제는 Review와 구현 이후 단계에는 강하지만, 큰 변경에서도 Problem, Scope, Requirement, Acceptance Scenario, Verification Approach를 하나의 검토 가능한 단위로 고정하기 전에 구현이 시작될 수 있습니다.

Issue Template이 Proposal과 Impact를 수집하지만 Requirement에서 Task와 Evidence까지의 추적성을 일관되게 보존하지는 않습니다. 반대로 모든 변경에 완전한 병렬 Spec 계층을 도입하면 Code, Test, Documentation, ADR을 중복하고 Drift를 만들며 작은 변경에도 과도한 절차를 부과합니다.

## 결정

OpenForge는 위험도에 따라 Short-lived Change Package를 사용합니다.

1. Class A는 별도 Package 없이 기존 Issue/PR Workflow를 사용합니다.
2. Class B는 Acceptance Criteria가 필요하며, 복잡하거나 Component Boundary를 넘거나 운영 위험이 큰 경우가 아니면 전체 Package는 선택 사항입니다.
3. Class C/D는 본격적인 구현 전에 수락된 Change Package가 필요합니다.
4. Package에는 Problem, Intent, Scope/Non-goals, Stable Requirement, Acceptance Scenario, Decision, Impact Analysis, Task, Verification, Expected Evidence와 필요한 경우 Rollout/Rollback/Recovery를 기록합니다.
5. Stable ID를 사용해 Requirement, Task, Evidence를 추적합니다.
6. 수락 전에도 Exploration, Reproduction, Reversible Prototype은 가능하지만 최종 계약을 암묵적으로 확정하거나 Production/Shared Environment를 변경할 수 없습니다.
7. 완료 시 Durable Truth를 Code/Test, Normative Documentation, ADR, Evidence Record, Portfolio Status로 승격합니다. Issue/PR과 Git History를 기본 Archive로 사용합니다.
8. OpenForge는 병렬적인 장기 System Specification Tree를 도입하지 않습니다.

재사용 Template은 `templates/change/`에 둡니다. Versioned Collaboration이 필요하면 Project가 Issue/PR에서 Package를 직접 관리하거나 작업 Branch의 임시 파일을 사용할 수 있습니다.

## 검토한 대안

### 완전한 외부 Spec-driven Framework 도입

기본값으로는 채택하지 않습니다. OpenForge는 이미 중복되는 Issue, ADR, Evidence, Agent, CI, Portfolio 계약을 소유합니다. 두 번째 Lifecycle과 Command Layer는 Governance 중복과 Tool Coupling을 만듭니다.

### 모든 변경에 Package 의무화

채택하지 않습니다. 문서 수정과 작은 내부 변경에 Runtime, Release, Security Boundary 변경과 같은 절차를 요구할 필요가 없습니다.

### Issue와 PR의 자유 형식 설명만 유지

고위험 작업에는 충분하지 않아 채택하지 않습니다. 자유 형식 설명만으로는 구현 전에 Scope, Testable Requirement, Verification Plan, Evidence Traceability를 일관되게 보존하기 어렵습니다.

### 모든 Package를 Repository에 영구 Archive

채택하지 않습니다. 장기 Package는 현재 상태를 소유하는 Artifact를 중복하고 Drift가 발생할 가능성이 큽니다. 운영 문서로 계속 가치가 있을 때만 Package를 유지합니다.

## 근거

Risk Scaling은 잘못되거나 불완전한 계약의 비용이 큰 작업에 규율을 추가하면서 Routine Maintenance를 느리게 만들지 않습니다. 검토된 Change-scoped Contract는 Human과 Agent Implementer에게 안정적인 목표를 제공하고 OpenForge의 Evidence-first Workflow를 유지합니다. Durable Fact를 이를 소유하는 Artifact로 승격하면 두 번째의 오래된 Spec 계층이 생기는 것을 막습니다.

## 결과와 Trade-off

- Class C/D 작업에 명시적인 Pre-implementation Review Gate가 추가됩니다.
- Reviewer가 Requirement를 Implementation과 Verification Evidence까지 추적할 수 있습니다.
- 복잡한 작업에는 추가 작성 및 Review 비용이 생깁니다.
- Maintainer는 조용한 Scope Expansion을 허용하지 않고 주요 변경을 다시 검토해야 합니다.
- Downstream Project는 Template과 PR Field를 의도적으로 적용해야 하며 기존 Class A/B Workflow는 호환됩니다.
- Change Package는 ADR, Test, Normative Documentation, Evidence Record, Portfolio Status를 대체할 수 없습니다.

## 영향 받는 표준/템플릿/프로젝트

- `docs/change-management.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/pull_request_template.md`
- `templates/change/`
- `templates/AGENTS.md`
- `templates/SKILL.md`
- `templates/github/pull_request_template.md`
- Class C/D Workflow Control을 적용하는 Downstream OpenForge Project

## 마이그레이션과 적용

Class A와 Routine Class B에는 Backward Compatible합니다. Downstream Repository는 다음 Change-management Guide 갱신 시 Change Package Template과 PR Contract를 적용하는 것을 권장합니다. 이미 완료한 변경에 Package를 소급 작성할 필요는 없습니다.

## Evidence와 Reference

- 이 변경의 Change-management Standard와 Template
- 관련 ADR: ADR-0001, ADR-0005, ADR-0009, ADR-0010
