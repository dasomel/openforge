# Repository Standard

Every OpenForge-based project should start with a predictable, maintainable repository layout.

```text
project/
├── README.md
├── README-ko.md
├── LICENSE
├── CONTRIBUTING.md
├── CONTRIBUTING-ko.md
├── SECURITY.md
├── SECURITY-ko.md
├── CODE_OF_CONDUCT.md
├── CODE_OF_CONDUCT-ko.md
├── CHANGELOG.md
├── CHANGELOG-ko.md
├── .editorconfig
├── .gitignore
├── .github/
├── docs/
├── src/ or application-specific source tree
└── tests/
```

## Rules

- Use lowercase kebab-case repository names where applicable.
- Keep generated artifacts out of source control.
- Keep configuration examples safe and secret-free.
- Prefer one authoritative source for versions and compatibility information.
- Use standard directory names for source, tests, docs and GitHub metadata.
- Keep architecture and lifecycle documents versioned with the project.
