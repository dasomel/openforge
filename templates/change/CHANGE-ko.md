# 변경: <결과 중심의 짧은 제목>

- 변경 등급: `B` / `C` / `D`
- 책임자:
- 관련 Issue:
- 상태: `Draft` / `Accepted` / `Implementing` / `Verified`
- 수락자 / 날짜:

## 문제

어떤 관찰 가능한 문제, 위험 또는 미충족 요구가 이 변경을 필요로 하는지 설명합니다.

## 의도

모든 구현 세부사항을 미리 고정하지 않고 이 변경이 만들어야 하는 결과를 설명합니다.

## 범위

- 포함 범위:
- 영향 받는 사용자/시스템:

## 제외 범위

- 명시적으로 제외하는 동작, 시스템 또는 후속 작업:

## 요구사항

요구사항을 Task와 Verification Evidence에 연결할 수 있도록 Stable ID를 사용합니다.

- `REQ-001` — ...
- `REQ-002` — ...

## 인수 시나리오

### `AC-001` — <시나리오 제목>

- 대상: `REQ-001`
- Given ...
- When ...
- Then ...

## 아키텍처와 의사결정

- 관련 ADR/Design 링크:
- ADR Threshold 결과: `required` / `not required` — 근거:
- 대안과 주요 Trade-off:

## 변경 영향

| 영역 | 영향 / 필요한 Evidence |
|---|---|
| Source / API / Command | |
| Dependency / Lockfile | |
| Runtime / Toolchain | |
| CI / CD | |
| Release / Packaging | |
| Generated Output | |
| Security / Supply Chain | |
| Offline / Air-gap | |
| Documentation / Operations | |
| Portfolio / Downstream Repository | |

검토하지 않은 채 비워두지 말고 해당 사항이 없으면 `N/A — <이유>`로 기록합니다.

## 검증 계획

| Acceptance ID | 검증 방법 | 환경 | 예상 Evidence |
|---|---|---|---|
| `AC-001` | | | |

Unit/Static Check와 Integration, Runtime, User Journey Evidence를 구분합니다.

## Rollout, Rollback, Recovery

- Rollout 순서:
- Rollback 조건과 절차:
- Data/Configuration Recovery:
- Compatibility 또는 Migration 의무:

사용자, Shared Environment, Produced Artifact에 영향을 줄 수 없는 경우에만 `N/A — <이유>`를 사용합니다.

## Evidence와 Durable Synchronization

- Evidence 위치/형식:
- 장기 Regression Control로 남길 Test 또는 Check:
- 갱신할 Documentation:
- 갱신할 ADR/Evidence/Portfolio Record:

## 검토 기록

- 수락된 Scope/Requirement:
- 수락 이후의 주요 변경과 재검토:
- Open Question 또는 Blocker:
