"""
Generates all QuizGenie icons from a single set of normalized coordinates.
Produces:
  static/favicon.svg          (vector, any size)
  static/apple-touch-icon.png (180x180  – iOS home screen)
  static/icon-192.png         (192x192  – PWA manifest)
  static/icon-512.png         (512x512  – PWA manifest hi-res)

Run with:  python generate_icons.py
Requires:  Pillow  (pip install Pillow)
"""

import os
from PIL import Image, ImageDraw

# ── Brand colour ───────────────────────────────────────────────────────────
BLUE = (13, 110, 253)       # #0d6efd  Bootstrap primary
WHITE = (255, 255, 255)

OUT = os.path.join(os.path.dirname(__file__), "static")

# ── Design in normalised 0–100 units ──────────────────────────────────────
# All shapes are defined here once; both SVG and PNG renderers use them.

# Background rounded-corner radius as % of icon size
BG_RADIUS_PCT = 0.22

# Mortarboard board (diamond / rhombus)
# Four corners in normalised coords: top, right, bottom, left
DIAMOND = [
    (50.0, 22.0),   # top
    (80.0, 34.0),   # right
    (50.0, 46.0),   # bottom
    (20.0, 34.0),   # left
]

# Cap body (trapezoid below the diamond)
CAP = [
    (31.0, 49.0),   # top-left
    (69.0, 49.0),   # top-right
    (76.0, 74.0),   # bottom-right
    (24.0, 74.0),   # bottom-left
]

# Tassel: a thin vertical rectangle hanging from the right diamond corner
# (right diamond corner is at 80, 34)
TASSEL_RECT = (78.0, 34.0, 82.5, 62.0)   # x0, y0, x1, y1
TASSEL_BOB  = (74.5, 62.0, 86.0, 73.5)   # bounding box of the end circle


# ── PNG renderer (Pillow) ─────────────────────────────────────────────────

def scale(pts, s):
    """Scale a list of (x, y) tuples from 0-100 space to pixel space."""
    return [(x * s / 100, y * s / 100) for x, y in pts]

def scale_rect(r, s):
    x0, y0, x1, y1 = r
    f = s / 100
    return [x0 * f, y0 * f, x1 * f, y1 * f]

def make_png(size: int) -> Image.Image:
    img = Image.new("RGB", (size, size), BLUE)
    draw = ImageDraw.Draw(img)

    # Rounded background (overwrite with blue, then draw shapes on top)
    radius = int(size * BG_RADIUS_PCT)
    # Fill corners with white first so we can mask them back to blue
    # Simpler: draw a white full rect, then re-draw a blue rounded rect
    draw.rectangle([0, 0, size, size], fill=WHITE)
    draw.rounded_rectangle([0, 0, size - 1, size - 1], radius=radius, fill=BLUE)

    s = size
    draw.polygon(scale(DIAMOND, s), fill=WHITE)
    draw.polygon(scale(CAP, s), fill=WHITE)
    draw.rectangle(scale_rect(TASSEL_RECT, s), fill=WHITE)
    draw.ellipse(scale_rect(TASSEL_BOB, s), fill=WHITE)

    return img


def save_png(path: str, size: int) -> None:
    img = make_png(size)
    img.save(path, "PNG", optimize=True)
    print(f"  wrote {path}  ({size}×{size})")


# ── SVG renderer ───────────────────────────────────────────────────────────

def pts_to_svg(pts):
    return " ".join(f"{x:.2f},{y:.2f}" for x, y in pts)

def make_svg() -> str:
    # SVG uses the same 100×100 coordinate space directly
    vb = 100
    rx = vb * BG_RADIUS_PCT

    d_pts = pts_to_svg(DIAMOND)
    c_pts = pts_to_svg(CAP)

    tx0, ty0, tx1, ty1 = TASSEL_RECT
    bx0, by0, bx1, by1 = TASSEL_BOB
    bcx = (bx0 + bx1) / 2
    bcy = (by0 + by1) / 2
    br  = (bx1 - bx0) / 2

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {vb} {vb}">
  <rect width="{vb}" height="{vb}" rx="{rx:.2f}" fill="#0d6efd"/>
  <polygon points="{d_pts}" fill="white"/>
  <polygon points="{c_pts}" fill="white"/>
  <rect x="{tx0:.2f}" y="{ty0:.2f}" width="{tx1-tx0:.2f}" height="{ty1-ty0:.2f}" fill="white"/>
  <circle cx="{bcx:.2f}" cy="{bcy:.2f}" r="{br:.2f}" fill="white"/>
</svg>
"""


def save_svg(path: str) -> None:
    with open(path, "w") as f:
        f.write(make_svg())
    print(f"  wrote {path}  (SVG)")


# ── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    print("Generating QuizGenie icons…")
    save_svg(os.path.join(OUT, "favicon.svg"))
    save_png(os.path.join(OUT, "apple-touch-icon.png"), 180)
    save_png(os.path.join(OUT, "icon-192.png"), 192)
    save_png(os.path.join(OUT, "icon-512.png"), 512)
    print("Done.")
