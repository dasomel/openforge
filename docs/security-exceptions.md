# Security Exception and Waiver Standard

Exceptions are controlled risk decisions, not permanent bypasses.

## Required fields

Every security/supply-chain exception SHOULD record:

- scope
- affected repository/component
- reason
- risk assessment
- compensating controls
- owner
- reviewer/approver where available
- creation date
- expiration/review date
- rollback or remediation plan

## Rules

- No indefinite exception without explicit periodic re-approval.
- Emergency exceptions may bypass routine cooling or review only for a defined scope and duration.
- Compensating controls MUST be stronger where normal controls cannot be applied.
- Expired exceptions fail closed where practical.
- Exceptions must not silently become project defaults.

## Single-maintainer projects

A single maintainer may approve an emergency exception when no independent reviewer is available. Automated checks, explicit evidence and a time-bounded retrospective review should compensate for the missing second person.
