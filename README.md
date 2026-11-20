# agent-kit

A plugin for Claude Code and Codex that adds agents, skills and hooks for
shipping a spec ticket by ticket, with verification, security review and
escalation on every ticket.

The plugin is named `xbajci` and is published through the `agent-kit`
marketplace. It builds on [Matt Pocock's skills](https://github.com/mattpocock/skills).

## Features

- **Per-ticket gates.** A separate agent verifies each ticket. Changes to
  authentication, permissions, secrets, input handling or isolation also go
  through a security auditor before they merge.
- **Escalation.** After two failed attempts, an advisor reviews the attempts
  and a fresh implementer retries on a stronger model.
- **Finish step.** When a feature is done, the spec and tickets are distilled
  into the project's docs (glossary, ADRs, coding standards) and then deleted.
- **Optional BDD.** Gherkin scenarios and end-to-end tests are written before
  the code.
- **Security audits.** A coverage-tracked audit workflow with validators.
- **Browser guard.** A hook stops agents from attaching to or killing your own
  browser.

## Requirements

- Claude Code or Codex CLI
- Python 3.11+ with PyYAML (only for `scripts/build-agents`)
- `jq` (for the hooks)
- [Matt Pocock's skills](https://github.com/mattpocock/skills), for the
  workflow (`setup` offers to install them)

## Installation

Claude Code:

```bash
claude plugin marketplace add xBajci/agent-kit
claude plugin install xbajci@agent-kit
```

Codex:

```bash
codex plugin marketplace add xBajci/agent-kit
codex plugin add xbajci@agent-kit
```

Then run the setup skill: `/xbajci:setup` in Claude Code, or pick
`xbajci:setup` from the skill list (`$` in the composer) in Codex. Setup:

- offers to install the recommended companion plugins, one at a time;
- installs the agents for Codex into `~/.codex/agents/`;
- prepares the current repo for local Markdown tickets in `.scratch/`.

Run setup again after a plugin update to refresh the Codex agents.

## Usage

```
/grill-with-docs       sharpen the idea                    (mattpocock-skills)
/to-spec               .scratch/<feature>/spec.md          (mattpocock-skills)
/to-tickets            .scratch/<feature>/issues/NN-*.md   (mattpocock-skills)
/xbajci:ship-spec
  ├─ BDD? (not asked if the repo requires BDD)
  ├─ per ticket: implementer in its own worktree, test-first
  ├─ per ticket: verifier, and security-auditor for sensitive changes
  ├─ 2 failures → advisor + stronger model (or Jev, with a key)
  ├─ merge into the integration branch + code review
  ├─ finish-implementation: verify, update docs, delete plan, ask to merge
  └─ delete worktrees
```

Tickets are Markdown files in `.scratch/`. Commit them: implementers work in
git worktrees, and a worktree only contains tracked files.

`finish-implementation` also works on its own, for example after `/implement`.

## Contents

### Agents

| Agent | Role |
|---|---|
| `advisor` | Second opinion on an approach, design or completion evidence |
| `debugger` | Reproduces a failure and proves its cause |
| `doc-writer` | Writes docs and distills finished plans |
| `implementer` | Implements one ticket test-first |
| `jev` | Relays routing decisions to Jev (optional) |
| `researcher` | Verifies external APIs, versions and sources |
| `reviewer` | Reviews a diff for correctness and project conventions |
| `scout` | Finds definitions, usages and configuration |
| `security-auditor` | Reviews trust-boundary changes and runs audits |
| `verifier` | Checks completion claims with real test, build or browser evidence |

### Skills

| Skill | Purpose |
|---|---|
| `setup` | Installs companions, Codex agents and repo prerequisites |
| `ship-spec` | Implements a spec and its tickets end to end |
| `finish-implementation` | Verifies, updates docs, deletes the plan, asks to merge |
| `security-audit` | Security guidance and full audits |
| `bdd-gherkin` | Writes and reviews Gherkin scenarios |
| `progressive-disclosure` | Designs and audits UI that reveals detail on demand |
| `memory-review` | Turns session history into long-term agent memory |

### Hooks (Claude Code only)

| Hook | Event | What it does |
|---|---|---|
| `session-rules.sh` | SessionStart | Adds rules: reply in Czech or English, ask one question at a time |
| `memory-publish.sh` | SessionStart | After a plugin update, points the memory block at the new version (`publish.py --if-stale`). Silent; does nothing before the first memory-review publish |
| `deny-browser-attach.sh` | PreToolUse (Bash) | Blocks browser-attach flags and kill commands aimed at a real browser |

Codex does not load the hooks.

## Configuration

**Session rules.** To change or drop them, edit `hooks/session-rules.sh` or
remove the `SessionStart` entry from `hooks/hooks.json` in a fork.

**Jev.** `bin/jev` routes tickets through [TypeSafe](https://typesafe.ai)'s Jev
model when `TYPESAFE_API_KEY` is set. It sends the task, a diff summary and the
agent's report to `api.typesafe.ai`. Without the key, `jev` returns
`unavailable` and `ship-spec` uses its built-in escalation rule.

**memory-review.** Writes to `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md`. It
asks before it changes them. The memory directory defaults to `~/.agents/memory`
(`MEMORY_REVIEW_DIR`). If `~/.codex/AGENTS.md` is a symlink to a shared file
such as `~/.agents/AGENTS.md`, and `CLAUDE.md` imports that file with
`@~/.agents/AGENTS.md`, the memory is written once into the shared file and
removed from `CLAUDE.md`. After a plugin update, the `memory-publish.sh` hook
refreshes the block on the next Claude session start.

## Recommended companions

| Plugin | Used for |
|---|---|
| [mattpocock-skills](https://github.com/mattpocock/skills) | Spec, tickets, TDD and code review |
| [episodic-memory](https://github.com/obra/episodic-memory) | Session history for `memory-review` |
| [taste-skill](https://github.com/Leonxlnx/taste-skill) | UI art direction |
| [postgres-best-practices](https://github.com/neondatabase/postgres-skills) | Postgres schema, index and query rules |
| [browser-harness](https://github.com/browser-use/browser-harness) | Browser verification, see [docs/browser-tools.md](docs/browser-tools.md) |

## Development

Agent sources live in `src/agents/`, with shared rules in `src/runtime.md`.
Do not edit `agents/` or `codex/agents/` by hand; regenerate them.

```bash
scripts/build-agents                  # regenerate agents/ and codex/agents/
scripts/build-agents --check          # fail if generated files are stale
python3 scripts/test_build_agents.py
scripts/test_jev.sh
scripts/test_hooks.sh
claude plugin validate .
```

## Credits

`ship-spec` is based on Matt Pocock's `implement-spec`, MIT licensed. See
`skills/ship-spec/LICENSE-implement-spec`.

## License

[MIT](LICENSE)
