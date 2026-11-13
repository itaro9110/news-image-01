import math
import os
import struct
import zlib

W = 1024
H = 1024
PW = 494
PH = 288

NAVY = (22, 35, 61)
PAPER = (250, 249, 246)
INK = (24, 32, 48)
SLATE = (84, 96, 116)
RED = (214, 48, 49)
BLUE = (37, 99, 235)
GREEN = (22, 163, 74)
AMBER = (217, 119, 6)
PURPLE = (124, 58, 237)
GREY = (203, 213, 225)

canvas = bytearray(b"\xf5\xf5\xf2" * (W * H))


def px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        canvas[i:i + 3] = bytes(c)


def rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        i = (yy * W + x0) * 3
        canvas[i:(yy * W + x1) * 3] = bytes(c) * (x1 - x0)


def line(x0, y0, x1, y1, c):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    e = dx + dy
    while True:
        px(x0, y0, c)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * e
        if e2 >= dy:
            e += dy
            x0 += sx
        if e2 <= dx:
            e += dx
            y0 += sy


def disc(cx, cy, r, c):
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(r * r - dy * dy))
        rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)


def poly(pts, c):
    ys = [p[1] for p in pts]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(pts)
        for i in range(n):
            x0, y0 = pts[i]
            x1, y1 = pts[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                t = (y - y0) / (y1 - y0)
                xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            rect(int(xs[i]), y, int(xs[i + 1]) - int(xs[i]) + 1, 1, c)


# Small 5x7 bitmap font, drawn from scratch for this page.
FONT = {
    "A": ("..#..", ".#.#.", "#...#", "#...#", "#####", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
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
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    "$": ("..#..", ".####", "#....", ".###.", "....#", "####.", "..#.."),
    ".": (".....", ".....", ".....", ".....", ".....", ".....", "..#.."),
    ",": (".....", ".....", ".....", ".....", ".....", "..#..", ".#..."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
}


def text_w(s, sc):
    return len(s) * 6 * sc - sc


def draw_text(s, x, y, sc, c, center=False):
    if center:
        x -= text_w(s, sc) // 2
    cx = x
    for ch in s:
        g = FONT.get(ch, FONT[" "])
        for r in range(7):
            row = g[r]
            for col in range(5):
                if row[col] == "#":
                    rect(cx + col * sc, y + r * sc, sc, sc, c)
        cx += 6 * sc


def masthead():
    rect(0, 0, W, 118, NAVY)
    draw_text("FRIDAY 13 NOVEMBER 2026", W // 2, 10, 7, (255, 255, 255), True)
    draw_text("THE WORLD IN ONE PAGE", W // 2, 68, 4, (147, 197, 253), True)
    rect(0, 118, W, 6, RED)


def panel(x, y, tag, tc, l1, l2, sub, pic, tint):
    rect(x, y, PW, PH, PAPER)
    rect(x, y, PW, 34, tc)
    draw_text(tag, x + 12, y + 7, 3, (255, 255, 255))
    draw_text(l1, x + PW // 2, y + 46, 4, INK, True)
    draw_text(l2, x + PW // 2, y + 84, 4, INK, True)
    rect(x + 16, y + 126, PW - 32, 108, tint)
    pic(x + 16, y + 126, PW - 32, 108)
    draw_text(sub, x + PW // 2, y + 248, 3, SLATE, True)
    rect(x, y, PW, 2, GREY)
    rect(x, y + PH - 2, PW, 2, GREY)
    rect(x, y, 2, PH, GREY)
    rect(x + PW - 2, y, 2, PH, GREY)


def pic_tanker(px, py, w, h):
    rect(px, py + 62, w, h - 62, (59, 130, 246))
    rect(px + 30, py + 40, 190, 22, (31, 41, 55))
    rect(px + 42, py + 26, 42, 14, (220, 38, 38))
    rect(px + 90, py + 26, 42, 14, (250, 204, 21))
    rect(px + 138, py + 26, 42, 14, (255, 255, 255))
    cx, cy = px + 285, py + 34
    disc(cx, cy, 15, (249, 115, 22))
    for k in range(8):
        a = k * math.pi / 4
        line(cx, cy, int(cx + 32 * math.cos(a)),
             int(cy + 32 * math.sin(a)), (249, 115, 22))
    disc(cx, cy, 6, (253, 224, 71))
    mx, my = px + 380, py + 84
    disc(mx, my, 11, (15, 23, 42))
    for k in range(8):
        a = k * math.pi / 4 + 0.4
        line(mx, my, int(mx + 18 * math.cos(a)),
             int(my + 18 * math.sin(a)), (15, 23, 42))


def pic_flags(px, py, w, h):
    rect(px + 34, py + 18, 130, 72, (0, 51, 153))
    ccx, ccy = px + 99, py + 54
    for k in range(12):
        a = k * math.pi / 6 - math.pi / 2
        disc(int(ccx + 24 * math.cos(a)),
             int(ccy + 24 * math.sin(a)), 3, (255, 209, 0))
    rect(px + 300, py + 18, 130, 36, (0, 91, 187))
    rect(px + 300, py + 54, 130, 36, (255, 213, 0))
    rect(px + 176, py + 50, 112, 8, (255, 193, 7))
    rect(px + 28, py + 12, 3, 84, (100, 116, 139))
    rect(px + 433, py + 12, 3, 84, (100, 116, 139))


def pic_chip(px, py, w, h):
    for k in range(4):
        rect(px + 86 + k * 18, py + 2, 8, 12, (234, 88, 12))
        rect(px + 86 + k * 18, py + 94, 8, 12, (234, 88, 12))
        rect(px + 58, py + 26 + k * 18, 12, 8, (234, 88, 12))
        rect(px + 150, py + 26 + k * 18, 12, 8, (234, 88, 12))
    rect(px + 70, py + 14, 80, 80, (22, 163, 74))
    rect(px + 86, py + 30, 48, 48, (134, 239, 172))
    rect(px + 102, py + 46, 16, 16, (20, 83, 45))
    poly([(px + 330, py + 12), (px + 356, py + 12), (px + 356, py + 58),
          (px + 376, py + 58), (px + 343, py + 98), (px + 310, py + 58),
          (px + 330, py + 58)], (220, 38, 38))


def pic_coin(px, py, w, h):
    disc(px + 110, py + 54, 42, (217, 119, 6))
    disc(px + 110, py + 54, 36, (250, 204, 21))
    draw_text("$", px + 110, py + 36, 5, (146, 64, 14), True)
    poly([(px + 250, py + 28), (px + 412, py + 28), (px + 412, py + 80),
          (px + 250, py + 80), (px + 276, py + 54)], (220, 38, 38))
    draw_text("SEIZED", px + 336, py + 40, 3, (255, 255, 255), True)


def pic_window(px, py, w, h):
    rect(px + 88, py + 10, 44, 44, (59, 130, 246))
    rect(px + 138, py + 10, 44, 44, (147, 197, 253))
    rect(px + 88, py + 60, 44, 44, (37, 99, 235))
    rect(px + 138, py + 60, 44, 44, (147, 197, 253))
    poly([(px + 310, py + 6), (px + 276, py + 56), (px + 298, py + 56),
          (px + 280, py + 102), (px + 330, py + 44), (px + 306, py + 44)],
         (250, 204, 21))


def pic_building(px, py, w, h):
    rect(px + 180, py + 8, 120, 66, (100, 116, 139))
    for r in range(2):
        for k in range(4):
            rect(px + 196 + k * 28, py + 20 + r * 26, 16, 14,
                 (226, 232, 240))
    rect(px + 180, py + 74, 120, 24, (71, 85, 105))
    cx = px + 240
    for ox in (0, 2):
        line(cx + ox, py + 8, cx + 8 + ox, py + 30, (15, 23, 42))
        line(cx + 8 + ox, py + 30, cx - 6 + ox, py + 52, (15, 23, 42))
        line(cx - 6 + ox, py + 52, cx + 6 + ox, py + 74, (15, 23, 42))
        line(cx + 6 + ox, py + 74, cx - 4 + ox, py + 98, (15, 23, 42))
    poly([(px + 150, py + 98), (px + 180, py + 74), (px + 210, py + 98)],
         (148, 163, 184))
    poly([(px + 220, py + 98), (px + 250, py + 70), (px + 280, py + 98)],
         (100, 116, 139))
    poly([(px + 290, py + 98), (px + 320, py + 76), (px + 350, py + 98)],
         (148, 163, 184))


def save_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += canvas[y * W * 3:(y + 1) * W * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(t, data):
        out = struct.pack(">I", len(data)) + t + data
        return out + struct.pack(">I", zlib.crc32(t + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", comp) + chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


PANELS = [
    ("MIDDLE EAST", RED, "IRAN SAYS IT HIT", "US RADAR",
     "TANKER HITS MINE IN HORMUZ", pic_tanker, (219, 234, 254)),
    ("EUROPE", BLUE, "EU JOINS UKRAINE", "PEACE TALKS",
     "BIGGEST PRISONER SWAP EYED", pic_flags, (239, 246, 255)),
    ("BUSINESS", GREEN, "NVIDIA CEO", "HUANG RESIGNS",
     "KRESS IS INTERIM CHIEF", pic_chip, (220, 252, 231)),
    ("CRYPTO", AMBER, "DOJ TO SEIZE $1.2B", "IN BINANCE HACK",
     "FBI BLAMES NORTH KOREA", pic_coin, (254, 243, 199)),
    ("TECH", PURPLE, "MICROSOFT OUTAGE", "HITS WORLDWIDE",
     "BUSINESSES DISRUPTED", pic_window, (237, 233, 254)),
    ("USA", (51, 65, 85), "BROOKLYN COLLAPSE", "8 DEAD",
     "SEARCH ENDS, 18 HURT", pic_building, (241, 245, 249)),
]


def pick_out_dir():
    d = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if d:
        return d
    if os.access("/output", os.W_OK):
        return "/output"
    return "/tmp"


def main():
    masthead()
    for i, p in enumerate(PANELS):
        x = 12 + (i % 2) * 506
        y = 136 + (i // 2) * 300
        panel(x, y, *p)
    out = pick_out_dir()
    os.makedirs(out, exist_ok=True)
    save_png(os.path.join(out, "entry.png"))


if __name__ == "__main__":
    main()
