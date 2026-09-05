# HANDOFF.md — ブログ「昭和44年男」引き継ぎ資料

最終更新: 2026-09-05

このファイルはプロジェクト全体の引き継ぎ資料です。
**毎日の記事公開の手順そのものは [`AGENTS.md`](./AGENTS.md) に書いてあります。**
作業を始める前に、両方を読んでください。

---

## 1. ブログの目的と構成

### 目的

昭和44年（1969年）生まれ・57歳・現役の路線バス運転士である竹内一見さんの、
**個人ブログ兼収益サイト**です。目的は3つ。

1. 昭和の記憶を、当時子どもだった一人の目線で日々書き残すこと
2. 検索流入を積み上げること（Google Search Console 運用中）
3. Amazonアソシエイトと Google AdSense による収益化

### 構成

| カテゴリ | 本数 | 内容 |
|---|---:|---|
| **昭和の今日は何があった日？** | 132 | 主力。昭和40〜64年の「今日」を毎日1本。2026年4月29日〜9月5日まで日刊で継続中 |
| お金と暮らし | 26 | インデックス投資、固定費削減、不動産、書評 |
| 走って・ぶら下がって・考えた | 4 | ランニング関連 |
| 昭和の記憶 | 3 | 連載外の昭和もの |
| **合計** | **170** | |

固定ページは `about` / `contact` / `privacy` / `showa-calendar`。
`/showa-calendar/` は連載132本を月別・日付順に並べるハブページで、記事を足せば自動で載ります。

### 書き手のプロフィール（記事の一人称「私」）

竹内一見。昭和44年4月生まれ。東京都葛飾区高砂で生まれ育ち、現在も葛飾在住。
路線バス運転士。前職は信用金庫。子ども5人。高校まで野球部。いまも筋トレとランニング。
FXで150万円を失った経験から、現在はS&P500・NASDAQ100のインデックス投資。

---

## 2. 使用している技術

| 分類 | 内容 |
|---|---|
| 静的サイトジェネレータ | **Hugo v0.160.1 extended**（Windows/amd64） |
| テーマ | **PaperMod**（`themes/PaperMod` に git submodule として配置） |
| 設定ファイル | `hugo.toml`（`buildFuture = true` / `markup.goldmark.renderer.unsafe = true`） |
| ホスティング | **Cloudflare Pages**。GitHub連携で `main` への push を検知し、**ソースからビルド**する |
| リポジトリ | https://github.com/kamakyuukoi6535-debug/my-blog |
| 独自ドメイン | https://showa44man.com/ |
| アクセス解析 | Google Analytics（測定IDは `hugo.toml` に記載。公開識別子であり秘密情報ではない） |
| 広告 | Google AdSense（クライアントIDは `layouts/partials/extend_head.html` に記載。同上） |
| 収益 | Amazonアソシエイト（タグは記事内のURLに記載。同上） |
| 補助スクリプト | Python 3 + **Pillow**（画像生成・検査） |

### 必要な環境変数（名前のみ）

**現状、ローカルで作業する分には環境変数の設定は不要です。**
git の認証は Windows 資格情報マネージャー（`credential.helper = manager`）に保存済みで、
Cloudflare Pages は GitHub 連携で自動ビルドするため、こちらからトークンを渡していません。

ヘッドレス環境やCIから操作する場合にのみ、次の名前の環境変数が必要になります。
**値はこのファイルにも、リポジトリのどこにも書きません。**

| 変数名 | 用途 |
|---|---|
| `GITHUB_TOKEN`（または `GH_TOKEN`） | `git push` の認証 |
| `CLOUDFLARE_API_TOKEN` | Cloudflare Pages をAPIから操作する場合のみ |
| `CLOUDFLARE_ACCOUNT_ID` | 同上 |

---

## 3. 記事の保存場所

```
content/
├── posts/          記事本体（.md）170本
├── about.md        プロフィール
├── contact.md      お問い合わせ
├── privacy.md      プライバシーポリシー
└── showa-calendar.md  連載の日付別ハブページ
```

### ファイル名の規則

| 種類 | 例 |
|---|---|
| 昭和シリーズ | `showa-september-05.md`（`showa-{英語の月}-{2桁の日}.md`） |
| 同じ日の2本目 | `showa-august-25b.md`（末尾に `b`） |
| その他 | `money-war-01.md`, `kenja-no-toushijutsu.md` など内容に応じた英字slug |

公開URLは `https://showa44man.com/posts/{ファイル名}/` になります。

### front matter

大半はYAML（`---`）ですが、**4本だけTOML（`+++`）**です
（`blog-setup` / `jasso-loan` / `mvno-switch` / `real-estate-ai`）。
スクリプトは両方に対応させてありますが、手で扱うときは注意してください。

```yaml
---
title: "9月5日 ── 見出し｜昭和の今日は何があった日？"
date: 2026-09-05T05:00:00+09:00
draft: false
categories: ["昭和の今日は何があった日？"]
tags: ["昭和", "昭和44年男", "テレビ", "昭和の暮らし"]
description: "（120字前後）"
images: ["/images/september05-ogp.jpg"]
---
```

