# Upgrade 및 Compatibility Engineering 표준

Upgrade는 단순 버전 치환이 아니라 Engineering Change입니다. Compatibility는 필요한 조건이지만 adoption의 충분조건은 아닙니다.

## 요구사항

- 필요한 경우 지원 버전/호환성 matrix를 유지합니다.
- patch, minor, major, runtime/toolchain, security, migration 변경을 분류합니다.
- 일반 upgrade에는 dependency cooling/review 정책을 적용합니다.
- 이전/목표 버전, dependency graph 변경, breaking change를 기록합니다.
- merge 전에 영향을 받는 build, test, package, deployment, release workflow를 확인합니다.
- 변경에 맞는 clean-build, regression, compatibility validation을 수행합니다.
- release-critical upgrade는 last-known-good과 deterministic rollback 경로를 유지합니다.
- major/runtime/toolchain 변경은 가능한 경우 canary/staged adoption을 사용합니다.
- deprecation과 migration 작업을 문서화합니다.
- compatibility test가 integrity, provenance, security 실패를 우회하도록 하지 않습니다.

## Runtime / Toolchain migration

npm → pnpm, Node → Bun 같은 migration은 이전 toolchain에 의존하는 모든 workflow, script, 개발 문서, container, release 경로를 함께 검사해야 합니다.

## 증적

```text
previous version
→ target version
→ dependency diff
→ compatibility matrix
→ build/test result
→ security result
→ artifact digest
→ rollback reference
```
