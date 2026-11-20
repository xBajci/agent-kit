#!/usr/bin/env python3
"""Session digest for the memory-review skill. Reads the episodic-memory
index (Claude Code, Codex, ...) and manages the shared memory folder.

  digest.py --init             create MEM (templates, .gitignore, git) if missing
  digest.py                    sync, then print digest of new exchanges
  digest.py --no-sync          same, without `episodic-memory sync`
  digest.py --since ISO        override start (ignores state)
  digest.py --session ARCHIVE  print one whole session (user + agent text, no tool output)
  digest.py --finish           publish to agents, git commit MEM, save watermark
  digest.py --finish --no-publish
  digest.py --project-key PATH print the project key for a folder

Env: MEMORY_REVIEW_DIR (default ~/.agents/memory),
     EPISODIC_MEMORY_DB (default ~/.config/superpowers/conversation-index/db.sqlite)
"""
import argparse, glob, json, os, re, signal, sqlite3, subprocess, sys, time
from collections import OrderedDict
from datetime import datetime, timedelta, timezone

HOME = os.path.expanduser("~")
HERE = os.path.dirname(os.path.abspath(__file__))
MEM = os.path.expanduser(os.environ.get("MEMORY_REVIEW_DIR", "~/.agents/memory"))
DB = os.path.expanduser(os.environ.get(
    "EPISODIC_MEMORY_DB", "~/.config/superpowers/conversation-index/db.sqlite"))
STATE = os.path.join(MEM, ".state.json")

MAX_DAYS = 7            # never look further back than this
FIRST_RUN_HOURS = 24    # window for the very first run
USER_CAP = 1500         # chars per user message in the digest
ASSIST_CAP = 300        # chars per agent message in the digest
SESSION_CAP = 16000     # chars per session; middle is cut, head + tail kept
HEAD_KEEP = 3           # exchanges always kept from the start of a long session

# Sessions that are this skill's own runs, or not a human conversation at all.
# Match only real invocations, never the published memory block or docs.
SKIP_SESSION = re.compile(
    r"Base directory for this skill: \S*/memory-review\b|<command-name>/?memory-review<|"
    r"(^|\s)[/$]memory-review\b|"
    r"since your last approval assessment|You are an approval reviewer", re.I)
MEM_BLOCK = re.compile(r"<!-- BEGIN memory-review -->.*?<!-- END memory-review -->", re.S)
# Harness text injected into user turns (not written by the user).
NOISE_TAGS = ("system-reminder", "task-notification", "environment_context", "INSTRUCTIONS",
              "user_instructions", "local-command-stdout", "local-command-caveat",
              "command-message", "command-args", "turn_aborted", "subagent_notification", "agent-message")
NOISE = re.compile(r"<(%s)\b[^>]*>.*?</\1>" % "|".join(NOISE_TAGS), re.S)
AGENTS_HDR = re.compile(r"^# AGENTS\.md instructions for [^\n]*\n?")

SECRET = re.compile(
    r"(sk-[A-Za-z0-9_\-]{16,}|gh[pousr]_[A-Za-z0-9]{20,}|xox[abpr]-[A-Za-z0-9\-]{10,}"
    r"|AKIA[0-9A-Z]{16}|eyJ[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"
    r"|[A-Fa-f0-9]{40,}|(?=[A-Za-z0-9+/]*\d)(?=[A-Za-z0-9+/]*[A-Z])[A-Za-z0-9+/]{48,}={0,2})")
SECRET_KV = re.compile(
    r"((?:token|key|api[_-]?key|secret|password|passwd|pwd|auth|signature|sig|code)=)[^&\s\"'<>]{6,}", re.I)
URL_CREDS = re.compile(r"(\w+://[^/\s:@]+:)[^@\s]+@")

TEMPLATES = {
    "USER.md": "# User\n## Profile\n## Preferences\n## Tools and services\n## Corrections\n",
    "SKILL-IDEAS.md": "# Skill ideas\n",
    "projects/general.md": "# general\nPaths: home folder and scratch folders\n"
                           "## Facts\n## Decisions\n## Gotchas\n## Conventions\n",
    ".gitignore": ".state.json\n",
}


