"""Generate vibrant flat PNG icons (no black outlines) with anti-aliasing."""
from PIL import Image, ImageDraw, ImageFont
import math, os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'icons')
os.makedirs(OUT, exist_ok=True)

SS = 6          # supersample factor (higher = smoother anti-aliased edges)
SIZE = 32       # final icon size (px)
S = SIZE * SS

WHITE = (255, 255, 255, 255)

def new():
    return Image.new('RGBA', (S, S), (0, 0, 0, 0))

def save(img, name):
    img.resize((SIZE, SIZE), Image.LANCZOS).save(os.path.join(OUT, name))

def font(px):
    for f in ('arialbd.ttf', 'segoeuib.ttf', 'arial.ttf'):
        try:
            return ImageFont.truetype(f, px)
        except OSError:
            continue
    return ImageFont.load_default()

# ── CPU — bright blue chip (procedural fallback; see the hand-made
#    override pass at the bottom of this file) ─────────────────────────
def cpu():
    img = new(); d = ImageDraw.Draw(img)
    m = S * 0.18
    bx0, by0, bx1, by1 = m, m, S-m, S-m
    pin = S * 0.05; plen = S * 0.10
    gold = (255, 205, 40, 255)
    for i in range(4):
        t = bx0 + (bx1-bx0)*(i+0.5)/4
        d.rectangle([t-pin, by0-plen, t+pin, by0], fill=gold)
        d.rectangle([t-pin, by1, t+pin, by1+plen], fill=gold)
        d.rectangle([bx0-plen, t-pin, bx0, t+pin], fill=gold)
        d.rectangle([bx1, t-pin, bx1+plen, t+pin], fill=gold)
    r = S*0.06
    d.rounded_rectangle([bx0, by0, bx1, by1], radius=r, fill=(59, 130, 246, 255))   # blue
    inset = S*0.10
    d.rounded_rectangle([bx0+inset, by0+inset, bx1-inset, by1-inset], radius=r*0.6,
                        fill=(37, 99, 235, 255))                                     # deeper blue
    fnt = font(int(S*0.20))
    tb = d.textbbox((0, 0), 'CPU', font=fnt)
    tw, th = tb[2]-tb[0], tb[3]-tb[1]
    d.text(((S-tw)/2 - tb[0], (S-th)/2 - tb[1]), 'CPU', font=fnt, fill=WHITE)
    save(img, 'cpu.png')

# ── RAM — bright green stick ───────────────────────────────────────────
def ram():
    base = new(); d = ImageDraw.Draw(base)
    w, h = S*0.86, S*0.42
    cx, cy = S/2, S/2
    x0, y0, x1, y1 = cx-w/2, cy-h/2, cx+w/2, cy+h/2
    d.rounded_rectangle([x0, y0, x1, y1-h*0.18], radius=S*0.03, fill=(34, 197, 94, 255))  # green
    n = 4
    gap = (w-S*0.06)/n; csz = gap*0.6
    for i in range(n):
        ccx = x0 + S*0.03 + gap*i + gap/2; ccy = cy - h*0.06
        d.rounded_rectangle([ccx-csz/2, ccy-csz/2, ccx+csz/2, ccy+csz/2], radius=S*0.015,
                            fill=(56, 189, 248, 255))                                 # cyan chips
    teeth = 10
    tw = (w-S*0.08)/teeth
    for i in range(teeth):
        tx = x0 + S*0.04 + tw*i
        d.rectangle([tx+tw*0.15, y1-h*0.22, tx+tw*0.85, y1-h*0.02], fill=(255, 205, 40, 255))  # gold
    d.rectangle([cx-S*0.03, y1-h*0.22, cx+S*0.03, y1], fill=(0, 0, 0, 0))
    save(base.rotate(30, resample=Image.BICUBIC, expand=False), 'ram.png')

# ── NET — cyan globe ───────────────────────────────────────────────────
def net():
    img = new(); d = ImageDraw.Draw(img)
    m = S*0.10; cx, cy = S/2, S/2; r = (S-2*m)/2
    col = (34, 211, 238, 255)        # cyan
    ow = int(S*0.045); lw = int(S*0.035)
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=None, outline=col, width=ow)
    for fy in (-0.62, -0.32, 0, 0.32, 0.62):
        yy = cy + r*fy
        dx = math.sqrt(max(0, r*r - (r*fy)**2)) - ow*0.4
        d.line([cx-dx, yy, cx+dx, yy], fill=col, width=lw)
    d.line([cx, cy-r+ow*0.4, cx, cy+r-ow*0.4], fill=col, width=lw)
    for fw in (0.40, 0.78):
        d.ellipse([cx-r*fw, cy-r, cx+r*fw, cy+r], outline=col, width=lw)
    save(img, 'net.png')

