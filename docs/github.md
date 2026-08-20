# GitHub Standard

OpenForge projects use GitHub as the primary system for collaboration and change management.

## Issues

Recommended types:

- Bug
- Feature
- Architecture
- Documentation
- Dependency
- Security

Use issues to capture requirements, decisions and implementation scope before substantial changes.

## Pull Requests

Every meaningful change should be submitted through a pull request when collaboration or review is expected.

PRs should:

- explain the problem and solution
- link relevant issues
- describe tests
- include documentation updates when needed
- keep commits focused

## Branches

Prefer short-lived branches such as:

```text
feat/<name>
fix/<name>
refactor/<name>
chore/<name>
docs/<name>
```

## Commits

Prefer Conventional Commits:

```text
feat: add unified service API
fix: handle stale metadata
chore: update dependencies
docs: add architecture guide
```
