# Release Security Standard

Release is a distinct trust boundary between building software and distributing software.

## Release lifecycle

```text
Source
→ Build
→ Test
→ Security Gate
→ Artifact Freeze
→ Approval
→ Publish
→ Post-publish Verify
→ Monitor
```

## Requirements

- Separate build and publish identities.
- Do not publish directly from untrusted or general-purpose CI jobs.
- Freeze the exact artifact digest before publish.
- Re-verify artifact identity immediately before publication where practical.
- Prefer staged publishing or approval-supported registry features when available.
- Protect release branches/tags and publishing configuration.
- Verify the published artifact matches the approved artifact.
- Maintain last-known-good release identity and rollback procedure.
- Define quarantine/revocation handling for compromised releases.
- Record release evidence linking source, dependency set, builder, artifact and approver where applicable.

## Trust limitations

- Signature does not prove an artifact is benign.
- Provenance does not prove that the source or behavior was intended.
- SBOM does not prove malware absence.
- Successful CI does not prove release safety.

These signals are evidence for policy decisions, not automatic authorization to publish.
