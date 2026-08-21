# 변경 관리 및 영향 분석 표준

OpenForge는 engineering change를 단순한 소스 코드 변경이 아니라 시스템 계약(contract)의 변경으로 관리합니다.

dependency, runtime, build command 또는 개발 도구가 바뀌면 애플리케이션 호환성에 문제가 없어도 CI workflow, release workflow, deployment, generated artifact, 운영 절차가 영향을 받을 수 있습니다.

## 변경 영향 분석

중요 변경은 최소한 다음을 검토합니다.

- source/build command
- package manager 및 dependency resolution
- runtime/toolchain version
- generated file/generator
- CI workflow
- CD/deployment workflow
- release/packaging workflow
- test/E2E environment
- container/base image
- documentation/operational procedure
- offline/air-gap asset
- security/supply-chain control

소스 구현이 정상이어도 기존 계약을 전제로 하는 workflow가 남아 있다면 변경은 완료된 것이 아닙니다.

## 영향 분석 표

| 영역 | 확인 질문 |
|---|---|
| Source | 어떤 script, command, API가 변경되는가? |
| Dependencies | package manager, lockfile, version resolution이 바뀌는가? |
| Runtime | 요구 runtime/toolchain이 바뀌는가? |
| CI | 변경된 command를 실행하는 workflow는 무엇인가? |
| CD | 배포 workflow가 영향을 받는가? |
| Release | packaging/publishing workflow가 영향을 받는가? |
| Generated output | RSS, 문서, manifest 등의 재생성이 필요한가? |
| Security | 새 executable/download/build input이 생기는가? |
| Offline | 새로운 cache/mirror artifact가 필요한가? |
| Documentation | 개발/설치/release 문서가 바뀌는가? |

Dependency/runtime/toolchain 변경은 PR 또는 연계 Issue에 영향 분석을 남깁니다.

## Workflow 전체 점검

Build 또는 toolchain contract가 변경되면 **모든 workflow**에서 영향을 받는 command, package manager, runtime을 검색합니다.

예를 들어 Node 프로젝트의 build가:

```text
npm run build
  → bun <script>
```

을 필요로 하게 되면 `npm run build`, `bun`, packaging, release, generated-output script를 실행할 수 있는 모든 workflow를 점검해야 합니다.

한 workflow에서 설치한 tool이 다른 workflow에도 존재한다고 가정하지 않습니다.

## Runtime / Toolchain 일관성

Build/release contract에 필요한 runtime/toolchain은 각 workflow가 명시적으로 설치하거나 문서화된 reusable workflow를 통해 상속해야 합니다.

예: Node/npm/pnpm/Bun, Python/uv/Poetry, Go, Rust/Cargo, JDK/Maven/Gradle, Packer, Terraform, kubectl, Helm.

암묵적으로 runner에 설치되어 있는 tool에 의존하지 않습니다.

권장 흐름:

```text
setup runtime/toolchain
→ verify version
→ install dependencies deterministically
→ test
→ build/package/release
```

## Workflow Contract Check

가능한 경우 expensive 단계 전에 runtime/tool version을 검증합니다.

```text
bun --version
node --version
pnpm --version
go version
rustc --version
java -version
```

`command not found` 또는 호환되지 않는 tool 오류가 뒤늦게 발생하기보다 early fail을 유도합니다.

## 변경 등급

### Class A — 문서 변경

실행 또는 release contract가 변경되지 않는 문서 수정.

### Class B — 내부 구현

외부 build/release contract가 바뀌지 않는 내부 동작 변경.

### Class C — Dependency / Runtime / Toolchain

다음과 같은 변경입니다.

- Bun 도입
- Node/Python/Go/Rust/JDK 업그레이드
- package-manager 변경
- CI action/tool 변경
- build plugin/code generator 변경

Class C는 반드시 변경 영향 분석을 포함합니다.

### Class D — Release / Deployment / Security Boundary

생성 artifact, deployment 권한, release input 또는 security control을 바꾸는 변경입니다.

Class D는 영향 분석과 security/release evidence를 포함합니다.

## Regression Rule

변경 중 발견된 integration failure는 가능한 경우 deterministic CI regression check로 전환합니다.

예를 들어 build가 Bun을 요구하게 되었다면 release-producing workflow마다 요구된 Bun version이 설치되고 검증되는지 확인해야 합니다.

목표는 과거의 특정 오류만 막는 것이 아니라 workflow configuration drift라는 오류 종류 전체를 막는 것입니다.

## Supply Chain 연계

Class C/D 변경은 `docs/supply-chain.md`를 따라야 합니다.

```text
Change request
  → compatibility
  → dependency/provenance review
  → change impact analysis
  → CI/CD contract validation
  → isolated build/test
  → evidence
  → progressive adoption
```

호환성은 유지되지만 build script, install hook, generated artifact, required CI runtime이 바뀌는 dependency upgrade는 저위험 변경으로 취급하지 않습니다.

## PR 요구사항

중요 변경 PR은 다음을 명시하는 것을 권장합니다.

- change class
- affected contract
- affected workflow
- runtime/toolchain 변경
- dependency/lockfile 변경
- documentation 영향
- 실행한 test와 workflow validation
- release behavior 변경 시 rollback/mitigation

## Reusable Workflow 권장

여러 workflow에서 같은 runtime/toolchain setup을 사용한다면 reusable workflow 또는 shared setup action을 우선해 version drift를 줄입니다.

의도적으로 서로 다른 runtime version을 사용한다면 그 이유와 compatibility boundary를 문서화합니다.

## Release Gate

Release 전에 다음을 확인합니다.

- 모든 release-producing workflow에서 source build 성공
- 필요한 runtime/tool이 명시적으로 설치되고 version verified
- dependency lock/integrity check 통과
- 관련 build input이 SBOM/provenance에 포함
- 필요한 generated artifact 갱신
- release documentation과 실제 command 일치
- 필요한 경우 offline/air-gap asset 완전성 확인

## 역사적 회귀 패턴

Build command는 문법적으로 그대로여도 runtime requirement가 바뀔 수 있습니다.

```text
package.json
  "build": "next build && bun scripts/generate-rss.js"
```

CI가 계속 `npm run build`를 실행하더라도 build contract는 Bun을 필요로 하도록 변경되었습니다.

따라서 해당 command를 호출하는 모든 workflow에서 Bun setup과 version verification을 확인해야 합니다.