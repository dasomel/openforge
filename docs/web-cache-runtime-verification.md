# WEB-008 Runtime Web Cache Verification

`WEB-008` adds opt-in runtime evidence for image cache behavior.

It is intentionally separate from `WEB-007`:

- `WEB-007` evaluates repository/source configuration evidence.
- `WEB-008` performs a read-only HTTP `HEAD` request against one explicit image URL supplied by the user.

OpenForge does not auto-discover or automatically call image URLs from the target repository.

## Usage

```bash
openforge assess . \
  --web-cache-url https://cdn.example.com/assets/logo.a1b2c3d4.webp \
  --format json
```

When `--web-cache-url` is omitted, `WEB-008` is `SKIP` and does not affect the score.

## Pass criteria

The explicit endpoint must return a successful HTTP status and a `Cache-Control` header containing:

- `immutable`
- `max-age` or `s-maxage` of at least 86,400 seconds

Example:

```text
Cache-Control: public, max-age=31536000, immutable
Age: 42
ETag: "a1b2c3d4"
```

`Age`, `ETag`, and `Last-Modified` are collected as supporting evidence when present, but they are not currently required for PASS.

## Safety and determinism

The first implementation deliberately keeps the network scope narrow:

- only an explicit `http://` or `https://` URL is accepted
- URL userinfo credentials are rejected
- only a `HEAD` request is issued
- redirects are not followed
- connection timeout is 5 seconds
- total request timeout is 10 seconds
- the supplied URL is not copied into the assessment evidence, avoiding accidental disclosure of signed query parameters

A redirect therefore fails this first runtime check instead of silently extending the network target set. A future provider/runtime adapter can add explicit redirect policy if there is a strong use case.

## Evidence level

`WEB-008` proves only what was observed from the selected endpoint at assessment time. It does not prove global CDN configuration, cache-hit ratio, origin shielding, browser behavior, or behavior for other assets.

Recommended evidence progression:

```text
WEB-007 source/config evidence
        |
        v
WEB-008 explicit endpoint runtime header evidence
        |
        v
future cache effectiveness / CDN telemetry evidence
```
