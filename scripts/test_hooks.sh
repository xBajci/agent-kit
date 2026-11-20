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

# memory-publish: fake HOME and plugin root, so real files stay untouched.
T=$(mktemp -d)
mkdir -p "$T/home/.agents/memory" "$T/home/.claude" "$T/home/.codex" "$T/root/skills/memory-review/scripts"
cp "$H/../skills/memory-review/scripts/publish.py" "$T/root/skills/memory-review/scripts/"
printf '# User\n- pref\n' > "$T/home/.agents/memory/USER.md"
printf '# codex\n' > "$T/home/.codex/AGENTS.md"
pub() { echo '{}' | HOME="$T/home" CLAUDE_PLUGIN_ROOT="$T/root" "$H/memory-publish.sh"; }
out=$(pub)
check "memory-publish prints nothing" "[ -z \"\$out\" ]"
check "memory-publish skips files without a block" "! grep -q 'BEGIN memory-review' '$T/home/.codex/AGENTS.md'"
printf '<!-- BEGIN memory-review -->\nold/0.1.0/digest.py\n<!-- END memory-review -->\n' >> "$T/home/.codex/AGENTS.md"
pub >/dev/null
check "memory-publish rewrites a stale block" "grep -q '$T/root/skills/memory-review/scripts/digest.py\|root/skills/memory-review/scripts/digest.py' '$T/home/.codex/AGENTS.md' && ! grep -q 'old/0.1.0' '$T/home/.codex/AGENTS.md'"
before=$(stat -f %m "$T/home/.codex/AGENTS.md" 2>/dev/null || stat -c %Y "$T/home/.codex/AGENTS.md")
sleep 1; pub >/dev/null
after=$(stat -f %m "$T/home/.codex/AGENTS.md" 2>/dev/null || stat -c %Y "$T/home/.codex/AGENTS.md")
check "memory-publish leaves a current block alone" "[ '$before' = '$after' ]"
rm -rf "$T"

[ "$fail" -eq 0 ] && echo "PASS"
exit "$fail"
