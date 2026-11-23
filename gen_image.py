#!/usr/bin/env python3
"""Draw the 23 November 2026 front page (entry.png) with PIL.

Build-time only: run `python3 gen_image.py` in this directory.
Deterministic: fixed palette, fixed fonts, fixed layout, no randomness,
no timestamps embedded in the PNG (PIL writes no time chunk).
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")

PAPER = (247, 242, 231)
INK = (20, 20, 20)
RED = (178, 34, 34)
DARK_BLUE = (30, 58, 95)
GREEN = (34, 110, 72)
MUTED = (90, 84, 72)
RULE = (60, 55, 45)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF_REG = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for word in words[1:]:
            trial = cur + " " + word
            if draw.textlength(trial, font=fnt) <= max_w:
                cur = trial
            else:
                lines.append(cur)
                cur = word
        lines.append(cur)
    return lines


def draw_text_block(draw, x, y, text, fnt, fill, max_w, leading=None):
    """Draw wrapped text; return y just below the last line."""
    if leading is None:
        leading = int(fnt.size * 1.28)
    for line in wrap(draw, text, fnt, max_w):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


def lead_illustration(draw, x0, y0, w, h):
    """Antalya coast at dusk: gradient sky, low sun, sea, mountains,
    summit hall with three flags, light on the water."""
    # Sky gradient: warm orange at top to dusky purple at horizon.
    top = (244, 164, 96)
    mid = (232, 120, 84)
    bot = (122, 74, 110)
    horizon = int(h * 0.52)
    for yy in range(horizon):
        t = yy / max(1, horizon - 1)
        if t < 0.5:
            u = t / 0.5
            c = tuple(int(top[i] + (mid[i] - top[i]) * u) for i in range(3))
        else:
            u = (t - 0.5) / 0.5
            c = tuple(int(mid[i] + (bot[i] - mid[i]) * u) for i in range(3))
        draw.line([(x0, y0 + yy), (x0 + w, y0 + yy)], fill=c)
    # Sun, low over the sea, in the gap between the mountains.
    cx, cy = x0 + int(w * 0.86), y0 + horizon - 95
    r = 40
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(250, 224, 148))
    draw.ellipse([cx - r + 10, cy - r + 10, cx + r - 10, cy + r - 10],
                 fill=(253, 238, 180))
    # Birds.
    for bx, by in [(x0 + 60, y0 + 42), (x0 + 120, y0 + 30), (x0 + 290, y0 + 28)]:
        draw.arc([bx, by, bx + 22, by + 10], 180, 360, fill=(60, 40, 40), width=2)
        draw.arc([bx + 20, by, bx + 42, by + 10], 180, 360, fill=(60, 40, 40), width=2)
    # Mountains left and right.
    draw.polygon([(x0, y0 + horizon), (x0 + 130, y0 + horizon - 88),
                  (x0 + 260, y0 + horizon)], fill=(52, 84, 66))
    draw.polygon([(x0 + w - 260, y0 + horizon), (x0 + w - 130, y0 + horizon - 70),
                  (x0 + w, y0 + horizon)], fill=(44, 72, 58))
    # Sea.
    draw.rectangle([x0, y0 + horizon, x0 + w, y0 + h], fill=(38, 78, 110))
    # Sunlight path on the water.
    for i, (ww, yy) in enumerate([(150, 6), (120, 20), (92, 34), (64, 48), (40, 62)]):
        draw.rectangle([cx - ww // 2, y0 + horizon + yy,
                        cx + ww // 2, y0 + horizon + yy + 5],
                       fill=(250, 214, 130))
    # Summit hall on the shore, centre-left.
    hx0, hy0 = x0 + 150, y0 + horizon - 62
    hw, hh = 170, 62
    draw.rectangle([hx0, hy0, hx0 + hw, hy0 + hh], fill=(245, 240, 228))
    draw.polygon([(hx0 - 8, hy0), (hx0 + hw // 2, hy0 - 34),
                  (hx0 + hw + 8, hy0)], fill=(178, 34, 34))
    for i in range(5):
        wx = hx0 + 18 + i * 30
        draw.rectangle([wx, hy0 + 16, wx + 14, hy0 + 44], fill=(250, 214, 130))
    # Three flags behind the hall.
    for i, col in enumerate([(178, 34, 34), (30, 58, 150), (34, 110, 72)]):
        fx = hx0 + hw + 22 + i * 26
        draw.line([(fx, hy0 - 46), (fx, hy0 + 2)], fill=(40, 40, 40), width=3)
        draw.rectangle([fx, hy0 - 46, fx + 20, hy0 - 30], fill=col)


def icon_burst(draw, x, y, s):
    cx, cy = x + s // 2, y + s // 2
    pts = []
    for i in range(16):
        ang = 3.14159 * i / 8
        r = s // 2 - 2 if i % 2 == 0 else s // 5
        pts.append((cx + r * math.cos(ang),
                    cy + r * math.sin(ang)))
    draw.polygon(pts, fill=(232, 120, 40))
    draw.ellipse([cx - 9, cy - 9, cx + 9, cy + 9], fill=(250, 214, 130))


def icon_chart(draw, x, y, s):
    draw.line([(x + 6, y + s - 10), (x + s // 3, y + s // 2),
               (x + s // 2, y + s - 18), (x + s - 8, y + 8)],
              fill=(178, 34, 34), width=4)
    draw.polygon([(x + s - 16, y + 6), (x + s - 4, y + 6), (x + s - 8, y + 18)],
                 fill=(178, 34, 34))


def icon_tanker(draw, x, y, s):
    # Ship hull + flame above it.
    draw.polygon([(x + 6, y + s - 18), (x + s - 6, y + s - 18),
                  (x + s - 14, y + s - 6), (x + 14, y + s - 6)],
                 fill=(40, 60, 80))
    draw.rectangle([x + s // 2 - 4, y + s - 34, x + s // 2 + 12, y + s - 18],
                   fill=(90, 90, 90))
    draw.polygon([(x + s // 2, y + 4), (x + s // 2 + 12, y + 22),
                  (x + s // 2 + 2, y + 30), (x + s // 2 - 6, y + 20)],
                 fill=(232, 120, 40))
    draw.polygon([(x + s // 2 + 2, y + 16), (x + s // 2 + 9, y + 26),
                  (x + s // 2 + 1, y + 30)], fill=(250, 214, 130))


def icon_flags(draw, x, y, s):
    for i, col in enumerate([(178, 34, 34), (30, 58, 150), (34, 110, 72)]):
        fx = x + 10 + i * 16
        draw.line([(fx, y + 8), (fx, y + s - 8)], fill=(40, 40, 40), width=3)
        draw.rectangle([fx, y + 8, fx + 14, y + 22], fill=col)
    draw.line([(x + 6, y + s - 8), (x + s - 6, y + s - 8)],
              fill=(40, 40, 40), width=3)


def icon_ballot(draw, x, y, s):
    draw.rectangle([x + 8, y + s - 22, x + s - 8, y + s - 6],
                   fill=(30, 58, 95))
    draw.rectangle([x + s // 2 - 8, y + s - 30, x + s // 2 + 8, y + s - 22],
                   fill=(247, 242, 231))
    draw.line([(x + 10, y + 16), (x + s // 2 - 2, y + 30),
               (x + s - 10, y + 6)], fill=(34, 110, 72), width=5)


def icon_drone_ship(draw, x, y, s):
    # Waves.
    for wy in (y + s - 14, y + s - 8):
        draw.arc([x + 4, wy, x + s // 2, wy + 10], 0, 180,
                 fill=(38, 78, 110), width=3)
        draw.arc([x + s // 2, wy, x + s - 4, wy + 10], 0, 180,
                 fill=(38, 78, 110), width=3)
    # Small ship.
    draw.polygon([(x + 12, y + s - 22), (x + s - 12, y + s - 22),
                  (x + s - 20, y + s - 12), (x + 20, y + s - 12)],
                 fill=(60, 60, 60))
    # Drone above.
    dx, dy = x + s // 2, y + 16
    draw.ellipse([dx - 6, dy - 5, dx + 6, dy + 5], fill=(40, 40, 40))
    draw.line([(dx - 16, dy - 6), (dx + 16, dy - 6)], fill=(40, 40, 40), width=3)
    draw.ellipse([dx - 18, dy - 9, dx - 12, dy - 3], fill=(120, 120, 120))
    draw.ellipse([dx + 12, dy - 9, dx + 18, dy - 3], fill=(120, 120, 120))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    M = 28  # outer margin

    # Outer double border.
    d.rectangle([M - 8, M - 8, W - M + 8, H - M + 8], outline=INK, width=3)
    d.rectangle([M - 2, M - 2, W - M + 2, H - M + 2], outline=INK, width=1)

    # ---- Masthead ----
    y = 30
    f_kicker = font(SANS_BOLD, 21)
    d.text((W // 2, y), "THE WORLD IN ONE IMAGE", font=f_kicker,
           fill=MUTED, anchor="ma")
    y += 28
    date_text = "MONDAY, 23 NOVEMBER 2026"
    date_size = 58
    f_date = font(SERIF, date_size)
    while d.textlength(date_text, font=f_date) > W - 2 * M - 10 and date_size > 30:
        date_size -= 2
        f_date = font(SERIF, date_size)
    d.text((W // 2, y), date_text, font=f_date, fill=INK, anchor="ma")
    y += date_size + 16
    d.line([(M, y), (W - M, y)], fill=RED, width=4)
    d.line([(M, y + 7), (W - M, y + 7)], fill=INK, width=2)
    y += 14

    # ---- Lead story ----
    lead_top = y
    ill_w, ill_h = 512, 250
    lead_illustration(d, M, lead_top, ill_w, ill_h)
    # Caption bar under the illustration.
    cap_y = lead_top + ill_h
    d.rectangle([M, cap_y, M + ill_w, cap_y + 30], fill=INK)
    f_cap = font(SANS_BOLD, 15)
    d.text((M + 10, cap_y + 7), "ANTALYA, TURKEY — COP31 ENDS WITHOUT A DEAL",
           font=f_cap, fill=(247, 242, 231))

    tx = M + ill_w + 26
    tw = W - M - tx
    f_lead_kick = font(SANS_BOLD, 19)
    d.text((tx, lead_top + 2), "CLIMATE  •  LEAD STORY", font=f_lead_kick, fill=RED)
    f_lead_head = font(SERIF, 36)
    hy = draw_text_block(d, tx, lead_top + 34,
                         "COP31 collapses with no deal in Antalya",
                         f_lead_head, INK, tw, leading=43)
    d.line([(tx, hy + 6), (tx + tw, hy + 6)], fill=(180, 172, 156), width=1)
    f_lead_body = font(SERIF_REG, 19)
    draw_text_block(
        d, tx, hy + 18,
        "The UN climate summit ends after two days of overtime "
        "with no deal. The EU and some 130 parties reject a "
        "final text that omits fossil fuels.",
        f_lead_body, INK, tw, leading=24)

    y = cap_y + 30 + 12

    # ---- Story cards: 3 columns x 2 rows ----
    gap = 14
    cw = (W - 2 * M - 2 * gap) // 3
    ch = 190
    cards = [
        ("WAR IN EUROPE", RED, icon_burst,
         "Russian strike on Dymer kills at least 10",
         "Rescuers pull a 7-year-old boy alive from the rubble "
         "of a home north of Kyiv."),
        ("MARKETS", DARK_BLUE, icon_chart,
         "AI sell-off rattles world markets",
         "Nikkei falls 5.06%; the S&P 500 fell 3.70% on Friday. "
         "US futures rebound on Monday."),
        ("IRAN WAR", RED, icon_tanker,
         "Tankers ablaze near Hormuz",
         "A US strike hits an oil tanker as Trump threatens to "
         "sink Iranian vessels; Iran says it downed a US MQ-9 drone."),
        ("DIPLOMACY", GREEN, icon_flags,
         "Trump, Xi, Putin agree peace talks",
         "The three leaders meet in Shenzhen and issue a "
         "'Declaration toward Peace', starting nuclear "
         "risk-reduction talks."),
        ("UNITED STATES", DARK_BLUE, icon_ballot,
         "Democrats win biggest House majority since 1992",
         "Democrats take 258 seats."),
        ("WAR AT SEA", RED, icon_drone_ship,
         "Ukraine drone cripples Russian corvette",
         "A naval drone severely damages the Russian corvette "
         "Merkury off the coast of Libya."),
    ]
    f_card_kick = font(SANS_BOLD, 16)
    f_card_head = font(SERIF, 24)
    f_card_body = font(SERIF_REG, 16)
    for row in range(2):
        for col in range(3):
            i = row * 3 + col
            kick, color, icon, head, body = cards[i]
            x0 = M + col * (cw + gap)
            y0 = y + row * (ch + gap)
            d.rectangle([x0, y0, x0 + cw, y0 + ch], outline=(150, 142, 128), width=1)
            d.line([(x0, y0), (x0 + cw, y0)], fill=color, width=4)
            ix = x0 + cw - 62
            iy = y0 + 12
            d.rectangle([ix, iy, ix + 52, iy + 52], outline=color, width=2)
            icon(d, ix + 1, iy + 1, 50)
            d.text((x0 + 12, y0 + 12), kick, font=f_card_kick, fill=color)
            draw_text_block(d, x0 + 12, y0 + 38, head, f_card_head, INK,
                            cw - 76, leading=29)
            n_head_lines = len(wrap(d, head, f_card_head, cw - 76))
            by = y0 + 38 + n_head_lines * 29 + 4
            draw_text_block(d, x0 + 12, by, body, f_card_body, (50, 48, 44),
                            cw - 24, leading=20)

    y = y + 2 * ch + gap + 12

    # ---- Footer ticker ----
    d.line([(M, y), (W - M, y)], fill=INK, width=2)
    y += 10
    f_tick_kick = font(SANS_BOLD, 18)
    d.text((M, y), "ALSO IN THE NEWS", font=f_tick_kick, fill=RED)
    y += 26
    f_tick = font(SERIF_REG, 16)
    ticker = (
        "Anthropic mathematician + Claude claim a proof of the Riemann "
        "Hypothesis  •  Cartel boss 'El Chapo Isidro' captured in Sinaloa  •  "
        "South Korea's annual exports top $1 trillion for the first time  •  "
        "Gaza war left widespread contamination, report finds  •  Bolsonaro "
        "in intensive care  •  Marc Márquez wins an eighth MotoGP title  •  "
        "M6.5 earthquake in the Vanuatu region"
    )
    draw_text_block(d, M, y, ticker, f_tick, INK, W - 2 * M, leading=20)
    n_tick = len(wrap(d, ticker, f_tick, W - 2 * M))
    y += n_tick * 20 + 6
    f_src = font(SANS, 14)
    d.text((W // 2, y), "Sources: wire reports, 23 November 2026  •  One day, one picture",
           font=f_src, fill=MUTED, anchor="ma")

    img.save(OUT, format="PNG", optimize=True)
    print("wrote", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main()
