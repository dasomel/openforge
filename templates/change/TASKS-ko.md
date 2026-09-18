# 작업: <변경 제목>

이 Checklist를 관련 Change Package에 연결합니다. 각 Implementation Task는 대상 Requirement 또는 Acceptance Scenario를 명시하는 것을 권장합니다.

## 점검과 기준 Evidence 확보

- [ ] `T-001` (`REQ-___`) Source of Truth와 현재 동작을 확인합니다.
- [ ] `T-002` (`AC-___`) 문제를 재현하거나 변경 전 Baseline을 수집합니다.
- [ ] `T-003` Dependency, 영향 받는 Workflow, Downstream Consumer를 검토합니다.

## 구현

- [ ] `T-010` (`REQ-___`) ...
- [ ] `T-011` (`REQ-___`) ...

## 검증

- [ ] `T-020` (`AC-___`) 계획한 Unit/Static Check를 실행합니다.
- [ ] `T-021` (`AC-___`) 계획한 Integration/Runtime/User Journey Check를 실행합니다.
- [ ] `T-022` 실패와 성공, 환경, 실행 Command를 Evidence로 수집합니다.
- [ ] `T-023` 발견한 Regression Risk를 가능한 경우 장기 Check로 전환합니다.

## Durable Truth 동기화

- [ ] `T-030` Normative Documentation과 운영 가이드를 갱신합니다.
- [ ] `T-031` 필요한 경우 ADR 또는 Design Reference를 갱신합니다.
- [ ] `T-032` Release, Migration, Rollback, Compatibility Note를 갱신합니다.
- [ ] `T-033` Portfolio/Downstream Impact를 검토하고 필요한 경우 검증된 상태를 게시합니다.

## 완료 검토

- [ ] 모든 Requirement가 Acceptance Scenario와 Verification Result에 연결됩니다.
- [ ] 주요 Scope 변경을 Change Package에 반영하고 다시 검토했습니다.
- [ ] Expected Evidence가 첨부되거나 링크되어 있습니다.
- [ ] 완료하지 못한 작업에 Owner와 Tracking Issue가 있습니다.
- [ ] PR에 실제 실행한 Check와 중요한 미검증 경로를 명시했습니다.
