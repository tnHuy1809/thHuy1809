#!/usr/bin/env python3
"""Sinh toàn bộ asset SVG động cho README 'Huy's Orbit'.
Chữ được chuyển thành path (không phụ thuộc font của máy người xem)."""
import base64, io, math, random, sys
from pathlib import Path
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assets")
IMG_BH = sys.argv[2] if len(sys.argv) > 2 else "blackhole_disk.png"
IMG_DUO = sys.argv[3] if len(sys.argv) > 3 else "blackhole_duo.png"
FONT_DISPLAY = "Unbounded[wght].ttf"
FONT_TEXT = "SpaceGrotesk[wght].ttf"
OUT.mkdir(parents=True, exist_ok=True)

# ---------- chữ -> path ----------
_cache = {}
def load(fp, wght):
    k = (fp, wght)
    if k not in _cache:
        f = TTFont(fp)
        f = instancer.instantiateVariableFont(f, {"wght": wght})
        _cache[k] = f
    return _cache[k]

def text_path(text, fp, wght, size, tracking=0.0):
    """Trả về (d, width) với gốc (0,0) là baseline-trái."""
    f = load(fp, wght)
    gs, cmap, hmtx = f.getGlyphSet(), f.getBestCmap(), f["hmtx"]
    upm = f["head"].unitsPerEm
    s = size / upm
    x, d = 0.0, []
    for ch in text:
        gn = cmap.get(ord(ch))
        if gn is None:
            x += size * 0.3
            continue
        pen = SVGPathPen(gs)
        gs[gn].draw(TransformPen(pen, (s, 0, 0, -s, x, 0)))
        c = pen.getCommands()
        if c:
            d.append(c)
        x += hmtx[gn][0] * s + tracking
    return " ".join(d), x - tracking

def place(text, fp, wght, size, tracking, anchor, x, y):
    d, w = text_path(text, fp, wght, size, tracking)
    ox = x - (w / 2 if anchor == "middle" else w if anchor == "end" else 0)
    return f'<g transform="translate({ox:.1f} {y})"><path d="{d}"/></g>', w

def data_uri(path, width, quality=80):
    im = Image.open(path).convert("RGB")
    h = round(im.height * width / im.width)
    im = im.resize((width, h), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "JPEG", quality=quality, optimize=True, progressive=True)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode(), h

def stars(n, w, h, seed, avoid=None, rmax=1.5):
    rnd = random.Random(seed)
    out = []
    while len(out) < n:
        x, y = rnd.uniform(8, w - 8), rnd.uniform(6, h - 6)
        if avoid and avoid(x, y):
            continue
        r = rnd.choice([0.5, 0.6, 0.8, 1.0, rmax])
        dur, beg = rnd.uniform(2.4, 6.5), -rnd.uniform(0, 6)
        lo = rnd.uniform(0.08, 0.3)
        col = rnd.choice(["#FFFFFF", "#FFFFFF", "#FFE8C7", "#CFC4FF"])
        out.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{col}">'
            f'<animate attributeName="opacity" values="{lo:.2f};1;{lo:.2f}" dur="{dur:.1f}s" begin="{beg:.1f}s" repeatCount="indefinite"/></circle>')
    return "\n".join(out)

REDUCE = "<style>@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>"
EMBER = ["#FFF1D6", "#FFB347", "#FF6A1F"]

