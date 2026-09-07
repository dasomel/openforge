# OpenForge OSS Portfolio Dashboard

> Generated from `portfolio/*.json`. Do not hand-edit measured or relationship state in this document.

## Portfolio pulse

- Projects: **14**
- Engineering metrics: **35**
- OpenForge standard maturity: **96.9%**
- Portfolio adoption: **61.6%**
- Adoption target: **70.0%**
- ADRs: **13**
- Active projects: **12**

## Development board

| Project | Role | Development | OpenForge adoption | Domains | Verified revision | Evidence (ci · security · runtime) |
|---|---|---|---:|---|---|---|
| [OpenForge](https://github.com/dasomel/openforge) | `portfolio-governance` | **active** | — | standards, governance, security, compliance, portfolio | — | — |
| [Narwhal](https://github.com/dasomel/narwhal) | `reference-implementation` | **active** | 81.8% | kubernetes, platform-engineering, gitops, ai-agent | — | — |
| [Narwhal Portal](https://github.com/dasomel/narwhal-portal) | `control-surface` | **active** | 83.8% | portal, kubernetes, ai-agent, operations | — | — |
| [KubeMetal](https://github.com/dasomel/kubemetal) | `adopter` | **active** | 82.4% | kubernetes, local-ai, mlops, agent, remediation | — | — |
| [Beluga](https://github.com/dasomel/beluga) | `adopter` | **active** | — | kubernetes, data-platform, operations-agent | [`8dedb46`](https://github.com/dasomel/beluga/commit/8dedb4614da34752f07c15736ea06d3c3cbe9c4b) | ci: pass · security: pass · runtime: partial |
| [Beluga Manager](https://github.com/dasomel/beluga-manager) | `control-surface` | **active** | — | data-platform, management, ui | [`670a076`](https://github.com/dasomel/beluga-manager/commit/670a076a86c84929ddb5eb83a057efea4ba26b27) | ci: pass · security: pass · runtime: pass |
| [kube-ready-box](https://github.com/dasomel/kube-ready-box) | `enforcement-provider` | **active** | 87.1% | kubernetes, runtime, sandbox, security, evidence | — | — |
| [nfs-quota-agent](https://github.com/dasomel/nfs-quota-agent) | `service-provider` | **active** | 81.8% | kubernetes, storage, quota, controller | — | — |
| [ldapium](https://github.com/dasomel/ldapium) | `service-provider` | **active** | 89.7% | identity, ldap, admin | — | — |
| [ClusterDeck](https://github.com/dasomel/clusterdeck) | `operations-client` | **active** | 82.4% | kubernetes, desktop, operations, ui | — | — |
| [eGovFrame Launcher](https://github.com/dasomel/egovframe-launcher) | `developer-tool` | **active** | — | developer-experience, egovframe | — | — |
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
| ldapium | 89.7% |
| kube-ready-box | 87.1% |
| Narwhal Portal | 83.8% |
| ClusterDeck | 82.4% |
| KubeMetal | 82.4% |
| Narwhal | 81.8% |
| nfs-quota-agent | 81.8% |

## Current milestones

| Milestone | Status | Progress |
|---|---|---|
| Portfolio Adoption M2 | **implementing** | 61.6% / 70.0% |
| Agent Execution Security Rollout | **implementing** | narwhal-portal: design-adopted, kubemetal: design-adopted, beluga: design-adopted, kube-ready-box: design-adopted |
| OSS Portfolio Control Plane | **implementing** | openforge: implementing |

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
