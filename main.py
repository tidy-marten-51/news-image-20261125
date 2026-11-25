#!/usr/bin/env python3
"""Draw a newspaper front page summing up world news of Wednesday 25 November 2026.

Pure Python 3 standard library: a tiny canvas, a 5x7 bitmap font drawn as filled
rectangles, and a hand-written PNG encoder (zlib + struct). No network, no random
numbers, no timestamps anywhere in the image, so two runs are byte-identical.

Run:  MAKEFUN_OUTPUT_DIR=out python3 main.py   -> writes out/entry.png
"""

import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- colours ----
PAPER = b"\xf8\xf3\xe8"   # warm newsprint
INK = b"\x16\x16\x16"    # near-black
RED = b"\xa8\x1e\x23"    # headline red
BLUE = b"\x1f\x3a\x5f"    # deep blue
SKY = b"\xbc\xd3\xe8"    # pale sky
STEEL = b"\x5b\x6b\x7d"  # building grey-blue
GREY = b"\x5c\x5c\x5c"
LIGHT = b"\xe9\xe1\xcd"   # light rule / panel fill
GREEN = b"\x2e\x7d\x32"
BROWN = b"\x7a\x4a\x21"
GOLD = b"\xc9\x8a\x1b"
WAVE = b"\x2f\x6f\xb2"
WHITE = b"\xff\xff\xff"

# ------------------------------------------------------------- 5x7 font ----
# Each glyph: 7 rows of 5 bits. Uppercase letters, digits and punctuation.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "*": ("00000", "10101", "01110", "11111", "01110", "10101", "00000"),
}

BLANK = ("00000",) * 7


# ---------------------------------------------------------------- canvas ----
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(bg * (w * h))

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i:i + 3] = c

    def rect(self, x, y, w, h, c):
        # A colour must be exactly 3 bytes: a longer value would silently
        # resize the bytearray on slice assignment and corrupt every row.
        assert len(c) == 3, "colour must be 3 bytes"
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = c * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + (x1 - x0) * 3] = row

    def hline(self, x, y, w, c, thick=1):
        self.rect(x, y, w, thick, c)

    def vline(self, x, y, h, c, thick=1):
        self.rect(x, y, thick, h, c)

    def line(self, x1, y1, x2, y2, c, thick=1):
        dx = x2 - x1
        dy = y2 - y1
        steps = max(abs(dx), abs(dy), 1)
        half = thick // 2
        for s in range(steps + 1):
            x = int(round(x1 + dx * s / steps))
            y = int(round(y1 + dy * s / steps))
            self.rect(x - half, y - half, thick, thick, c)

    def circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = math.isqrt(max(0, r * r - dy * dy))
            self.rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def ring(self, cx, cy, r, c, thick=2):
        for dy in range(-r, r + 1):
            dx = math.isqrt(max(0, r * r - dy * dy))
            self.rect(cx - dx, cy + dy, thick, 1, c)
            self.rect(cx + dx - thick + 1, cy + dy, thick, 1, c)
        for dx in range(-r, r + 1):
            dy = math.isqrt(max(0, r * r - dx * dx))
            self.rect(cx + dx, cy - dy, 1, thick, c)
            self.rect(cx + dx, cy + dy - thick + 1, 1, thick, c)

    def tri(self, pts, c):
        (x1, y1), (x2, y2), (x3, y3) = sorted(pts, key=lambda p: p[1])

        def edge(xa, ya, xb, yb, y):
            if yb == ya:
                return float(xa)
            return xa + (xb - xa) * (y - ya) / (yb - ya)

        for y in range(y1, y3 + 1):
            if y < y2:
                xa = edge(x1, y1, x2, y2, y)
                xb = edge(x1, y1, x3, y3, y)
            else:
                xa = edge(x2, y2, x3, y3, y)
                xb = edge(x1, y1, x3, y3, y)
            x0 = int(min(xa, xb))
            x1x = int(max(xa, xb))
            self.rect(x0, y, x1x - x0 + 1, 1, c)

    # ------------------------------------------------------------ text ----
    def text_w(self, s, scale):
        return len(s) * 6 * scale - scale

    def text(self, x, y, s, scale, c, bold=False):
        cx = x
        off = max(1, scale // 3) if bold else 0
        for ch in s:
            g = FONT.get(ch, BLANK)
            for r, row in enumerate(g):
                for col, bit in enumerate(row):
                    if bit == "1":
                        self.rect(cx + col * scale, y + r * scale, scale, scale, c)
                        if off:
                            self.rect(cx + col * scale + off, y + r * scale,
                                     scale, scale, c)
            cx += 6 * scale
        return cx

    def centered(self, y, s, scale, c, bold=False):
        self.text((self.w - self.text_w(s, scale)) // 2, y, s, scale, c, bold)

    def wrap(self, s, scale, maxw):
        lines = []
        cur = ""
        for word in s.split(" "):
            trial = (cur + " " + word).strip() if cur else word
            if self.text_w(trial, scale) <= maxw:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, scale, maxw, c, leading=None, bold=False):
        lh = leading if leading is not None else 9 * scale
        for ln in self.wrap(s, scale, maxw):
            self.text(x, y, ln, scale, c, bold)
            y += lh
        return y


# ------------------------------------------------------------ PNG writer ----
def encode_png(w, h, buf):
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)  # filter: none
        raw += buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", comp) + chunk(b"IEND", b""))


