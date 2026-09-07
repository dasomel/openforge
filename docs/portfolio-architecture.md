# OpenForge OSS Portfolio Architecture

> Generated from `portfolio/projects.json` and `portfolio/relationships.json`.

## Ecosystem graph

```mermaid
flowchart TB
  subgraph Governance["Standards & Governance"]
    openforge["OpenForge\nportfolio-governance"]
  end
  subgraph Platform["Platform Engineering"]
    narwhal["Narwhal\nreference-implementation"]
    narwhal_portal["Narwhal Portal\ncontrol-surface"]
    clusterdeck["ClusterDeck\noperations-client"]
  end
  subgraph AIData["AI / Data Platforms"]
    kubemetal["KubeMetal\nadopter"]
    beluga["Beluga\nadopter"]
    beluga_manager["Beluga Manager\ncontrol-surface"]
  end
  subgraph Foundation["Runtime / Shared Services"]
    kube_ready_box["kube-ready-box\nenforcement-provider"]
    nfs_quota_agent["nfs-quota-agent\nservice-provider"]
    ldapium["ldapium\nservice-provider"]
  end
  subgraph DeveloperCommunity["Developer / Community"]
    egovframe_launcher["eGovFrame Launcher\ndeveloper-tool"]
    cka_lab["CKA Lab\nlab"]
    dasomel_github_io["dasomel.github.io\npresentation"]
    kairos["Kairos\nindependent-adopter"]
  end
  openforge -->|standardizes| narwhal
  openforge -->|standardizes| narwhal_portal
  openforge -->|standardizes| kubemetal
  openforge -->|standardizes| beluga
  openforge -->|standardizes| kube_ready_box
  openforge -->|standardizes| nfs_quota_agent
  openforge -->|standardizes| ldapium
  openforge -->|standardizes| clusterdeck
  openforge -->|standardizes| beluga_manager
  openforge -->|standardizes| egovframe_launcher
  openforge -->|standardizes| dasomel_github_io
  narwhal -->|reference-implementation| openforge
  narwhal -->|provides| narwhal_portal
  narwhal_portal -->|control-surface| narwhal
  kubemetal -->|consumes| kube_ready_box
  narwhal -->|consumes| kube_ready_box
  kube_ready_box -->|provides| narwhal
  kube_ready_box -->|provides| kubemetal
  beluga -->|provides| beluga_manager
  beluga_manager -->|control-surface| beluga
  narwhal -->|consumes| nfs_quota_agent
  nfs_quota_agent -->|provides| narwhal
  narwhal -->|consumes| ldapium
  ldapium -->|provides| narwhal
  narwhal -->|shared-contract| kubemetal
  narwhal -->|shared-contract| beluga
  narwhal_portal -->|shared-contract| kubemetal
  clusterdeck -->|consumes| narwhal
  dasomel_github_io -->|consumes| openforge
```

## Relationship semantics

| Type | Meaning |
|---|---|
| `standardizes` | OpenForge rule/contract is expected to influence the target |
| `reference-implementation` | project experience feeds a reusable OpenForge rule |
| `provides` | source exposes a capability consumed by target |
| `consumes` | source depends on or integrates a target capability |
| `control-surface` | source is an operational/user control surface for target |
| `shared-contract` | projects share a portable contract without hard runtime dependency |
| `security-impact` | changes may alter trust or authorization boundaries |

Relationship edges express engineering influence and integration intent, not necessarily build-time package dependencies.
