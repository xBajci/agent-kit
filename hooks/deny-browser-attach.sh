#!/usr/bin/env bash
# PreToolUse (Bash) guard:
#   1. never attach a browser tool to the user's own browser or profile
#      (chrome-devtools-mcp: --autoConnect --browserUrl --wsEndpoint;
#       @playwright/mcp: --cdp-endpoint --extension)
#   2. never kill the user's own browser. A throwaway automation instance
#      (a --user-data-dir under ~/.claude/chrome-automation) stays killable.
# See docs/browser-tools.md.
cmd=$(jq -r '.tool_input.command // empty')
[ -z "$cmd" ] && exit 0

deny() {
  jq -n --arg r "$1" '{hookSpecificOutput:{hookEventName:"PreToolUse",permissionDecision:"deny",permissionDecisionReason:$r}}'
  exit 0
}

if printf '%s' "$cmd" | grep -Eq -- "--(autoConnect|browserUrl|wsEndpoint|cdp-endpoint|extension)([[:space:]=\"']|$)"; then
  deny "Browser-attach flag: this connects a tool to the user's own browser or profile. Launch your own Chrome with a throwaway --user-data-dir instead (docs/browser-tools.md in the xbajci plugin)."
fi

if printf '%s' "$cmd" | grep -Eq '(^|[;&|[:space:]])(pkill|killall|kill)([[:space:]]|$)'; then
  if printf '%s' "$cmd" | grep -Eiq 'chrome|chromium|brave|firefox|safari|msedge|microsoft edge|opera|vivaldi' \
     && ! printf '%s' "$cmd" | grep -q 'chrome-automation'; then
    deny "Kill aimed at the user's own browser. Kill only your throwaway instance: pkill -f \"user-data-dir=\$HOME/.claude/chrome-automation\"."
  fi
fi

exit 0
