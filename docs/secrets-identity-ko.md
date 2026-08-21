# Secrets 및 Machine Identity 표준

개발, CI, release, deployment에 사용하는 credential은 supply-chain asset입니다.

## 요구사항

- long-lived token보다 short-lived credential과 OIDC를 우선합니다.
- repository, environment, job, action 단위로 최소 권한을 적용합니다.
- developer, CI build, release, production identity를 분리합니다.
- publish 권한은 필요한 release job에만 부여합니다.
- source, generated artifact, cache, log에 secret을 저장하지 않습니다.
- 가능한 경우 secret scanning을 적용합니다.
- 노출 의심 시 credential을 즉시 revoke/rotate합니다.
- emergency credential recovery/replacement 절차를 문서화합니다.

```text
developer
  ≠ CI build
  ≠ release
  ≠ package publish
  ≠ production deployment
```

Identity/OIDC trust/publishing 설정 변경은 security-sensitive change입니다.
