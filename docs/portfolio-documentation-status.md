# Portfolio Documentation Status

> Review date: **2026-08-28**
>
> Scope: the 10 projects currently presented as the CnE OSS portfolio. This is a documentation/adoption review, not a product maturity score. Repository evidence and the existing OpenForge portfolio audit were used as the baseline; items marked as gaps mean the evidence is missing, incomplete, inconsistent, or not yet optimized for an external first-time user.

## Review model

Documentation is reviewed against the external adoption journey:

```text
Discover -> Understand -> Install -> Verify -> Operate -> Troubleshoot -> Contribute
```

The target is not to create more files. The target is to make existing documentation lead a new user to a reproducible first success and clearly distinguish verified behavior from plans.

## Current portfolio status

| Project | Current documentation | Adoption readiness | Highest-value documentation update |
|---|---|---|---|
| **Narwhal** | Strong README, architecture/operations material, VERSIONS, incident/lesson knowledge, verification scripts | **Strong foundation / onboarding still heavy** | Add a clearly bounded first-success path and distinguish cluster creation from full IDP success; avoid static activity counters becoming stale |
| **Narwhal Portal** | README covers role, features, screenshots, local/in-cluster development and security bootstrap | **Good developer docs / user journey partial** | Replace placeholder screenshot guidance with implemented UI evidence; add architecture/navigation entry point and explicit supported/implemented status for planned tests |
| **NFS Quota Agent** | Very detailed README, bilingual policy/security/community docs, DESIGN, CHANGELOG, Helm values and operational options | **Best external-adoption candidate** | Move a minimal Helm install + create PVC + exceed quota + verify result flow near the top; keep advanced configuration below it |
| **ldapium** | Evidence-oriented README, Helm verification, security posture, known prototype status, chart documentation | **Honest prototype docs** | Verify published artifact instructions against actual release state and update the prototype/registry note when release evidence changes; add architecture navigation |
| **Kube-Ready-Box** | Detailed README, Ubuntu/filesystem/provider matrix and post-install guidance | **Strong reference docs / broad surface** | Add one canonical “box -> verify OS readiness” first-success check and architecture navigation; reduce duplicated version facts where Vagrant/release metadata can be authoritative |
| **ClusterDeck** | Concise bilingual README, core flow, scope, architecture/MVP links, security warning | **Clear concept / early product onboarding** | Add current implementation status, supported macOS/build targets, packaged-app path when available, and an end-to-end Profile -> SSH -> kubeconfig -> API verification example |
| **Beluga** | Detailed Korean README with architecture, requirements, quick start, verification and mistakes log | **Strong lab narrative / localization gap** | Provide canonical English entry path and make the two E2E success scenarios the primary first-success evidence; keep resource requirements prominent |
| **Beluga Manager** | Clear product/domain architecture README and i18n intent | **Architecture-heavy / implementation evidence light** | Mark implemented vs planned domains/endpoints explicitly and add a runnable read-first vertical-slice Quick Start with verification |
| **KubeMetal** | Rich README, design/architecture/research/user/E2E docs, measured external-cluster notes | **Strong engineering evidence / high complexity** | Add a short “local first success” path before advanced D26/D30 material; consolidate architecture entry points and improve Korean coverage for user-facing docs |
| **OpenForge** | Extensive standards, ADRs, templates, audit/scorecard and design-system documentation | **Strong standards corpus / adoption path can be simpler** | Lead with “apply one standard/template to one repository” Quick Start; treat portfolio scores as standards-compliance evidence, not product maturity |

## 2026-08 adoption-guide rollout

The review has moved from analysis into repository-level implementation. Draft adoption-guide PRs now encode a project-specific first-success contract without rewriting each project into a generic template:

