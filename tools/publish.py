#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
publish.py --- ブログ「昭和44年男」の記事を検査して公開する

使い方:
    python publish.py showa-september-04
    python publish.py showa-september-04 --dry-run   # 検査とビルドだけ（pushしない）

やること（この順番）:
    1. front matter の検査（未来日付 / 半角クォート / タグ / OGPサイズ ほか）
    2. 本文で使っている画像ファイルの存在確認
    3. hugo でローカルビルド（ここで落ちたら公開しない）
    4. git add / commit / push origin main
    5. 公開URLが 200 を返すまで待つ
    6. 画像・カード・カレンダー掲載の到達確認
    7. X投稿文の文字数を計算するための雛形を表示

必要なもの: python 3, hugo, git（すべてPATHが通っていること）
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
import os
import re
import subprocess
import sys
import time
import unicodedata
import urllib.request

# スクリプトの1つ上（リポジトリのルート）を基準にする
BLOG = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://showa44man.com"

CANONICAL_TAGS = {
    "昭和", "昭和44年男", "昭和の暮らし", "葛飾", "テレビ", "スポーツ", "インデックス投資",
    "音楽", "学校と子ども時代", "プロ野球", "お金と僕の12年戦争", "高校野球", "資産形成",
    "家計管理", "駄菓子", "漫画", "書評", "リベ大", "おもちゃ・ゲーム", "鉄道", "宇宙",
    "大相撲", "不動産", "固定費削減", "映画", "特撮・ヒーロー", "オリンピック", "FX",
    "奨学金", "NISA",
}
CANONICAL_CATEGORIES = {
    "昭和の今日は何があった日？", "お金と暮らし", "走って・ぶら下がって・考えた", "昭和の記憶",
}


