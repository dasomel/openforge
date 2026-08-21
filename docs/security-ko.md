# 보안 표준

보안은 릴리스 직전에 추가하는 기능이 아니라 프로젝트의 기본 요구사항입니다.

## 규칙

- password, token, API key, private key, 운영 secret을 commit하지 않습니다.
- 민감한 값은 secret manager 또는 GitHub Actions secrets를 사용합니다.
- 애플리케이션, Kubernetes 리소스, CI credential에 최소 권한을 적용합니다.
- 외부 입력을 검증하고 안전하게 실패하도록 합니다.
- dependency와 base image는 공급망 정책에 따라 관리하며 단순히 최신 버전을 사용하는 것을 기본값으로 삼지 않습니다.
- 가능한 경우 CI에서 보안 및 dependency scan을 실행합니다.
- 보안 정책과 취약점 신고 절차를 제공합니다.
- 보안에 영향을 주는 중요한 아키텍처 결정은 기록합니다.

## 공급망

OpenForge는 `docs/supply-chain.md`를 포트폴리오 공통 공급망 보안 기준으로 사용합니다.

필수 관리 항목:

- 가능한 경우 dependency/artifact의 immutable identity
- lockfile 및 checksum/integrity 검증
- dependency release-age/cooling 정책
- direct/transitive dependency diff 검토
- build-time dependency 및 script trust boundary 검토
- 고위험 build/test 작업의 outbound network 제한
- runtime뿐 아니라 관련 build-time input을 포함한 SBOM
- 가능한 경우 provenance/attestation
- 이미지 취약점 검사
- 가능한 경우 release signing
- quarantine 및 last-known-good rollback
- 필요 환경의 offline/air-gapped 검증

`latest compatible`만으로는 안전한 dependency 채택을 판단할 수 없습니다.

## 변경 영향 분석

dependency, runtime, package manager, build tool, CI action, release tool 변경은 `docs/change-management.md`의 Class C 또는 D 변경으로 취급하며 workflow 전체에 대한 영향 분석을 수행합니다.

소스 코드 변경이 성공했더라도 독립적인 CI/CD/release workflow가 이전 runtime 또는 build contract에 의존한다면 변경은 완료된 것이 아닙니다.

## 사고 대응

보안 문제는 수정 또는 완화가 준비될 때까지 비공개로 신고합니다.
공개 Issue에는 민감한 운영 정보를 기록하지 않습니다.

보안 사고 또는 통합 실패에서 반복 가능한 취약점이 확인되면 deterministic CI/regression check로 전환하고 관련 표준 문서를 갱신합니다.