def redact(s):
    s = SECRET.sub("[REDACTED]", s or "")
    s = SECRET_KV.sub(r"\1[REDACTED]", s)
    return URL_CREDS.sub(r"\1[REDACTED]@", s)


def clean_user(s):
    t = (s or "").lstrip()
    if t.startswith("Base directory for this skill:") or "[Subagent hand-back]" in t[:600] \
            or t.startswith("Another Claude session sent a message"):
        return ""  # a loaded skill body or another agent's report, not the user's words
    s = NOISE.sub("", MEM_BLOCK.sub("", s or ""))
    s = AGENTS_HDR.sub("", s)
    return s.strip()


def clip(s, n):
    s = re.sub(r"\s+", " ", redact(s)).strip()
    return s if len(s) <= n else s[:n] + " …[cut]"


_key_cache = {}


def project_key(cwd):
    """Folder name of the MAIN git repo (worktrees map to their main repo).
    Home or scratch folder -> 'general'."""
    if cwd in _key_cache:
        return _key_cache[cwd]
    key = None
    if not cwd or os.path.realpath(cwd) == os.path.realpath(HOME) or "scratch-workspaces" in cwd:
        key = "general"
    elif os.path.isdir(cwd):
        try:
            out = subprocess.run(
                ["git", "-C", cwd, "rev-parse", "--path-format=absolute", "--git-common-dir"],
                capture_output=True, text=True, timeout=5)
            gd = out.stdout.strip()
            if out.returncode == 0 and gd:
                key = os.path.basename(os.path.dirname(gd.rstrip("/")))
        except Exception:
            pass
    if not key:  # folder gone or not a repo: guess from the path
        m = re.search(r"/workspaces/([^/]+)/[^/]+/?$", cwd)
        key = m.group(1) if m else os.path.basename(cwd.rstrip("/")) or "general"
    key = re.sub(r"[^A-Za-z0-9._-]+", "-", key).strip("-").lower() or "general"
    _key_cache[cwd] = key
    return key


def load_state():
    try:
        with open(STATE) as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(st):
    if not os.path.isdir(MEM):
        sys.exit(f"{MEM} missing: run digest.py --init first.")
    with open(STATE, "w") as f:
        json.dump(st, f, indent=2)


def git(*a):
    return subprocess.run(["git", "-C", MEM, *a], capture_output=True, text=True)


def init():
    created = []
    for rel, body in TEMPLATES.items():
        p = os.path.join(MEM, rel)
        if not os.path.exists(p):
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w") as f:
                f.write(body)
            created.append(rel)
    if not os.path.isdir(os.path.join(MEM, ".git")):
        git("init", "-q")
        created.append(".git")
    print(f"MEM = {MEM}\n" + (f"created: {', '.join(created)}" if created else "already set up"))


def find_cli():
    on_path = subprocess.run(["which", "episodic-memory"], capture_output=True, text=True).stdout.strip()
    if on_path:
        return [on_path]
    pats = [os.path.join(HOME, p) for p in (
        ".claude/plugins/cache/*/episodic-memory/*/cli/episodic-memory",
        ".codex/plugins/cache/*/episodic-memory/*/cli/episodic-memory",
        ".codex/plugins/*/episodic-memory/*/cli/episodic-memory")]
    hits = [h for p in pats for h in glob.glob(p)]

    def ver(p):
        v = p.split("/episodic-memory/")[1].split("/")[0]
        return [int(x) if x.isdigit() else 0 for x in re.split(r"[.\-]", v)]
    return ["node", max(hits, key=ver)] if hits else None


def sync():
    cli = find_cli()
    if not cli:
        print("WARN: episodic-memory CLI not found; skipping sync (hooks usually sync anyway).", file=sys.stderr)
        return
    try:
        r = subprocess.run(cli + ["sync"], capture_output=True, text=True, timeout=600)
        if r.returncode != 0:
            print("WARN: sync failed: " + (r.stderr or r.stdout)[-500:], file=sys.stderr)
    except subprocess.TimeoutExpired:
        print("WARN: sync timed out after 10 min; using what is indexed.", file=sys.stderr)


def iso(ms):
    return datetime.fromtimestamp(ms / 1000, timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def local(ts, fmt="%Y-%m-%d"):
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).astimezone().strftime(fmt)
    except Exception:
        return ts[:10]


