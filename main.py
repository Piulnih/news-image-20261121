#!/usr/bin/env python3
"""Sum up 21 November 2026's world news in one image.

A front page drawn from scratch with the Python standard library only:
a tiny 5x7 bitmap font, a small raster canvas, and a hand-written PNG
encoder. No network, no files read, no randomness, no clock: the same
bytes come out of every run.
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (247, 242, 227)
INK = (20, 20, 20)
RED = (179, 35, 27)
BLUE = (29, 78, 137)
TEAL = (15, 118, 110)
GREEN = (34, 120, 60)
ORANGE = (214, 110, 20)
GREY = (110, 108, 100)
LIGHT = (232, 226, 208)
GOLD = (212, 160, 23)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, "." off, "#" on. Text is rendered in capitals.

FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", "..#..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", "..#..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "-": (".....", ".....", ".....", ".####", ".....", ".....", "....."),
    "\u2014": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#.##", "#..##"),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "*": (".....", "#.#.#", ".###.", "#.#.#", ".....", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "\u2022": (".....", ".....", ".###.", ".###.", ".###.", ".....", "....."),
    "\u00d7": (".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "....."),
    "\u00b7": (".....", ".....", ".....", ".##..", ".##..", ".....", "....."),
    "\u2192": (".....", "..#..", "...#.", "#####", "...#.", "..#..", "....."),
    "\u20ac": (".###.", "#...#", "#....", "####.", "#....", "#...#", ".###."),
}

CHAR_W = 6  # glyph cell width in font units (5 + 1 gap)


def text_width(s, scale):
    return max(0, len(s) * CHAR_W * scale - scale)


def wrap_text(s, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w pixels."""
    lines = []
    for para in s.split("\n"):
        line = ""
        for word in para.split(" "):
            trial = word if not line else line + " " + word
            if text_width(trial, scale) <= max_w or not line:
                line = trial
            else:
                lines.append(line)
                line = word
        if line:
            lines.append(line)
    return lines


