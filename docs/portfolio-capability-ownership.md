# Portfolio Capability Ownership

OpenForge treats the Dasomel OSS portfolio as a set of independently releasable projects with explicit capability ownership. The canonical machine-readable registry is `portfolio/capability-ownership.json`.

## Rules

1. A shared capability has one implementation owner.
2. A project that needs an owned capability should create an integration, adapter, consumer-contract, or control-surface issue instead of reimplementing the capability.
3. Portal/manager repositories own presentation and control surfaces, not the underlying platform capability.
4. Cross-project integration must preserve independent operation where intended and must not create circular hard dependencies.
5. Evidence is owned by the project that implements the capability; consumers may reference that evidence but must separately verify their integration boundary.
6. New portfolio issues must first check the ownership registry and the owning project's canonical taxonomy.

## Current boundaries

| Capability | Owner | Primary consumers / surfaces |
| --- | --- | --- |
| Portfolio engineering governance | OpenForge | all portfolio projects |
| Kubernetes platform control plane | Narwhal | Narwhal Portal, Beluga, KubeMetal |
| Data platform / lakehouse | Beluga | Beluga Manager |
| Local / edge AI runtime | KubeMetal | Beluga, Siqoq |
| Node runtime foundation | kube-ready-box | Narwhal, Beluga |
| Directory identity data plane | LDAPium | Narwhal, Beluga |
| Filesystem quota enforcement | nfs-quota-agent | Narwhal, Beluga |
| Local Kubernetes operations client | ClusterDeck | standalone operator UX |
| eGovFrame developer tooling | eGovFrame Launcher | standalone developer workflow |
| Physical / edge AI experimentation | Siqoq | may consume KubeMetal/Narwhal contracts |

## Issue triage decision

Before opening a new capability issue:

```text
Does another portfolio project own the capability?
  yes -> integration / adapter / consumer-contract issue
  no  -> does this repository's taxonomy already contain it?
          yes -> extend the canonical issue
          no  -> create a new implementation issue and update ownership if portfolio-wide
```

Research, acceptance evidence, operations exercises, and control-surface work should not become separate top-level implementations when they are merely lifecycle stages of an existing canonical capability.

## Beluga-specific application

Beluga issue `#97` remains the repository taxonomy and `#99` the cross-OSS integration contract. Beluga should own data-platform semantics and consume portfolio capabilities such as cluster lifecycle, node readiness, LDAP lifecycle, local AI runtime, and filesystem quota enforcement through explicit contracts rather than duplicating their implementation scope.
