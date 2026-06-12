"""Generate professional-looking brand wordmark PNGs for PulseDeck's System tab.

Each is a flat, modern wordmark — solid brand color block with white text, or
white block with brand-colored text — no childish rounded rect / gradient.
Designed to identify the user's actual hardware (nominative use).
"""
import os
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), 'icons', 'brands')
os.makedirs(OUT, exist_ok=True)

# Target a 2x retina-style render; the runtime scales down to ~32px tall
W, H = 200, 64

def _font(family, size):
    """Try increasingly common Windows fonts that approximate the brand style."""
    if family == 'black':
        candidates = ['ariblk.ttf', 'arialbd.ttf', 'segoeuib.ttf']
    elif family == 'cond':
        candidates = ['arialnb.ttf', 'arialn.ttf', 'arialbd.ttf', 'segoeuib.ttf']
    elif family == 'light':
        candidates = ['ariali.ttf', 'arial.ttf', 'segoeui.ttf']
    elif family == 'med':
        candidates = ['segoeuib.ttf', 'arialbd.ttf']
    else:
        candidates = ['arial.ttf', 'segoeui.ttf']
    for n in candidates:
        p = os.path.join(r'C:\Windows\Fonts', n)
        if os.path.exists(p):
            try: return ImageFont.truetype(p, size)
            except Exception: pass
    return ImageFont.load_default()

def make(key, label, bg, fg, family='black', size=36, tracking=2, padding_x=14):
    """Flat wordmark: solid bg rectangle (or transparent) + centered label."""
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = _font(family, size)

    # measure each character to apply uniform tracking
    widths = [d.textbbox((0, 0), ch, font=f)[2] for ch in label]
    total_w = sum(widths) + tracking * max(0, len(label) - 1)
    ref_bb = d.textbbox((0, 0), 'Hg', font=f)
    text_h = ref_bb[3] - ref_bb[1]

    # solid block when bg is not transparent
    if bg.lower() not in ('transparent', 'none', ''):
        block_w = min(W, total_w + padding_x * 2)
        block_h = min(H, text_h + 20)
        x0 = (W - block_w) // 2
        y0 = (H - block_h) // 2
        d.rectangle((x0, y0, x0 + block_w, y0 + block_h), fill=bg)

    # text placement (centered)
    x = (W - total_w) // 2
    y = (H - text_h) // 2 - ref_bb[1]
    for ch, cw in zip(label, widths):
        d.text((x, y), ch, fill=fg, font=f)
        x += cw + tracking

    img.save(os.path.join(OUT, key + '.png'))

print('Generating brand wordmarks...')

# Flat, minimalist wordmarks. Brand colors used as identifying accents.
# These are stylized inspired-by marks for hardware identification, not the
# trademarked logo files themselves.
LOGOS = [
    # CPUs / GPUs
    ('amd',       'AMD',       '#000000', '#ffffff', 'black', 40, 4),
    ('nvidia',    'NVIDIA',    '#76b900', '#ffffff', 'black', 30, 3),
    ('intel',     'intel',     '#0071c5', '#ffffff', 'light', 38, 0),
    # Motherboard / OEM
    ('asus',      'ASUS',      '#000000', '#ffffff', 'black', 36, 6),
    ('msi',       'MSI',       '#0a0a0a', '#ff0000', 'black', 42, 4),
    ('gigabyte',  'GIGABYTE',  '#000000', '#ff6600', 'cond',  22, 2),
    ('asrock',    'ASRock',    '#1a1a1a', '#ffffff', 'black', 30, 0),
    ('dell',      'DELL',      '#007db8', '#ffffff', 'black', 36, 6),
    ('hp',        'hp',        '#0096d6', '#ffffff', 'black', 46, 0),
    ('lenovo',    'Lenovo',    '#e2231a', '#ffffff', 'black', 32, 0),
    ('acer',      'acer',      '#ffffff', '#83b81a', 'black', 36, 0),
    # Monitors
    ('samsung',   'SAMSUNG',   '#1428a0', '#ffffff', 'cond',  26, 3),
    ('lg',        'LG',        '#ffffff', '#a50034', 'black', 46, 4),
    ('benq',      'BenQ',      '#80278d', '#ffffff', 'black', 34, 0),
    ('aoc',       'AOC',       '#e60012', '#ffffff', 'black', 38, 4),
    ('philips',   'PHILIPS',   '#0a4ea2', '#ffffff', 'cond',  26, 3),
    ('viewsonic', 'ViewSonic', '#e30613', '#ffffff', 'black', 26, 0),
    ('iiyama',    'iiyama',    '#003366', '#ffffff', 'black', 30, 0),
    ('xmi',       'Xiaomi',    '#ff6700', '#ffffff', 'black', 28, 0),
    # RAM
    ('corsair',   'CORSAIR',   '#000000', '#ffd23f', 'cond',  26, 3),
    ('kingston',  'Kingston',  '#e2231a', '#ffffff', 'black', 26, 0),
    ('gskill',    'G.SKILL',   '#0a0a0a', '#e2231a', 'black', 24, 2),
    ('crucial',   'Crucial',   '#005baa', '#ffffff', 'black', 30, 0),
    # Storage
    ('wd',        'WD',        '#000000', '#ffffff', 'black', 46, 4),
    ('seagate',   'SEAGATE',   '#0a0a0a', '#7fb800', 'cond',  26, 4),
    ('sandisk',   'SanDisk',   '#ed1c24', '#ffffff', 'black', 28, 0),
    ('kioxia',    'KIOXIA',    '#1a1a1a', '#ffffff', 'black', 30, 4),
    # Audio
    ('realtek',   'Realtek',   '#a31621', '#ffffff', 'black', 30, 0),
    ('creative',  'Creative',  '#e2231a', '#ffffff', 'black', 28, 0),
    ('logitech',  'Logitech',  '#00b8fc', '#ffffff', 'black', 28, 0),
]

for args in LOGOS:
    make(*args)
    print(' ', args[0] + '.png')

print(f'\nDone. {len(LOGOS)} wordmarks generated at {W}x{H} -> scaled to 32px tall at runtime.')
