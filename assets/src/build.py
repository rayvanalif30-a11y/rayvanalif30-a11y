"""Builds the animated SVGs used in the profile README.

Run from anywhere:  python assets/src/build.py
Needs: pip install pillow fonttools brotli
"""
import base64, io, math, random
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from PIL import Image, ImageDraw, ImageFont

SRC = Path(__file__).resolve().parent
OUT = SRC.parent

BG = "#060606"
FG = "#f5f6f8"
MUTED = "#b3b9c7"
DIM = "#5b6272"
BLUE = "#2563eb"
BLUE_L = "#8db8ff"
GROTESK = SRC / "space-grotesk-latin-wght-normal.woff2"
ARCHIVO = SRC / "archivo-latin-wght-normal.woff2"


def font_face(path, family, text):
    """Subset a variable woff2 to the characters used and return an @font-face rule."""
    opts = subset.Options()
    opts.flavor = "woff2"
    opts.layout_features = ["*"]
    f = subset.load_font(str(path), opts)
    s = subset.Subsetter(opts)
    s.populate(text=text + " ")
    s.subset(f)
    buf = io.BytesIO()
    subset.save_font(f, buf, opts)
    b64 = base64.b64encode(buf.getvalue()).decode()
    return (f"@font-face{{font-family:'{family}';font-weight:300 800;"
            f"src:url(data:font/woff2;base64,{b64}) format('woff2');}}")


def esc(t):
    return t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


REDUCED = ("@media (prefers-reduced-motion: reduce){*{animation-duration:0s!important;"
           "animation-delay:0s!important;animation-iteration-count:1!important;}}")


# ---------------------------------------------------------------- hero
def hero():
    W, H = 1200, 420
    name = "RAYVAN ALIFARLO"
    # static bold instance for rasterising the name into dots
    vf = TTFont(str(GROTESK))
    st = instancer.instantiateVariableFont(vf, {"wght": 700})
    st.flavor = None
    ttf = io.BytesIO(); st.save(ttf); ttf.seek(0)
    size = 150
    while True:
        ttf.seek(0)
        pil_font = ImageFont.truetype(ttf, size)
        b = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), name, font=pil_font)
        if b[2] - b[0] <= 1040:
            break
        size -= 2

    img = Image.new("L", (W, 220), 0)
    d = ImageDraw.Draw(img)
    box = d.textbbox((0, 0), name, font=pil_font)
    tw, th = box[2] - box[0], box[3] - box[1]
    ox, oy = (W - tw) / 2 - box[0], (220 - th) / 2 - box[1]
    d.text((ox, oy), name, font=pil_font, fill=255)

    step = 6
    rnd = random.Random(8000)
    dots = []
    for y in range(0, 220, step):
        for x in range(0, W, step):
            if img.getpixel((x, y)) > 140:
                dots.append((x, y + 60))
    cx = W / 2
    circles = []
    for x, y in dots:
        ang = rnd.uniform(0, 2 * math.pi)
        dist = rnd.uniform(380, 820)
        dx, dy = math.cos(ang) * dist, math.sin(ang) * dist * 0.55
        fly = 0.15 + (abs(x - cx) / cx) * 0.9 + rnd.uniform(0, 0.5)
        wave = (x / W) * 3.2  # shimmer travels left to right
        r = 2.3 if rnd.random() > 0.12 else 1.4
        cls = "d a" if rnd.random() < 0.09 else "d"
        circles.append(
            f'<circle class="{cls}" cx="{x}" cy="{y}" r="{r}" '
            f'style="--x:{dx:.0f}px;--y:{dy:.0f}px;animation-delay:{fly:.2f}s,{fly + 2.2 + wave:.2f}s"/>')

    # ambient drifting background dots
    amb = []
    for i in range(70):
        x, y = rnd.uniform(0, W), rnd.uniform(0, H)
        dur = rnd.uniform(9, 18)
        amb.append(f'<circle class="m" cx="{x:.0f}" cy="{y:.0f}" r="{rnd.uniform(.6,1.5):.1f}" '
                   f'style="animation-duration:{dur:.1f}s;animation-delay:-{rnd.uniform(0,dur):.1f}s"/>')

    sub = "Information Technology @ Telkom University"
    sub2 = "Interactive web  ·  scroll-driven experiences  ·  campus apps"
    css = font_face(GROTESK, "SG", sub + sub2) + f"""
.d{{fill:{FG};animation:fly 2.4s cubic-bezier(.16,1,.3,1) both,glow 4.2s ease-in-out infinite;}}
.d.a{{fill:{BLUE_L};}}
@keyframes fly{{from{{transform:translate(var(--x),var(--y));opacity:0}}to{{transform:none;opacity:1}}}}
@keyframes glow{{0%,100%{{opacity:1}}50%{{opacity:.35}}}}
.m{{fill:{BLUE_L};opacity:.0;animation:drift linear infinite;}}
@keyframes drift{{0%{{transform:translateY(0);opacity:0}}20%{{opacity:.45}}80%{{opacity:.45}}100%{{transform:translateY(-60px);opacity:0}}}}
.t{{font-family:'SG',system-ui,sans-serif;}}
.s1{{font-size:26px;font-weight:500;fill:{FG};}}
.s2{{font-size:17px;font-weight:400;fill:{MUTED};letter-spacing:.06em;}}
.type{{animation:type 1.8s steps({len(sub)}) 2.6s both;}}
@keyframes type{{from{{width:0}}to{{width:{W}px}}}}
.caret{{fill:{BLUE_L};animation:blink 1s steps(1) infinite 2.6s, caretmove 1.8s steps({len(sub)}) 2.6s both;}}
@keyframes blink{{50%{{opacity:0}}}}
.fade{{animation:fade 1.2s ease 4.4s both;}}
@keyframes fade{{from{{opacity:0;transform:translateY(8px)}}to{{opacity:1;transform:none}}}}
.scan{{animation:scan 6s ease-in-out 2.4s infinite;}}
@keyframes scan{{0%{{transform:translateX(-300px);opacity:0}}15%{{opacity:1}}85%{{opacity:1}}100%{{transform:translateX({W}px);opacity:0}}}}
{REDUCED}
"""
    # caret travel distance approx: measure text width with PIL at 26px
    medium = instancer.instantiateVariableFont(TTFont(str(GROTESK)), {"wght": 500})
    medium.flavor = None
    mb = io.BytesIO(); medium.save(mb); mb.seek(0)
    sw = ImageDraw.Draw(Image.new("L", (1, 1))).textlength(sub, font=ImageFont.truetype(mb, 26))
    sx = (W - sw) / 2
    css += f"@keyframes caretmove{{from{{transform:translateX(0)}}to{{transform:translateX({sw:.0f}px)}}}}"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Rayvan Alifarlo Mahesworo, Information Technology at Telkom University">
