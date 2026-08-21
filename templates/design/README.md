# OpenForge Design Templates

Design templates for making OSS projects feel consistent, readable, and maintainable without forcing a single visual identity.

## Design layers

```text
Project identity
  ↓
README / landing page
  ↓
Documentation information architecture
  ↓
Architecture diagrams
  ↓
Status / health communication
  ↓
Release / changelog presentation
```

## Templates

- `README-template.md` — project homepage structure with stable information hierarchy.
- `project-landing.html` / `project-landing.css` — accessible, responsive static OSS project landing page.
- `architecture.md` — Mermaid-based architecture diagram structure.
- `status.md` — project health/status presentation template.
- `design-tokens.css` — small neutral design token layer for project sites and docs.

Templates intentionally avoid brand-specific colors and dependencies. Projects should apply their own identity while keeping the information architecture and accessibility baseline.
