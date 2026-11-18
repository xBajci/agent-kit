#!/usr/bin/env bash
# SessionStart: always-on rules a plugin cannot ship as CLAUDE.md.
cat >/dev/null
rules='Rules from the xbajci plugin:
- Reply in the language of the user'"'"'s message: Czech or English, never Slovak.
- Ask the user one question at a time, with numbered options and your recommendation first. This also applies inside skills that ask several questions per round, such as Matt Pocock'"'"'s grilling skills.'
jq -n --arg c "$rules" '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$c}}'
