---
name: audit-ui
description: Visual design and accessibility audit of an application's interface covering WCAG 2.2 AA (contrast, keyboard and focus, semantics and labels, reflow and target size), visual consistency, hierarchy, and component states, delivered as a PDF/HTML report with ready-to-paste GitHub issues. Use when the user asks for a UI, visual design, design system, or accessibility (a11y, WCAG) audit.
---

# Audit: UI

Audit how the interface looks and whether everyone can perceive and operate
it, and deliver the report defined by the `audit-report` skill. Task flows and
usability belong to `audit-ux`.

Copy this checklist and track it:

```
- [ ] 1. Load audit-report
- [ ] 2. Set up the interface
- [ ] 3. Build the screen inventory
- [ ] 4. Run the automated accessibility checks
- [ ] 5. Check every category on every screen
- [ ] 6. Write findings.json and render
```

## 1. Load audit-report

Invoke the `audit-report` skill now. It defines the findings file you fill in
as you go. The area is `ui`; the issue title prefix is `[UI]`.

## 2. Set up the interface

Ask the user how to run the application in a test environment, with test data.
Use the browser tools available (Claude in Chrome, Playwright) to view screens
at a desktop width and at 320 CSS pixels wide. Work only in the environment the
user names.

If the interface cannot run, audit from the code (styles, components, markup)
and say so in `methodology`. Mark each finding made from code alone with
"from code" in `conditions`.

Save screenshots of findings in `docs/audits/ui/screenshots/`.

## 3. Build the screen inventory

List every screen or page and the shared components and design tokens (colors,
spacing, typography) they use. Record one row per screen in `inventory`:
screen, route or entry point, shared components used, checked at desktop and
mobile width (yes/no).

## 4. Run the automated accessibility checks

Run one automated checker on every screen in the inventory:

- `npx @axe-core/cli <url>`, or axe through Playwright when the project uses it;
- otherwise `npx lighthouse <url> --only-categories=accessibility --output=json`.

Record each confirmed violation as a finding. Automated checkers find only
part of the WCAG failures; categories 2 and 3 need the manual checks below.

## 5. Categories

### 1. Color and contrast (`contrast`)

Text contrast of at least 4.5:1, or 3:1 for large text (WCAG 1.4.3); 3:1 for
control boundaries, focus indicators, and meaningful graphics (1.4.11);
information not conveyed by color alone (1.4.1).

### 2. Keyboard and focus (`keyboard`)

Every action reachable and operable with the keyboard (2.1.1), no keyboard
traps (2.1.2), a logical focus order (2.4.3), a visible focus indicator (2.4.7)
not hidden by sticky headers or overlays (2.4.11), and focus moved into dialogs
and back when they close. Check by tabbing through each screen.

### 3. Semantics and labels (`semantics`)

Text alternatives for meaningful images and icon-only buttons (1.1.1), labels
tied to every form field (3.3.2), native elements or correct roles, names, and
states for custom controls (4.1.2), headings and landmarks that reflect the
structure (1.3.1), and errors announced to assistive technology.

### 4. Layout and responsiveness (`responsive`)

Content usable at 320 CSS pixels wide without horizontal scrolling (1.4.10)
and at 200% text size (1.4.4), touch targets of at least 24 by 24 CSS pixels
(2.5.8), and no overflow or clipping with long text, long names, or
translations.

### 5. Visual consistency (`consistency`)

Design tokens used instead of hard-coded colors, sizes, and spacing; one
component per job instead of several variants of the same button or card; a
consistent type scale, spacing scale, and icon set.

### 6. Visual hierarchy (`hierarchy`)

One clear primary action per screen, grouping and alignment that show what
belongs together, and density that lets the main content stand out.

### 7. Component states (`states`)

Hover, focus, active, disabled, loading, empty, and error states designed for
every interactive component and data view, instead of blank areas or frozen
controls.

### 8. Motion and themes (`motion-theme`)

Animations reduced or removed under `prefers-reduced-motion`, nothing that
flashes, moving content that can be paused (2.2.2), and, when the application
offers a dark or high-contrast theme, every screen and state checked in it.

## Severity

| Level | Meaning |
|---|---|
| `critical` | Some users cannot use a primary flow: a keyboard trap, unlabeled controls on a primary task, or unreadable text. |
| `high` | A WCAG 2.2 AA failure on a primary flow, or a layout broken at a common screen width. |
| `medium` | A WCAG 2.2 AA failure on a secondary screen, or inconsistencies that make the same element look different across screens. |
| `low` | A cosmetic inconsistency. |
| `info` | An observation or improvement idea with no current problem. |

## 6. Write findings.json and render

Fill `findings.json` as `audit-report` defines, with all eight categories in
`categories`, and render it. For each finding, put the screen and the element
in `location`, the WCAG success criterion in `title` when one applies, the
component's `file:line` in `fix` when you found it in code, and a screenshot in
`screenshot`.
