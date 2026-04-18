"""
One-time script to generate PWA icons from the QuizGenie brand colors.
Produces apple-touch-icon.png (180x180) and icon-512.png (512x512).

Run with:  python generate_icons.py
Requires no third-party dependencies.
"""

import os
import struct
import zlib
import math

# QuizGenie brand blue  (#0d6efd)
BG_R, BG_G, BG_B = 13, 110, 253

OUT_DIR = os.path.join(os.path.dirname(__file__), "static")


def make_png(width: int, height: int, pixels: list[tuple[int, int, int]]) -> bytes:
    """Encode a list of (r, g, b) pixels into a minimal PNG bytestring."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        raw = tag + data
        return (
            struct.pack(">I", len(data))
            + raw
            + struct.pack(">I", zlib.crc32(raw) & 0xFFFFFFFF)
        )

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(
        b"IHDR",
        struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0),
    )

    raw_rows = bytearray()
    for y in range(height):
        raw_rows.append(0)  # filter type: None
        for x in range(width):
            r, g, b = pixels[y * width + x]
            raw_rows += bytes([r, g, b])

    idat = chunk(b"IDAT", zlib.compress(bytes(raw_rows), 9))
    iend = chunk(b"IEND", b"")
    return sig + ihdr + idat + iend


def draw_icon(size: int) -> list[tuple[int, int, int]]:
    """
    Draw the QuizGenie icon at the given square pixel size.
    Blue background + simple white mortarboard shape.
    """
    pixels = [(BG_R, BG_G, BG_B)] * (size * size)

    cx = size / 2
    cy = size / 2

    # Scale factor: design is normalised to a 32x32 grid
    scale = size / 32.0

    def set_px(x: int, y: int) -> None:
        if 0 <= x < size and 0 <= y < size:
            pixels[y * size + x] = (255, 255, 255)

    def fill_rect(fx: float, fy: float, fw: float, fh: float) -> None:
        x0 = round(fx * scale)
        y0 = round(fy * scale)
        x1 = round((fx + fw) * scale)
        y1 = round((fy + fh) * scale)
        for yy in range(y0, y1):
            for xx in range(x0, x1):
                set_px(xx, yy)

    def fill_diamond(fx: float, fy: float, fw: float, fh: float) -> None:
        """Fill an axis-aligned ellipse (approximated as filled diamond)."""
        x0 = fx * scale
        y0 = fy * scale
        rx = (fw / 2) * scale
        ry = (fh / 2) * scale
        ccx = x0 + rx
        ccy = y0 + ry
        for yy in range(round(y0), round(y0 + fh * scale) + 1):
            for xx in range(round(x0), round(x0 + fw * scale) + 1):
                dx = (xx - ccx) / rx if rx else 0
                dy = (yy - ccy) / ry if ry else 0
                if dx * dx + dy * dy <= 1.0:
                    set_px(xx, yy)

    # ── Mortarboard top (diamond / rhombus shape) ──────────────────────────
    # SVG path approximation: a wide flat diamond centred at (16, 8)
    fill_diamond(6, 3.5, 20, 7)

    # ── Vertical pole ──────────────────────────────────────────────────────
    fill_rect(15, 10, 2, 5)

    # ── Cap (tassel base) ──────────────────────────────────────────────────
    fill_rect(13, 15, 6, 2)

    # ── Hat brim / lower band ──────────────────────────────────────────────
    fill_diamond(7, 14, 18, 5)

    return pixels


def save(path: str, size: int) -> None:
    pixels = draw_icon(size)
    png_bytes = make_png(size, size, pixels)
    with open(path, "wb") as f:
        f.write(png_bytes)
    print(f"  wrote {path}  ({size}×{size}, {len(png_bytes):,} bytes)")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    print("Generating QuizGenie PWA icons...")
    save(os.path.join(OUT_DIR, "apple-touch-icon.png"), 180)
    save(os.path.join(OUT_DIR, "icon-192.png"), 192)
    save(os.path.join(OUT_DIR, "icon-512.png"), 512)
    print("Done.")
