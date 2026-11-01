# OpenForge OSS Portfolio Dashboard

> Generated from `portfolio/*.json`. Do not hand-edit measured or relationship state in this document.

## Portfolio pulse

- Projects: **13**
- Engineering metrics: **35**
- OpenForge standard maturity: **96.9%**
- Portfolio adoption: **61.6%**
- Adoption target: **70.0%**
- ADRs: **15**
- Active projects: **11**

## Development board

| Project | Role | Development | OpenForge adoption | Domains | Verified revision | Evidence (ci · security · runtime) |
|---|---|---|---:|---|---|---|
| [OpenForge](https://github.com/dasomel/openforge) | `portfolio-governance` | **active** | — | standards, governance, security, compliance, portfolio | — | — |
| [Narwhal](https://github.com/dasomel/narwhal) | `reference-implementation` | **active** | 81.8% | kubernetes, platform-engineering, gitops, ai-agent, portal, operations | — | — |
| [KubeMetal](https://github.com/dasomel/kubemetal) | `adopter` | **active** | 95.8% | kubernetes, local-ai, mlops, agent, remediation | [`ed1d870`](https://github.com/dasomel/kubemetal/commit/ed1d8709823547c8c4ee1efb1843701dffc635f7) | — |
| [Beluga](https://github.com/dasomel/beluga) | `adopter` | **active** | — | kubernetes, data-platform, operations-agent, management, ui | [`2f78873`](https://github.com/dasomel/beluga/commit/2f7887376cc4e048e04d715b7d429c1991ec4d60) | ci: pass · security: pass · runtime: pass |
| [kube-ready-box](https://github.com/dasomel/kube-ready-box) | `enforcement-provider` | **active** | 87.1% | kubernetes, runtime, sandbox, security, evidence | — | — |
| [nfs-quota-agent](https://github.com/dasomel/nfs-quota-agent) | `service-provider` | **active** | 81.8% | kubernetes, storage, quota, controller | — | — |
| [ldapium](https://github.com/dasomel/ldapium) | `service-provider` | **active** | 89.7% | identity, ldap, admin | — | — |
| [ClusterDeck](https://github.com/dasomel/clusterdeck) | `operations-client` | **active** | 82.4% | kubernetes, desktop, operations, ui | — | — |
| [eGovFrame Launcher](https://github.com/dasomel/egovframe-launcher) | `developer-tool` | **active** | — | developer-experience, egovframe | — | — |
| [Siqoq](https://github.com/dasomel/siqoq) | `experiment` | **active** | — | physical-ai, edge-ai, simulation, ai-agent | — | — |
| [CKA Lab](https://github.com/dasomel/cka-lab) | `lab` | **maintenance** | — | kubernetes, education, lab | — | — |
| [dasomel.github.io](https://github.com/dasomel/dasomel.github.io) | `presentation` | **active** | — | documentation, community, portfolio | — | — |
| [Kairos](https://github.com/dasomel/kairos) | `independent-adopter` | **maintenance** | — | automation | — | — |

## Capability verification

| Project | Capability | Verification (unit · integration · runtime · security) |
|---|---|---|
| Beluga | `compliance-baseline` | unit pass · integration pass · runtime not-applicable · security pass |
| Beluga | `stream-iceberg` | unit pass · integration pass · runtime pass · security pass |
| Beluga | `policy-compiler-seam` | unit pass · integration pass · runtime pass · security pass |
| Beluga | `policy-compiler` | unit pass · integration pass · runtime pass · security pass |

## Adoption snapshot

| Project | Adoption |
|---|---:|
| KubeMetal | 95.8% |
| ldapium | 89.7% |
| kube-ready-box | 87.1% |
| ClusterDeck | 82.4% |
| Narwhal | 81.8% |
| nfs-quota-agent | 81.8% |

## Current milestones

| Milestone | Status | Progress |
|---|---|---|
| Portfolio Adoption M2 | **implementing** | 61.6% / 70.0% |
| Agent Execution Security Rollout | **implementing** | narwhal: design-adopted, kubemetal: design-adopted, beluga: design-adopted, kube-ready-box: design-adopted |
| OSS Portfolio Control Plane | **implementing** | openforge: implementing |

## Agent engineering audit

> Counts what the revision-bound audit can observe. A zero false-green count means no finding matched the detector's current rules at that revision; it is not proof that every validation path fails closed. A `—` means the control was not measured at that revision, which is different from measured and clean.

- Audited repositories: **9**
- Repositories with false-green findings: **7**
- False-green findings (total): **7**
- Canonical agent skills: **21**
- Evidence-backed mature skills: **11**
- Skill audit errors: **0**
- Swallowed-failure findings: **0** (measured in 9 of 9 repositories)
- Repositories with a local agent CI gate: **2** (measured in 9 of 9 repositories)

| Repository | Revision | False-green findings | Canonical skills | Evidence-backed verified+stable skills | Skill audit errors |
|---|---|---:|---:|---:|---:|
| dasomel/narwhal | `e2845fc` | 0 | 4 | 3 | 0 |
| dasomel/beluga | `5adf8fc` | 1 | 2 | 1 | 0 |
| dasomel/kubemetal | `a7acdba` | 1 | 1 | 1 | 0 |
| dasomel/clusterdeck | `2f25ed7` | 1 | 1 | 1 | 0 |
| dasomel/ldapium | `2da51c8` | 1 | 1 | 1 | 0 |
| dasomel/nfs-quota-agent | `bfc4ab0` | 1 | 1 | 1 | 0 |
| dasomel/egovframe-launcher | `26ad1fb` | 1 | 1 | 1 | 0 |
| dasomel/kube-ready-box | `1f047ff` | 0 | 9 | 1 | 0 |
| dasomel/siqoq | `fe1804b` | 1 | 1 | 1 | 0 |

## Security readiness

> Normalized from `portfolio/security-readiness/*.json`; upstream tools (OpenSSF Scorecard, ...) remain the source of the checks. Not a compliance or certification claim. See [Security Readiness Evidence](security-readiness-evidence.md).

| Repository | Overall | pass · fail · partial · not-run · n/a | Scorecard | Source evidence |
|---|---|---|---|---|
| dasomel/clusterdeck | **fail** | 2 · 3 · 1 · 0 · 0 | 3.6/10 (2026-10-15, `2f25ed7`) | [record](../portfolio/security-readiness/clusterdeck.json) · [scorecard](../portfolio/security-readiness/scorecard/clusterdeck.json) |
| dasomel/kubemetal | **fail** | 2 · 2 · 2 · 0 · 0 | 3.5/10 (2026-10-15, `a7acdba`) | [record](../portfolio/security-readiness/kubemetal.json) · [scorecard](../portfolio/security-readiness/scorecard/kubemetal.json) |
| dasomel/narwhal | **fail** | 2 · 3 · 1 · 0 · 0 | 4.1/10 (2026-10-15, `bb1e12f`) | [record](../portfolio/security-readiness/narwhal.json) · [scorecard](../portfolio/security-readiness/scorecard/narwhal.json) |

## External contributions

> Public discussions by external (non-owner, non-bot) GitHub accounts, from `portfolio/external-contributions.json`. State is a snapshot as of 2026-11-01T23:15:01Z; re-check the thread for the current state. GitHub handles only. See [External Contributions](external-contributions.md).

- Threads: **7** from **7** contributors
- By state: closed 2 · merged 1 · open 4
- By type: bug-report 1 · design 1 · design-review 2 · docs 1 · proposal 1 · support-offer 1

| Thread | Contributors | Type | State | Summary |
|---|---|---|---|---|
| [dasomel/kube-ready-box#79](https://github.com/dasomel/kube-ready-box/issues/79) | [Evantage-WS](https://github.com/Evantage-WS) | `bug-report` | **closed** | 26.04 box dracut loop on VirtualBox, macOS 27, M4 — outcome: Reproduced and fixed: VirtualBox ARM64 boxes ship on an NVMe controller (kube-ready-box#80); reporter confirmed the login prompt |
| [dasomel/kubemetal#84](https://github.com/dasomel/kubemetal/issues/84) | [Lulzx](https://github.com/Lulzx) | `support-offer` | **open** | CuMetal maintainer offered support when issues are reported |
| [dasomel/narwhal#4](https://github.com/dasomel/narwhal/pull/4) | [iamroseyoung](https://github.com/iamroseyoung) | `docs` | **merged** | Staged verification guide (docs/evaluation) with stage-0 static validation |
| [dasomel/narwhal#73](https://github.com/dasomel/narwhal/issues/73) | [23A91A6183](https://github.com/23A91A6183), [Aliipou](https://github.com/Aliipou) | `proposal` | **open** | Agent identity / MCP tool authorization: PDP-PEP separation, spend-once grants, signed evidence log |
| [dasomel/narwhal#155](https://github.com/dasomel/narwhal/issues/155) | [ozereray](https://github.com/ozereray) | `design-review` | **open** | Tool authorization, approval and execution evidence reviewed from the contributor's own project perspective |
| [dasomel/narwhal#372](https://github.com/dasomel/narwhal/issues/372) | [ozereray](https://github.com/ozereray) | `design-review` | **open** | Roadmap issue for agent/MCP tool authorization, approval and execution evidence, reviewed from the contributor's own project perspective |
| [dasomel/openforge#128](https://github.com/dasomel/openforge/issues/128) | [saniya-malik](https://github.com/saniya-malik) | `design` | **closed** | Figma dashboard/infographic reference design for the portfolio control plane — outcome: Reflected in the live portfolio dashboard |

## Status publication workflow

```text
Project change merged
        ↓
project CI + required verification
        ↓
openforge-project-status/v1 payload
        ↓
PR to OpenForge portfolio registry
        ↓
portfolio validation + impact review
        ↓
merge = official portfolio state change
        ↓
dashboard / graph / infographic regeneration
```

See [Portfolio Governance](portfolio-governance.md), [Architecture Graph](portfolio-architecture.md), and [Impact Graph](portfolio-impact.md).
