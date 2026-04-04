#!/usr/bin/env python3
import sys
import numpy as np

QUAD_CHARS = np.array([
    ' ','\u259d','\u2598','\u2580','\u2597','\u2590','\u259a','\u259c',
    '\u2596','\u259e','\u258c','\u259b','\u2584','\u259f','\u2599','\u2588',
])
MASKS = np.array([[(m >> i) & 1 for i in range(4)] for m in range(16)], dtype=np.float32)

W  = int(sys.argv[1]) if len(sys.argv) > 1 else 80
H  = int(sys.argv[2]) if len(sys.argv) > 2 else 30
PW = W * 2
PH = H * 2

sys.stderr.write(f'Grid: {W}x{H} chars  |  Source: {PW}x{PH} pixels\n')

# Pre-build reset string
RESET = '\033[0m'

frame_num = 0
out_write = sys.stdout.write

while True:
    raw = sys.stdin.buffer.read(PW * PH * 3)
    if len(raw) < PW * PH * 3:
        break

    frame = np.frombuffer(raw, dtype=np.uint8).reshape(PH, PW, 3).astype(np.float32)

    # Reshape into (H, W, 4, 3) — 4 pixels per 2x2 cell
    blocks = frame.reshape(H, 2, W, 2, 3).transpose(0, 2, 1, 3, 4).reshape(H, W, 4, 3)

    m     = MASKS.reshape(1, 1, 16, 4, 1)
    p     = blocks[:, :, np.newaxis, :, :]

    fg_avg = (p * m).sum(axis=3) / m.sum(axis=3).clip(min=1)
    bg_avg = (p * (1-m)).sum(axis=3) / (1-m).sum(axis=3).clip(min=1)

    m_exp  = m.transpose(0,1,2,4,3).reshape(1,1,16,4,1)
    diff   = (fg_avg[:,:,:,np.newaxis,:] * m_exp + bg_avg[:,:,:,np.newaxis,:] * (1-m_exp)) - p
    err    = (diff**2).sum(axis=(3,4))

    best_mask = err.argmin(axis=2)                                    # (H,W)
    iy, ix    = np.mgrid[0:H, 0:W]
    best_fg   = fg_avg[iy, ix, best_mask].clip(0,255).astype(np.uint8)  # (H,W,3)
    best_bg   = bg_avg[iy, ix, best_mask].clip(0,255).astype(np.uint8)  # (H,W,3)
    chars     = QUAD_CHARS[best_mask]                                 # (H,W)

    # Build output: vectorize per-row using list comprehension + join
    lines = []
    for cy in range(H):
        row_parts = [
            f'\033[38;2;{best_fg[cy,cx,0]};{best_fg[cy,cx,1]};{best_fg[cy,cx,2]}m'
            f'\033[48;2;{best_bg[cy,cx,0]};{best_bg[cy,cx,1]};{best_bg[cy,cx,2]}m'
            f'{chars[cy,cx]}'
            for cx in range(W)
        ]
        lines.append(''.join(row_parts) + RESET)

    out_write('\n'.join(lines) + '\n---FRAME---\n')
    frame_num += 1
    if frame_num % 10 == 0:
        sys.stderr.write(f'  {frame_num} frames...\n')

sys.stderr.write(f'Done: {frame_num} frames\n')
