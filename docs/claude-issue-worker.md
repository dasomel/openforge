# Claude issue worker: WIF pilot change package

Status: Draft; Class D (CI write authority and external model authentication). Review before enabling. This pilot is limited to OpenForge; downstream standards/templates are unchanged.

Goal: process one explicitly queued GitHub issue per maintainer dispatch, propose a minimal tested fix as a draft PR, and preserve human merge authority.

## Setup

Register GitHub issuer https://token.actions.githubusercontent.com in Claude Console Workload identity. Set audience https://api.anthropic.com and subject repo:dasomel/openforge:ref:refs/heads/main. Bind the rule/service account to the intended workspace. Set repository Actions variables ANTHROPIC_FEDERATION_RULE_ID and ANTHROPIC_ORGANIZATION_ID, optionally ANTHROPIC_SERVICE_ACCOUNT_ID and ANTHROPIC_WORKSPACE_ID. These identifiers are not secrets. Do not add static API or OAuth credentials to this workflow.

After review and merge, create ai-ready label, apply it to a narrow issue, and manually dispatch Claude issue worker (WIF). It selects the oldest issue among the first 100 candidates. No eligible issue means no model call. Existing worker PRs prevent duplicate proposals; remove the label before moving to another issue. A failed run may leave a branch or label: inspect before retrying.

## Impact and boundaries

- Source/runtime/build/release: application code and existing commands unchanged; new Ubuntu Actions job runs the SHA-pinned official Claude Action (which installs its own Bun/Claude runtime).
- CI/security: read-only selection, then repository-scoped write token and id-token permission in worker. Uses GitHub runner gh CLI; inspect runtime version during pilot. No production credentials, shared deploy, workflow/auth changes, auto-merge or auto-close are requested of the agent.
- Documentation: this English/Korean package records setup, acceptance, risks and rollback.
- Offline/downstream: optional online workflow only; no default scanner, air-gap asset or downstream template changes.

## Acceptance and evidence

- [x] actionlint passes on workflow syntax and expressions.
- [x] Repository Python tests: 289 tests, OK (7.961s); agent-skills strict and instruction-debt audits: 0 findings, exit 0.
- [ ] Design package reviewed; WIF identifiers registered and subject restrictions confirmed.
- [ ] Dispatch without ai-ready ends with no model execution.
- [ ] One narrow queued issue authenticates, runs actual tests and creates at most one draft PR.
- [ ] Record actual run URL, token cost and CI status; missing evidence is unknown.

## Risks and rollback

20 turns / $2 CLI budget / 25 minutes bound a pilot, but are not a hard account spending cap. Set Console workspace spend limit and disable auto-reload. Max promotional-credit eligibility for this Action remains unverified. Issue content is untrusted; prompt restrictions are not an enforced sandbox. The worker has repository write authority. GITHUB_TOKEN-created PRs may not trigger ordinary PR CI: manually dispatch relevant checks or later introduce a restricted GitHub App token. Do not merge without actual evidence. PR permission must be enabled in repository Actions settings. Label cleanup depends on model completion. Remove/disable the workflow and revoke the federation rule to stop the pilot; inspect any proposed branches separately.
