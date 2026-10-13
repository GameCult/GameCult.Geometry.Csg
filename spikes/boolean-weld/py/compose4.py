"""Compose render sheets: <case>_<tag>.png files side by side per case, labelled, saved as JPEG.
Usage: compose4.py <render-dir> <out-dir> [prefix]"""
import sys, os
from PIL import Image, ImageDraw
rd, out = sys.argv[1], sys.argv[2]; pre = sys.argv[3] if len(sys.argv) > 3 else ''; os.makedirs(out, exist_ok=True)
rows = {}
for f in sorted(x for x in os.listdir(rd) if x.endswith('.png')):
    case, tag = f[:-4].rsplit('_', 1); rows.setdefault(case, []).append((tag, f))
for case, items in rows.items():
    ims = [Image.open(os.path.join(rd, f)).convert('RGB') for t, f in items]
    W = sum(i.width for i in ims); H = max(i.height for i in ims) + 28
    c = Image.new('RGB', (W, H), (255, 255, 255)); d = ImageDraw.Draw(c); x = 0
    for (t, f), im in zip(items, ims):
        c.paste(im, (x, 28)); d.text((x + 8, 6), f'{case}: {t}', fill=(0, 0, 0)); x += im.width
    c.save(os.path.join(out, pre + case + '.jpg'), quality=82); print(case, [t for t, f in items])
