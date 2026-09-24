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

Evidence는 Revision에 귀속됩니다. `templates/scripts/apply-portfolio-status.py`는 Payload의 `revision`이 Registry에 기록된 이전 `status.revision`과 다를 경우, 이전 Status에는 있었지만 새 Payload에 없는 `security`/`runtime` Evidence와 Capability를 `not-run`으로 명시적으로 낮춥니다 — 조용히 삭제(#106/#108)하거나 이전 Revision의 값을 그대로 이어받지(#107) 않습니다. 같은 Revision을 다시 게시하는 경우에는 이 강등 로직이 적용되지 않고 Payload 값이 그대로 반영됩니다. `.github/workflows/publish-project-status.yml`은 이 값을 신선하게 검증했을 때만 채우도록 선택적 `security_evidence`/`runtime_evidence` Input을 제공하며, 비워두면 Payload에서 생략되어 Revision이 바뀔 때 위 강등 로직의 대상이 됩니다.

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
python3 templates/scripts/apply-portfolio-status.py <payload.json> --report <report.md>
```

`--report <path>`는 Revision 변화, Dimension별 Evidence 변경, `not-run`으로 강등된 Evidence/Capability, 그리고 새 Revision에서 이전 값과 동일하게 반복된 Claim(리뷰어 재검증 필요, #107 신호)을 담은 Markdown 변경 보고서를 생성합니다. `.github/workflows/publish-project-status.yml`과 `templates/workflows/publish-openforge-status.yml` 모두 이 보고서를 생성해 `gh pr create --body-file`의 PR 본문에 포함시킵니다.

`templates/workflows/publish-openforge-status.yml`은 각 OSS가 자기 Status를 OpenForge PR로 게시하기 위한 재사용 가능한 Workflow Baseline입니다.

## Downstream Consumer

`portfolio/dashboard.json`은 이 Repository 외부에서 소비됩니다. `dasomel.github.io`는 `.github/workflows/sync-openforge-portfolio.yml`을 통해 이 파일을 주기적으로 fetch하고 `version`과 비어있지 않은 `projects[]`를 검증한 뒤 공개 `/oss` Portfolio Page에 렌더링합니다. 따라서 `version: openforge-dashboard/v1`과 `projects[]` 구조는 내부 표현이 아니라 이 Consumer와의 Compatibility Contract이며, `version`을 변경하려면 Consumer 측의 Migration을 함께 조율해야 합니다.

`portfolio/agent-audit.json`(Repository별 False-green Finding, Deterministic Control, Agent Skill Maturity 감사 결과)은 `dashboard.json`의 다섯 번째 입력이며, `render_dashboard_json`/`build_agent_audit_view`가 이를 최상위 `agent_audit` 키로 추가(Additive)합니다. `version`은 변경하지 않습니다 — Consumer는 Payload를 구조적으로 파싱하고 알 수 없는 최상위 키는 무시하므로, 키 추가는 하위 호환이지만 `version` 변경은 그렇지 않습니다. `agent_audit.repositories[]`는 체크인된 감사 파일의 순서(이미 우선순위로 정렬됨)를 그대로 따릅니다. `swallowed_failure_count`와 `local_agent_ci_gate` 두 필드는 아직 감사 매트릭스에 반영되는 중이라 현재 일부 또는 전체 Repository 레코드에 없을 수 있습니다 — Dashboard는 이 부재를 `0`/`false`가 아니라 `null`로 렌더링합니다. `0`은 "측정했고 없음"을 의미하지만 실제 의미는 "이 Revision에서 아직 측정하지 않음"이기 때문입니다. 대응하는 `agent_audit.summary` 필드(`swallowed_failure_findings`, `repositories_with_local_ci_gate`)는 실제로 해당 키를 가진 Repository만 합산하며, 아무 Repository도 갖고 있지 않으면 그 자체가 `null`입니다. `swallowed_failure_findings_measured_repositories`와 `local_ci_gate_measured_repositories`는 몇 개의 Repository가 합산에 기여했는지 보고하여, 부분 측정과 전체 측정을 구분할 수 있게 합니다. `portfolio/agent-audit.json`은 나머지 네 입력과 동일하게 필수 입력이며, 누락되거나 파싱 불가능하면 빈 `agent_audit` 블록을 만드는 대신 생성기가 크게 실패합니다.
