# Architecture Diagram Template

Use Mermaid for diagrams that should remain source-controlled and easy to review.

```mermaid
flowchart LR
    U[Users / Clients] --> G[Gateway / Ingress]
    G --> APP[Application]
    APP --> DB[(Data Store)]
    APP --> OBS[Observability]
    APP --> IDP[Identity Provider]

    subgraph Delivery
      CI[CI] --> ART[Artifact Registry]
      ART --> G
    end
```

## Diagram rules

- Start with user-visible boundaries before implementation details.
- Keep one primary diagram per architectural concern.
- Show trust boundaries, external dependencies, persistent state, and control planes when relevant.
- Link implementation details to source files or deployment manifests.
- Prefer Mermaid for editable diagrams; use exported SVG/PNG only as derived artifacts.
