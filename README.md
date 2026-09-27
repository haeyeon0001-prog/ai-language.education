# AI ✖️ 言語教育・言語学習

語学教員のための AI 活用情報サイト — 白海燕 博士（学術）

## About

大学で中国語・韓国語・日本語を教える教員が、AI を活用して教育の効率化を図る実践を共有するサイトです。

## Setup

`index.html` をブラウザで開くだけで動作します。  
GitHub Pages を有効にすれば、そのまま公開サイトとして使えます。

## GitHub Pages で公開する手順

1. リポジトリの **Settings** → **Pages** を開く
2. Source を **Deploy from a branch** に設定
3. Branch を **main** / **(root)** に設定して Save
4. 数分後に `https://<username>.github.io/ai-language-education/` で公開されます

## 多言語ページ（EN / KO / ZH）

`en.html`・`ko.html`・`zh.html` は `index.html`（日本語）から自動生成しています。直接編集しないでください。

1. `index.html` を編集する
2. 文章を変えた・追加した場合は、`i18n/build.py` の翻訳表に同じ文と訳を追加する
3. `python3 i18n/build.py` を実行する（翻訳漏れがあると警告が出ます）
