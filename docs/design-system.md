# OpenForge OSS Design System

OpenForge Design System is a shared UI/UX contract for open-source projects that need a consistent engineering quality bar without forcing every product to look identical.

**Figma source:** https://www.figma.com/design/Y1JpRSOwctAKSwPjDNbe1g

## 1. Goals

- Standardize semantic color, spacing, radius, typography, state, focus, and accessibility.
- Reuse interaction patterns across platform portals, desktop operators, operations dashboards, admin consoles, data control planes, and developer tools.
- Preserve project identity through controlled accent, density, navigation, and visualization choices.
- Keep design-to-code handoff explicit through CSS-compatible token names and `DESIGN.md` project contracts.

## 2. Core principles

1. **Clarity before decoration** — state, consequence, and next action come first.
2. **Task-first density** — density follows the operating context rather than a single global preference.
3. **Semantic consistency** — success, warning, serious, danger, info, focus, selected, and disabled retain the same meaning.
4. **Accessible by default** — keyboard, focus, contrast, non-color status cues, and usable targets are release criteria.
5. **Progressive disclosure** — advanced YAML, logs, topology details, raw identifiers, and destructive options appear when needed.
6. **OSS-native handoff** — tokens map to code and deviations are documented instead of silently forked.

## 3. Foundations

### Semantic colors

Projects should consume semantic roles rather than raw palette values:

- `color/bg/canvas`, `color/bg/surface`, `color/bg/subtle`, `color/bg/inverse`
- `color/text/primary`, `color/text/secondary`, `color/text/muted`, `color/text/inverse`
- `color/border/default`
- `color/action/primary`, `color/action/hover`
- `color/focus/ring`
- `color/status/success`, `warning`, `serious`, `danger`, `info`

Figma semantic colors support Light/Dark modes. Web implementations should map them to `--of-*` CSS custom properties or alias existing project tokens to them.

### Spacing and radius

Base spacing: `4, 8, 12, 16, 24, 32, 48, 64px`.

Base radius: `6, 10, 14, 20px`, plus full/pill.

Use the 8px rhythm for layout. Use 4px for tight icon/text relationships. Operator UIs may intentionally use denser card/table spacing than portals.

### Typography

Reference scale:

- Display: 40/48 Bold
- H1: 28/36 Semi Bold
- H2: 22/30 Semi Bold
- Body: 14/21 Regular
- Small: 12/18 Regular
- Label: 12/16 Medium

Identifiers, paths, YAML, commands, raw bytes, DNs, and similar technical values should use an appropriate monospace stack.

### Data visualization

- Categorical series: Blue → Green → Pink → Amber, normally no more than four visible categories before aggregation.
- Sequential magnitude: blue ramp.
- Status colors are reserved for status and must not be reused as ordinary chart-series colors.
- Charts use the same surface/text semantics as the surrounding UI and never rely on color alone.

## 4. Shared components

The Figma source defines the initial shared component contract:

- **Button** — Primary / Secondary / Danger with Default / Disabled states.
- **Status Badge** — Healthy / Warning / Serious / Critical / Info; always text/icon plus color.
- **Stat Tile** — large value + label + contextual limit/remaining value.
- **Data Row** — identifier → state → quantitative context → recency/actions.

Projects may wrap these components in framework-specific implementations, but should preserve intent and state semantics.

## 5. Reusable patterns

### Resource Explorer
Sidebar → filter/search → resource table → detail drawer. Use for namespaces, clusters, users, services, data assets, and similar resource models.

### Topology & Dependency
Health summary → graph → selected-node detail → events/logs. Graphs visualize relationships; list/detail alternatives remain available. Uncertain relationships must be labeled as uncertain.

### Operator Dashboard
Hero metrics → capacity/state → ranked resources → trends. Numbers are the heroes. Always show limits/remaining values where subtraction would otherwise be required.

### Guided Workflow
Prerequisite check → configuration → execution → progress → recovery. Long-running operations expose textual progress, logs, retry/cancel, and actionable failure recovery.

### Desktop Control Surface
Compact sidebar/toolbar → focused workspace → status footer. Favor keyboard-first navigation, split views, native dialogs, and local action safety.

## 6. Project archetypes

### Narwhal — Platform Portal
Comfortable density; global cluster context; topology and health; role-aware actions; progressive YAML/log details.

### Beluga Manager — Data Control Plane
Relationship-first UI. Primary information architecture is Pipeline, Data Asset, Service, and Operations. Preserve upstream OSS context and clearly mark inferred/uncertain correlations.

### ClusterDeck — Desktop Operator
Compact desktop density; keyboard-first navigation; persistent cluster context; split-view detail. Avoid portal-like whitespace.

### KubeMetal — Desktop ML Infrastructure
Guided lifecycle; hardware/runtime visibility; long-running progress and logs; native desktop dialogs and recovery paths.

### ldapium — Admin Console
Strong form/table conventions; DN and identifiers in monospace; bulk-selection safety; explicit destructive confirmations; audit-friendly feedback.

### NFS Quota Agent — Operations Dashboard
Metrics-first, self-contained UI; capacity and remaining values together; chart palette separated from status; dense resource tables. This aligns with the project's existing `DESIGN.md` dashboard contract.

### eGovFrame Launcher — Developer Tool
Wizard/checklist workflow; prerequisite validation; transparent commands/logs; copyable remediation; successful completion ends with a clear next developer action.

## 7. Accessibility release gates

- Normal text contrast ≥ 4.5:1; large text ≥ 3:1.
- Full keyboard operation with logical focus order.
- Visible focus indicator; never remove outline without an equivalent replacement.
- Status never uses color alone.
- Forms use persistent labels and actionable errors.
- Destructive actions identify the affected resource and consequence.
- Respect reduced-motion preferences.
- Dense tables preserve header association, sort state, row focus, truncation recovery, and copy access for technical identifiers.

## 8. Adoption workflow

1. Map project tokens to OpenForge semantic roles.
2. Declare a project archetype in the project's `DESIGN.md`.
3. Adopt shared state/interaction semantics.
4. Apply project-specific accent, density, navigation, and data-viz rules.
5. Document intentional deviations with rationale and accessibility impact.
6. Validate light/dark, keyboard/focus, status cues, loading/error/empty states, and target density during review.

## 9. Design review checklist

- [ ] Semantic tokens used instead of ad-hoc component colors
- [ ] Light and dark modes reviewed where supported
- [ ] Keyboard navigation and focus reviewed
- [ ] Status has a non-color cue
- [ ] Loading, empty, error, success, and disabled states covered
- [ ] Destructive actions communicate consequence
- [ ] Data tables remain usable with long technical identifiers
- [ ] Project archetype and deviations documented
- [ ] Figma and implementation references remain traceable
