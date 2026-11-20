#!/usr/bin/env python3
"""Compose the 19 November 2026 front page (round 1 draft).

Builds entry.png (1024x1024) from the three generated illustrations plus
PIL-drawn panels. Run: python3 compose.py
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (22, 22, 34)
RED = (178, 32, 44)
NAVY = (20, 38, 74)
GREY = (90, 88, 84)
RULE = (180, 175, 162)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def para(draw, x, y, text, fnt, color, max_w, leading=None):
    lines = wrap(draw, text, fnt, max_w)
    lh = leading or int(fnt.size * 1.32)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=color)
        y += lh
    return y


def cover_crop(img, tw, th):
    iw, ih = img.size
    s = max(tw / iw, th / ih)
    img = img.resize((int(iw * s) + 1, int(ih * s) + 1), Image.LANCZOS)
    x = (img.width - tw) // 2
    y = (img.height - th) // 2
    return img.crop((x, y, x + tw, y + th))


def draw_ipo_chart(d, x, y, w, h):
    # Panel background
    d.rectangle([x, y, x + w, y + h], fill=(233, 238, 245), outline=RULE)
    d.text((x + 14, y + 10), "NASDAQ  ·  ANT", font=font(SANS_B, 15),
           fill=NAVY)
    d.text((x + w - 14, y + 10), "19 NOV 2026", font=font(SANS_B, 15),
           fill=GREY, anchor="ra")
    # Axes
    ox, oy = x + 34, y + h - 40
    ex, ey = x + w - 20, y + 34
    d.line([(ox, oy), (ex, oy)], fill=GREY, width=2)
    d.line([(ox, oy), (ox, ey)], fill=GREY, width=2)
    # Line: priced $83 -> opened $111.50, peaked higher, closed lower
    pts = [(0.00, 83), (0.12, 96), (0.25, 111.5), (0.38, 124),
           (0.52, 118), (0.68, 104), (0.85, 97), (1.00, 101)]
    lo, hi = 78, 130

    def px(t, v):
        return (ox + t * (ex - ox), oy - (v - lo) / (hi - lo) * (oy - ey))

    for i in range(len(pts) - 1):
        d.line([px(*pts[i]), px(*pts[i + 1])], fill=RED, width=4)
    d.ellipse([px(0, 83)[0] - 6, px(0, 83)[1] - 6,
               px(0, 83)[0] + 6, px(0, 83)[1] + 6], fill=NAVY)
    d.ellipse([px(0.25, 111.5)[0] - 6, px(0.25, 111.5)[1] - 6,
               px(0.25, 111.5)[0] + 6, px(0.25, 111.5)[1] + 6], fill=RED)
    d.text((px(0, 83)[0] + 10, px(0, 83)[1] + 8), "$83 priced",
           font=font(SANS_B, 15), fill=NAVY)
    d.text((ex - 4, ey + 2), "$111.50 open  +34%",
           font=font(SANS_B, 15), fill=RED, anchor="ra")


def draw_riyadh(d, x, y, w, h):
    # Night skyline panel: tallest tower struck, smoke plume
    d.rectangle([x, y, x + w, y + h], fill=(24, 30, 54))
    # stars
    for sx, sy in [(30, 22), (90, 40), (160, 18), (230, 46), (300, 24),
                   (380, 38), (440, 20), (60, 70), (200, 64), (350, 66)]:
        d.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2],
                  fill=(220, 220, 235))
    # skyline blocks
    base = y + h
    for bx, bw, bh in [(0, 52, 46), (56, 40, 70), (100, 60, 54),
                       (330, 48, 62), (382, 56, 44), (442, 30, 58)]:
        d.rectangle([x + bx, base - bh, x + bx + bw, base], fill=(12, 16, 34))
    # PIF tower (tall, centre-left)
    tx0, tx1 = x + 160, x + 270
    d.polygon([(tx0, base), (tx0 + 10, y + 18), (tx1 - 10, y + 18),
               (tx1, base)], fill=(52, 60, 96))
    for wy in range(y + 32, base - 8, 13):
        d.line([(tx0 + 8, wy), (tx1 - 8, wy)], fill=(240, 200, 90), width=2)
    # smoke plume from tower top, kept inside the panel
    cx = (tx0 + tx1) // 2
    for i, r in enumerate([8, 11, 14]):
        d.ellipse([cx - r, y + 34 - i * 9 - r,
                   cx + r, y + 34 - i * 9 + r],
                  fill=(130, 126, 120))
    d.ellipse([cx - 7, y + 20, cx + 7, y + 34], fill=(255, 150, 60))
    # missile trail arc
    arc = []
    for t in range(0, 41):
        a = t / 40 * math.pi * 0.5
        arc.append((x + w - 20 - math.cos(a) * 190,
                    y + 30 + math.sin(a) * 120))
    d.line(arc, fill=(255, 150, 60), width=3)


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- Masthead ----
    d.line([(24, 14), (1000, 14)], fill=INK, width=3)
    d.text((512, 26), "THE WORLD IN ONE DAY", font=font(SERIF_B, 62),
           fill=INK, anchor="ma")
    d.text((512, 96), "THURSDAY,  19  NOVEMBER  2026",
           font=font(SANS_B, 20), fill=RED, anchor="ma")
    d.text((28, 122), "ONE DAY  ·  ONE PAGE  ·  THE WORLD'S NEWS",
           font=font(SANS_B, 15), fill=GREY)
    d.text((996, 122), "FRONT PAGE", font=font(SANS_B, 15), fill=GREY,
           anchor="ra")
    d.line([(24, 146), (1000, 146)], fill=INK, width=3)

    # ---- Hero: summit ----
    d.text((28, 158), "SHENZHEN  ·  APEC SUMMIT", font=font(SANS_B, 16),
           fill=RED)
    y = 182
    for ln in ["THREE LEADERS,", "ONE TABLE"]:
        d.text((28, y), ln, font=font(SERIF_B, 47), fill=INK)
        y += 56
    y = para(d, 28, y + 6,
             "Trump, Xi and Putin hold the first three-way summit "
             "and issue a \u201cpeace declaration\u201d on nuclear risks "
             "and energy flows \u2014 but announce no deal on Ukraine "
             "or Iran.", font(SERIF, 19), INK, 452, leading=26)
    d.text((28, 408), "90 minutes  ·  Shenzhen, China",
           font=font(SANS_B, 15), fill=GREY)
    globe = Image.open("assets/media-generation-summit-globe-0-"
                       "d21b7b9a-6965-470b-af2b-c7b3bcf4709f.webp").convert("RGB")
    img.paste(cover_crop(globe, 484, 240), (512, 158))
    d.rectangle([512, 158, 996, 398], outline=RULE)
    d.text((512, 404), "The globe over Shenzhen: the US, China and Russia "
           "talk nuclear risk.", font=font(SANS, 14), fill=GREY)

    # ---- Row 2 ----
    d.line([(24, 432), (1000, 432)], fill=RULE, width=2)
    # Left: ICJ
    court = Image.open("assets/media-generation-court-scales-0-"
                       "b41a7257-6c7f-4b0e-965d-df1dc2a8dfbc.webp").convert("RGB")
    img.paste(cover_crop(court, 472, 120), (28, 446))
    d.rectangle([28, 446, 500, 566], outline=RULE)
    d.text((28, 574), "THE HAGUE  ·  INTERNATIONAL COURT",
           font=font(SANS_B, 14), fill=RED)
    y = para(d, 28, 594, "WORLD COURT: MYANMAR COMMITTED GENOCIDE",
             font(SERIF_B, 27), INK, 472, leading=32)
    para(d, 28, y + 4,
         "The UN\u2019s top court rules Myanmar carried out "
         "state-sponsored genocide against the Rohingya in 2017 \u2014 "
         "the first ruling of its kind.", font(SERIF, 16), INK, 472,
         leading=21)
    # Right: Anthropic IPO
    d.text((524, 446), "NEW YORK  ·  MARKETS", font=font(SANS_B, 14),
           fill=RED)
    y = para(d, 524, 466, "THE BIGGEST IPO IN HISTORY: $107.3bn",
             font(SERIF_B, 27), INK, 472, leading=32)
    draw_ipo_chart(d, 524, y + 6, 472, 118)
    para(d, 524, y + 130,
         "Anthropic debuts on Nasdaq at $83 and opens at $111.50, "
         "valued near $1.5 trillion \u2014 passing SpaceX\u2019s record.",
         font(SERIF, 16), INK, 472, leading=21)

    # ---- Row 3 ----
    d.line([(24, 742), (1000, 742)], fill=RULE, width=2)
    # Left: GTA VI
    vice = Image.open("assets/media-generation-vice-city-0-"
                      "e9818076-fe96-415c-958d-75be9f68b074.webp").convert("RGB")
    img.paste(cover_crop(vice, 472, 96), (28, 754))
    d.rectangle([28, 754, 500, 850], outline=RULE)
    d.text((28, 858), "VICE CITY OPENS ITS DOORS",
           font=font(SERIF_B, 25), fill=INK)
    para(d, 28, 888,
         "Grand Theft Auto VI launches after a 13-year wait: "
         "$1.84bn and 19m copies on day one.",
         font(SERIF, 16), INK, 472, leading=21)
    # Right: Riyadh
    draw_riyadh(d, 524, 754, 472, 96)
    d.rectangle([524, 754, 996, 850], outline=RULE)
    d.text((524, 858), "MISSILE STRIKES RIYADH TOWER",
           font=font(SERIF_B, 25), fill=INK)
    para(d, 524, 888,
         "A Houthi missile damages Riyadh\u2019s tallest tower, home "
         "of the PIF. Trump says no major new Iran strikes until 2027.",
         font(SERIF, 16), INK, 472, leading=21)

    # ---- Ticker ----
    d.rectangle([24, 940, 1000, 990], fill=NAVY)
    d.text((36, 950), "ALSO TODAY", font=font(SANS_B, 15),
           fill=(255, 200, 90))
    para(d, 168, 948,
         "Cyclone Akvan nears India\u2019s east coast  \u00b7  COP31 "
         "final-stage talks on fossil fuels  \u00b7  Ukraine hits the "
         "Crimea bridge again  \u00b7  Denmark, Greenland and the US "
         "sign an Arctic security deal",
         font(SANS, 14), (240, 240, 240), 820, leading=19)

    # ---- Footer ----
    d.text((512, 998), "All events of Thursday, 19 November 2026, as "
           "reported that day.", font=font(SANS, 13), fill=GREY,
           anchor="ma")

    img.save("entry.png", optimize=True)
    print("saved entry.png")


if __name__ == "__main__":
    main()
