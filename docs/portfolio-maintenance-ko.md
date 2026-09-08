# OSS 포트폴리오 유지보수 인텔리전스

OpenForge는 구현 완료를 엔지니어링 책임의 끝이 아니라 유지보수 라이프사이클의 시작으로 취급합니다.

이 모델은 개발 상태와 OpenForge 표준 적용률과 분리합니다. 구현이 끝났더라도 패치를 책임질 사람이 없거나, 장애·침해의 피해 범위를 모르거나, 교체 경로가 없다면 장기적으로 좋은 포트폴리오 상태라고 볼 수 없습니다.

## 반드시 답해야 할 질문

각 프로젝트는 라이프사이클 검토에서 다음 질문에 답해야 합니다.

1. **피해 범위(Blast radius)** — 장애, 침해, 유지보수 중단이 발생하면 무엇이 영향을 받는가?
2. **유지보수 책임** — 취약점 판단, 패치, 업그레이드, 장애 복구를 실제로 누가 책임지는가?
3. **전략적 역할** — 차별화 기능인가, 차별화를 가능하게 하는 기반인가, 범용 유틸리티인가, 실험인가, 시장 공백을 임시로 메우는 도구인가?
4. **교체 경로(Exit path)** — 더 나은 상용/OSS/업스트림 대안이 나오면 감당 가능한 비용으로 교체하거나 종료할 수 있는가?

이는 AI가 초기 구현 비용을 크게 낮추더라도 수년간의 운영 책임까지 같은 속도로 줄여주지는 않는다는 Build-vs-Buy 원칙을 포트폴리오 거버넌스로 옮긴 것입니다.

## Canonical metadata

`portfolio/maintenance.json`을 유지보수 거버넌스의 source of truth로 사용합니다.

각 프로젝트는 다음 항목을 기록합니다.

- `maintenance_owner`: 실제 책임 유지관리자
- `maintenance_status`: `owned`, `shared`, `unowned`, `review-required`
- `strategic_role`: `differentiator`, `enabler`, `utility`, `experiment`, `temporary-gap`
- `blast_radius`: `high`, `medium`, `low`
- `exit_path_status`: `defined`, `partial`, `review-required`, `not-applicable`
- `review_cadence`: 라이프사이클 재검토 주기

초기 레지스트리는 검토하지 않은 대안을 임의로 만들어내지 않기 위해 모든 교체 경로를 우선 `review-required`로 둡니다.

## Lifecycle governance

기능 개발 상태와 별개로 다음 라이프사이클을 사용할 수 있습니다.

```text
experimental -> incubating -> active -> mature -> maintenance -> deprecated -> archived
```

코드가 merge되거나 release되었다고 해서 OpenForge가 이 상태를 자동 추론하지 않습니다. 개발 완료는 각 저장소의 검증 evidence로 제안하며, 유지보수·라이프사이클 전환은 명시적인 포트폴리오 의사결정으로 남깁니다.

## Maintenance readiness

향후 readiness score는 다음과 같은 실제 evidence가 있을 때만 계산할 수 있습니다.

- 책임 유지관리자 지정
- 보안 정책과 취약점 접수 경로
- dependency/update 자동화
- 유지되는 CI와 release 절차
- incident/recovery 경로
- 교체 또는 종료 경로 문서화
- dependency/impact 관계 파악
- 정해진 주기 내 lifecycle review 완료

검증하지 않은 선언에 임의의 가중치를 부여해서 숫자만 만드는 방식은 사용하지 않습니다.

## Review cadence

포트폴리오 기본값은 분기별입니다. 최소한 다음을 재검토합니다.

- 현재 유지보수 비용을 처음부터 알았어도 다시 이 프로젝트를 만들고 책임질 것인가?
- 내일 치명적 취약점이 공개되면 누가 발견하고 패치하는가?
- 다른 프로젝트가 새로 의존하면서 피해 범위가 커지지 않았는가?
- 여전히 전략적으로 유지할 가치가 있는가?
- 교체 가능한 외부 대안이 생겼는가?
- active를 유지할지, maintenance/deprecated/archived로 전환할지?

## Portfolio Control Plane과의 관계

```text
Development evidence
        ↓
OpenForge status PR
        ↓
Official development state
        │
        ├── Dependency / impact intelligence
        └── Maintenance / lifecycle intelligence
                     ↓
             Invest / Maintain / Replace
             Deprecate / Archive
```

OpenForge merge를 공식 포트폴리오 상태 변경 경계로 유지합니다. 유지보수 메타데이터는 저장소 활동량에서 암묵적으로 추정하지 않고 개발/영향도 정보와 함께 명시적으로 검토합니다.
