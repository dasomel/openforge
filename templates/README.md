# OpenForge Templates

OpenForge provides copyable implementation templates for projects that adopt the standards.

Templates are deliberately conservative. Projects should adapt versions, permissions, paths and ecosystem-specific commands rather than treating them as universal drop-in configuration.

## Structure

```text
templates/
├── github/
│   ├── pull_request_template.md
│   └── CODEOWNERS.security-sample
├── workflows/
│   ├── ci.yml
│   └── release-security.yml
├── scripts/
│   └── verify-toolchain.sh
└── policy/
    └── dependency-policy.yml
```

See the relevant template directory and the linked OpenForge standard before adoption.
