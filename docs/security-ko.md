# 보안 표준

보안은 릴리스 직전에 추가하는 기능이 아니라 프로젝트의 기본 요구사항입니다.

## 규칙

- password, token, API key, private key, 운영 secret을 commit하지 않습니다.
- 민감한 값은 secret manager 또는 GitHub Actions secrets를 사용합니다.
- 애플리케이션, Kubernetes 리소스, CI credential에 최소 권한을 적용합니다.
- 외부 입력을 검증하고 안전하게 실패하도록 합니다.
- dependency와 base image를 최신 상태로 유지합니다.
- 가능한 경우 CI에서 보안 및 dependency scan을 실행합니다.
- 보안 정책과 취약점 신고 절차를 제공합니다.
- 보안에 영향을 주는 중요한 아키텍처 결정은 기록합니다.

## 공급망

권장 항목:

- dependency pinning 또는 lockfile
- SBOM 생성
- provenance/attestation
- 이미지 취약점 검사
- 가능한 경우 release signing

## 사고 대응

보안 문제는 수정 또는 완화가 준비될 때까지 비공개로 신고합니다.
공개 Issue에는 민감한 운영 정보를 기록하지 않습니다.
