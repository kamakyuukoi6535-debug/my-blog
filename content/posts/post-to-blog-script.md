---
title: "ブログ投稿をPythonで自動化した話。コマンド1つで記事がアップされる仕組み"
date: 2026-04-26T12:00:00+09:00
draft: false
tags: ["Python", "Hugo", "自動化", "ブログ運営", "Claude Code"]
description: "Hugoブログへの記事投稿を自動化するPythonスクリプトを作った。タイトル・本文を入力するだけで、Markdownファイル生成からGitHubプッシュまで一気に完了する。"
---

このブログはHugo製で、Cloudflare Pagesで公開している。記事を書くたびに「Markdownファイルを作る→front matterを書く→git add→commit→push」という手順を踏む必要があった。

面倒なので、Pythonスクリプトで一気に自動化した。

---

## 作ったもの

`post_to_blog.py` という1ファイルのスクリプトだ。コマンドプロンプトで実行すると、対話形式で記事情報を入力でき、最後にGitHubへのプッシュまで自動でやってくれる。

```
python post_to_blog.py
```

実行すると以下の順で進む。

---

## 動作の流れ

### STEP 0: 環境チェック

まずHugoとGitが使える状態かを確認する。どちらかが見つからなければその場でエラーを出して終了する。

```
✅ Hugo: hugo v0.160.1+extended windows/amd64
✅ Git: git version 2.x.x
✅ ブログフォルダ: C:\Users\kamak\OneDrive\Desktop\my-blog
```

### STEP 1: 記事情報の入力

タイトル・ファイル名・タグ・本文を順番に入力する。

```
📝 記事タイトル（日本語OK）: ブログ投稿を自動化した話
💡 ファイル名の候補: new-post.md
📁 ファイル名（半角英数字・ハイフン）: post-automation
🏷️  タグ（カンマ区切り）: Python,自動化
📄 記事本文を貼り付けてください。
```

本文は貼り付け後、`END` と入力してEnterを押せば完了。

### STEP 2: Markdownファイルを生成

入力した情報をもとに、Hugo用のMarkdownファイルを自動生成する。front matterのdateは実行時刻で自動設定されるため、手書きする必要がない。

```markdown
---
title: "記事タイトル"
date: 2026-04-26T12:00:00+09:00
draft: false
tags:
  - "Python"
  - "自動化"
---

本文がここに入る
```

### STEP 3: GitHubにプッシュ

`git add .` → `git commit` → `git push origin main` を自動実行する。コミットメッセージは記事タイトルが自動でセットされる。

```
✅ git add .
✅ git commit -m "記事タイトル"
✅ git push origin main
```

---

## スクリプト全文

```python
#!/usr/bin/env python3
import subprocess
import sys
import re
import datetime
from pathlib import Path

BLOG_DIR  = Path(r"C:\Users\kamak\OneDrive\Desktop\my-blog")
POSTS_DIR = BLOG_DIR / "content" / "posts"
BLOG_URL  = "https://my-blog-b4d.pages.dev"

def run(cmd, cwd=None):
    result = subprocess.run(
        cmd, cwd=str(cwd or BLOG_DIR),
        capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def slugify(text):
    slug = re.sub(r"[^\w\s-]", "", text.lower())
    slug = re.sub(r"[\s_]+", "-", slug).strip("-")
    return slug or "new-post"

def main():
    # 環境チェック
    for cmd in [["hugo", "version"], ["git", "--version"]]:
        code, out, _ = run(cmd)
        if code != 0:
            print(f"❌ {cmd[0]} が見つかりません"); sys.exit(1)
        print(f"✅ {out.splitlines()[0]}")

    # 記事情報の入力
    title = input("📝 タイトル: ").strip()
    slug  = input(f"📁 ファイル名 [{slugify(title)}]: ").strip() or slugify(title)
    filename = slug.rstrip(".md") + ".md"
    tags_raw = input("🏷️  タグ（カンマ区切り）: ").strip()
    tags = [t.strip() for t in tags_raw.split(",") if t.strip()]

    print("📄 本文を入力（ENDで終了）:")
    lines = []
    while True:
        line = input()
        if line.strip() == "END": break
        lines.append(line)
    body = "\n".join(lines).strip()

    # Markdown生成
    now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S+09:00")
    tags_yaml = "\n".join(f'  - "{t}"' for t in tags)
    tags_block = f"tags:\n{tags_yaml}\n" if tags else ""
    content = f"---\ntitle: \"{title}\"\ndate: {now}\ndraft: false\n{tags_block}---\n\n{body}\n"

    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    (POSTS_DIR / filename).write_text(content, encoding="utf-8")
    print(f"✅ ファイル作成: {filename}")

    # GitHubへプッシュ
    for cmd in [["git","add","."], ["git","commit","-m",title], ["git","push","origin","main"]]:
        code, _, err = run(cmd)
        if code != 0:
            print(f"❌ {' '.join(cmd)} 失敗: {err}"); sys.exit(1)
        print(f"✅ {' '.join(cmd[:2])}")

    print(f"\n🌐 1〜2分後に確認: {BLOG_URL}")

if __name__ == "__main__":
    main()
```

---

## 使ってみた感想

記事を書く心理的ハードルが下がった。「書いたらすぐ出せる」という状態になると、短い記事でも気軽に投稿できるようになる。

Markdown慣れしていない人にとっても、front matterを手書きしなくていいのは助かるはずだ。Hugo + Cloudflare Pagesで運営しているブログがあれば、そのまま使い回せる。

---

スクリプトはClaude Codeと相談しながら作った。こういう「繰り返し作業を1コマンドにまとめる」用途にPythonは本当に向いている。
