# Lean tokens (for Codex)

Apply these rules whenever work runs long or uses several agents. The measurement script referenced below is Claude-Code-specific; the rules are not.

# Lean tokens: same speed, same quality, far less usage

Proven on a real multi-day, multi-agent software build: usage per active hour fell ~86% with no quality or pace loss. The cost model
behind every rule: each step RE-READS the whole context (cache read ~0.1x), a context that sat idle past the cache
lifetime is RE-WRITTEN at ~2x, and output costs ~5x. So cost ~ context size x number of steps, and idle big
contexts are the most expensive thing there is. Never lower the model or effort to save tokens unless the user
asks: quality stays fixed; only waste goes.

## 0. Measure before cutting
Run `python3 ~/.claude/skills/lean-tokens/scripts/usage_report.py --minutes 90` (Claude Code transcripts) (whole session: drop the flag).
It lists effective cost per main session and per subagent, last context size, and cache rewrites, and flags any
agent over 250k context. Cut what the numbers show, not what feels expensive. Re-run after a few hours to verify.

## 1. Subagents: fresh and small (the biggest lever, typically 50-80% of spend)
- One FRESH agent per phase/task. Never keep a worker across phases "because it knows the context".
- Rotate at ~250k context even mid-task: the agent writes a <= 50-line handoff in ONE Write call (state, heads,
  done/open, gotchas, exact next step) and stops; a new agent starts from that file.
- Never resume/SendMessage an agent whose context is large and has been idle: the resume re-writes everything
  at 2x. Retire it with the one-call handoff instead. Small fresh agents are cheap to resume after outages.
- Tell every builder: commit working increments often (a stall or outage then loses nothing).

## 2. Waiting costs tokens - wait in one step
- Long runs (test suites, sweeps, builds): ONE blocking call or a background run with notification. No
  "check again" loops, no sleep-poll turns, no status peeks between notifications.
- Save output to a file and read only the tail/summary (`tail -3`, `grep -E "passed|failed"`). If a tool prints
  no summary line, count failures (`-rfE`) - never trust an empty tail as a pass.

## 3. Reports are re-read forever - keep them short
- Every agent's final reply <= 15 lines (verdict, one line per serious finding, file path). Details go in a file
  (use .txt if report .md files are blocked for subagents).
- Your own updates to the user: short, only when something finishes or needs a decision.

## 4. Prompts that prevent wasted work
- Give each agent the exact files/paths, the review report path, and the gotchas already learned (env quirks,
  ports, known false failures) so it doesn't rediscover them.
- Combine small related jobs in one agent (e.g. verify last round's fixes + review the next phase together).
- Standing instructions for every agent: short tool outputs, batch independent calls, no polling, handoff at
  ~250k, report <= 15 lines.

## 5. Stop repeat rounds at the root
If a review loop fails 3+ rounds on the same CLASS of bug (e.g. parsing free text with ever more patterns),
change the design (allow-list / structural rule / fail-safe default) instead of patching instances. Each extra
round costs a full build + review.

## 6. Read narrow, rotate early, relay paths
- Agents read ONLY what their task needs: the project rules file, the (short) decision log, their own
  phase/section of the big plan (grep the heading, read that range), and the threat models of any phase they
  touch — never the whole multi-thousand-line plan. A fresh agent otherwise starts at ~100k+ context.
- Rotate builders at ~150k context (one-call handoff, fresh agent), not 250k: every step stays cheap.
- Blocking waits: an agent waits for its long run in ONE blocking call (tool timeout permitting) instead of
  backgrounding it and stopping — each interim "stopped/waiting" notification wakes the coordinator, and every
  wake-up re-reads the coordinator's whole context even when it does nothing.
- Relay PATHS, not content: reviewers write their own report file; the coordinator passes the path to the
  builder instead of rewriting findings into messages or files (output costs ~5x, and the builder then reads
  the reviewer's exact words).

## 7. Main session hygiene
- Batch independent tool calls in one step; avoid re-reading files already seen; grep/sed ranges, not whole files.
- Don't narrate or poll; act on notifications.
- Machine limits (memory/CPU) slow runs, and slow runs mean more waiting turns: keep heavy jobs to what fits.

## Checklist when usage is burning
1. Run the report. 2. Any agent > 250k? Retire it via one-call handoff, start fresh. 3. Anyone polling? Stop.
4. Reports long? Cap them. 5. Same failure class 3+ rounds? Change the design. 6. Re-measure in 1-2 hours.
