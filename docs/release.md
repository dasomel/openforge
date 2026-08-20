# Release Standard

Use a predictable release lifecycle and keep release artifacts traceable.

## Versioning

Prefer Semantic Versioning for libraries and applications where it fits:

```text
MAJOR.MINOR.PATCH
```

Document breaking changes clearly.

When multiple artifacts carry versions (application, image, Helm chart, CLI, base image, deployment bundle), keep one authoritative compatibility inventory such as `VERSIONS.md` and validate drift automatically where practical.

## Changelog

Maintain:

```text
CHANGELOG.md
CHANGELOG-ko.md
```

Korean and English changelogs must remain semantically synchronized.

## Release procedure

Projects with non-trivial packaging should keep an explicit release guide:

```text
RELEASING.md
RELEASING-ko.md
```

Document version bumping, artifact build, signing/provenance, registry publication, verification and rollback/recovery.

## Release checklist

- CI passes on the release commit
- security/dependency checks reviewed
- version updated consistently
- version compatibility inventory updated when applicable
- changelog updated
- release notes prepared in English and Korean
- artifacts published from a known commit
- image/package provenance and SBOM produced when applicable
- artifact digests recorded when practical
- rollback/recovery notes documented when applicable
