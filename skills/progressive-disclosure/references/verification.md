# Verification for screenshots, code, and runtime

Select checks relevant to the evidence and changed behavior; do not impose an exhaustive suite.

## Evidence limits

| Input | Can establish | Cannot establish alone |
| --- | --- | --- |
| Single screenshot | Hierarchy, wording, shown state, local layout | Hidden/offscreen content, keyboard, ARIA, validation, persistence, full responsive behavior |
| Several screenshots | Captured state differences | Actual transitions or retention between captures |
| Source | Conditions, handlers, data flow, explicit semantics | Actual rendering, assistive-tech output, real user discovery |
| Runtime | Behavior exercised in a stated environment | Untested combinations, browsers/devices, representative user performance |
| User study | Observed outcomes in its sample/context | Universal conversion effects or success elsewhere |

Use “not verified” for unavailable checks. Cite image/region, file/symbol, or action sequence. Do not claim full accessibility compliance from an automated scan.

## State and data

Trace initial/default -> open -> edit/select -> close -> reopen -> submit/back/reset.

- Distinguish collapse from deactivation. A collapsed advanced section may still apply; a conditional field hidden by a changed answer may no longer apply.
- Preserve drafts on temporary collapse. Define intentional reset/cancel; do not silently discard values.
- Inspect inactive fields against validation and payload schemas. CSS hiding does not stop native validation or remove values from submission. Unmounting may discard state depending on framework/library.
- Prevent invisible required fields blocking submission. Reveal and identify invalid sections before focusing their error fields, following existing error-summary conventions.
- Keep active values and important nondefault settings understandable after collapse; permit predictable edit/clear.
- Check editing existing records, prefilled values, deep links, refresh/back, and persisted expansion when relevant. Do not leak one account's state into another.
- Check loading, empty, and failed dynamic content where used. Avoid hiding failures or shifting interaction targets.
- Treat hiding as presentation, never authorization. Inspect authorization separately when changed functionality exposes data/actions.

## Accessibility and interaction

- Prefer existing accessible primitives or native `<details><summary>` for simple disclosure. Avoid redundant ARIA without demonstrated need.
- For custom disclosure, use a real button, accessible name, accurate `aria-expanded`, and appropriate optional `aria-controls` to a unique ID. Enter and Space must activate it.
- Treat disclosure, tabs, menus, and modal dialogs as different patterns; use the corresponding WAI-ARIA guidance.
- Keep hidden content out of keyboard navigation and appropriately hidden from assistive technology. `aria-hidden` alone does not prevent focus. Relocate focus safely before hiding its ancestor.
- Normally retain focus on an inline trigger after expanding and let Tab reach revealed controls. Avoid unexplained automatic focus jumps.
- For modal drawers/dialogs, check accessible name, focus entry/containment, close behavior, and restoration. Do not trap focus in ordinary nonmodal panels.
- Keep conditional fields in logical reading order near their parent. Do not mechanically add `aria-expanded` to radios; check current semantics and actual library behavior.
- Use announcements selectively for asynchronous results, not every reveal. Test assistive output where available and mark untested announcements unverified.
- Verify visible focus, touch activation, target size, zoom/reflow, and small viewports for obscured actions, trapped scrolling, and offscreen content.

## Targeted scenarios

| Scenario | Expected outcome |
| --- | --- |
| Complete common task | Main action and essential instructions discoverable without unrelated exploration. |
| Find advanced option without hint | Trigger provides credible path; option is reachable and usable. |
| Edit option, close/reopen | Effect stays understandable; intended values persist. |
| Change conditional parent | Irrelevant values follow explicit retention/clearing/submission policy; invisible requirements do not block. |
| Submit error in collapsed section | Error communicated; field reachable and visible. |
| Open/close by keyboard | Valid focus; hidden controls skipped; trigger and fields operable. |
| Compare two sections | Both consultable without unnecessary memorization. |
| Return via Back/edit saved record | State and revealed fields match record/navigation policy. |

Use existing tooling and a small high-value scenario set. Favor behavioral regression tests for draft loss, hidden validation, stale payloads, and focus. Successful build means build verification only.

For material criteria, report **passed / failed / not verified / not applicable**, evidence, and remaining action. Distinguish source inspection from runtime results. Recheck after fixes.
