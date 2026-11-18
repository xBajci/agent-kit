---
name: setup
description: "Set up the xbajci plugin: offer to install the recommended companions (Matt Pocock's skills, episodic-memory, taste-skill, browser-harness), install the agents for Codex, and prepare the current repo for local-markdown tickets."
disable-model-invocation: true
---

# Setup

Ask the user one question at a time, each with numbered options and your
recommendation first. Never install anything without a yes.

## 1. Which client

Detect the client you run in. Claude Code: use `claude plugin …` commands.
Codex: use `codex plugin …` commands. Run the commands through the shell.

## 2. Companions

List what is installed: `claude plugin list --json` (Claude) or
`codex plugin list` (Codex). `codex plugin list` also lists plugins that are
only available; treat a companion as installed only if its line says
installed. For each companion below that is missing, ask
"Install <name>? <why>" and on a yes run its commands.

| Companion | Why | Claude | Codex |
|---|---|---|---|
| `mattpocock-skills` | The base workflow: grill, to-spec, to-tickets, tdd, code-review. `ship-spec` needs it. | `claude plugin marketplace add anthropics/claude-plugins-official` then `claude plugin install mattpocock-skills@claude-plugins-official` | `codex plugin marketplace add anthropics/claude-plugins-official` then `codex plugin add mattpocock-skills@claude-plugins-official` |
| `episodic-memory` | Searchable history of past sessions. `memory-review` reads it. | `claude plugin marketplace add obra/superpowers-marketplace` then `claude plugin install episodic-memory@superpowers-marketplace` | `codex plugin marketplace add obra/superpowers-marketplace` then `codex plugin add episodic-memory@superpowers-marketplace` |
| `taste-skill` | Art direction for UI work instead of generic AI pages. | `claude plugin marketplace add Leonxlnx/taste-skill` then `claude plugin install taste-skill@taste-skill` | `codex plugin marketplace add Leonxlnx/taste-skill` then `codex plugin add taste-skill@taste-skill` |
| browser-harness | Fast browser verification in one script. `verifier` prefers it. | Follow https://github.com/browser-use/browser-harness/blob/main/install.md | same |

Skip a marketplace add when `claude plugin marketplace list` / `codex plugin
marketplace list` already shows it. After browser-harness, point the user to
`docs/browser-tools.md` in this plugin.

If a command fails, show its output and move on to the next companion.

## 3. Agents for Codex

Codex does not load agents from plugins. In Codex only, ask "Install the 10
xbajci agents into ~/.codex/agents/?" On a yes, copy `codex/agents/*.toml` from
this plugin's directory into `~/.codex/agents/`. Before copying, list any file
that already exists there with different content and ask before overwriting it.
Tell the user to re-run setup after updating the plugin, to refresh
`~/.codex/agents/`.

## 4. This repo

Skip this part outside a git repository.

1. If `docs/agents/issue-tracker.md` is missing, tell the user to run
   `/setup-matt-pocock-skills` and to pick **Local markdown** unless the repo
   uses GitHub or GitLab issues.
2. If `.gitignore` ignores `.scratch/`, ask to remove that line. Explain:
   implementers work in worktrees, and a worktree only contains tracked files.

## Report

One line per item: installed / already present / skipped / failed (with the
error).
