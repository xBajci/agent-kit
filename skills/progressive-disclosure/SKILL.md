---
name: progressive-disclosure
description: "Design, audit, implement, and verify web UI using progressive disclosure rules. Use when asked to simplify an overloaded interface, decide what stays visible versus expandable, review screenshots or frontend code for hidden functionality, or design and verify forms, filters, accordions, drawers, advanced settings, contextual actions, and multi-step flows. Accept screenshots, source code, running apps, or a design brief; distinguish visual evidence, static code findings, runtime verification, and user-research hypotheses. Support Czech requests such as navrhni UI, zkontroluj screenshot, zjednoduš formulář, and ověř progressive disclosure. Do not use for progressive web apps, lazy loading alone, or general aesthetic critique unrelated to disclosure."
---

# Progressive Disclosure

Design for successful tasks, discoverability, and understandable state. Treat fewer visible controls as a means, never a success metric. Respond in the user's language and preserve the product's terminology and design system.

## Choose scope and mode

1. Extract the main task, audience, visit frequency, supplied artifacts, and requested mode. State reasonable assumptions briefly; do not block useful work for missing personas or analytics.
2. Use **Design** for proposals, **Audit** for assessment, and **Implement + verify** when changes are requested. A review alone does not authorize code edits or deployment.
3. Identify common, advanced, and comparison tasks. Distinguish occasional users from frequent operators. Do not infer feature frequency from visual prominence or low analytics alone.
4. Inspect supplied artifacts before recommending changes. If no artifact exists but the brief is sufficient, propose a design and mark it unverified. Ask for an artifact only when needed to assess an existing UI.
5. Honor project instructions and tool permissions. Use authorized browser access when available; do not invent access or bypass restrictions. Do not require a running app to deliver a useful static review.

## Load references selectively

- Read [decision-rules.md](references/decision-rules.md) for rule IDs, pattern selection, and tradeoffs in every substantive review or proposal.
- Read [verification.md](references/verification.md) when inspecting code, interactive behavior, accessibility, or preparing acceptance criteria.
- Read [sources.md](references/sources.md) when explaining research support or checking a disputed recommendation. Treat summaries as a dated snapshot; verify current platform/standard details before version-specific claims.

## Build an evidence inventory

### Screenshots

- Open and inspect each relevant image visually. Record image identity, visible viewport/state, and exact labels or regions; use coordinates only when reliably known.
- Inspect hierarchy, primary actions, disclosure triggers, labels, selected values, errors, and context retained around overlays.
- Treat OCR as assistance, not a substitute for seeing the image. Mark unreadable text rather than inventing it.
- Do not equate absent-from-crop with absent-from-app. Do not infer clickability, keyboard behavior, ARIA, validation, persistence, responsive behavior, or hidden contents from a static image.
- Compare only supported states and viewports across images. Request a missing state only when it would change a material conclusion; otherwise list it as unverified.

### Code

- Read applicable project instructions, package scripts, related screens, and shared components. Use `rg` to locate routes, triggers, controlled content, conditional branches, form schemas, payload construction, and tests.
- Trace initial state -> user action -> state update -> visible summary -> save/close/back/error. Do not judge by component names alone.
- Inspect shared primitives before calling a component inaccessible; a wrapper may already implement keyboard/ARIA behavior.
- Cite file path and symbol or an allowed line location. Distinguish source-level issues from reproduced runtime issues. Conditional JSX proves neither good UX nor runtime failure.
- Map screenshots to code by route/component and state. If they disagree, report possible version drift rather than silently choosing one as authoritative.

### Running app

- Capture initial and relevant revealed states using available authorized tooling. Exercise common and advanced tasks, not every page.
- Use harmless sample data. Avoid messages, publishing, production deletion, or other external side effects without task authorization.
- Record actions and outcomes. If blocked, continue screenshot/code assessment and mark runtime checks not verified.

## Apply decision rules

Evaluate task relevance, frequency, consequence of omission, comparison needs, default safety, and trigger discoverability for each candidate section. Use the reference's PD rule IDs. Prefer the smallest change that solves the problem.

Keep mandatory decision information, critical warnings, main actions, and important active state visible at the point of need. Hide only information whose deferral is justified. Distinguish optional disclosure, conditional fields, contextual controls, and mandatory staged flows.

Do not impose a universal control-count limit, two-level law, three-click rule, or invented usability score. Prefer shallow structures but justify exceptions from tasks. Treat anticipated usage frequency and novice/expert preferences as hypotheses unless supported.

## Design

1. Inventory information and controls. Classify each as **visible**, **on demand**, **conditional**, or **separate step/page**.
2. Provide a compact disclosure specification: item; placement; exact trigger label; revealed content; retained summary; close/back behavior; rationale.
3. Describe relevant states: initial, expanded, selected/edited, validation error, loading/empty where applicable, and narrow viewport.
4. Preserve working interactions and existing tokens/components. Consider removing redundancy or improving labels before adding containers. Include keeping everything visible when it better supports the task.
5. Provide concrete copy and acceptance criteria. Produce visual artifacts when requested or materially useful using appropriate available design/image/prototype workflows. Do not require mockup generation for text recommendations or code audits.

## Audit

1. State the task and evidence boundary briefly.
2. Rank findings by user impact, with IDs such as F1. Give location, evidence, affected task, PD rule, consequence, specific change, and verification criterion.
3. Assign severity independently of confidence: **blocker** prevents completion or causes serious loss; **major** hides essential information or repeatedly impedes the main task; **minor** adds recoverable friction; **opportunity** is a hypothesis worth testing.
4. Label evidence **visible in screenshot**, **confirmed in code**, **reproduced at runtime**, or **hypothesis**. Keep severity conditional for unproven risks.
5. Mention effective existing disclosure when useful. Report no issue when supported; never manufacture a quota of findings.

## Implement and verify

1. Establish current behavior and make a scoped change using existing primitives. Preserve data semantics, authorization, routes, and unrelated functionality.
2. Apply relevant state/accessibility checks in [verification.md](references/verification.md). Hiding UI is never a security boundary.
3. Run existing relevant checks and targeted interactions warranted by behavioral risk. Add regression tests for meaningful state/validation/focus risks, not trivial copy edits or markup mirroring.
4. Reinspect changed UI at relevant viewports and states when runtime access exists. Compare the same states before and after.
5. Report each material criterion as **passed**, **failed**, **not verified**, or **not applicable**, with evidence. A static review or successful build does not establish runtime usability or WCAG conformance.
6. Stop when the requested scope is sufficiently verified. Report residual gaps and the exact next check needed; do not broaden indefinitely or imply unrun tests passed.

## Handoff

Lead with the result and priorities. Match depth to scope; use a findings table for comparable issues. For design, include the disclosure specification; for changes, summarize what changed, why, and what was actually checked. Include unresolved decisions/checks only if any remain.

When measuring success, propose task completion, time, errors, unaided discovery, and understanding of active state across novice/frequent users. Interpret expansion rates in context. Never claim conversion improvements from heuristics alone.
