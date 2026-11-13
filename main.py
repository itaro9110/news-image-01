#!/usr/bin/env python3
"""The World in One Page - v2: sixteen stories from Friday 13 Nov 2026.

A newspaper front page: masthead + a strict 4x4 grid of story panels.
Each panel has a region tag, a pictogram, a two-line headline and a
sub-label. Unverified claims are labelled as claims.

Python 3 standard library only. Deterministic: no clock, no randomness,
no network. Writes one PNG (1024x1024) to the output directory.
"""

import os
import struct
import zlib


def out_dir():
    """Output dir: env var, else /output if writable, else /tmp.

    Never a relative default: the grader runs as an unprivileged user
    in a read-only container where only /tmp is writable.
    """
    d = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if d:
        os.makedirs(d, exist_ok=True)
        return d
    if os.path.isdir("/output") and os.access("/output", os.W_OK):
        return "/output"
    return "/tmp"


def png_bytes(rgb, w, h):
    """Encode an RGB bytearray as a PNG (8-bit, colour type 2)."""
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        raw += rgb[y * w * 3:(y + 1) * w * 3]

    def chunk(typ, data):
        out = struct.pack(">I", len(data)) + typ + data
        return out + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


W = 1024
H = 1024
PAPER = (251, 248, 241)
INK = (26, 26, 26)
GREY = (85, 85, 85)
WHITE = (255, 255, 255)


class Canvas:
    """A plain RGB canvas with small drawing helpers."""

    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        for i in range(0, len(self.px), 3):
            self.px[i:i + 3] = bytes(bg)

    def set(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(c)

    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, c)

    def hline(self, x, y, w, c):
        for xx in range(x, x + w):
            self.set(xx, y, c)

    def vline(self, x, y, h, c):
        for yy in range(y, y + h):
            self.set(x, yy, c)

    def frame(self, x, y, w, h, c, t=1):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set(x0, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        x = 0
        y = r
        d = 3 - 2 * r
        while x <= y:
            for px, py in ((cx + x, cy + y), (cx - x, cy + y),
                           (cx + x, cy - y), (cx - x, cy - y),
                           (cx + y, cy + x), (cx - y, cy + x),
                           (cx + y, cy - x), (cx - y, cy - x)):
                self.set(px, py, c)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def disc(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5)
            for xx in range(cx - dx, cx + dx + 1):
                self.set(xx, yy, c)

    def poly(self, pts, c):
        """Fill a polygon with a simple scanline fill."""
        ys = sorted(set(y for _, y in pts))
        for y in range(min(ys), max(ys) + 1):
            xs = []
            for i in range(len(pts)):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % len(pts)]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                for xx in range(int(xs[i]), int(xs[i + 1]) + 1):
                    self.set(xx, y, c)


# 5x7 bitmap font, uppercase only. "#" = ink, "." = empty.
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
    "3": ("11110", "00001", "00001", "01110", "00001", "00001", "11110"),
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
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
}


def text_w(s, scale):
    """Pixel width of a string at a font scale."""
    return len(s) * 6 * scale - scale if s else 0


def draw_text(cv, x, y, s, scale, color):
    """Draw a string left-aligned at (x, y). Unknown glyphs are skipped."""
    cx = x
    for ch in s:
        g = FONT.get(ch)
        if g is None:
            cx += 6 * scale
            continue
        for r in range(7):
            row = g[r]
            for c in range(5):
                if row[c] == "1":
                    cv.rect(cx + c * scale, y + r * scale, scale, scale,
                            color)
        cx += 6 * scale


