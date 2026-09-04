# Generates the app icon set (icon-192/512.png, apple-touch-icon.png,
# favicon.png) -- a full-bleed pastel pink book with a small jellycat-style
# face, using the same pink tokens as the page's own CSS.
#
# Run from the repo root: `python scripts/gen_icon.py`
# Requires: pip install pillow numpy
#
# To tweak: change the PINK/PINK_STRONG/PINK_INK/PAPER constants (keep them
# in sync with the --pink/--pink-strong/--pink-ink tokens in index.html if
# the page's palette ever changes), or the face/ribbon/page-edge geometry
# in build(). Re-run and re-commit the four output PNGs -- filenames are
# fixed, so manifest.json and the <link> tags in index.html need no changes.

import numpy as np
from PIL import Image, ImageDraw

SIZE = 1024  # supersample; downscaled afterwards for smooth edges

def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))

# exact tokens pulled from the app's own CSS palette
PINK = hex2rgb('#fbe1e7')        # --pink, the soft blush used all over the page
PINK_STRONG = hex2rgb('#eeb4c2') # --pink-strong, card borders/accents
PINK_INK = hex2rgb('#9c4d63')    # --pink-ink, the ink-on-pink text color
PAPER = hex2rgb('#fff6f2')       # warm cream, close to --bg/--surface

def build():
    img = Image.new('RGBA', (SIZE, SIZE), (*PINK, 255))
    draw = ImageDraw.Draw(img)

    # spine strip on the left (the book's binding edge)
    spine_w = SIZE * 0.075
    draw.rectangle([0, 0, spine_w, SIZE], fill=PINK_STRONG)

    # page-edge sliver peeking out on the right (the book's open edge)
    pg_l, pg_r = SIZE * 0.905, SIZE * 0.97
    pg_t, pg_b = SIZE * 0.05, SIZE * 0.95
    draw.rounded_rectangle([pg_l, pg_t, pg_r, pg_b], radius=SIZE * 0.02, fill=PAPER)
    for i in range(1, 3):
        lx = pg_l + SIZE * (0.018 * i)
        draw.line([(lx, pg_t + 10), (lx, pg_b - 10)], fill=(0, 0, 0, 16), width=2)

    # bookmark ribbon hanging from the top edge, swallow-tail notch at bottom
    rw = SIZE * 0.155
    r_left = SIZE * 0.40
    r_right = r_left + rw
    r_flat = SIZE * 0.285
    r_notch = r_flat - SIZE * 0.055
    draw.polygon([
        (r_left, 0), (r_right, 0),
        (r_right, r_flat), ((r_left + r_right) / 2, r_notch),
        (r_left, r_flat),
    ], fill=PAPER)

    # ---- jellycat-style face: simple bead eyes, a stitched smile, soft cheeks ----
    face_cx, face_cy = SIZE * 0.55, SIZE * 0.60
    eye_dx = SIZE * 0.085
    eye_w, eye_h = SIZE * 0.05, SIZE * 0.062
    eye_y = face_cy - SIZE * 0.05

    # soft cheek blushes, drawn on their own layer so they can be semi-transparent
    cheek_layer = Image.new('RGBA', (SIZE, SIZE), (0, 0, 0, 0))
    cd = ImageDraw.Draw(cheek_layer)
    cheek_r = SIZE * 0.032
    cheek_y = eye_y + SIZE * 0.05
    for dx in (-eye_dx - SIZE * 0.06, eye_dx + SIZE * 0.06):
        cx = face_cx + dx
        cd.ellipse([cx - cheek_r, cheek_y - cheek_r, cx + cheek_r, cheek_y + cheek_r],
                   fill=(PINK_STRONG[0], PINK_STRONG[1], PINK_STRONG[2], 150))
    img = Image.alpha_composite(img, cheek_layer)
    draw = ImageDraw.Draw(img)

    # eyes
    for dx in (-eye_dx, eye_dx):
        ex = face_cx + dx
        draw.ellipse([ex - eye_w / 2, eye_y - eye_h / 2, ex + eye_w / 2, eye_y + eye_h / 2], fill=PINK_INK)

    # smile -- bottom arc of an ellipse, drawn thick for a stitched-plush feel
    smile_w, smile_h = SIZE * 0.13, SIZE * 0.11
    smile_top = face_cy + SIZE * 0.005
    smile_box = [face_cx - smile_w / 2, smile_top, face_cx + smile_w / 2, smile_top + smile_h]
    draw.arc(smile_box, start=25, end=155, fill=PINK_INK, width=int(SIZE * 0.014))

    return img

def render(img, out_size, path):
    out = img.resize((out_size, out_size), Image.LANCZOS)
    out.save(path)
    print('wrote', path, out.size)

def with_squircle(img):
    mask = Image.new('L', (SIZE, SIZE), 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=int(SIZE * 0.22), fill=255)
    out = img.copy()
    out.putalpha(mask)
    return out

if __name__ == '__main__':
    import os
    OUT = os.path.join(os.path.dirname(__file__), '..') + os.sep

    master = build()
    render(master, 512, OUT + 'icon-512.png')
    render(master, 192, OUT + 'icon-192.png')
    render(master, 180, OUT + 'apple-touch-icon.png')
    render(with_squircle(master), 64, OUT + 'favicon.png')