---

## 4. 画像の保存場所

```
static/
├── images/          562点。すべてここに平置き（サブフォルダは作っていない）
├── _redirects       Cloudflare Pages の301設定（旧タグURL → 「昭和」タグ）
├── favicon.ico / favicon.png / apple-touch-icon.png
└── google47b4b81200316e65.html   Search Console の所有権確認ファイル
```

本文からは `/images/ファイル名.jpg` で参照します（`static/` は付けません）。

### 命名の傾向

| 種類 | 例 |
|---|---|
| SNSカード（OGP） | `september05-ogp.jpg` / `showa-may-16-ogp.jpg` |
| 実物写真 | `keisei-ueno-station.jpg`, `fuji-tv-kawadacho.jpg` |
| 自作の図解 | `tvran-1977-0905.jpg`, `panda-gyoretsu.jpg` |

**SNSカード画像は1200×630が必須です。** それ以外のサイズだとXでカードが崩れます。

---

## 5. ローカルでの起動方法

```bash
cd C:\Users\kamak\OneDrive\Desktop\my-blog

# 初回のみ：テーマのサブモジュールを取得する（これが無いとビルドできない）
git submodule update --init --depth 1 themes/PaperMod

# 初回のみ：Python側の依存
pip install pillow

# 開発サーバを起動（http://localhost:1313/）
hugo server -D
```

`-D` は下書き（`draft: true`）も表示するオプションです。
ファイルを保存すると自動でリロードされます。

---

## 6. ビルド方法

```bash
hugo --quiet --gc
```

`public/` に静的ファイルが生成されます。

- **`public/` は Git の追跡対象外です**（`.gitignore` に記載）。
  Cloudflare Pages はソースからビルドするので、コミットする必要はありません。
- **push の前に必ずこのコマンドを通してください。** テンプレートのエラーで
  サイト全体のビルドが壊れかけた事故があります。

---

## 7. 公開方法

### 推奨（スクリプト）

```bash
python tools\publish.py showa-september-06
```

検査 → ビルド → commit → push → 公開待ち → 到達確認までを1コマンドで行います。
検査に引っかかった場合は**公開せずに停止**します。

```bash
python tools\publish.py showa-september-06 --dry-run   # 検査とビルドだけ
```

### 手動で行う場合

```bash
hugo --quiet --gc                                  # 落ちたら push しない
git add content/posts/xxx.md static/images/...
git commit -m "feat: 9月6日 …の記事を公開"
git push origin main
```

push から公開までは Cloudflare Pages のビルドで**約1〜2分**かかります。
`https://showa44man.com/posts/{slug}/` が 200 を返すまで待ってから、公開を宣言してください。

---

## 8. 現在完了している作業

- 記事170本を公開済み。連載「昭和の今日は何があった日？」は
  **2026年4月29日から9月5日まで、1日も落とさず日刊で継続中**
- 全記事に `description`（約120字）を設定済み
- 全記事に SNSカード画像（`images`）を設定済み
- 日付とタイトルのずれを全記事で解消済み（過去に37本まとめて修正）
- タグを30個の正規セットに統一。廃止した旧タグは `static/_redirects` で301転送済み
- `/showa-calendar/` ハブページを構築し、全メニューから導線を確保
- 孤児記事（被リンクゼロ）を解消
- OGPの構造化プロパティ（`og:image:width` など）を `og:image` の直後に出力するよう修正
- `og:locale` を `ja_jp` に修正
- 運用スクリプト3本（`tools/`）と、エージェント向けマニュアル `AGENTS.md` を整備

---

## 9. 未完了の作業 / 現在発生している問題

優先度の高い順に並べています。

### 9-1. 【未解決】Xでカード画像が表示されない

**症状**：記事URLをXに投稿しても、画像付きカードが出ないことがある。

**調査済みの内容**（いずれも問題なし）:

- `twitter:card` = `summary_large_image`、`twitter:image` / `og:image` とも絶対URLで出力されている
- Twitterbot のUAでページ・画像とも 200 が返る
- robots.txt に禁止設定なし、リダイレクトなし、Cloudflareのボット遮断もなし
  （Twitterbot / facebookexternalhit / Slackbot / Discordbot / LinkedInBot すべて200で同一サイズ）
- 外部のOGP検証サービス（別ネットワークからの取得）で**エラー0件・合格12件**。
  「Image loads cleanly」「Image dimensions are perfect（1200×630）」「X card uses a large image」
- 上記サービスのX用プレビューでも、カードは正常にレンダリングされる

**つまりサイト側の配信は正常です。** 残る可能性は次のいずれかで、こちらからは検証できていません。

1. XがそのURLを一度取得に失敗し、結果をキャッシュしている（Xは約1週間キャッシュする）
2. 投稿前の入力欄で判断している（Xは投稿前プレビューを出さないことが多い）
3. 投稿に画像を別途添付している（添付があるとカードは抑制される）

