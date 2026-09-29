"""Generates the README charts (pure Python, no dependencies). Numbers: measured on one real multi-day,
multi-agent Claude Code build (effective tokens: input + 0.1x cache read + 2x cache write + 5x output)."""
FONT = "Inter,Segoe UI,Helvetica Neue,Helvetica,Arial,sans-serif"

def hexrgb(h):
    h = h.lstrip('#'); return [int(h[i:i + 2], 16) for i in (0, 2, 4)]

def mix(h, f):
    return '#%02x%02x%02x' % tuple(max(0, min(255, int(c * f))) for c in hexrgb(h))

def defs(colors):
    out = ['<filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="8" result="b"/>'
           '<feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
           '<filter id="soft" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="10"/></filter>',
           '<radialGradient id="bg" cx="30%" cy="10%" r="100%"><stop offset="0" stop-color="#312e81"/>'
           '<stop offset="0.45" stop-color="#111827"/><stop offset="1" stop-color="#030712"/></radialGradient>',
           '<linearGradient id="gloss" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
           '<stop offset="0.28" stop-color="#fff" stop-opacity="0.35"/><stop offset="0.42" stop-color="#fff" stop-opacity="0"/></linearGradient>']
    for c in colors:
        k = c[1:]
        out.append(f'<linearGradient id="side{k}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{mix(c, .55)}"/>'
                   f'<stop offset="0.35" stop-color="{mix(c, 1.15)}"/><stop offset="0.7" stop-color="{c}"/>'
                   f'<stop offset="1" stop-color="{mix(c, .45)}"/></linearGradient>')
        out.append(f'<radialGradient id="top{k}" cx="40%" cy="40%" r="70%"><stop offset="0" stop-color="{mix(c, 1.6)}"/>'
                   f'<stop offset="1" stop-color="{mix(c, 1.05)}"/></radialGradient>')
    return '<defs>' + ''.join(out) + '</defs>'

def cylinder(cx, base, r, h, c):
    """glossy 3D cylinder with floor shadow"""
    k, ry, top = c[1:], r * 0.32, base - h
    return (f'<ellipse cx="{cx + 8}" cy="{base + 6}" rx="{r * 1.25}" ry="{ry * 1.1}" fill="#000" opacity="0.45" filter="url(#soft)"/>'
            f'<path d="M{cx - r},{top} L{cx - r},{base} A{r},{ry} 0 0 0 {cx + r},{base} L{cx + r},{top} Z" fill="url(#side{k})"/>'
            f'<path d="M{cx - r},{top} L{cx - r},{base} A{r},{ry} 0 0 0 {cx + r},{base} L{cx + r},{top} Z" fill="url(#gloss)"/>'
            f'<ellipse cx="{cx}" cy="{top}" rx="{r}" ry="{ry}" fill="url(#top{k})"/>'
            f'<ellipse cx="{cx}" cy="{top}" rx="{r}" ry="{ry}" fill="none" stroke="{mix(c, 1.8)}" stroke-opacity="0.6"/>')

def text(x, y, t, size=16, color="#e5e7eb", weight=500, anchor="middle", extra=""):
    return (f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{color}" font-weight="{weight}" '
            f'text-anchor="{anchor}" {extra}>{t}</text>')

def frame(w, h, colors, body):
    grid = ''.join(f'<line x1="0" y1="{y}" x2="{w}" y2="{y}" stroke="#ffffff" stroke-opacity="0.03"/>' for y in range(0, h, 32))
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">{defs(colors)}'
            f'<rect width="{w}" height="{h}" rx="24" fill="url(#bg)"/>{grid}'
            f'<rect x="1" y="1" width="{w - 2}" height="{h - 2}" rx="24" fill="none" stroke="#6366f1" stroke-opacity="0.35"/>{body}</svg>')

RED, GREEN, AMBER, VIOLET, BLUE, SLATE = "#f43f5e", "#10b981", "#f59e0b", "#8b5cf6", "#3b82f6", "#64748b"

# ---- 1. hero -------------------------------------------------------------------------------------------------
b = text(70, 92, "lean-tokens", 22, "#a5b4fc", 700, "start", 'letter-spacing="3"')
b += text(70, 170, "−86%", 108, "#34d399", 900, "start", 'filter="url(#glow)"')
b += text(70, 220, "token usage per active hour", 28, "#f9fafb", 700, "start")
b += text(70, 262, "Same model. Same speed. Same quality.", 22, "#c7d2fe", 500, "start")
b += text(70, 300, "Measured on a real multi-day, multi-agent build.", 16, "#94a3b8", 400, "start")
for i, (lbl, c) in enumerate([("fresh small agents", VIOLET), ("one-shot waits", BLUE), ("short reports", AMBER)]):
    x = 70 + i * 200
    b += (f'<rect x="{x}" y="330" width="184" height="40" rx="20" fill="{c}" fill-opacity="0.16" stroke="{c}" stroke-opacity="0.7"/>'
          + text(x + 92, 356, lbl, 15, mix(c, 1.5), 600))
