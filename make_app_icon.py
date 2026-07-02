"""Build app.ico and emblem assets from the real transparent PulseDeck shield."""
from PIL import Image, ImageDraw
import os

D = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(D, 'assets')
sh = Image.open(os.path.join(A, 'pulsedeck_logo_transparent.png')).convert('RGBA')
sh = sh.crop(sh.getbbox())                      # trim transparent margins

def square(im, size, scale=1.0):
    side = int(max(im.size) / scale)
    c = Image.new('RGBA', (side, side), (0, 0, 0, 0))
    c.paste(im, ((side - im.width) // 2, (side - im.height) // 2), im)
    return c.resize((size, size), Image.LANCZOS)

# clean transparent emblem (for promo / README), 512
square(sh, 512, scale=0.96).save(os.path.join(A, 'pulsedeck_emblem.png'))

# tray emblem (transparent), 64
square(sh, 64, scale=0.98).save(os.path.join(D, 'icons', 'tray.png'))

# app-icon badge: navy rounded square + shield (used as app.ico)
SZ = 256
badge = Image.new('RGBA', (SZ, SZ), (0, 0, 0, 0))
m = Image.new('L', (SZ, SZ), 0)
ImageDraw.Draw(m).rounded_rectangle([0, 0, SZ - 1, SZ - 1], radius=54, fill=255)
badge.paste(Image.new('RGBA', (SZ, SZ), (13, 17, 23, 255)), (0, 0), m)
emb = square(sh, int(SZ * 0.88))
badge.alpha_composite(emb, ((SZ - emb.width) // 2, (SZ - emb.height) // 2))

# multi-resolution .ico
badge.save(os.path.join(D, 'app.ico'),
           sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
print('saved app.ico + pulsedeck_emblem.png + icons/tray.png')
