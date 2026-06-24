"""Slice the Gemini 3D icon sheet (background already removed) into the
individual bar/weather PNGs used by PulseDeck. Re-run to regenerate.

Source: assets/gemini_icons_src.png — a 5x3 grid of transparent icons.
"""
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'assets', 'gemini_icons_src.png')
OUT = os.path.join(HERE, 'icons')
SIZE = 32

# tight pixel extents of each icon in the grid (from alpha projection)
COLS = [(22, 111), (174, 235), (299, 377), (435, 512), (573, 646)]
ROWS = [(21, 99), (142, 217), (260, 338)]
PAD = 8

# grid index (row*5+col) -> output filename
MAP = {0: 'cpu.png', 1: 'net.png', 2: 'wx_clear.png', 3: 'wx_partly.png',
       4: 'wx_storm.png', 5: 'gpu.png', 6: 'disk.png', 8: 'wx_rain.png',
       9: 'wx_cloudy.png', 10: 'ram.png', 11: 'battery.png',
       12: 'wx_snow.png', 13: 'wx_fog.png'}

def main():
    src = Image.open(SRC).convert('RGBA')
    W, H = src.size
    for idx, name in MAP.items():
        r, c = divmod(idx, 5)
        x0, x1 = COLS[c]; y0, y1 = ROWS[r]
        box = (max(0, x0 - PAD), max(0, y0 - PAD),
               min(W, x1 + PAD), min(H, y1 + PAD))
        ic = src.crop(box)
        bb = ic.getbbox()
        if bb:
            ic = ic.crop(bb)
        ic.thumbnail((SIZE, SIZE), Image.LANCZOS)
        canvas = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
        canvas.paste(ic, ((SIZE - ic.size[0]) // 2, (SIZE - ic.size[1]) // 2), ic)
        canvas.save(os.path.join(OUT, name))
        print(f'{name:16} <- grid#{idx}')

if __name__ == '__main__':
    main()
    print('Gemini icons written to', OUT)
