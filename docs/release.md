# Release Standard

Use a predictable release lifecycle and keep release artifacts traceable.

## Versioning

Prefer Semantic Versioning for libraries and applications where it fits:

```text
MAJOR.MINOR.PATCH
```

Document breaking changes clearly.

## Changelog

Maintain:

```text
CHANGELOG.md
CHANGELOG-ko.md
```

Korean and English changelogs must remain semantically synchronized.

## Release checklist

- CI passes on the release commit
- security/dependency checks reviewed
- version updated consistently
- changelog updated
- release notes prepared in English and Korean
- artifacts published from a known commit
- rollback/recovery notes documented when applicable
