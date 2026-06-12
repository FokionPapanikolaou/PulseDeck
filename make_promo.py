"""Create a clean promo banner using the real widget closeup."""
from PIL import Image, ImageDraw, ImageFont
import os

D = os.path.dirname(os.path.abspath(__file__))
shot = Image.open(os.path.join(D, 'assets', 'screenshots', 'widget_closeup.png')).convert('RGBA')

W, H = 900, 460
img = Image.new('RGBA', (W, H), (13, 17, 23, 255))
d = ImageDraw.Draw(img)
# gradient-ish top band
for y in range(H):
    t = y / H
    d.line([(0,y),(W,y)], fill=(int(13+t*8), int(17+t*10), int(23+t*14), 255))

def font(px, bold=True):
    name = 'segoeuib.ttf' if bold else 'segoeui.ttf'
    try: return ImageFont.truetype(name, px)
    except OSError: return ImageFont.load_default()

# Title
d.text((50, 50), 'PulseDeck', font=font(56), fill=(255,255,255,255))
d.text((52, 122), "Your PC's pulse β€” live on the Windows 11 taskbar",
       font=font(22, False), fill=(160, 200, 255, 255))

# PulseDeck shield emblem top-right
try:
    ic = Image.open(os.path.join(D, 'assets', 'pulsebar_emblem.png')).convert('RGBA').resize((150,150), Image.LANCZOS)
    img.alpha_composite(ic, (W-185, 28))
except FileNotFoundError:
    pass

# Widget closeup on a faux taskbar strip
strip_y = 250
d.rectangle([0, strip_y, W, strip_y+90], fill=(8, 11, 16, 255))
scale = 1.6
sw, sh = int(shot.width*scale), int(shot.height*scale)
big = shot.resize((sw, sh), Image.LANCZOS)
img.alpha_composite(big, (40, strip_y + (90-sh)//2))

# Feature bullets
feats = ['Live CPU Β· RAM Β· GPU Β· Network', 'Sits right on the taskbar',
         'Weather, 10 themes & 8 languages', 'Free Β· Auto-start with Windows']
fy = strip_y + 110
for f in feats:
    d.ellipse([50, fy+8, 60, fy+18], fill=(63, 185, 80, 255))
    d.text((74, fy), f, font=font(20, False), fill=(220, 225, 230, 255))
    fy += 30

img.convert('RGB').save(os.path.join(D, 'assets', 'promo_banner.png'))
print('Saved promo_banner.png')
