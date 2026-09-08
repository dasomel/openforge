# OSS Portfolio Maintenance Intelligence

OpenForge treats implementation completion as the start of a maintenance lifecycle, not the end of engineering responsibility.

This model is intentionally separate from development status and OpenForge adoption. A project can be fully implemented and still be a poor long-term portfolio choice if nobody owns patching, its blast radius is misunderstood, or there is no realistic replacement path.

## Decision questions

Every maintained project SHOULD answer these questions during lifecycle review:

1. **Blast radius** — what breaks or becomes exposed if this project fails, is compromised, or stops receiving maintenance?
2. **Maintenance ownership** — who is personally accountable for vulnerability triage, patching, upgrades, and recovery?
3. **Strategic role** — does the project differentiate the portfolio, enable differentiating work, provide a utility, validate an experiment, or temporarily fill a market gap?
4. **Exit path** — if a stronger upstream/commercial/OSS alternative appears, can the project be replaced or retired without unacceptable migration cost?

These questions are derived from the Build-vs-Buy maintenance principle that AI reduces initial implementation cost much faster than it removes multi-year operational responsibility.

## Canonical metadata

`portfolio/maintenance.json` is the source of truth for maintenance governance.

Each project records:

- `maintenance_owner`: accountable maintainer identity
- `maintenance_status`: `owned`, `shared`, `unowned`, or `review-required`
- `strategic_role`: `differentiator`, `enabler`, `utility`, `experiment`, or `temporary-gap`
- `blast_radius`: `high`, `medium`, or `low`
- `exit_path_status`: `defined`, `partial`, `review-required`, or `not-applicable`
- `review_cadence`: lifecycle review frequency

The initial registry deliberately marks exit paths as `review-required` rather than inventing alternatives that have not been evaluated.

## Lifecycle governance

A portfolio project can move through a lifecycle independently of feature-development status:

```text
experimental -> incubating -> active -> mature -> maintenance -> deprecated -> archived
```

OpenForge does not automatically infer these transitions from a code merge or release. The owning repository must provide evidence for development status, while lifecycle/maintenance decisions remain explicit portfolio governance decisions.

## Maintenance readiness

A future readiness score MAY be derived only from evidence-backed checks such as:

- accountable maintainer assigned
- security policy and vulnerability intake path
- dependency/update automation
- supported CI and release procedure
- incident/recovery path
- documented replacement or retirement path
- dependency/impact relationships known
- lifecycle review completed within cadence

A numeric score MUST NOT be introduced by simply assigning arbitrary weights to unverified declarations.

## Review cadence

Quarterly is the portfolio default. The review should answer at minimum:

- Would we choose to build and own this project again knowing its current maintenance cost?
- If a critical vulnerability is disclosed tomorrow, who detects and patches it?
- Has the blast radius changed because more projects now depend on it?
- Is the project still strategically justified?
- Has a credible replacement appeared?
- Should the project remain active, move to maintenance, be deprecated, or be archived?

## Relationship to the Portfolio Control Plane

```text
Development evidence
        ↓
OpenForge status PR
        ↓
Official development state
        │
        ├── Dependency / impact intelligence
        └── Maintenance / lifecycle intelligence
                     ↓
             Invest / Maintain / Replace
             Deprecate / Archive
```

OpenForge merge remains the official portfolio-state boundary. Maintenance metadata is reviewed alongside development and impact information rather than being silently inferred from repository activity.
