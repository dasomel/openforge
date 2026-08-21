# CI/CD Resilience 표준

CI/CD는 OSS의 운영 의존성이므로 일시적인 플랫폼, registry, network 장애가 상태를 훼손하거나 안전하지 않은 release를 유도하지 않아야 합니다.

## 요구사항

- build/test/release job은 가능한 경우 retry-safe/idempotent하게 설계합니다.
- workflow failure에서도 중요한 artifact/evidence를 보존합니다.
- transient retry와 semantic failure를 구분하며 destructive publish/deploy를 무조건 retry하지 않습니다.
- release-critical project는 가능한 경우 manual/offline fallback을 문서화합니다.
- 선언된 offline/air-gap mode에서는 dependency/artifact mirror 또는 cache를 준비합니다.
- workflow 재실행으로 duplicate/unintended artifact가 publish되지 않도록 합니다.
- 명확한 last-known-good release reference를 유지합니다.
- outage로 발생한 exception을 기록하고 반복 장애는 regression check로 전환합니다.

CI outage가 발생해도 security gate를 무시하고 긴급 publish하지 않습니다.

```text
CI unavailable
→ release candidate 보존
→ approved fallback validation
→ 필요한 경우 명시적 exception
→ 필수 evidence 복구 후 publish
```
