"""
記事用の図を作る（サイトと同じ黒×ライムの配色）。

    python scripts/figures.py note/<folder>

note/<folder>/figures.yaml を読み、fig-1.png, fig-2.png … と thumbnail.png を書く。

figures.yaml の例:
  thumbnail:
    title: Makuake 毎月出品を回す段取り
    sub: ページ制作を「量産型」にする方法
  figures:
    - type: lp_sample          # 縦長LPのサンプル（スライド1枚＝1セクション）
      title: 11セクションの型
      sections: [表紙, 課題, 解決, 特徴, 使い方, 仕様, ストーリー, リターン, 流れ, 注意, FAQ]
    - type: compare            # 2列の比較
      title: 外注と月額制の違い
      left:  {head: 単発の外注, rows: ["約10万円/本", "納期2週間〜1か月", "毎回ゼロから説明"]}
      right: {head: BlackSwan, rows: ["月額7,980円で6件", "翌営業日に初稿", "型を共有して差し替え"]}
  ※ 金額のようにカンマを含む文は "..." で囲む（YAMLの区切りと混ざるため）
    - type: steps              # 番号付きの手順
      title: 毎月回す段取り
      steps: [商品と価格を決める, 写真を撮る, 型に当てはめる, 画像を書き出す, 申請する]
    - type: calendar           # 4週間の配分
      title: 1か月のカレンダー
      weeks: [商品決定・撮影, ページ制作, 申請・審査対応, 公開・告知]
"""
import sys
import textwrap
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
BG = (18, 18, 20)
PANEL = (32, 33, 38)
LIME = (200, 255, 60)
FG = (255, 255, 255)
SUB = (190, 195, 205)
FONTS = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
]


def font(size: int):
    for f in FONTS:
        if Path(f).exists():
            try:
                return ImageFont.truetype(f, size, index=0)
            except OSError:
                pass
    return ImageFont.load_default()


def canvas(title: str):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 14, H], fill=LIME)
    d.text((60, 36), title, font=font(40), fill=FG)
    d.text((60, H - 48), "BlackSwan ｜ クラファンのページ、送るだけで翌営業日に", font=font(22), fill=LIME)
    return img, d


def fig_lp_sample(spec):
    img, d = canvas(spec.get("title", "縦長LPの型"))
    secs = spec.get("sections", [])
    # 縦長のスマホ風フレームに、セクションを積む
    x0, y0, w = 90, 110, 300
    h = H - 110 - 90
    d.rounded_rectangle([x0, y0, x0 + w, y0 + h], radius=28, fill=PANEL, outline=(70, 72, 80), width=3)
    n = max(len(secs), 1)
    sh = (h - 30) / n
    f = font(int(min(26, sh * 0.6)))
    for i, s in enumerate(secs):
        y = y0 + 15 + i * sh
        col = LIME if i == 0 else (52, 54, 62)
        d.rounded_rectangle([x0 + 16, y + 3, x0 + w - 16, y + sh - 3], radius=8, fill=col)
        d.text((x0 + 30, y + (sh - f.size) / 2), f"{i+1:02d}  {s}", font=f, fill=(BG if i == 0 else FG))
    # 右側: 説明
    fx = x0 + w + 80
    d.text((fx, 130), "スライド1枚 ＝ 1セクション", font=font(44), fill=LIME)
    lines = spec.get("notes", [
        "上から順に読者の疑問に答える並び",
        "1枚に伝えることは1つ、文字は大きめ",
        "翌月は文字と写真を差し替えるだけ",
        "PNGで書き出して本文に順に置く",
    ])
    y = 220
    for ln in lines:
        d.ellipse([fx, y + 14, fx + 14, y + 28], fill=LIME)
        d.text((fx + 32, y), ln, font=font(30), fill=FG)
        y += 64
    return img


def fig_compare(spec):
    img, d = canvas(spec.get("title", "比較"))
    cols = [spec.get("left", {}), spec.get("right", {})]
    cw = (W - 60 * 2 - 40) // 2
    for i, c in enumerate(cols):
        x = 60 + i * (cw + 40)
        hl = i == 1
        d.rounded_rectangle([x, 110, x + cw, H - 90], radius=20, fill=PANEL, outline=(LIME if hl else (70, 72, 80)), width=4)
        d.text((x + 30, 135), c.get("head", ""), font=font(38), fill=(LIME if hl else FG))
        y = 215
        for r in c.get("rows", []):
            for ln in textwrap.wrap(str(r), width=18)[:2]:
                d.text((x + 34, y), ("✓ " if hl else "・ ") + ln, font=font(30), fill=FG)
                y += 48
            y += 14
    return img


def fig_steps(spec):
    img, d = canvas(spec.get("title", "手順"))
    steps = spec.get("steps", [])
    n = max(len(steps), 1)
    y = 140
    gap = min(100, (H - 240) // n)
    for i, s in enumerate(steps):
        d.ellipse([70, y, 70 + 64, y + 64], fill=LIME)
        d.text((70 + 32 - 11, y + 12), str(i + 1), font=font(34), fill=BG)
        d.text((160, y + 12), str(s), font=font(34), fill=FG)
        if i < n - 1:
            d.line([102, y + 64, 102, y + gap], fill=(80, 82, 90), width=4)
        y += gap
    return img


def fig_calendar(spec):
    img, d = canvas(spec.get("title", "1か月の配分"))
    weeks = spec.get("weeks", [])
    cw = (W - 120 - 30 * 3) // 4
    for i in range(4):
        x = 60 + i * (cw + 30)
        d.rounded_rectangle([x, 130, x + cw, H - 100], radius=18, fill=PANEL)
        d.text((x + 22, 150), f"第{i+1}週", font=font(30), fill=LIME)
        txt = weeks[i] if i < len(weeks) else ""
        y = 215
        for ln in textwrap.wrap(str(txt), width=8)[:6]:
            d.text((x + 22, y), ln, font=font(28), fill=FG)
            y += 46
    return img


def thumbnail(spec, out: Path):
    img = Image.new("RGB", (1280, 670), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 18, 670], fill=LIME)
    title = spec.get("title", "")
    sub = spec.get("sub", "")
    lines = textwrap.wrap(title, width=14)[:3]
    size = 76 if len(lines) <= 2 else 64
    y = 150
    for ln in lines:
        d.text((80, y), ln, font=font(size), fill=FG)
        y += size + 18
    if sub:
        for ln in textwrap.wrap(sub, width=26)[:2]:
            d.text((84, y + 10), ln, font=font(38), fill=SUB)
            y += 50
    d.text((80, 590), "BlackSwan ｜ クラファンのページ、送るだけで翌営業日に", font=font(30), fill=LIME)
    img.save(out)


RENDER = {"lp_sample": fig_lp_sample, "compare": fig_compare, "steps": fig_steps, "calendar": fig_calendar}


def main() -> None:
    folder = Path(sys.argv[1])
    spec = yaml.safe_load((folder / "figures.yaml").read_text(encoding="utf-8")) or {}
    if "thumbnail" in spec:
        thumbnail(spec["thumbnail"], folder / "thumbnail.png")
        print(folder / "thumbnail.png")
    for i, fs in enumerate(spec.get("figures", []), 1):
        fn = RENDER.get(fs.get("type"))
        if not fn:
            print(f"unknown type: {fs.get('type')}", file=sys.stderr)
            continue
        out = folder / f"fig-{i}.png"
        fn(fs).save(out)
        print(out)


if __name__ == "__main__":
    main()
