# 기존 OSS 구현 사례 기반 메트릭

> 기존 dasomel OSS 저장소에서 실제로 사용하고 있는 패턴을 OpenForge의 실무 참고 기준으로 정리한 메트릭이다.

## 1. 목적

OpenForge는 표준을 정의하지만, 새로운 저장소에 표준을 적용할 때 실제 구현 사례와 비교할 수 있으면 훨씬 쉽게 품질을 판단할 수 있다. 이 문서는 이미 운영 중인 OSS 프로젝트의 패턴을 기반으로 한 가벼운 maturity scorecard를 제공한다.

이 메트릭은 **모든 프로젝트에 강제되는 절대 기준이 아니다.** 해당하지 않는 항목은 N/A로 표시할 수 있으며, 의도적인 예외는 ADR에 남긴다.

## 2. Repository Maturity Matrix

| 영역 | 메트릭 | 목표 | 기존 참고 사례 | 확인 대상 |
|---|---|---:|---|---|
| Documentation | 영문 README | 1 | 대부분의 성숙 저장소 | `README.md` |
| Documentation | 한글 README | 1 | 현재 dasomel OSS 방향 | `README-ko.md` |
| Documentation | 언어별 문서 쌍 | 적용 문서 100% | English canonical + `-ko.md` | CI/문서 감사 |
| Documentation | Architecture 문서 | 1 | Narwhal / Narwhal Portal | `docs/architecture*.md` |
| Documentation | Development guide | 1 | 주요 활성 저장소 | `docs/development*.md` |
| Documentation | Release guide | 1 | 릴리스 중심 저장소 | `RELEASING*.md` |
| Documentation | Version inventory | 플랫폼 프로젝트는 1 | Narwhal 사례 | `VERSIONS.md` |
| Documentation | Lessons / mistakes log | 권장 | Narwhal / KubeMetal 사례 | `lessons-log*.md` / `mistakes-log*.md` |
| Architecture | ADR 체계 | 1 | OpenForge / Narwhal Portal 사례 | `docs/adr/` |
| Architecture | Decision Management Standard | 여러 프로젝트 공통 표준 저장소 권장 | OpenForge | `docs/decision-management*.md` |
| Architecture | ADR 영/한 쌍 | 사용자 대상 ADR 100% | OpenForge | ADR CI validation |
| Architecture | Decision Map / Traceability | Standards Repository 권장 | OpenForge | `docs/decision-map*.md` |
| GitHub | PR template | 1 | ldapium 등 | `.github/pull_request_template.md` |
| GitHub | Bug template | 1 | 일반적인 OSS 관행 | `.github/ISSUE_TEMPLATE/` |
| GitHub | Feature template | 1 | 일반적인 OSS 관행 | `.github/ISSUE_TEMPLATE/` |
| GitHub | Architecture template | 권장 | Beluga/OpenForge 방향 | `.github/ISSUE_TEMPLATE/` |
| CI | 자동 CI | 1 | 활성 코드 저장소 | `.github/workflows/` |
| CI | Format check | 언어별 1 | 언어별 표준 | workflow |
| CI | Test | 1 | 코드 저장소 | workflow |
| CI | Build | 애플리케이션/라이브러리는 1 | 코드 저장소 | workflow |
| CI | Documentation validation | 권장 | OpenForge 표준 | workflow |
| CI | ADR pair/index validation | Bilingual ADR 사용 시 권장 | OpenForge | `templates/scripts/validate-adrs.sh` |
| Security | Dependency update 자동화 | 1 | Dependabot 사례 | `.github/dependabot.yml` |
| Security | Container scanning | 컨테이너가 있으면 필수 | Trivy 계열 사례 | CI |
| Security | Code scanning | 권장 | CodeQL / 동등 도구 | CI |
| Security | Scorecard / supply-chain 검사 | 공개 OSS 권장 | ldapium 사례 | workflow |
| Security | SECURITY 정책 | 1 | 성숙 OSS 관행 | `SECURITY*.md` |
| Development | Formatter | 언어별 1 | 프로젝트별 표준 | tooling matrix |
| Development | Go formatter | `gofumpt` | OpenForge Go 표준 | `gofumpt` 검사 |
| Development | Go 정적 분석 | `go vet` + 권장 static analyzer | OpenForge Go 표준 | CI |
| Development | Test command | 문서화된 명령 1개 | Makefile/개발 문서 | `make test` 등 |
| Development | 통합 task runner | 권장 | KubeMetal Makefile 사례 | `Makefile` |
| Development | Code graph | 복잡한 코드베이스 권장 | codegraph / graphify 활용 사례 | 생성 graph/artifact |
| Development | AI agent 지침 | 권장 | Narwhal / KubeMetal / Portal 사례 | `AGENTS.md`, `CLAUDE.md` 등 |
| Release | Changelog | 1 | 기존 OSS 사례 | `CHANGELOG.md` |
| Release | Versioning 정책 | 1 | 기존 OSS 사례 | `VERSION*` / release docs |
| Release | Release workflow | 권장 | KubeMetal / 활성 프로젝트 | `.github/workflows/` |
| Release | Artifact 검증 | 권장 | Supply-chain 표준 | digest/SBOM/provenance |
| Configuration | `.env.example` | 환경변수가 있으면 필수 | ldapium 사례 | `.env.example` |
| Localization | UI i18n | UI 프로젝트는 필수 | Beluga Manager 방향 | locale resources |
| Localization | `en-US` | 1 | Beluga Manager 표준 | locale resources |
| Localization | `ko-KR` | 1 | Beluga Manager 표준 | locale resources |

