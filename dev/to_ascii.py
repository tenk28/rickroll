#!/usr/bin/env python3
"""
High quality UTF-8 terminal video encoder.
Uses 2x2 quadrant block characters with fg+bg truecolor.

Usage:
    ffmpeg -i video.mp4 -vf "scale=PW:PH,format=rgb24" -f rawvideo - 2>/dev/null \\
        | python3 to_ascii_hq.py [char_cols] [char_rows]

Defaults: 80 cols x 30 rows  (source pixels: 160x60)
This displays 4:3 correctly on a standard terminal where
char cells are ~2x taller than wide.

If your terminal has square-ish cells (e.g. some modern fonts),
use 80x60 char grid with source 160x120.
"""
import sys

QUADRANTS = [
    (' ',      0b0000),
    ('\u259d', 0b0001),  # ▝
    ('\u2598', 0b0010),  # ▘
    ('\u2580', 0b0011),  # ▀
    ('\u2597', 0b0100),  # ▗
    ('\u2590', 0b0101),  # ▐
    ('\u259a', 0b0110),  # ▚
    ('\u259c', 0b0111),  # ▜
    ('\u2596', 0b1000),  # ▖
    ('\u259e', 0b1001),  # ▞
    ('\u258c', 0b1010),  # ▌
    ('\u259b', 0b1011),  # ▛
    ('\u2584', 0b1100),  # ▄
    ('\u259f', 0b1101),  # ▟
    ('\u2599', 0b1110),  # ▙
    ('\u2588', 0b1111),  # █
]

def avg_color(pixels):
    n = len(pixels)
    return (sum(p[0] for p in pixels)//n,
            sum(p[1] for p in pixels)//n,
            sum(p[2] for p in pixels)//n)

def color_dist(a, b):
    return (a[0]-b[0])**2 + (a[1]-b[1])**2 + (a[2]-b[2])**2

def best_cell(pixels):
    best_err = float('inf')
    best = ('\u2588', pixels[0], pixels[0])
    for char, mask in QUADRANTS:
        fg_px = [pixels[i] for i in range(4) if (mask >> i) & 1]
        bg_px = [pixels[i] for i in range(4) if not (mask >> i) & 1]
        fg = avg_color(fg_px) if fg_px else (0,0,0)
        bg = avg_color(bg_px) if bg_px else (0,0,0)
        err = sum(color_dist(pixels[i], fg if (mask>>i)&1 else bg) for i in range(4))
        if err < best_err:
            best_err = err
            best = (char, fg, bg)
    return best

# Char grid size (each char = 2x2 source pixels)
W  = int(sys.argv[1]) if len(sys.argv) > 1 else 80
H  = int(sys.argv[2]) if len(sys.argv) > 2 else 30
PW = W * 2   # source pixel width
PH = H * 2   # source pixel height

sys.stderr.write(f'Grid: {W}x{H} chars  |  Source: {PW}x{PH} pixels\n')

frame_num = 0
while True:
    chunk = sys.stdin.buffer.read(PW * PH * 3)
    if len(chunk) < PW * PH * 3:
        break
    out = []
    for cy in range(H):
        row = ''
        for cx in range(W):
            pixels = []
            for dy in range(2):
                for dx in range(2):
                    i = ((cy*2+dy) * PW + (cx*2+dx)) * 3
                    pixels.append((chunk[i], chunk[i+1], chunk[i+2]))
            char, (fr,fg,fb), (br,bg,bb) = best_cell(pixels)
            row += f'\033[38;2;{fr};{fg};{fb}m\033[48;2;{br};{bg};{bb}m{char}'
        row += '\033[0m'
        out.append(row)
    sys.stdout.write('\n'.join(out) + '\n---FRAME---\n')
    frame_num += 1
    if frame_num % 10 == 0:
        sys.stderr.write(f'  {frame_num} frames...\n')

sys.stderr.write(f'Done: {frame_num} frames\n')
