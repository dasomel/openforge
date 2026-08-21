# Documentation Site Template

This directory defines the reusable documentation-site contract for projects that expose public engineering documentation.

- `blueprint.md` — implementation-neutral documentation-site architecture and content contract.
- `blueprint-ko.md` — Korean counterpart.

Use the blueprint when creating the corresponding documentation site. The site may live in the project repository, a dedicated documentation repository, or a portfolio documentation portal.

Recommended relationship:

```text
Project repository
  ├── source code
  ├── standards / templates
  └── exact implementation
          ↓
Documentation site
  ├── explanation
  ├── tutorial
  ├── reference
  └── evidence / lessons
```
