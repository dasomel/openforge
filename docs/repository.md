# Repository Standard

Every OpenForge-based project should start with a predictable, maintainable repository layout.

```text
project/
├── README.md
├── README-ko.md
├── LICENSE
├── NOTICE                         # when required
├── THIRD-PARTY-LICENSES.md       # when required
├── CONTRIBUTING.md
├── CONTRIBUTING-ko.md
├── SECURITY.md
├── SECURITY-ko.md
├── CODE_OF_CONDUCT.md
├── CODE_OF_CONDUCT-ko.md
├── CHANGELOG.md
├── CHANGELOG-ko.md
├── VERSIONS.md                   # when multiple versions/targets matter
├── .env.example                  # when environment configuration exists
├── .editorconfig
├── .gitignore
├── .github/
├── docs/
├── src/ or application-specific source tree
├── tests/                         # when applicable
└── Makefile                       # when a common command surface is useful
```

## Rules

- Use lowercase kebab-case repository names where applicable.
- Keep generated artifacts out of source control unless they are deliberate release assets or required checked-in generated sources.
- Keep configuration examples safe and secret-free.
- Prefer one authoritative source for versions and compatibility information. Use `VERSIONS.md` when version drift across manifests, charts, images or deployment targets is material.
- Use standard directory names for source, tests, docs and GitHub metadata.
- Keep architecture and lifecycle documents versioned with the project.
- Use a small Makefile or equivalent command runner when it materially improves discoverability and reproducibility.
- Add release, legal and third-party artifacts when the distribution model requires them.
- Add repository-local AI guidance when AI-assisted development is part of the workflow.

## Deployment-specific documentation

Infrastructure projects may separate common documentation from target-specific operational guides:

```text
docs/common/
docs/vagrant/
docs/cloud/
docs/airgap/
```

Do not duplicate common rules merely because deployment targets differ.

## Exceptions

Third-party, vendored, generated, or upstream-contract files may preserve their original naming conventions. The English/Korean filename policy in the Documentation Standard applies to project-owned user-facing documentation.
