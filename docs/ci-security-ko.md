# CI/CD 보안 표준

CI/CD는 단순한 빌드 기능이 아니라 보안 경계입니다. Workflow, runner, cache, credential, artifact, trigger를 모두 보안 대상 인프라로 취급합니다.

## 1. Workflow 신뢰 경계

- fork PR, issue, comment, 외부 event, 생성된 콘텐츠는 기본적으로 untrusted input으로 취급합니다.
- 신뢰하지 않는 코드 검증은 `pull_request`를 우선합니다.
- fork가 제어하는 코드를 privileged release/publish workflow에서 실행하지 않습니다.
- `pull_request_target` 사용은 가급적 피하고, 불가피하면 trust boundary와 예외 사유를 기록하며 untrusted checkout/execution을 금지합니다.
- validation, release, publishing workflow를 분리합니다.

## 2. 권한

- 가능한 경우 workflow 수준에서 `permissions: {}`로 시작하고 필요한 job에만 권한을 부여합니다.
- `contents: write`, `packages: write`, `id-token: write`, deployment와 secret 접근은 필요한 job/environment로 제한합니다.
- release identity를 일반 test/build job에서 상속하지 않습니다.
- 장기 토큰보다 short-lived OIDC credential을 우선합니다.

## 3. Actions / reusable workflow

- 제3자 Action은 immutable commit SHA로 고정합니다.
- reusable workflow와 composite action도 dependency로 취급합니다.
- action source, transitive dependency, ownership 변경, release 변경을 검토합니다.
- mutable tag를 보안 identity로 신뢰하지 않습니다.
- 가능한 경우 action upgrade에도 dependency cooling/review 정책을 적용합니다.

## 4. Runner 보안

- untrusted 또는 high-impact job에는 ephemeral runner를 우선합니다.
- untrusted build runner와 release/publish runner를 분리합니다.
- 재사용 runner는 workspace, credential, cache, temporary file을 job 사이에 정리합니다.
- 일반 CI runner에 개발자 credential이나 production credential을 노출하지 않습니다.
- high-risk runner에서 예상치 못한 process와 network destination을 관찰합니다.

## 5. Cache 보안

Cache는 신뢰되지 않은 상태이며 공급망 자산입니다.

- PR, main, release, publish cache를 분리합니다.
- dependency cache와 release/publish cache를 분리합니다.
- untrusted workflow가 privileged cache에 쓰지 못하도록 합니다.
- 가능한 경우 cache key에 trust context를 포함합니다.
- release-critical job에서 restore한 cache를 사용하기 전에 검증합니다.
- high-risk workflow에는 cache poisoning 회귀 테스트를 추가합니다.

## 6. Network egress

- build/test job은 allowlist된 registry/service 사용을 우선합니다.
- privileged build/release job의 임의 outbound 연결은 차단을 우선합니다.
- 외부 서비스와 remote download 예외는 기록합니다.
- build 단계의 예상 밖 DNS, HTTP(S), webhook 등 outbound 활동을 조사합니다.

## 7. OIDC와 publish identity

- OIDC subject/audience/trust policy를 repository, branch, environment에 맞춰 최소화합니다.
- `id-token: write`는 필요한 job에만 부여합니다.
- build identity와 publish identity를 분리합니다.
- 유효한 OIDC token은 authorization mechanism일 뿐 실행된 코드가 안전하다는 증명이 아닙니다.

## 8. Artifact 처리

- untrusted workflow의 artifact를 trusted release input으로 취급하지 않습니다.
- release artifact를 immutable commit, dependency set, builder identity와 연결합니다.
- transfer 또는 cache restore 후 checksum/digest를 검증합니다.
- publish 전 최종 artifact를 freeze합니다.

## 9. 보안 민감 경로

다음 경로는 보호 대상입니다.

```text
.github/workflows/**
.github/actions/**
Dockerfile*
package.json
lockfiles
release scripts
publishing configuration
OIDC/trust configuration
CODEOWNERS
SECURITY.md
```

이 경로 변경은 repository governance 정책에 따라 강화된 review를 적용하는 것을 권장합니다.

## 10. 회귀 요구사항

알려진 CI 장애는 가능한 경우 deterministic check로 전환합니다. runtime/toolchain migration 시 영향을 받는 build, packaging, release contract를 실행하는 모든 workflow를 점검해야 합니다.