def draw_text_c(cv, cx, y, s, scale, color):
    """Draw a string horizontally centred on cx."""
    draw_text(cv, cx - text_w(s, scale) // 2, y, s, scale, color)


def draw_masthead(cv):
    """Nameplate, date line, rules and a contents line."""
    draw_text_c(cv, W // 2, 12, "THE WORLD IN ONE PAGE", 4, INK)
    draw_text_c(cv, W // 2, 50, "FRIDAY 13 NOVEMBER 2026", 2, INK)
    cv.hline(24, 78, W - 48, INK)
    cv.hline(24, 80, W - 48, INK)
    cv.hline(24, 84, W - 48, INK)
    draw_text_c(cv, W // 2, 92,
                "16 STORIES - MIDDLE EAST - UKRAINE - BUSINESS - TECH - USA - WORLD",
                1, GREY)


def draw_footer(cv):
    draw_text_c(cv, W // 2, 1006,
                "ALL STORIES AS REPORTED ON 13 NOVEMBER 2026", 1, GREY)


# (tag, accent colour, headline line 1, headline line 2,
#  sub-label line 1, sub-label line 2, pictogram key)
PANELS = [
    ("MIDDLE EAST", (169, 50, 38), "IRAN SAYS IT HIT", "US RADAR IN BAHRAIN",
     "CLAIM, NOT VERIFIED", "", "radar"),
    ("HORMUZ", (17, 120, 100), "LNG TANKER HITS", "NAVAL MINE",
     "LNG TANKER, FRI MORNING", "4 TANKERS HIT WED-THU", "tanker"),
    ("IRAN TALKS", (108, 52, 131), "TRUMP PULLS VANCE", "FROM IRAN TALKS",
     "NO DEAL NEEDED, HE SAYS", "IAEA TALKS STALLED", "talks"),
    ("UKRAINE", (46, 134, 193), "EU JOINS UKRAINE", "PEACE TALKS",
     "KUSHNER, WITKOFF MET PUTIN", "THEN BRIEFED ZELENSKYY", "peace"),
    ("UKRAINE", (46, 134, 193), "BIGGEST PRISONER", "SWAP EYED",
     "LARGEST OF THE WAR", "BEING PREPARED", "swap"),
    ("RUSSIA", (93, 109, 126), "MOSCOW CAR BOMB", "WOUNDS ZAVOROTNIY",
     "UK SANCTIONS 10 OIL FIRMS", "RUSSIA'S LARGEST PRODUCERS", "carbomb"),
    ("BUSINESS", (147, 81, 22), "NVIDIA CEO HUANG", "RESIGNS",
     "CFO KRESS INTERIM CEO", "TRUMP: A TERRIBLE THING", "chip"),
    ("CRYPTO", (183, 149, 11), "DOJ TO SEIZE $1.2B", "IN BINANCE HACK",
     "FBI BLAMES NORTH KOREA", "PYONGYANG DENIES IT", "coin"),
    ("TECH", (20, 143, 119), "MICROSOFT OUTAGE", "HITS WORLDWIDE",
     "BUSINESSES DISRUPTED", "", "cloud"),
    ("USA", (31, 97, 141), "BROOKLYN COLLAPSE", "8 DEAD, 18 HURT",
     "SEARCH ENDED THURSDAY", "INCL. 2 CHILDREN, 2 WORKERS", "collapse"),
    ("VATICAN", (125, 102, 8), "POPE LEO IN PERU", "MEETS SURVIVORS",
     "SURVIVORS OF ABUSE", "", "mitre"),
    ("USA", (31, 97, 141), "VAN HOLLEN TAKES", "ON SCHUMER",
     "LEADERSHIP VOTE 1 DEC", "", "ballot"),
    ("MIDDLE EAST", (169, 50, 38), "HOUTHIS ATTACK", "SAUDI PIPELINE",
     "EAST-WEST LINE HIT", "", "pipeline"),
    ("TRADE", (202, 111, 30), "TRUMP: DOUBLE", "MEXICO TARIFFS",
     "TARIFFS TO DOUBLE", "", "tariffs"),
    ("EUROPE", (36, 113, 163), "STORM CHARLES", "HITS PORTUGAL",
     "ATLANTIC STORM", "", "storm"),
    ("ASIA", (108, 52, 131), "SRI LANKA BUDGET", "2027 UNVEILED",
     "BANGLADESH: 120 FACTORIES SHUT", "", "factory"),
]


def _thick_circle(cv, cx, cy, r, c):
    cv.circle(cx, cy, r, c)
    cv.circle(cx, cy, r - 1, c)


def draw_pic(cv, key, cx, cy, accent):
    """One simple pictogram, centred near (cx, cy)."""
    if key == "radar":
        _thick_circle(cv, cx, cy, 30, accent)
        cv.circle(cx, cy, 20, accent)
        cv.hline(cx - 30, cy, 61, accent)
        cv.vline(cx, cy - 30, 61, accent)
        cv.line(cx, cy, cx + 21, cy - 21, accent)
        cv.disc(cx + 12, cy - 12, 3, accent)
    elif key == "tanker":
        cv.poly([(cx - 36, cy + 4), (cx + 28, cy + 4), (cx + 38, cy + 10),
                 (cx + 28, cy + 16), (cx - 36, cy + 16)], accent)
        cv.rect(cx - 30, cy - 8, 12, 12, INK)
        cv.rect(cx - 16, cy - 8, 12, 12, INK)
        cv.rect(cx - 2, cy - 8, 12, 12, INK)
        cv.rect(cx + 14, cy - 10, 8, 14, INK)
        cv.hline(cx - 36, cy + 22, 72, accent)
        cv.hline(cx - 30, cy + 27, 60, accent)
        cv.circle(cx + 30, cy - 22, 6, INK)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                       (1, 1), (-1, -1), (1, -1), (-1, 1)):
            cv.line(cx + 30 + dx * 8, cy - 22 + dy * 8,
                    cx + 30 + dx * 13, cy - 22 + dy * 13, INK)
    elif key == "talks":
        cv.frame(cx - 36, cy - 24, 34, 22, accent, 2)
        cv.poly([(cx - 28, cy - 2), (cx - 18, cy - 2), (cx - 28, cy + 8)],
                accent)
        cv.disc(cx - 26, cy - 13, 2, accent)
        cv.disc(cx - 19, cy - 13, 2, accent)
        cv.disc(cx - 12, cy - 13, 2, accent)
        cv.rect(cx + 2, cy + 2, 34, 22, accent)
        cv.poly([(cx + 26, cy + 24), (cx + 16, cy + 24), (cx + 26, cy + 32)],
                accent)
        cv.disc(cx + 12, cy + 13, 2, WHITE)
        cv.disc(cx + 19, cy + 13, 2, WHITE)
        cv.disc(cx + 26, cy + 13, 2, WHITE)
    elif key == "peace":
        _thick_circle(cv, cx, cy, 28, accent)
        cv.vline(cx, cy - 28, 57, accent)
        cv.line(cx, cy, cx - 20, cy + 20, accent)
        cv.line(cx, cy, cx + 20, cy + 20, accent)
    elif key == "swap":
        cv.hline(cx - 30, cy - 11, 52, accent)
        cv.hline(cx - 30, cy - 10, 52, accent)
        cv.poly([(cx + 30, cy - 10), (cx + 20, cy - 18), (cx + 20, cy - 2)],
                accent)
        cv.hline(cx - 22, cy + 9, 52, accent)
        cv.hline(cx - 22, cy + 10, 52, accent)
        cv.poly([(cx - 30, cy + 10), (cx - 20, cy + 2), (cx - 20, cy + 18)],
                accent)
    elif key == "carbomb":
        cv.poly([(cx - 18, cy + 2), (cx - 12, cy - 10), (cx + 12, cy - 10),
                 (cx + 18, cy + 2)], INK)
        cv.rect(cx - 30, cy + 2, 60, 14, INK)
        cv.disc(cx - 18, cy + 18, 5, INK)
        cv.disc(cx + 18, cy + 18, 5, INK)
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1),
                       (1, 1), (-1, -1), (1, -1), (-1, 1)):
            cv.line(cx + dx * 9, cy - 20 + dy * 9,
                    cx + dx * 17, cy - 20 + dy * 17, accent)
        cv.disc(cx, cy - 20, 5, accent)
    elif key == "chip":
        cv.frame(cx - 24, cy - 24, 48, 48, accent, 3)
        cv.frame(cx - 14, cy - 14, 28, 28, accent, 2)
        for px in (cx - 16, cx - 8, cx, cx + 8, cx + 16):
            cv.vline(px, cy - 31, 7, accent)
            cv.vline(px, cy + 24, 7, accent)
        for py in (cy - 16, cy - 8, cy, cy + 8, cy + 16):
            cv.hline(cx - 31, py, 7, accent)
            cv.hline(cx + 24, py, 7, accent)
        cv.vline(cx + 34, cy - 6, 24, (192, 57, 43))
        cv.poly([(cx + 34, cy + 26), (cx + 26, cy + 16), (cx + 42, cy + 16)],
                (192, 57, 43))
    elif key == "coin":
        _thick_circle(cv, cx, cy, 28, accent)
        cv.circle(cx, cy, 22, accent)
        draw_text(cv, cx - 7, cy - 11, "$", 3, accent)
    elif key == "cloud":
        cv.disc(cx - 18, cy + 2, 12, accent)
        cv.disc(cx, cy - 6, 14, accent)
        cv.disc(cx + 18, cy + 2, 12, accent)
        cv.rect(cx - 30, cy + 2, 60, 12, accent)
        cv.poly([(cx + 2, cy + 12), (cx + 10, cy + 12), (cx + 2, cy + 24),
                 (cx + 8, cy + 24), (cx - 4, cy + 40), (cx - 2, cy + 26),
                 (cx - 8, cy + 26)], (241, 196, 15))
    elif key == "collapse":
        cv.rect(cx - 22, cy - 28, 44, 56, (230, 230, 230))
        cv.frame(cx - 22, cy - 28, 44, 56, INK, 2)
        for wx in (cx - 14, cx, cx + 14):
            for wy in (cy - 20, cy - 8, cy + 4):
                cv.rect(wx - 2, wy - 2, 5, 5, INK)
        for a, b in (((cx, cy - 28), (cx - 4, cy - 14)),
                     ((cx - 4, cy - 14), (cx + 4, cy)),
                     ((cx + 4, cy), (cx - 4, cy + 14)),
                     ((cx - 4, cy + 14), (cx + 2, cy + 28))):
            cv.line(a[0], a[1], b[0], b[1], accent)
            cv.line(a[0] + 1, a[1], b[0] + 1, b[1], accent)
        cv.poly([(cx - 30, cy + 28), (cx - 20, cy + 28), (cx - 25, cy + 20)],
                INK)
        cv.poly([(cx - 6, cy + 28), (cx + 4, cy + 28), (cx - 1, cy + 21)],
                INK)
        cv.poly([(cx + 18, cy + 28), (cx + 28, cy + 28), (cx + 23, cy + 20)],
                INK)
    elif key == "mitre":
        cv.poly([(cx - 20, cy + 20), (cx - 20, cy - 6), (cx, cy - 30),
                 (cx + 20, cy - 6), (cx + 20, cy + 20)], accent)
        cv.rect(cx - 20, cy + 8, 40, 6, WHITE)
        cv.rect(cx - 1, cy - 42, 3, 12, accent)
        cv.rect(cx - 6, cy - 38, 13, 3, accent)
    elif key == "ballot":
        cv.rect(cx - 6, cy - 26, 12, 16, WHITE)
        cv.frame(cx - 6, cy - 26, 12, 16, INK, 1)
        cv.rect(cx - 28, cy - 10, 56, 8, INK)
        cv.rect(cx - 24, cy - 2, 48, 30, accent)
        cv.line(cx + 16, cy - 30, cx + 22, cy - 22, accent)
        cv.line(cx + 22, cy - 22, cx + 34, cy - 38, accent)
        cv.line(cx + 17, cy - 30, cx + 23, cy - 22, accent)
        cv.line(cx + 23, cy - 22, cx + 35, cy - 38, accent)
    elif key == "pipeline":
        cv.rect(cx - 36, cy - 6, 72, 12, accent)
        cv.rect(cx - 20, cy - 10, 6, 20, INK)
        cv.rect(cx + 14, cy - 10, 6, 20, INK)
        cv.poly([(cx - 8, cy - 10), (cx - 2, cy - 32), (cx + 2, cy - 18),
                 (cx + 8, cy - 34), (cx + 12, cy - 10)], (230, 126, 34))
        cv.poly([(cx - 3, cy - 10), (cx, cy - 24), (cx + 4, cy - 10)],
                (241, 196, 15))
    elif key == "tariffs":
        cv.frame(cx - 28, cy - 2, 40, 30, accent, 2)
        cv.line(cx - 28, cy - 2, cx + 12, cy + 28, accent)
        cv.line(cx + 12, cy - 2, cx - 28, cy + 28, accent)
        cv.vline(cx + 26, cy - 16, 40, accent)
        cv.poly([(cx + 26, cy - 26), (cx + 18, cy - 14), (cx + 34, cy - 14)],
                accent)
    elif key == "storm":
        cv.disc(cx - 18, cy - 2, 12, (93, 109, 126))
        cv.disc(cx, cy - 10, 14, (93, 109, 126))
        cv.disc(cx + 18, cy - 2, 12, (93, 109, 126))
        cv.rect(cx - 30, cy - 2, 60, 12, (93, 109, 126))
        cv.line(cx - 20, cy + 16, cx - 24, cy + 26, accent)
        cv.line(cx, cy + 16, cx - 4, cy + 26, accent)
        cv.line(cx + 20, cy + 16, cx + 16, cy + 26, accent)
        cv.hline(cx - 30, cy + 32, 40, accent)
        cv.hline(cx - 10, cy + 38, 40, accent)
    elif key == "factory":
        cv.poly([(cx - 32, cy), (cx - 32, cy - 16), (cx - 16, cy),
                 (cx - 16, cy - 16), (cx, cy), (cx, cy - 16),
                 (cx + 16, cy), (cx + 16, cy - 16), (cx + 32, cy),
                 (cx + 32, cy + 28), (cx - 32, cy + 28)], accent)
        cv.rect(cx - 24, cy + 8, 8, 8, WHITE)
        cv.rect(cx - 4, cy + 8, 8, 8, WHITE)
        cv.rect(cx + 16, cy + 8, 8, 8, WHITE)
        cv.rect(cx + 24, cy - 28, 8, 28, INK)
        cv.disc(cx + 28, cy - 34, 3, GREY)
        cv.disc(cx + 28, cy - 41, 2, GREY)


