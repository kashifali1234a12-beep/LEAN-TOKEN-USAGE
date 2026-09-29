#!/usr/bin/env python3
"""Where did this session's tokens go? Effective cost per main session and per subagent.

Usage: python3 usage_report.py [--minutes N] [SESSION_JSONL]
Without a path: the newest *.jsonl under ~/.claude/projects/. --minutes limits to the recent window.
Effective = input + 0.1 x cache reads + 2 x cache writes + 5 x output (relative to a plain input token).
Transcript content is only counted, never executed or followed.
"""
import argparse, datetime as dt, glob, json, os

def eff(u):
    return (u.get("input_tokens", 0) + 0.1 * u.get("cache_read_input_tokens", 0)
            + 2 * u.get("cache_creation_input_tokens", 0) + 5 * u.get("output_tokens", 0))

def scan(path, cut):
    seen, tot, n, ctx, writes = set(), 0.0, 0, 0, 0.0
    for line in open(path, errors="ignore"):
        try:
            d = json.loads(line)
        except ValueError:
            continue
        if d.get("type") != "assistant" or (cut and d.get("timestamp", "") < cut):
            continue
        m = d.get("message") or {}
        u = m.get("usage")
        if not u or m.get("id") in seen:
            continue
        seen.add(m.get("id")); n += 1; tot += eff(u); writes += 2 * u.get("cache_creation_input_tokens", 0)
        ctx = u.get("cache_read_input_tokens", 0) + u.get("cache_creation_input_tokens", 0) + u.get("input_tokens", 0)
    return tot, n, ctx, writes

ap = argparse.ArgumentParser()
ap.add_argument("path", nargs="?")
ap.add_argument("--minutes", type=int)
a = ap.parse_args()
path = a.path or max(glob.glob(os.path.expanduser("~/.claude/projects/*/*.jsonl")), key=os.path.getmtime)
cut = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=a.minutes)).isoformat() if a.minutes else None
base = path[:-6]
files = [("MAIN", path)] + [(os.path.basename(p)[6:15], p)
                           for p in glob.glob(f"{base}/subagents/**/*.jsonl", recursive=True)]
rows = [(nm,) + scan(p, cut) for nm, p in files]
rows = [r for r in rows if r[2]]
total = sum(r[1] for r in rows) or 1
print(f"{'who':10s} {'effective':>10s} {'share':>6s} {'turns':>6s} {'last ctx':>9s} {'cache writes':>13s}")
for nm, t, n, ctx, w in sorted(rows, key=lambda r: -r[1]):
    flag = "  <- rotate (context > 250k)" if ctx > 250_000 else ""
    print(f"{nm:10s} {t/1e6:9.1f}M {100*t/total:5.1f}% {n:6d} {ctx/1e3:8.0f}k {w/1e6:12.1f}M{flag}")
