#!/usr/bin/env python3
"""news-image-01: Friday 13 November 2026 in one image.

A newspaper front page drawn procedurally with the standard library
only: a dated masthead plus six panels, one per story, each with a
region tag, a two-line headline, a bold pictogram and a one-line
sub-label. No network, no fonts, no image files: every pixel is
drawn by this program from a small embedded 5x7 bitmap font.
"""
import binascii
import math
import os
import struct
import zlib

W, H = 1024, 1024
NAVY = (11, 31, 58)
RED = (220, 38, 38)
INK = (15, 23, 42)
SUB = (71, 85, 105)
WHITE = (255, 255, 255)
BORDER = (203, 213, 225)
PAGE = (241, 245, 249)


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(bg * (w * h))

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.buf[i:i + (x1 - x0) * 3] = bytes(c) * (x1 - x0)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            for a in range(t):
                self.px(x0 + a, y0, c)
            if x0 == x1 and y0 == y1:
                return
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x0 += sx
            if e2 < dx:
                err += dx
                y0 += sy

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5)
            self.rect(cx - dx, yy, 2 * dx + 1, 1, c)

    def poly(self, pts, c):
        # Scanline fill of a simple polygon.
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(self.h, max(ys) + 1)):
            xs = []
            for i in range(len(pts)):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % len(pts)]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.rect(int(xs[i]), y, int(xs[i + 1]) - int(xs[i]), 1, c)


def save_png(cv, path):
    raw = b"".join(b"\x00" + bytes(cv.buf[y * cv.w * 3:(y + 1) * cv.w * 3])
                   for y in range(cv.h))

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
           + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


# 5x7 bitmap font: each glyph is 7 rows of 5 bits, row-major.
FONT = {
    "A": "01110100011000111111100011000110001",
    "B": "11110100011000111110100011000111110",
    "C": "01110100011000010000100001000101110",
    "D": "11110100011000110001100011000111110",
    "E": "11111100001000011110100001000011111",
    "F": "11111100001000011110100001000010000",
    "G": "01110100011000010111100011000101111",
    "H": "10001100011000111111100011000110001",
    "I": "01110001000010000100001000010001110",
    "J": "00111000100001000010000101001001100",
    "K": "10001100101010011000101001001010001",
    "L": "10000100001000010000100001000011111",
    "M": "10001110111010110101100011000110001",
    "N": "10001110011010110011100011000110001",
    "O": "01110100011000110001100011000101110",
    "P": "11110100011000111110100001000010000",
}
FONT.update({
    "Q": "01110100011000110001101011001001101",
    "R": "11110100011000111110101001001010001",
    "S": "01111100001000001110000010000111110",
    "T": "11111001000010000100001000010000100",
    "U": "10001100011000110001100011000101110",
    "V": "10001100011000110001100010101000100",
    "W": "10001100011000110101101011101110001",
    "X": "10001100010101000100010101000110001",
    "Y": "10001100010101000100001000010000100",
    "Z": "11111000010001000100010001000011111",
    "0": "01110100011001110101110011000101110",
    "1": "00100011000010000100001000010001110",
    "2": "01110100010000100010001000100011111",
    "3": "11110000010000101110000010000111110",
    "4": "00010001100101010010111110001000010",
    "5": "11111100001111000001000011000101110",
    "6": "01110100001000011110100011000101110",
})
FONT.update({
    "7": "1111100001000100010001000100001000",
    "8": "01110100011000101110100011000101110",
    "9": "01110100011000101111000010000101110",
    " ": "00000000000000000000000000000000000",
    ".": "00000000000000000000000000110001100",
    ",": "00000000000000000000011000010001000",
    "'": "00100001000100000000000000000000000",
    "$": "00100011111010001110001011111000100",
    "%": "11001110100001000100010000101110011",
    "-": "00000000000000001110000000000000000",
    ":": "00000011000110000000011000110000000",
    "/": "0000100010000100010001000100010000",
    "(": "00010001000100001000010000010000010",
    ")": "01000001000001000010000100010001000",
    "!": "00100001000010000100001000000000100",
    "?": "01110100010000100010001000000000100",
})