def draw_panel(cv, x, y, idx, p):
    """One story panel: tag bar, pictogram, headline, sub-label."""
    tag, accent, h1, h2, s1, s2, pic = p
    cv.frame(x, y, 246, 215, INK, 1)
    cv.rect(x, y, 246, 26, accent)
    draw_text_c(cv, x + 123, y + 6, tag, 2, WHITE)
    draw_text(cv, x + 246 - 26, y + 9, "%02d" % (idx + 1), 1, WHITE)
    draw_pic(cv, pic, x + 123, y + 74, accent)
    draw_text_c(cv, x + 123, y + 122, h1, 2, INK)
    draw_text_c(cv, x + 123, y + 140, h2, 2, INK)
    if s1:
        draw_text_c(cv, x + 123, y + 162, s1, 1, GREY)
    if s2:
        draw_text_c(cv, x + 123, y + 172, s2, 1, GREY)
    cv.rect(x + 93, y + 196, 60, 3, accent)


def build():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    for i, p in enumerate(PANELS):
        x = 8 + (i % 4) * (246 + 8)
        y = 112 + (i // 4) * (215 + 8)
        draw_panel(cv, x, y, i, p)
    draw_footer(cv)
    return cv


def main():
    cv = build()
    path = os.path.join(out_dir(), "entry.png")
    with open(path, "wb") as f:
        f.write(png_bytes(cv.px, W, H))
    print("wrote " + path)


if __name__ == "__main__":
    main()
