#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
make_ogp.py --- ブログ「昭和44年男」のSNSカード画像（1200x630）を作る

使い方:
    python make_ogp.py showa-september-04
    python make_ogp.py showa-september-04 --force     # 既存を上書き
    python make_ogp.py --all                          # 画像が無い/縦長の記事を全部作る
    python make_ogp.py --all --strict                 # 1200x630でないものを全部作り直す

記事の front matter（title / description / categories）を読んで、
static/images/{slug}-ogp.jpg を生成します。

必要なもの:
    pip install pillow
    Windows標準フォント（游ゴシック）を使います。
"""

# Windowsのコマンドプロンプトでも日本語が化けないようにする
import io as _io
import sys as _sys
if _sys.platform == "win32":
    try:
        _sys.stdout = _io.TextIOWrapper(_sys.stdout.buffer, encoding="utf-8", errors="replace")
        _sys.stderr = _io.TextIOWrapper(_sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass


import argparse
import glob
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

# スクリプトの1つ上（リポジトリのルート）を基準にする
BLOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT_BOLD = "C:/Windows/Fonts/YuGothB.ttc"
FONT_REG = "C:/Windows/Fonts/YuGothR.ttc"

W, H = 1200, 630

# カテゴリ -> (背景色, アクセント色, 説明文の色)
PALETTE = {
    "昭和の今日は何があった日？": ((26, 36, 56), (214, 178, 110), (198, 206, 220)),
    "お金と暮らし":               ((22, 48, 38), (206, 186, 120), (196, 212, 200)),
    "走って・ぶら下がって・考えた": ((30, 44, 52), (198, 190, 140), (192, 204, 210)),
    "昭和の記憶":                 ((44, 34, 32), (216, 184, 126), (212, 202, 196)),
}
DEFAULT = ((34, 32, 36), (210, 182, 124), (204, 202, 208))


def font(path, size):
    return ImageFont.truetype(path, size)


def read_front_matter(path):
    """YAML(---) と TOML(+++) の両方に対応して title/description/categories を取り出す"""
    raw = open(path, encoding="utf-8", errors="replace").read()
    head = raw[:3000]

    def get(key):
        m = re.search(r"^%s\s*[:=]\s*['\"](.+?)['\"]\s*$" % key, head, re.M)
        return m.group(1) if m else ""

    m = re.search(r"^categories\s*[:=]\s*\[?\s*['\"]([^'\"\]]+)", head, re.M)
    return get("title"), get("description"), (m.group(1) if m else "")


def clean_title(t):
    """表示用にタイトルから連載名や日付の接頭辞を落とす"""
    t = re.sub(r"^【昭和の今日は何があった日？】\s*", "", t)
    t = re.sub(r"｜昭和の今日は何があった日？.*$", "", t)
    t = re.sub(r"^昭和の今日は何があった日？\s*[～~](.+?)[～~]\s*", "", t)
    t = re.sub(r"^\d{1,2}月\d{1,2}日\s*[─―—–\-]{1,2}\s*", "", t)
    t = re.sub(r"^昭和\d+年\d{1,2}月\d{1,2}日\s*[─―—–\-]{1,2}\s*", "", t)
    return t.strip()


def date_label(title):
    m = re.search(r"(\d{1,2})月(\d{1,2})日", title)
    return "%d月%d日" % (int(m.group(1)), int(m.group(2))) if m else ""


def wrap(draw, text, fnt, max_width):
    """日本語向け：1文字ずつ幅を測って折り返す"""
    lines, cur = [], ""
    for ch in text:
        if draw.textlength(cur + ch, font=fnt) > max_width and cur:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines


def build(slug, title, desc, category, out_path):
    bg, accent, sub = PALETTE.get(category, DEFAULT)
    im = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(im)

    # 左端の帯
    d.rectangle([0, 0, 14, H], fill=accent)

    # 上のラベル
    ds = date_label(title)
    if category == "昭和の今日は何があった日？" and ds:
        kicker = "【昭和の今日は何があった日？】%s" % ds
    else:
        kicker = category or "昭和44年男"
    d.text((60, 76), kicker, font=font(FONT_REG, 26), fill=accent)

    # タイトル（3行に収まるまでサイズを落とす）
    disp = clean_title(title)
    size = 56
    lines = wrap(d, disp, font(FONT_BOLD, size), 1050)
    while len(lines) > 3 and size > 38:
        size -= 4
        lines = wrap(d, disp, font(FONT_BOLD, size), 1050)
    lines = lines[:3]

    y = 132
    for line in lines:
        d.text((60, y), line, font=font(FONT_BOLD, size), fill=(252, 250, 248))
        y += size + 22

    # 横線
    divider_y = max(y + 26, 340)
    d.line([(60, divider_y), (860, divider_y)],
           fill=tuple(int(c * 0.55 + 60) for c in bg), width=1)

    # 説明文（2行まで、切れたら…）
    all_lines = wrap(d, desc, font(FONT_REG, 25), 1040)
    dl = all_lines[:2]
    if len(all_lines) > 2 and dl:
        dl[-1] = dl[-1][:-1] + "…"
    yy = divider_y + 40
    for line in dl:
        d.text((60, yy), line, font=font(FONT_REG, 25), fill=sub)
        yy += 40

    # フッター
    d.text((60, H - 74), "昭和44年男 showa44man.com",
           font=font(FONT_REG, 26), fill=tuple(int(c * 0.6 + 90) for c in sub))

    im.save(out_path, quality=92)
    return out_path


def needs_ogp(post_path, strict=False):
    """images が無い/縦長なら True。strict なら 1200x630 でないもの全部 True"""
    head = open(post_path, encoding="utf-8", errors="replace").read()[:3000]
    m = re.search(r"^images\s*[:=]\s*\[?\s*['\"]([^'\"\]]+)", head, re.M)
    if not m:
        return True
    p = os.path.join(BLOG, "static") + m.group(1).strip().replace("/", os.sep)
    if not os.path.exists(p):
        return True
    w, h = Image.open(p).size
    if strict:
        return (w, h) != (1200, 630)
    return (w / h) < 1.4


def set_images_field(post_path, image_url):
    raw = open(post_path, encoding="utf-8").read()
    toml = raw.lstrip().startswith("+++")
    delim = "+++" if toml else "---"
    first = raw.index(delim)
    second = raw.index("\n" + delim, first + 3)
    head, rest = raw[first + 3:second], raw[second:]
    newline = ('images = ["%s"]' if toml else 'images: ["%s"]') % image_url
    if re.search(r"^images\s*[:=]", head, re.M):
        head = re.sub(r"^images\s*[:=].*$", newline, head, count=1, flags=re.M)
    else:
        head = head.rstrip("\n") + "\n" + newline + "\n"
    open(post_path, "w", encoding="utf-8").write(raw[:first + 3] + head + rest)


def process(slug, force=False, quiet=False):
    post = os.path.join(BLOG, "content", "posts", slug + ".md")
    if not os.path.exists(post):
        print("記事が見つかりません: %s" % post)
        return False
    # すでに 1200x630 のカード画像が指定されていれば触らない
    if not force and not needs_ogp(post, strict=True):
        if not quiet:
            print("すでに1200x630のカード画像があります（--force で作り直し）: %s" % slug)
        return True
    out = os.path.join(BLOG, "static", "images", slug + "-ogp.jpg")
    if os.path.exists(out) and not force:
        if not quiet:
            print("既にあります（--force で上書き）: %s" % out)
        return True
    title, desc, cat = read_front_matter(post)
    if not title:
        print("titleが読めません: %s" % slug)
        return False
    build(slug, title, desc, cat, out)
    set_images_field(post, "/images/%s-ogp.jpg" % slug)
    print("作成: %s" % out)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?", help="記事のファイル名（.md なし）")
    ap.add_argument("--all", action="store_true", help="OGPが無い/縦長の記事を全部作る")
    ap.add_argument("--strict", action="store_true",
                    help="--all と併用。1200x630 でないものを全部作り直す")
    ap.add_argument("--force", action="store_true", help="既存を上書きする")
    args = ap.parse_args()

    if args.all:
        made = 0
        for p in sorted(glob.glob(os.path.join(BLOG, "content", "posts", "*.md"))):
            slug = os.path.basename(p)[:-3]
            if needs_ogp(p, strict=args.strict):
                if process(slug, force=True, quiet=True):
                    made += 1
        print("\n%d本にSNSカード画像を作りました。" % made)
        return

    if not args.slug:
        ap.print_help()
        sys.exit(1)
    process(args.slug, force=args.force)


if __name__ == "__main__":
    main()
