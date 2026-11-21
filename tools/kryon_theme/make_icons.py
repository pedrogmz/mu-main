#!/usr/bin/env python3
"""Draw the Kryon theme's button icons and write them as the game's .OZT textures.

Usage, from the MuMain root (needs Pillow):
    uv run --no-project --with pillow python tools/kryon_theme/make_icons.py

Writes tools/kryon_theme/handmade/icons/<name>.OZT; generate_theme.py copies them into the theme,
where a stylesheet names one as icons/<name>.tga (the game swaps the extension for .OZT). Each
icon is a gold line drawing on a transparent square, drawn at 4x and scaled down, in the style of
the web page's top bar icons.

An .OZT file is a 32-bit uncompressed TGA with 4 bytes in front (Render/Textures/OztFile.h).
"""
import math
import struct
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter

SIZE = 48                      # the texture's side, in pixels
SCALE = 4                      # drawn at SIZE * SCALE, then scaled down for smooth edges
GRID = 24.0                    # icons are designed on a 24-unit grid, as the web page's SVGs
STROKE = 1.8                   # line width, in grid units
GOLD = (241, 212, 154, 255)    # the web's icon gold (#F1D49A)
SHADOW = (0, 0, 0, 200)        # the dark line under each stroke, for contrast over the game
OUT_DIR = Path(__file__).resolve().parent / "handmade" / "icons"


class Pen:
    """Draws in grid units on a supersampled canvas."""

    def __init__(self, draw, color, offset=0.0):
        self.draw = draw
        self.color = color
        self.offset = offset
        self.unit = SIZE * SCALE / GRID

    def p(self, x, y):
        return ((x + self.offset) * self.unit, (y + self.offset) * self.unit)

    def width(self, scale=1.0):
        return max(1, round(STROKE * scale * self.unit))

    def line(self, *points, scale=1.0):
        pts = [self.p(x, y) for x, y in points]
        self.draw.line(pts, fill=self.color, width=self.width(scale), joint="curve")
        radius = self.width(scale) / 2
        for x, y in (pts[0], pts[-1]):
            self.draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=self.color)

    def poly(self, *points):
        self.line(*(points + (points[0],)))

    def rect(self, x0, y0, x1, y1):
        self.poly((x0, y0), (x1, y0), (x1, y1), (x0, y1))

    def circle(self, cx, cy, r, fill=False):
        x0, y0 = self.p(cx - r, cy - r)
        x1, y1 = self.p(cx + r, cy + r)
        if fill:
            self.draw.ellipse((x0, y0, x1, y1), fill=self.color)
        else:
            self.draw.ellipse((x0, y0, x1, y1), outline=self.color, width=self.width())

    def arc(self, cx, cy, r, start, end):
        x0, y0 = self.p(cx - r, cy - r)
        x1, y1 = self.p(cx + r, cy + r)
        self.draw.arc((x0, y0, x1, y1), start, end, fill=self.color, width=self.width())

    def fill(self, *points):
        self.draw.polygon([self.p(x, y) for x, y in points], fill=self.color)


# ---------------------------------------------------------------- the icons (24-unit grid)

def close(pen):
    pen.line((6, 6), (18, 18))
    pen.line((18, 6), (6, 18))

def plus(pen):
    pen.line((12, 5), (12, 19))
    pen.line((5, 12), (19, 12))

def expand(pen):  # inventory extension: a bag with a plus
    pen.rect(4, 8, 20, 20)
    pen.line((9, 8), (9, 5), (15, 5), (15, 8))
    pen.line((12, 11), (12, 17))
    pen.line((9, 14), (15, 14))

def repair(pen):  # hammer
    pen.line((5, 19), (13.5, 10.5))
    pen.line((10, 5), (18, 13), scale=2.6)

def shop(pen):  # stall with an awning
    pen.line((4, 9), (6, 4), (18, 4), (20, 9))
    pen.line((4, 9), (20, 9))
    pen.arc(6, 9, 2, 0, 180)
    pen.arc(10, 9, 2, 0, 180)
    pen.arc(14, 9, 2, 0, 180)
    pen.arc(18, 9, 2, 0, 180)
    pen.line((5, 11), (5, 20), (19, 20), (19, 11))
    pen.rect(10, 14, 14, 20)

def quest(pen):  # scroll
    pen.line((7, 5), (17, 5))
    pen.line((7, 5), (7, 19))
    pen.line((17, 5), (17, 19))
    pen.line((5, 19), (19, 19))
    pen.line((10, 9), (14, 9))
    pen.line((10, 12), (14, 12))
    pen.line((10, 15), (14, 15))

def pet(pen):  # paw
    pen.circle(12, 15, 3.6)
    pen.circle(7, 10, 1.7, fill=True)
    pen.circle(10.5, 6.5, 1.7, fill=True)
    pen.circle(13.5, 6.5, 1.7, fill=True)
    pen.circle(17, 10, 1.7, fill=True)

def master(pen):  # star
    points = []
    for i in range(10):
        angle = -math.pi / 2 + i * math.pi / 5
        radius = 8 if i % 2 == 0 else 3.5
        points.append((12 + radius * math.cos(angle), 12.5 + radius * math.sin(angle)))
    pen.poly(*points)

def minimize(pen):
    pen.line((6, 17), (18, 17))

def maximize(pen):
    pen.rect(6, 6, 18, 18)