def local_date(ts):
    return local(ts)


def _open(path, mode="ro"):
    con = sqlite3.connect(f"file:{path}?mode={mode}", uri=True)
    con.execute("SELECT 1 FROM exchanges LIMIT 1")
    return con


def _open_copy():
    """Read a private copy when the DB itself will not open read-only: sandboxes
    (e.g. Codex) may forbid the -shm file next to it, and a WAL DB that no other
    process holds open has no -shm, which mode=ro cannot create. Nobody else
    uses the copy, so open it read-write and let SQLite create its -shm."""
    import shutil, tempfile
    tmp = tempfile.mkdtemp(prefix="memory-review-")
    for suf in ("", "-wal"):
        if os.path.exists(DB + suf):
            shutil.copy2(DB + suf, os.path.join(tmp, "db.sqlite" + suf))
    return _open(os.path.join(tmp, "db.sqlite"), mode="rw")


def connect():
    """Read-only. Right after a sync the DB can be briefly unavailable: retry."""
    err = None
    for i in range(6):
        try:
            return _open(DB)
        except sqlite3.OperationalError as e:
            err = e
            try:
                return _open_copy()
            except Exception as e2:
                err = f"{err}; copy failed: {e2}"
            time.sleep(5)
    sys.exit(f"Cannot open {DB}: {err}")


def fmt_session(s):
    """Lines for one session; if too long, keep head + as much tail as fits."""
    lines = []
    for ts, um, am in s["ex"]:
        u = clean_user(um)
        if not u:
            continue
        lines.append(f"- [{local_date(ts)}] U: {clip(u, USER_CAP)}\n  A: {clip(am, ASSIST_CAP)}")
    if sum(map(len, lines)) <= SESSION_CAP:
        return lines, 0
    head = lines[:HEAD_KEEP]
    budget = SESSION_CAP - sum(map(len, head))
    tail = []
    for ln in reversed(lines[HEAD_KEEP:]):
        if budget - len(ln) < 0:
            break
        tail.insert(0, ln)
        budget -= len(ln)
    cut = len(lines) - len(head) - len(tail)
    return head + [f"- …[{cut} exchanges cut from the middle — read with --session]"] + tail, cut


def digest(args):
    if not os.path.isdir(MEM):
        sys.exit(f"{MEM} missing: run digest.py --init first.")
    st = load_state()
    floor_ts = (datetime.now(timezone.utc) - timedelta(days=MAX_DAYS)).strftime("%Y-%m-%dT%H:%M:%SZ")
    con = connect()

    if args.since:
        where, params = "timestamp >= ?", [max(args.since, floor_ts)]
        mode = f"since {args.since} (manual)"
    elif st.get("last_indexed_ms"):
        where, params = "last_indexed > ? AND timestamp >= ?", [st["last_indexed_ms"], floor_ts]
        mode = f"indexed after {iso(st['last_indexed_ms'])} (last run {st.get('last_run', '?')})"
    else:
        start = (datetime.now(timezone.utc) - timedelta(hours=FIRST_RUN_HOURS)).strftime("%Y-%m-%dT%H:%M:%SZ")
        where, params = "timestamp >= ?", [start]
        mode = f"first run: last {FIRST_RUN_HOURS} h (since {start})"

    rows = con.execute(
        f"""SELECT session_id, archive_path, harness, cwd, timestamp, user_message,
                   assistant_message, last_indexed
            FROM exchanges
            WHERE is_sidechain = 0 AND project != 'subagents' AND {where}
            ORDER BY timestamp""", params).fetchall()
    max_idx = max([r[7] or 0 for r in rows], default=st.get("last_indexed_ms") or int(time.time() * 1000))

    sessions = OrderedDict()
    for sid, path, harness, cwd, ts, um, am, _ in rows:
        s = sessions.setdefault(sid or path, {"path": path, "harness": harness, "cwd": cwd,
                                              "start": ts, "end": ts, "ex": []})
        s["end"] = ts
        s["ex"].append((ts, um, am))

    skipped = [k for k, s in sessions.items()
               if any(SKIP_SESSION.search(MEM_BLOCK.sub("", u or "")) for _, u, _ in s["ex"])]
    for k in skipped:
        del sessions[k]

    by_project = OrderedDict()
    for k, s in sessions.items():
        by_project.setdefault(project_key(s["cwd"]), []).append(s)

    out, total, hidden, partial = [], 0, [], 0
    out.append(f"# Session digest — {mode}")
    out.append(f"{len(sessions)} sessions, {sum(len(s['ex']) for s in sessions.values())} exchanges, "
               f"{len(by_project)} projects. Skipped {len(skipped)} session(s) (memory-review runs, approval reviewers).")
    out.append("U = user (cleaned of harness text), A = agent (clipped). All times are local. "
               f"Full session: python3 {os.path.abspath(__file__)} --session <archive>\n")
    for proj, items in by_project.items():
        out.append(f"## project: {proj}")
        for s in items:
            head = [f"### {s['harness']} · {local(s['start'], '%Y-%m-%d %H:%M')} → {local(s['end'], '%Y-%m-%d %H:%M')} · {s['cwd']}",
                    f"archive: {s['path']}"]
            summ = s["path"].replace(".jsonl", "-summary.txt")
            if os.path.exists(summ):
                with open(summ, errors="replace") as f:
                    head.append("summary (may cover older parts of the session): " + clip(f.read(), 800))
            body, cut = fmt_session(s)
            partial += bool(cut)
            block = "\n".join(head + body) + "\n"
            if total + len(block) > args.max_chars:
                hidden.append(f"{proj}: {s['path']}")
                continue
            out.append(block)
            total += len(block)
    out.append("## MUST READ before finishing")
    if not (hidden or partial):
        out.append("none — every session above is complete.")
    else:
        if partial:
            out.append(f"{partial} session(s) above have a cut middle. Read each with --session.")
        if hidden:
            out.append("Not shown (budget). Read each with --session:")
            out += [f"- {h}" for h in hidden]

    st["pending_last_indexed_ms"] = max_idx
    save_state(st)
    print("\n".join(out))