<title>Rayvan Alifarlo Mahesworo</title>
<style>{css}</style>
<defs>
<radialGradient id="halo" cx="50%" cy="38%" r="60%"><stop offset="0" stop-color="{BLUE}" stop-opacity=".28"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>
<linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="{BLUE_L}" stop-opacity="0"/><stop offset=".5" stop-color="{BLUE_L}" stop-opacity=".9"/><stop offset="1" stop-color="{BLUE_L}" stop-opacity="0"/></linearGradient>
<clipPath id="tc"><rect class="type" x="0" y="0" height="{H}" width="0"/></clipPath>
<clipPath id="round"><rect width="{W}" height="{H}" rx="22"/></clipPath>
</defs>
<g clip-path="url(#round)">
<rect width="{W}" height="{H}" fill="{BG}"/>
<rect width="{W}" height="{H}" fill="url(#halo)"/>
{''.join(amb)}
{''.join(circles)}
<rect class="scan" x="0" y="300" width="300" height="1.5" fill="url(#beam)"/>
<g clip-path="url(#tc)" transform="translate({sx:.0f},0)"><text class="t s1" x="0" y="335">{esc(sub)}</text></g>
<rect class="caret" x="{sx + 3:.0f}" y="314" width="2" height="27"/>
<text class="t s2 fade" x="{W/2}" y="372" text-anchor="middle">{esc(sub2)}</text>
</g>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="22" fill="none" stroke="#ffffff" stroke-opacity=".12"/>
</svg>"""
    (OUT / "hero.svg").write_text(svg)
    print("hero.svg", len(dots), "dots", len(svg) // 1024, "KB")


# ---------------------------------------------------------------- terminal
def terminal():
    W = 1200
    lines = [
        ("cmd", "whoami"),
        ("out", "Rayvan Alifarlo Mahesworo · IT student @ Telkom University"),
        ("cmd", "cat focus.txt"),
        ("out", "Interactive websites: WebGL, Canvas, scroll-driven motion"),
        ("out", "Campus web apps: Node.js + Express, Supabase"),
        ("cmd", "cat experience.txt"),
        ("out", "Staff Muda, KPM HMIT (Oct 2025 – Jan 2026)"),
        ("cmd", "ls certificates/"),
        ("out", "HaKI copyright, Trans TucTuc app (DJKI, 2026)"),
        ("out", "Workshop Cyber Security, Dunia Coding (Jul 2026)"),
        ("cmd", "echo $STATUS"),
        ("ok", "Open to internships & collaborations"),
    ]
    top, lh = 78, 34
    H = top + lh * (len(lines) + 1) + 14
    t = 0.6
    rows = []
    for i, (kind, text) in enumerate(lines):
        y = top + i * lh
        n = len(text) + (2 if kind == "cmd" else 0)
        dur = 0.045 * n if kind == "cmd" else 0.35
        steps = n if kind == "cmd" else 1
        if kind == "cmd":
            content = (f'<tspan fill="{BLUE_L}">rayvan</tspan><tspan fill="{DIM}">@github</tspan>'
                       f'<tspan fill="{MUTED}"> ~ $ </tspan><tspan fill="{FG}">{esc(text)}</tspan>')
            prefix = len("rayvan@github ~ $ ")
            # prompt appears instantly, the command types out
            rows.append(f'<g style="animation-delay:{t:.2f}s" class="ln"><clipPath id="c{i}"><rect class="ty" '
                        f'style="animation:ty {dur:.2f}s steps({steps}) {t:.2f}s both;--w:{(prefix + n) * 11.4:.0f}px;--s:{prefix * 11.4:.0f}px" '
                        f'x="40" y="{y-24}" height="{lh}"/></clipPath>'
                        f'<text clip-path="url(#c{i})" class="mono" x="40" y="{y}">{content}</text></g>')
            t += dur + 0.25
        else:
            color = "#4ade80" if kind == "ok" else MUTED
            mark = "✓ " if kind == "ok" else "  "
            rows.append(f'<text class="mono ln fadein" style="animation-delay:{t:.2f}s" x="40" y="{y}" fill="{color}">{mark}{esc(text)}</text>')
            t += dur
    caret_y = top + (len(lines) - 1) * lh
    css = f"""
