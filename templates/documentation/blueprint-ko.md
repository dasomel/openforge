# Documentation Site Blueprint

OpenForge는 source implementation asset과 public explanatory documentation을 두 개의 연계된 계층으로 봅니다.

```text
OpenForge repository
  ├── standards
  └── templates
        ↓
Project implementation
        ↓
Documentation site
  ├── concepts
  ├── guides / tutorials
  ├── reference
  ├── operations
  ├── troubleshooting
  └── ADR
```

## Source-of-truth 원칙

Standard, reusable configuration, script, template, exact implementation example은 프로젝트 repository에 둡니다. Documentation portal은 이를 설명하고 링크하며, 동일 내용을 별도로 복사해 관리하지 않습니다.

## 권장 URL 모델

```text
/{locale}/docs/{project}/
/{locale}/docs/{project}/concepts
/{locale}/docs/{project}/getting-started
/{locale}/docs/{project}/reference
/{locale}/docs/{project}/operations
/{locale}/docs/{project}/troubleshooting
/{locale}/docs/{project}/adr
```

더 깊은 경로를 사용할 수 있지만 project namespace는 안정적으로 유지합니다.

## Content Model

문서는 최소한 다음 metadata를 갖습니다.

```yaml
title: Page title
description: One-line description
project: Project Name
path: project/section/page
order: 100
lastModified: 2026-08-21
```

`path`는 public information architecture이고, source filename은 implementation-oriented naming을 사용할 수 있습니다.

## Documentation Navigation

- Concepts: 무엇이고 왜 필요한가
- Getting Started / Guides: 특정 작업을 어떻게 수행하는가
- Tutorials: 끝까지 따라가는 학습 경로
- Reference: 정확한 configuration/API/CLI
- Operations: deploy, observe, upgrade, backup, restore
- Troubleshooting: symptom → evidence → root cause → fix
- ADR: 설계/정책 결정을 왜 선택했는가

## Bilingual

Locale별 path 구조를 동일하게 유지합니다.

```text
/ko/docs/project/...
/en/docs/project/...
```

문서 구조는 맞추되 번역은 직역보다 대상 독자의 맥락에 맞춥니다.

## Template Contract

Documentation-site template은 다음을 지원해야 합니다.

1. locale routing
2. hierarchical document paths
3. frontmatter-driven navigation
4. project grouping
5. GitHub source links
6. generated table of contents
7. source-controlled architecture diagrams
8. static-build validation

구현 기술은 고정하지 않습니다. Next.js, MkDocs, Docusaurus, Astro 등 정적 documentation stack을 사용할 수 있습니다.
