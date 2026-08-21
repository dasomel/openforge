# Security Exception 및 Waiver 표준

Exception은 통제된 risk decision이며 영구적인 bypass가 아닙니다.

## 필수 기록

Security/supply-chain exception은 가능한 경우 다음을 기록합니다.

- scope
- affected repository/component
- reason
- risk assessment
- compensating control
- owner
- reviewer/approver
- creation date
- expiration/review date
- rollback/remediation plan

## 규칙

- 명시적인 재승인 없는 indefinite exception을 두지 않습니다.
- Emergency exception은 정의된 scope와 기간 안에서만 routine cooling/review를 우회합니다.
- 일반 통제를 적용할 수 없으면 compensating control을 강화합니다.
- 만료된 exception은 가능한 경우 fail-closed 합니다.
- Exception이 프로젝트의 기본 동작으로 조용히 변하지 않도록 합니다.

## 단독 Maintainer

독립 reviewer가 없는 단독 maintainer는 emergency exception을 직접 승인할 수 있습니다. 이 경우 자동 검증, 명시적 evidence, 기간이 정해진 retrospective review로 보완합니다.
