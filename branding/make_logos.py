"""Generate Marine Vibroacoustics Lab logo files (SVG with text as outlines + PNG)."""
import subprocess
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen

FD = "/usr/share/fonts/opentype/inter/"
FONTS = {w: TTFont(FD + f"Inter-{w}.otf") for w in ["Light", "Regular", "Medium", "SemiBold", "Bold"]}
OUT = Path("/home/claude/logo/out")
OUT.mkdir(exist_ok=True)

NAVY, BLUE, GREY = "#0C2340", "#2b6cb0", "#6b7280"
WHITE, LIGHTBLUE, LIGHTGREY = "#ffffff", "#9cc3ee", "#c9d3df"


def text_path(s, weight, size, x, y, tracking=0.0):
    """Return (svg path d, advance width) for string s at baseline (x, y)."""
    f = FONTS[weight]
    gs, cmap = f.getGlyphSet(), f.getBestCmap()
    upm = f["head"].unitsPerEm
    sc = size / upm
    d, cx = [], x
    for ch in s:
        g = cmap.get(ord(ch))
        if g is None:
            continue
        pen = SVGPathPen(gs)
        gs[g].draw(TransformPen(pen, (sc, 0, 0, -sc, cx, y)))
        d.append(pen.getCommands())
        cx += gs[g].width * sc + tracking * size
    width = cx - x - (tracking * size if s else 0)
    return " ".join(d), width


def cap_height(weight, size):
    f = FONTS[weight]
    return f["OS/2"].sCapHeight * size / f["head"].unitsPerEm


def svg(w, h, body, bg=None):
    rect = f'<rect width="{w}" height="{h}" fill="{bg}"/>' if bg else ""
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w:.0f} {h:.0f}" '
            f'width="{w:.0f}" height="{h:.0f}">{rect}{body}</svg>')


def p(d, fill):
    return f'<path d="{d}" fill="{fill}"/>'


SUB = "Memorial University of Newfoundland · Department of Ocean and Naval Architectural Engineering"
SUB_SHORT = "Memorial University of Newfoundland"


def stacked(c, sub=True):
    """Like the website: MARINE / Vibroacoustics Lab / subline."""
    pad = 40
    y1 = pad + cap_height("Medium", 32)
    d1, w1 = text_path("MARINE", "Medium", 32, pad, y1, tracking=0.3)
    y2 = y1 + 120
    d2, w2 = text_path("Vibroacoustics Lab", "Light", 120, pad - 4, y2)
    body = p(d1, c["eyebrow"]) + p(d2, c["title"])
    w = max(w1, w2) + 2 * pad
    h = y2 + 30 + pad
    if sub:
        y3 = y2 + 62
        d3, w3 = text_path(SUB_SHORT, "Regular", 34, pad, y3)
        body += p(d3, c["sub"])
        w = max(w, w3 + 2 * pad)
        h = y3 + pad
    return w, h, body


def horizontal(c, sub=True):
    """MVL on the side, thin rule, then MARINE / Vibroacoustics Lab."""
    pad = 40
    mvl_size = 190
    mvl_base = pad + cap_height("SemiBold", mvl_size)
    dm, wm = text_path("MVL", "SemiBold", mvl_size, pad, mvl_base, tracking=0.02)
    rule_x = pad + wm + 48
    tx = rule_x + 48
    y1 = pad + cap_height("Medium", 30) + 4
    d1, w1 = text_path("MARINE", "Medium", 30, tx, y1, tracking=0.3)
    y2 = y1 + 100
    d2, w2 = text_path("Vibroacoustics Lab", "Light", 100, tx - 3, y2)
    right = max(w1, w2)
    bottom = mvl_base
    body = p(dm, c["mono"]) + p(d1, c["eyebrow"]) + p(d2, c["title"])
    if sub:
        y3 = y2 + 52
        d3, w3 = text_path(SUB_SHORT, "Regular", 30, tx, y3)
        body += p(d3, c["sub"])
        right = max(right, w3)
        bottom = max(bottom, y3)
    body += (f'<rect x="{rule_x - 1.5}" y="{pad}" width="3" height="{bottom - pad:.1f}" '
             f'fill="{c["rule"]}"/>')
    return tx + right + pad, bottom + pad, body


def monogram(c):
    """Square MVL mark for small spaces (slide corners, icons)."""
    s = 600
    size = 220
    d, w = text_path("MVL", "SemiBold", size, 0, 0, tracking=0.02)
    x = (s - w) / 2
    y = s / 2 + cap_height("SemiBold", size) / 2
    d, _ = text_path("MVL", "SemiBold", size, x, y, tracking=0.02)
    rx = 48
    body = (f'<rect width="{s}" height="{s}" rx="{rx}" fill="{c["tile"]}"/>' + p(d, c["tile_text"]))
    return s, s, body


COLOUR = dict(eyebrow=BLUE, title=NAVY, sub=GREY, mono=NAVY, rule=BLUE, tile=NAVY, tile_text=WHITE)
REVERSE = dict(eyebrow=LIGHTBLUE, title=WHITE, sub=LIGHTGREY, mono=WHITE, rule=LIGHTBLUE,
               tile=WHITE, tile_text=NAVY)

variants = {
    "MVL_stacked": lambda c: stacked(c, sub=True),
    "MVL_stacked_nosub": lambda c: stacked(c, sub=False),
    "MVL_horizontal": lambda c: horizontal(c, sub=True),
    "MVL_horizontal_nosub": lambda c: horizontal(c, sub=False),
    "MVL_monogram": monogram,
}

for name, fn in variants.items():
    for tag, c in [("navy", COLOUR), ("white", REVERSE)]:
        w, h, body = fn(c)
        f = OUT / f"{name}_{tag}.svg"
        f.write_text(svg(w, h, body))
        # PowerPoint: transparent PNG, 4x for crisp projection
        subprocess.run(["rsvg-convert", "-z", "4", "-o", str(f.with_suffix(".png")), str(f)], check=True)
    # preview on background
    for tag, c, bg in [("navy", COLOUR, "#ffffff"), ("white", REVERSE, NAVY)]:
        w, h, body = fn(c)
        pf = OUT / f"_preview_{name}_{tag}.svg"
        pf.write_text(svg(w, h, body, bg=bg))
        subprocess.run(["rsvg-convert", "-z", "1", "-o", str(pf.with_suffix(".png")), str(pf)], check=True)
print("done")
