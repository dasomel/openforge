# Branch Protection 및 필수 상태 검사 표준

[English](branch-protection.md) | 한국어

> OpenForge OSS 포트폴리오 전반의 Branch Protection, 필수 CI 검사(Required Status Checks), 병합 안전성 표준.

## 1. 목적

지속적 통합(CI)은 자동화된 품질 검증을 제공하지만, 기준 브랜치(`main`)로의 병합이 통과된 상태 검사에 바인딩되어 있지 않으면 실질적인 품질을 보장하기 어렵습니다. Branch Protection이 없으면 실패한 검증이나 누락된 공급망 게이트가 우회되어 `main`에 반영될 수 있습니다.

본 표준은 [ADR-0003 (위험 기반 OSS 보안 거버넌스)](adr/0003-risk-based-oss-security-governance-ko.md)에 따라 개발 속도와 품질 보증의 균형을 맞추며, OpenForge를 준수하는 모든 OSS 저장소의 기준 브랜치 보호 체계를 정의합니다.

## 2. 표준 필수 상태 검사 매트릭스

표준 저장소의 `main` 병합 시 기본 필수 검사 구성은 다음과 같습니다.

```text
main
 ├─ Markdown 검사 (파일명 규칙, 영한 쌍, 포맷)
 ├─ Repository Baseline 검사 (필수 파일, 라이선스, editorconfig)
 ├─ ADR 검증 (영한 쌍 일치, 색인 등록, 상태/날짜)
 ├─ Supply-Chain Baseline (정책 코드, 불변 action 해시 고정)
 └─ 프로젝트 Test & Build (단위/통합 테스트, 빌드 검증)
       ↓
 병합 전 필수 통과 (Required before merge)
```

### 필수 상태 검사 항목

| 상태 검사 컨텍스트 | 워크플로 Job / 도구 | 범위 | 중요도 |
|---|---|---|---|
| `markdown` | `.github/workflows/markdown.yml` | `-ko.md` 파일명 규칙 및 루트 영한 문서 쌍 검증 | 높음 |
| `repository-check` | `.github/workflows/ci.yml` (`repository-check`) | 필수 파일(`README.md`, `LICENSE`, `SECURITY.md` 등) 검증 | 필수 (Critical) |
| `adr-validation` | `.github/workflows/ci.yml` (`adr-validation`) | ADR 영한 쌍, Status, Date, 색인 동기화 검증 | ADR 저장소 필수 |
| `supply-chain` | `.github/workflows/ci.yml` (`supply-chain`) | 의존성 정책, Action 불변 커밋 SHA 고정 검증 | 필수 (Critical) |
| `compliance-tests` | `.github/workflows/ci.yml` (`compliance-tests`) | 컴플라이언스 감사 엔진 단위/스모크 테스트 | 필수 (Critical) |
| `test` / `build` | 프로젝트별 CI 워크플로 | 단위 테스트, 정적 분석, 빌드 성공 검증 | 필수 (Critical) |

## 3. 프로젝트 계층별 거버넌스 모델

[ADR-0003](adr/0003-risk-based-oss-security-governance-ko.md) 원칙에 따라 다음과 같이 계층별로 적용합니다.

### Tier 1: 표준 청사진 및 프로덕션 서비스 (`openforge`, `narwhal`, `ldapium`)
- **Branch Protection:** `main` 브랜치 활성화.
- **Require Status Checks to Pass:** 필수 적용 (`strict: true` — 최신 브랜치 리베이스 요구).
- **PR 리뷰 요구:** 1인 메인테이너는 선택적 적용, 다수 기여자 프로젝트는 필수.
- **Enforce Admins:** 실수로 인한 직접 푸시 방지를 위해 권장.
- **Linear History / Squash Merges:** 릴리스 변경 이력 추적성을 위해 활성화.

### Tier 2: 활성 데스크톱 및 플랫폼 오퍼레이터 (`clusterdeck`, `kubemetal`, `beluga-manager`)
- **Branch Protection:** `main` 브랜치 활성화.
- **Require Status Checks to Pass:** 필수 적용 (`ci.yml`, `markdown.yml`, `test`).
- **직접 푸시:** 제한하고 PR 또는 검증된 스테이징 브랜치 경유.

### Tier 3: 실험적 랩 및 프로토타입 (`cka-lab`)
- **Branch Protection:** Advisory / CI 자동 실행 연계.
- **병합 게이트:** 로컬 검증 후 메인테이너 수동 패스트포워드 병합.

## 4. `gh` CLI를 통한 검증 및 설정

OpenForge는 GitHub CLI를 통해 Branch Protection 상태를 계획하고 안전하게 적용하는 스크립트(`templates/scripts/plan-branch-protection.sh`, `check-branch-protection.sh`)를 제공합니다.

```bash
# Dry-run 계획: 활성 CI 검사 컨텍스트 확인
bash templates/scripts/plan-branch-protection.sh dasomel/openforge main

# OpenForge 베이스라인 보호 규칙 적용 (관리자 권한 필요)
bash templates/scripts/plan-branch-protection.sh dasomel/openforge main --apply
```

## 5. 추적성 및 연결 문서

- **ADR-0003:** [위험 기반 OSS 보안 거버넌스](adr/0003-risk-based-oss-security-governance-ko.md)
- **ADR-0006:** [릴리스 공급망 보안 통제](adr/0006-build-security-into-release-supply-chain-ko.md)
- **ADR-0011:** [CI 복원력과 보안 보증](adr/0011-ci-resilience-must-not-encourage-security-bypass-ko.md)
- **ADR-0012:** [의도적인 예외 기록 및 기한 설정](adr/0012-document-and-time-bound-intentional-exceptions-ko.md)
- **참고 메트릭:** [docs/reference-metrics-ko.md](reference-metrics-ko.md)
