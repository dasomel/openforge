# Documentation Site Blueprint

OpenForge treats source implementation assets and public explanatory documentation as two related layers:

```text
OpenForge repository
  ├── standards
  └── templates
        ↓
Project implementation
        ↓
OSS Documentation Portal
  ├── project hub
  └── project-specific documentation space
        ├── concepts
        ├── guides / tutorials
        ├── reference
        ├── operations
        ├── troubleshooting
        └── ADR
```

## Source-of-truth rule

Keep standards, reusable configuration, scripts, templates, and exact implementation examples in the project repository. The documentation portal should explain and link to those assets rather than silently copying them.

## Recommended OSS URL model

The documentation portal is intentionally separate from the main blog/workbench UI:

```text
/oss/
/oss/{project}/
/oss/{project}/concepts
/oss/{project}/getting-started
/oss/{project}/reference
/oss/{project}/operations
/oss/{project}/troubleshooting
/oss/{project}/adr

English:
/oss/en/
/oss/en/{project}/
/oss/en/{project}/concepts
```

`/oss/` is the OSS documentation hub/catalog. Each project owns an independent documentation shell, navigation tree, project landing page, and source links. Do not embed project documentation into the generic blog/workbench Docs lane.

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

## Project hub

The `/oss/` landing page should be a catalog rather than an article list. Each project card should expose:

- project name and short description
- current lifecycle/status
- documented capability areas
- link to the independent project documentation
- GitHub/source link

Start with one project (for example OpenForge) to validate the information architecture, then add additional OSS projects without changing the portal contract.

## Bilingual projects

Use identical information architecture for Korean and English:

```text
/oss/{project}/...
/oss/en/{project}/...
```

Localized documents should be structurally aligned even when wording is not a literal translation.

## Template contract

A documentation-site template should provide:

1. independent OSS portal layout
2. project hub/catalog
3. hierarchical project paths
4. frontmatter-driven navigation
5. project grouping
6. source links back to GitHub
7. generated table of contents
8. architecture diagrams from source-controlled definitions
9. static-build validation
10. project-specific theming/navigation without coupling to the main blog UI

This blueprint is intentionally implementation-neutral. Next.js, MkDocs, Docusaurus, Astro, or another static/documentation stack may implement it.
