# OSS Portfolio Governance

[한국어](portfolio-governance-ko.md)

OpenForge manages the engineering state of the OSS portfolio as a reviewable, evidence-backed control plane. Individual repositories remain the source of truth for their own implementation; OpenForge records the **official cross-project portfolio state** after a status update is reviewed and merged.

## Source of truth

```text
portfolio/projects.json       project registry and curated development state
portfolio/relationships.json cross-project relationships and impact edges
portfolio/milestones.json     portfolio milestones and allowed lifecycle states
portfolio/status.schema.json  downstream status publication contract
```

Generated dashboards and diagrams are presentation views. They must not become independent sources of truth.

## State ownership

```text
Individual OSS repository
  owns implementation + tests + runtime/security evidence
             │
             │ verified completion/change
             ▼
openforge-project-status/v1
             │
             │ pull request
             ▼
OpenForge
  validates project identity, state transition,
  evidence references and cross-project impact
             │
             │ merge
             ▼
Official portfolio state
             │
             ├─ dashboard
             ├─ dependency/impact graph
             ├─ infographic/site data
             └─ downstream impact review
```

A code merge in a downstream repository is **not automatically equivalent to feature completion**. The repository should publish status only after the evidence class required for the capability has passed.

## Lifecycle

Allowed development states are:

`planned → designing → implementing → verifying → implemented → adopted`

Additional states:

- `maintenance` — feature development is not the current primary mode, but supported maintenance continues.
- `blocked` — progress is stopped by an explicit verified blocker.
- `deprecated` — capability/project remains visible for history but is no longer recommended.

`implemented` means the repository has implemented and verified the declared capability at its own boundary. `adopted` means a shared OpenForge standard or capability is integrated sufficiently for portfolio-level adoption claims.

## Status publication contract

A downstream repository publishes an `openforge-project-status/v1` payload after its required checks pass.

Minimum example:

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

The schema permits repositories to report the evidence they actually have. It must not invent a stronger evidence class merely to obtain a green portfolio status.

## Status PR policy

Recommended title:

```text
chore(portfolio): update <project> development status
```

The PR should contain:

1. project and revision;
2. lifecycle transition;
3. changed capabilities/standards;
4. issue/PR/commit evidence;
5. CI/security/runtime verification class;
6. relationship changes, if any;
7. expected cross-project impact.

The status PR updates the canonical registry and regenerates the dashboard outputs. **Merging the PR is the official portfolio state transition.**

## Automation model

Downstream repositories may automate status publication after a release, milestone, or explicitly named verification workflow succeeds.

Automation should use a dedicated GitHub App or narrowly scoped fine-grained credential that can create a branch/PR in `dasomel/openforge`. Do not distribute broad owner credentials or reuse unrestricted maintainer tokens.

The automation boundary is deliberately two-step:

```text
repository CI verifies capability
        ↓
status publisher proposes OpenForge PR
        ↓
OpenForge CI validates registry + generated views
        ↓
maintainer/allowed automation merges
```

A downstream workflow should not silently rewrite `main` in OpenForge.

## Evidence classes

Portfolio state distinguishes the same evidence classes used by OpenForge engineering standards:

- unit/stub/mocked
- integration
- real runtime/cluster/device/filesystem
- static analysis/lint
- security/policy
- build/package

A lower-level evidence class must not be presented as proof of a higher-level runtime property.

## Relationship and impact model

Relationships have typed semantics such as:

- `standardizes`
- `reference-implementation`
- `implements`
- `depends-on`
- `consumes`
- `provides`
- `shared-contract`
- `security-impact`
- `control-surface`

Each edge also has `high`, `medium`, or `low` coordination impact. Impact indicates review priority when the source changes; it is not a quality score.

## Change impact

A durable OpenForge standard change should be checked against `portfolio/relationships.json` before merge. High-impact targets are reviewed first, then medium and low relationships as relevant.

Example:

```text
ADR-0013 / Agent Execution Security
        │
        ├─ HIGH → Narwhal
        ├─ HIGH → Narwhal Portal
        ├─ HIGH → KubeMetal
        ├─ MED  → Beluga
        └─ MED  → kube-ready-box
```

OpenForge may identify the blast radius, but it does not automatically mark downstream implementation complete. Each affected repository must perform its own implementation/verification and publish the result back.

## Dashboard generation

```bash
python3 templates/scripts/generate-portfolio.py
python3 templates/scripts/generate-portfolio.py --validate-only
python3 templates/scripts/generate-portfolio.py --check
```

`--check` is intended for CI once generated outputs are committed. `--validate-status <file>` validates the core repository/project/state/evidence identity of a downstream payload; the JSON Schema remains the full machine-readable contract.

## Downstream consumers

`portfolio/dashboard.json` is fetched outside this repository. `dasomel.github.io` pulls it on a schedule via `.github/workflows/sync-openforge-portfolio.yml`, validates `version` and a non-empty `projects[]`, and renders it on the public `/oss` portfolio page. `version: openforge-dashboard/v1` and the `projects[]` shape are therefore a compatibility contract with that consumer, not an internal representation detail; changing `version` requires a coordinated migration on the consumer side.
