# Documentation Site Blueprint

OpenForge treats source implementation assets and public explanatory documentation as two related layers:

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

## Source-of-truth rule

Keep standards, reusable configuration, scripts, templates, and exact implementation examples in the project repository. A documentation portal should explain and link to those assets rather than silently copying them.

## Recommended URL model

```text
/{locale}/docs/{project}/
/{locale}/docs/{project}/concepts
/{locale}/docs/{project}/getting-started
/{locale}/docs/{project}/reference
/{locale}/docs/{project}/operations
/{locale}/docs/{project}/troubleshooting
/{locale}/docs/{project}/adr
```

A project may add deeper paths, but the project namespace should remain stable.

## Content model

A document should expose at least:

```yaml
title: Page title
description: One-line description
project: Project Name
path: project/section/page
order: 100
lastModified: 2026-08-21
```

The `path` is the public information architecture. The source filename may remain implementation-oriented.

## Documentation navigation

Use a hierarchy that separates:

- Concepts: what and why
- Getting Started / Guides: how to accomplish a task
- Tutorials: end-to-end learning paths
- Reference: exact configuration/API/CLI information
- Operations: deploy, observe, upgrade, backup, restore
- Troubleshooting: symptom → evidence → root cause → fix
- ADR: why a design or policy decision was made

## Bilingual projects

Use identical path structures for locales:

```text
/ko/docs/project/...
/en/docs/project/...
```

Localized documents should be structurally aligned even when wording is not a literal translation.

## Template contract

A documentation-site template should provide:

1. locale routing
2. hierarchical document paths
3. frontmatter-driven navigation
4. project grouping
5. source links back to GitHub
6. generated table of contents
7. architecture diagrams from source-controlled definitions
8. static-build validation

This blueprint is intentionally implementation-neutral. Next.js, MkDocs, Docusaurus, Astro, or another static/documentation stack may implement it.
