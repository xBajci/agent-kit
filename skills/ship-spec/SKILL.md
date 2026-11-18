---
name: ship-spec
description: "Implement a spec and its tickets end to end: optional BDD, one implementer per ticket in its own worktree, verification and security review per ticket, escalation, code review and finish-implementation. Use after /to-spec and /to-tickets."
disable-model-invocation: true
---

# Ship a spec

Based on Matt Pocock's `implement-spec` (MIT, see `LICENSE-implement-spec`),
with per-ticket verification, security review, escalation, optional BDD and a
finish step.

You have been given a spec. It should have tickets that describe how to
implement it. The issue tracker should be configured; if not, tell the user to
run `/setup-matt-pocock-skills`.

The goal is the whole spec implemented on one **integration branch**, verified,
documented and merged after the user agrees.

The tickets are a **task graph** with blocking relationships. There is always a
**frontier** of tickets that are ready to grab.

Start every subagent with a fresh context window. Communicate through context
pointers: the spec, tickets, research notes and commits. Do not duplicate what
a pointer already gives. Run implementer subagents in the background where
possible.

Agents named here come from the `xbajci` plugin (`xbajci:implementer`,
`xbajci:verifier`, …). In Codex use the agent roles with the same names.

## Steps

1. **Read** the spec and tickets to understand the task graph.

2. **BDD.** If the repo has a BDD rule (for example `docs/tests/bdd.md`, or
   AGENTS.md says every feature needs `.feature` files), do BDD without asking.
   Otherwise ask the user one question: "Do you want BDD scenarios and E2E tests
   for this feature?" If yes:
   - add ticket `00-bdd-scenarios` in the tracker (a deliberate exception to
     "numbered from `01`", so it sorts first); its job is to write `.feature`
     files from the spec's user stories with the `bdd-gherkin` skill;
   - add `00` to the `Blocked by` line of every other ticket; where that line
     says `None (can start immediately)`, replace it with `00` instead of
     appending;
   - commit ticket 00 and the `Blocked by` edits before step 4, so the
     integration branch and every worktree contain them;
   - tell each implementer which scenario its ticket covers; it writes that
     scenario's end-to-end test first, as the highest `tdd` seam.

3. **(Optional) Explore.** Spawn an exploration subagent for codebase or
   external research the tickets need. It saves Markdown notes in a directory
   outside the repo that every later subagent can read.

4. **Integration branch.** Create it. If the tracker closes work through PRs,
   or the user asks for one, open a draft PR after the first merge in step 7
   (a branch with no commits ahead of main can't open one), marked as closing
   the spec and tickets.

5. **Implement the frontier.** For each ready ticket, spawn a fresh
   `implementer` in its own worktree on its own branch based on the integration
   branch. The brief points to the spec, the ticket, the notes and, if BDD is on,
   the scenario. The implementer uses `tdd` and merges the integration branch
   tip into its branch before reporting.

6. **Gate each ticket.** When an implementer reports:
   - spawn a fresh `verifier` on that branch with the ticket's acceptance
     criteria (and the E2E test if BDD is on);
   - if the change touches authentication, authorization, permissions, secrets,
     untrusted input, uploads, execution or tenant/account isolation, spawn
     `security-auditor` on the diff;
   - only a TRUE verdict and no blocking security finding let the ticket pass.

7. **Merge or escalate.**
   - Passed: merge the ticket branch into the integration branch with a merger
     subagent, and mark the ticket done in the tracker. Local tracker: set the
     ticket's status line to `Status: resolved` (Matt's triage labels have no
     done role; `resolved` is the status his local tracker uses for finished
     tickets). GitHub or GitLab: leave the issue open; the PR's closing
     keywords or `finish-implementation` close it.
   - Failed once: send the failure to the same implementer (attempt 2).
   - Failed twice: spawn `advisor` yourself with both failed attempts and the
     ticket. Then spawn a fresh `implementer` with model `fable` (in Codex, the
     strongest available model); its brief lists both failed attempts and the
     advisor's verdict. If it fails too, stop and report to the user.
   - Jev: if `TYPESAFE_API_KEY` is set, run `jev route` before a ticket and
     `jev next` after each attempt, and follow its lane and model instead of
     the rule above. A failed check or a missing security review still blocks,
     whatever Jev says. Without the key, use the rule above.

8. **Repeat** step 5 whenever a merge changes the frontier, for maximum
   concurrency.

9. **Review.** When every ticket is done, run Matt's `code-review` on the
   integration branch. Fix every issue it raises in one fresh `implementer`,
   then run step 6 once more on the integration branch.

10. **Finish.** Run the `finish-implementation` skill on the integration branch.
    It verifies, distills the plan into docs, deletes the plan and asks the user
    before merging into `main`, or, if a PR exists, before marking it ready for
    review.

11. **Clean up.** Only after step 10: delete every implementer worktree and
    ticket branch. Leave the integration branch and any PR as step 10 left them.

## Report

```
Spec: <path or issue>
Tickets: <done>/<total>, escalated: <list or none>
Security reviews: <tickets reviewed, open findings>
Code review: <issues found → fixed>
Finish: <finish-implementation report>
```