# ── NET (Wi-Fi) — cyan signal arcs + dot ──────────────────────────────
def net_wifi():
    img = new(); d = ImageDraw.Draw(img)
    col = (34, 211, 238, 255)
    cx, cy = S/2, S*0.82
    lw = int(S*0.075)
    for fr in (0.62, 0.44, 0.26):                   # three arcs, outer→inner
        r = S*fr
        d.arc([cx-r, cy-r, cx+r, cy+r], start=222, end=318, fill=col, width=lw)
    dr = S*0.075
    d.ellipse([cx-dr, cy-dr*1.9, cx+dr, cy+dr*0.1], fill=col)
    save(img, 'net_wifi.png')

# ── NET (Ethernet) — cyan LAN topology: hub on top, two nodes below ───
def net_eth():
    img = new(); d = ImageDraw.Draw(img)
    col = (34, 211, 238, 255)
    lw = int(S*0.055)
    bs = S*0.20                                     # node box size
    hubx, huby = S/2, S*0.24
    n1x = S*0.24; n2x = S*0.76; ny = S*0.76
    busy = S*0.52                                   # horizontal bus height
    # links
    d.line([hubx, huby, hubx, busy], fill=col, width=lw)
    d.line([n1x, busy, n2x, busy], fill=col, width=lw)
    d.line([n1x, busy, n1x, ny], fill=col, width=lw)
    d.line([n2x, busy, n2x, ny], fill=col, width=lw)
    # nodes (filled, the hub slightly larger)
    hb = bs*1.12
    d.rounded_rectangle([hubx-hb/2, huby-hb/2, hubx+hb/2, huby+hb/2],
                        radius=S*0.035, fill=col)
    for nx in (n1x, n2x):
        d.rounded_rectangle([nx-bs/2, ny-bs/2, nx+bs/2, ny+bs/2],
                            radius=S*0.035, fill=col)
    save(img, 'net_eth.png')

# ── DISK — blue drive ──────────────────────────────────────────────────
def disk():
    img = new(); d = ImageDraw.Draw(img)
    body = (96, 165, 250, 255)       # bright steel blue
    plat = (30, 64, 175, 255)        # deep blue platter
    m = S*0.16
    d.rounded_rectangle([m, m, S-m, S-m], radius=S*0.10, fill=body)
    cx, cy = S/2, S/2; r = S*0.24
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=plat)
    d.ellipse([cx-S*0.05, cy-S*0.05, cx+S*0.05, cy+S*0.05], fill=WHITE)
    d.line([S-m-S*0.06, m+S*0.06, cx+r*0.5, cy-r*0.5], fill=WHITE, width=int(S*0.03))
    save(img, 'disk.png')

# ── BATTERY — bright green ─────────────────────────────────────────────
def battery():
    img = new(); d = ImageDraw.Draw(img)
    green = (34, 197, 94, 255)
    edge = (200, 210, 220, 255)      # light grey edge (not black)
    x0, y0, x1, y1 = S*0.14, S*0.30, S*0.80, S*0.70
    d.rounded_rectangle([x0, y0, x1, y1], radius=S*0.04, outline=edge,
                        width=int(S*0.03), fill=(33, 40, 54, 255))
    d.rounded_rectangle([x1, S*0.42, x1+S*0.07, S*0.58], radius=S*0.02, fill=edge)
    pad = S*0.05
    fillw = (x1-x0-2*pad) * 0.75
    d.rounded_rectangle([x0+pad, y0+pad, x0+pad+fillw, y1-pad], radius=S*0.02, fill=green)
    save(img, 'battery.png')

# ── GPU — teal graphics card ───────────────────────────────────────────
def gpu():
    img = new(); d = ImageDraw.Draw(img)
    board = (20, 184, 166, 255)      # teal
    fan = (224, 242, 254, 255)       # light fans
    m = S*0.13
    d.rounded_rectangle([m, S*0.28, S-m, S-m], radius=S*0.06, fill=board)
    for cx in (S*0.36, S*0.64):
        cy = S*0.60; r = S*0.13
        d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=fan)
        d.ellipse([cx-S*0.03, cy-S*0.03, cx+S*0.03, cy+S*0.03], fill=board)
        for ang in range(0, 360, 60):
            ax = cx + r*0.7*math.cos(math.radians(ang))
            ay = cy + r*0.7*math.sin(math.radians(ang))
            d.line([cx, cy, ax, ay], fill=(13, 148, 136, 255), width=int(S*0.014))
    d.rectangle([m, S*0.20, S*0.5, S*0.30], fill=(186, 230, 253, 255))
    save(img, 'gpu.png')