def show_session(archive):
    con = connect()
    rows = con.execute("""SELECT timestamp, user_message, assistant_message FROM exchanges
                          WHERE archive_path = ? AND is_sidechain = 0 ORDER BY timestamp""",
                       (archive,)).fetchall()
    if not rows:
        sys.exit("No exchanges for that archive path (copy it exactly from the digest).")
    for ts, um, am in rows:
        u = clean_user(um)
        if u:
            print(f"--- [{local(ts, '%Y-%m-%d %H:%M')}]\nU: {redact(u)[:4000]}\nA: {clip(am, 1500)}\n")


def finish(publish=True):
    st = load_state()
    if "pending_last_indexed_ms" not in st:
        sys.exit("Nothing pending: run digest.py first.")
    if publish:
        r = subprocess.run([sys.executable, os.path.join(HERE, "publish.py")], text=True)
        if r.returncode != 0:
            sys.exit("publish.py failed; watermark NOT saved.")
    git("add", "-A")
    if git("diff", "--cached", "--quiet").returncode != 0:
        c = git("commit", "-qm", f"memory-review {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        if c.returncode != 0:
            sys.exit("git commit failed; watermark NOT saved:\n" + c.stderr)
        print("committed: " + git("log", "-1", "--format=%h %s").stdout.strip())
    else:
        print("no memory changes to commit")
    st["last_indexed_ms"] = st.pop("pending_last_indexed_ms")
    st["last_run"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    save_state(st)
    print(f"Saved. Next run starts after {iso(st['last_indexed_ms'])}.")


if __name__ == "__main__":
    signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # quiet when piped to head
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--init", action="store_true")
    ap.add_argument("--no-sync", action="store_true")
    ap.add_argument("--since")
    ap.add_argument("--max-chars", type=int, default=100000)
    ap.add_argument("--session", metavar="ARCHIVE")
    ap.add_argument("--finish", action="store_true")
    ap.add_argument("--no-publish", action="store_true")
    ap.add_argument("--project-key", metavar="PATH")
    a = ap.parse_args()
    if a.project_key:
        print(project_key(os.path.abspath(a.project_key)))
    elif a.init:
        init()
    elif a.session:
        show_session(a.session)
    elif a.finish:
        finish(publish=not a.no_publish)
    else:
        if not a.no_sync:
            sync()
        digest(a)
