# DESIGN.md — <project-name>

This file records the project-specific design contract used with the OpenForge OSS Design System.

Reference: `docs/design-system.md`
Figma: https://www.figma.com/design/Y1JpRSOwctAKSwPjDNbe1g

## Product archetype

Choose one primary archetype and optionally one secondary archetype:

- Platform Portal
- Data Control Plane
- Desktop Operator
- Operations Dashboard
- Admin Console
- Developer Tool

```yaml
archetype:
  primary: ""
  secondary: ""
  rationale: ""
```

## Product personality

```yaml
personality:
  density: comfortable # compact | comfortable | spacious
  accent: "#2a78d6"
  navigation: "sidebar"
  platformConvention: "web" # web | macos | windows | linux | cross-platform
```

Describe what should feel unique about this product without changing shared semantic meanings.

## Token mapping

Map project tokens to OpenForge roles. Alias existing variables when possible.

```yaml
tokens:
  bgCanvas: "var(--of-color-bg-canvas)"
  bgSurface: "var(--of-color-bg-surface)"
  textPrimary: "var(--of-color-text-primary)"
  textSecondary: "var(--of-color-text-secondary)"
  borderDefault: "var(--of-color-border-default)"
  actionPrimary: "var(--of-color-action-primary)"
  focusRing: "var(--of-color-focus-ring)"
```

## Information architecture

Document primary navigation, global context selectors, resource hierarchy, and detail behavior.

## Core workflows

For each critical workflow record:

1. Entry condition
2. Primary action
3. Progress/loading state
4. Success state
5. Empty state
6. Error and recovery
7. Destructive or irreversible consequences

## Components

List shared OpenForge components used directly or wrapped locally. Record local additions and why they are not generic enough for the shared system.

## Data visualization

Document series types, thresholds, units, aggregation rules, and non-color cues. Status colors must not be used as ordinary categorical series colors.

## Accessibility

- Keyboard flow:
- Focus behavior:
- Contrast notes:
- Target-size/density exception:
- Screen-reader/label notes:
- Reduced-motion behavior:

## Responsive / desktop behavior

Document supported viewport/window ranges, split-view behavior, overflow strategy, and platform-native conventions.

## Deviations

Every intentional deviation from OpenForge must be explicit.

| Rule | Deviation | Rationale | Accessibility impact | Owner |
|---|---|---|---|---|
| | | | | |

## Review checklist

- [ ] Semantic tokens used
- [ ] Project archetype declared
- [ ] Loading/empty/error/success/disabled states covered
- [ ] Keyboard and focus reviewed
- [ ] Status is not color-only
- [ ] Destructive actions communicate consequence
- [ ] Long identifiers and technical data remain usable
- [ ] Light/dark modes reviewed where supported
- [ ] Deviations documented
- [ ] Figma reference and implementation remain traceable