base, k = 430, 300 / 17.5
b += cylinder(800, base, 70, 17.5 * k, RED) + text(800, base - 17.5 * k - 44, "17.5M / h", 30, "#fda4af", 800)
b += text(800, base + 52, "Before", 18, "#cbd5e1", 600)
b += cylinder(1010, base, 70, 2.4 * k, GREEN) + text(1010, base - 2.4 * k - 44, "2.4M / h", 30, "#6ee7b7", 800, extra='filter="url(#glow)"')
b += text(1010, base + 52, "With lean-tokens", 18, "#cbd5e1", 600)
open("assets/hero.svg", "w").write(frame(1200, 520, [RED, GREEN], b))

# ---- 2. hour by hour -----------------------------------------------------------------------------------------
hours = [(31.4, RED), (13.7, RED), (12.1, RED), (6.8, AMBER), (2.1, GREEN), (5.1, GREEN), (0.4, GREEN), (1.9, GREEN)]
b = text(600, 70, "The moment lean mode switched on", 32, "#f9fafb", 800)
b += text(600, 104, "Effective tokens per active hour (millions). Red: long-lived agents. Amber: retiring them. Green: lean.", 16, "#94a3b8")
base, k = 470, 290 / 31.4
for i, (v, c) in enumerate(hours):
    cx = 150 + i * 130
    b += cylinder(cx, base, 42, max(6, v * k), c) + text(cx, base - max(6, v * k) - 26, f"{v}M", 20, mix(c, 1.6), 800)
b += (f'<line x1="605" y1="140" x2="605" y2="{base + 30}" stroke="#34d399" stroke-width="2" stroke-dasharray="8 8"/>'
      + f'<rect x="620" y="150" width="236" height="44" rx="22" fill="#10b981" fill-opacity="0.18" stroke="#34d399"/>'
      + text(738, 179, "lean-tokens ON →", 18, "#6ee7b7", 800))
open("assets/hourly.svg", "w").write(frame(1200, 540, [RED, AMBER, GREEN], b))

# ---- 3. where the tokens went --------------------------------------------------------------------------------
parts = [("Long-lived worker agents re-reading their history", 53, RED),
         ("Reviewers (fresh each time — already lean)", 22, VIOLET),
         ("Coordinator re-reading its own context", 21, BLUE),
         ("Actually running commands and tests", 3, AMBER), ("Everything else", 1, SLATE)]
b = text(600, 70, "Where the tokens really went", 32, "#f9fafb", 800)
b += text(600, 104, "Most usage was not work — it was re-reading. Idle big contexts reload at 2x when the cache expires.", 16, "#94a3b8")
y = 150
for name, v, c in parts:
    w = max(14, v * 12.5)
    b += (f'<rect x="80" y="{y}" width="1040" height="58" rx="29" fill="#ffffff" fill-opacity="0.04"/>'
          f'<rect x="80" y="{y}" width="{w + 60}" height="58" rx="29" fill="url(#side{c[1:]})"/>'
          f'<rect x="80" y="{y}" width="{w + 60}" height="24" rx="12" fill="#fff" fill-opacity="0.18"/>'
          + text(110 + w + 90, y + 37, f"{v}%", 24, mix(c, 1.6), 800, "start")
          + text(110 + w + 170, y + 37, name, 17, "#e5e7eb", 500, "start"))
    y += 78
open("assets/breakdown.svg", "w").write(frame(1200, 560, [c for _, _, c in parts], b))

# ---- 4. the lessons ------------------------------------------------------------------------------------------
lessons = [("Measure first", "See per-agent cost before cutting anything.", BLUE),
           ("Fresh, small agents", "One per task; hand off at ~150k context.", VIOLET),
           ("Never wake a giant", "Big idle contexts reload at 2x. Retire them.", RED),
           ("Wait in one step", "No polling, no “still running” wake-ups.", AMBER),
           ("Paths, not prose", "Short reports; pass file paths, not rewrites.", GREEN),
           ("Fix the class", "3 failed rounds? Change the design.", "#ec4899")]
b = text(600, 70, "6 lessons behind the −86%", 32, "#f9fafb", 800)
b += text(600, 104, "Quality never traded: same model, same effort, same reviews and tests.", 16, "#94a3b8")
for i, (t, d, c) in enumerate(lessons):
    x, y = 60 + (i % 3) * 370, 140 + (i // 3) * 190
    b += (f'<rect x="{x + 6}" y="{y + 8}" width="340" height="160" rx="22" fill="#000" opacity="0.4" filter="url(#soft)"/>'
          f'<rect x="{x}" y="{y}" width="340" height="160" rx="22" fill="#111827" stroke="{c}" stroke-opacity="0.6"/>'
          f'<rect x="{x}" y="{y}" width="340" height="6" rx="3" fill="{c}"/>'
          f'<circle cx="{x + 46}" cy="{y + 56}" r="26" fill="url(#side{c[1:]})"/>'
          + text(x + 46, y + 65, str(i + 1), 24, "#fff", 900)
          + text(x + 88, y + 64, t, 22, "#f9fafb", 800, "start")
          + text(x + 26, y + 118, d, 16, "#cbd5e1", 400, "start"))
open("assets/lessons.svg", "w").write(frame(1200, 540, [c for _, _, c in lessons], b))
print("ok")
