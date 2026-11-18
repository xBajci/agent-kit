# Browser tools: which one for which question

Three questions, three tools.

| The question | Tool |
|---|---|
| Does what I just built work? | [browser-harness](https://github.com/browser-use/browser-harness) |
| Why does it not work, or why is it slow? | [chrome-devtools MCP](https://github.com/ChromeDevTools/chrome-devtools-mcp) |
| How do I stop it breaking again? | `@playwright/test` committed in the repo |

## 1. browser-harness: verification while building

Verification is a checklist: you already know what to look for. One Python
block answers every question at once — does the element exist, how many items
rendered, is the console clean, did the request return 200.

- One call, not eight tool calls.
- Only the result enters the agent's context, not a snapshot per step.
- The same block runs again after a code change, so results compare.
- `js()` and coordinate clicks reach inside iframes, shadow DOM and
  cross-origin frames.

Its failure mode: the agent writes the probe, so a bad probe returns a false
green. Take a screenshot in the same block. A probe and a screenshot fail in
different ways.

## 2. chrome-devtools MCP: diagnosis

Use it when the probe is red and the cause is unknown, or when the question is
performance, weight or health: Lighthouse, performance traces with insights,
heap snapshots, network requests, console messages, emulation (viewport, touch,
colour scheme, CPU and network throttling).

## 3. @playwright/test: make it permanent

A check that lives only in a transcript is gone next week. Turn it into a
committed test. Playwright MCP's codegen can record a flow once and give back
`@playwright/test` code. Real cross-browser coverage belongs in Playwright
projects, not in an MCP server flag.

## Launch your own browser

Never attach an agent to your everyday browser or profile. Attaching needs the
remote-debugging permission dialog and exposes your logged-in sessions. Launch a
throwaway Chrome instead:

```bash
PORT=9333
DIR="$HOME/.claude/chrome-automation"
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=$PORT --user-data-dir="$DIR" \
  --no-first-run --no-default-browser-check about:blank &
curl -s "http://127.0.0.1:$PORT/json/version"   # webSocketDebuggerUrl for BU_CDP_WS
```

- The dedicated `--user-data-dir` is the whole point: it is your own instance,
  so nothing has to be granted. Do not drop it.
- Use a port other than 9222 so it can run next to a browser that already uses
  9222.
- To stop it, kill only this instance:
  `pkill -f "user-data-dir=$HOME/.claude/chrome-automation"`.
- The trade-off: no logged-in sessions. For authenticated work use
  browser-harness's cloud profiles instead of your real browser.

The plugin's `deny-browser-attach` hook blocks the attach flags
(`--autoConnect`, `--browserUrl`, `--wsEndpoint`, `--cdp-endpoint`,
`--extension`) and kill commands aimed at your own browser.
