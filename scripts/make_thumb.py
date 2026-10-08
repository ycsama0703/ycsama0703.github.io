#!/usr/bin/env python3
"""Prepare a publication teaser figure for assets/pubs/.

The frame on the page is 4:3 and uses object-fit: cover, so it is always
filled edge to edge — whatever this writes is what shows, and anything not
4:3 gets cropped by the browser. So this script always hands back exactly
4:3.

Typical use: a paper's Fig. 1 is a tall flowchart, and only the top third of
it is worth showing at thumbnail size.

    # see the figure, with a ruler, to choose a region
    python3 scripts/make_thumb.py paper.pdf --page 3 --inspect

    # take the top 45% of it
    python3 scripts/make_thumb.py paper.pdf --page 3 --box 0,0,1,0.45 fingpt

    # or start from an image you already cropped
    python3 scripts/make_thumb.py fig.png fingpt

--box is L,T,R,B as fractions of the image AFTER white margins are trimmed.
Whatever you ask for is then squared off to 4:3 by trimming the long side,
anchored at the top (--anchor center to take it from the middle instead).
"""
import argparse, os, subprocess, sys, tempfile
from PIL import Image, ImageChops, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "assets", "pubs")
OUT_W, RATIO = 560, 4 / 3


def load(path, page):
    path = os.path.expanduser(path)
    if not path.lower().endswith(".pdf"):
        return Image.open(path).convert("RGB")
    d = tempfile.mkdtemp(prefix="pubfig-")
    subprocess.run(["pdftoppm", "-png", "-r", "200", "-f", str(page), "-l", str(page),
                    path, os.path.join(d, "p")], check=True)
    hits = sorted(os.listdir(d))
    if not hits:
        sys.exit(f"pdftoppm produced nothing for page {page}")
    return Image.open(os.path.join(d, hits[0])).convert("RGB")


def trim(im):
    bbox = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    return im.crop(bbox) if bbox else im


def to_ratio(im, anchor):
    """Trim the long side so the result is exactly 4:3."""
    w, h = im.size
    if abs(w / h - RATIO) < 0.005:
        return im
    if w / h > RATIO:                       # too wide -> trim width, always centred
        new = int(round(h * RATIO))           # (anchor only has a meaning vertically)
        off = (w - new) // 2
        return im.crop((off, 0, off + new, h))
    new = int(round(w / RATIO))             # too tall -> trim height
    off = 0 if anchor == "top" else (h - new) // 2
    return im.crop((0, off, w, off + new))


def main():
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("src"); ap.add_argument("name", nargs="?")
    ap.add_argument("--page", type=int, default=1)
    ap.add_argument("--box", default="0,0,1,1")
    ap.add_argument("--anchor", choices=("top", "center"), default="top")
    ap.add_argument("--no-trim", action="store_true")
    ap.add_argument("--inspect", action="store_true")
    ap.add_argument("-h", "--help", action="store_true")
    a = ap.parse_args()
    if a.help:
        sys.exit(__doc__)

    im = load(a.src, a.page)
    if not a.no_trim:
        im = trim(im)
    W, H = im.size

    if a.inspect:
        g = im.copy(); d = ImageDraw.Draw(g)
        for i in range(1, 10):                   # decile rules, to read off --box
            y = H * i // 10
            d.line([(0, y), (W, y)], fill=(255, 0, 0), width=max(2, H // 500))
            d.text((6, y + 4), f"{i/10:.1f}", fill=(255, 0, 0))
        p = os.path.join(tempfile.mkdtemp(prefix="inspect-"), "ruler.png")
        g.save(p); subprocess.run(["open", p])
        print(f"{W}x{H} after trim; ruler at {p}")
        return

    if not a.name:
        sys.exit("need an output name (or pass --inspect)")

    l, t, r, b = (float(x) for x in a.box.split(","))
    im = im.crop((int(W * l), int(H * t), int(W * r), int(H * b)))
    boxed = im.size
    im = to_ratio(im, a.anchor)
    im = im.resize((OUT_W, int(round(OUT_W / RATIO))), Image.LANCZOS)

    os.makedirs(OUT_DIR, exist_ok=True)
    dst = os.path.join(OUT_DIR, f"{a.name}.png")
    im.save(dst, "PNG", optimize=True)
    kb = os.path.getsize(dst) / 1024
    print(f"{W}x{H} -> box {boxed[0]}x{boxed[1]} -> 4:3 -> {im.size[0]}x{im.size[1]}  {kb:.0f} KB")
    print(f"wrote {os.path.relpath(dst, ROOT)}")
    if kb > 200:
        print("  (over 200 KB — re-export as JPEG if it is a photo)")
    print(f"\nWire it up:  thumb: /assets/pubs/{a.name}.png")


if __name__ == "__main__":
    main()
