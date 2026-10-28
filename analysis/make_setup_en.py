# -*- coding: utf-8 -*-
"""English schematic and annotated setup photo."""

import os
import math
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "bubble")


def schematic():
    fig, ax = plt.subplots(figsize=(12.5, 5.0))
    ax.set_xlim(0, 13)
    ax.set_ylim(0, 5)
    ax.axis("off")

    def box(x, y, w, h, text, fc="#e8f1fb", ec="#4a7fb5", fs=8.5):
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                    fc=fc, ec=ec, lw=1.0))
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs)

    def arrow(x1, y1, x2, y2, text="", color="#222222", fs=8):
        ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                    arrowprops=dict(arrowstyle="-|>", lw=1.2, color=color))
        if text:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.12, text, ha="center", va="bottom",
                    fontsize=fs, color=color)

    box(0.2, 2.15, 1.8, 1.0, "Stepper motor\n+ lead screw", fc="#f0f0f0", ec="#777777", fs=8)
    box(2.4, 2.05, 1.9, 1.2, "Input syringe\n10 mL", fc="#dfeefc", ec="#3d78b0")
    box(4.7, 2.25, 1.7, 0.8, "Silicone tube", fc="#eef7e7", ec="#6a9b4d", fs=8)
    box(6.8, 2.05, 1.9, 1.2, "Output syringe\n20 mL", fc="#dfeefc", ec="#3d78b0")
    box(9.1, 2.15, 1.5, 1.0, "Extension\nspring", fc="#fff2cc", ec="#b38f00", fs=8)
    box(10.9, 1.9, 0.5, 1.5, "Fixed\nend", fc="#f0f0f0", ec="#777777", fs=8)

    arrow(2.0, 2.65, 2.4, 2.65, "push")
    arrow(4.3, 2.65, 4.7, 2.65, "p")
    arrow(6.4, 2.65, 6.8, 2.65, "push")
    arrow(8.7, 2.65, 9.1, 2.65)
    arrow(10.6, 2.65, 10.9, 2.65)

    box(3.8, 0.35, 4.9, 0.75,
        "Water load (0.3 / 0.55 / 0.85 kg)\nStatic: 0.2 mm scale / caliper",
        fc="#fdf2f0", ec="#b55a4a", fs=7.5)
    ax.plot([8.05, 8.05], [1.1, 2.05], color="#b55a4a", lw=1.2, ls="--")
    ax.annotate("", xy=(8.05, 2.05), xytext=(8.05, 1.6),
                arrowprops=dict(arrowstyle="-|>", lw=1.2, color="#b55a4a"))
    ax.text(8.15, 1.55, "known force", color="#b55a4a", fontsize=7.5)

    box(7.9, 3.55, 2.7, 0.75, "Phone 240 fps\noutput displacement + scale",
        fc="#f3e8fb", ec="#7a4a9b", fs=7.5)
    ax.annotate("", xy=(8.7, 3.25), xytext=(8.7, 3.55),
                arrowprops=dict(arrowstyle="-|>", lw=1.2, color="#7a4a9b"))

    box(0.3, 0.35, 2.9, 0.75, "Arduino Mega2560\nTB6600 / 12 V", fc="#f0f0f0", ec="#777777", fs=7.5)
    ax.annotate("", xy=(1.1, 2.15), xytext=(1.1, 1.1),
                arrowprops=dict(arrowstyle="-|>", lw=1.0, color="#777777"))

    ax.text(6.5, 4.75, "Schematic of the syringe hydraulic bubble-compliance setup",
            ha="center", va="center", fontsize=12)
    ax.text(0.25, 4.05,
            "Exp. 1: remove spring, lock input, hang water, measure static K_air\n"
            "Exp. 2: install spring, release input, step + video, measure tau\n"
            "Exp. 3: install spring, lock input, hang water, measure K_eff",
            ha="left", va="top", fontsize=8, linespacing=1.55,
            bbox=dict(boxstyle="round,pad=0.35", fc="#fafafa", ec="#cccccc"))

    fig.tight_layout()
    fig.savefig(os.path.join(DATA, "setup_schematic_en.png"), dpi=220, facecolor="white")
    plt.close(fig)


def annotate_photo():
    src = os.path.join(DATA, "setup_photo_clean.jpg")
    dst = os.path.join(DATA, "setup_photo_en.jpg")
    im = Image.open(src).convert("RGB")
    draw = ImageDraw.Draw(im)
    font_path = r"C:\Windows\Fonts\arialbd.ttf"
    if not os.path.exists(font_path):
        font_path = r"C:\Windows\Fonts\arial.ttf"
    font = ImageFont.truetype(font_path, 22)
    labels = [
        ("Output syringe", (300, 25), (420, 150)),
        ("Extension spring", (20, 250), (180, 180)),
        ("Input syringe / lead screw", (790, 25), (1010, 150)),
        ("Phone stand / 240 fps", (720, 420), (610, 340)),
        ("0.2 mm scale", (300, 500), (430, 380)),
    ]

    def arrow(a, b, color=(176, 0, 32), width=3, head=10):
        draw.line([a, b], fill=color, width=width)
        ang = math.atan2(b[1] - a[1], b[0] - a[0])
        p1 = (b[0] - head * math.cos(ang - 0.42), b[1] - head * math.sin(ang - 0.42))
        p2 = (b[0] - head * math.cos(ang + 0.42), b[1] - head * math.sin(ang + 0.42))
        draw.polygon([b, p1, p2], fill=color)

    for text, (bx, by), (tx, ty) in labels:
        bb = draw.textbbox((0, 0), text, font=font)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        pad_x, pad_y = 7, 4
        bw, bh = tw + 2 * pad_x, th + 2 * pad_y
        arrow((bx + bw // 2, by + bh // 2), (tx, ty))
    for text, (bx, by), (tx, ty) in labels:
        bb = draw.textbbox((0, 0), text, font=font)
        tw, th = bb[2] - bb[0], bb[3] - bb[1]
        pad_x, pad_y = 7, 4
        bw, bh = tw + 2 * pad_x, th + 2 * pad_y
        draw.rounded_rectangle([bx, by, bx + bw, by + bh], radius=5,
                               fill=(255, 255, 255), outline=(70, 70, 70), width=1)
        draw.text((bx + pad_x - bb[0], by + pad_y - bb[1]), text, font=font, fill=(0, 0, 0))
    im.save(dst, quality=94, optimize=True)


if __name__ == "__main__":
    schematic()
    annotate_photo()
    print("English setup figures written to", DATA)
