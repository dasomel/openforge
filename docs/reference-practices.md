# OSS Reference Practices Audit

This document records practices observed in active `dasomel` OSS repositories and converts reusable patterns into OpenForge standards.

## English

OpenForge was reviewed against active repositories including Narwhal, Narwhal Portal, nfs-quota-agent, kube-ready-box, KubeMetal, ldapium, and Beluga.

### Reusable practices observed

| Practice | Reference repositories | OpenForge treatment |
|---|---|---|
| English/Korean documentation pairs | Narwhal, Narwhal Portal, nfs-quota-agent, KubeMetal, ldapium | Standardize on `<name>.md` + `<name>-ko.md` for owned user-facing docs |
| Version authority | Narwhal `VERSIONS.md` | Prefer one authoritative version/compatibility inventory |
| Changelog pair | Narwhal, nfs-quota-agent, KubeMetal, ldapium | `CHANGELOG.md` + `CHANGELOG-ko.md` |
| ADR / design records | Narwhal Portal, KubeMetal | Important architectural decisions become versioned ADRs |
| Incident / lessons log | Narwhal, KubeMetal | Operational failures become reusable engineering knowledge |
| AI repository instructions | Narwhal, Narwhal Portal, KubeMetal, nfs-quota-agent | Version `AGENTS.md`, `CLAUDE.md`, or equivalent when AI-assisted development is used |
| Release guide | ldapium, KubeMetal | Release procedures become explicit and reproducible |
| Security policy | ldapium and other platform repositories | `SECURITY.md` plus private reporting guidance |
| Legal / third-party attribution | ldapium, kube-ready-box | License, NOTICE and third-party obligations are documented |
| Environment example | ldapium | `.env.example` or equivalent safe configuration examples |
| Make-based developer UX | KubeMetal, ldapium, Narwhal | Prefer a small, discoverable command surface where appropriate |
| Version checks | ldapium | Automate version consistency checks when multiple manifests/configs carry versions |
| Supply-chain checks | ldapium scorecard workflow, image/release workflows | Add provenance, SBOM, vulnerability and workflow-hardening checks where applicable |
| **Dependency freshness / cooling** | Portfolio security review | **`docs/supply-chain.md`: latest-compatible is insufficient; 14-day default cooling, emergency exception and progressive adoption** |
| **Change impact / workflow contract** | Recent Bun CI incident and cross-workflow review | **`docs/change-management.md`: Class C/D changes require workflow-wide impact analysis and runtime/toolchain verification** |
| **Build-time trust boundary** | Rust supply-chain incident analysis | **Treat install hooks, build scripts, proc-macros, plugins and code generators as executable supply-chain inputs** |
| Deployment-specific docs | Narwhal | Separate common guidance from target-specific operational documents |
| Helm chart docs | ldapium | Maintain chart README and values documentation for reusable charts |
| Image/packaging docs | ldapium, KubeMetal | Document build, packaging, registry and architecture expectations |
| CI regression evidence | Narwhal | Preserve reproducible regression tests and link important failures to lessons |

## Change-management rule

A dependency/runtime/toolchain migration changes the build contract even when the application interface remains compatible. Before merge, search every workflow that can invoke the affected build, test, package or release command.

The historical Bun migration failure is the reference example: a build command changed to invoke Bun, but an independent Pages deployment workflow did not install Bun. The durable OpenForge rule is therefore **workflow-wide impact analysis**, not a one-off fix.

## Supply-chain rule

OpenForge is the reference standard for the portfolio. Repository-specific supply-chain policies should reference `docs/supply-chain.md` rather than inventing incompatible freshness, pinning, provenance or rollback rules.

## Documentation naming exception

The `-ko.md` rule applies to **project-owned, user-facing documentation**. It does not require rewriting third-party or vendored documentation, generated documentation, or upstream artifacts whose filename is part of the upstream distribution contract.

Examples from Narwhal include vendored chart documentation and existing upstream README conventions. Preserve those artifacts unless there is a specific reason to change the filename.

## Recommended evidence loop

```text
Failure / Change
      ↓
Issue / ADR / Incident record
      ↓
Change impact analysis
      ↓
Implementation
      ↓
Regression test or CI check
      ↓
Security / supply-chain evidence
      ↓
Release note / Changelog
      ↓
Reusable documentation
```

This loop is particularly valuable for infrastructure and platform projects where integration defects can recur after upgrades.

## Korean

OpenForge는 Narwhal, Narwhal Portal, nfs-quota-agent, kube-ready-box, KubeMetal, ldapium, Beluga 등 실제 개발 중인 저장소를 기준으로 공통 패턴을 검토했습니다.

이번 표준화에서 공급망과 변경 영향 분석도 공통 engineering practice로 승격했습니다.

- `docs/supply-chain.md`: dependency freshness/cooling, immutable input, build-time trust boundary, provenance, progressive adoption, quarantine/rollback
- `docs/change-management.md`: Class C/D 변경 분류, workflow-wide impact analysis, runtime/toolchain verification, regression rule

프로젝트별 특수성은 ADR 또는 project-specific guidance로 분리하고, 공통 정책은 위 두 표준을 참조합니다.
