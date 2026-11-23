#!/usr/bin/env python3
"""The World Today - front page of Monday 23 November 2026.

Draws a newspaper front page that sums up the day's world news, using
only the Python standard library. Writes entry.png into MAKEFUN_OUTPUT_DIR
(default /output). Deterministic: the same bytes on every run.
"""

import binascii
import math
import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)
INK = (17, 17, 17)
GREY = (110, 108, 100)
RED = (179, 35, 27)
NAVY = (22, 35, 63)
SEA = (14, 42, 68)
SEA_LIGHT = (42, 90, 122)
SKY_MID = (74, 53, 80)
HORIZON = (217, 93, 30)
SUN = (245, 166, 35)
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)
STEEL = (120, 126, 134)
SMOKE = (106, 106, 106)
SMOKE_LIGHT = (150, 148, 142)
FLAME = (232, 116, 24)
FLAME_YELLOW = (250, 200, 60)
GLOBE_BLUE = (42, 109, 176)
LAND = (58, 158, 77)
BUILDING = (96, 100, 108)
WINDOW = (30, 34, 44)

# ------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 bits, '1' = ink. Lowercase sits on rows 1-6
# with descenders reaching row 6.
FONT = {
    'A': ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    'B': ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    'C': ["01110", "10001", "10000", "10000", "10000", "10001", "01110"],
    'D': ["11110", "10001", "10001", "10001", "10001", "10001", "11110"],
    'E': ["11111", "10000", "10000", "11110", "10000", "10000", "11111"],
    'F': ["11111", "10000", "10000", "11110", "10000", "10000", "10000"],
    'G': ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    'H': ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    'I': ["01110", "00100", "00100", "00100", "00100", "00100", "01110"],
    'J': ["00111", "00010", "00010", "00010", "00010", "10010", "01100"],
    'K': ["10001", "10010", "10100", "11000", "10100", "10010", "10001"],
    'L': ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    'M': ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    'N': ["10001", "11001", "10101", "10011", "10001", "10001", "10001"],
    'O': ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    'P': ["11110", "10001", "10001", "11110", "10000", "10000", "10000"],
    'Q': ["01110", "10001", "10001", "10001", "10101", "10010", "01101"],
    'R': ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    'S': ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    'T': ["11111", "00100", "00100", "00100", "00100", "00100", "00100"],
    'U': ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    'V': ["10001", "10001", "10001", "10001", "10001", "01010", "00100"],
    'W': ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
    'X': ["10001", "10001", "01010", "00100", "01010", "10001", "10001"],
    'Y': ["10001", "10001", "01010", "00100", "00100", "00100", "00100"],
    'Z': ["11111", "00001", "00010", "00100", "01000", "10000", "11111"],
    '0': ["01110", "10001", "10011", "10101", "11001", "10001", "01110"],
    '1': ["00100", "01100", "00100", "00100", "00100", "00100", "01110"],
    '2': ["01110", "10001", "00001", "00110", "01000", "10000", "11111"],
    '3': ["11111", "00010", "00100", "00010", "00001", "10001", "01110"],
    '4': ["00010", "00110", "01010", "10010", "11111", "00010", "00010"],
    '5': ["11111", "10000", "11110", "00001", "00001", "10001", "01110"],
    '6': ["00110", "01000", "10000", "11110", "10001", "10001", "01110"],
    '7': ["11111", "00001", "00010", "00100", "01000", "01000", "01000"],
    '8': ["01110", "10001", "10001", "01110", "10001", "10001", "01110"],
    '9': ["01110", "10001", "10001", "01111", "00001", "00010", "01100"],
    'a': ["00000", "00000", "01110", "00001", "01111", "10001", "01111"],
    'b': ["10000", "10000", "11110", "10001", "10001", "10001", "11110"],
    'c': ["00000", "00000", "01110", "10001", "10000", "10001", "01110"],
    'd': ["00001", "00001", "01111", "10001", "10001", "10001", "01111"],
    'e': ["00000", "00000", "01110", "10001", "11111", "10000", "01110"],
    'f': ["00110", "01001", "01000", "11110", "01000", "01000", "01000"],
    'g': ["00000", "01111", "10001", "10001", "01111", "00001", "01110"],
    'h': ["10000", "10000", "11110", "10001", "10001", "10001", "10001"],
    'i': ["00100", "00000", "01100", "00100", "00100", "00100", "01110"],
    'j': ["00010", "00000", "00110", "00010", "00010", "10010", "01100"],
    'k': ["10000", "10000", "10010", "10100", "11000", "10100", "10010"],
    'l': ["01100", "00100", "00100", "00100", "00100", "00100", "01110"],
    'm': ["00000", "00000", "11010", "10101", "10101", "10101", "10101"],
    'n': ["00000", "00000", "11110", "10001", "10001", "10001", "10001"],
    'o': ["00000", "00000", "01110", "10001", "10001", "10001", "01110"],
    'p': ["00000", "11110", "10001", "10001", "11110", "10000", "10000"],
    'q': ["00000", "01111", "10001", "10001", "01111", "00001", "01110"],
    'r': ["00000", "00000", "10110", "11001", "10000", "10000", "10000"],
    's': ["00000", "00000", "01111", "10000", "01110", "00001", "11110"],
    't': ["01000", "01000", "11110", "01000", "01000", "01000", "00110"],
    'u': ["00000", "00000", "10001", "10001", "10001", "10011", "01101"],
    'v': ["00000", "00000", "10001", "10001", "10001", "01010", "00100"],
    'w': ["00000", "00000", "10001", "10101", "10101", "10101", "01010"],
    'x': ["00000", "00000", "10001", "01010", "00100", "01010", "10001"],
    'y': ["00000", "10001", "10001", "10001", "01111", "00001", "01110"],
    'z': ["00000", "00000", "11111", "00010", "00100", "01000", "11111"],
    ' ': ["00000", "00000", "00000", "00000", "00000", "00000", "00000"],
    '.': ["00000", "00000", "00000", "00000", "00000", "01100", "01100"],
    ',': ["00000", "00000", "00000", "00000", "01100", "00100", "01000"],
    ':': ["00000", "01100", "01100", "00000", "01100", "01100", "00000"],
    ';': ["00000", "01100", "01100", "00000", "01100", "00100", "01000"],
    "'": ["00100", "00100", "01000", "00000", "00000", "00000", "00000"],
    '"': ["01010", "01010", "01010", "00000", "00000", "00000", "00000"],
    '!': ["00100", "00100", "00100", "00100", "00100", "00000", "00100"],
    '?': ["01110", "10001", "00001", "00110", "00100", "00000", "00100"],
    '-': ["00000", "00000", "00000", "01110", "00000", "00000", "00000"],
    '(': ["00010", "00100", "01000", "01000", "01000", "00100", "00010"],
    ')': ["01000", "00100", "00010", "00010", "00010", "00100", "01000"],
    '/': ["00001", "00010", "00010", "00100", "01000", "01000", "10000"],
    '&': ["01100", "10010", "10100", "01000", "10101", "10010", "01101"],
    '%': ["11001", "11010", "00010", "00100", "01000", "01011", "10011"],
    '$': ["00100", "01111", "10100", "01110", "00101", "11110", "00100"],
    '+': ["00000", "00100", "00100", "01110", "00100", "00100", "00000"],
    '=': ["00000", "00000", "01110", "00000", "01110", "00000", "00000"],
    '\u00b7': ["00000", "00000", "00000", "01100", "01100", "00000", "00000"],
}


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(w * h * 3)
        for i in range(0, w * h * 3, 3):
            self.px[i] = bg[0]
            self.px[i + 1] = bg[1]
            self.px[i + 2] = bg[2]

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i] = color[0]
            self.px[i + 1] = color[1]
            self.px[i + 2] = color[2]

    def rect(self, x, y, w, h, color):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i] = color[0]
                self.px[i + 1] = color[1]
                self.px[i + 2] = color[2]

    def line(self, x0, y0, x1, y1, color, thick=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            for a in range(thick):
                for b in range(thick):
                    self.set(x + a, y + b, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                if (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r:
                    self.set(xx, yy, color)

    def circle_outline(self, cx, cy, r, color, thick=2):
        for a in range(360):
            rad = math.radians(a)
            for t in range(thick):
                self.set(int(cx + (r + t) * math.cos(rad)),
                         int(cy + (r + t) * math.sin(rad)), color)

    def poly(self, points, color):
        """Fill a simple polygon with a scanline fill."""
        if len(points) < 3:
            return
        ys = [p[1] for p in points]
        for y in range(min(ys), max(ys) + 1):
            nodes = []
            n = len(points)
            for i in range(n):
                x0, y0 = points[i]
                x1, y1 = points[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    nodes.append(int(x0 + (y - y0) * (x1 - x0) / (y1 - y0)))
            nodes.sort()
            for k in range(0, len(nodes) - 1, 2):
                for x in range(nodes[k], nodes[k + 1] + 1):
                    self.set(x, y, color)


# ------------------------------------------------------------------- text
def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_char(cv, x, y, ch, scale, color):
    glyph = FONT.get(ch)
    if glyph is None:
        return
    for r in range(7):
        row = glyph[r]
        for c in range(5):
            if row[c] == '1':
                cv.rect(x + c * scale, y + r * scale, scale, scale, color)


def draw_text(cv, x, y, s, scale, color):
    cx = x
    for ch in s:
        draw_char(cv, cx, y, ch, scale, color)
        cx += 6 * scale


def draw_text_centered(cv, cx, y, s, scale, color):
    draw_text(cv, cx - text_width(s, scale) // 2, y, s, scale, color)


def wrap_text(s, max_px, scale):
    """Greedy word wrap; returns a list of lines that fit max_px."""
    words = s.split(' ')
    lines = []
    cur = ''
    for word in words:
        trial = word if not cur else cur + ' ' + word
        if text_width(trial, scale) <= max_px:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(cv, x, y, s, max_px, scale, color, line_gap=4):
    lines = wrap_text(s, max_px, scale)
    for i, line in enumerate(lines):
        draw_text(cv, x, y + i * (7 * scale + line_gap), line, scale, color)
    return len(lines)


# -------------------------------------------------------------------- png
def write_png(path, cv):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]

    def chunk(kind, data):
        out = struct.pack('>I', len(data)) + kind + data
        return out + struct.pack('>I', binascii.crc32(kind + data) & 0xFFFFFFFF)

    ihdr = struct.pack('>IIBBBBB', cv.w, cv.h, 8, 2, 0, 0, 0)
    png = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', ihdr)
           + chunk(b'IDAT', zlib.compress(bytes(raw), 9))
           + chunk(b'IEND', b''))
    with open(path, 'wb') as f:
        f.write(png)
    return len(png)


# ------------------------------------------------------------ hero scene
def draw_hero(cv, x, y, w, h):
    """Dusk over the Strait of Hormuz: a tanker, missile trails, fire."""
    # Sky bands: deep navy down to a burning horizon.
    bands = [
        (NAVY, 0.00), (NAVY, 0.28), (SKY_MID, 0.52),
        ((146, 74, 66), 0.68), (HORIZON, 0.82), ((232, 140, 52), 0.94),
    ]
    horizon = y + int(h * 0.80)
    for yy in range(y, horizon):
        f = (yy - y) / max(1, horizon - y)
        col = NAVY
        for i in range(len(bands) - 1):
            c0, f0 = bands[i]
            c1, f1 = bands[i + 1]
            if f0 <= f <= f1:
                t = (f - f0) / max(0.001, f1 - f0)
                col = tuple(int(c0[k] + (c1[k] - c0[k]) * t) for k in range(3))
                break
        cv.rect(x, yy, w, 1, col)
    # Setting sun, half sunk at the horizon.
    cv.disc(x + w - 130, horizon - 6, 30, SUN)
    cv.disc(x + w - 130, horizon - 6, 22, (250, 190, 80))
    # Sea.
    cv.rect(x, horizon, w, y + h - horizon, SEA)
    for k in range(3):
        wy = horizon + 14 + k * 14
        for wx in range(x + 10, x + w - 10, 46):
            off = int(3 * math.sin((wx + k * 31) / 40.0))
            cv.line(wx, wy + off, wx + 30, wy + off, SEA_LIGHT, 2)
    # Tanker: hull, deck containers, superstructure, funnel.
    hx, hy = x + 90, horizon - 46
    cv.rect(hx, hy, 430, 44, BLACK)                       # hull
    cv.rect(hx, hy + 34, 430, 10, (120, 30, 24))          # hull stripe
    cv.rect(hx + 330, hy - 46, 80, 46, WHITE)             # superstructure
    cv.rect(hx + 330, hy - 46, 80, 6, (180, 40, 30))      # superstructure top
    for i in range(4):                                     # windows
        cv.rect(hx + 340 + i * 18, hy - 36, 10, 8, WINDOW)
    cont_colors = [(176, 48, 36), (36, 96, 160), (46, 128, 84), (200, 150, 40)]
    for i in range(6):
        cv.rect(hx + 20 + i * 48, hy - 30, 44, 30,
                cont_colors[i % len(cont_colors)])
        cv.rect(hx + 20 + i * 48, hy - 30, 44, 3, (0, 0, 0))
    cv.rect(hx + 300, hy - 58, 26, 58, (60, 60, 60))       # funnel
    cv.rect(hx + 300, hy - 58, 26, 8, (176, 48, 36))
    # Smoke from the funnel, drifting left.
    for i, (sx, sy, sr) in enumerate([(hx + 313, hy - 78, 12),
                                      (hx + 296, hy - 100, 16),
                                      (hx + 272, hy - 118, 20),
                                      (hx + 242, hy - 130, 24)]):
        cv.disc(sx, sy, sr, SMOKE_LIGHT if i % 2 else SMOKE)
    # Missile trails arcing down from the top right.
    for t in range(0, 21):
        f = t / 20.0
        px = int(x + w - 60 - f * 260)
        py = int(y + 8 + f * f * 250)
        cv.disc(px, py, 4 if t % 3 == 0 else 2, FLAME_YELLOW)
    cv.disc(x + w - 60, y + 8, 7, WHITE)
    for t in range(0, 21):
        f = t / 20.0
        px = int(x + w - 180 - f * 200)
        py = int(y + 30 + f * f * 210)
        cv.disc(px, py, 4 if t % 3 == 0 else 2, FLAME_YELLOW)
    cv.disc(x + w - 180, y + 30, 6, WHITE)
    # Explosion burst on the water, right of the tanker.
    ex, ey = x + 640, horizon - 8
    for r, col in [(26, FLAME), (18, FLAME_YELLOW), (10, WHITE)]:
        cv.disc(ex, ey, r, col)
    for a in range(0, 360, 45):
        rad = math.radians(a)
        cv.line(ex, ey, int(ex + 44 * math.cos(rad)),
                int(ey + 30 * math.sin(rad)), FLAME, 3)
    # Fire and smoke column above the burst.
    for i, (sx, sy, sr) in enumerate([(ex, ey - 26, 14), (ex + 8, ey - 52, 18),
                                      (ex - 6, ey - 80, 22), (ex + 4, ey - 106, 26)]):
        cv.disc(sx, sy, sr, SMOKE if i % 2 else SMOKE_LIGHT)
    cv.disc(ex, ey - 22, 10, FLAME)
    cv.disc(ex, ey - 22, 5, FLAME_YELLOW)


# ------------------------------------------------------------ story icons
def draw_globe_icon(cv, x, y, w, h):
    """COP31: a cracked globe."""
    cx, cy = x + w // 2, y + h // 2 - 6
    r = 62
    cv.disc(cx, cy, r, GLOBE_BLUE)
    cv.circle_outline(cx, cy, r, INK, 2)
    # Land blobs.
    cv.poly([(cx - 44, cy - 26), (cx - 18, cy - 40), (cx + 2, cy - 30),
             (cx - 6, cy - 8), (cx - 30, cy - 6)], LAND)
    cv.poly([(cx + 12, cy + 8), (cx + 40, cy - 2), (cx + 46, cy + 22),
             (cx + 22, cy + 34), (cx + 6, cy + 26)], LAND)
    cv.poly([(cx - 34, cy + 26), (cx - 12, cy + 20), (cx - 4, cy + 40),
             (cx - 24, cy + 48)], LAND)
    # Latitude lines.
    cv.line(cx - r + 8, cy - 24, cx + r - 8, cy - 24, (120, 180, 220), 2)
    cv.line(cx - r + 4, cy + 24, cx + r - 4, cy + 24, (120, 180, 220), 2)
    # Crack: a jagged red line across the globe.
    crack = [(cx - 52, cy - 44), (cx - 28, cy - 18), (cx - 38, cy + 6),
             (cx - 8, cy + 22), (cx + 6, cy + 44), (cx + 30, cy + 52)]
    for i in range(len(crack) - 1):
        cv.line(crack[i][0], crack[i][1], crack[i + 1][0], crack[i + 1][1],
                RED, 4)


def draw_drone_icon(cv, x, y, w, h):
    """Ukraine: a drone over a shelled building."""
    bx, by = x + 56, y + 78
    cv.rect(bx, by, 200, 82, BUILDING)
    cv.rect(bx, by - 18, 200, 18, (70, 74, 82))
    for row in range(3):
        for col in range(6):
            cv.rect(bx + 14 + col * 32, by + 12 + row * 24, 16, 14, WINDOW)
    # Smoke rising from the roof.
    for i, (sx, sy, sr) in enumerate([(bx + 60, by - 34, 12),
                                      (bx + 48, by - 56, 16),
                                      (bx + 66, by - 76, 20)]):
        cv.disc(sx, sy, sr, SMOKE_LIGHT if i % 2 else SMOKE)
    # Drone above, top right.
    dx, dy = x + w - 78, y + 34
    cv.line(dx - 34, dy, dx + 34, dy, INK, 4)
    cv.line(dx, dy - 22, dx, dy + 22, INK, 4)
    for ox, oy in [(-34, 0), (34, 0), (0, -22), (0, 22)]:
        cv.circle_outline(dx + ox, dy + oy, 12, INK, 2)
    cv.disc(dx, dy, 8, INK)


def draw_factory_icon(cv, x, y, w, h):
    """Indonesia: a factory on fire."""
    bx, by = x + 46, y + 84
    cv.rect(bx, by, 220, 76, BUILDING)
    # Sawtooth roof.
    cv.poly([(bx, by), (bx + 55, by - 26), (bx + 110, by),
             (bx + 165, by - 26), (bx + 220, by)], (70, 74, 82))
    # Chimney, shortened so its smoke stays inside the icon area.
    cv.rect(bx + 186, by - 44, 26, 44, (70, 74, 82))
    cv.rect(bx + 186, by - 44, 26, 8, RED)
    # Flames along the roofline.
    for fx in range(bx + 12, bx + 200, 34):
        cv.poly([(fx, by - 2), (fx + 12, by - 34), (fx + 24, by - 2)], FLAME)
        cv.poly([(fx + 6, by - 2), (fx + 12, by - 20), (fx + 18, by - 2)],
                FLAME_YELLOW)
    # Windows.
    for col in range(5):
        cv.rect(bx + 16 + col * 42, by + 22, 20, 18, WINDOW)
    # Smoke from the chimney, kept above the chimney top and inside
    # the icon area (y >= 560).
    for i, (sx, sy, sr) in enumerate([(bx + 199, by - 58, 11),
                                      (bx + 188, by - 72, 14),
                                      (bx + 199, by - 84, 17)]):
        cv.disc(sx, sy, sr, SMOKE if i % 2 else SMOKE_LIGHT)


# ---------------------------------------------------------------- layout
def build_page():
    cv = Canvas(W, H, PAPER)
    m = 28                      # margin
    right = W - m               # 996
    content_w = right - m       # 968

    # Masthead.
    draw_text_centered(cv, W // 2, 30, "THE WORLD TODAY", 6, INK)
    cv.rect(m, 92, content_w, 3, INK)
    cv.rect(m, 98, content_w, 1, INK)
    # Date bar: the day this page sums up, unmissable.
    cv.rect(m, 108, content_w, 40, BLACK)
    draw_text_centered(cv, W // 2, 119, "MONDAY 23 NOVEMBER 2026", 3, WHITE)

    # Hero picture.
    hx, hy, hw, hh = m, 164, content_w, 272
    cv.rect(hx - 2, hy - 2, hw + 4, hh + 4, INK)
    draw_hero(cv, hx, hy, hw, hh)

    # Hero headline and standfirst.
    draw_text(cv, m, 452, "WAR WIDENS IN THE GULF", 3, RED)
    draw_wrapped(cv, m, 490,
                 "Iranian missiles strike a US base in Bahrain, Houthi "
                 "missiles are fired at Saudi Arabia, and attacks on "
                 "tankers in the Strait of Hormuz reach a new high.",
                 content_w, 2, INK)
    cv.rect(m, 544, content_w, 2, INK)

    # Three story columns.
    col_w = 312
    col_x = [m, m + 328, m + 656]
    stories = [
        ("CLIMATE TALKS COLLAPSE",
         "COP31 ends with no deal. The final draft leaves out fossil "
         "fuels, and the talks break down over money.",
         draw_globe_icon),
        ("DRONE HITS KYIV REGION",
         "At least 14 people are missing after a Russian drone hits a "
         "building. A Russian cargo ship burns after an attack.",
         draw_drone_icon),
        ("FACTORY FIRE IN INDONESIA",
         "A fire at a factory in Indonesia leaves dozens of workers "
         "missing. Rescuers search the ruins.",
         draw_factory_icon),
    ]
    for i, (headline, body, icon) in enumerate(stories):
        x = col_x[i]
        if i > 0:
            cv.rect(x - 9, 560, 1, 352, GREY)
        icon(cv, x, 560, col_w, 160)
        draw_wrapped(cv, x, 730, headline, col_w, 2, INK)
        draw_wrapped(cv, x, 780, body, col_w, 2, (40, 40, 40))

    # Also today: breadth across regions and fields.
    cv.rect(m, 920, content_w, 2, INK)
    draw_wrapped(cv, m, 934,
                 "ALSO: Nepal's PM meets Modi in Delhi; India 720/9 in "
                 "Wellington; South Korea's education minister quits over "
                 "AI exam cheating.",
                 content_w, 2, INK)
    return cv


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    cv = build_page()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path, cv)
    print("wrote %s: %d bytes, %dx%d" % (path, size, W, H))


if __name__ == "__main__":
    main()
