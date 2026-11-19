#!/usr/bin/env python3
"""The World in One Picture - Thursday 19 November 2026.

A newspaper front page for one day's world news, drawn entirely from code
with the Python standard library only: a hand-written 5x7 bitmap font, a
tiny software rasteriser and a minimal PNG encoder. No network, no clock,
no randomness - run it twice and the bytes are identical.

Usage: MAKEFUN_OUTPUT_DIR=out python3 main.py
Writes entry.png (1024x1024) into MAKEFUN_OUTPUT_DIR, or /output when that
directory exists, or ./out otherwise.
"""

import binascii
import os
import struct
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- colours
INK = (26, 24, 20)
PAPER = (247, 242, 231)
PAPER_DARK = (233, 224, 203)
RED = (178, 32, 44)
BLUE = (29, 78, 137)
SKY = (168, 205, 232)
SKY_DEEP = (110, 160, 205)
LAKE = (96, 150, 190)
GOLD = (201, 162, 39)
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
GREY = (110, 106, 98)
SUIT = (38, 42, 54)
SKIN = (232, 184, 148)
WOOD = (122, 84, 50)
GREEN = (70, 130, 74)
ORANGE = (232, 122, 40)
FLAME = (245, 176, 48)
SEA = (52, 102, 148)
SAND = (226, 204, 160)

# ------------------------------------------------------------------- font
# 5x7 bitmap glyphs, rows top to bottom, '#' is a lit pixel.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", "#####"),
    "2": (".###.", "#...#", "....#", "..##.", ".#...", "#....", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".##..", ".#..."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".##.#"),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#...", "#..##"),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    '"': (".#.#.", ".#.#.", ".#.#.", ".....", ".....", ".....", "....."),
}

for _ch, _glyph in FONT.items():
    assert len(_glyph) == 7 and all(len(row) == 5 for row in _glyph), _ch


def text_width(s, scale):
    if not s:
        return 0
    return len(s) * (5 * scale + scale) - scale


# ------------------------------------------------------------------ canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        self.fill_rect(0, 0, w, h, bg)

    def set_px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = c[0]
            self.px[i + 1] = c[1]
            self.px[i + 2] = c[2]

    def fill_rect(self, x, y, w, h, c):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(c) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def outline_rect(self, x, y, w, h, c, t=1):
        self.fill_rect(x, y, w, t, c)
        self.fill_rect(x, y + h - t, w, t, c)
        self.fill_rect(x, y, t, h, c)
        self.fill_rect(x + w - t, y, t, h, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.fill_rect(x - t // 2, y - t // 2, t, t, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def fill_circle(self, cx, cy, r, c):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.fill_rect(cx - dx, cy + dy, 2 * dx + 1, 1, c)

    def fill_poly(self, pts, c):
        ys = [p[1] for p in pts]
        y_lo = max(0, int(min(ys)))
        y_hi = min(self.h - 1, int(max(ys)))
        n = len(pts)
        for y in range(y_lo, y_hi + 1):
            xs = []
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if y0 == y1:
                    continue
                if (y0 <= y < y1) or (y1 <= y < y0):
                    xs.append(x0 + (y - y0) * (x1 - x0) / (y1 - y0))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self.fill_rect(int(xs[i]), y, int(xs[i + 1]) - int(xs[i]) + 1, 1, c)

    def star(self, cx, cy, r, c):
        import math

        pts = []
        for i in range(10):
            ang = -math.pi / 2 + i * math.pi / 5
            rad = r if i % 2 == 0 else r * 0.45
            pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
        self.fill_poly(pts, c)

    def text(self, x, y, s, scale, c):
        s = s.upper()
        cx = x
        for ch in s:
            glyph = FONT.get(ch, FONT[" "])
            for ry, row in enumerate(glyph):
                for rx, cell in enumerate(row):
                    if cell == "#":
                        self.fill_rect(cx + rx * scale, y + ry * scale, scale, scale, c)
            cx += 6 * scale
        return cx

    def text_centered(self, y, s, scale, c):
        x = (self.w - text_width(s, scale)) // 2
        self.text(x, y, s, scale, c)


# -------------------------------------------------------------- PNG encode
def encode_png(cv):
    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        out += struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)
        return out

    raw = bytearray()
    stride = cv.w * 3
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * stride:(y + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0)
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
        + chunk(b"IEND", b"")
    )


