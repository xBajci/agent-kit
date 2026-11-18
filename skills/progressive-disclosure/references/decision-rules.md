# Decision rules and patterns

Use task-dependent heuristics, not universal standards. Cite rule IDs when useful.

| ID | Rule | Check |
| --- | --- | --- |
| PD-01 | Prioritize the current task | Keep main actions and frequently needed controls directly accessible. An optional upload may still deserve a prominent trigger. |
| PD-02 | Preserve consequential information | Keep price implications, visibility/audience, critical errors, and consequences visible before the decision. Hide explanation only when the summary suffices. |
| PD-03 | Make the path discoverable | Use specific labels such as “Export format” or “History of changes”; keep the trigger obvious. Avoid generic “More” for unrelated capabilities. |
| PD-04 | Keep active state understandable | Retain selected filters, nondefault configuration, completion/error summaries, and a clear edit/clear path after collapse. A count alone may be insufficient. |
| PD-05 | Reveal relevant dependencies | Place simple follow-up fields near the choice. For complex branching, consider a distinct step/page and explain the relationship. |
| PD-06 | Preserve comparison and context | Allow simultaneous information access when needed. Avoid exclusive accordions or back-and-forth between dependent wizard steps. |
| PD-07 | Minimize repeated interaction cost | Consider expert workflows, defaults, remembered expansion, saved views, and direct access. Avoid extra layers on every visit. |
| PD-08 | Preserve user control and data | Define close, back, cancel, reset, and parent-choice changes. Avoid silent draft loss and hidden stale choices. |
| PD-09 | Support all input methods | Check touch, keyboard, focus, names, state announcements, and hidden elements. Avoid essential hover-only controls. |
| PD-10 | Use the simplest suitable structure | Improve grouping, copy, and hierarchy first. Prefer shallow disclosure; justify nested containers. |
| PD-11 | Distinguish progressive from staged disclosure | Use optional layers for specialized needs and steps for ordered tasks. Do not call essential content “advanced” to justify hiding it. |
| PD-12 | Match conclusions to evidence | Separate screenshots, code, runtime, and research. Infrequent use does not prove low demand; cleanliness does not prove usability. |

## Choose a pattern

| Need | Candidate | Limitation |
| --- | --- | --- |
| Short optional explanation | Inline details/summary | Do not hide instructions everyone needs. |
| Independent sections | Accordion with meaningful headings | Allow simultaneous expansion for comparison; consider expand-all for substantial optional content. |
| Peer views used one at a time | Tabs | Avoid when simultaneous comparison dominates or steps must be completed sequentially. |
| Specialized configuration | Advanced section | Summarize meaningful nondefault values after collapse. |
| Simple follow-up answer | Conditional field | Keep relationship/DOM order clear; define inactive validation and payload behavior. |
| Many filtering options | Filter panel/drawer | Retain useful common filters and applied-value summaries near results. |
| Detail alongside list context | Nonmodal side panel | Preserve selection/context; support deep links when useful. |
| Focused interrupting decision | Modal dialog | Apply dialog behavior; avoid modals for ordinary reading. |
| Actions on selected records | Contextual toolbar | Make selection discoverable and scope/count explicit. |
| Ordered process with limited dependencies | Wizard | Preserve answers, show progress, enable back/edit, surface consequences before submission. |

## Worked decisions

- Filters: reveal infrequent criteria on demand, then expose applied values such as “Status: unresolved” with removal controls. Keep the panel trigger visible.
- Export: show format and scope directly if normally required. Place delimiter/encoding under a named section only if defaults suit typical users; summarize changed values.
- Form: keep “Add photos” visible when photos support the main task even if optional. Reveal upload controls after activation without burying the capability.
- Daily operations: keep “Reply” or “Change status” visible when central; consider overflow for rare ancillary actions.
- Landing page: keep offer, decision-critical conditions, and CTA readable. Use details for optional technical explanation; avoid hiding the entire value proposition behind tabs.
- Comparison: prefer side-by-side facts or simultaneously open sections over a sequence requiring memory.

## Evaluate

Ask whether a user can identify the next action, predict a trigger's contents, understand state after closing, recover from mistakes, and complete common and specialized tasks. Treat predicted answers as hypotheses until observed.

Measure representative tasks for new and frequent users: completion, time, errors, discovery without hints, and state comprehension. High expansion can suggest promoting content; low expansion can mean lack of need or poor discovery.
