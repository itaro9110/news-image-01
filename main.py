#!/usr/bin/env python3
"""The World in One Page — 20 Stories.
Sums up Friday 13 November 2026 in one 1024x1024 front page:
20 verified stories, 5 columns x 4 rows, hand-drawn pictograms
and a hand-rolled 5x7 bitmap font. Stdlib only, deterministic.
"""
import math, os, struct, zlib

def out_dir():
    d = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if d:
        return d
    if os.path.isdir("/output") and os.access("/output", os.W_OK):
        return "/output"
    return "/tmp"

def save_png(path, w, h, buf):
    raw = b"".join(b"\x00" + bytes(buf[y*w*3:(y+1)*w*3])
                   for y in range(h))
    def ck(t, d):
        return (struct.pack(">I", len(d)) + t + d +
                struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF))
    png = (b"\x89PNG\r\n\x1a\n" +
           ck(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)) +
           ck(b"IDAT", zlib.compress(raw, 9)) + ck(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)

class CV:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.b = bytearray(bg * (w * h))
    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.b[i:i+3] = c
    def rect(self, x, y, w, h, c):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.px(xx, yy, c)
    def circ(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5)
            for xx in range(cx - dx, cx + dx + 1):
                self.px(xx, yy, c)
    def ring(self, cx, cy, r, c, t=2):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d = ((xx - cx) ** 2 + (yy - cy) ** 2) ** 0.5
                if r - t < d <= r:
                    self.px(xx, yy, c)
    def line(self, x0, y0, x1, y1, c, w=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        e = dx - dy
        while True:
            for a in range(-(w // 2), w // 2 + 1):
                for b in range(-(w // 2), w // 2 + 1):
                    self.px(x0 + a, y0 + b, c)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * e
            if e2 > -dy:
                e -= dy; x0 += sx
            if e2 < dx:
                e += dx; y0 += sy
    def tri(self, x0, y0, x1, y1, x2, y2, c):
        ys = sorted([(y0, x0), (y1, x1), (y2, x2)])
        (ya, xa), (yb, xb), (yc, xc) = ys
        for y in range(ya, yc + 1):
            if y < yb:
                xa1 = xa + (xb - xa) * (y - ya) / max(1, yb - ya)
            else:
                xa1 = xb + (xc - xb) * (y - yb) / max(1, yc - yb)
            xa2 = xa + (xc - xa) * (y - ya) / max(1, yc - ya)
            lo, hi = sorted([int(xa1), int(xa2)])
            for x in range(lo, hi + 1):
                self.px(x, y, c)
    def ell(self, cx, cy, a, b, c, t=2):
        for k in range(0, 360, 2):
            r = math.radians(k)
            x = int(cx + a * math.cos(r))
            y = int(cy + b * math.sin(r))
            for dx in range(-t // 2, t // 2 + 1):
                for dy in range(-t // 2, t // 2 + 1):
                    self.px(x + dx, y + dy, c)
FONT = {
"A": ("01110","10001","10001","11111","10001","10001","10001"),
"B": ("11110","10001","10001","11110","10001","10001","11110"),
"C": ("01110","10001","10000","10000","10000","10001","01110"),
"D": ("11110","10001","10001","10001","10001","10001","11110"),
"E": ("11111","10000","10000","11110","10000","10000","11111"),
"F": ("11111","10000","10000","11110","10000","10000","10000"),
"G": ("01110","10001","10000","10111","10001","10001","01111"),
"H": ("10001","10001","10001","11111","10001","10001","10001"),
"I": ("01110","00100","00100","00100","00100","00100","01110"),
"J": ("00111","00010","00010","00010","00010","10010","01100"),
"K": ("10001","10010","10100","11000","10100","10010","10001"),
"L": ("10000","10000","10000","10000","10000","10000","11111"),
"M": ("10001","11011","10101","10101","10001","10001","10001"),
"N": ("10001","11001","10101","10011","10001","10001","10001"),
"O": ("01110","10001","10001","10001","10001","10001","01110"),
"P": ("11110","10001","10001","11110","10000","10000","10000"),
"Q": ("01110","10001","10001","10001","10101","10010","01101"),
"R": ("11110","10001","10001","11110","10100","10010","10001"),
"S": ("01111","10000","10000","01110","00001","00001","11110"),
"T": ("11111","00100","00100","00100","00100","00100","00100"),
"U": ("10001","10001","10001","10001","10001","10001","01110"),
"V": ("10001","10001","10001","10001","10001","01010","00100"),
"W": ("10001","10001","10001","10101","10101","10101","01010"),
"X": ("10001","10001","01010","00100","01010","10001","10001"),
"Y": ("10001","10001","01010","00100","00100","00100","00100"),
"Z": ("11111","00001","00010","00100","01000","10000","11111"),
"0": ("01110","10001","10011","10101","11001","10001","01110"),
"1": ("00100","01100","00100","00100","00100","00100","01110"),
"2": ("01110","10001","00001","00110","01000","10000","11111"),
"3": ("11111","00010","00100","00010","00001","10001","01110"),
"4": ("00010","00110","01010","10010","11111","00010","00010"),
"5": ("11111","10000","11110","00001","00001","10001","01110"),
"6": ("00110","01000","10000","11110","10001","10001","01110"),
"7": ("11111","00001","00010","00100","01000","01000","01000"),
"8": ("01110","10001","10001","01110","10001","10001","01110"),
"9": ("01110","10001","10001","01111","00001","00010","01100"),
" ": ("00000","00000","00000","00000","00000","00000","00000"),
".": ("00000","00000","00000","00000","00000","01100","01100"),
",": ("00000","00000","00000","00000","01100","00100","01000"),
":": ("00000","01100","01100","00000","01100","01100","00000"),
"'": ("00100","00100","01000","00000","00000","00000","00000"),
"-": ("00000","00000","00000","01110","00000","00000","00000"),
"$": ("00100","01111","10100","01110","00101","11110","00100"),
"%": ("11001","11010","00010","00100","01000","01011","10011"),
"&": ("01100","10010","10100","01000","10101","10010","01101"),
"/": ("00001","00010","00010","00100","01000","01000","10000"),
"(": ("00010","00100","01000","01000","01000","00100","00010"),
")": ("01000","00100","00010","00010","00010","00100","01000"),
"!": ("00100","00100","00100","00100","00100","00000","00100"),
"?": ("01110","10001","00001","00110","00100","00000","00100"),
}

def text_w(s, sc):
    return len(s) * (5 * sc + 1) - 1

def draw_text(cv, s, x, y, sc, col):
    for i, ch in enumerate(s):
        g = FONT.get(ch, FONT[" "])
        for r in range(7):
            for c in range(5):
                if g[r][c] == "1":
                    cv.rect(x + i * (5 * sc + 1) + c * sc, y + r * sc,
                            sc, sc, col)

def center_text(cv, s, cx, y, sc, col):
    draw_text(cv, s, cx - text_w(s, sc) // 2, y, sc, col)
INK = (28, 28, 28)
RED = (178, 34, 34)
GOLD = (212, 160, 40)
BLUE = (0, 120, 215)
DK = (60, 50, 40)

def pic_chip(cv, cx, cy):
    R, L, T = cv.rect, cv.line, cv.tri
    R(cx - 32, cy - 17, 46, 34, (16, 110, 60))
    R(cx - 24, cy - 9, 30, 18, (30, 160, 90))
    for i in range(3):
        R(cx - 38, cy - 12 + i * 10, 6, 4, GOLD)
        R(cx + 14, cy - 12 + i * 10, 6, 4, GOLD)
    L(cx + 32, cy - 24, cx + 32, cy + 12, RED, 4)
    T(cx + 23, cy + 10, cx + 41, cy + 10, cx + 32, cy + 26, RED)

def pic_scale(cv, cx, cy):
    R, L, T = cv.rect, cv.line, cv.tri
    R(cx - 2, cy - 26, 4, 52, DK)
    R(cx - 28, cy - 26, 56, 4, DK)
    R(cx - 16, cy + 24, 32, 4, DK)
    for s in (-1, 1):
        L(cx + s * 26, cy - 22, cx + s * 20, cy - 6, DK, 2)
        T(cx + s * 28, cy - 6, cx + s * 12, cy - 6,
          cx + s * 20, cy + 6, GOLD)
    R(cx - 3, cy - 32, 6, 6, GOLD)

def pic_window(cv, cx, cy):
    R, L = cv.rect, cv.line
    R(cx - 26, cy - 22, 52, 44, BLUE)
    R(cx - 2, cy - 22, 4, 44, (255, 255, 255))
    R(cx - 26, cy - 2, 52, 4, (255, 255, 255))
    L(cx - 26, cy - 20, cx - 10, cy - 4, RED, 2)
    L(cx - 10, cy - 4, cx + 2, cy - 14, RED, 2)
    L(cx + 2, cy - 14, cx + 16, cy + 2, RED, 2)
    L(cx + 16, cy + 2, cx + 26, cy + 16, RED, 2)

def pic_radar(cv, cx, cy):
    C, L = cv.circ, cv.line
    cv.ring(cx, cy, 28, (20, 90, 50), 3)
    cv.ring(cx, cy, 15, (20, 90, 50), 2)
    L(cx, cy, cx + 20, cy - 20, (40, 180, 80), 2)
    C(cx + 10, cy - 8, 3, (40, 180, 80))
    C(cx - 12, cy + 10, 3, (40, 180, 80))
    C(cx, cy, 3, (40, 180, 80))
    L(cx + 16, cy - 28, cx + 30, cy - 14, GOLD, 3)
    L(cx + 30, cy - 28, cx + 16, cy - 14, GOLD, 3)

def pic_tanker(cv, cx, cy):
    R, L, T, C = cv.rect, cv.line, cv.tri, cv.circ
    R(cx - 32, cy - 2, 58, 14, (120, 40, 30))
    T(cx + 26, cy - 2, cx + 26, cy + 12, cx + 40, cy + 12, (120, 40, 30))
    R(cx - 22, cy - 12, 30, 10, (90, 30, 25))
    R(cx + 2, cy - 22, 8, 10, (60, 60, 60))
    L(cx - 38, cy + 22, cx + 38, cy + 22, BLUE, 2)
    L(cx - 30, cy + 28, cx + 30, cy + 28, BLUE, 2)
    C(cx + 34, cy - 16, 7, INK)
    for k in range(8):
        a = math.radians(k * 45)
        L(cx + 34 + int(7 * math.cos(a)), cy - 16 + int(7 * math.sin(a)),
          cx + 34 + int(12 * math.cos(a)), cy - 16 + int(12 * math.sin(a)),
          INK, 2)
def pic_flags(cv, cx, cy):
    R, C = cv.rect, cv.circ
    R(cx - 30, cy - 20, 3, 44, DK)
    R(cx + 27, cy - 20, 3, 44, DK)
    R(cx - 27, cy - 20, 26, 16, (0, 70, 160))
    for k in range(6):
        a = math.radians(k * 60)
        C(cx - 14 + int(5 * math.cos(a)), cy - 12 + int(5 * math.sin(a)),
          1, GOLD)
    R(cx + 1, cy - 20, 26, 8, (0, 90, 180))
    R(cx + 1, cy - 12, 26, 8, (240, 200, 40))

def pic_swap(cv, cx, cy):
    L, T = cv.line, cv.tri
    L(cx - 30, cy - 10, cx + 22, cy - 10, (0, 90, 180), 4)
    T(cx + 22, cy - 18, cx + 22, cy - 2, cx + 34, cy - 10, (0, 90, 180))
    L(cx + 30, cy + 10, cx - 22, cy + 10, (240, 200, 40), 4)
    T(cx - 22, cy + 2, cx - 22, cy + 18, cx - 34, cy + 10, (240, 200, 40))

def pic_kremlin(cv, cx, cy):
    R, C, T = cv.rect, cv.circ, cv.tri
    R(cx - 30, cy + 8, 60, 16, (150, 60, 40))
    C(cx, cy - 4, 14, GOLD)
    T(cx - 3, cy - 26, cx + 3, cy - 26, cx, cy - 14, GOLD)
    R(cx, cy - 32, 2, 8, DK)
    T(cx + 2, cy - 32, cx + 2, cy - 24, cx + 13, cy - 28, (200, 40, 40))

def pic_car(cv, cx, cy):
    R, L, C = cv.rect, cv.line, cv.circ
    R(cx - 30, cy - 2, 60, 12, (40, 80, 140))
    R(cx - 18, cy - 14, 30, 12, (40, 80, 140))
    C(cx - 18, cy + 12, 6, INK)
    C(cx + 18, cy + 12, 6, INK)
    for k in range(8):
        a = math.radians(k * 45 + 20)
        L(cx, cy - 30 + int(6 * math.sin(a)),
          cx + int(16 * math.cos(a)), cy - 30 + int(16 * math.sin(a)),
          (240, 120, 20), 3)
    C(cx, cy - 30, 5, (240, 120, 20))

def pic_barrel(cv, cx, cy):
    R, L = cv.rect, cv.line
    R(cx - 16, cy - 24, 32, 48, (40, 40, 40))
    R(cx - 16, cy - 12, 32, 3, (120, 120, 120))
    R(cx - 16, cy + 8, 32, 3, (120, 120, 120))
    L(cx - 22, cy - 28, cx + 22, cy + 28, RED, 4)
def pic_bubble(cv, cx, cy):
    C, L, T = cv.circ, cv.line, cv.tri
    C(cx, cy - 6, 22, (240, 240, 235))
    cv.ring(cx, cy - 6, 22, (120, 120, 120), 2)
    T(cx - 8, cy + 12, cx + 8, cy + 12, cx, cy + 26, (240, 240, 235))
    C(cx - 8, cy - 8, 2, INK)
    C(cx, cy - 8, 2, INK)
    C(cx + 8, cy - 8, 2, INK)
    L(cx - 26, cy - 30, cx + 26, cy + 22, RED, 4)

def pic_pipe(cv, cx, cy):
    R, L, T = cv.rect, cv.line, cv.tri
    R(cx - 34, cy - 4, 68, 10, (110, 110, 110))
    R(cx - 6, cy - 8, 12, 18, (80, 80, 80))
    T(cx, cy - 30, cx - 10, cy - 10, cx + 10, cy - 10, (240, 120, 20))
    T(cx, cy - 22, cx - 5, cy - 10, cx + 5, cy - 10, (240, 200, 40))
    L(cx - 30, cy + 16, cx + 30, cy + 16, (70, 90, 60), 2)

def pic_atom(cv, cx, cy):
    C = cv.circ
    cv.ell(cx - 8, cy, 26, 11, (0, 90, 160), 2)
    cv.ell(cx - 8, cy, 11, 26, (0, 90, 160), 2)
    C(cx - 8, cy, 5, (200, 40, 40))
    cv.rect(cx + 24, cy - 12, 5, 24, (120, 120, 120))
    cv.rect(cx + 33, cy - 12, 5, 24, (120, 120, 120))

def pic_building(cv, cx, cy):
    R, L = cv.rect, cv.line
    R(cx - 18, cy - 28, 36, 56, (140, 120, 100))
    for r in range(3):
        for c in range(3):
            R(cx - 12 + c * 11, cy - 22 + r * 13, 6, 7, (60, 50, 40))
    L(cx - 18, cy - 28, cx - 6, cy - 10, RED, 2)
    L(cx - 6, cy - 10, cx - 14, cy + 6, RED, 2)
    L(cx - 14, cy + 6, cx - 2, cy + 28, RED, 2)
    R(cx - 26, cy + 28, 52, 4, (100, 90, 80))

def pic_ballot(cv, cx, cy):
    R, L = cv.rect, cv.line
    R(cx - 20, cy - 6, 40, 34, (0, 90, 160))
    R(cx - 8, cy - 2, 16, 3, (20, 20, 20))
    R(cx - 8, cy - 20, 16, 14, (255, 255, 255))
    L(cx - 16, cy + 14, cx - 8, cy + 22, (40, 180, 80), 3)
    L(cx - 8, cy + 22, cx + 14, cy + 4, (40, 180, 80), 3)
def pic_truck(cv, cx, cy):
    R, L, T, C = cv.rect, cv.line, cv.tri, cv.circ
    R(cx - 32, cy - 6, 38, 20, (0, 110, 90))
    R(cx + 6, cy, 18, 14, (0, 110, 90))
    R(cx + 10, cy + 2, 8, 7, (200, 230, 255))
    C(cx - 20, cy + 16, 6, INK)
    C(cx + 14, cy + 16, 6, INK)
    L(cx + 30, cy - 8, cx + 30, cy - 24, RED, 3)
    T(cx + 24, cy - 22, cx + 36, cy - 22, cx + 30, cy - 32, RED)

def pic_church(cv, cx, cy):
    R, C, T = cv.rect, cv.circ, cv.tri
    C(cx, cy - 8, 16, (250, 250, 250))
    R(cx - 16, cy - 8, 32, 34, (250, 250, 250))
    R(cx - 2, cy - 30, 4, 14, GOLD)
    R(cx - 7, cy - 26, 14, 4, GOLD)
    C(cx - 7, cy + 16, 6, RED)
    C(cx + 7, cy + 16, 6, RED)
    T(cx - 13, cy + 14, cx + 13, cy + 14, cx, cy + 30, RED)

def pic_storm(cv, cx, cy):
    C, L = cv.circ, cv.line
    C(cx - 14, cy - 8, 13, (110, 120, 130))
    C(cx + 2, cy - 14, 15, (110, 120, 130))
    C(cx + 16, cy - 8, 12, (110, 120, 130))
    cv.rect(cx - 26, cy - 8, 52, 12, (110, 120, 130))
    for i in range(3):
        L(cx - 18 + i * 16, cy + 8, cx - 22 + i * 16, cy + 24,
          (0, 90, 180), 2)
    L(cx + 4, cy + 6, cx - 4, cy + 16, GOLD, 3)
    L(cx - 4, cy + 16, cx + 6, cy + 16, GOLD, 3)
    L(cx + 6, cy + 16, cx - 2, cy + 28, GOLD, 3)

def pic_budget(cv, cx, cy):
    R, T, C = cv.rect, cv.tri, cv.circ
    R(cx - 16, cy - 26, 32, 52, (255, 255, 255))
    T(cx + 16, cy - 26, cx + 16, cy - 14, cx + 4, cy - 26, (200, 200, 200))
    for i in range(4):
        R(cx - 10, cy - 14 + i * 9, 20, 3, (100, 100, 100))
    C(cx + 22, cy + 18, 8, GOLD)
    C(cx + 22, cy + 8, 8, GOLD)
    C(cx + 22, cy - 2, 8, GOLD)

def pic_shirt(cv, cx, cy):
    R, T, L = cv.rect, cv.tri, cv.line
    R(cx - 14, cy - 18, 28, 42, (0, 140, 160))
    T(cx - 14, cy - 18, cx - 30, cy - 8, cx - 14, cy - 2, (0, 140, 160))
    T(cx + 14, cy - 18, cx + 30, cy - 8, cx + 14, cy - 2, (0, 140, 160))
    R(cx - 6, cy - 18, 12, 6, (240, 240, 240))
    L(cx - 28, cy - 28, cx + 28, cy + 28, RED, 4)
BUS = (31, 78, 121)
CRY = (138, 109, 0)
TEC = (14, 107, 107)
MID = (122, 46, 29)
EUR = (43, 76, 155)
USA = (91, 31, 46)
AME = (46, 107, 52)
WOR = (91, 58, 122)
ASI = (154, 91, 0)

PANELS = [
("BUSINESS", BUS, pic_chip,
 ["NVIDIA CEO", "HUANG RESIGNS"],
 ["CFO COLETTE KRESS", "IS INTERIM CHIEF"]),
("CRYPTO", CRY, pic_scale,
 ["DOJ SEIZES $1.2B", "BINANCE CRYPTO"],
 ["FBI BLAMES NORTH KOREA", "HACK GROUP DENIES IT"]),
("TECH", TEC, pic_window,
 ["MICROSOFT", "OUTAGE WORLDWIDE"],
 ["MAJOR DISRUPTION TO", "BUSINESSES WORLDWIDE"]),
("MIDDLE EAST", MID, pic_radar,
 ["IRAN SAYS IT HIT", "US RADAR"],
 ["CLAIM, NOT VERIFIED", "NO US COMMENT YET"]),
("MIDDLE EAST", MID, pic_tanker,
 ["TANKER HITS MINE", "IN HORMUZ"],
 ["FIFTH TANKER HIT", "THIS WEEK"]),
("EUROPE", EUR, pic_flags,
 ["EU JOINS UKRAINE", "PEACE TALKS"],
 ["RUSSIA AGREES TO", "EUROPE AT THE TABLE"]),
("EUROPE", EUR, pic_swap,
 ["BIGGEST PRISONER", "SWAP EYED"],
 ["COULD BE THE WAR'S", "LARGEST EXCHANGE"]),
("EUROPE", EUR, pic_kremlin,
 ["US ENVOYS MEET", "PUTIN IN MOSCOW"],
 ["KUSHNER AND WITKOFF", "THEN BRIEF ZELENSKYY"]),
("EUROPE", EUR, pic_car,
 ["MOSCOW CAR BOMB", "WOUNDS OFFICIAL"],
 ["SERGEI ZAVOROTNIY", "HURT IN BLAST"]),
("EUROPE", EUR, pic_barrel,
 ["UK SANCTIONS", "OIL GIANTS"],
 ["10 LARGEST PRODUCERS", "SANCTIONED"]),
("MIDDLE EAST", MID, pic_bubble,
 ["TRUMP PULLS VANCE", "FROM IRAN TALKS"],
 ["WE DON'T NEED A DEAL", "WITH IRAN, SAYS TRUMP"]),
("MIDDLE EAST", MID, pic_pipe,
 ["HOUTHIS HIT SAUDI", "OIL PIPELINE"],
 ["ATTACK ON SAUDI OIL", "PIPELINE"]),
("MIDDLE EAST", MID, pic_atom,
 ["IRAN: IAEA TALKS", "CAN'T PROCEED"],
 ["UNDER THREAT, TEHRAN", "TELLS NUCLEAR WATCHDOG"]),
("USA", USA, pic_building,
 ["BROOKLYN", "COLLAPSE: 8 DEAD"],
 ["FINAL TOLL: 8 DEAD,", "18 INJURED IN FLATBUSH"]),
("USA", USA, pic_ballot,
 ["VAN HOLLEN RUNS", "AGAINST SCHUMER"],
 ["BALLOT SET FOR 1 DEC", "SENATE LEADER RACE"]),
("AMERICAS", AME, pic_truck,
 ["TRUMP TO DOUBLE", "MEXICO TARIFFS"],
 ["THREATENS NEW LEVY", "ON MEXICAN GOODS"]),
("WORLD", WOR, pic_church,
 ["POPE LEO IN PERU", "MEETS SURVIVORS"],
 ["ABUSE SURVIVORS MET", "DURING PERU VISIT"]),
("EUROPE", EUR, pic_storm,
 ["STORM CHARLES", "HITS PORTUGAL"],
 ["HEAVY RAIN AND WIND", "BATTER THE COAST"]),
("ASIA", ASI, pic_budget,
 ["SRI LANKA UNVEILS", "2027 BUDGET"],
 ["NEW SPENDING PLAN", "PRESENTED FOR 2027"]),
("ASIA", ASI, pic_shirt,
 ["BANGLADESH", "GARMENT DISPUTE"],
 ["AROUND 120 FACTORIES", "CLOSED IN DISPUTE"]),
]
def main():
    cv = CV(1024, 1024, (246, 241, 231))
    cv.rect(0, 0, 1024, 84, (22, 35, 63))
    center_text(cv, "THE WORLD IN ONE PAGE", 512, 12, 3, (255, 255, 255))
    center_text(cv, "FRIDAY 13 NOVEMBER 2026 - 20 STORIES", 512, 52, 2,
                (242, 201, 76))
    cv.rect(0, 84, 1024, 4, GOLD)
    for i, (tag, col, pic, head, sub) in enumerate(PANELS):
        x = 8 + (i % 5) * 203
        y = 96 + (i // 5) * 216
        cv.rect(x, y, 197, 210, (255, 253, 246))
        cv.rect(x, y, 197, 1, (201, 194, 178))
        cv.rect(x, y + 209, 197, 1, (201, 194, 178))
        cv.rect(x, y, 1, 210, (201, 194, 178))
        cv.rect(x + 196, y, 1, 210, (201, 194, 178))
        cv.rect(x, y, 197, 22, col)
        center_text(cv, tag, x + 98, y + 8, 1, (255, 255, 255))
        pic(cv, x + 98, y + 70)
        center_text(cv, head[0], x + 98, y + 120, 2, INK)
        center_text(cv, head[1], x + 98, y + 137, 2, INK)
        center_text(cv, sub[0], x + 98, y + 161, 1, (68, 64, 58))
        center_text(cv, sub[1], x + 98, y + 173, 1, (68, 64, 58))
        cv.rect(x, y + 207, 197, 3, col)
    cv.rect(8, 966, 1008, 2, (120, 110, 95))
    center_text(cv, "ALL EVENTS FIRST REPORTED ON FRIDAY 13 NOVEMBER 2026",
                512, 978, 2, (68, 64, 58))
    d = out_dir()
    os.makedirs(d, exist_ok=True)
    save_png(os.path.join(d, "entry.png"), 1024, 1024, cv.b)
    print("wrote", os.path.join(d, "entry.png"))

if __name__ == "__main__":
    main()