.mono{{font-family:ui-monospace,'SFMono-Regular','Cascadia Code',Consolas,'Liberation Mono',monospace;font-size:19px;}}
.ty{{width:var(--s);}}
@keyframes ty{{from{{width:var(--s)}}to{{width:var(--w)}}}}
.fadein{{animation:fi .35s ease both;}}
@keyframes fi{{from{{opacity:0;transform:translateX(-6px)}}to{{opacity:1;transform:none}}}}
.ln{{opacity:1}}
g.ln{{animation:show 0s linear both;}}
@keyframes show{{from{{opacity:0}}to{{opacity:1}}}}
.cur2{{animation:show 0s {t:.2f}s both;}}
.cur{{fill:{BLUE_L};animation:show 0s {t:.2f}s both,blink 1s steps(1) {t:.2f}s infinite;}}
@keyframes blink{{50%{{opacity:0}}}}
{REDUCED}
"""
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="About Rayvan">
<title>About Rayvan</title>
<style>{css}</style>
<rect x=".5" y=".5" width="{W-1}" height="{H-1}" rx="18" fill="#0b0d12" stroke="#ffffff" stroke-opacity=".12"/>
<path d="M18.5 .5h{W-37}a18 18 0 0 1 18 18V44H.5V18.5a18 18 0 0 1 18-18z" fill="#11141b"/>
<circle cx="30" cy="22" r="6.5" fill="#ff5f57"/><circle cx="52" cy="22" r="6.5" fill="#febc2e"/><circle cx="74" cy="22" r="6.5" fill="#28c840"/>
<text class="mono" x="{W/2}" y="28" text-anchor="middle" fill="{DIM}" style="font-size:14px">rayvan@github: ~/about</text>
{''.join(rows)}
<text class="mono cur2" x="40" y="{caret_y + lh}"><tspan fill="{BLUE_L}">rayvan</tspan><tspan fill="{DIM}">@github</tspan><tspan fill="{MUTED}"> ~ $ </tspan></text>
<rect class="cur" x="{40 + len('rayvan@github ~ $ ') * 11.4 + 4:.0f}" y="{caret_y + lh - 20}" width="10" height="20"/>
</svg>"""
    # last line is output, so put the idle caret on a fresh prompt line below
    (OUT / "about.svg").write_text(svg)
    print("about.svg", len(svg) // 1024, "KB, runs", round(t, 1), "s")


# ---------------------------------------------------------------- cards
PROJECTS = [
    ("portfolio", "Portfolio", "8,000 dots form my name and reshape chapter by chapter as you scroll.",
     ["WebGL", "Canvas", "JavaScript"], "rayvan-alifarlo.netlify.app"),
    ("cv", "Interactive CV", "A paper CV that comes apart into layers as you scroll, then turns over.",
     ["HTML", "CSS", "Scroll motion"], "cv-rayvanalifarlo.netlify.app"),
    ("tuctuc", "TucTuc Tel-U", "Campus transport booking app for Telkom University students. HaKI registered.",
     ["Node.js", "Express", "JavaScript"], "trans-tuc-tuc.vercel.app"),
    ("aspirasi", "Aspirasi KPM HMIT", "Anonymous student feedback with status tracking and an admin dashboard.",
     ["Supabase", "JavaScript", "SQL"], "source on GitHub"),
]


def wrap(text, n):
    out, cur = [], ""
    for w in text.split():
        if len(cur) + len(w) + 1 > n:
            out.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return out + [cur]


def cards():
    alltext = "".join(p[1] + p[2] + "".join(p[3]) + p[4] for p in PROJECTS) + "↗0123456789 /"
    css_fonts = font_face(GROTESK, "SG", alltext) + font_face(ARCHIVO, "AR", alltext)
    W, H = 580, 230
    for idx, (slug, title, desc, tags, url) in enumerate(PROJECTS):
        per = 2 * (W + H - 4 * 18) + 2 * math.pi * 18
        tag_svg, x = [], 28
        for tg in tags:
            w = len(tg) * 8.2 + 22
            tag_svg.append(f'<rect x="{x}" y="160" width="{w:.0f}" height="26" rx="13" fill="{BLUE}" fill-opacity=".14" stroke="{BLUE_L}" stroke-opacity=".35"/>'
                           f'<text class="ar tag" x="{x + w/2:.0f}" y="177.5" text-anchor="middle">{esc(tg)}</text>')
            x += w + 8
        dl = "".join(f'<text class="ar desc" x="28" y="{104 + i*24}">{esc(l)}</text>' for i, l in enumerate(wrap(desc, 52)))
        # mini dot field in the corner, pulsing
        rnd = random.Random(idx)
        field = "".join(
            f'<circle cx="{W-120 + c*14}" cy="{30 + r*14}" r="2" class="pd" style="animation-delay:{(c+r)*0.18 + rnd.uniform(0,.3):.2f}s"/>'
            for r in range(4) for c in range(7))
        delay = idx * 0.9
        css = css_fonts + f"""
.sg{{font-family:'SG',system-ui,sans-serif;}} .ar{{font-family:'AR',system-ui,sans-serif;}}
.title{{font-size:27px;font-weight:700;fill:{FG};}}
.desc{{font-size:16.5px;fill:{MUTED};}}
.tag{{font-size:13px;font-weight:600;fill:{BLUE_L};}}
.url{{font-size:13.5px;fill:{DIM};}}
.edge{{stroke-dasharray:140 {per-140:.0f};animation:run 5s linear {delay:.1f}s infinite both;}}
@keyframes run{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-{per:.0f}}}}}
.pd{{fill:{BLUE_L};animation:pd 2.6s ease-in-out infinite;opacity:.15}}
@keyframes pd{{0%,100%{{opacity:.12}}50%{{opacity:.85}}}}
.live{{fill:#4ade80;animation:live 1.8s ease-out infinite;transform-origin:34px 214px;}}
@keyframes live{{0%{{transform:scale(1);opacity:.7}}100%{{transform:scale(3);opacity:0}}}}
.in{{animation:in .8s cubic-bezier(.16,1,.3,1) {0.2+idx*0.15:.2f}s both;}}
@keyframes in{{from{{opacity:0;transform:translateY(14px)}}to{{opacity:1;transform:none}}}}
{REDUCED}
"""
        svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{esc(title)}: {esc(desc)}">
<title>{esc(title)}</title>
<style>{css}</style>
<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0f1424"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="url(#g)" stroke="#ffffff" stroke-opacity=".12"/>
<rect class="edge" x="1" y="1" width="{W-2}" height="{H-2}" rx="18" fill="none" stroke="{BLUE_L}" stroke-width="2" stroke-linecap="round"/>
{field}
<g class="in">
<text class="sg title" x="28" y="62">{esc(title)} <tspan fill="{BLUE_L}" font-size="22">↗</tspan></text>
{dl}
{''.join(tag_svg)}
<circle cx="34" cy="214" r="4" fill="#4ade80"/><circle class="live" cx="34" cy="214" r="4"/>
<text class="ar url" x="46" y="218.5">{esc(url)}</text>
</g>
</svg>"""
        (OUT / f"card-{slug}.svg").write_text(svg)
        print(f"card-{slug}.svg", len(svg) // 1024, "KB")


# ---------------------------------------------------------------- divider
def divider():
    W, H = 1200, 24
    dots = "".join(f'<circle cx="{8 + i*16}" cy="12" r="2.2" style="animation-delay:{i*0.04:.2f}s"/>' for i in range(75))
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" aria-hidden="true">
<style>circle{{fill:{BLUE_L};opacity:.15;animation:w 3s ease-in-out infinite;}}
@keyframes w{{0%,100%{{opacity:.12;transform:translateY(0)}}50%{{opacity:.9;transform:translateY(-4px)}}}}{REDUCED}</style>
{dots}</svg>"""
    (OUT / "divider.svg").write_text(svg)
    print("divider.svg")


if __name__ == "__main__":
    hero(); terminal(); cards(); divider()