| Project | Draft PR | First verified success focus |
|---|---:|---|
| Narwhal | #174 | cluster readiness + GitOps/identity/platform verification |
| Narwhal Portal | #77 | authenticated Day-2 workspace with backend evidence |
| NFS Quota Agent | #87 | real filesystem quota enforcement |
| ldapium | #107 | LDAP bind/read/write/deny with TLS/ACL/audit behavior |
| kube-ready-box | #37 | reproducible guest OS/storage/Kubernetes readiness |
| ClusterDeck | #11 | Profile -> SSH -> kubeconfig -> Kubernetes API |
| Beluga | #112 | deterministic E2E data path |
| Beluga Manager | #48 | one implemented/integrated vertical slice |
| KubeMetal | #53 | local Kubernetes control plane + native MLX/Metal compute |
| OpenForge | #35 | apply one standard and verify it before expanding |

The CnE blog has a matching bilingual portfolio article in `dasomel.github.io` PR #310 so public narrative and repository documentation evolve from the same evidence model.

These PRs are intentionally Draft. They establish the adoption contract first; README restructuring, screenshots, localized parity and executable copy/paste validation can then be reviewed project by project without mixing product changes into the documentation baseline.

## Cross-portfolio findings

### 1. File presence is no longer the main problem

The stronger repositories already have README, security, contribution, release/change and architecture-oriented material. The next gap is **information architecture for a first-time external user**.

The common README order should converge toward:

```text
What / Why
Current status and scope
Prerequisites
Quick Start
Verify first success
Known limitations / compatibility
Architecture
Operations / troubleshooting
Documentation map
Contributing / support
License
```

Detailed design, research, migration and internal engineering material should remain available, but should not block the shortest supported path.

### 2. Verification should describe a product outcome

Examples:

- Narwhal: not only `kubectl get nodes`; verify the intended IDP integration state.
- NFS Quota Agent: prove a PVC limit is enforced at the filesystem layer.
- ClusterDeck: prove Profile -> SSH -> kubeconfig -> Kubernetes API connectivity.
- Beluga: prove the documented E2E data path, not only healthy pods.
- KubeMetal: prove the local control/compute split with one model/MLflow flow.
- ldapium: `helm test` is already a good example because it verifies LDAP behavior, not only pod readiness.

### 3. Plans and evidence need clearer separation

Early projects such as Beluga Manager and ClusterDeck should explicitly label planned features. Mature engineering notes should use dates or releases for measured claims when appropriate. Placeholder screenshots and intended publication instructions must not read like verified release evidence.

### 4. Localization is inconsistent

The portfolio currently contains `README-ko.md`, `README_ko.md`, `README.ko.md`, Korean-only README content and incomplete docs translations. OpenForge keeps `-ko.md` as the canonical convention, but migration should happen when documents are naturally touched rather than through a risky mass rename.

Priority is **semantic parity for the adoption path**, not translating every internal engineering note.

### 5. Adoption documentation should be evidence-based

Do not claim external adoption from stars, forks or raw contributor counts. External references should move through Candidate -> Reported -> Verified review before being presented as adoption evidence.

## Update priority

### P0 — external first success

1. **NFS Quota Agent** — make the quota-enforcement success scenario the shortest path.
2. **Narwhal** — define a bounded Quick Lab / first-success contract for the integrated platform.
3. **ClusterDeck** — document one complete workstation access workflow.
4. **Beluga Manager** — separate implemented MVP from target architecture and add runnable verification.

### P1 — simplify strong but dense documentation

5. **KubeMetal** — local-first onboarding before advanced external-cluster paths.
6. **Kube-Ready-Box** — explicit readiness verification and architecture entry point.
7. **ldapium** — release/publication evidence refresh and architecture navigation.
8. **Narwhal Portal** — implemented UI evidence and user-oriented navigation.

### P2 — portfolio consistency

9. **Beluga** — English adoption path and E2E-first presentation.
10. **OpenForge** — simpler “apply OpenForge” first-success path and score terminology cleanup.

## Maintenance rule

For future releases, documentation review should be part of the release/change checklist. A documentation update is required when installation, verification, compatibility, security/identity, release artifact, architecture boundary or a user-facing workflow changes.

The portfolio should optimize for **Time to First Verified Success**, not document count.