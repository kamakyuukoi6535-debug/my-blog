#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
check.py --- ブログ「昭和44年男」の全記事を健康診断する

使い方:
    python check.py

見るところ:
    - date が未来になっている記事（404の原因）
    - date と記事タイトルの日付がずれている記事
    - description が無い / 半角クォートが入っている / 長さが極端
    - SNSカード画像が無い / 1200x630 でない（Xでカードが出ない原因）
    - 正規セットにないタグ
    - リンク切れ（本文の画像・内部リンク）
    - 被リンクゼロの記事（孤児記事。SEO上よくない）
    - アフィリエイトのアソシエイトタグ漏れ
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


import collections
import glob
import os
import re
from datetime import datetime

# スクリプトの1つ上（リポジトリのルート）を基準にする
BLOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POSTS = os.path.join(BLOG, "content", "posts")
STATIC = os.path.join(BLOG, "static")

CANONICAL_TAGS = {
    "昭和", "昭和44年男", "昭和の暮らし", "葛飾", "テレビ", "スポーツ", "インデックス投資",
    "音楽", "学校と子ども時代", "プロ野球", "お金と僕の12年戦争", "高校野球", "資産形成",
    "家計管理", "駄菓子", "漫画", "書評", "リベ大", "おもちゃ・ゲーム", "鉄道", "宇宙",
    "大相撲", "不動産", "固定費削減", "映画", "特撮・ヒーロー", "オリンピック", "FX",
    "奨学金", "NISA",
}


def section(title):
    print("\n" + "─" * 62)
    print(" " + title)
    print("─" * 62)


def main():
    files = sorted(glob.glob(os.path.join(POSTS, "*.md")))
    now = datetime.now()

    future, mismatch, desc_ng, ogp_ng, tag_ng = [], [], [], [], []
    img_missing, link_missing, aff_ng = [], [], []
    inbound = collections.Counter()
    slugs = set()

    try:
        from PIL import Image
        have_pil = True
    except ImportError:
        have_pil = False
        print("[注意] Pillow が無いので画像サイズは確認できません（pip install pillow）")

    for f in files:
        slug = os.path.basename(f)[:-3]
        slugs.add(slug)
        raw = open(f, encoding="utf-8", errors="replace").read()
        head = raw[:3000]

        # date
        m = re.search(r"^date\s*[:=]\s*'?\"?(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", head, re.M)
        t = re.search(r"^title\s*[:=]\s*['\"](.+?)['\"]\s*$", head, re.M)
        if m:
            dt = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")
            if dt > now:
                future.append((slug, m.group(1)))
            if t:
                md = re.search(r"(\d{1,2})月(\d{1,2})日", t.group(1))
                if md and (dt.month, dt.day) != (int(md.group(1)), int(md.group(2))):
                    mismatch.append((slug, "%s月%s日" % md.groups(), "%d月%d日" % (dt.month, dt.day)))

        # description
        dm = re.search(r"^description\s*[:=]\s*(.+)$", head, re.M)
        if not dm:
            desc_ng.append((slug, "無し"))
        else:
            body = dm.group(1).strip()
            inner = body[1:-1] if len(body) > 1 and body[0] in "'\"" else body
            if '"' in inner:
                desc_ng.append((slug, "半角クォートあり（404の危険）"))
            elif len(inner) < 60:
                desc_ng.append((slug, "%d字と短い" % len(inner)))

        # OGP
        im = re.search(r"^images\s*[:=]\s*\[?\s*['\"]([^'\"\]]+)", head, re.M)
        if not im:
            ogp_ng.append((slug, "images が無い"))
        else:
            p = STATIC + im.group(1).replace("/", os.sep)
            if not os.path.exists(p):
                ogp_ng.append((slug, "ファイルが無い %s" % im.group(1)))
            elif have_pil:
                w, h = Image.open(p).size
                if (w, h) != (1200, 630):
                    ogp_ng.append((slug, "%dx%d（1200x630にする）" % (w, h)))

        # tags
        tm = re.search(r"^tags\s*[:=]\s*\[(.*?)\]", head, re.M | re.S)
        if tm:
            tags = [x.strip().strip("'\"") for x in tm.group(1).split(",") if x.strip()]
            bad = [x for x in tags if x not in CANONICAL_TAGS]
            if bad:
                tag_ng.append((slug, "、".join(bad)))

        # 本文の画像
        for path in re.findall(r"!\[[^\]]*\]\((/images/[^)]+)\)", raw):
            if not os.path.exists(STATIC + path.replace("/", os.sep)):
                img_missing.append((slug, path))

        # 内部リンク
        for path in re.findall(r"\]\((/posts/([a-z0-9\-]+)/)\)", raw):
            inbound[path[1]] += 1
            if not os.path.exists(os.path.join(POSTS, path[1] + ".md")):
                link_missing.append((slug, path[0]))

        # アフィリ
        for url in re.findall(r'url="(https://www\.amazon\.co\.jp/dp/[^"]+)"', raw):
            if "tag=showa44man22-22" not in url:
                aff_ng.append((slug, url))

    print("記事 %d本を確認しました。" % len(files))

    def report(title, rows, ok_msg):
        section(title)
        if not rows:
            print("  " + ok_msg)
        else:
            for r in rows:
                print("  " + " | ".join(str(x) for x in r))

    report("date が未来（記事が404になります）", future, "なし")
    report("date とタイトルの日付がずれている", mismatch, "なし")
    report("description の問題", desc_ng, "全記事OK")
    report("SNSカード画像の問題（Xでカードが出ない原因）", ogp_ng, "全記事1200x630でOK")
    report("正規セットにないタグ", tag_ng, "なし")
    report("本文の画像が見つからない", img_missing, "なし")
    report("内部リンク先の記事が無い", link_missing, "なし")
    report("アソシエイトタグが入っていないリンク", aff_ng, "なし")

    orphans = sorted(s for s in slugs if inbound[s] == 0)
    section("被リンクゼロの記事（孤児記事・%d本）" % len(orphans))
    if not orphans:
        print("  なし")
    else:
        for s in orphans:
            print("  " + s)
        print("\n  ※ 新しい記事から本文リンクを張ると、検索エンジンに拾われやすくなります。")


if __name__ == "__main__":
    main()
