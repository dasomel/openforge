# WEB-009 Runtime Cache Effectiveness

`WEB-009` measures whether cache-hit evidence is observable for one explicit image endpoint.

It is deliberately separate from the earlier layers:

- `WEB-007`: source/configuration evidence for immutable caching.
- `WEB-008`: one runtime `HEAD` response has a long-lived immutable `Cache-Control` policy.
- `WEB-009`: two runtime `HEAD` responses expose evidence that a cache path is actually being used.

## Usage

```bash
openforge assess . \
  --web-cache-effectiveness-url https://cdn.example.com/assets/logo.a1b2c3d4.webp \
  --format json
```

When the option is omitted, `WEB-009` is `SKIP` and does not affect the score.

## Observable signals

The second request passes when at least one explicit cache-hit signal is observed:

- `Age` greater than zero
- `X-Cache-Hits` greater than zero
- `Cache-Status` containing a hit signal
- `CF-Cache-Status` containing a hit signal
- `X-Cache` containing a hit signal

`MISS`-style values are not treated as hits.

Evidence is recorded with `first_` and `second_` prefixes so the two observations remain distinguishable.

## Safety boundary

The implementation intentionally keeps network behavior narrow and predictable:

- only a URL explicitly provided by the user is requested
- only `http://` and `https://` are accepted
- URL userinfo credentials are rejected
- exactly two read-only `HEAD` requests are issued
- redirects are not followed
- connection timeout is 5 seconds
- total timeout per request is 10 seconds
- the source URL is not copied into assessment evidence

OpenForge does not auto-discover repository URLs for this check.

## Interpretation limits

A PASS proves only that cache-hit evidence was observable for the selected endpoint at assessment time. It does not prove global cache-hit ratio, CDN coverage, browser caching behavior, origin shielding, freshness correctness, or equivalent behavior for other assets.

The intended maturity progression is:

```text
WEB-007 source/config evidence
        |
        v
WEB-008 runtime cache-policy evidence
        |
        v
WEB-009 runtime cache-hit evidence
        |
        v
future provider telemetry / cache-hit-ratio evidence
```
