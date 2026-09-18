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

Issue/PR 자체를 변경 기록으로 사용하며 별도 Change Package는 필요하지 않습니다.

### Class B — 내부 구현

외부 build/release contract가 바뀌지 않는 내부 동작 변경.

Issue에 Acceptance Criteria를 반드시 명시합니다. 독립적으로 검증 가능한 구현 단계가 여러 개라면 간단한 Task Checklist 사용을 권장합니다. 복잡하거나 Component Boundary를 넘거나 운영 위험이 큰 변경이 아니라면 전체 Change Package는 선택 사항입니다.

### Class C — Dependency / Runtime / Toolchain

다음과 같은 변경입니다.

- Bun 도입
- Node/Python/Go/Rust/JDK 업그레이드
- package-manager 변경
- CI action/tool 변경
- build plugin/code generator 변경

Class C는 반드시 변경 영향 분석을 포함합니다.

Class C는 본격적인 구현을 시작하기 전에 Change Package를 반드시 사용합니다.

### Class D — Release / Deployment / Security Boundary

생성 artifact, deployment 권한, release input 또는 security control을 바꾸는 변경입니다.

Class D는 영향 분석과 security/release evidence를 포함합니다.

Class D는 본격적인 구현을 시작하기 전에 Change Package를 반드시 사용합니다. `docs/decision-management-ko.md`의 Threshold를 넘는 변경은 ADR도 필요합니다.

## Change Package

Change Package는 구현 전에 Intent, Requirement, Acceptance Scenario, Verification을 고정하는 짧은 수명의 변경 단위 계약입니다. 전체 시스템을 다시 설명하는 별도의 장기 Spec이 아닙니다.

Class C, Class D 및 복잡한 Class B 작업에는 재사용 가능한 [`CHANGE.md`](../templates/change/CHANGE.md), [`TASKS.md`](../templates/change/TASKS.md) Template을 사용합니다. Issue/PR이 가장 명확한 협업 공간이라면 Package 내용을 그 안에서 직접 관리할 수 있습니다. 작업 Branch에서 임시 파일을 사용할 수 있지만, 운영 문서로 계속 가치가 있는 경우가 아니라면 영구적인 `changes/` Archive로 Merge하지 않는 것을 권장합니다.

Change Package에는 다음을 반드시 식별합니다.

- Problem, Intent, Scope, Non-goals
- Stable ID를 가진 테스트 가능한 Requirement
- 명시적인 Acceptance Scenario(동작은 가능하면 `Given / When / Then`)
- 관련 Architecture Decision 또는 ADR이 필요하지 않은 이유
- 이 표준의 Matrix를 사용한 Change Impact
- Implementation Task와 Dependency
- Verification Plan과 Expected Evidence
- 사용자 또는 운영에 영향을 줄 수 있는 변경의 Rollout, Rollback 또는 Recovery
- 재사용 계약이 바뀌는 경우 Portfolio/Downstream Impact

Requirement, Task, Evidence는 추적 가능해야 합니다. Reviewer가 각 주요 Requirement를 Acceptance Scenario, Implementation Task, Verification Result에 연결할 수 있어야 합니다.

### Review Gate

Class C/D는 본격적인 구현 전에 책임 Maintainer가 Change Package를 검토하고 수락해야 합니다. 수락 전에 탐색, 재현, 되돌릴 수 있는 Prototype은 가능하지만, 최종 계약을 암묵적으로 확정하거나 Production/Shared Environment를 변경해서는 안 됩니다.

수락은 Problem, Intended Outcome, Boundary, Verification Approach가 구현을 시작할 만큼 명확하다는 뜻입니다. 모든 구현 세부사항을 미리 확정한다는 뜻은 아닙니다. 수락 이후 Scope 또는 Requirement가 실질적으로 바뀌면 Package에 반영하고 다시 검토합니다.

### Lifecycle과 Source of Truth

```text
Issue
  → Change 분류
  → 필요한 경우 Change Package 작성/검토
  → 추적 가능한 Task 구현
  → Acceptance Scenario 검증
  → Evidence 수집
  → Durable Truth 동기화
  → Review 및 Merge
```

완료할 때 장기적으로 유지할 정보는 이를 소유하는 Artifact로 승격합니다.

- Behavior와 Invariant → Code와 Test
- 현재 운영 계약 → Normative Documentation
- 장기적인 Rationale → ADR
- 측정 결과 → Evidence Record
- Cross-project State → Portfolio Status
- 변경 이력 → Issue, PR, Git History

Code, Test, Documentation, ADR을 중복하는 별도의 장기 Spec Tree를 만들지 않습니다. Merge된 Issue/PR을 Change Intent와 Review History의 기본 Archive로 사용합니다.

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