# ── WEATHER icons ──────────────────────────────────────────────────────
def _sun(d, cx, cy, r, rays=True):
    yellow = (255, 200, 40, 255)
    if rays:
        rw = int(S*0.022)
        for ang in range(0, 360, 45):
            a = math.radians(ang)
            x0 = cx + math.cos(a)*r*1.25; y0 = cy + math.sin(a)*r*1.25
            x1 = cx + math.cos(a)*r*1.65; y1 = cy + math.sin(a)*r*1.65
            d.line([x0, y0, x1, y1], fill=yellow, width=rw)
    d.ellipse([cx-r, cy-r, cx+r, cy+r], fill=yellow)

def _cloud(d, cx, cy, w, color):
    h = w*0.62; b = cy + h*0.18
    d.rounded_rectangle([cx-w*0.5, b-h*0.22, cx+w*0.5, b+h*0.30], radius=h*0.3, fill=color)
    d.ellipse([cx-w*0.5, b-h*0.5, cx-w*0.5+h*0.95, b+h*0.45], fill=color)
    d.ellipse([cx-h*0.5, b-h*0.95, cx+h*0.7, b+h*0.35], fill=color)
    d.ellipse([cx+w*0.5-h*0.95, b-h*0.5, cx+w*0.5, b+h*0.45], fill=color)

CLOUD_W = (236, 240, 245, 255)
CLOUD_GREY = (176, 190, 205, 255)

def wx_clear():
    img = new(); d = ImageDraw.Draw(img)
    _sun(d, S/2, S/2, S*0.22)
    save(img, 'wx_clear.png')

def wx_partly():
    img = new(); d = ImageDraw.Draw(img)
    _sun(d, S*0.36, S*0.36, S*0.16)
    _cloud(d, S*0.56, S*0.58, S*0.62, CLOUD_W)
    save(img, 'wx_partly.png')

def wx_cloudy():
    img = new(); d = ImageDraw.Draw(img)
    _cloud(d, S/2, S*0.46, S*0.74, CLOUD_W)
    save(img, 'wx_cloudy.png')

def wx_fog():
    img = new(); d = ImageDraw.Draw(img)
    _cloud(d, S/2, S*0.36, S*0.70, CLOUD_GREY)
    fog = (200, 210, 220, 255)
    for i, yy in enumerate((0.72, 0.84, 0.96)):
        off = S*0.10 if i % 2 else 0
        d.line([S*0.16+off, S*yy, S*0.84-off, S*yy], fill=fog, width=int(S*0.045))
    save(img, 'wx_fog.png')

def wx_rain():
    img = new(); d = ImageDraw.Draw(img)
    _cloud(d, S/2, S*0.36, S*0.70, CLOUD_GREY)
    blue = (56, 160, 248, 255)
    for x in (0.34, 0.5, 0.66):
        d.line([S*x, S*0.72, S*(x-0.05), S*0.94], fill=blue, width=int(S*0.05))
    save(img, 'wx_rain.png')

def wx_snow():
    img = new(); d = ImageDraw.Draw(img)
    _cloud(d, S/2, S*0.36, S*0.70, CLOUD_W)
    fl = (190, 230, 255, 255)
    for x in (0.34, 0.5, 0.66):
        r = S*0.035
        d.ellipse([S*x-r, S*0.80-r, S*x+r, S*0.80+r], fill=fl)
    save(img, 'wx_snow.png')

def wx_storm():
    img = new(); d = ImageDraw.Draw(img)
    _cloud(d, S/2, S*0.34, S*0.70, (120, 134, 150, 255))
    bolt = (255, 210, 40, 255)
    d.polygon([(S*0.52, S*0.58), (S*0.40, S*0.80), (S*0.50, S*0.80),
               (S*0.44, S*0.98), (S*0.64, S*0.72), (S*0.52, S*0.72)], fill=bolt)
    save(img, 'wx_storm.png')

cpu(); ram(); net(); net_wifi(); net_eth(); disk(); battery(); gpu()
wx_clear(); wx_partly(); wx_cloudy(); wx_fog(); wx_rain(); wx_snow(); wx_storm()
print('Vibrant icons saved to', OUT)

# ── Hand-made art overrides ────────────────────────────────────────────
# Anything in assets/icon_src/<name>.png is user-supplied artwork (full-res,
# background already removed). It always wins over the procedural drawings
# above: regeneration downscales it to the standard 32px instead of clobbering
# it with the drawn fallback.
SRC_DIR = os.path.join(os.path.dirname(OUT), 'assets', 'icon_src')
if os.path.isdir(SRC_DIR):
    n = 0
    for fn in sorted(os.listdir(SRC_DIR)):
        if fn.lower().endswith('.png'):
            im = Image.open(os.path.join(SRC_DIR, fn)).convert('RGBA')
            im.resize((SIZE, SIZE), Image.LANCZOS).save(os.path.join(OUT, fn))
            n += 1
    print(f'{n} hand-made overrides applied from assets/icon_src')
