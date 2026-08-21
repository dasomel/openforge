# Secrets and Machine Identity Standard

Credentials used by development, CI, release and deployment are supply-chain assets.

## Requirements

- Prefer short-lived credentials and OIDC over long-lived tokens.
- Scope credentials to repository, environment, job and action as narrowly as practical.
- Separate developer, CI, release and production identities.
- Grant publish permissions only to release jobs that require them.
- Never store secrets in source, generated artifacts, cache or logs.
- Apply secret scanning to source and generated release material where practical.
- Rotate or revoke credentials immediately after suspected exposure.
- Document emergency credential recovery and replacement.

## Identity separation

```text
developer
  ≠ CI build
  ≠ release
  ≠ package publish
  ≠ production deployment
```

Identity changes, OIDC trust changes and publishing configuration changes are security-sensitive changes.
