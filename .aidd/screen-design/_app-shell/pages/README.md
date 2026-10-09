# mockup — _app-shell（入口とシステムエラー）

> **これは画面設計書とスタイルガイドから生成した画面の具体形です**
> 構成・項目・状態・文言と、案件の見た目を確認するためのものです。
> 挙動は再現していません（JS なし・画面遷移はリンクのみ・表示データはすべて固定値のダミーです）。
> 正は**画面設計書**（構成・項目・操作・状態・文言）と**スタイルガイド**（見た目）であり、
> この HTML を実装のソースには使いません。
> 直したいところは、この HTML ではなく**入力（画面設計書・画面マップ・スタイルガイド）を直して再生成**します。

## 生成条件

| 入力 | 版・時点 |
|---|---|
| 画面設計書 `.aidd/screen-design/_app-shell/screen-spec.md` | status: confirmed / 確定 2026-10-09T22:38+09:00 |
| 画面マップ `.aidd/screen-design/_app-shell/screen-map.md` | revision 1 |
| STYLEGUIDE.md / styleguide.css | version 0.3.10 |
| 生成の手段 | `.aidd/screen-design/_tools/mockup/gen-_app-shell.mjs`（シェルは `shell.mjs`）— `node .aidd/screen-design/_tools/mockup/gen-_app-shell.mjs <案件ルート>` |

生成日時: 2026-10-09T22:40:18+09:00

## ページ（画面 × 状態 = 2 ページ）

| ページ | 画面 | 状態 |
|---|---|---|
| [s-01-default.html](s-01-default.html) | S-01 メニュー | 通常（案件の入口） |
| [s-02-default.html](s-02-default.html) | S-02 システムエラー | 通常 |

## 見るときの観点

**A. 毎回同じ 3 観点**

| # | 観点 | 代表ページ |
|---|---|---|
| 1 | **読み込み切れ** — `tokens/styleguide.css` が当たっているか（素の HTML に見えるページが無いか） | [s-01-default.html](s-01-default.html) |
| 2 | **崩れ** — 部品の重なり・はみ出し・折り返し・間隔の詰まり | [s-02-default.html](s-02-default.html)（3 列の表とメッセージの長さ） |
| 3 | **シェルとナビの一致** — 全ページに同じシェルが載り、ナビ項目と現在地が画面マップ §4-1 / §4-2 と合っているか | [s-01-default.html](s-01-default.html) |

**B. この回だけの観点**（manifest の `notes[]` から）

| # | 観点 | 代表ページ |
|---|---|---|
| 4 | **無効表示のナビ項目** — 「物件基本情報登録変更」が押せない表示（灰色・下線なし・矢印付き）として、有効な項目と並んで違和感が無いか | [s-01-default.html](s-01-default.html) |
| 5 | **入口画面のヘッダ** — S-01 で「MENU」が無効表示になっていること、「LOGOUT」が全ページで無効表示であること | [s-01-default.html](s-01-default.html) / [s-02-default.html](s-02-default.html) |
| 6 | **システムエラーの中身** — 詳細欄・戻るボタンを置かない形（画面設計書 §5-1 #4・#5）で足りて見えるか。種別・メッセージの文言は仮置き（画面設計書 §5-4 #1） | [s-02-default.html](s-02-default.html) |
| 7 | **入口からの遷移** — ナビ項目 #2 から application-status-search の一覧へ移れ、そこからヘッダの「MENU」で戻れるか（今回はじめて両方向がつながった） | [s-01-default.html](s-01-default.html) |