def run(cmd, cwd=BLOG, check=True):
    p = subprocess.run(cmd, cwd=cwd, shell=isinstance(cmd, str),
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if check and p.returncode != 0:
        print("コマンド失敗: %s" % cmd)
        print(p.stdout)
        print(p.stderr)
        sys.exit(1)
    return p


def http_status(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "publish.py"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def x_weight(text):
    """Xの文字数（全角2・半角1）。URLは別途23で数える"""
    return sum(2 if unicodedata.east_asian_width(c) in "FWA" else 1 for c in text)


# ---------------------------------------------------------------- 検査

def validate(slug):
    post = os.path.join(BLOG, "content", "posts", slug + ".md")
    if not os.path.exists(post):
        print("[NG] 記事がありません: %s" % post)
        sys.exit(1)

    raw = open(post, encoding="utf-8", errors="replace").read()
    head = raw[:3000]
    errors, warnings = [], []

    # date
    m = re.search(r"^date\s*[:=]\s*'?\"?(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2})", head, re.M)
    if not m:
        errors.append("date が読めません")
    else:
        from datetime import datetime
        dt = datetime.strptime(m.group(1), "%Y-%m-%dT%H:%M:%S")
        if dt > datetime.now():
            errors.append("date が未来です（%s）。記事が404になります" % m.group(1))
        # タイトルの日付と一致するか
        t = re.search(r"^title\s*[:=]\s*['\"](.+?)['\"]\s*$", head, re.M)
        if t:
            md = re.search(r"(\d{1,2})月(\d{1,2})日", t.group(1))
            if md and (dt.month, dt.day) != (int(md.group(1)), int(md.group(2))):
                errors.append("タイトルの日付（%s月%s日）と date（%d月%d日）がずれています"
                              % (md.group(1), md.group(2), dt.month, dt.day))

    # description
    dm = re.search(r"^description\s*[:=]\s*(.+)$", head, re.M)
    if not dm:
        errors.append("description がありません")
    else:
        body = dm.group(1).strip()
        inner = body[1:-1] if len(body) > 1 and body[0] in "'\"" else body
        if '"' in inner:
            errors.append("description に半角の \" が入っています。YAMLが壊れて404になります")
        n = len(inner)
        if n < 80 or n > 170:
            warnings.append("description が %d字です（120字前後が目安）" % n)

    # draft
    if re.search(r"^draft\s*[:=]\s*true", head, re.M):
        errors.append("draft: true のままです")

    # categories
    cm = re.search(r"^categories\s*[:=]\s*\[?\s*['\"]([^'\"\]]+)", head, re.M)
    if cm and cm.group(1) not in CANONICAL_CATEGORIES:
        warnings.append("見慣れないカテゴリ: %s" % cm.group(1))

    # tags
    tm = re.search(r"^tags\s*[:=]\s*\[(.*?)\]", head, re.M | re.S)
    if not tm:
        warnings.append("tags がありません")
    else:
        tags = [x.strip().strip("'\"") for x in tm.group(1).split(",") if x.strip()]
        bad = [t for t in tags if t not in CANONICAL_TAGS]
        if bad:
            errors.append("正規セットにないタグ: %s" % "、".join(bad))
        if len(tags) > 5:
            warnings.append("タグが%d個あります（3〜4個が目安）" % len(tags))

    # images（OGP）
    im = re.search(r"^images\s*[:=]\s*\[?\s*['\"]([^'\"\]]+)", head, re.M)
    if not im:
        errors.append("images（SNSカード画像）がありません")
    else:
        p = os.path.join(BLOG, "static") + im.group(1).replace("/", os.sep)
        if not os.path.exists(p):
            errors.append("SNSカード画像がありません: %s" % im.group(1))
        else:
            try:
                from PIL import Image
                w, h = Image.open(p).size
                if (w, h) != (1200, 630):
                    errors.append("SNSカード画像が %dx%d です。1200x630 にしてください" % (w, h))
            except ImportError:
                warnings.append("Pillow が無いので画像サイズを確認できません")

    # 本文の画像
    for path in re.findall(r"!\[[^\]]*\]\((/images/[^)]+)\)", raw):
        f = os.path.join(BLOG, "static") + path.replace("/", os.sep)
        if not os.path.exists(f):
            errors.append("本文の画像がありません: %s" % path)

    # 内部リンク
    for path in re.findall(r"\]\((/posts/[a-z0-9\-]+/)\)", raw):
        target = os.path.join(BLOG, "content", "posts", path.strip("/").split("/")[-1] + ".md")
        if not os.path.exists(target):
            errors.append("内部リンク先の記事がありません: %s" % path)

    # アフィリエイト
    aff = re.findall(r"amazon\s+title=", raw)
    if len(aff) != 2:
        warnings.append("アフィリエイトが%d点です（2点が基本）" % len(aff))
    for url in re.findall(r'url="(https://www\.amazon\.co\.jp/dp/[^"]+)"', raw):
        if "tag=showa44man22-22" not in url:
            errors.append("アソシエイトタグが入っていません: %s" % url)

    # 空のalt
    if re.search(r"^!\[\]\(", raw, re.M):
        warnings.append("altテキストが空の画像があります")

    return errors, warnings


# ---------------------------------------------------------------- 公開

def publish(slug, dry_run=False):
    print("=" * 60)
    print(" 1. front matter と本文の検査")
    print("=" * 60)
    errors, warnings = validate(slug)
    for w in warnings:
        print("  [注意] %s" % w)
    for e in errors:
        print("  [NG] %s" % e)
    if errors:
        print("\n検査に通らなかったので中止します。上の [NG] を直してください。")
        sys.exit(1)
    print("  OK")

    print("\n" + "=" * 60)
    print(" 2. ローカルビルド（hugo）")
    print("=" * 60)
    p = run("hugo --quiet --gc", check=False)
    if p.returncode != 0:
        print(p.stdout)
        print(p.stderr)
        print("\nビルドに失敗しました。pushしません。")
        sys.exit(1)
    out = os.path.join(BLOG, "public", "posts", slug, "index.html")
    if not os.path.exists(out):
        print("  [NG] ページが生成されませんでした（dateが未来かもしれません）")
        sys.exit(1)
    print("  OK")

    if dry_run:
        print("\n--dry-run なのでここで終わります。")
        return

    print("\n" + "=" * 60)
    print(" 3. GitHubへ push")
    print("=" * 60)
    run("git add -A content static layouts hugo.toml")
    msg = "feat: %s の記事を公開" % slug
    p = run("git commit -q -m \"%s\"" % msg, check=False)
    if p.returncode != 0 and "nothing to commit" not in (p.stdout + p.stderr):
        print(p.stdout + p.stderr)
    run("git push origin main -q")
    print("  push しました")

    print("\n" + "=" * 60)
    print(" 4. 公開を待つ（Cloudflare Pages）")
    print("=" * 60)
    url = "%s/posts/%s/" % (SITE, slug)
    for i in range(1, 41):
        if http_status(url) == 200:
            print("  公開されました（%d回目の確認）" % i)
            break
        time.sleep(15)
    else:
        print("  [NG] 10分待っても200になりませんでした。Cloudflareのビルドログを見てください。")
        sys.exit(1)

    print("\n" + "=" * 60)
    print(" 5. 到達確認")
    print("=" * 60)
    raw = open(os.path.join(BLOG, "content", "posts", slug + ".md"),
               encoding="utf-8", errors="replace").read()
    targets = [url, "%s/showa-calendar/" % SITE]
    targets += ["%s%s" % (SITE, p) for p in
                sorted(set(re.findall(r"!\[[^\]]*\]\((/images/[^)]+)\)", raw)))]
    im = re.search(r"^images\s*[:=]\s*\[?\s*['\"]([^'\"\]]+)", raw[:3000], re.M)
    if im:
        targets.append(SITE + im.group(1))
    ng = 0
    for t in targets:
        s = http_status(t)
        print("  %s  %s" % (s, t.replace(SITE, "")))
        if s != 200:
            ng += 1

    html = urllib.request.urlopen(
        urllib.request.Request(url, headers={"User-Agent": "publish.py"}), timeout=20
    ).read().decode("utf-8", "replace")
    card_ok = 'name="twitter:card" content="summary_large_image"' in html
    order_ok = re.search(r'og:image"[^>]*>\s*<meta property="og:image:width"', html) is not None
    cal_ok = slug in urllib.request.urlopen(
        urllib.request.Request("%s/showa-calendar/" % SITE, headers={"User-Agent": "publish.py"}),
        timeout=20).read().decode("utf-8", "replace")
    print("\n  SNSカード（summary_large_image）: %s" % ("OK" if card_ok else "NG"))
    print("  og:image の直後に width/height : %s" % ("OK" if order_ok else "NG"))
    print("  昭和カレンダーに掲載            : %s" % ("OK" if cal_ok else "NG"))

    print("\n" + "=" * 60)
    print(" 公開URL（そのままコピーして使ってください）")
    print("=" * 60)
    print(url)
    print("\nX投稿文は280以内に収めてください（全角2・半角1・URLは23）。")
    print("下の関数で数えられます:  python publish.py --count \"本文\"")
    if ng:
        print("\n[注意] %d件が200以外でした。数分おいて再確認してください。" % ng)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("slug", nargs="?", help="記事のファイル名（.md なし）")
    ap.add_argument("--dry-run", action="store_true", help="検査とビルドだけ")
    ap.add_argument("--count", metavar="TEXT", help="X投稿文の文字数を数える（URL分の23を足す）")
    args = ap.parse_args()

    if args.count:
        w = x_weight(args.count)
        print("本文 %d ＋ URL 23 ＝ %d / 280 %s" % (w, w + 23, "OK" if w + 23 <= 280 else "超過"))
        return
    if not args.slug:
        ap.print_help()
        sys.exit(1)
    publish(args.slug, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