## 3. 점수 계산

빠른 Repository Health Check를 위해 각 적용 항목을 다음과 같이 평가한다.

- **2 — 구현되어 있고 가능한 경우 자동화됨**
- **1 — 수동 또는 부분적으로 구현됨**
- **0 — 없음**
- **N/A — 해당 없음**

권장 해석:

| 점수 | 성숙도 |
|---:|---|
| 90–100% | Production-ready OSS foundation |
| 75–89% | Healthy / minor gaps |
| 60–74% | Developing / improvement recommended |
| <60% | Foundation work required |

백분율은 N/A를 제외한 적용 가능한 항목만으로 계산한다.

## 4. 참고 프로젝트

이 매트릭스는 처음부터 임의로 만든 것이 아니라 기존 저장소의 실제 관행을 기반으로 한다.

- `openforge` — Cross-project ADR Governance, 영/한 Decision History, CI Validation, Standard/Template Traceability
- `narwhal` — 플랫폼 아키텍처, 버전, lessons, AI 지침, release/deployment 문서
- `narwhal-portal` — ADR, roadmap, design system, AI 지침
- `nfs-quota-agent` — 영/한 문서 및 개발/release 관행
- `kube-ready-box` — 영/한 README 및 AI/skill 지침
- `kubemetal` — Makefile, release workflow, mistakes log, AI 지침
- `ldapium` — security/release, `.env.example`, PR 표준, Scorecard 계열 supply-chain 검사
- `beluga-manager` — 영/한 문서, unified domain/API architecture, i18n-first UI 정책

## 5. 사용 방법

새 OSS 저장소를 만들 때:

1. OpenForge 프로젝트 골격을 적용한다.
2. Reference Metrics checklist를 실행한다.
3. 각 항목을 `2`, `1`, `0`, `N/A`로 표시한다.
4. 적용 대상 중 `0`인 항목은 issue로 등록한다.
5. 의도적인 예외는 ADR에 기록한다.
6. 장기적인 공통 Default는 ADR → Standard → Enforcement → Adoption Evidence로 연결한다.
7. 첫 stable release 전에 다시 matrix를 실행한다.

기존 프로젝트에서 더 나은 반복 가능한 관행이 발견되면 이 매트릭스도 함께 발전시킨다.