# --------------------------------------------------------- illustrations ----
def draw_building(cv, x, y, w, h):
    """Government hall with columns and a red flag: the investigation story."""
    cv.rect(x, y, w, h, SKY)
    cv.rect(x, y + h - 26, w, 26, LIGHT)
    bx, bw = x + 18, w - 36
    base_y = y + h - 26
    # steps
    cv.rect(bx - 8, base_y - 6, bw + 16, 6, STEEL)
    cv.rect(bx - 4, base_y - 12, bw + 8, 6, STEEL)
    # columns
    cv.rect(bx, base_y - 96, bw, 84, STEEL)
    for i in range(5):
        cx = bx + 12 + i * ((bw - 24) // 4)
        cv.rect(cx, base_y - 90, 10, 78, WHITE)
    # pediment
    cv.tri([(bx - 6, base_y - 96), (bx + bw + 6, base_y - 96),
            (bx + bw // 2, base_y - 128)], STEEL)
    cv.tri([(bx + 8, base_y - 100), (bx + bw - 8, base_y - 100),
            (bx + bw // 2, base_y - 122)], RED)
    # flag pole + flag
    cv.rect(x + w - 34, y + 8, 3, 74, INK)
    cv.rect(x + w - 31, y + 8, 34, 22, RED)
    cv.text(x + w - 26, y + 13, "*", 1, GOLD)
    # door
    cv.rect(bx + bw // 2 - 12, base_y - 44, 24, 32, INK)


def draw_phone(cv, x, y, w, h):
    """Smartphone with a circuit on its screen: the Huawei verdict."""
    cv.rect(x, y, w, h, LIGHT)
    px, py, pw, ph = x + w // 2 - 52, y + 10, 104, h - 20
    cv.rect(px, py, pw, ph, INK)
    cv.rect(px + 6, py + 12, pw - 12, ph - 30, SKY)
    # circuit traces on the screen
    for i, yy in enumerate(range(py + 22, py + ph - 40, 16)):
        cv.hline(px + 14, yy, pw - 28 - i * 6, BLUE, 3)
        cv.circle(px + pw - 20 - i * 6, yy, 4, RED)
    cv.circle(px + pw // 2, py + ph - 12, 5, WHITE)
    cv.text(x + 8, y + h - 16, "GUILTY", 2, RED, bold=True)


def draw_turkey(cv, x, y, w, h):
    """A pardoned turkey: fanned tail, round body, small head."""
    cv.rect(x, y, w, h, LIGHT)
    cx, cy = x + w // 2, y + h - 42
    # tail fan
    for i, ang in enumerate((-52, -26, 0, 26, 52)):
        rad = math.radians(ang)
        tx = cx + int(58 * math.sin(rad))
        ty = cy - 26 - int(58 * math.cos(rad))
        cv.line(cx, cy - 20, tx, ty, BROWN, 9)
        cv.circle(tx, ty, 8, GOLD)
    # body
    cv.circle(cx, cy, 34, BROWN)
    cv.circle(cx - 12, cy - 6, 12, GOLD)
    # head + beak + wattle
    cv.circle(cx + 26, cy - 34, 13, BROWN)
    cv.tri([(cx + 36, cy - 36), (cx + 52, cy - 32), (cx + 36, cy - 28)], GOLD)
    cv.rect(cx + 30, cy - 22, 6, 12, RED)
    # legs
    cv.vline(cx - 10, cy + 32, 12, GOLD, 3)
    cv.vline(cx + 10, cy + 32, 12, GOLD, 3)


def draw_chart(cv, x, y, w, h):
    """A share-price line falling after a peak: Nvidia shares fall."""
    cv.rect(x, y, w, h, WHITE)
    cv.rect(x, y, w, h, LIGHT)
    ox, oy = x + 14, y + h - 16
    cv.hline(ox, oy, w - 28, INK, 2)
    cv.vline(ox, y + 12, h - 28, INK, 2)
    pts = [(ox + 6, y + 26), (ox + 34, y + 22), (ox + 62, y + 34),
           (ox + 92, y + 30), (ox + 122, y + 52), (ox + 152, y + 62),
           (ox + 182, y + 78), (ox + 212, y + h - 30)]
    for (ax, ay), (bx, by) in zip(pts, pts[1:]):
        cv.line(ax, ay, bx, by, RED, 4)
    for px, py in pts:
        cv.circle(px, py, 4, RED)
    # down arrow at the end (no invented percentage: the brief gives none)
    ex, ey = pts[-1]
    cv.line(ex, ey, ex - 12, ey - 14, RED, 4)
    cv.line(ex, ey, ex + 2, ey - 16, RED, 4)


def draw_flood(cv, x, y, w, h):
    """A house with flood water lapping at its doorstep: California."""
    cv.rect(x, y, w, h, SKY)
    hx, hy, hw = x + w // 2 - 58, y + 8, 116
    cv.rect(hx, hy + 30, hw, 48, WHITE)
    cv.tri([(hx - 10, hy + 32), (hx + hw + 10, hy + 32), (hx + hw // 2, hy)],
           RED)
    cv.rect(hx + hw // 2 - 10, hy + 52, 20, 26, INK)
    cv.rect(hx + 14, hy + 42, 18, 18, BLUE)
    cv.rect(hx + hw - 32, hy + 42, 18, 18, BLUE)
    # waves covering only the bottom strip, lapping at the doorstep
    for i, wy in enumerate((y + h - 26, y + h - 13, y + h - 2)):
        for wx in range(x, x + w, 22):
            cv.circle(wx + (11 if i % 2 else 0), wy, 11, WAVE)
        cv.rect(x, wy, w, 11, WAVE)


def draw_tanker(cv, x, y, w, h):
    """An oil tanker on the sea beside a spiked naval mine: Hormuz."""
    cv.rect(x, y, w, h, SKY)
    # mine, upper right
    mx, my = x + w - 56, y + 34
    for ang in range(0, 360, 45):
        rad = math.radians(ang)
        cv.line(mx, my, mx + int(26 * math.cos(rad)),
                my + int(26 * math.sin(rad)), INK, 4)
    cv.circle(mx, my, 16, INK)
    cv.circle(mx - 5, my - 5, 5, GREY)
    # tanker hull
    hx, hy = x + 16, y + h - 66
    cv.tri([(hx, hy), (hx + w - 96, hy), (hx + w - 116, hy + 26)], INK)
    cv.rect(hx, hy, w - 96, 26, INK)
    cv.rect(hx + 8, hy - 30, 46, 30, RED)
    cv.rect(hx + 58, hy - 30, 46, 30, GOLD)
    cv.rect(hx + 108, hy - 30, 46, 30, BLUE)
    cv.rect(hx + w - 132, hy - 52, 30, 52, WHITE)
    cv.rect(hx + w - 126, hy - 46, 8, 10, INK)
    cv.rect(hx + w - 112, hy - 46, 8, 10, INK)
    # sea
    for wy in (y + h - 14, y + h - 4):
        for wx in range(x, x + w, 24):
            cv.circle(wx + 12, wy, 10, WAVE)
        cv.rect(x, wy, w, 10, WAVE)


def draw_clock(cv, x, y, w, h):
    """A clock face with five figures beneath it: five women an hour."""
    cv.rect(x, y, w, h, LIGHT)
    cx, cy = x + w // 2, y + 46
    cv.circle(cx, cy, 38, WHITE)
    cv.ring(cx, cy, 38, INK, 3)
    cv.circle(cx, cy, 4, INK)
    cv.line(cx, cy, cx, cy - 26, INK, 4)
    cv.line(cx, cy, cx + 18, cy + 10, INK, 4)
    for ang in (0, 90, 180, 270):
        rad = math.radians(ang)
        cv.circle(cx + int(30 * math.cos(rad)), cy + int(30 * math.sin(rad)),
                  3, RED)
    # five small figures
    for i in range(5):
        fx = x + 30 + i * ((w - 60) // 4)
        fy = y + h - 26
        cv.circle(fx, fy - 14, 7, RED if i == 2 else BLUE)
        cv.rect(fx - 6, fy - 6, 12, 16, RED if i == 2 else BLUE)


# -------------------------------------------------------------- page ----
def story_card(cv, x, y, w, kicker, headline, standfirst, draw_fn):
    """One secondary story: kicker, headline, illustration, standfirst."""
    cv.text(x, y, kicker, 1, RED, bold=True)
    y += 16
    y = cv.para(x, y, headline, 2, w, INK, leading=20, bold=True)
    y += 6
    draw_fn(cv, x, y, w, 118)
    y += 118 + 8
    y = cv.para(x, y, standfirst, 1, w, GREY, leading=10)
    return y


def build_page():
    cv = Canvas(W, H, PAPER)

    # ---- masthead ----
    cv.hline(24, 16, W - 48, INK, 4)
    cv.centered(30, "THE WORLD", 8, INK, bold=True)
    cv.centered(96, "WEDNESDAY 25 NOVEMBER 2026", 2, INK, bold=True)
    cv.hline(24, 124, W - 48, INK, 3)
    cv.hline(24, 130, W - 48, INK, 1)

    # ---- summary strip ----
    cv.centered(146, "CHINA PROBES CHEN JINING - HUAWEI CONVICTED - TURKEYS PARDONED", 1, INK)
    cv.centered(160, "NVIDIA CHIEF BACK - CALIFORNIA FLOODS - HORMUZ TANKERS HIT - UN: FIVE WOMEN AN HOUR", 1, INK)
    cv.hline(24, 178, W - 48, INK, 2)

    # ---- lead story ----
    lx, lw = 24, 596
    cv.text(lx, 196, "LEAD STORY - AP", 1, RED, bold=True)
    y = 214
    for ln in ("CHINA INVESTIGATES", "POLITBURO MEMBER", "CHEN JINING"):
        cv.text(lx, y, ln, 4, INK, bold=True)
        y += 36
    y += 6
    y = cv.para(lx, y,
                "CHINA IS INVESTIGATING CHEN JINING, A POLITBURO MEMBER "
                "AND SHANGHAI PARTY CHIEF.", 2, lw, INK, leading=20)
    y += 10
    cv.text(lx, y, "BEIJING - 25 NOVEMBER 2026", 1, GREY, bold=True)
    draw_building(cv, 644, 196, 356, 250)
    cv.text(644, 452, "BEIJING", 1, GREY)
    cv.hline(24, 482, W - 48, INK, 2)

    # ---- secondary stories, two rows of three ----
    col_w = 312
    gap = 20
    xs = [24, 24 + col_w + gap, 24 + 2 * (col_w + gap)]
    row1_y = 500
    story_card(cv, xs[0], row1_y, col_w, "UNITED STATES - AFP",
               "US JURY CONVICTS HUAWEI OF STEALING TRADE SECRETS",
               "A US JURY FINDS THE CHINESE TELECOM GIANT GUILTY OF "
               "STEALING TRADE SECRETS.", draw_phone)
    story_card(cv, xs[1], row1_y, col_w, "WHITE HOUSE",
               "TRUMP PARDONS THANKSGIVING TURKEYS",
               "PRESIDENT TRUMP PARDONS TURKEYS AT THE WHITE HOUSE "
               "FOR THANKSGIVING.", draw_turkey)
    story_card(cv, xs[2], row1_y, col_w, "MARKETS",
               "NVIDIA CHIEF BACK IN THERAPY, SHARES FALL",
               "JENSEN HUANG IS REINSTATED AS CHIEF EXECUTIVE AND TELLS "
               "STAFF HE IS IN THERAPY. SHARES FALL.", draw_chart)
    cv.hline(24, 742, W - 48, INK, 1)

    row2_y = 756
    story_card(cv, xs[0], row2_y, col_w, "WEATHER",
               "EXTREME FLOODING THREATENS CALIFORNIA",
               "CALIFORNIA BRACES FOR EXTREME FLOODING.", draw_flood)
    story_card(cv, xs[1], row2_y, col_w, "MIDDLE EAST",
               "THREE OIL TANKERS HIT BY MINES IN HORMUZ",
               "THREE OIL TANKERS ARE HIT BY NAVAL MINES IN THE STRAIT "
               "OF HORMUZ, IRAN SAYS.", draw_tanker)
    story_card(cv, xs[2], row2_y, col_w, "UNITED NATIONS",
               "FIVE WOMEN KILLED EACH HOUR BY RELATIVES",
               "FIVE WOMEN ARE KILLED EACH HOUR BY RELATIVES IN 2025, "
               "THE UNITED NATIONS SAYS.", draw_clock)

    # ---- footer ----
    cv.hline(24, 994, W - 48, INK, 2)
    cv.centered(1004, "ALL STORIES REPORTED 25 NOVEMBER 2026 - SOURCES: AP, AFP", 1, GREY)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build_page()
    data = encode_png(W, H, cv.buf)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as f:
        f.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))


if __name__ == "__main__":
    main()
