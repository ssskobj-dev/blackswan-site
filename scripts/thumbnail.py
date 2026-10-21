"""
記事の見出し画像（1280×670）を作る。

    python scripts/thumbnail.py note/<folder>

article.md の1行目の題名を読み、thumbnail.png を同じフォルダに書く。
"""
import sys
import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 670
BG = (17, 24, 39)          # 濃紺
ACCENT = (250, 204, 21)    # 黄
FG = (255, 255, 255)
SUB = (203, 213, 225)
FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
]


def font(size: int):
    for f in FONT_CANDIDATES:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size, index=0)
            except OSError:
                continue
    return ImageFont.load_default()


def main() -> None:
    folder = Path(sys.argv[1])
    title = (folder / "article.md").read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
    main_title, _, sub = title.partition("｜")

    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 18, H], fill=ACCENT)

    lines = textwrap.wrap(main_title, width=14)[:3]
    size = 76 if len(lines) <= 2 else 64
    f = font(size)
    y = 150
    for ln in lines:
        d.text((80, y), ln, font=f, fill=FG)
        y += size + 18
    if sub:
        fs = font(38)
        for ln in textwrap.wrap(sub, width=26)[:2]:
            d.text((84, y + 10), ln, font=fs, fill=SUB)
            y += 50
    ff = font(30)
    d.text((80, H - 80), "BlackSwan ｜ クラファンのページ、送るだけで翌営業日に", font=ff, fill=ACCENT)
    out = folder / "thumbnail.png"
    img.save(out)
    print(out)


if __name__ == "__main__":
    main()
