# CI/CD 표준

CI는 Merge 전에 반복 가능한 검증을 제공하고, CD는 통제 가능하고 재현 가능한 배포를 제공합니다.

## 최소 CI

```text
format → lint → typecheck → test → build
```

프로젝트에 따라 다음을 추가합니다.

- integration test
- E2E test
- container build
- vulnerability scan
- license scan
- SBOM
- Helm/Kubernetes validation

## Pull Request

필수 check는 Branch protection의 기준으로 활용합니다.

## Release

Release workflow는 결정적이고 버전이 지정되며 특정 commit으로 추적 가능해야 합니다.

## Air-gapped / self-hosted

런타임에 public registry나 인터넷 접근을 당연히 가정하지 않습니다. 오프라인 운영이 중요하다면 필요한 artifact를 고정하고 문서화합니다.
