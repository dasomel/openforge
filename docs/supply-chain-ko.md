# 공급망 보안 표준

OpenForge는 소프트웨어 공급망 보안을 포트폴리오 공통 엔지니어링 통제로 정의합니다. 호환성은 업그레이드 조건이지만 신뢰의 근거는 아닙니다.

## 채택 흐름

```text
discover
  → compatibility
  → integrity / provenance
  → release age / cooling
  → dependency diff review
  → isolated build / test
  → security / evidence checks
  → canary
  → progressive adoption
```

`latest compatible`만으로 dependency를 채택해서는 안 됩니다.

## Immutable Input

릴리스에 중요한 input은 가능한 경우 immutable하고 감사 가능한 identity를 가져야 합니다.

- application dependency는 lockfile과 exact version을 사용합니다.
- package integrity/checksum을 검증합니다.
- container image, Helm/OCI artifact, 다운로드 도구는 immutable digest 또는 검증된 checksum으로 고정합니다.
- GitHub Actions는 commit SHA로 고정합니다.
- release 경로에서 `latest`, floating image tag, 제한 없는 dependency range, mutable download URL 사용을 금지합니다. 예외는 명시적으로 기록합니다.
- source revision, dependency lock 상태, builder/tool version, artifact digest를 연결합니다.

## Cooling 정책

일반적인 third-party dependency 채택의 기본값은 **최소 14일 release-age/cooling period**입니다.

Cooling은 vulnerability scan을 대신하지 않습니다. 긴급 보안 업데이트는 정확한 버전, 사유, 영향 범위, 검증 근거, 승인자, rollback 대상, 재검토 일자를 기록하는 예외 절차를 거쳐 조기 채택할 수 있습니다.

## Dependency Update 검토

dependency update마다 다음 정보를 확인할 수 있어야 합니다.

- 이전/신규 버전
- direct/transitive 변경
- lockfile/checksum 변경
- release age/timestamp
- integrity/provenance 상태
- build/install script 또는 generated code 변경
- advisory/revocation/withdrawal 상태
- 영향받는 artifact

가능하면 PR에 자동 dependency diff evidence를 제공합니다.

## Build-time Trust Boundary

install hook, build script, proc-macro, code generator, plugin, test helper, package-manager hook은 실행 가능한 공급망 input입니다.

고위험 build/test 작업은 가능한 경우 다음을 적용합니다.

- 최소 권한 credential
- 격리된 runner/container
- allowlist 기반 outbound network
- 예상하지 않은 outbound access 실패
- build/test에 불필요한 credential 제거
- 조사에 필요한 build evidence 보존

애플리케이션 테스트 성공만으로 build 과정이 신뢰할 수 있다고 판단하지 않습니다.

## SBOM / Provenance

릴리스 evidence는 runtime dependency뿐 아니라 관련 build-time dependency도 포함해야 합니다.

```text
source revision
  → dependency/tool manifest
  → builder identity/version
  → build/test evidence
  → artifact digest
  → release/promotion record
```

## Canary / Progressive Adoption

검증된 신규 dependency release를 모든 저장소에 동시에 적용하지 않습니다.

canary 저장소 또는 profile에서 clean build, regression, security/provenance 검증을 수행한 후 exact version/digest를 승격합니다.

## Quarantine / Rollback

각 release line은 last-known-good dependency manifest 또는 lock snapshot을 보존하는 것을 권장합니다.

악성/변조/철회 의심 버전이 발견되면:

1. affected version/digest quarantine
2. 신규 promotion 차단
3. 영향 repository/artifact 확인
4. last-known-good dependency set 복원
5. immutable input으로 rebuild/verify
6. incident/evidence 보존

Rollback은 당시 upstream registry가 반환하는 최신 상태에 의존해서는 안 됩니다.

## Offline / Air-gapped

offline release profile도 live dependency resolution 없이 승인된 dependency/artifact/cache bundle로 재현 가능해야 합니다.

bundle에는 exact manifest/lockfile, package artifact, checksum/signature, tool version, base image/OCI reference, SBOM/provenance evidence를 포함하는 것을 권장합니다.

검증되지 않은 input은 fail-closed 하는 것을 기본으로 합니다.

## Ecosystem 최소 기준

| Ecosystem | 최소 통제 |
|---|---|
| npm / pnpm | lockfile, frozen install, integrity 검증, lifecycle script 검토 |
| Go | `go.sum`, checksum 검증, toolchain/tool 고정 |
| Rust | `Cargo.lock`, locked build, checksum/registry 검증 |
| Python | lock 또는 hash-pinned requirements, build tool 고정 |
| Maven / Gradle | dependency/plugin version 관리, repository integrity, dependency tree 검토 |
| OCI / Helm | immutable digest, 가능한 경우 provenance/signature 검증 |
| Packer / OS image | package/tool 고정, checksum/signature, input manifest |
| Nix | flake/input lock, immutable source, offline cache 검증 |
| GitHub Actions | commit-SHA pinning 및 action update 검토 |

## Governance

OpenForge는 포트폴리오 공급망 정책의 reference implementation입니다. 각 repository의 공급망 정책은 호환되지 않는 별도 규칙을 만드는 대신 이 표준을 참조하는 것을 원칙으로 합니다.

이 문서는 `docs/change-management.md`와 함께 유지하며, dependency/runtime/toolchain 변경 시 workflow 전체 영향 분석을 요구합니다.