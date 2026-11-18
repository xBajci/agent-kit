---
name: finish-implementation
description: "Close out a finished feature: verify it, distill the spec and tickets into lasting docs, delete the plan and merge into main (or mark its PR ready) after the user agrees. Use at the end of ship-spec, or by hand after /implement."
---

# Finish implementation

The plan (spec and tickets) is scaffolding. When the feature works, keep what is
worth knowing in the project's docs, then remove the plan. Run this before any
worktree is deleted.

## Inputs

- The feature branch (or integration branch) and its worktree, if any.
- The plan: `.scratch/<feature>/` for a local tracker, or the spec and ticket
  issues on GitHub or GitLab. Read `docs/agents/issue-tracker.md` if it exists
  to know which.

## Steps

1. **Verify.** Spawn a fresh `verifier` on the finished branch: type check,
   lint, unit and end-to-end tests, build — the project's own commands. If the
   verdict is not TRUE, stop and report. Do not continue to step 2.

2. **Distill.** Spawn a fresh `doc-writer` with pointers to the spec, the
   tickets and the branch diff. It keeps only knowledge that passes all five
   gates:

   | Gate | Question | If no |
   |---|---|---|
   | Durability | Will this still be true in 6 months? | Skip; it is tied to the task |
   | Non-obvious | Could an agent figure it out by reading the code? | Skip; the code is the record |
   | Actionable | Would knowing it change how an agent writes code? | Skip; it is trivia |
   | Unique | Is it already in GLOSSARY.md, an ADR, coding standards, CLAUDE.md or AGENTS.md? | Skip; do not duplicate |
   | Verified | Does the code match what the plan says? | Correct it to match the code, or skip |

   Worth keeping: decisions and their reasons, domain rules not visible in code,
   gotchas found during implementation, data constraints with reasons,
   integration contracts. Skip: file paths and line numbers, task breakdowns,
   code snippets, testing checklists, ordering.

3. **Update the docs.** The same `doc-writer` writes each kept item where it
   belongs:
   - terms → `GLOSSARY.md`
   - decisions with reasons → an ADR in the project's ADR folder
   - rules for writing code → the project's coding standards
   - what the feature does for users → `docs/` or `README.md`

   It reports a short list: item → file. Commit the doc changes on the branch.

4. **Delete the local plan.** Local tracker only: `git rm -r .scratch/<feature>/`
   and commit on the branch. This touches only the branch; Git history keeps
   it. Issues on GitHub or GitLab stay open until step 6.

5. **Ask.** Show the user the verifier verdict, the doc changes and the branch.
   Ask one question:
   - If the branch has a PR: "Mark PR `<url>` ready for review?" On a yes, mark
     it ready; merge it instead only if the user asks for that. Do not merge
     into `main` locally.
   - Otherwise: "Merge `<branch>` into `main`?" Merge only after a yes.

   On a no, stop. The branch, the PR and the issues stay as they are.

6. **Close the issues.** GitHub or GitLab only, and only after a yes. With a
   PR, its closing keywords close the spec and ticket issues when it merges; do
   not close them by hand. Without a PR, close the spec issue and every ticket
   issue with a short comment pointing to the merge.

## Report

```
Verify: <verdict, failing checks if any>
Docs updated: <item → file, one per line>
Plan: <deleted .scratch/<feature>/ | closed issues #… | left to the PR | left open>
Merge: <merged into main at <sha> | PR <url> ready for review | PR merged | waiting for user | declined>
```
