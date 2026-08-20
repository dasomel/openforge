# Development Standard

Projects should keep implementation changes small, testable and reviewable.

## Architecture

- Define boundaries before implementation.
- Record important decisions as ADRs.
- Prefer stable domain models over UI-specific APIs.
- Avoid unnecessary coupling to external components.

## Testing

Use the lowest appropriate test level and add end-to-end tests for critical user journeys.

```text
Unit → Component → Integration → E2E
```

## Configuration

- Keep environment-specific configuration explicit.
- Commit safe examples, not secrets.
- Fail clearly when required configuration is missing.

## Dependencies

- Pin or constrain critical dependencies.
- Review dependency updates.
- Remove unused dependencies.

## Localization

All user-facing strings must use translation keys when the application supports multiple languages.
APIs and domain objects must remain locale-neutral.
