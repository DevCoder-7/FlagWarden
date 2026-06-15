from __future__ import annotations

import struct
import zlib
from pathlib import Path

OUTPUT_DIR = Path("assets/logo")
SVG_PATH = OUTPUT_DIR / "flagwarden-logo.svg"
PNG_PATH = OUTPUT_DIR / "flagwarden-logo.png"
SIZE = 1024

NAVY = (15, 23, 42)
PANEL = (19, 35, 63)
TEAL = (20, 184, 166)
WHITE = (248, 250, 252)
MUTED = (148, 163, 184)
GOLD = (250, 204, 21)
RED = (248, 113, 113)


FONT_5X7 = {
    "F": [
        "11111",
        "10000",
        "10000",
        "11110",
        "10000",
        "10000",
        "10000",
    ],
    "W": [
        "10001",
        "10001",
        "10001",
        "10101",
        "10101",
        "11011",
        "10001",
    ],
}


def make_canvas(color: tuple[int, int, int]) -> list[list[tuple[int, int, int]]]:
    return [[color for _ in range(SIZE)] for _ in range(SIZE)]


def fill_rect(
    image: list[list[tuple[int, int, int]]],
    x0: int,
    y0: int,
    x1: int,
    y1: int,
    color: tuple[int, int, int],
) -> None:
    for y in range(max(0, y0), min(SIZE, y1)):
        row = image[y]
        for x in range(max(0, x0), min(SIZE, x1)):
            row[x] = color


def fill_circle(
    image: list[list[tuple[int, int, int]]],
    cx: int,
    cy: int,
    radius: int,
    color: tuple[int, int, int],
) -> None:
    radius_sq = radius * radius
    for y in range(max(0, cy - radius), min(SIZE, cy + radius + 1)):
        dy = y - cy
        row = image[y]
        for x in range(max(0, cx - radius), min(SIZE, cx + radius + 1)):
            dx = x - cx
            if dx * dx + dy * dy <= radius_sq:
                row[x] = color


def fill_polygon(
    image: list[list[tuple[int, int, int]]],
    points: list[tuple[int, int]],
    color: tuple[int, int, int],
) -> None:
    min_y = max(0, min(y for _, y in points))
    max_y = min(SIZE - 1, max(y for _, y in points))
    for y in range(min_y, max_y + 1):
        intersections: list[float] = []
        for index, (x1, y1) in enumerate(points):
            x2, y2 = points[(index + 1) % len(points)]
            if y1 == y2:
                continue
            if min(y1, y2) <= y < max(y1, y2):
                intersections.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        intersections.sort()
        for start, end in zip(intersections[0::2], intersections[1::2], strict=False):
            fill_rect(image, int(start), y, int(end) + 1, y + 1, color)


def draw_bitmap_text(
    image: list[list[tuple[int, int, int]]],
    text: str,
    x: int,
    y: int,
    scale: int,
    color: tuple[int, int, int],
) -> None:
    cursor = x
    for char in text:
        glyph = FONT_5X7[char]
        for row_index, row in enumerate(glyph):
            for col_index, pixel in enumerate(row):
                if pixel == "1":
                    fill_rect(
                        image,
                        cursor + col_index * scale,
                        y + row_index * scale,
                        cursor + (col_index + 1) * scale,
                        y + (row_index + 1) * scale,
                        color,
                    )
        cursor += 6 * scale


def png_chunk(chunk_type: bytes, data: bytes) -> bytes:
    return (
        struct.pack(">I", len(data))
        + chunk_type
        + data
        + struct.pack(">I", zlib.crc32(chunk_type + data) & 0xFFFFFFFF)
    )


def write_png(path: Path, image: list[list[tuple[int, int, int]]]) -> None:
    raw_rows = []
    for row in image:
        raw_rows.append(b"\x00" + b"".join(bytes(pixel) for pixel in row))
    raw = b"".join(raw_rows)
    png = (
        b"\x89PNG\r\n\x1a\n"
        + png_chunk(b"IHDR", struct.pack(">IIBBBBB", SIZE, SIZE, 8, 2, 0, 0, 0))
        + png_chunk(b"IDAT", zlib.compress(raw, level=9))
        + png_chunk(b"IEND", b"")
    )
    path.write_bytes(png)


def build_png() -> None:
    image = make_canvas(NAVY)
    fill_circle(image, 512, 512, 390, PANEL)
    fill_polygon(
        image,
        [(512, 150), (790, 268), (790, 485), (512, 842), (234, 485), (234, 268)],
        TEAL,
    )
    fill_polygon(
        image,
        [(512, 226), (714, 312), (714, 480), (512, 744), (310, 480), (310, 312)],
        NAVY,
    )
    fill_rect(image, 356, 348, 388, 636, MUTED)
    fill_polygon(image, [(388, 350), (610, 402), (388, 454)], GOLD)
    fill_polygon(image, [(388, 454), (548, 493), (388, 532)], RED)
    draw_bitmap_text(image, "FW", 360, 596, 34, WHITE)
    fill_rect(image, 384, 860, 640, 886, GOLD)
    write_png(PNG_PATH, image)


def build_svg() -> None:
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024"
  viewBox="0 0 1024 1024" role="img" aria-labelledby="title desc">
  <title id="title">FlagWarden logo</title>
  <desc id="desc">A square dark shield logo with a CTF flag and FW initials.</desc>
  <rect width="1024" height="1024" rx="190" fill="#0f172a"/>
  <circle cx="512" cy="512" r="390" fill="#13233f"/>
  <path d="M512 150 790 268v217L512 842 234 485V268L512 150Z" fill="#14b8a6"/>
  <path d="M512 226 714 312v168L512 744 310 480V312l202-86Z" fill="#0f172a"/>
  <rect x="356" y="348" width="32" height="288" rx="16" fill="#94a3b8"/>
  <path d="M388 350 610 402 388 454Z" fill="#facc15"/>
  <path d="M388 454 548 493 388 532Z" fill="#f87171"/>
  <text x="512" y="800" text-anchor="middle" fill="#f8fafc"
    font-family="Arial, Helvetica, sans-serif" font-size="210" font-weight="800">FW</text>
  <rect x="384" y="860" width="256" height="26" rx="13" fill="#facc15"/>
</svg>
"""
    SVG_PATH.write_text(svg, encoding="utf-8")


def main() -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    build_svg()
    build_png()
    print(f"Created {SVG_PATH}")
    print(f"Created {PNG_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
