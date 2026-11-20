#!/usr/bin/env bash
# SessionStart: after a plugin update, point the memory block at this version's
# digest.py. The cache path holds the version, and the old one is deleted later.
cat >/dev/null
# Quiet: SessionStart stdout would become session context. Never block a session.
python3 "${CLAUDE_PLUGIN_ROOT}/skills/memory-review/scripts/publish.py" --if-stale >/dev/null 2>&1 || true
exit 0
