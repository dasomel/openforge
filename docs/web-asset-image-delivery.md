# Web Asset / Image Delivery Maturity

OpenForge treats image delivery as an engineering capability rather than a recommendation for a specific vendor.

The goal is to detect whether a project has a repeatable strategy for responsive images, layout stability, modern formats, caching/optimization, and external-origin control.

## Reference architecture

```text
Image Source
   |
   v
Image Optimizer / Proxy
   |- origin validation
   |- resize / crop
   |- format conversion
   |- quality optimization
   |- cache-key normalization
   v
CDN / HTTP Cache
   |
   v
Browser
```

The optimizer may be application-native, self-hosted, or managed. OpenForge does not assign a higher score simply because a specific vendor or hosted service is used.

## Maturity rules

| Rule | Intent | Weight |
|---|---|---:|
| WEB-001 | non-critical images use lazy loading | 4 |
| WEB-002 | images reserve layout space with explicit dimensions | 5 |
| WEB-003 | responsive image delivery is present | 6 |
| WEB-004 | WebP/AVIF or equivalent modern delivery is referenced | 4 |
| WEB-005 | external images use an optimization/CDN path | 6 |
| WEB-006 | external image origins are constrained | 6 |

If no image usage is detected in supported web source files, all WEB rules are `SKIP` and do not affect the score.

The analyzer scans HTML, JSX, TSX, Vue, Svelte, Astro, Markdown/MDX, JavaScript, and TypeScript source. It intentionally favors explainable static evidence over heuristic browser simulation.

## Per-image coverage scoring

`WEB-001` through `WEB-004` are coverage rules. OpenForge extracts individual image usages and calculates the fraction that satisfy each rule.

```text
coverage = matching image usages / total detected image usages
score    = coverage * rule weight
```

A rule is `PASS` only when coverage is 100%. Partial coverage remains `FAIL`, but receives proportional credit so the maturity score reflects incremental improvement.

Example:

```text
FAIL [WEB-002] Images declare dimensions
coverage=17/20 coverage_percent=85.0
score=4.3/5.0
covered=src/pages/index.tsx:42
missing=src/components/Avatar.tsx:18
```

Evidence is reported at source location granularity and includes both covered and missing examples.

Current extraction semantics:

- `<img>` usages are evaluated per tag.
- JSX/TSX `<Image>` usages are treated as framework image components. They count as responsive and optimized by default, and lazy-loaded unless `priority` or eager loading is explicitly requested.
- `<Image fill>` satisfies layout-space handling for WEB-002.
- Markdown image syntax is counted as an image usage, but lazy loading, explicit dimensions, and responsive behavior are not inferred from Markdown alone.
- WebP/AVIF is credited only when the specific image fragment references the modern format or transformation option.

These rules deliberately avoid assuming browser/runtime behavior that cannot be established from source evidence.

## External image optimization coverage

`WEB-005` applies only to image usages whose source is an explicit `http://` or `https://` URL. Local and relative images do not participate in this rule.

OpenForge calculates how many external image usages pass through a recognized optimizer/CDN path. Framework image components such as Next.js `<Image>` are treated as optimized because the framework provides an image delivery pipeline unless explicitly configured otherwise.

```text
external_proxy_coverage = optimized external image usages / external image usages
```

If a project has no external images, WEB-005 is `SKIP` rather than `PASS`. This prevents local-only projects from receiving credit for a capability they do not need.

## External origin allow-list coverage

`WEB-006` extracts distinct external image hosts and compares them with explicit origin configuration found in the repository.

Examples of recognized policy signals include Next.js `remotePatterns` / `images.domains` and equivalent `allowedOrigins` / `allowed_origins` declarations. Exact hosts and wildcard subdomains such as `*.cdn.example.net` are supported by the first implementation.

```text
origin_coverage = allowed external image hosts / distinct external image hosts
```

Example:

```text
FAIL [WEB-006] External image origins are constrained
origin_coverage=2/3 coverage_percent=66.7
allowed=images.example.com
allowed=avatars.example.net
missing_allowlist=legacy.example.org
```

A rule is `PASS` only when every detected external image origin is represented by the source-level allow-list evidence. Partial coverage receives proportional score.

This remains a static source assessment. It does not prove that runtime requests cannot reach other destinations, so SSRF prevention and proxy runtime policy can be added as deeper provider/runtime checks later.

## Why origin control matters

Image proxy services fetch origin URLs on behalf of clients. Projects that accept arbitrary external image origins can unintentionally create SSRF-like fetch paths, uncontrolled bandwidth use, or privacy exposure. An allow-list or equivalent origin policy is therefore treated as a maturity signal when an external image path is present.

OpenForge does not claim that a textual allow-list reference alone proves complete request security. Runtime and configuration-specific validation can be added later as provider adapters.

## Public image service vs self-hosted image proxy

A public image service can be appropriate for public documentation, public thumbnails, avatars, and low-criticality OSS sites. It should not automatically become a production dependency for private or sensitive assets.

A self-hosted image proxy is more appropriate when the project requires control over availability, origin access, private assets, networking, cache policy, or deployment location.

Recommended progression:

```text
Static/native image optimization
        |
        v
Public or managed image optimization
        |
        v
Self-hosted / controlled image proxy
        |
        v
Policy-governed image delivery with observability
```

This is not a strict ladder. The correct level depends on the project threat model and operational requirements.

## wsrv.nl / weserv/images as a reference implementation

`wsrv.nl` is a useful reference implementation for URL-driven image resize/cache behavior. The open-source `weserv/images` project can be self-hosted and uses nginx with libvips. Its project documentation also describes Cloudflare for CDN caching/IP blocking, Valkey for rate limiting, and OpenDNS for DNS filtering.

OpenForge treats wsrv.nl only as an example. Equivalent application-native optimizers, managed image CDNs, or self-hosted proxies can satisfy the same engineering intent.

Example public transformation URL:

```text
https://wsrv.nl/?url=example.com/images/a.jpg&w=600&output=webp&q=80
```

For private images, authenticated assets, closed networks, or workloads requiring an SLA, prefer controlled/self-hosted delivery rather than assuming a public endpoint is suitable.

## Planned extensions

Further improvements can add:

- cache-control and immutable asset URL analysis
- framework-specific image configuration adapters
- exact parser adapters for Next.js and common image proxy configs
- fallback behavior for failed external origins
- self-hosted proxy runtime health
- cache hit ratio / origin latency evidence
- image payload size and format effectiveness
- HTML report integration and score history

The deterministic score remains independent of optional AI result analysis.
