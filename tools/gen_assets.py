# -*- coding: utf-8 -*-
"""Generate the site's PNG icons (apple-touch-icon + 512px icon).

The fabric illustrations this script used to generate are gone: the site now uses the
factory's real photos plus CC0 fabric photography (see website/CREDITS.md). Only the
brand icons are still generated here.
"""
import os

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "lichen_knitting_website", "assets", "img")
BLUE = "#1456a0"


def make_icon(size, path, radius_ratio=0.22):
    scale = 4
    s = size * scale
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([0, 0, s - 1, s - 1], radius=int(s * radius_ratio), fill=BLUE)

    font = None
    for cand in (
        r"C:\Windows\Fonts\msyhbd.ttc",
        r"C:\Windows\Fonts\msyh.ttc",
        r"C:\Windows\Fonts\simhei.ttf",
        r"C:\Windows\Fonts\Dengb.ttf",
    ):
        if os.path.exists(cand):
            try:
                font = ImageFont.truetype(cand, int(s * 0.62))
                break
            except Exception:
                font = None

    if font is not None:
        text = "利"
        box = d.textbbox((0, 0), text, font=font)
        w, h = box[2] - box[0], box[3] - box[1]
        d.text(((s - w) / 2 - box[0], (s - h) / 2 - box[1]), text, font=font, fill="white")
    else:
        d.rectangle([int(s * .28), int(s * .28), int(s * .72), int(s * .34)], fill="white")
        d.rectangle([int(s * .28), int(s * .44), int(s * .72), int(s * .50)], fill="white")
        d.rectangle([int(s * .28), int(s * .60), int(s * .58), int(s * .66)], fill="white")

    img.resize((size, size), Image.LANCZOS).save(path, "PNG", optimize=True)
    print("wrote", os.path.basename(path), size, "px")


def main():
    os.makedirs(OUT, exist_ok=True)
    make_icon(180, os.path.join(OUT, "apple-touch-icon.png"))
    make_icon(512, os.path.join(OUT, "icon-512.png"), radius_ratio=0.18)


if __name__ == "__main__":
    main()