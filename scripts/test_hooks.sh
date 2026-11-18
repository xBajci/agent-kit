#!/usr/bin/env bash
set -u
H="$(cd "$(dirname "$0")/.." && pwd)/hooks"
fail=0
check() { if eval "$2"; then :; else echo "FAIL: $1"; fail=1; fi; }

rules=$(echo '{}' | "$H/session-rules.sh")
check "session rules emit additionalContext" \
  "printf '%s' \"\$rules\" | jq -e '.hookSpecificOutput.additionalContext | test(\"never Slovak\")' >/dev/null"
check "session rules mention one question" \
  "printf '%s' \"\$rules\" | jq -e '.hookSpecificOutput.additionalContext | test(\"one question at a time\")' >/dev/null"

deny() { jq -n --arg c "$1" '{tool_input:{command:$c}}' | "$H/deny-browser-attach.sh"; }
check "unrelated kill allowed" "[ -z \"\$(deny 'pkill -f archiver')\" ]"
check "attach flag denied" "deny 'npx chrome-devtools-mcp --autoConnect' | jq -e '.hookSpecificOutput.permissionDecision==\"deny\"' >/dev/null"
check "real browser kill denied" "deny 'pkill -9 -f \"Google Chrome\"' | jq -e '.hookSpecificOutput.permissionDecision==\"deny\"' >/dev/null"
check "throwaway kill allowed" "[ -z \"\$(deny 'pkill -f \"user-data-dir=\$HOME/.claude/chrome-automation\"')\" ]"
check "normal command allowed" "[ -z \"\$(deny 'git status')\" ]"
check "brave kill denied" "deny 'killall \"Brave Browser\"' | jq -e '.hookSpecificOutput.permissionDecision==\"deny\"' >/dev/null"
check "no Brave in hooks" "! grep -qi brave '$H/session-rules.sh'"

[ "$fail" -eq 0 ] && echo "PASS"
exit "$fail"
