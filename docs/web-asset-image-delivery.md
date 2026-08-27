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
| WEB-005 | an image optimization/CDN path is present | 6 |
| WEB-006 | external image origins are constrained | 6 |

If no image usage is detected in supported web source files, all WEB rules are `SKIP` and do not affect the score.

The first implementation scans HTML, JSX, TSX, Vue, Svelte, Astro, Markdown/MDX, JavaScript, and TypeScript source. It intentionally favors explainable static evidence over heuristic browser simulation.

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

The initial static analyzer is intentionally conservative. Future improvements can add:

- per-image coverage rather than file-level evidence
- cache-control and immutable asset URL analysis
- framework-specific image configuration adapters
- origin allow-list validation for Next.js and common image proxies
- fallback behavior for failed external origins
- self-hosted proxy runtime health
- cache hit ratio / origin latency evidence
- image payload size and format effectiveness
- HTML report integration and score history

The deterministic score remains independent of optional AI result analysis.
