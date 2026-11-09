# -*- coding: utf-8 -*-
"""绘制站点图标并导出多尺寸 favicon.ico。

样式：微信绿圆角底 + 白色电影场记板/播放键，与站点主题色一致。
用法: python tools/make_favicon.py
"""
import os

from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "assets", "favicon.ico")  # 母本，构建时复制到 site/

GREEN = (7, 193, 96, 255)        # 站点主题色 --accent
WHITE = (255, 255, 255, 255)
S = 512  # 画布尺寸，ico 导出时会缩到各档位


def rounded(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def draw_icon(size):
    s = size / S
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # 绿色圆角底
    m = int(16 * s)
    rounded(d, [m, m, size - m, size - m], int(100 * s), GREEN)

    # 场记板顶条（白底 + 斜条纹）
    bar_top, bar_bot = int(96 * s), int(180 * s)
    bar_l, bar_r = int(96 * s), int(416 * s)
    rounded(d, [bar_l, bar_top, bar_r, bar_bot], int(24 * s), WHITE)
    # 斜条纹（绿色，模拟场记板纹路）
    for i in range(4):
        x0 = bar_l + int(60 * s) + i * int(80 * s)
        d.polygon([
            (x0, bar_top), (x0 + int(40 * s), bar_top),
            (x0 + int(8 * s), bar_bot), (x0 - int(32 * s), bar_bot),
        ], fill=GREEN)
    # 条纹裁回圆角条内
    mask = Image.new("L", (size, size), 0)
    md = ImageDraw.Draw(mask)
    md.rounded_rectangle([bar_l, bar_top, bar_r, bar_bot], radius=int(24 * s), fill=255)
    stripe = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    sd = ImageDraw.Draw(stripe)
    for i in range(4):
        x0 = bar_l + int(60 * s) + i * int(80 * s)
        sd.polygon([
            (x0, bar_top), (x0 + int(40 * s), bar_top),
            (x0 + int(8 * s), bar_bot), (x0 - int(32 * s), bar_bot),
        ], fill=GREEN)
    img.paste(stripe, (0, 0), mask)

    # 白色播放三角形（场记板身）
    body_top, body_bot = int(212 * s), int(416 * s)
    tri = [
        (int(150 * s), body_top),
        (int(150 * s), body_bot),
        (int(372 * s), (body_top + body_bot) // 2),
    ]
    d.polygon(tri, fill=WHITE)
    return img


def main():
    base = draw_icon(S)
    base.save(os.path.join(ROOT, "assets", "favicon-512.png"))
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    base.save(OUT, format="ICO", sizes=sizes)
    print(f"生成 {os.path.relpath(OUT, ROOT)}  sizes={sizes}")


if __name__ == "__main__":
    main()
