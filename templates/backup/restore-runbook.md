# Backup / Restore Runbook Template

## Scope

- Data stores:
- Persistent volumes:
- Configuration/secrets:
- Artifact/configuration bundles:

## Backup

1. Capture a consistent snapshot or application-aware dump.
2. Record source version and backup timestamp.
3. Encrypt and store backup outside the primary failure domain.
4. Verify backup integrity.
5. Retain at least one last-known-good backup.

## Restore validation

```text
backup
  ↓
restore into isolated environment
  ↓
application startup
  ↓
health checks
  ↓
data consistency checks
  ↓
smoke/E2E test
```

## Recovery evidence

- Backup identifier:
- Restore duration:
- RPO achieved:
- RTO achieved:
- Integrity check:
- Application validation:
