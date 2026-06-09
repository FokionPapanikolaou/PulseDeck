"""Generate crisp 16px monochrome menu icons (white lines, transparent bg)."""
from PIL import Image, ImageDraw, ImageFont
import os, math

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons', 'menu')
os.makedirs(OUT, exist_ok=True)

SS = 8
S = 16 * SS
W = (255, 255, 255, 255)

def canvas():
    return Image.new('RGBA', (S, S), (0, 0, 0, 0))

def save(img, name):
    img.resize((16, 16), Image.LANCZOS).save(os.path.join(OUT, name + '.png'))

def lw(px=1.4):
    return max(1, int(S * px / 16))

def font(px):
    for f in ('segoeuib.ttf', 'arialbd.ttf'):
        try: return ImageFont.truetype(f, px)
        except OSError: continue
    return ImageFont.load_default()

def centered_text(d, txt, px, fill=W, dy=0):
    fnt = font(px)
    tb = d.textbbox((0, 0), txt, font=fnt)
    tw, th = tb[2]-tb[0], tb[3]-tb[1]
    d.text(((S-tw)/2 - tb[0], (S-th)/2 - tb[1] + dy), txt, font=fnt, fill=fill)

# metrics — three bars of different heights
img = canvas(); d = ImageDraw.Draw(img)
xs = [3, 7.5, 12]; hs = [6, 10, 8]
for x, h in zip(xs, hs):
    x *= SS; h *= SS
    d.rectangle([x-1.2*SS, S-2*SS-h, x+1.2*SS, S-2*SS], fill=W)
save(img, 'metrics')

# position — frame with a filled block on the left
img = canvas(); d = ImageDraw.Draw(img)
d.rectangle([2*SS, 4*SS, 14*SS, 12*SS], outline=W, width=lw())
d.rectangle([3*SS, 5*SS, 6*SS, 11*SS], fill=W)
save(img, 'position')

# size — big A
img = canvas(); d = ImageDraw.Draw(img)
centered_text(d, 'A', int(S*0.78))
save(img, 'size')

# opacity — half-filled circle
img = canvas(); d = ImageDraw.Draw(img)
d.ellipse([3*SS, 3*SS, 13*SS, 13*SS], outline=W, width=lw())
d.pieslice([3*SS, 3*SS, 13*SS, 13*SS], 90, 270, fill=W)
save(img, 'opacity')

# refresh / interval — clock
img = canvas(); d = ImageDraw.Draw(img)
d.ellipse([2.5*SS, 2.5*SS, 13.5*SS, 13.5*SS], outline=W, width=lw())
cx = cy = 8*SS
d.line([cx, cy, cx, 4.5*SS], fill=W, width=lw())          # minute hand
d.line([cx, cy, 10.5*SS, cy], fill=W, width=lw())         # hour hand
save(img, 'clock')

# network — globe
img = canvas(); d = ImageDraw.Draw(img)
cx = cy = 8*SS; r = 5.2*SS
d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=W, width=lw())
d.line([cx-r, cy, cx+r, cy], fill=W, width=lw())
d.ellipse([cx-r*0.45, cy-r, cx+r*0.45, cy+r], outline=W, width=lw())
d.line([cx, cy-r, cx, cy+r], fill=W, width=lw())
save(img, 'globe')

# reposition — circular arrow
img = canvas(); d = ImageDraw.Draw(img)
cx = cy = 8*SS; r = 4.6*SS
d.arc([cx-r, cy-r, cx+r, cy+r], 300, 210, fill=W, width=lw(1.5))
# arrow head
ax, ay = cx + r*math.cos(math.radians(300)), cy + r*math.sin(math.radians(300))
d.polygon([(ax-1.6*SS, ay), (ax+1.4*SS, ay-1*SS), (ax+0.6*SS, ay+2*SS)], fill=W)
save(img, 'refresh')

# fullscreen — four corner arrows / expand
img = canvas(); d = ImageDraw.Draw(img)
m = 3*SS; e = 6*SS; t = lw(1.5)
# corners
d.line([m, m, m, m+e*0.6], fill=W, width=t); d.line([m, m, m+e*0.6, m], fill=W, width=t)
d.line([S-m, m, S-m, m+e*0.6], fill=W, width=t); d.line([S-m, m, S-m-e*0.6, m], fill=W, width=t)
d.line([m, S-m, m, S-m-e*0.6], fill=W, width=t); d.line([m, S-m, m+e*0.6, S-m], fill=W, width=t)
d.line([S-m, S-m, S-m, S-m-e*0.6], fill=W, width=t); d.line([S-m, S-m, S-m-e*0.6, S-m], fill=W, width=t)
save(img, 'fullscreen')

# startup — power symbol
img = canvas(); d = ImageDraw.Draw(img)
cx = cy = 8*SS; r = 4.6*SS
d.arc([cx-r, cy-r, cx+r, cy+r], -60, 240, fill=W, width=lw(1.5))
d.line([cx, 2.6*SS, cx, 8*SS], fill=W, width=lw(1.5))
save(img, 'power')

# language — globe with 'A文' hint (use 'A')
img = canvas(); d = ImageDraw.Draw(img)
cx = cy = 8*SS; r = 5.2*SS
d.ellipse([cx-r, cy-r, cx+r, cy+r], outline=W, width=lw())
centered_text(d, '文', int(S*0.42))
save(img, 'language')

# info — i in circle
img = canvas(); d = ImageDraw.Draw(img)
d.ellipse([2.5*SS, 2.5*SS, 13.5*SS, 13.5*SS], outline=W, width=lw())
centered_text(d, 'i', int(S*0.55))
save(img, 'info')

# close — X
img = canvas(); d = ImageDraw.Draw(img)
t = lw(1.6)
d.line([5*SS, 5*SS, 11*SS, 11*SS], fill=W, width=t)
d.line([11*SS, 5*SS, 5*SS, 11*SS], fill=W, width=t)
save(img, 'close')

# heart — donate
img = canvas(); d = ImageDraw.Draw(img)
import math as _m
cx, cy = 8*SS, 8.5*SS; r = 2.6*SS
d.ellipse([cx-2*r, cy-r-0.4*r, cx, cy+r-0.4*r], fill=W)
d.ellipse([cx, cy-r-0.4*r, cx+2*r, cy+r-0.4*r], fill=W)
d.polygon([(cx-2*r+0.3*SS, cy+0.2*r), (cx+2*r-0.3*SS, cy+0.2*r), (cx, cy+3.2*r)], fill=W)
save(img, 'heart')

print('Menu icons saved to', OUT)
