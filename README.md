# AI ✖️ 言語教育・言語学習

語学教員のための AI 活用情報サイト — 白海燕 博士（学術）

## About

大学で中国語・韓国語・日本語を教える教員が、AI を活用して教育の効率化を図る実践を共有するサイトです。

## 公開URL

👉 https://baihaiyan.com/

## 構成

- **ホスティング**：GitHub Pages（Public リポジトリ・無料）
- **独自ドメイン**：`baihaiyan.com`（Cloudflare Registrar）
- **DNS**：Cloudflare（無料プラン）
- **HTTPS**：Let's Encrypt（GitHub Pages が自動発行）
- **静的サイト生成**：Jekyll（GitHub Pages がビルド）

## ディレクトリ構成

```
.
├── index.html              トップページ（Hero / About / Purpose / Examples / 最新記事3件）
├── blog.html               ブログ記事一覧ページ（/blog/）
├── _config.yml             Jekyll 設定
├── _posts/                 ブログ記事（Markdown）
├── _layouts/               ページのテンプレート
│   ├── default.html        全ページ共通の枠（head / nav / footer）
│   ├── post.html           個別記事ページ
│   └── page.html           汎用ページ
├── _includes/              テンプレート部品
│   ├── head.html           <head> 部
│   ├── nav.html            ナビゲーション
│   ├── footer.html         フッター
│   └── fade-in.html        スクロール時のフェードイン JS
├── assets/css/style.css    全ページ共通スタイル
└── CNAME                   独自ドメイン設定
```

## ブログ記事の書き方

### 1. ファイルを作る

`_posts/` ディレクトリに、以下の命名規則で Markdown ファイルを作成します。

```
_posts/2026-05-15-ai-vocab-test.md
        └─年─┘└月┘└日┘└─スラッグ（URLの一部）─┘
```

スラッグは英数字とハイフンで。日本語の URL を避けるためです。

### 2. 記事を書く

ファイル冒頭に YAML フロントマター（`---` で囲む設定部）を書き、その下に本文を Markdown で書きます。

```markdown
---
layout: post
title: 記事のタイトル
date: 2026-05-15
tags: [韓国語, ChatGPT]
excerpt: 一覧ページに表示される短い説明文（1〜2行）。
---

ここから本文を Markdown で書く。

## 見出し2

段落は空行で分ける。

- 箇条書き
- も使える

> 引用ブロック（callout として薄い灰色背景で表示される）

**強調**や *斜体* も Markdown で書ける。
```

### 3. 公開

`main` ブランチにコミット & push すると、GitHub Pages が自動でビルドして数分後に公開されます。

- 記事URL：`https://baihaiyan.com/blog/2026/05/15/ai-vocab-test/`
- 一覧ページにも自動で追加されます

### タグの色

タグはサイトの配色（空色／桜色／緑）で自動的に色分けされます：

| タグ | 色 |
|---|---|
| `お知らせ`, `韓国語` | 空色（sky）|
| `中国語`, `ChatGPT` | 桜色（sakura）|
| その他 | 緑 |

色を増やしたい場合は `_layouts/post.html` と `blog.html` のタグ判定部を修正してください。

## ローカルで確認したいとき（任意）

ローカル環境で Jekyll を動かす場合：

```bash
# 初回のみ
gem install bundler jekyll

# プレビュー起動（http://localhost:4000）
jekyll serve
```

ローカルプレビューが不要なら、コミット & push して GitHub Pages 上で確認するのが最も手軽です。