def glyph(cv, ch, x, y, s, c, bold=False):
    g = FONT.get(ch, FONT[" "])
    g = (g + "0" * 35)[:35]
    offs = (0, max(1, s // 4)) if bold else (0,)
    for r in range(7):
        for col in range(5):
            if g[r * 5 + col] == "1":
                for o in offs:
                    cv.rect(x + o + col * s, y + r * s, s, s, c)


def text_w(s, scale, track=1):
    return len(s) * (5 * scale + track) - track


def draw_text(cv, s, x, y, scale, c, bold=False, track=1):
    for ch in s:
        glyph(cv, ch, x, y, scale, c, bold)
        x += 5 * scale + track


def draw_center(cv, s, cx, y, scale, c, bold=False, track=1):
    draw_text(cv, s, cx - text_w(s, scale, track) // 2, y, scale, c,
              bold, track)


# (tag, tag color, tint, headline line 1, headline line 2, sub, pic)
PANELS = [
    ("MIDDLE EAST", (185, 28, 28), (254, 242, 242),
     "IRAN SAYS IT HIT", "US RADAR",
     "TANKER HITS MINE IN HORMUZ", "hormuz"),
    ("EUROPE", (29, 78, 216), (239, 246, 255),
     "EU JOINS UKRAINE", "PEACE TALKS",
     "BIGGEST PRISONER SWAP EYED", "ukraine"),
    ("BUSINESS", (21, 128, 61), (240, 253, 244),
     "NVIDIA CEO", "HUANG RESIGNS",
     "KRESS IS INTERIM CHIEF", "nvidia"),
    ("CRYPTO", (180, 83, 9), (255, 251, 235),
     "DOJ TO SEIZE $1.2B", "IN BINANCE HACK",
     "FBI BLAMES NORTH KOREA", "binance"),
    ("TECH", (109, 40, 217), (245, 243, 255),
     "MICROSOFT OUTAGE", "HITS WORLDWIDE",
     "BUSINESSES DISRUPTED", "microsoft"),
    ("USA", (51, 65, 85), (248, 250, 252),
     "BROOKLYN COLLAPSE", "8 DEAD",
     "SEARCH ENDS, 18 HURT", "brooklyn"),
]


def pic_hormuz(cv, x, y, w, h):
    cv.rect(x, y, w, h, (219, 234, 254))
    cv.rect(x, y + h - 46, w, 46, (37, 99, 235))
    cv.rect(x, y + h - 46, w, 4, (147, 197, 253))
    # Tanker hull with containers.
    hx, hy = x + 30, y + h - 46 - 34
    cv.rect(hx, hy + 14, 210, 20, (30, 41, 59))
    cv.rect(hx + 8, hy, 52, 14, (220, 38, 38))
    cv.rect(hx + 66, hy, 52, 14, (234, 179, 8))
    cv.rect(hx + 124, hy, 52, 14, (255, 255, 255))
    cv.rect(hx + 186, hy - 6, 26, 20, (226, 232, 240))
    # Explosion burst at the bow: long spikes, orange heart.
    ex, ey = x + 252, y + 40
    for k in range(10):
        a = k * 3.14159 / 5
        dx, dy = int(36 * math.cos(a)), int(36 * math.sin(a))
        cv.poly([(ex, ey), (ex + dx, ey + dy),
                 (ex + int(12 * math.cos(a + 0.35)),
                  ey + int(12 * math.sin(a + 0.35)))], (234, 88, 12))
    cv.circle(ex, ey, 13, (249, 115, 22))
    # Naval mine in the water.
    mx, my = x + w - 70, y + h - 24
    for k in range(8):
        a = k * 3.14159 / 4
        cv.line(mx, my, mx + int(20 * math.cos(a)),
                my + int(20 * math.sin(a)), (15, 23, 42), 3)
    cv.circle(mx, my, 11, (15, 23, 42))


def pic_ukraine(cv, x, y, w, h):
    cv.rect(x, y, w, h, (239, 246, 255))
    # EU flag on the left, Ukraine flag on the right.
    for fx, fy, top, bot in ((x + 30, y + 22, (29, 78, 216), None),
                             (x + w - 160, y + 22, (37, 99, 235),
                              (250, 204, 21))):
        cv.line(fx - 8, fy - 8, fx - 8, fy + 92, (100, 116, 139), 4)
        cv.rect(fx, fy, 130, 84, top)
        if bot:
            cv.rect(fx, fy + 42, 130, 42, bot)
        else:
            for k in range(12):
                a = k * 3.14159 / 6
                cv.circle(fx + 65 + int(28 * math.cos(a)),
                          fy + 42 + int(28 * math.sin(a)), 3,
                          (250, 204, 21))
    # Gold link between the flags: talks.
    cv.rect(x + 168, y + 58, w - 336, 6, (234, 179, 8))


def pic_nvidia(cv, x, y, w, h):
    cv.rect(x, y, w, h, (240, 253, 244))
    # Green chip with pins, left of centre.
    cx, cy = x + 110, y + h // 2
    for dx in (-58, 58):
        for k in range(3):
            cv.rect(cx + dx - 8, cy - 30 + k * 26, 16, 10, (217, 119, 6))
    for dy in (-58, 58):
        for k in range(3):
            cv.rect(cx - 30 + k * 26, cy + dy - 8, 10, 16, (217, 119, 6))
    cv.rect(cx - 50, cy - 50, 100, 100, (22, 101, 52))
    cv.rect(cx - 34, cy - 34, 68, 68, (118, 185, 0))
    cv.rect(cx - 18, cy - 18, 36, 36, (22, 101, 52))
    # Red down arrow: the resignation.
    ax = x + w - 120
    cv.rect(ax - 14, y + 18, 28, 56, (220, 38, 38))
    cv.poly([(ax - 34, y + 74), (ax + 34, y + 74), (ax, y + 112)],
            (220, 38, 38))


def pic_binance(cv, x, y, w, h):
    cv.rect(x, y, w, h, (255, 251, 235))
    # Gold coin with a dollar sign.
    cx, cy = x + 120, y + h // 2
    cv.circle(cx, cy, 52, (217, 119, 6))
    cv.circle(cx, cy, 44, (250, 204, 21))
    draw_text(cv, "$", cx - 15, cy - 21, 6, (120, 53, 15), bold=True)
    # Red SEIZED ribbon on the right.
    rx, ry = x + w - 250, y + 40
    cv.poly([(rx, ry), (rx + 210, ry), (rx + 210, ry + 44),
             (rx, ry + 44), (rx + 22, ry + 22)], (220, 38, 38))
    draw_center(cv, "SEIZED", rx + 116, ry + 11, 4, WHITE, bold=True)


def pic_microsoft(cv, x, y, w, h):
    cv.rect(x, y, w, h, (245, 243, 255))
    # Four-pane window, left of centre.
    wx, wy = x + 90, y + 12
    cv.rect(wx, wy, 48, 48, (59, 130, 246))
    cv.rect(wx + 54, wy, 48, 48, (96, 165, 250))
    cv.rect(wx, wy + 54, 48, 48, (37, 99, 235))
    cv.rect(wx + 54, wy + 54, 48, 48, (147, 197, 253))
    # Yellow lightning bolt cracking across it.
    bx = x + w - 150
    cv.poly([(bx + 20, y + 8), (bx - 14, y + 62), (bx + 6, y + 62),
             (bx - 16, y + 116), (bx + 26, y + 52), (bx + 4, y + 52),
             (bx + 34, y + 8)], (250, 204, 21))


def pic_brooklyn(cv, x, y, w, h):
    cv.rect(x, y, w, h, (248, 250, 252))
    # A building split by a jagged crack, top half sliding down.
    bx, by = x + 150, y + 8
    cv.rect(bx, by, 170, 60, (100, 116, 139))
    cv.rect(bx + 24, by + 66, 146, 42, (100, 116, 139))
    for r in range(2):
        for c in range(4):
            cv.rect(bx + 14 + c * 40, by + 12 + r * 26, 20, 14,
                    (226, 232, 240))
    # Jagged crack between the halves.
    cv.line(bx + 10, by + 58, bx + 60, by + 70, (15, 23, 42), 3)
    cv.line(bx + 60, by + 70, bx + 110, by + 60, (15, 23, 42), 3)
    cv.line(bx + 110, by + 60, bx + 160, by + 70, (15, 23, 42), 3)
    # Rubble at the base.
    for i, (rx, rw) in enumerate(((x + 120, 60), (x + 190, 80),
                                  (x + 280, 54))):
        cv.poly([(rx, y + h - 8), (rx + rw // 2, y + h - 30 - i * 4),
                 (rx + rw, y + h - 8)], (148, 163, 184))


PICS = {"hormuz": pic_hormuz, "ukraine": pic_ukraine,
        "nvidia": pic_nvidia, "binance": pic_binance,
        "microsoft": pic_microsoft, "brooklyn": pic_brooklyn}


def draw_panel(cv, x0, y0, panel):
    tag, color, tint, l1, l2, sub, pic = panel
    w, h = 494, 286
    cv.rect(x0, y0, w, h, WHITE)
    cv.rect(x0, y0, w, 34, color)
    draw_text(cv, tag, x0 + 12, y0 + 7, 3, WHITE, bold=True)
    draw_center(cv, l1, x0 + w // 2, y0 + 48, 4, INK, bold=True)
    draw_center(cv, l2, x0 + w // 2, y0 + 82, 4, INK, bold=True)
    PICS[pic](cv, x0 + 12, y0 + 122, w - 24, 124)
    draw_center(cv, sub, x0 + w // 2, y0 + 256, 3, SUB, bold=True)
    # 2px border.
    cv.rect(x0, y0, w, 2, BORDER)
    cv.rect(x0, y0 + h - 2, w, 2, BORDER)
    cv.rect(x0, y0, 2, h, BORDER)
    cv.rect(x0 + w - 2, y0, 2, h, BORDER)


def main():
    cv = Canvas(W, H, PAGE)
    cv.rect(0, 0, W, 120, NAVY)
    draw_center(cv, "FRIDAY 13 NOVEMBER 2026", W // 2, 16, 6, WHITE,
                bold=True)
    draw_center(cv, "THE WORLD IN ONE PAGE", W // 2, 70, 4,
                (147, 197, 253), bold=True)
    cv.rect(0, 120, W, 6, RED)
    for i, panel in enumerate(PANELS):
        x0 = 12 + (i % 2) * 506
        y0 = 138 + (i // 2) * 298
        draw_panel(cv, x0, y0, panel)
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "out")
    os.makedirs(out, exist_ok=True)
    save_png(cv, os.path.join(out, "entry.png"))


if __name__ == "__main__":
    main()