# =====================================================================
# 1. HERO
# =====================================================================
def hero():
    W, H = 1200, 610
    uri, ih = data_uri(IMG_BH, 1200, 82)
    oy = -70   # đẩy ảnh lên để chừa chỗ cho tiêu đề
    cx, cy = 600, 260
    title, tw = place("HUY'S ORBIT", FONT_DISPLAY, 800, 54, 7, "middle", 600, 528)
    phrases = ["Hi, I'm Huy", "I build things with code", "Always learning and shipping"]
    subs = []
    for i, p in enumerate(phrases):
        g, _ = place(p, FONT_TEXT, 500, 21, 1.6, "middle", 600, 576)
        t0 = i / 3; t1 = t0 + 0.035; t2 = t0 + 0.29; t3 = t0 + 1 / 3
        kt = [0, t0, t1, t2, t3, 1]
        kt = [min(1, max(0, v)) for v in kt]
        subs.append(
            f'<g fill="#C9C2E8" opacity="0">{g}'
            f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{";".join(f"{v:.3f}" for v in kt)}" dur="10.5s" repeatCount="indefinite"/></g>')
    ell = lambda x, y: ((x - cx) / 640) ** 2 + ((y - 255) / 215) ** 2 < 1
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">Huy's Orbit</title><desc id="d">Hố đen với đĩa bồi tụ đang phát sáng, dòng chữ Huy's Orbit bên dưới</desc>
{REDUCE}
<defs>
  <image id="bh" x="0" y="{oy}" width="1200" height="{ih}" href="{uri}"/>
  <mask id="disk" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><use href="#bh"/></mask>
  <linearGradient id="sweepA" x1="0" x2="1"><stop offset="0" stop-color="#FFE9C4" stop-opacity="0"/><stop offset=".5" stop-color="#FFF4DE" stop-opacity=".62"/><stop offset="1" stop-color="#FFE9C4" stop-opacity="0"/></linearGradient>
  <linearGradient id="sweepB" x1="0" x2="1"><stop offset="0" stop-color="#7B61FF" stop-opacity="0"/><stop offset=".5" stop-color="#B9A7FF" stop-opacity=".5"/><stop offset="1" stop-color="#7B61FF" stop-opacity="0"/></linearGradient>
  <radialGradient id="halo" cx=".5" cy=".5" r=".5"><stop offset=".55" stop-color="#FF8A3D" stop-opacity="0"/><stop offset=".78" stop-color="#FF8A3D" stop-opacity=".55"/><stop offset="1" stop-color="#FF6A1F" stop-opacity="0"/></radialGradient>
  <radialGradient id="vig" cx=".5" cy=".42" r=".75"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".85"/></radialGradient>
  <linearGradient id="ttl" x1="0" x2="1"><stop offset="0" stop-color="#FFF1D6"/><stop offset=".5" stop-color="#FFB347"/><stop offset="1" stop-color="#FF6A1F"/></linearGradient>
  <linearGradient id="sheen" gradientUnits="userSpaceOnUse" x1="-300" x2="0" y1="0" y2="0">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".9"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
    <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="1800 0" dur="6.5s" repeatCount="indefinite"/>
  </linearGradient>
  <mask id="ttlmask"><rect width="{W}" height="{H}" fill="#000"/><g fill="#fff">{title}</g></mask>
  <filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14"/></filter>
</defs>
<rect width="{W}" height="{H}" fill="#000"/>
{stars(70, W, H, 7, avoid=ell)}
<use href="#bh"/>
<!-- quầng sáng thở quanh vòng photon -->
<circle cx="{cx}" cy="{cy}" r="150" fill="url(#halo)" style="mix-blend-mode:screen"><animate attributeName="opacity" values=".15;.7;.15" dur="5.5s" repeatCount="indefinite"/><animate attributeName="r" values="140;158;140" dur="5.5s" repeatCount="indefinite"/></circle>
<!-- dòng plasma chảy dọc đĩa: chỉ hiện ở vùng sáng của ảnh -->
<g mask="url(#disk)" style="mix-blend-mode:screen">
  <g><rect x="-320" y="0" width="300" height="{H}" fill="url(#sweepA)" transform="skewX(-24)"/><animateTransform attributeName="transform" type="translate" from="0 0" to="1750 0" dur="7s" repeatCount="indefinite"/></g>
  <g><rect x="1500" y="0" width="360" height="{H}" fill="url(#sweepB)" transform="skewX(24)"/><animateTransform attributeName="transform" type="translate" from="0 0" to="-1950 0" dur="11s" begin="-4s" repeatCount="indefinite"/></g>
</g>
<rect width="{W}" height="{H}" fill="url(#vig)"/>
<!-- sao băng -->
<g opacity="0"><line x1="0" y1="0" x2="-90" y2="30" stroke="url(#sweepA)" stroke-width="1.6" stroke-linecap="round"/><circle r="1.8" fill="#fff"/>
  <animateTransform attributeName="transform" type="translate" values="980 18;520 170;520 170" keyTimes="0;.09;1" dur="13s" repeatCount="indefinite"/>
  <animate attributeName="opacity" values="0;1;0;0" keyTimes="0;.01;.09;1" dur="13s" repeatCount="indefinite"/></g>
<g fill="url(#ttl)">{title}</g>
<g mask="url(#ttlmask)"><rect x="0" y="470" width="{W}" height="80" fill="url(#sheen)"/></g>
{"".join(subs)}
</svg>'''

# =====================================================================
# 2. QUỸ ĐẠO TECH STACK
# =====================================================================
def orbit():
    W, H = 1200, 560
    cx, cy, tilt = 600, 275, -11
    orbits = [
        # rx, ry, dur, chiều, nhãn nhóm, màu, nodes
        (225, 62, 30, 1, "Frontend", "#FFB347",
         [("HTML", "#E44D26"), ("CSS", "#2965F1"), ("JS", "#F7DF1E"), ("TS", "#4C9BE8"), ("React", "#61DAFB"), ("Tailwind", "#38BDF8")]),
        (385, 112, 48, -1, "Backend", "#B9A7FF",
         [("Node.js", "#6CC24A"), ("Python", "#FFD43B"), ("Java", "#F89820"), ("C#", "#B67FD0")]),
        (545, 160, 70, 1, "Dữ liệu & công cụ", "#7FE3FF",
         [("MySQL", "#5CB0D8"), ("PostgreSQL", "#6E9BD1"), ("MongoDB", "#5FBF6A"), ("Git", "#F1502F"), ("Docker", "#4DA6F5"), ("VS Code", "#3FA9F5")]),
    ]
    layers, nodes, legend = [], [], []
    for oi, (rx, ry, dur, dr, label, col, items) in enumerate(orbits):
        sweep = 1 if dr > 0 else 0
        path = f"M {rx} 0 A {rx} {ry} 0 1 {sweep} {-rx} 0 A {rx} {ry} 0 1 {sweep} {rx} 0 Z"
        layers.append(f'<path id="o{oi}" d="{path}" fill="none" stroke="{col}" stroke-opacity=".28" stroke-width="1.2" stroke-dasharray="2 7"><animate attributeName="stroke-dashoffset" from="0" to="{-18*dr}" dur="3s" repeatCount="indefinite"/></path>')
        n = len(items)
        for k, (name, c) in enumerate(items):
            d, w = text_path(name, FONT_TEXT, 600, 17, 0.4)
            pw = w + 26
            begin = -(dur * k / n)
            nodes.append(f'''<g><animateMotion dur="{dur}s" begin="{begin:.2f}s" repeatCount="indefinite"><mpath href="#o{oi}"/></animateMotion>
<g transform="rotate({-tilt})"><rect x="{-pw/2:.1f}" y="-17" width="{pw:.1f}" height="34" rx="17" fill="#0A0B12" stroke="{c}" stroke-width="1.6"/>
<circle cx="{-pw/2+13:.1f}" cy="0" r="3.2" fill="{c}"/><g fill="#F2EEFF" transform="translate({-pw/2+22:.1f} 6)"><path d="{d}"/></g></g></g>'''.replace("<circle", "<circle", 1))
        # chú giải
    lx = 330
    for oi, (rx, ry, dur, dr, label, col, items) in enumerate(orbits):
        g, w = place(label, FONT_TEXT, 500, 18, 0.8, "start", lx + 22, 536)
        legend.append(f'<circle cx="{lx}" cy="530" r="5" fill="{col}"/><g fill="#B9B4D0">{g}</g>')
        lx += w + 80
    # đĩa bồi tụ trung tâm
    disk = []
    rings = [(138, 25, "#FF6A1F", .5, 2.2, "150 22 60 16"), (112, 20, "#FF8A3D", .7, 2.6, "110 14 70 20"),
             (90, 16, "#FFB347", .85, 2.6, "130 18 40 12"), (70, 12.5, "#FFE3B0", .95, 2.2, "90 10 50 14")]
    for i, (rx, ry, c, o, sw, da) in enumerate(rings):
        disk.append(f'<ellipse rx="{rx}" ry="{ry}" fill="none" stroke="{c}" stroke-opacity="{o*0.28:.2f}" stroke-width="{sw+3}" filter="url(#bloom)"/>')
        disk.append(f'<ellipse rx="{rx}" ry="{ry}" fill="none" stroke="{c}" stroke-opacity="{o}" stroke-width="{sw}" stroke-linecap="round" stroke-dasharray="{da}" filter="url(#bloom)"><animate attributeName="stroke-dashoffset" from="0" to="{-sum(float(x) for x in da.split())*(1 if i%2==0 else -1):.0f}" dur="{9-i}s" repeatCount="indefinite"/></ellipse>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-labelledby="t d">
<title id="t">Tech stack quay quanh hố đen</title><desc id="d">HTML, CSS, JavaScript, TypeScript, React, Tailwind; Node.js, Python, Java, C#; MySQL, PostgreSQL, MongoDB, Git, Docker, VS Code</desc>
{REDUCE}
<defs>
  <filter id="bloom" x="-30%" y="-80%" width="160%" height="260%"><feGaussianBlur stdDeviation="1.8" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <radialGradient id="core" cx=".5" cy=".5" r=".5"><stop offset=".3" stop-color="#FF6A1F" stop-opacity=".5"/><stop offset="1" stop-color="#FF6A1F" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{W}" height="{H}" fill="#000"/>
{stars(90, W, H, 21, avoid=lambda x,y: abs(x-cx)<150 and abs(y-cy)<70)}
<g transform="translate({cx} {cy}) rotate({tilt})">
{"".join(layers)}
</g>
<circle cx="{cx}" cy="{cy}" r="110" fill="url(#core)"><animate attributeName="opacity" values=".45;1;.45" dur="5s" repeatCount="indefinite"/></circle>
<g transform="translate({cx} {cy}) rotate({tilt})">{"".join(disk)}</g>
<!-- chân trời sự kiện -->
<circle cx="{cx}" cy="{cy}" r="40" fill="#000"/>
<circle cx="{cx}" cy="{cy}" r="41" fill="none" stroke="#FFE3B0" stroke-width="1.6" filter="url(#bloom)"><animate attributeName="stroke-opacity" values=".55;1;.55" dur="4s" repeatCount="indefinite"/></circle>
<path d="M {cx-62} {cy-6} A 64 64 0 0 1 {cx+62} {cy-6}" fill="none" stroke="#FFB347" stroke-opacity=".65" stroke-width="3" stroke-linecap="round" filter="url(#bloom)"/>
<g transform="translate({cx} {cy}) rotate({tilt})">
{"".join(nodes)}
</g>
{"".join(legend)}
</svg>'''

# =====================================================================
# 3. HEADER TỪNG MỤC
# =====================================================================
def section(title, key):
    W, H = 1200, 76
    g, w = place(title, FONT_DISPLAY, 700, 25, 1.2, "start", 92, 48)
    x0 = 92 + w + 28
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{title}">
<title>{title}</title>{REDUCE}
<defs>
  <linearGradient id="ln" gradientUnits="userSpaceOnUse" x1="{x0:.0f}" x2="1160" y1="0" y2="0"><stop offset="0" stop-color="#FF8A3D" stop-opacity=".9"/><stop offset=".55" stop-color="#7B61FF" stop-opacity=".45"/><stop offset="1" stop-color="#7B61FF" stop-opacity="0"/></linearGradient>
  <linearGradient id="tx" x1="0" x2="1"><stop offset="0" stop-color="#FFF1D6"/><stop offset="1" stop-color="#FFB347"/></linearGradient>
  <filter id="gl" x="-60%" y="-60%" width="220%" height="220%"><feGaussianBlur stdDeviation="2.2" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" rx="14" fill="#000"/>
{stars(26, W, H, hash(key) % 1000, rmax=1.1)}
<g transform="translate(46 38)">
  <ellipse rx="22" ry="6" fill="none" stroke="#FF6A1F" stroke-width="2.4" stroke-dasharray="20 6 8 10" filter="url(#gl)" transform="rotate(-14)"><animate attributeName="stroke-dashoffset" from="0" to="-88" dur="3.2s" repeatCount="indefinite"/></ellipse>
  <circle r="10" fill="#000" stroke="#FFE3B0" stroke-width="1.4" filter="url(#gl)"/>
</g>
<g fill="url(#tx)">{g}</g>
<line x1="{x0:.0f}" y1="38" x2="1160" y2="38" stroke="url(#ln)" stroke-width="1.6" stroke-linecap="round"/>
<circle r="3" cy="38" fill="#FFE3B0" filter="url(#gl)"><animate attributeName="cx" from="{x0:.0f}" to="1160" dur="5.5s" repeatCount="indefinite"/><animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.8;1" dur="5.5s" repeatCount="indefinite"/></circle>
</svg>'''

# =====================================================================
# 4. FOOTER (ảnh hai hố đen)
# =====================================================================
def footer():
    W = 1200
    uri, ih = data_uri(IMG_DUO, 1200, 80)
    H = ih
    q = "Không ngừng tiến lên, mỗi dòng code đều là một bước khám phá mới."
    g, w = place(q, FONT_TEXT, 500, 21, 0.6, "middle", 600, H - 36)
    scale = min(1, 1080 / w)
    if scale < 1:
        g, w = place(q, FONT_TEXT, 500, 21 * scale, 0.6 * scale, "middle", 600, H - 36)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="Không ngừng tiến lên, mỗi dòng code đều là một bước khám phá mới.">
<title>Không ngừng tiến lên</title>{REDUCE}
<defs>
  <image id="duo" x="0" y="0" width="{W}" height="{H}" href="{uri}"/>
  <mask id="rings" maskUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><use href="#duo"/></mask>
  <linearGradient id="sw" x1="0" x2="1"><stop offset="0" stop-color="#FFE9C4" stop-opacity="0"/><stop offset=".5" stop-color="#FFF4DE" stop-opacity=".55"/><stop offset="1" stop-color="#FFE9C4" stop-opacity="0"/></linearGradient>
  <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1"><stop offset=".55" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".92"/></linearGradient>
  <linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="#000" stop-opacity=".7"/><stop offset=".12" stop-color="#000" stop-opacity="0"/><stop offset=".88" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity=".7"/></linearGradient>
</defs>
<rect width="{W}" height="{H}" rx="14" fill="#000"/>
<use href="#duo"/>
<g mask="url(#rings)" style="mix-blend-mode:screen">
  <g><rect x="-300" width="260" height="{H}" fill="url(#sw)" transform="skewX(-22)"/><animateTransform attributeName="transform" type="translate" from="0 0" to="1700 0" dur="9s" repeatCount="indefinite"/></g>
</g>
{stars(46, W, H, 99, avoid=lambda x,y: y>H-90, rmax=1.3)}
<rect width="{W}" height="{H}" fill="url(#edge)"/><rect width="{W}" height="{H}" fill="url(#fade)"/>
<g fill="#F2EEFF">{g}</g>
</svg>'''

files = {
    "hero.svg": hero(),
    "orbit-stack.svg": orbit(),
    "section-about.svg": section("Giới thiệu", "about"),
    "section-stack.svg": section("Hành trang", "stack"),
    "section-mission.svg": section("Nhiệm vụ hiện tại", "mission"),
    "section-signals.svg": section("Tín hiệu từ GitHub", "signals"),
    "section-contact.svg": section("Liên lạc", "contact"),
    "footer.svg": footer(),
}
for n, c in files.items():
    (OUT / n).write_text(c, encoding="utf-8")
    print(f"{n:24s} {len(c)/1024:7.1f} KB")