# -------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i], self.px[i + 1], self.px[i + 2] = color

    def fill_rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        r, g, b = color
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i], self.px[i + 1], self.px[i + 2] = r, g, b

    def hline(self, x, y, w, color, thick=1):
        self.fill_rect(x, y, w, thick, color)

    def vline(self, x, y, h, color, thick=1):
        self.fill_rect(x, y, thick, h, color)

    def rect(self, x, y, w, h, color, thick=1):
        self.hline(x, y, w, color, thick)
        self.hline(x, y + h - thick, w, color, thick)
        self.vline(x, y, h, color, thick)
        self.vline(x + w - thick, y, h, color, thick)

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        x, y = x0, y0
        while True:
            self.fill_rect(x - thick // 2, y - thick // 2, thick, thick, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x += sx
            if e2 < dx:
                err += dx
                y += sy

    def _circle_rows(self, cx, cy, r):
        rows = []
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            rows.append((cy + dy, cx - dx, cx + dx))
        return rows

    def fill_circle(self, cx, cy, r, color):
        for y, x0, x1 in self._circle_rows(cx, cy, r):
            self.hline(x0, y, x1 - x0 + 1, color)

    def circle(self, cx, cy, r, color, thick=1):
        for y, x0, x1 in self._circle_rows(cx, cy, r):
            self.fill_rect(x0, y, thick, 1, color)
            self.fill_rect(x1 - thick + 1, y, thick, 1, color)

    def fill_poly(self, pts, color):
        # Even-odd scanline fill for a simple polygon.
        ys = [p[1] for p in pts]
        for y in range(min(ys), max(ys) + 1):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for j in range(0, len(xs) - 1, 2):
                self.hline(int(xs[j]), y, max(1, int(xs[j + 1]) - int(xs[j])), color)

    def star(self, cx, cy, r_out, r_in, points, color, rot=-90):
        pts = []
        for i in range(points * 2):
            r = r_out if i % 2 == 0 else r_in
            a = math.radians(rot + i * 180 / points)
            pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
        self.fill_poly(pts, color)

    def text(self, x, y, s, scale, color, align="l"):
        if align == "c":
            x -= text_width(s, scale) // 2
        elif align == "r":
            x -= text_width(s, scale)
        cx = x
        for ch in s.upper():
            glyph = FONT.get(ch, FONT[" "])
            for row, bits in enumerate(glyph):
                for col, bit in enumerate(bits):
                    if bit == "#":
                        self.fill_rect(
                            cx + col * scale, y + row * scale, scale, scale, color
                        )
            cx += CHAR_W * scale
        return cx

    def text_block(self, x, y, s, scale, color, max_w, leading=None, align="l"):
        if leading is None:
            leading = 9 * scale
        yy = y
        for line in wrap_text(s, scale, max_w):
            self.text(x, yy, line, scale, color, align=align)
            yy += leading
        return yy


# ----------------------------------------------------------------- png
def _chunk(kind, data):
    return (
        struct.pack(">I", len(data))
        + kind
        + data
        + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    )


def write_png(path, canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for y in range(canvas.h):
        raw.append(0)
        raw += canvas.px[y * stride : (y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    data = (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(bytes(raw), 6))
        + _chunk(b"IEND", b"")
    )
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


# ------------------------------------------------------- illustrations
def draw_skyline_blast(c, x, y, w, h, color):
    """A city skyline under a double explosion: the Kryvyi Rih strike."""
    base = y + h - 4
    heights = (34, 52, 28, 44, 60, 38, 48, 30)
    bw = w // len(heights)
    for i, hh in enumerate(heights):
        bx = x + i * bw + 2
        c.fill_rect(bx, base - hh, bw - 4, hh, color)
        for wy in range(base - hh + 6, base - 6, 10):
            c.fill_rect(bx + 4, wy, 4, 5, PAPER)
    # Two blast stars above the skyline, one higher than the other.
    c.star(x + w // 3, y + 12, 16, 6, 8, ORANGE)
    c.star(x + w // 3, y + 12, 8, 3, 8, RED)
    c.star(x + 2 * w // 3, y + 22, 12, 5, 8, ORANGE)
    c.star(x + 2 * w // 3, y + 22, 6, 2, 8, RED)
    # Smoke puffs.
    c.fill_circle(x + w // 3 - 18, y + 8, 6, GREY)
    c.fill_circle(x + 2 * w // 3 + 20, y + 16, 5, GREY)


def draw_globe_flame(c, x, y, w, h, color):
    """A globe with a flame crossed out: fossil fuels dropped from COP31."""
    cx, cy, r = x + w // 2 - 40, y + h // 2, 28
    c.circle(cx, cy, r, color, 3)
    for k in range(1, 3):
        c.line(cx - r + k * (2 * r) // 3, cy - r, cx - r + k * (2 * r) // 3, cy + r, color, 2)
    c.line(cx - r, cy, cx + r, cy, color, 2)
    c.fill_circle(cx - 8, cy - 8, 5, TEAL)
    c.fill_circle(cx + 9, cy + 7, 6, TEAL)
    fx, fy = x + w - 52, y + h // 2
    c.fill_poly(
        [(fx, fy - 18), (fx + 11, fy - 2), (fx + 7, fy + 9), (fx + 13, fy + 13),
         (fx + 2, fy + 20), (fx - 9, fy + 13), (fx - 5, fy + 4)],
        ORANGE,
    )
    c.line(fx - 18, fy - 24, fx + 18, fy + 24, RED, 4)
    c.line(fx + 18, fy - 24, fx - 18, fy + 24, RED, 4)


def draw_badge(c, x, y, w, h, color):
    """A police badge with a star: the cartel boss capture."""
    cx, cy = x + w // 2, y + h // 2
    c.star(cx, cy, 26, 21, 5, GOLD, rot=-90)
    c.fill_circle(cx, cy, 12, BLUE)
    c.star(cx, cy, 9, 4, 5, PAPER)
    c.line(x + 8, y + h - 6, x + w - 8, y + h - 6, GREY, 2)


def draw_flame(c, x, y, w, h, color):
    """A big flame over a base: the Gulf escalation."""
    cx, base = x + w // 2, y + h - 6
    c.fill_poly(
        [(cx, y + 2), (cx + 16, y + 22), (cx + 10, y + 34), (cx + 20, y + 42),
         (cx + 4, y + h - 10), (cx - 14, y + h - 10), (cx - 8, y + 40),
         (cx - 16, y + 24)],
        ORANGE,
    )
    c.fill_poly(
        [(cx, y + 22), (cx + 8, y + 34), (cx + 4, y + 42), (cx, y + h - 14),
         (cx - 6, y + h - 14), (cx - 4, y + 40), (cx - 8, y + 32)],
        RED,
    )
    c.fill_rect(x + 10, base, w - 20, 4, color)


def draw_aid_bars(c, x, y, w, h, color):
    """Three rising bars in EU blue with a gold star: record aid to Kyiv."""
    bw = 26
    heights = (12, 20, 30)
    for i, hh in enumerate(heights):
        bx = x + 14 + i * (bw + 16)
        c.fill_rect(bx, y + h - 8 - hh, bw, hh, BLUE)
    c.star(x + 14 + 2 * (bw + 16) + bw // 2, y + 8, 8, 3, 5, GOLD)
    c.text(x + w - 78, y + 2, "7.9 BN", 2, BLUE)


def draw_rubble(c, x, y, w, h, color):
    """Broken walls and a tilted slab: Gaza's rubble and the food truck."""
    base = y + h - 4
    c.fill_rect(x + 8, base - 34, 60, 34, color)
    c.fill_rect(x + 8, base - 34, 60, 6, GREY)
    c.fill_rect(x + 84, base - 22, 46, 22, GREY)
    c.fill_rect(x + 146, base - 14, 40, 14, color)
    c.fill_poly([(x + 200, base - 30), (x + 250, base - 30), (x + 244, base - 8),
                 (x + 206, base - 8)], ORANGE)
    c.line(x + 210, base - 34, x + 240, base - 34, RED, 3)


def draw_quake(c, x, y, w, h, color):
    """A seismograph zigzag spiking across the strip."""
    mid = y + h // 2
    pts = [
        (x + 4, mid), (x + 30, mid), (x + 44, mid - 8), (x + 58, mid + 8),
        (x + 72, mid - 26), (x + 86, mid + 22), (x + 100, mid - 14),
        (x + 114, mid + 6), (x + 150, mid - 4), (x + 180, mid + 4),
        (x + 210, mid - 30), (x + 224, mid + 26), (x + 238, mid - 10),
        (x + 252, mid + 4), (x + w - 8, mid),
    ]
    for i in range(len(pts) - 1):
        c.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED, 3)
    c.text(x + w - 52, y + 2, "M6.7", 2, RED)


def draw_falling_chart(c, x, y, w, h, color):
    """Axes and a jagged line falling left to right: the market slide."""
    c.line(x, y + h - 8, x + w, y + h - 8, GREY, 2)
    c.line(x, y, x, y + h - 8, GREY, 2)
    pts = [
        (x + 6, y + 8),
        (x + w // 4, y + 14),
        (x + w // 2, y + 26),
        (x + 3 * w // 4, y + 30),
        (x + w - 10, y + h - 16),
    ]
    for i in range(len(pts) - 1):
        c.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], color, 3)
    for px, py in pts:
        c.fill_circle(px, py, 4, color)
    c.text(x + w - 60, y + 2, "CHIPS", 2, color)


# ---------------------------------------------------------------- page
def card(c, x, y, w, h, kicker, headline, sub, art):
    c.rect(x, y, w, h, INK, 2)
    c.text(x + 12, y + 12, kicker, 2, RED)
    yy = y + 36
    for line in wrap_text(headline, 3, w - 24):
        c.text(x + 12, yy, line, 3, INK)
        yy += 26
    c.text_block(x + 12, yy + 6, sub, 2, INK, w - 24, leading=18)
    art(c, x + 12, y + h - 62, w - 24, 50, INK)


def build():
    c = Canvas(W, H, PAPER)
    c.rect(10, 10, W - 20, H - 20, INK, 3)

    # Masthead.
    c.text(512, 32, "THE WORLD IN ONE DAY", 5, INK, align="c")
    c.text(512, 80, "SATURDAY, 21 NOVEMBER 2026", 3, RED, align="c")
    c.hline(28, 116, W - 56, INK, 3)
    c.hline(28, 122, W - 56, INK, 1)

    # Lead: the Kryvyi Rih strike, left; COP31 overtime, right.
    c.text(28, 138, "KRYVYI RIH  \u2022  WAR", 2, RED)
    c.text(28, 162, "DOUBLE-TAP STRIKE", 4, INK)
    c.text(28, 196, "ON KRYVYI RIH", 4, INK)
    c.text_block(
        28, 242,
        "Russian ballistic missiles hit Zelenskyy's hometown "
        "twice: a boy of 7 and a woman of 20 killed, 60 wounded.",
        2, INK, 560, leading=18,
    )
    draw_skyline_blast(c, 60, 300, 520, 128, BLUE)

    c.vline(628, 134, 300, GREY, 2)
    c.text(644, 138, "ANTALYA  \u2022  CLIMATE", 2, RED)
    c.text(644, 162, "COP31 RUNS INTO", 3, INK)
    c.text(644, 190, "OVERTIME", 3, INK)
    c.text_block(
        644, 226,
        "Draft deal drops every mention of fossil fuels as "
        "nearly 200 nations stay deadlocked after two weeks.",
        2, INK, 330, leading=18,
    )
    draw_globe_flame(c, 644, 306, 352, 62, INK)

    c.hline(28, 448, W - 56, INK, 3)

    # Row two.
    card(c, 28, 462, 312, 216, "MEXICO  \u2022  CRIME",
         "EL CHAPO ISIDRO CAPTURED",
         "FBI Top 10 cartel boss seized in Sinaloa with US intelligence help.",
         draw_badge)
    card(c, 356, 462, 312, 216, "GULF  \u2022  CONFLICT",
         "IRAN HITS US BASES",
         "Tehran says it struck bases in Bahrain; Trump weighs new strikes.",
         draw_flame)
    card(c, 684, 462, 312, 216, "EUROPE  \u2022  UKRAINE",
         "EU SENDS RECORD AID",
         "\u20ac7.9bn payment, plus \u20ac1bn more in arms, as a missile lands in Poland.",
         draw_aid_bars)

    # Row three.
    card(c, 28, 692, 312, 216, "GAZA  \u2022  CONFLICT",
         "THREE KILLED IN FOOD TRUCK",
         "Israeli strike hits a food vehicle; 129 bodies pulled from Gaza rubble.",
         draw_rubble)
    card(c, 356, 692, 312, 216, "PERU  \u2022  EARTHQUAKE",
         "M6.7 QUAKE SHAKES PERU",
         "Junin tremor felt in Lima; no casualties reported.",
         draw_quake)
    card(c, 684, 692, 312, 216, "MARKETS  \u2022  SPORT",
         "CHIPS PLUNGE, RUSSELL ON POLE",
         "US stocks slide; Russell takes Las Vegas pole, Verstappen fifth.",
         draw_falling_chart)

    # Footer: the rest of the day.
    c.hline(28, 922, W - 56, INK, 3)
    c.text(512, 934, "ALSO ON 21 NOVEMBER", 2, RED, align="c")
    c.text(512, 958, "UK-EU RESET DEAL AGREED  \u2022  FRANCE SEEKS UN SESSION OVER KYIV EMBASSY STRIKES",
           2, INK, align="c")
    c.text(512, 978, "POISONED LIQUOR KILLS 12 IN INDIA  \u2022  ALCARAZ INTO ATP SEMIS  \u2022  INDIA 486-4 V NZ",
           2, INK, align="c")
    return c


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    size = write_png(target, build())
    if size > 1048576:
        raise SystemExit(f"entry.png too big: {size} bytes")
    print(f"wrote {target} ({size} bytes)")


if __name__ == "__main__":
    main()