def restore(pen):
    pen.rect(5, 9, 15, 19)
    pen.line((9, 9), (9, 5), (19, 5), (19, 15), (15, 15))

def grip(pen):  # the resize corner
    pen.line((19, 9), (9, 19))
    pen.line((19, 14), (14, 19))

def chat_normal(pen):  # speech bubble
    pen.poly((4, 6), (20, 6), (20, 16), (11, 16), (7, 20), (7, 16), (4, 16))

def chat_party(pen):  # two people
    pen.circle(9, 8, 3)
    pen.arc(9, 19, 6, 180, 360)
    pen.circle(16.5, 9, 2.5)
    pen.arc(17, 19, 4.5, 200, 340)

def chat_guild(pen):  # shield
    pen.line((12, 4), (19, 7), (19, 12))
    pen.line((12, 4), (5, 7), (5, 12))
    pen.arc(12, 12, 7, 0, 180)

def chat_gens(pen):  # crossed swords
    pen.line((5, 5), (17, 17))
    pen.line((19, 5), (7, 17))
    pen.line((15, 19), (19, 15))
    pen.line((5, 15), (9, 19))

def chat_whisper(pen):  # bubble with a slash: block whispers
    pen.poly((5, 7), (19, 7), (19, 16), (11, 16), (8, 19), (8, 16), (5, 16))
    pen.line((4, 20), (20, 4))

def chat_system(pen):  # info
    pen.circle(12, 12, 8)
    pen.circle(12, 8, 1.2, fill=True)
    pen.line((12, 11), (12, 16.5))

def chat_log(pen):  # lines of text
    pen.line((5, 7), (19, 7))
    pen.line((5, 11), (19, 11))
    pen.line((5, 15), (19, 15))
    pen.line((5, 19), (13, 19))

def chat_frame(pen):  # a window
    pen.rect(4, 5, 20, 19)
    pen.line((4, 9), (20, 9))

def chat_size(pen):  # taller / shorter
    pen.line((12, 4), (12, 20))
    pen.line((8, 8), (12, 4), (16, 8))
    pen.line((8, 16), (12, 20), (16, 16))

def chat_alpha(pen):  # half-filled circle: transparency
    pen.circle(12, 12, 8)
    pen.fill(*[(12 + 8 * math.cos(a / 20 * math.pi), 12 + 8 * math.sin(a / 20 * math.pi)) for a in range(-10, 11)])


def chevron_left(pen):
    pen.line((15, 5), (8, 12), (15, 19))

def chevron_right(pen):
    pen.line((9, 5), (16, 12), (9, 19))

def gift(pen):  # a wrapped box
    pen.rect(4, 10, 20, 20)
    pen.line((3, 10), (21, 10))
    pen.line((12, 10), (12, 20))
    pen.line((12, 10), (8, 5), (6, 7), (12, 10))
    pen.line((12, 10), (16, 5), (18, 7), (12, 10))

def coin(pen):  # recharge: a coin with a plus
    pen.circle(12, 12, 8)
    pen.line((12, 8), (12, 16))
    pen.line((8, 12), (16, 12))

def refresh(pen):  # a circular arrow
    pen.arc(12, 12, 7, 330, 270)
    pen.line((9, 2), (12.5, 5), (9, 8))

def crown(pen):  # the party leader
    pen.fill((4, 8), (8.5, 12), (12, 5), (15.5, 12), (20, 8), (18, 18), (6, 18))
    pen.line((6, 20), (18, 20))


ICONS = {
    "chevron_left": chevron_left, "chevron_right": chevron_right, "gift": gift, "coin": coin,
    "refresh": refresh, "crown": crown,
    "close": close, "plus": plus, "expand": expand, "repair": repair, "shop": shop,
    "quest": quest, "pet": pet, "master": master,
    "minimize": minimize, "maximize": maximize, "restore": restore, "grip": grip,
    "chat_normal": chat_normal, "chat_party": chat_party, "chat_guild": chat_guild, "chat_gens": chat_gens,
    "chat_whisper": chat_whisper, "chat_system": chat_system, "chat_log": chat_log,
    "chat_frame": chat_frame, "chat_size": chat_size, "chat_alpha": chat_alpha,
}


def render(draw_icon):
    big = SIZE * SCALE
    shadow = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw_icon(Pen(ImageDraw.Draw(shadow), SHADOW, offset=0.6))
    shadow = shadow.filter(ImageFilter.GaussianBlur(SCALE))
    image = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    draw_icon(Pen(ImageDraw.Draw(image), GOLD))
    shadow.alpha_composite(image)
    return shadow.resize((SIZE, SIZE), Image.LANCZOS)


def write_ozt(image, path):
    """4 bytes, then a TGA header and BGRA pixels, bottom row first."""
    width, height = image.size
    tga_header = struct.pack("<BBBHHBHHHHBB", 0, 0, 2, 0, 0, 0, 0, 0, width, height, 32, 8)
    pixels = bytearray()
    data = image.load()
    for y in range(height - 1, -1, -1):
        for x in range(width):
            r, g, b, a = data[x, y]
            pixels += bytes((b, g, r, a))
    path.write_bytes(bytes(4) + tga_header + bytes(pixels))


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, draw_icon in ICONS.items():
        write_ozt(render(draw_icon), OUT_DIR / (name + ".OZT"))
    print("%d icons written to %s" % (len(ICONS), OUT_DIR))


if __name__ == "__main__":
    main()
