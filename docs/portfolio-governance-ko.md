# OSS 포트폴리오 Governance

[English](portfolio-governance.md)

OpenForge는 여러 OSS의 Engineering State를 **검토 가능하고 Evidence 기반인 Portfolio Control Plane**으로 관리합니다. 각 Repository는 자기 구현의 Source of Truth를 유지하고, OpenForge는 검증된 상태 변경 PR이 merge된 뒤 **공식 Cross-project Portfolio State**를 기록합니다.

## Source of Truth

```text
portfolio/projects.json       Project Registry / 현재 개발 상태
portfolio/relationships.json Cross-project Relationship / Impact Edge
portfolio/milestones.json     Portfolio Milestone / Lifecycle State
portfolio/status.schema.json  Downstream Status Publication Contract
```

Dashboard, Mermaid Graph, Infographic는 Presentation View이며 별도의 Source of Truth가 되어서는 안 됩니다.

## 상태 소유권

```text
개별 OSS Repository
  구현 + Test + Runtime/Security Evidence 소유
             │
             │ 검증된 완료/변경
             ▼
openforge-project-status/v1
             │
             │ Pull Request
             ▼
OpenForge
  Project Identity / State Transition /
  Evidence / Cross-project Impact 검증
             │
             │ Merge
             ▼
공식 Portfolio State
             │
             ├─ Dashboard
             ├─ Dependency / Impact Graph
             ├─ Infographic / Site Data
             └─ Downstream Impact Review
```

Downstream Repository에서 코드가 merge됐다는 사실만으로 Feature Complete라고 판단하지 않습니다. 해당 Capability에 필요한 Evidence Class가 통과한 뒤 Status를 게시해야 합니다.

## Lifecycle

기본 상태:

`planned → designing → implementing → verifying → implemented → adopted`

추가 상태:

- `maintenance` — 신규 기능 개발보다는 유지보수 중심
- `blocked` — 검증된 Blocker로 진행 중단
- `deprecated` — History를 유지하지만 더 이상 권장하지 않음

`implemented`는 해당 Repository Boundary에서 구현/검증이 완료되었다는 의미이고, `adopted`는 공통 OpenForge Standard/Capability가 Portfolio 차원의 Adoption Claim을 할 수 있을 정도로 통합된 상태를 의미합니다.

## Status Publication Contract

각 OSS는 검증이 끝나면 `openforge-project-status/v1` Payload를 생성합니다.

```json
{
  "version": "openforge-project-status/v1",
  "project": "narwhal",
  "repository": "dasomel/narwhal",
  "revision": "v1.4.0",
  "updated_at": "2026-09-07",
  "development": {
    "status": "implemented",
    "milestone": "agent-execution-security",
    "progress_percent": 100
  },
  "capabilities": {
    "agent-execution-security": {
      "status": "implemented",
      "standard": "openforge/agent-execution-security",
      "verification": {
        "unit": "pass",
        "integration": "pass",
        "runtime": "pass",
        "security": "pass"
      }
    }
  },
  "evidence": {
    "issue": 155,
    "pull_request": 201,
    "commit": "abcdef0123456789",
    "ci": "pass",
    "security": "pass",
    "runtime": "pass"
  }
}
```

실제보다 높은 Evidence Class를 표시해서 Portfolio 상태를 Green으로 만들면 안 됩니다.

## Status PR 정책

권장 제목:

```text
chore(portfolio): update <project> development status
```

PR에는 다음을 포함합니다.

1. Project / Revision
2. Lifecycle Transition
3. 변경된 Capability / Standard
4. Issue / PR / Commit Evidence
5. CI / Security / Runtime Verification Class
6. 필요한 경우 Relationship 변경
7. 예상 Cross-project Impact

**Status PR merge가 공식 Portfolio State Transition입니다.**

## 자동화 모델

Downstream Repository는 Release, Milestone, 명시적인 Verification Workflow 성공 이후 Status Publication을 자동화할 수 있습니다.

Cross-repository PR 생성에는 `dasomel/openforge`에 Branch/PR을 생성하는 데 필요한 최소 권한만 가진 GitHub App 또는 Fine-grained Credential을 사용해야 합니다. Broad Owner/Maintainer Token을 배포하지 않습니다.

```text
Repository CI가 Capability 검증
        ↓
Status Publisher가 OpenForge PR 제안
        ↓
OpenForge CI가 Registry / Contract 검증
        ↓
Maintainer 또는 허용된 Automation이 Merge
```

Downstream Workflow가 OpenForge `main`을 직접 수정하지 않습니다.

## Evidence Class

- Unit / Stub / Mock
- Integration
- 실제 Runtime / Cluster / Device / Filesystem
- Static Analysis / Lint
- Security / Policy
- Build / Package

낮은 Evidence Class가 높은 Runtime Property를 증명한다고 표현하지 않습니다.

## Relationship / Impact Model

주요 Relationship Type:

- `standardizes`
- `reference-implementation`
- `implements`
- `depends-on`
- `consumes`
- `provides`
- `shared-contract`
- `security-impact`
- `control-surface`

각 Edge에는 `high`, `medium`, `low` Impact를 기록합니다. 이는 품질 점수가 아니라 Change Review Priority입니다.

## Change Impact

```text
ADR-0013 / Agent Execution Security
        │
        ├─ HIGH → Narwhal
        ├─ HIGH → Narwhal Portal
        ├─ HIGH → KubeMetal
        ├─ MED  → Beluga
        └─ MED  → kube-ready-box
```

OpenForge는 Blast Radius를 식별하지만 Downstream Implementation Complete를 자동 판정하지 않습니다. 각 Repository가 구현/검증 후 다시 Status PR을 게시합니다.

## Dashboard Tooling

```bash
python3 templates/scripts/generate-portfolio.py
python3 templates/scripts/generate-portfolio.py --validate-only
python3 templates/scripts/generate-portfolio.py --check
python3 templates/scripts/generate-portfolio.py --validate-status <payload.json>
python3 templates/scripts/apply-portfolio-status.py <payload.json>
```

`templates/workflows/publish-openforge-status.yml`은 각 OSS가 자기 Status를 OpenForge PR로 게시하기 위한 재사용 가능한 Workflow Baseline입니다.