**次にやること**：竹内さんに「投稿後のポストで出ないのか、投稿前の入力欄で出ないのか」を
確認してもらう。暫定回避策は、URLの末尾に `?x=1` を付けて投稿すること
（Xが別URLとみなして取り直す。この形でも200とカードタグが返ることは確認済み）。

### 9-2. SNSカード画像が1200×630でない記事が28本

横長ではあるものの、サイズがまちまちです。`showa-june-23`（540×360）、
`showa-april-29`（640×426）など、小さすぎるものも含まれます。

```bash
python tools\check.py                        # 対象の一覧を出す
python tools\make_ogp.py --all --strict      # 28本を一括で作り直す
```

**注意**：実行すると、現在入っている実物写真が自動生成の文字カードに置き換わります。
写真のほうが良い記事もあるため、**一括実行するかどうかは竹内さんの判断が必要です。**

### 9-3. 記事内の未解決事項（竹内さんの回答待ち）

| 記事 | 内容 |
|---|---|
| `showa-august-22.md` | 本文は「3000キロ近く／5月12日出発」、記念碑の刻字は「2,600キロ／5月10日〜8月22日」。どちらに揃えるか未決 |
| `showa-june-24.md` | 本文の冒頭に、`description` と同じ文が重複して入っている。削除の可否が未確認 |
| `cap-washer-review.md` | アフィリエイトのASIN `B0CSBD4RTV` が、竹内さんが実際に購入した製品ではなく同種の別商品。差し替え候補が未確定 |

### 9-4. 環境の整理

`C:\Users\kamak\OneDrive\Desktop\Code作業\my-blog` に**古いコピー（記事69本）**が残っています。
本番は `C:\Users\kamak\OneDrive\Desktop\my-blog`（記事170本）です。
引き継ぎ先が取り違える危険があるため、**削除するか名前を変えることを推奨します。**

---

## 10. 次に行うべき作業

1. **連載を毎日続ける。** 9月6日以降、竹内さんが下書きを渡してきます。
   手順は `AGENTS.md` のとおり。画像4〜6点＋アフィリエイト2点＋X投稿文まで作って公開します。
2. **9-1（Xのカード）の切り分け**を進める。竹内さんへの確認が先。
3. **9-3の3件**について竹内さんの判断を仰ぎ、決まり次第反映する。
4. **9-2のカード画像**を揃えるかどうか確認する。
5. **月に一度 `python tools\check.py` を流す。** 未来日付・日付ずれ・リンク切れ・
   孤児記事・タグの逸脱を早期に発見できます。
6. Search Console の推移を見る。descriptionを全記事に入れた効果の観測が途中です。

---

## 11. 重要なファイル一覧

### 設定・ドキュメント

| パス | 役割 |
|---|---|
| `hugo.toml` | サイト設定。`baseURL` / `buildFuture` / `unsafe` は変更しないこと |
| `AGENTS.md` | **毎日の記事公開手順。作業前に必読** |
| `HANDOFF.md` | このファイル |
| `.gitignore` | `/public/` `/resources/` `.hugo_build.lock` を除外 |
| `.gitmodules` | PaperMod テーマのサブモジュール定義 |

### テンプレート（`layouts/` — テーマを上書きしている）

| パス | 役割 |
|---|---|
| `layouts/partials/templates/opengraph.html` | **OGPタグ。`og:image` の直後に width/height/alt を出す（順序が重要）** |
| `layouts/partials/templates/twitter_cards.html` | Twitterカード。`twitter:image:alt` を追加 |
| `layouts/partials/extend_head.html` | AdSenseタグ、本文の色付けCSS（`hl-y` `txt-blue` など）を定義 |
| `layouts/partials/extend_footer.html` | 記事末尾のURLコピーボックス |
| `layouts/shortcodes/amazon.html` | `{{< amazon title="" note="" url="" >}}` のアフィリエイトボックス |
| `layouts/_default/showa-calendar.html` | 連載の日付別ハブページ。月別にグループ化して自動生成 |
| `layouts/404.html` | カスタム404 |

### スクリプト（`tools/`）

| パス | 役割 |
|---|---|
| `tools/publish.py` | 検査 → ビルド → push → 公開確認。`--dry-run` / `--count` |
| `tools/make_ogp.py` | SNSカード画像（1200×630）の生成。`--all` / `--strict` / `--force` |
| `tools/check.py` | 全記事の健康診断 |

### その他

| パス | 役割 |
|---|---|
| `static/_redirects` | 旧タグURL → 「昭和」タグへの301。**消さないこと**（SEO資産） |
| `static/google47b4b81200316e65.html` | Search Console の所有権確認ファイル。**消さないこと** |
| `themes/PaperMod/` | git submodule。**直接編集しない**。変更は `layouts/` 側で上書きする |

---

## 12. 触ってはいけないもの

- `themes/PaperMod/` — サブモジュール。直接編集した変更は失われます
- `static/_redirects` と `static/google47b4b81200316e65.html` — SEOの資産
- `hugo.toml` の `baseURL` / `buildFuture` / `markup.goldmark.renderer.unsafe`
- 記事本文の文章 — 竹内さんの文章です。事実誤りを見つけたときは、直さずに指摘してください
