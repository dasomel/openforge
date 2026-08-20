# OSS 참고 프로젝트 관행 감사

## 한국어

OpenForge는 실제 개발 중인 `dasomel` OSS를 기준으로 표준을 다시 검토했습니다. 주요 참조 대상은 Narwhal, Narwhal Portal, nfs-quota-agent, kube-ready-box, KubeMetal, ldapium, Beluga입니다.

### 재사용 가능한 공통 관행

- 영/한 문서 쌍: `<name>.md` + `<name>-ko.md`
- 버전 기준 문서: `VERSIONS.md`와 같은 단일 authoritative inventory
- 영/한 CHANGELOG
- ADR 및 설계 기록
- Incident/Lessons/Mistakes Log
- `AGENTS.md`, `CLAUDE.md` 등 AI 개발 지침
- 명시적인 Release Guide
- Security Policy
- Legal / Third-party attribution
- `.env.example` 등 안전한 설정 예시
- Makefile 기반의 간결한 개발 명령 집합
- 여러 파일의 버전을 비교하는 자동화된 version check
- Scorecard, provenance, SBOM, vulnerability 등 supply-chain 검증
- 공통 문서와 배포 대상별 문서의 분리
- Helm chart README와 values 문서
- 이미지/패키징/registry 문서
- CI 회귀 검사와 실패 기록의 연결

### 문서 파일명 예외

`-ko.md` 규칙은 **프로젝트가 직접 소유하는 사용자용 문서**에 적용합니다. Third-party 문서, vendored 문서, generated 문서, upstream distribution contract의 일부인 파일명까지 강제로 변경하지 않습니다.

Narwhal의 vendored chart 문서와 같은 경우에는 upstream 파일명을 유지합니다.

### 권장 증거 순환

```text
장애 / 변경
   ↓
Issue / ADR / Incident
   ↓
구현
   ↓
Regression Test / CI Check
   ↓
Release Note / Changelog
   ↓
재사용 가능한 문서
```

인프라와 플랫폼 프로젝트에서는 업그레이드 후 동일한 통합 문제가 재발할 수 있으므로 이 순환을 표준 관행으로 권장합니다.

## English

OpenForge treats the observed repository practices as reference evidence. Common practices become reusable standards; project-specific choices remain explicit through ADRs or project-local guidance.
