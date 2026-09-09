# OpenForge OSS Portfolio Dashboard

> Generated from `portfolio/*.json`. Do not hand-edit measured or relationship state in this document.

## Portfolio pulse

- Projects: **15**
- Engineering metrics: **35**
- OpenForge standard maturity: **96.9%**
- Portfolio adoption: **61.6%**
- Adoption target: **70.0%**
- ADRs: **14**
- Active projects: **13**

## Development board

| Project | Role | Development | OpenForge adoption | Domains | Verified revision | Evidence (ci · security · runtime) |
|---|---|---|---:|---|---|---|
| [OpenForge](https://github.com/dasomel/openforge) | `portfolio-governance` | **active** | — | standards, governance, security, compliance, portfolio | — | — |
| [Narwhal](https://github.com/dasomel/narwhal) | `reference-implementation` | **active** | 81.8% | kubernetes, platform-engineering, gitops, ai-agent | — | — |
| [Narwhal Portal](https://github.com/dasomel/narwhal-portal) | `control-surface` | **active** | 83.8% | portal, kubernetes, ai-agent, operations | — | — |
| [KubeMetal](https://github.com/dasomel/kubemetal) | `adopter` | **active** | 95.8% | kubernetes, local-ai, mlops, agent, remediation | [`ed1d870`](https://github.com/dasomel/kubemetal/commit/ed1d8709823547c8c4ee1efb1843701dffc635f7) | — |
| [Beluga](https://github.com/dasomel/beluga) | `adopter` | **active** | — | kubernetes, data-platform, operations-agent | [`8dedb46`](https://github.com/dasomel/beluga/commit/8dedb4614da34752f07c15736ea06d3c3cbe9c4b) | ci: pass · security: pass · runtime: partial |
| [Beluga Manager](https://github.com/dasomel/beluga-manager) | `control-surface` | **active** | — | data-platform, management, ui | [`670a076`](https://github.com/dasomel/beluga-manager/commit/670a076a86c84929ddb5eb83a057efea4ba26b27) | ci: pass · security: pass · runtime: pass |
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
| Beluga | `stream-iceberg` | unit pass · integration pass · runtime partial · security pass |
| Beluga Manager | `policy-compiler` | unit pass · integration pass · runtime pass · security pass |

## Adoption snapshot

| Project | Adoption |
|---|---:|
| KubeMetal | 95.8% |
| ldapium | 89.7% |
| kube-ready-box | 87.1% |
| Narwhal Portal | 83.8% |
| ClusterDeck | 82.4% |
| Narwhal | 81.8% |
| nfs-quota-agent | 81.8% |

## Current milestones

| Milestone | Status | Progress |
|---|---|---|
| Portfolio Adoption M2 | **implementing** | 61.6% / 70.0% |
| Agent Execution Security Rollout | **implementing** | narwhal-portal: design-adopted, kubemetal: design-adopted, beluga: design-adopted, kube-ready-box: design-adopted |
| OSS Portfolio Control Plane | **implementing** | openforge: implementing |

## Agent engineering audit

> Counts what the revision-bound audit can observe. A zero false-green count means no finding matched the detector's current rules at that revision; it is not proof that every validation path fails closed. A `—` means the control was not measured at that revision, which is different from measured and clean.

- Audited repositories: **11**
- Repositories with false-green findings: **0**
- False-green findings (total): **0**
- Canonical agent skills: **16**
- Evidence-backed mature skills: **0**
- Skill audit errors: **0**
- Swallowed-failure findings: **—** (measured in 0 of 11 repositories)
- Repositories with a local agent CI gate: **—** (measured in 0 of 11 repositories)

| Repository | Revision | False-green findings | Canonical skills | Verified+stable skills | Skill audit errors |
|---|---|---:|---:|---:|---:|
| dasomel/narwhal | `1b1e5c0` | 0 | 4 | 0 | 0 |
| dasomel/narwhal-portal | `0730430` | 0 | 3 | 0 | 0 |
| dasomel/beluga | `6c5bdd1` | 0 | 1 | 0 | 0 |
| dasomel/beluga-manager | `0e7a495` | 0 | 1 | 0 | 0 |
| dasomel/kubemetal | `829221e` | 0 | 1 | 0 | 0 |
| dasomel/clusterdeck | `3b7c283` | 0 | 1 | 0 | 0 |
| dasomel/ldapium | `438e244` | 0 | 1 | 0 | 0 |
| dasomel/nfs-quota-agent | `60aa69a` | 0 | 1 | 0 | 0 |
| dasomel/egovframe-launcher | `73cf922` | 0 | 1 | 0 | 0 |
| dasomel/kube-ready-box | `a0c8d7e` | 0 | 1 | 0 | 0 |
| dasomel/siqoq | `b71c68f` | 0 | 1 | 0 | 0 |

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
