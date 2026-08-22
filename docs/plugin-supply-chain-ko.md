# Plugin 공급망 Intake 표준

OpenForge는 외부에서 가져오는 AI agent plugin, skill, hook, script, repository를 명시적인 intake 정책을 통과하기 전까지 모두 untrusted input으로 취급합니다.

## 신뢰 모델

Repository 소유자, 조직명, star 수, publisher 이름이나 인기만으로 trust를 결정해서는 안 됩니다.

설치 판단은 다음 네 가지를 독립적으로 확인합니다.

| 항목 | 필수 근거 |
|---|---|
| Source identity | repository URL + immutable commit/tag reference |
| Content integrity | content digest/checksum 또는 동등한 immutable artifact identity |
| Dependency integrity | lockfile/manifest + 가능한 경우 checksum |
| Executable behavior | hook/script/install/build command 정적 검사 |

Trusted source라는 이유만으로 executable content를 안전하다고 판단하지 않습니다.

## Intake evidence

승인된 plugin은 최소한 다음 설치 evidence를 남기는 것을 권장합니다.

```yaml
source:
  repository: https://example.invalid/plugin
  revision: <immutable-commit-sha>
  reference_type: commit
content:
  digest: sha256:<content-digest>
dependencies:
  manifest: <path-or-inline-reference>
  lockfile: <path-or-inline-reference>
installer:
  name: openforge
  version: <installer-version>
assessment:
  static_policy: pass
  network_policy: restricted
  approved_by: <maintainer-or-policy-id>
  approved_at: <timestamp>
rollback:
  known_good_revision: <immutable-reference>
```

## Resolution 정책

Plugin resolution은 다음 순서를 우선합니다.

1. 사전 승인된 offline trusted catalog
2. 승인된 source의 immutable commit 또는 immutable artifact digest
3. 서명/검증 가능한 release와 독립적으로 확인된 artifact identity
4. 별도 예외로 승인된 mutable branch/tag

`main`, `master`, `develop` 등 mutable branch 또는 임의의 version range는 release-grade installer에서 명시적 예외 없이 허용하지 않습니다.

## 정적 검사

설치 전에 최소한 다음을 검사합니다.

- package-manager lifecycle script
- `preinstall`, `install`, `postinstall`, build/release hook
- shell, Python, Node, Bun, PowerShell 등 executable file
- remote content 다운로드 후 실행
- `eval` 및 command execution API 등 동적 실행
- credential, token, SSH key, kubeconfig, cloud metadata 접근
- 설치 경계 밖 파일 쓰기
- network client와 외부 endpoint
- persistence/background process
- 난독화 또는 encoded executable payload

정적 검사는 설명 가능하고 policy 기반이어야 하며, 안전성의 최종 증명이 아닙니다.

## Network 경계

Plugin install/build는 가능한 경우 다음과 같이 격리합니다.

- 기본적으로 credential 미제공
- package registry/artifact store allowlist
- DNS/network logging
- 예상하지 않은 outbound destination 차단
- 다른 repository 또는 host 설정을 변경하지 못하는 filesystem boundary

구조상 적용할 수 없는 통제는 residual risk로 명시합니다.

## Quarantine / Revocation

Revocation은 repository 이름이 아니라 immutable revision과 content digest를 기준으로 관리합니다.

의심 버전이 발견되면 quarantine → 신규 설치 차단 → 영향 확인 → known-good revision 복구 → 재검증 → evidence 보존 순서로 처리합니다.

## Offline Trusted Catalog

offline catalog는 plugin의 immutable identity와 integrity metadata를 포함해야 합니다.

```yaml
plugins:
  - name: example-plugin
    repository: https://example.invalid/example-plugin
    revision: 0123456789abcdef0123456789abcdef01234567
    digest: sha256:<digest>
    dependencies:
      lockfile_sha256: <digest>
    installer_min_version: <version>
    status: approved
```

Offline mode에서는 catalog에 없거나 digest가 일치하지 않는 plugin을 fail-closed 해야 합니다.

## Change Management 연계

Dependency, runtime, executable hook, release behavior, security boundary가 바뀌는 plugin update는 `change-management.md`의 Class C 또는 D로 취급합니다.

PR/Issue에는 이전/신규 immutable identity, content/dependency diff, hook/script diff, cooling status, 영향 workflow/runtime, rollback identity, security/provenance evidence를 기록합니다.

## Negative Test 기준

참조 구현은 최소한 다음을 거부해야 합니다.

| 상황 | 기대 결과 |
|---|---|
| typo-squatted repository/name | reject 또는 quarantine |
| 예외 없는 floating branch | reject |
| release 경로의 mutable artifact URL | reject |
| install script가 remote code를 다운로드 후 실행 | reject/quarantine |
| 필요성 없이 credential 접근 | reject |
| digest mismatch | reject |
| revoked revision | reject |
| offline catalog에 없는 plugin | reject |

자세한 공급망 일반 원칙은 [`supply-chain-ko.md`](supply-chain-ko.md)를 따릅니다.
