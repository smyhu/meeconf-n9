# MeeConf icon: "@" (after the native Mail icon) in our style - light green
# pictogram with glow on the dark N9 background with the arc gloss.
# Variants: a = @ only, b = @ + small gear (configuration), c = @ + stack of
# three lines (bulk / list). Usage: python3 icon.py background80.png outdir
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import sys, os, math
K = 8
W = 80 * K
LIGHT = (231, 255, 205)
GLOW = (120, 170, 100)
STROKE = (30, 30, 32)
FONT = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
base = Image.open(sys.argv[1]).convert('RGBA')
out_dir = sys.argv[2]

def at_mask(size, pos):
    m = Image.new('L', (W, W), 0)
    ImageDraw.Draw(m).text(pos, '@', font=ImageFont.truetype(FONT, size), fill=255, anchor='mm')
    return m

def gear_mask(cx, cy, r, teeth=8):
    m = Image.new('L', (W, W), 0)
    d = ImageDraw.Draw(m)
    pts = []
    for i in range(teeth * 4):
        a = 2 * math.pi * i / (teeth * 4)
        rr = r if (i % 4) in (0, 1) else r * 0.74
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=255)
    d.ellipse([cx - r * 0.30, cy - r * 0.30, cx + r * 0.30, cy + r * 0.30], fill=0)
    return m

def lines_mask(x, y, w, h, n=3):
    m = Image.new('L', (W, W), 0)
    d = ImageDraw.Draw(m)
    gap = h / (n * 2 - 1)
    for i in range(n):
        d.rounded_rectangle([x, y + i * 2 * gap, x + w, y + i * 2 * gap + gap], radius=gap / 2, fill=255)
    return m

def paint(img, mask):
    glow = mask.filter(ImageFilter.GaussianBlur(K * 1.6)).point(lambda v: int(v * 0.55))
    img = Image.composite(Image.new('RGBA', (W, W), GLOW + (255,)), img, glow)
    return Image.composite(Image.new('RGBA', (W, W), LIGHT + (255,)), img, mask)

def badge(img, mask):
    edge = mask.filter(ImageFilter.MaxFilter(2 * K + 1))
    img = Image.composite(Image.new('RGBA', (W, W), STROKE + (255,)), img, edge)
    return Image.composite(Image.new('RGBA', (W, W), LIGHT + (255,)), img, mask)

def make(variant):
    img = base.resize((W, W), Image.BICUBIC)
    alpha = img.split()[3]
    if variant == 'a':
        img = paint(img, at_mask(int(W * 0.78), (W * 0.5, W * 0.53)))
    elif variant == 'b':
        img = paint(img, at_mask(int(W * 0.70), (W * 0.45, W * 0.48)))
        img = badge(img, gear_mask(W * 0.75, W * 0.75, W * 0.17))
    else:
        img = paint(img, at_mask(int(W * 0.70), (W * 0.45, W * 0.48)))
        m = lines_mask(W * 0.60, W * 0.62, W * 0.27, W * 0.22)
        img = badge(img, m)
    img.putalpha(alpha)
    return img.resize((80, 80), Image.LANCZOS)

icons = {}
for v in 'abc':
    icons[v] = make(v)
    icons[v].save(os.path.join(out_dir, 'meeconf-n9-%s.png' % v))
icons['a'].save(os.path.join(out_dir, 'meeconf-n9.png'))
sheet = Image.new('RGBA', (3 * 200 + 20, 300), (0, 0, 0, 255))
d = ImageDraw.Draw(sheet)
for i, v in enumerate('abc'):
    sheet.alpha_composite(icons[v].resize((180, 180), Image.LANCZOS), (20 + i * 200, 20))
    sheet.alpha_composite(icons[v], (70 + i * 200, 210))
    d.text((20 + i * 200, 280), v.upper(), fill=(200, 200, 200))
sheet.save(os.path.join(out_dir, 'icon-variants.png'))
