#!/usr/bin/env bash
set -u
HERE="$(cd "$(dirname "$0")/.." && pwd)"
fail=0

out=$(echo '{"task":"add a button"}' | env -u TYPESAFE_API_KEY "$HERE/bin/jev" route 2>/dev/null)
code=$?
[ "$code" -eq 0 ] || { echo "FAIL: exit $code without key"; fail=1; }
echo "$out" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert "unavailable" in d, d' \
  || { echo "FAIL: no unavailable field: $out"; fail=1; }

grep -q '"ESCALATE": "fable"' "$HERE/bin/jev" || { echo "FAIL: ESCALATE model is not fable"; fail=1; }
grep -q 'implementer-escalated' "$HERE/bin/jev" && { echo "FAIL: implementer-escalated still referenced"; fail=1; }

[ "$fail" -eq 0 ] && echo "PASS"
exit "$fail"
