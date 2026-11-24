"""Recreate Lorenzo's three wordmark designs (one-line, stacked, monogram) for a new lab name.

Geometry and colours copied from the original MVL_wordmarks set.
Text is converted to outlines, so the files do not depend on the Inter font.
"""
import subprocess
import sys
from pathlib import Path

exec(open(Path(__file__).with_name("make_logos.py")).read().split("COLOUR =")[0])

NAVY_C = dict(main="#0C2340", eyebrow="#2B6CB0", rule="#0C2340")
WHITE_C = dict(main="#FFFFFF", eyebrow="#9EC3E6", rule="#FFFFFF")


def oneline(name, c):
    d, w = text_path(name, "Light", 64, 26, 82, tracking=0.014)
    return w + 52, 114, p(d, c["main"])


def stacked(eyebrow, title, c):
    d1, w1 = text_path(eyebrow.upper(), "Medium", 34, 24.7, 54, tracking=0.25)
    d2, w2 = text_path(title, "Light", 96, 22.7, 160.4, tracking=-0.004)
    return max(w1, w2) + 48, 206, p(d1, c["eyebrow"]) + p(d2, c["main"])


def monogram(acr, line1, line2, c):
    dm, wm = text_path(acr, "Medium", 120, 29.7, 138, tracking=0.04)
    rule_x = 29.7 + wm + 41
    tx = rule_x + 39
    d1, w1 = text_path(line1, "Light", 46.5, tx, 78, tracking=0.035)
    d2, w2 = text_path(line2, "Light", 46.5, tx, 144, tracking=0.035)
    body = (p(dm, c["main"]) +
            f'<rect x="{rule_x:.1f}" y="28" width="2.5" height="132" fill="{c["rule"]}" fill-opacity="0.5"/>' +
            p(d1, c["main"]) + p(d2, c["main"]))
    return tx + max(w1, w2) + 23, 188, body


def build(acr, first, rest, outdir):
    out = Path(outdir)
    out.mkdir(parents=True, exist_ok=True)
    full = f"{first} {rest}"
    jobs = {
        f"{acr}_wordmark_1_oneline": lambda c: oneline(full, c),
        f"{acr}_wordmark_3_stacked": lambda c: stacked(first, rest, c),
        f"{acr}_wordmark_6_monogram": lambda c: monogram(acr, first, rest, c),
    }
    for stem, fn in jobs.items():
        for tag, c in [("navy", NAVY_C), ("white", WHITE_C)]:
            w, h, body = fn(c)
            f = out / f"{stem}_{tag}.svg"
            f.write_text(svg(w, h, body))
            subprocess.run(["rsvg-convert", "-z", "3", "-o", str(f.with_suffix(".png")), str(f)], check=True)


if __name__ == "__main__":
    # e.g. python3 make_wordmarks.py MSVL Marine "Sound and Vibration Lab" out_msvl
    build(*sys.argv[1:5])