# ------------------------------------------------------------------ scenes
def draw_flag_us(cv, x, y, w, h):
    stripe = h // 7
    for i in range(7):
        cv.fill_rect(x, y + i * stripe, w, stripe + 1, RED if i % 2 == 0 else WHITE)
    canton_w = int(w * 0.45)
    canton_h = stripe * 4
    cv.fill_rect(x, y, canton_w, canton_h, BLUE)
    for r in range(4):
        for cix in range(5):
            cv.fill_circle(x + 6 + cix * (canton_w - 10) // 4, y + 5 + r * (canton_h - 8) // 3, 2, WHITE)


def draw_flag_china(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, RED)
    cv.star(x + w // 5, y + h // 4, 9, GOLD)
    for dx, dy in ((w // 3, h // 9), (w // 3 + 4, h // 4), (w // 3, h // 2 - 4), (w // 4 + 2, h // 2 + 4)):
        cv.star(x + dx, y + dy, 4, GOLD)


def draw_flag_russia(cv, x, y, w, h):
    band = h // 3
    cv.fill_rect(x, y, w, band + 1, WHITE)
    cv.fill_rect(x, y + band, w, band + 1, BLUE)
    cv.fill_rect(x, y + 2 * band, w, h - 2 * band, RED)
    cv.outline_rect(x, y, w, h, GREY, 1)


def draw_leader(cv, cx, base, tie, label):
    # legs and suit body
    cv.fill_rect(cx - 16, base - 58, 32, 58, SUIT)
    cv.fill_rect(cx - 16, base - 58, 32, 6, WHITE)  # shirt band
    cv.fill_poly([(cx - 5, base - 54), (cx + 5, base - 54), (cx, base - 30)], tie)
    # arms resting forward
    cv.line(cx - 16, base - 50, cx - 30, base - 22, SUIT, 6)
    cv.line(cx + 16, base - 50, cx + 30, base - 22, SUIT, 6)
    # head
    cv.fill_circle(cx, base - 74, 15, SKIN)
    cv.fill_rect(cx - 15, base - 92, 30, 8, (60, 52, 44))  # hair
    # nameplate under the figure
    lw = text_width(label, 2)
    cv.fill_rect(cx - lw // 2 - 5, base + 4, lw + 10, 20, PAPER)
    cv.outline_rect(cx - lw // 2 - 5, base + 4, lw + 10, 20, INK, 1)
    cv.text(cx - lw // 2, base + 7, label, 2, INK)


def draw_lead_scene(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, SKY)
    # distant Shenzhen towers
    towers = [(0, 90), (60, 130), (130, 100), (190, 150), (700, 120), (770, 160), (845, 105), (905, 140)]
    for tx, th in towers:
        cv.fill_rect(x + tx, y + h - 60 - th, 42, th, SKY_DEEP)
        for wy in range(y + h - 52 - th, y + h - 66, 14):
            cv.fill_rect(x + tx + 8, wy, 6, 6, GOLD)
            cv.fill_rect(x + tx + 26, wy, 6, 6, GOLD)
    # lake band
    cv.fill_rect(x, y + h - 60, w, 60, LAKE)
    for i in range(9):
        lx = x + 30 + i * 105
        cv.fill_rect(lx, y + h - 44 + (i % 3) * 12, 46, 3, WHITE)
    # villa: white hall with a sweeping roof, centre-left
    vx, vy = x + 250, y + h - 118
    cv.fill_rect(vx, vy, 190, 58, WHITE)
    cv.fill_poly([(vx - 14, vy), (vx + 204, vy), (vx + 160, vy - 26), (vx + 30, vy - 26)], (150, 60, 48))
    for i in range(5):
        cv.fill_rect(vx + 16 + i * 36, vy + 14, 18, 30, SKY_DEEP)
    # flags on poles behind the table
    for fx, draw in ((x + 120, draw_flag_us), (x + 452, draw_flag_china), (x + 800, draw_flag_russia)):
        cv.fill_rect(fx + 32, y + 26, 4, 118, GREY)
        draw(cv, fx - 28, y + 26, 64, 42)
    # long table and the three leaders
    table_y = y + h - 96
    cv.fill_rect(x + 300, table_y + 34, 380, 14, WOOD)
    cv.fill_rect(x + 316, table_y + 48, 12, 26, WOOD)
    cv.fill_rect(x + 652, table_y + 48, 12, 26, WOOD)
    draw_leader(cv, x + 380, table_y + 40, BLUE, "TRUMP")
    draw_leader(cv, x + 492, table_y + 40, RED, "XI JINPING")
    draw_leader(cv, x + 604, table_y + 40, (90, 90, 90), "PUTIN")
    cv.outline_rect(x, y, w, h, INK, 2)


# ------------------------------------------------------------------- icons
def icon_tanker(cv, x, y, w, h):
    cv.fill_rect(x, y + h - 18, w, 18, SEA)
    for i in range(4):
        cv.fill_rect(x + 8 + i * (w // 4), y + h - 12, 18, 3, WHITE)
    hull_y = y + h - 34
    cv.fill_poly([(x + 14, hull_y), (x + w - 8, hull_y), (x + w - 26, hull_y + 16), (x + 30, hull_y + 16)], (52, 54, 60))
    cv.fill_rect(x + 34, hull_y - 14, w - 90, 14, (140, 60, 40))
    cv.fill_rect(x + w - 52, hull_y - 24, 16, 24, GREY)
    for fx in (x + 56, x + 92, x + 128):
        cv.fill_poly([(fx, hull_y - 14), (fx + 7, hull_y - 34), (fx + 14, hull_y - 14)], FLAME)
        cv.fill_poly([(fx + 3, hull_y - 14), (fx + 7, hull_y - 26), (fx + 11, hull_y - 14)], ORANGE)


def icon_bridge(cv, x, y, w, h):
    cv.fill_rect(x, y + h - 12, w, 12, LAKE)
    deck_y = y + h - 28
    cv.fill_rect(x + 6, deck_y, w // 2 - 26, 7, GREY)
    cv.fill_rect(x + w // 2 + 22, deck_y, w // 2 - 28, 7, GREY)
    cv.fill_rect(x + 16, deck_y - 20, 7, 20, GREY)
    cv.fill_rect(x + w - 23, deck_y - 20, 7, 20, GREY)
    cv.line(x + 19, deck_y - 20, x + w // 2 - 24, deck_y, GREY, 2)
    cv.line(x + w - 20, deck_y - 20, x + w // 2 + 24, deck_y, GREY, 2)
    for sx in (x + w // 2 - 10, x + w // 2 + 4):
        cv.fill_circle(sx, deck_y - 12, 5, (90, 90, 90))
        cv.fill_circle(sx + 5, deck_y - 19, 6, (130, 130, 130))


def icon_game(cv, x, y, w, h):
    # Vice-City style sunset, palms and a controller
    cv.fill_rect(x, y, w, h - 14, (250, 178, 120))
    cv.fill_circle(x + w - 42, y + 26, 16, (250, 220, 90))
    cv.fill_rect(x, y + h - 14, w, 14, (214, 110, 130))
    for px in (x + 22, x + w - 30):
        cv.line(px, y + h - 14, px + 4, y + 22, (90, 60, 40), 4)
        for ang in (-38, -14, 12, 36):
            import math

            ex = px + 4 + int(20 * math.sin(ang * 3.14159 / 180))
            ey = y + 22 - int(10 * math.cos(ang * 3.14159 / 180))
            cv.line(px + 4, y + 22, ex, ey, GREEN, 3)
    pad_x, pad_y = x + w // 2 - 34, y + h - 44
    cv.fill_rect(pad_x, pad_y, 68, 26, (40, 40, 48))
    cv.fill_circle(pad_x, pad_y + 13, 13, (40, 40, 48))
    cv.fill_circle(pad_x + 68, pad_y + 13, 13, (40, 40, 48))
    cv.fill_rect(pad_x + 8, pad_y + 10, 14, 5, WHITE)
    cv.fill_rect(pad_x + 12, pad_y + 6, 5, 14, WHITE)
    cv.fill_circle(pad_x + 52, pad_y + 9, 3, RED)
    cv.fill_circle(pad_x + 60, pad_y + 16, 3, GOLD)


def icon_art(cv, x, y, w, h):
    fx, fy = x + w // 2 - 40, y + 2
    cv.fill_rect(fx, fy, 80, 56, GOLD)
    cv.fill_rect(fx + 6, fy + 6, 68, 44, (24, 32, 74))
    for sx, sy, sr in ((fx + 20, fy + 18, 4), (fx + 44, fy + 14, 3), (fx + 58, fy + 26, 4), (fx + 30, fy + 32, 3), (fx + 52, fy + 40, 3)):
        cv.star(sx, sy, sr, (250, 230, 150))
    cv.fill_circle(fx + 58, fy + 16, 6, (240, 230, 180))
    cv.line(fx + 12, fy + 44, fx + 34, fy + 24, (90, 130, 90), 3)
    cv.line(fx + 34, fy + 24, fx + 52, fy + 40, (90, 130, 90), 3)
    cv.line(fx + 52, fy + 40, fx + 66, fy + 28, (90, 130, 90), 3)


def icon_court(cv, x, y, w, h):
    cx = x + w // 2
    cv.fill_poly([(cx - 52, y + 16), (cx + 52, y + 16), (cx, y + 2)], GREY)
    cv.fill_rect(cx - 56, y + 18, 112, 5, GREY)
    for i in range(4):
        cv.fill_rect(cx - 46 + i * 26, y + 26, 9, 28, (168, 160, 148))
    cv.fill_rect(cx - 56, y + 56, 112, 5, GREY)


def icon_chart(cv, x, y, w, h):
    base = y + h - 8
    cv.line(x + 8, y + 4, x + 8, base, GREY, 2)
    cv.line(x + 8, base, x + w - 6, base, GREY, 2)
    bars = [(26, 16, BLUE), (58, 26, BLUE), (90, 38, RED), (122, 52, RED)]
    for bx, bh, col in bars:
        if x + bx + 22 <= x + w:
            cv.fill_rect(x + bx, base - bh, 22, bh, col)
    cv.line(x + 16, base - 22, x + 60, base - 34, GOLD, 3)
    cv.line(x + 60, base - 34, x + 100, base - 48, GOLD, 3)
    cv.line(x + 100, base - 48, x + 140, base - 60, GOLD, 3)
    cv.fill_poly([(x + 140, base - 66), (x + 152, base - 58), (x + 138, base - 54)], GOLD)


def icon_tank(cv, x, y, w, h):
    gy = y + h - 12
    cv.fill_rect(x, gy, w, 4, SAND)
    cv.fill_rect(x + 30, gy - 16, 96, 16, (96, 104, 74))
    cv.fill_circle(x + 44, gy - 8, 8, (60, 64, 50))
    cv.fill_circle(x + 66, gy - 8, 8, (60, 64, 50))
    cv.fill_circle(x + 88, gy - 8, 8, (60, 64, 50))
    cv.fill_circle(x + 110, gy - 8, 8, (60, 64, 50))
    cv.fill_rect(x + 52, gy - 30, 48, 14, (110, 118, 84))
    cv.line(x + 98, gy - 26, x + 148, gy - 34, (80, 86, 64), 5)
    cv.fill_rect(x + 64, gy - 38, 16, 8, (110, 118, 84))


def icon_space(cv, x, y, w, h):
    cv.fill_rect(x, y, w, h, (16, 22, 48))
    for sx, sy in ((16, 8), (52, 20), (90, 6), (130, 16), (160, 30), (36, 34), (118, 38), (70, 26)):
        if x + sx < x + w and y + sy < y + h:
            cv.fill_circle(x + sx, y + sy, 2, WHITE)
    cx, cy = x + 52, y + h - 16
    cv.fill_poly([(cx - 26, cy - 26), (cx + 10, cy - 40), (cx + 16, cy - 6), (cx - 12, cy + 2)], (200, 204, 210))
    cv.line(cx - 6, cy - 4, cx - 20, y + h - 2, GREY, 4)
    cv.line(cx - 6, cy - 4, cx + 16, y + h - 2, GREY, 4)
    for r in (6, 11, 16):
        for a in range(200, 341, 10):
            import math

            px = cx + 16 + int(r * math.cos(a * 3.14159 / 180))
            py = cy - 22 + int(r * math.sin(a * 3.14159 / 180))
            cv.set_px(px, py, GOLD)
            cv.set_px(px + 1, py, GOLD)


ICONS = [icon_tanker, icon_bridge, icon_game, icon_art, icon_court, icon_chart, icon_tank, icon_space]

PANELS = [
    ("GULF", (29, 78, 137), ["TANKERS BLAZE IN", "HORMUZ STRAIT", "3 SHIPS HIT MINES"]),
    ("UKRAINE", (178, 32, 44), ["CRIMEAN BRIDGE", "ATTACKED AGAIN", "AS TALKS NEAR"]),
    ("GAMING", (150, 60, 130), ["GTA VI LAUNCHES", "AROUND THE WORLD", "13-YEAR WAIT ENDS"]),
    ("ART", (146, 110, 20), ["VAN GOGH SELLS", "FOR A RECORD", "$190.4 MILLION"]),
    ("THE HAGUE", (40, 110, 110), ["WORLD COURT RULES", "ON MYANMAR AND", "THE ROHINGYA"]),
    ("TECH", (70, 70, 120), ["ANTHROPIC POISED", "FOR $1.4 TRILLION", "STOCK DEBUT"]),
    ("GAZA", (96, 104, 60), ["ISRAELI TANKS", "CROSS CEASEFIRE", "LINE IN GAZA"]),
    ("SPACE", (30, 40, 90), ["VOYAGER 1 NOW", "ONE LIGHT-DAY", "FROM EARTH"]),
]


# -------------------------------------------------------------------- page
def render():
    cv = Canvas(W, H, PAPER)
    cv.outline_rect(14, 14, W - 28, H - 28, INK, 3)
    cv.outline_rect(23, 23, W - 46, H - 46, INK, 1)

    # masthead
    cv.text_centered(38, "THE WORLD IN ONE PICTURE", 5, INK)
    cv.fill_rect(40, 92, W - 80, 3, INK)
    cv.text_centered(106, "THURSDAY 19 NOVEMBER 2026", 4, RED)
    cv.text_centered(146, "ALL THE DAY'S NEWS IN A SINGLE IMAGE", 2, GREY)
    cv.fill_rect(40, 172, W - 80, 2, INK)

    # lead story
    cv.text(40, 188, "SHENZHEN, CHINA - APEC SUMMIT SIDELINES", 2, RED)
    cv.text(40, 214, "TRUMP, XI AND PUTIN", 6, INK)
    cv.text(40, 268, "HOLD FIRST TRILATERAL", 6, INK)
    cv.text(40, 322, "SUMMIT IN SHENZHEN", 6, INK)
    draw_lead_scene(cv, 40, 384, W - 80, 208)
    cv.text(40, 606, "LEADERS OF THE THREE BIGGEST NUCLEAR POWERS MEET AT KYLIN VILLA BY XILI LAKE", 2, INK)
    cv.text(40, 630, "NUCLEAR ARMS, UKRAINE AND IRAN TOP THE AGENDA; NO BIG DEAL IS EXPECTED", 2, INK)
    cv.fill_rect(40, 662, W - 80, 2, INK)

    # panels: 2 rows of 4
    grid_x, grid_y = 40, 678
    pw, ph, gap = 227, 148, 12
    for i, (cat, colour, lines) in enumerate(PANELS):
        px = grid_x + (i % 4) * (pw + gap)
        py = grid_y + (i // 4) * (ph + gap)
        cv.outline_rect(px, py, pw, ph, INK, 2)
        cv.fill_rect(px, py, pw, 22, colour)
        cv.text(px + 8, py + 4, cat, 2, WHITE)
        ICONS[i](cv, px + 14, py + 28, pw - 28, 56)
        for j, line in enumerate(lines):
            cv.text(px + 10, py + 92 + j * 18, line, 2, INK)

    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR")
    if not out_dir:
        out_dir = "/output" if os.path.isdir("/output") else "out"
    os.makedirs(out_dir, exist_ok=True)
    png = encode_png(render())
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as fh:
        fh.write(png)
    print("wrote %s (%d bytes)" % (target, len(png)))


if __name__ == "__main__":
    main()
